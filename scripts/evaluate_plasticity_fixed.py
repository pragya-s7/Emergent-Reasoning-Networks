"""
Fixed and Enhanced Hebbian Plasticity Evaluation Script.

Tests whether Hebbian plasticity improves performance over time by:
1. Running repeated queries over multiple cycles
2. Tracking edge strength evolution
3. Monitoring emergent connection formation
4. Measuring performance improvements

Key hypothesis: Frequently used reasoning paths should strengthen and improve efficiency.
"""

import argparse
import json
import os
import sys
import csv
import time
import numpy as np
import copy
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.knowledge_graph.knowledgeGraph import KnowledgeGraph
from core.orchestrator.index import orchestrate


def evaluate_plasticity(queries: list, kg: KnowledgeGraph, anthropic_key: str,
                       cycles: int, output_path: str):
    """
    Evaluate Hebbian plasticity effects over multiple reasoning cycles.

    Args:
        queries: List of queries to run repeatedly
        kg: Knowledge graph (will be modified in place)
        anthropic_key: API key
        cycles: Number of cycles to run
        output_path: Where to save results
    """
    results = []

    # Track specific edges over time
    monitored_edges = [
        ("ApolloContract", "has_vulnerability", "Reentrancy"),
    ]

    print(f"Running {cycles} cycles with {len(queries)} queries per cycle...")

    with open(output_path, 'w', newline='') as csvfile:
        fieldnames = [
            'cycle', 'query_idx', 'query', 'latency', 'trust_score',
            'retrieval_time_ms', 'facts_retrieved',  # NEW: retrieval efficiency metrics
            'edges_strengthened', 'entities_activated', 'emergent_edges_count',
            'avg_top_k_strength', 'monitored_edge_strength', 'reasoning_steps'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for cycle in range(1, cycles + 1):
            print(f"\n{'='*80}")
            print(f"CYCLE {cycle}/{cycles}")
            print(f"{'='*80}")

            for query_idx, query in enumerate(queries):
                print(f"\n  Query {query_idx + 1}/{len(queries)}: {query[:60]}...")

                # Record edge strength before
                edge_strength_before = {}
                for subj, pred, obj in monitored_edges:
                    edge_strength_before[(subj, pred, obj)] = kg.get_edge_strength(subj, pred, obj)

                # Measure retrieval efficiency BEFORE reasoning
                retrieval_start = time.perf_counter()
                # extract potential entities from query for retrieval test
                query_words = query.split()
                query_entities = [word for word in query_words if word in kg.label_to_id]
                test_facts = []
                for ent_label in query_entities[:5]:  # limit to first 5 entities found
                    test_facts.extend(kg.query(subject=ent_label))
                retrieval_time_ms = (time.perf_counter() - retrieval_start) * 1000  # convert to ms
                facts_retrieved = len(test_facts)

                # Run query with timing
                start_time = time.time()
                try:
                    result = orchestrate(query, kg, anthropic_key, run_validation=True)
                    latency = time.time() - start_time

                    if not result:
                        print("    WARNING: Empty result")
                        continue

                    # Extract metrics
                    trust_score = result.get("trust_score", 0.0)
                    hebbian = result.get("hebbian_plasticity", {})
                    reasoning = result.get("reasoning", {})

                    edges_strengthened = hebbian.get("edges_strengthened", 0)
                    entities_activated = hebbian.get("entities_activated", 0)
                    emergent_edges = hebbian.get("emergent_edges", [])

                    # Get top-k edge strengths
                    top_k_edges = kg.get_strongest_edges(top_k=10)
                    avg_top_k_strength = np.mean([e[3] for e in top_k_edges]) if top_k_edges else 0.0

                    # Check monitored edge strength after
                    monitored_strength = 0.0
                    for subj, pred, obj in monitored_edges:
                        strength = kg.get_edge_strength(subj, pred, obj)
                        monitored_strength = max(monitored_strength, strength)

                    reasoning_steps = len(reasoning.get("reasoningPath", []))

                    writer.writerow({
                        'cycle': cycle,
                        'query_idx': query_idx,
                        'query': query,
                        'latency': latency,
                        'trust_score': trust_score,
                        'retrieval_time_ms': retrieval_time_ms,
                        'facts_retrieved': facts_retrieved,
                        'edges_strengthened': edges_strengthened,
                        'entities_activated': entities_activated,
                        'emergent_edges_count': len(emergent_edges),
                        'avg_top_k_strength': avg_top_k_strength,
                        'monitored_edge_strength': monitored_strength,
                        'reasoning_steps': reasoning_steps
                    })

                    print(f"    Trust: {trust_score:.3f}, Latency: {latency:.2f}s, "
                          f"Edges +{edges_strengthened}, Emergent: {len(emergent_edges)}")

                    if monitored_strength > 0:
                        print(f"    Monitored edge strength: {monitored_strength:.4f}")

                except Exception as e:
                    print(f"    ERROR: {str(e)}")
                    import traceback
                    traceback.print_exc()

            # Save KG state after each cycle
            kg_snapshot_path = output_path.replace('.csv', f'_kg_cycle_{cycle}.json')
            kg.save_to_json(kg_snapshot_path)
            print(f"\n  Saved KG snapshot to {kg_snapshot_path}")

    print(f"\n{'='*80}")
    print(f"Plasticity evaluation complete! Results saved to {output_path}")
    print(f"{'='*80}")


def main():
    parser = argparse.ArgumentParser(description="Enhanced Kairos Hebbian Plasticity Evaluation")
    parser.add_argument("--dataset", default="tests/comprehensive_evaluation_dataset.json",
                       help="Path to evaluation dataset")
    parser.add_argument("--kg-path", default="output/knowledge_graph.json",
                       help="Path to knowledge graph")
    parser.add_argument("--anthropic-key", required=True, help="Anthropic API key")
    parser.add_argument("--output-dir", default="output", help="Output directory")
    parser.add_argument("--cycles", type=int, default=20, help="Number of reasoning cycles (default: 20 for minimal viable)")
    parser.add_argument("--queries-per-cycle", type=int, default=10,
                       help="Number of queries per cycle (default: 10 for minimal viable)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--use-repeated-queries", action="store_true",
                       help="Use same queries each cycle (tests strengthening)")
    args = parser.parse_args()

    # Set random seed
    np.random.seed(args.seed)

    # Load KG
    print(f"Loading knowledge graph from {args.kg_path}...")
    kg = KnowledgeGraph()
    kg.load_from_json(args.kg_path)

    # Load dataset
    print(f"Loading evaluation dataset from {args.dataset}...")
    with open(args.dataset, 'r') as f:
        dataset = json.load(f)

    questions = dataset.get("evaluation_questions", dataset)
    if isinstance(questions, dict):
        questions = [questions]

    # Select queries for plasticity testing
    if args.use_repeated_queries:
        # Use same queries repeatedly to test edge strengthening
        plasticity_questions = [q.get("question", q.get("query", ""))
                               for q in questions[:args.queries_per_cycle]]
        print(f"Using {len(plasticity_questions)} repeated queries to test edge strengthening")
    else:
        # Use different queries each cycle
        if len(questions) < args.queries_per_cycle * args.cycles:
            # Sample with replacement if needed
            plasticity_questions = [
                questions[i % len(questions)].get("question", questions[i % len(questions)].get("query", ""))
                for i in range(args.queries_per_cycle * args.cycles)
            ]
        else:
            indices = np.random.choice(len(questions), args.queries_per_cycle, replace=False)
            plasticity_questions = [questions[i].get("question", questions[i].get("query", ""))
                                   for i in indices]

    # Prepare output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"plasticity_evaluation_results_{timestamp}.csv"
    output_path = os.path.join(args.output_dir, output_filename)
    os.makedirs(args.output_dir, exist_ok=True)

    # Run evaluation
    evaluate_plasticity(plasticity_questions, kg, args.anthropic_key, args.cycles, output_path)

    # Analyze results
    print("\nRunning statistical analysis...")
    import pandas as pd
    from scripts.statistical_analysis import analyze_plasticity_over_time

    df = pd.read_csv(output_path)

    print("\n" + "=" * 80)
    print("PLASTICITY ANALYSIS")
    print("=" * 80)

    # Overall trends
    print("\nTrend Analysis:")
    for metric in ['trust_score', 'avg_top_k_strength', 'latency', 'retrieval_time_ms', 'emergent_edges_count']:
        if metric in df.columns:
            try:
                analysis = analyze_plasticity_over_time(df, metric=metric)

                print(f"\n{metric.upper().replace('_', ' ')}:")
                print(f"  First cycle mean: {analysis['first_cycle_mean']:.4f}")
                print(f"  Last cycle mean: {analysis['last_cycle_mean']:.4f}")
                print(f"  Improvement: {analysis['improvement_pct']:.2f}%")
                print(f"  Trend slope: {analysis['trend_slope']:.6f}")
                print(f"  R²: {analysis['trend_r_squared']:.4f}")
                print(f"  Trend significant: {'YES' if analysis['trend_significant'] else 'NO'} "
                      f"(p={analysis['trend_p_value']:.4f})")

                if analysis['first_vs_last']['significant']:
                    print(f"  First vs Last: SIGNIFICANT (p={analysis['first_vs_last']['p_value']:.4f}, "
                          f"d={analysis['first_vs_last']['cohens_d']:.3f})")
            except Exception as e:
                print(f"  Error analyzing {metric}: {e}")

    # Per-cycle statistics
    print("\n\nPer-Cycle Statistics:")
    cycle_stats = df.groupby('cycle').agg({
        'trust_score': ['mean', 'std'],
        'avg_top_k_strength': ['mean', 'std'],
        'retrieval_time_ms': ['mean', 'std'],
        'facts_retrieved': 'mean',
        'edges_strengthened': 'sum',
        'emergent_edges_count': 'sum',
        'latency': 'mean'
    }).round(4)
    print(cycle_stats)

    # Save analysis
    analysis_path = output_path.replace('.csv', '_analysis.txt')
    with open(analysis_path, 'w') as f:
        f.write("HEBBIAN PLASTICITY EVALUATION ANALYSIS\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Configuration:\n")
        f.write(f"  Cycles: {args.cycles}\n")
        f.write(f"  Queries per cycle: {args.queries_per_cycle}\n")
        f.write(f"  Repeated queries: {args.use_repeated_queries}\n\n")
        f.write(cycle_stats.to_string())

    print(f"\nAnalysis saved to {analysis_path}")

    print("\n" + "=" * 80)
    print("PLASTICITY EVALUATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
