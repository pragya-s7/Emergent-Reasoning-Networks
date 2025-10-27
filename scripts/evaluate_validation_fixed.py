"""
Fixed and Enhanced Validation Evaluation Script.

Tests whether validation nodes effectively catch flawed reasoning by comparing:
1. Standard reasoning modules (clean)
2. Noisy/flawed reasoning modules (intentionally buggy)

Expected: Validation scores should be significantly lower for noisy modules.
"""

import argparse
import json
import os
import sys
import csv
import numpy as np
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.knowledge_graph.knowledgeGraph import KnowledgeGraph
from core.orchestrator.index import orchestrate, RM_REGISTRY
from reasoning_modules.base.module import ReasoningModule


class NoisyLogicalFallacyModule(ReasoningModule):
    """
    Intentionally produces reasoning with logical fallacies for testing validation.
    """

    def __init__(self):
        super().__init__('noisy-logical-fallacy')

    def run(self, query: str, knowledge_graph: KnowledgeGraph) -> dict:
        reasoning_path = [
            {
                "step": "Step 1",
                "data": "Some systems have vulnerabilities",
                "source": "General Knowledge",
                "inference": "All systems with vulnerabilities are unsafe"  # Overgeneralization
            },
            {
                "step": "Step 2",
                "data": "The sky is blue",
                "source": "Observation",
                "inference": "Therefore, we should not use any systems"  # Non-sequitur
            },
            {
                "step": "Step 3",
                "data": "Security is important",
                "source": "Common Sense",
                "inference": "Thus, all contracts are either perfect or worthless"  # False dichotomy
            }
        ]

        return {
            "subquery": query,
            "timestamp": datetime.now().isoformat(),
            "reasoningPath": reasoning_path,
            "sources": {"test": "Noisy Module"},
            "conclusion": "All systems are unsafe because the sky is blue and there are no middle grounds in security",
            "confidence": 0.95,  # Ironically high confidence
            "source_triples": [],
            "relevantMetrics": {},
            "module_used": "noisy_logical_fallacy"
        }


class NoisyUngroundedModule(ReasoningModule):
    """
    Makes claims not supported by the knowledge graph (hallucination test).
    """

    def __init__(self):
        super().__init__('noisy-ungrounded')

    def run(self, query: str, knowledge_graph: KnowledgeGraph) -> dict:
        # Make up facts that don't exist in KG
        reasoning_path = [
            {
                "step": "Step 1",
                "data": "ApolloContract was certified by NASA",  # Made up
                "source": "Fabricated Database",
                "inference": "NASA-certified contracts are always secure"
            },
            {
                "step": "Step 2",
                "data": "ApolloContract has quantum encryption",  # Made up
                "source": "Imaginary Spec",
                "inference": "Quantum encryption prevents all attacks"
            }
        ]

        return {
            "subquery": query,
            "timestamp": datetime.now().isoformat(),
            "reasoningPath": reasoning_path,
            "sources": {"test": "Noisy Module"},
            "conclusion": "ApolloContract is perfectly secure due to NASA certification and quantum encryption",
            "confidence": 0.99,
            "source_triples": [
                "ApolloContract --certified_by--> NASA",  # Not in KG
                "ApolloContract --has_encryption--> QuantumEncryption"  # Not in KG
            ],
            "relevantMetrics": {},
            "module_used": "noisy_ungrounded"
        }


class NoisyLowNoveltyModule(ReasoningModule):
    """
    Produces obvious, redundant reasoning with no insights.
    """

    def __init__(self):
        super().__init__('noisy-low-novelty')

    def run(self, query: str, knowledge_graph: KnowledgeGraph) -> dict:
        reasoning_path = [
            {
                "step": "Step 1",
                "data": "Contracts exist",
                "source": "Obvious",
                "inference": "Therefore contracts exist"  # Tautology
            },
            {
                "step": "Step 2",
                "data": "Security is about security",
                "source": "Definition",
                "inference": "Secure things are secure"  # Circular
            }
        ]

        return {
            "subquery": query,
            "timestamp": datetime.now().isoformat(),
            "reasoningPath": reasoning_path,
            "sources": {"test": "Noisy Module"},
            "conclusion": "Things are as they are",  # Completely uninformative
            "confidence": 1.0,
            "source_triples": [],
            "relevantMetrics": {},
            "module_used": "noisy_low_novelty"
        }


def main():
    parser = argparse.ArgumentParser(description="Enhanced Kairos Validation Evaluation")
    parser.add_argument("--dataset", default="tests/comprehensive_evaluation_dataset.json",
                       help="Path to evaluation dataset")
    parser.add_argument("--kg-path", default="output/knowledge_graph.json", help="Path to knowledge graph")
    parser.add_argument("--anthropic-key", required=True, help="Anthropic API key")
    parser.add_argument("--output-dir", default="output", help="Output directory")
    parser.add_argument("--n-questions", type=int, default=20,
                       help="Number of questions to evaluate (default: 20)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    args = parser.parse_args()

    # Set random seed for reproducibility
    np.random.seed(args.seed)

    # Load knowledge graph
    print(f"Loading knowledge graph from {args.kg_path}...")
    kg = KnowledgeGraph()
    kg.load_from_json(args.kg_path)

    # Load dataset
    print(f"Loading evaluation dataset from {args.dataset}...")
    with open(args.dataset, 'r') as f:
        dataset = json.load(f)

    questions = dataset.get("evaluation_questions", dataset)
    if isinstance(questions, dict):
        questions = [questions]  # Handle single question case

    # Sample questions if dataset is large
    if len(questions) > args.n_questions:
        indices = np.random.choice(len(questions), args.n_questions, replace=False)
        questions = [questions[i] for i in indices]

    print(f"Evaluating {len(questions)} questions...")

    # Prepare output file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"validation_evaluation_results_{timestamp}.csv"
    output_path = os.path.join(args.output_dir, output_filename)

    os.makedirs(args.output_dir, exist_ok=True)

    with open(output_path, 'w', newline='') as csvfile:
        fieldnames = [
            'question_id', 'question', 'module_type', 'trust_score',
            'logical_score', 'grounding_score', 'novelty_score', 'alignment_score',
            'validation_caught_issue', 'module_confidence'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Test each question with different module types
        for idx, item in enumerate(questions):
            question = item.get('question', item.get('query', ''))
            question_id = item.get('id', f'q_{idx}')

            print(f"\n[{idx+1}/{len(questions)}] Testing: {question[:60]}...")

            # 1. Test with standard module
            print("  Running standard module...")
            try:
                standard_result = orchestrate(question, kg, args.anthropic_key, run_validation=True)

                if standard_result and "validation" in standard_result:
                    writer.writerow({
                        'question_id': question_id,
                        'question': question,
                        'module_type': 'standard',
                        'trust_score': standard_result.get('trust_score', 0),
                        'logical_score': standard_result['validation'].get('logical', {}).get('score', 0),
                        'grounding_score': standard_result['validation'].get('grounding', {}).get('score', 0),
                        'novelty_score': standard_result['validation'].get('novelty', {}).get('score', 0),
                        'alignment_score': standard_result['validation'].get('alignment', {}).get('score', 0),
                        'validation_caught_issue': False,
                        'module_confidence': standard_result.get('reasoning', {}).get('confidence', 0)
                    })
            except Exception as e:
                print(f"    Error with standard module: {e}")

            # 2. Test with noisy logical fallacy module
            print("  Running noisy logical module...")
            try:
                noisy_logical = NoisyLogicalFallacyModule()
                reasoning = noisy_logical.run(question, kg)

                # Manually run validation nodes
                from validation_nodes.logical_vn import run_logical_vn
                from validation_nodes.grounding_vn import run_grounding_vn
                from validation_nodes.novelty_vn import run_novelty_vn
                from validation_nodes.alignment_vn import run_alignment_vn

                validation = {}
                try:
                    validation['logical'] = run_logical_vn(reasoning, args.anthropic_key)
                except Exception as e:
                    validation['logical'] = {"score": 0, "valid": False}

                try:
                    validation['grounding'] = run_grounding_vn(reasoning, kg)
                except Exception as e:
                    validation['grounding'] = {"score": 0, "valid": False}

                try:
                    validation['novelty'] = run_novelty_vn(reasoning, kg, args.anthropic_key)
                except Exception as e:
                    validation['novelty'] = {"score": 0, "valid": False}

                try:
                    validation['alignment'] = run_alignment_vn(reasoning, args.anthropic_key)
                except Exception as e:
                    validation['alignment'] = {"score": 0, "valid": False}

                trust_score = np.mean([v.get('score', 0) for v in validation.values()])
                caught_issue = trust_score < 0.7  # Threshold for catching issues

                writer.writerow({
                    'question_id': question_id,
                    'question': question,
                    'module_type': 'noisy_logical',
                    'trust_score': trust_score,
                    'logical_score': validation.get('logical', {}).get('score', 0),
                    'grounding_score': validation.get('grounding', {}).get('score', 0),
                    'novelty_score': validation.get('novelty', {}).get('score', 0),
                    'alignment_score': validation.get('alignment', {}).get('score', 0),
                    'validation_caught_issue': caught_issue,
                    'module_confidence': reasoning.get('confidence', 0)
                })
            except Exception as e:
                print(f"    Error with noisy logical module: {e}")

            # 3. Test with ungrounded module
            print("  Running ungrounded module...")
            try:
                noisy_ungrounded = NoisyUngroundedModule()
                reasoning = noisy_ungrounded.run(question, kg)

                validation = {}
                try:
                    validation['logical'] = run_logical_vn(reasoning, args.anthropic_key)
                except:
                    validation['logical'] = {"score": 0, "valid": False}

                try:
                    validation['grounding'] = run_grounding_vn(reasoning, kg)
                except:
                    validation['grounding'] = {"score": 0, "valid": False}

                try:
                    validation['novelty'] = run_novelty_vn(reasoning, kg, args.anthropic_key)
                except:
                    validation['novelty'] = {"score": 0, "valid": False}

                try:
                    validation['alignment'] = run_alignment_vn(reasoning, args.anthropic_key)
                except:
                    validation['alignment'] = {"score": 0, "valid": False}

                trust_score = np.mean([v.get('score', 0) for v in validation.values()])
                caught_issue = trust_score < 0.7

                writer.writerow({
                    'question_id': question_id,
                    'question': question,
                    'module_type': 'noisy_ungrounded',
                    'trust_score': trust_score,
                    'logical_score': validation.get('logical', {}).get('score', 0),
                    'grounding_score': validation.get('grounding', {}).get('score', 0),
                    'novelty_score': validation.get('novelty', {}).get('score', 0),
                    'alignment_score': validation.get('alignment', {}).get('score', 0),
                    'validation_caught_issue': caught_issue,
                    'module_confidence': reasoning.get('confidence', 0)
                })
            except Exception as e:
                print(f"    Error with ungrounded module: {e}")

    print(f"\nEvaluation complete! Results saved to {output_path}")
    print("\nRunning statistical analysis...")

    # Run statistical analysis
    import pandas as pd
    df = pd.read_csv(output_path)

    print("\n" + "=" * 80)
    print("VALIDATION EFFECTIVENESS ANALYSIS")
    print("=" * 80)

    for module_type in ['standard', 'noisy_logical', 'noisy_ungrounded']:
        subset = df[df['module_type'] == module_type]
        if len(subset) > 0:
            print(f"\n{module_type.upper()}:")
            print(f"  Mean trust score: {subset['trust_score'].mean():.3f} ± {subset['trust_score'].std():.3f}")
            print(f"  Logical score: {subset['logical_score'].mean():.3f}")
            print(f"  Grounding score: {subset['grounding_score'].mean():.3f}")
            print(f"  Novelty score: {subset['novelty_score'].mean():.3f}")
            if module_type.startswith('noisy'):
                caught_rate = subset['validation_caught_issue'].mean()
                print(f"  Issues caught: {caught_rate * 100:.1f}%")

    # Compare standard vs noisy
    standard_scores = df[df['module_type'] == 'standard']['trust_score'].tolist()
    noisy_logical_scores = df[df['module_type'] == 'noisy_logical']['trust_score'].tolist()
    noisy_ungrounded_scores = df[df['module_type'] == 'noisy_ungrounded']['trust_score'].tolist()

    if len(standard_scores) > 0 and len(noisy_logical_scores) > 0:
        from scipy import stats
        t_stat, p_value = stats.ttest_ind(standard_scores, noisy_logical_scores)
        print(f"\nStandard vs Noisy Logical:")
        print(f"  t-statistic: {t_stat:.3f}")
        print(f"  p-value: {p_value:.4f}")
        print(f"  Significant: {'YES' if p_value < 0.05 else 'NO'}")

    if len(standard_scores) > 0 and len(noisy_ungrounded_scores) > 0:
        t_stat, p_value = stats.ttest_ind(standard_scores, noisy_ungrounded_scores)
        print(f"\nStandard vs Noisy Ungrounded:")
        print(f"  t-statistic: {t_stat:.3f}")
        print(f"  p-value: {p_value:.4f}")
        print(f"  Significant: {'YES' if p_value < 0.05 else 'NO'}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
