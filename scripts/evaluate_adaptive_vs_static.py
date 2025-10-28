#!/usr/bin/env python3
"""
EXPERIMENT 2: ADAPTIVE vs STATIC COMPARISON

Tests whether Hebbian adaptation improves reasoning performance over static graphs.

DESIGN:
- Baseline: Static graph (NO Hebbian updates - frozen weights)
- Treatment: Adaptive graph (WITH Hebbian updates - learning enabled)
- Same queries, same initial state, compare performance over time

METRICS:
1. Trust scores (validation quality)
2. Retrieval accuracy (can find relevant facts)
3. Answer quality (reasoning correctness)
4. Edge strength evolution

HYPOTHESIS: Adaptive graphs will outperform static graphs as they:
- Strengthen frequently used paths
- Prune weak/unused edges
- Form emergent connections
"""

import argparse
import json
import os
import sys
import csv
import copy
import time
import numpy as np
from datetime import datetime
from typing import List, Dict, Any

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.knowledge_graph.knowledgeGraph import KnowledgeGraph
from core.orchestrator.index import orchestrate


def create_static_kg_wrapper(kg: KnowledgeGraph) -> KnowledgeGraph:
    """
    Create a wrapper around KG that disables Hebbian plasticity.
    All Hebbian methods become no-ops.
    """
    # deep copy to avoid modifying original
    static_kg = copy.deepcopy(kg)
    
    # override hebbian methods to do nothing
    static_kg.activate_relation = lambda *args, **kwargs: None
    static_kg.activate_entities = lambda *args, **kwargs: None
    static_kg.form_emergent_connections = lambda *args, **kwargs: []
    static_kg.apply_temporal_decay = lambda *args, **kwargs: []
    static_kg.consolidate_memory = lambda *args, **kwargs: {"emergent_edges": [], "decayed_edges": []}
    static_kg.increment_cycle_counters = lambda *args, **kwargs: None
    
    return static_kg


def measure_retrieval_accuracy(kg: KnowledgeGraph, query: str) -> float:
    """
    Measure how well the KG can retrieve relevant facts for a query.
    Higher = better retrieval.
    """
    # extract entity mentions from query
    query_words = query.split()
    found_entities = [w for w in query_words if w in kg.label_to_id]
    
    if not found_entities:
        return 0.0
    
    # count how many facts we can retrieve
    total_facts = 0
    for entity in found_entities[:3]:  # limit to first 3 entities
        facts = kg.query(subject=entity)
        facts.extend(kg.query(object_=entity))
        total_facts += len(facts)
    
    # normalize to 0-1 range (assume 10 facts = perfect)
    return min(1.0, total_facts / 10.0)


def compute_answer_quality_score(reasoning_output: Dict, validation: Dict) -> float:
    """
    Compute answer quality from reasoning output and validation.
    Combines confidence, reasoning steps, and validation scores.
    """
    # base confidence from reasoning
    confidence = reasoning_output.get("confidence", 0.0)
    
    # reasoning path quality (more steps = more thorough, up to a point)
    reasoning_path = reasoning_output.get("reasoningPath", [])
    path_quality = min(1.0, len(reasoning_path) / 5.0)  # 5 steps = ideal
    
    # validation quality (average of validation scores)
    val_scores = []
    for vn_name, vn_result in validation.items():
        if isinstance(vn_result, dict) and "score" in vn_result:
            val_scores.append(vn_result["score"])
    
    val_quality = np.mean(val_scores) if val_scores else 0.5
    
    # weighted combination
    quality = (confidence * 0.4) + (path_quality * 0.2) + (val_quality * 0.4)
    
    return min(1.0, max(0.0, quality))


def run_experiment(queries: List[str], kg_path: str, anthropic_key: str,
                   output_dir: str, cycles: int = 3):
    """
    Run the adaptive vs static comparison experiment.
    
    Args:
        queries: List of test queries
        kg_path: Path to initial knowledge graph
        anthropic_key: Anthropic API key for Claude
        output_dir: Where to save results
        cycles: Number of reasoning cycles to run
    """
    print("\n" + "="*80)
    print("EXPERIMENT 2: ADAPTIVE vs STATIC COMPARISON")
    print("="*80)
    print(f"\nConfiguration:")
    print(f"  Queries: {len(queries)}")
    print(f"  Cycles: {cycles}")
    print(f"  Initial KG: {kg_path}")
    print(f"  Model: Claude 3 Haiku")
    
    # load initial KG
    print(f"\nLoading knowledge graph...")
    kg_initial = KnowledgeGraph()
    kg_initial.load_from_json(kg_path)
    print(f"  Loaded: {len(kg_initial.entities)} entities, {len(kg_initial.relations)} relations")
    
    # create two separate KGs - one static, one adaptive
    print(f"\nCreating experimental conditions...")
    kg_static = create_static_kg_wrapper(copy.deepcopy(kg_initial))
    kg_adaptive = copy.deepcopy(kg_initial)
    print(f"  [STATIC] Hebbian learning DISABLED (frozen)")
    print(f"  [ADAPTIVE] Hebbian learning ENABLED (active)")
    
    # prepare output files
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    static_csv = os.path.join(output_dir, f"static_results_{timestamp}.csv")
    adaptive_csv = os.path.join(output_dir, f"adaptive_results_{timestamp}.csv")
    
    fieldnames = [
        'cycle', 'query_idx', 'query', 'latency', 'trust_score',
        'retrieval_accuracy', 'answer_quality', 'reasoning_steps',
        'edges_strengthened', 'emergent_edges', 'avg_edge_strength',
        'num_relations', 'condition'
    ]
    
    # ============= RUN STATIC BASELINE =============
    print("\n" + "="*80)
    print("RUNNING BASELINE: Static Graph (No Hebbian)")
    print("="*80)
    
    with open(static_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for cycle in range(1, cycles + 1):
            print(f"\n--- Cycle {cycle}/{cycles} ---")
            
            for query_idx, query in enumerate(queries):
                print(f"\n  Query {query_idx + 1}/{len(queries)}: {query[:60]}...")
                
                # measure pre-query state
                retrieval_acc = measure_retrieval_accuracy(kg_static, query)
                
                # run reasoning
                start_time = time.time()
                try:
                    result = orchestrate(query, kg_static, anthropic_key, run_validation=True)
                    latency = time.time() - start_time
                    
                    # extract metrics
                    trust_score = result.get("trust_score", 0.0)
                    reasoning = result.get("reasoning", {})
                    validation = result.get("validation", {})
                    hebbian = result.get("hebbian_plasticity", {})
                    
                    answer_quality = compute_answer_quality_score(reasoning, validation)
                    reasoning_steps = len(reasoning.get("reasoningPath", []))
                    
                    # get edge stats (should be unchanged for static)
                    top_edges = kg_static.get_strongest_edges(top_k=10)
                    avg_edge_strength = np.mean([e[3] for e in top_edges]) if top_edges else 0.0
                    
                    writer.writerow({
                        'cycle': cycle,
                        'query_idx': query_idx,
                        'query': query,
                        'latency': round(latency, 2),
                        'trust_score': round(trust_score, 3),
                        'retrieval_accuracy': round(retrieval_acc, 3),
                        'answer_quality': round(answer_quality, 3),
                        'reasoning_steps': reasoning_steps,
                        'edges_strengthened': 0,  # static = no learning
                        'emergent_edges': 0,
                        'avg_edge_strength': round(avg_edge_strength, 3),
                        'num_relations': len(kg_static.relations),
                        'condition': 'static'
                    })
                    
                    print(f"    Trust: {trust_score:.3f}, Quality: {answer_quality:.3f}, "
                          f"Latency: {latency:.2f}s")
                    
                except Exception as e:
                    print(f"    ERROR: {str(e)}")
                    import traceback
                    traceback.print_exc()
    
    print(f"\n[STATIC] Results saved to: {static_csv}")
    
    # ============= RUN ADAPTIVE TREATMENT =============
    print("\n" + "="*80)
    print("RUNNING TREATMENT: Adaptive Graph (With Hebbian)")
    print("="*80)
    
    with open(adaptive_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for cycle in range(1, cycles + 1):
            print(f"\n--- Cycle {cycle}/{cycles} ---")
            
            for query_idx, query in enumerate(queries):
                print(f"\n  Query {query_idx + 1}/{len(queries)}: {query[:60]}...")
                
                # measure pre-query state
                retrieval_acc = measure_retrieval_accuracy(kg_adaptive, query)
                
                # run reasoning with hebbian learning
                start_time = time.time()
                try:
                    result = orchestrate(query, kg_adaptive, anthropic_key, run_validation=True)
                    latency = time.time() - start_time
                    
                    # extract metrics
                    trust_score = result.get("trust_score", 0.0)
                    reasoning = result.get("reasoning", {})
                    validation = result.get("validation", {})
                    hebbian = result.get("hebbian_plasticity", {})
                    
                    answer_quality = compute_answer_quality_score(reasoning, validation)
                    reasoning_steps = len(reasoning.get("reasoningPath", []))
                    
                    edges_strengthened = hebbian.get("edges_strengthened", 0)
                    emergent_edges = hebbian.get("emergent_edges", 0)
                    
                    # get edge stats (should be changing for adaptive)
                    top_edges = kg_adaptive.get_strongest_edges(top_k=10)
                    avg_edge_strength = np.mean([e[3] for e in top_edges]) if top_edges else 0.0
                    
                    writer.writerow({
                        'cycle': cycle,
                        'query_idx': query_idx,
                        'query': query,
                        'latency': round(latency, 2),
                        'trust_score': round(trust_score, 3),
                        'retrieval_accuracy': round(retrieval_acc, 3),
                        'answer_quality': round(answer_quality, 3),
                        'reasoning_steps': reasoning_steps,
                        'edges_strengthened': edges_strengthened,
                        'emergent_edges': emergent_edges,
                        'avg_edge_strength': round(avg_edge_strength, 3),
                        'num_relations': len(kg_adaptive.relations),
                        'condition': 'adaptive'
                    })
                    
                    print(f"    Trust: {trust_score:.3f}, Quality: {answer_quality:.3f}, "
                          f"Latency: {latency:.2f}s")
                    print(f"    Hebbian: +{edges_strengthened} edges, {emergent_edges} emergent")
                    
                except Exception as e:
                    print(f"    ERROR: {str(e)}")
                    import traceback
                    traceback.print_exc()
            
            # save KG snapshot after each cycle
            kg_snapshot = os.path.join(output_dir, f"adaptive_kg_cycle_{cycle}.json")
            kg_adaptive.save_to_json(kg_snapshot)
            print(f"\n  Saved adaptive KG snapshot: {kg_snapshot}")
    
    print(f"\n[ADAPTIVE] Results saved to: {adaptive_csv}")
    
    # ============= ANALYZE RESULTS =============
    print("\n" + "="*80)
    print("ANALYZING RESULTS")
    print("="*80)
    
    import pandas as pd
    
    df_static = pd.read_csv(static_csv)
    df_adaptive = pd.read_csv(adaptive_csv)
    
    # compute averages
    metrics = ['trust_score', 'retrieval_accuracy', 'answer_quality', 'avg_edge_strength']
    
    results_summary = {}
    
    for metric in metrics:
        static_mean = df_static[metric].mean()
        adaptive_mean = df_adaptive[metric].mean()
        
        improvement_pct = ((adaptive_mean - static_mean) / static_mean * 100) if static_mean > 0 else 0
        
        results_summary[metric] = {
            'static_mean': static_mean,
            'adaptive_mean': adaptive_mean,
            'improvement_pct': improvement_pct
        }
        
        print(f"\n{metric.upper().replace('_', ' ')}:")
        print(f"  Static:      {static_mean:.3f}")
        print(f"  Adaptive:    {adaptive_mean:.3f}")
        print(f"  Improvement: {improvement_pct:+.1f}%")
    
    # overall improvement
    overall_improvement = np.mean([results_summary[m]['improvement_pct'] for m in metrics])
    
    print(f"\n{'='*80}")
    print(f"OVERALL PERFORMANCE IMPROVEMENT: {overall_improvement:+.1f}%")
    print(f"{'='*80}")
    
    # determine verdict
    if overall_improvement > 5:
        verdict = "CLAIM SUPPORTED"
        print(f"\n[{verdict}]")
        print(f"Adaptive graphs outperform static graphs by {overall_improvement:.1f}%")
    else:
        verdict = "INCONCLUSIVE"
        print(f"\n[{verdict}]")
        print("Improvement is marginal or not significant")
    
    # hebbian mechanism stats
    print(f"\n{'-'*80}")
    print("HEBBIAN MECHANISMS:")
    print(f"{'-'*80}")
    print(f"Total edges strengthened: {df_adaptive['edges_strengthened'].sum()}")
    print(f"Total emergent connections: {df_adaptive['emergent_edges'].sum()}")
    print(f"Final relation count (static): {df_static['num_relations'].iloc[-1]}")
    print(f"Final relation count (adaptive): {df_adaptive['num_relations'].iloc[-1]}")
    
    # save summary
    summary_file = os.path.join(output_dir, f"comparison_summary_{timestamp}.json")
    summary_data = {
        "experiment": "Adaptive vs Static Comparison",
        "timestamp": timestamp,
        "configuration": {
            "queries": len(queries),
            "cycles": cycles,
            "model": "claude-3-haiku-20240307"
        },
        "results": results_summary,
        "overall_improvement_pct": overall_improvement,
        "verdict": verdict,
        "claim": f"Adaptive graphs outperform static graphs by {overall_improvement:.1f}%",
        "hebbian_stats": {
            "total_edges_strengthened": int(df_adaptive['edges_strengthened'].sum()),
            "total_emergent_edges": int(df_adaptive['emergent_edges'].sum()),
            "final_relations_static": int(df_static['num_relations'].iloc[-1]),
            "final_relations_adaptive": int(df_adaptive['num_relations'].iloc[-1])
        }
    }
    
    with open(summary_file, 'w') as f:
        json.dump(summary_data, f, indent=2)
    
    print(f"\n[SUCCESS] Summary saved to: {summary_file}")
    
    return summary_data


def main():
    parser = argparse.ArgumentParser(
        description="Experiment 2: Adaptive vs Static Graph Comparison"
    )
    parser.add_argument("--anthropic-key", required=True, help="Anthropic API key")
    parser.add_argument("--kg-path", default="output/knowledge_graph.json",
                       help="Path to knowledge graph")
    parser.add_argument("--queries", nargs='+',
                       help="List of queries to test (or use --dataset)")
    parser.add_argument("--dataset", default="tests/comprehensive_evaluation_dataset.json",
                       help="Path to evaluation dataset")
    parser.add_argument("--n-queries", type=int, default=5,
                       help="Number of queries to test (default: 5)")
    parser.add_argument("--cycles", type=int, default=3,
                       help="Number of reasoning cycles (default: 3)")
    parser.add_argument("--output-dir", default="output",
                       help="Output directory")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    
    args = parser.parse_args()
    
    np.random.seed(args.seed)
    
    # get queries
    if args.queries:
        test_queries = args.queries
    else:
        # load from dataset
        print(f"Loading queries from {args.dataset}...")
        with open(args.dataset, 'r') as f:
            dataset = json.load(f)
        
        questions = dataset.get("evaluation_questions", dataset)
        if isinstance(questions, dict):
            questions = [questions]
        
        # sample queries
        indices = np.random.choice(len(questions), min(args.n_queries, len(questions)), replace=False)
        test_queries = [questions[i].get("question", questions[i].get("query", ""))
                       for i in indices]
    
    print(f"\nTest queries ({len(test_queries)}):")
    for i, q in enumerate(test_queries, 1):
        print(f"  {i}. {q}")
    
    # run experiment
    results = run_experiment(
        queries=test_queries,
        kg_path=args.kg_path,
        anthropic_key=args.anthropic_key,
        output_dir=args.output_dir,
        cycles=args.cycles
    )
    
    print("\n" + "="*80)
    print("[SUCCESS] Experiment completed!")
    print("="*80)


if __name__ == "__main__":
    main()

