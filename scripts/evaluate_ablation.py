import argparse
import json
import os
import sys
import csv
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.knowledge_graph.knowledgeGraph import KnowledgeGraph
from core.orchestrator.index import orchestrate

def main():
    parser = argparse.ArgumentParser(description="Kairos Ablation Study Evaluation Script")
    parser.add_argument("--dataset", default="tests/evaluation_dataset.json", help="Path to evaluation dataset")
    parser.add_argument("--kg-path", default="output/knowledge_graph.json", help="Path to knowledge graph")
    parser.add_argument("--anthropic-key", required=True, help="OpenAI API key")
    parser.add_argument("--output-dir", default="output", help="Output directory")
    args = parser.parse_args()

    # Load knowledge graph
    kg = KnowledgeGraph()
    kg.load_from_json(args.kg_path)

    # Load dataset
    with open(args.dataset, 'r') as f:
        dataset = json.load(f)

    # Prepare output file
    output_filename = f"ablation_evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    output_path = os.path.join(args.output_dir, output_filename)
    with open(output_path, 'w', newline='') as csvfile:
        fieldnames = ['query', 'ablation_condition', 'trust_score', 'logical_score', 'grounding_score', 'novelty_score', 'alignment_score']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Define ablation conditions
        ablation_conditions = {
            "full_system": {"run_validation": True, "apply_hebbian": True},
            "no_validation": {"run_validation": False, "apply_hebbian": True},
            "no_hebbian": {"run_validation": True, "apply_hebbian": False},
            "no_logical_vn": {"run_validation": True, "apply_hebbian": True, "disabled_vn": "logical"},
            "no_grounding_vn": {"run_validation": True, "apply_hebbian": True, "disabled_vn": "grounding"},
            "no_novelty_vn": {"run_validation": True, "apply_hebbian": True, "disabled_vn": "novelty"},
            "no_alignment_vn": {"run_validation": True, "apply_hebbian": True, "disabled_vn": "alignment"},
        }

        for condition_name, condition_params in ablation_conditions.items():
            print(f"Running ablation condition: {condition_name}...")
            for item in dataset:
                query = item['query']

                # Monkey patch the orchestrate function to control plasticity
                original_apply_hebbian = orchestrate.apply_hebbian_learning
                if not condition_params['apply_hebbian']:
                    orchestrate.apply_hebbian_learning = lambda a, b, c: {}

                # Disable a validation node if specified
                disabled_vn = condition_params.get('disabled_vn')
                if disabled_vn:
                    original_vn = orchestrate.VN_REGISTRY[disabled_vn]
                    del orchestrate.VN_REGISTRY[disabled_vn]

                result = orchestrate(query, kg, args.anthropic_key, run_validation=condition_params['run_validation'])
                
                # Restore monkey patching
                orchestrate.apply_hebbian_learning = original_apply_hebbian
                if disabled_vn:
                    orchestrate.VN_REGISTRY[disabled_vn] = original_vn

                writer.writerow({
                    'query': query,
                    'ablation_condition': condition_name,
                    'trust_score': result.get('trust_score', 0),
                    'logical_score': result.get('validation', {}).get('logical', {}).get('score', 0),
                    'grounding_score': result.get('validation', {}).get('grounding', {}).get('score', 0),
                    'novelty_score': result.get('validation', {}).get('novelty', {}).get('score', 0),
                    'alignment_score': result.get('validation', {}).get('alignment', {}).get('score', 0),
                })

    print(f"Evaluation complete. Results saved to {output_path}")

if __name__ == "__main__":
    main()
