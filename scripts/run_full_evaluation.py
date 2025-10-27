import argparse
import json
import os
import sys
import pandas as pd
from datetime import datetime
import re

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.knowledge_graph.knowledgeGraph import KnowledgeGraph
from core.orchestrator.index import orchestrate

def run_full_evaluation(openai_key: str, num_cycles: int):
    """Runs the full evaluation framework, including all validation nodes."""
    kg_path = 'tests/mock_kg_for_eval.json'
    dataset_path = 'tests/evaluation_dataset.json'
    
    with open(dataset_path, 'r') as f:
        evaluation_data = json.load(f)

    questions = evaluation_data['evaluation_questions']
    results = []
    triple_pattern = re.compile(r"(.*?)\s*--(.+?)-->\s*(.*)")

    print(f"--- Running Full Evaluation --- Hebbian Learning: ON, Cycles: {num_cycles} ---")

    kg = KnowledgeGraph()
    kg.load_from_json(kg_path)

    for cycle in range(1, num_cycles + 1):
        print(f"\n--- Cycle {cycle} ---")

        for i, item in enumerate(questions):
            question = item['question']
            key_triples = item['key_triples']
            print(f"  [Q{i+1}] Asking: {question}")

            initial_confidences = {}
            for t in key_triples:
                match = triple_pattern.match(t)
                if match:
                    subj, pred, obj = [s.strip() for s in match.groups()]
                    initial_confidences[t] = kg.get_edge_strength(subj, pred, obj)

            orchestrator_output = orchestrate(question, kg, openai_key=openai_key, run_validation=True)

            if orchestrator_output is None or 'reasoning' not in orchestrator_output:
                print(f"    - DEBUG: Orchestrator returned an invalid output.")
                continue

            conclusion = orchestrator_output['reasoning'].get('conclusion', '')
            validation = orchestrator_output.get('validation', {})
            accuracy = all(kw.lower() in conclusion.lower() for kw in item['expected_conclusion_keywords'])

            # Calculate trust score
            scores = [v.get('score', 0.0) for v in validation.values() if isinstance(v, dict)]
            trust_score = sum(scores) / len(scores) if scores else 0.0

            final_confidences = {}
            for t in key_triples:
                match = triple_pattern.match(t)
                if match:
                    subj, pred, obj = [s.strip() for s in match.groups()]
                    final_confidences[t] = kg.get_edge_strength(subj, pred, obj)
            
            emergent_edges = orchestrator_output.get('hebbian_plasticity', {}).get('emergent_edges', [])

            results.append({
                'cycle': cycle,
                'question_id': i + 1,
                'accuracy': accuracy,
                'trust_score': trust_score,
                'grounding_score': validation.get('grounding', {}).get('score', 0.0),
                'novelty_score': validation.get('novelty', {}).get('score', 0.0),
                'logical_score': validation.get('logical', {}).get('score', 0.0),
                'initial_confidence': json.dumps(initial_confidences),
                'final_confidence': json.dumps(final_confidences),
                'emergent_edges_created': len(emergent_edges) if isinstance(emergent_edges, list) else 0,
            })
            
            print(f"    - Accuracy: {'Pass' if accuracy else 'Fail'}")
            print(f"    - Trust Score: {trust_score:.2f}")

        output_kg_path = f'output/kg_after_full_eval_cycle_{cycle}.json'
        kg.save_to_json(output_kg_path)
        print(f"  > Saved updated KG to {output_kg_path}")

    results_df = pd.DataFrame(results)
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_filename = os.path.join(output_dir, f'full_evaluation_results_{timestamp}.csv')
    results_df.to_csv(results_filename, index=False)

    print(f"\n--- Full Evaluation Complete ---")
    print(f"Results saved to {results_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Kairos full evaluation framework.")
    parser.add_argument("--openai-key", required=True, help="OpenAI API key")
    parser.add_argument("--cycles", type=int, default=5, help="Number of evaluation cycles.")
    args = parser.parse_args()

    run_full_evaluation(openai_key=args.openai_key, num_cycles=args.cycles)
