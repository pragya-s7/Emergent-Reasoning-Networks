"""
Quick Baseline Comparison Evaluation.

Tests Kairos (full system) against 4 baselines on a subset of questions.
Designed to run quickly for workshop paper evaluation.
"""

import argparse
import json
import os
import sys
import csv
import time
import numpy as np
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.knowledge_graph.knowledgeGraph import KnowledgeGraph
from core.orchestrator.index import orchestrate
from scripts.baselines import (
    NaiveKGQueryBaseline,
    SingleAgentBaseline,
    NoValidationBaseline,
    NoHebbianBaseline
)


def main():
    parser = argparse.ArgumentParser(description="Quick Baseline Comparison for Kairos")
    parser.add_argument("--dataset", default="tests/comprehensive_evaluation_dataset.json",
                       help="Path to evaluation dataset")
    parser.add_argument("--kg-path", default="output/knowledge_graph.json",
                       help="Path to knowledge graph")
    parser.add_argument("--anthropic-key", required=True, help="Anthropic API key")
    parser.add_argument("--output-dir", default="output", help="Output directory")
    parser.add_argument("--n-questions", type=int, default=10,
                       help="Number of questions to test (default: 10)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

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

    # Sample questions (prefer simple ones for fair baseline comparison)
    simple_questions = [q for q in questions if not q.get("requires_multi_hop", False)]
    if len(simple_questions) < args.n_questions:
        simple_questions = questions  # Use all if not enough simple ones

    if len(simple_questions) > args.n_questions:
        indices = np.random.choice(len(simple_questions), args.n_questions, replace=False)
        test_questions = [simple_questions[i] for i in indices]
    else:
        test_questions = simple_questions[:args.n_questions]

    print(f"Testing {len(test_questions)} questions across 5 systems...")

    # Prepare output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"baseline_comparison_results_{timestamp}.csv"
    output_path = os.path.join(args.output_dir, output_filename)
    os.makedirs(args.output_dir, exist_ok=True)

    # Initialize baselines
    baselines = {
        "kairos_full": None,  # Full Kairos system
        "naive_kg": NaiveKGQueryBaseline(),
        "single_agent": SingleAgentBaseline(),
        "no_validation": NoValidationBaseline(),
        "no_hebbian": NoHebbianBaseline()
    }

    with open(output_path, 'w', newline='') as csvfile:
        fieldnames = [
            'question_id', 'question', 'baseline_type',
            'trust_score', 'latency', 'conclusion_length',
            'reasoning_steps', 'has_conclusion'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        total_runs = len(test_questions) * len(baselines)
        current_run = 0

        for idx, item in enumerate(test_questions):
            question = item.get('question', item.get('query', ''))
            question_id = item.get('id', f'q_{idx}')

            print(f"\n{'='*80}")
            print(f"Question {idx+1}/{len(test_questions)}: {question[:60]}...")
            print(f"{'='*80}")

            for baseline_name, baseline_obj in baselines.items():
                current_run += 1
                print(f"\n  [{current_run}/{total_runs}] Testing: {baseline_name}")

                # Create fresh KG copy for each run
                kg_copy = KnowledgeGraph()
                kg_copy.load_from_json(args.kg_path)

                start_time = time.time()

                try:
                    if baseline_name == "kairos_full":
                        # Full Kairos system
                        result = orchestrate(question, kg_copy, args.anthropic_key, run_validation=True)
                        reasoning = result.get("reasoning", {})
                        validation = result.get("validation", {})

                        trust_score = result.get("trust_score", 0.0)
                        conclusion = reasoning.get("conclusion", "")
                        reasoning_steps = len(reasoning.get("reasoningPath", []))

                    elif baseline_name == "naive_kg":
                        # Naive KG query (no API call needed)
                        result = baseline_obj.run(question, kg_copy)

                        trust_score = 0.0  # No validation for naive baseline
                        conclusion = result.get("conclusion", "")
                        reasoning_steps = len(result.get("reasoningPath", []))

                    elif baseline_name == "single_agent":
                        # Single agent LLM
                        result = baseline_obj.run(question, kg_copy, args.anthropic_key)

                        trust_score = 0.0  # No validation for single agent
                        conclusion = result.get("conclusion", "")
                        reasoning_steps = len(result.get("reasoningPath", []))

                    elif baseline_name == "no_validation":
                        # No validation baseline
                        result = baseline_obj.run(question, kg_copy, args.anthropic_key)
                        reasoning = result.get("reasoning", {})

                        trust_score = 0.0  # No validation
                        conclusion = reasoning.get("conclusion", "")
                        reasoning_steps = len(reasoning.get("reasoningPath", []))

                    elif baseline_name == "no_hebbian":
                        # No Hebbian baseline
                        result = baseline_obj.run(question, kg_copy, args.anthropic_key)

                        trust_score = result.get("trust_score", 0.0)
                        reasoning = result.get("reasoning", {})
                        conclusion = reasoning.get("conclusion", "")
                        reasoning_steps = len(reasoning.get("reasoningPath", []))

                    latency = time.time() - start_time

                    writer.writerow({
                        'question_id': question_id,
                        'question': question,
                        'baseline_type': baseline_name,
                        'trust_score': trust_score,
                        'latency': latency,
                        'conclusion_length': len(conclusion),
                        'reasoning_steps': reasoning_steps,
                        'has_conclusion': bool(conclusion)
                    })

                    if baseline_name in ["naive_kg", "single_agent", "no_validation"] and trust_score == 0.0:
                        print("      (NOTE: Trust score is 0.0 by design for this baseline as it does not use the validation framework.)")
                    print(f"    Trust: {trust_score:.3f}, Latency: {latency:.2f}s, Steps: {reasoning_steps}")

                except Exception as e:
                    print(f"    ERROR: {str(e)}")
                    import traceback
                    traceback.print_exc()

                    latency = time.time() - start_time
                    writer.writerow({
                        'question_id': question_id,
                        'question': question,
                        'baseline_type': baseline_name,
                        'trust_score': 0.0,
                        'latency': latency,
                        'conclusion_length': 0,
                        'reasoning_steps': 0,
                        'has_conclusion': False
                    })

    print(f"\n{'='*80}")
    print(f"Baseline comparison complete! Results saved to {output_path}")
    print(f"{'='*80}")

    # Quick analysis
    print("\nRunning statistical analysis...")
    import pandas as pd
    df = pd.read_csv(output_path)

    print("\n" + "="*80)
    print("BASELINE COMPARISON ANALYSIS")
    print("="*80)

    for baseline in ["kairos_full", "naive_kg", "single_agent", "no_validation", "no_hebbian"]:
        subset = df[df['baseline_type'] == baseline]
        if len(subset) > 0:
            print(f"\n{baseline.upper().replace('_', ' ')}:")
            print(f"  N: {len(subset)}")
            print(f"  Trust score: {subset['trust_score'].mean():.3f} ± {subset['trust_score'].std():.3f}")
            print(f"  Avg latency: {subset['latency'].mean():.2f}s")
            print(f"  Avg reasoning steps: {subset['reasoning_steps'].mean():.1f}")
            print(f"  Success rate: {subset['has_conclusion'].mean()*100:.1f}%")

    # Compare Kairos vs baselines
    kairos_scores = df[df['baseline_type'] == 'kairos_full']['trust_score'].tolist()

    if len(kairos_scores) > 0:
        print("\n" + "="*80)
        print("KAIROS vs BASELINES")
        print("="*80)

        for baseline in ["naive_kg", "single_agent", "no_validation", "no_hebbian"]:
            baseline_scores = df[df['baseline_type'] == baseline]['trust_score'].tolist()

            if len(baseline_scores) > 0 and len(kairos_scores) > 0:
                from scipy import stats

                # Independent t-test (different samples for each baseline)
                t_stat, p_value = stats.ttest_ind(kairos_scores, baseline_scores)

                improvement = ((np.mean(kairos_scores) - np.mean(baseline_scores)) /
                              np.mean(baseline_scores) * 100 if np.mean(baseline_scores) > 0 else 0)

                print(f"\nKairos vs {baseline.replace('_', ' ').title()}:")
                print(f"  Kairos: M={np.mean(kairos_scores):.3f}")
                print(f"  {baseline}: M={np.mean(baseline_scores):.3f}")
                print(f"  Improvement: {improvement:+.1f}%")
                print(f"  t-statistic: {t_stat:.3f}")
                print(f"  p-value: {p_value:.4f}")
                print(f"  Significant: {'YES' if p_value < 0.05 else 'NO'}")

    print("\n" + "="*80)
    print("BASELINE COMPARISON COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
