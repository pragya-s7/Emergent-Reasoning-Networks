"""
Fixed and Enhanced Ablation Study Evaluation Script.

Tests the contribution of each system component by systematically removing them:
1. Full system (baseline)
2. No validation layer
3. No Hebbian plasticity
4. No individual validation nodes (logical, grounding, novelty, alignment)
5. No specialized modules (use single agent)

Expected: Performance degrades when components are removed.
"""

import argparse
import json
import os
import sys
import csv
import numpy as np
import copy
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.knowledge_graph.knowledgeGraph import KnowledgeGraph
from core.orchestrator.index import orchestrate
import core.orchestrator.index as orchestrator_module


def run_with_ablation(query: str, kg: KnowledgeGraph, anthropic_key: str,
                      ablation_type: str) -> dict:
    """
    Run orchestrator with specific component ablated (removed).

    Args:
        query: Query to process
        kg: Knowledge graph
        anthropic_key: API key
        ablation_type: Which component to remove

    Returns:
        Result dict with reasoning and validation
    """
    # Create a copy of the KG to avoid state pollution
    kg_copy = copy.deepcopy(kg)

    if ablation_type == "full_system":
        # Baseline - all components active
        result = orchestrate(query, kg_copy, anthropic_key, run_validation=True)

    elif ablation_type == "no_validation":
        # Remove entire validation layer
        result = orchestrate(query, kg_copy, anthropic_key, run_validation=False)
        # Add empty validation for consistent structure
        if "validation" not in result:
            result["validation"] = {}

    elif ablation_type == "no_hebbian":
        # Disable Hebbian learning
        original_apply_hebbian = orchestrator_module.apply_hebbian_learning

        def no_op_hebbian(kg_arg, reasoning, validation):
            return {
                "edges_strengthened": 0,
                "entities_activated": 0,
                "emergent_edges": [],
                "decayed_edges": 0
            }

        orchestrator_module.apply_hebbian_learning = no_op_hebbian
        try:
            result = orchestrate(query, kg_copy, anthropic_key, run_validation=True)
        finally:
            orchestrator_module.apply_hebbian_learning = original_apply_hebbian

    elif ablation_type.startswith("no_") and ablation_type.endswith("_vn"):
        # Remove specific validation node
        vn_name = ablation_type.replace("no_", "").replace("_vn", "")

        original_registry = copy.deepcopy(orchestrator_module.VN_REGISTRY)
        if vn_name in orchestrator_module.VN_REGISTRY:
            del orchestrator_module.VN_REGISTRY[vn_name]

        try:
            result = orchestrate(query, kg_copy, anthropic_key, run_validation=True)
        finally:
            orchestrator_module.VN_REGISTRY = original_registry

    else:
        raise ValueError(f"Unknown ablation type: {ablation_type}")

    # Add ablation metadata
    if result:
        result["ablation_type"] = ablation_type

    return result


def main():
    parser = argparse.ArgumentParser(description="Enhanced Kairos Ablation Study")
    parser.add_argument("--dataset", default="tests/comprehensive_evaluation_dataset.json",
                       help="Path to evaluation dataset")
    parser.add_argument("--kg-path", default="output/knowledge_graph.json",
                       help="Path to knowledge graph")
    parser.add_argument("--anthropic-key", required=True, help="Anthropic API key")
    parser.add_argument("--output-dir", default="output", help="Output directory")
    parser.add_argument("--n-questions", type=int, default=30,
                       help="Number of questions per ablation (default: 30)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
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

    # Sample questions
    if len(questions) > args.n_questions:
        indices = np.random.choice(len(questions), args.n_questions, replace=False)
        questions = [questions[i] for i in indices]

    print(f"Evaluating {len(questions)} questions across ablation conditions...")

    # Define ablation conditions
    ablation_conditions = [
        "full_system",
        "no_validation",
        "no_hebbian",
        "no_logical_vn",
        "no_grounding_vn",
        "no_novelty_vn",
        "no_alignment_vn"
    ]

    # Prepare output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"ablation_evaluation_results_{timestamp}.csv"
    output_path = os.path.join(args.output_dir, output_filename)
    os.makedirs(args.output_dir, exist_ok=True)

    with open(output_path, 'w', newline='') as csvfile:
        fieldnames = [
            'ablation_condition', 'question_id', 'question',
            'trust_score', 'logical_score', 'grounding_score',
            'novelty_score', 'alignment_score', 'conclusion_length',
            'reasoning_steps', 'hebbian_edges_strengthened', 'hebbian_emergent_edges'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        total_runs = len(ablation_conditions) * len(questions)
        current_run = 0

        for condition in ablation_conditions:
            print(f"\n{'='*80}")
            print(f"ABLATION CONDITION: {condition}")
            print(f"{'='*80}")

            for idx, item in enumerate(questions):
                current_run += 1
                question = item.get('question', item.get('query', ''))
                question_id = item.get('id', f'q_{idx}')

                print(f"\n[{current_run}/{total_runs}] {condition}: {question[:50]}...")

                try:
                    result = run_with_ablation(question, kg, args.anthropic_key, condition)

                    if not result:
                        print("  WARNING: Empty result")
                        continue

                    # Extract metrics
                    validation = result.get("validation", {})
                    reasoning = result.get("reasoning", {})
                    hebbian = result.get("hebbian_plasticity", {})

                    trust_score = result.get("trust_score", 0.0)

                    # Handle missing validation scores
                    logical_score = validation.get("logical", {}).get("score", 0.0) if "logical" in validation else 0.0
                    grounding_score = validation.get("grounding", {}).get("score", 0.0) if "grounding" in validation else 0.0
                    novelty_score = validation.get("novelty", {}).get("score", 0.0) if "novelty" in validation else 0.0
                    alignment_score = validation.get("alignment", {}).get("score", 0.0) if "alignment" in validation else 0.0

                    conclusion = reasoning.get("conclusion", "")
                    reasoning_path = reasoning.get("reasoningPath", [])

                    writer.writerow({
                        'ablation_condition': condition,
                        'question_id': question_id,
                        'question': question,
                        'trust_score': trust_score,
                        'logical_score': logical_score,
                        'grounding_score': grounding_score,
                        'novelty_score': novelty_score,
                        'alignment_score': alignment_score,
                        'conclusion_length': len(conclusion),
                        'reasoning_steps': len(reasoning_path),
                        'hebbian_edges_strengthened': hebbian.get("edges_strengthened", 0),
                        'hebbian_emergent_edges': len(hebbian.get("emergent_edges", []))
                    })

                    print(f"  Trust score: {trust_score:.3f}")

                except Exception as e:
                    print(f"  ERROR: {str(e)}")
                    import traceback
                    traceback.print_exc()

    print(f"\n{'='*80}")
    print(f"Ablation study complete! Results saved to {output_path}")
    print(f"{'='*80}")

    # Run statistical analysis
    print("\nRunning statistical analysis...")
    import pandas as pd
    from scripts.statistical_analysis import analyze_ablation_study, generate_statistical_report

    df = pd.read_csv(output_path)

    print("\n" + "=" * 80)
    print("ABLATION STUDY ANALYSIS")
    print("=" * 80)

    # Summary statistics by condition
    for condition in ablation_conditions:
        subset = df[df['ablation_condition'] == condition]
        if len(subset) > 0:
            print(f"\n{condition.upper().replace('_', ' ')}:")
            print(f"  N: {len(subset)}")
            print(f"  Trust score: {subset['trust_score'].mean():.3f} ± {subset['trust_score'].std():.3f}")
            print(f"  Logical: {subset['logical_score'].mean():.3f}")
            print(f"  Grounding: {subset['grounding_score'].mean():.3f}")
            print(f"  Novelty: {subset['novelty_score'].mean():.3f}")
            print(f"  Alignment: {subset['alignment_score'].mean():.3f}")
            print(f"  Reasoning steps: {subset['reasoning_steps'].mean():.1f}")

    # Statistical comparison to full system
    try:
        analysis = analyze_ablation_study(df, metric="trust_score")
        report = generate_statistical_report(analysis)
        print("\n" + report)

        # Save analysis to JSON
        analysis_path = output_path.replace('.csv', '_analysis.json')
        with open(analysis_path, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"\nDetailed analysis saved to {analysis_path}")

    except Exception as e:
        print(f"\nError in statistical analysis: {e}")

    print("\n" + "=" * 80)
    print("ABLATION STUDY COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
