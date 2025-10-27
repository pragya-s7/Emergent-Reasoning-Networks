import argparse
import json
import os
import sys
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.knowledge_graph.knowledgeGraph import KnowledgeGraph
from core.orchestrator.index import orchestrate

import re

def run_evaluation(hebbian_on: bool, num_cycles: int):
    """Runs the evaluation framework."""
    kg_path = 'tests/mock_kg_for_eval.json'
    dataset_path = 'tests/evaluation_dataset.json'
    
    with open(dataset_path, 'r') as f:
        evaluation_data = json.load(f)

    questions = evaluation_data['evaluation_questions']
    results = []
    triple_pattern = re.compile(r"(.*?)\s*--(.+?)-->\s*(.*)")

    print(f"--- Running Evaluation --- Hebbian Learning: {'ON' if hebbian_on else 'OFF'}, Cycles: {num_cycles} ---")

    # Load a single KG instance to persist changes across cycles
    kg = KnowledgeGraph()
    kg.load_from_json(kg_path)
    print("--- Loaded KG ---")
    print(kg)
    print("-------------------")

    if not hebbian_on:
        kg.consolidate_memory = lambda: {"emergent_edges": [], "decayed_edges": 0}
        kg.activate_relation = lambda *args, **kwargs: None
        kg.activate_entities = lambda *args, **kwargs: None

    for cycle in range(1, num_cycles + 1):
        print(f"\n--- Cycle {cycle} ---")

        for i, item in enumerate(questions):
            question = item['question']
            key_triples = item['key_triples']
            print(f"  [Q{i+1}] Asking: {question}")

            # Get initial confidence of key triples
            initial_confidences = {}
            for t in key_triples:
                match = triple_pattern.match(t)
                if match:
                    subj, pred, obj = [s.strip() for s in match.groups()]
                    initial_confidences[t] = kg.get_edge_strength(subj, pred, obj)

            orchestrator_output = orchestrate(question, kg, run_validation=True)

            if orchestrator_output is None:
                print(f"    - DEBUG: Orchestrator returned None.")
                continue

            conclusion = orchestrator_output.get('reasoning', {}).get('conclusion', '')
            grounding_vn = orchestrator_output.get('validation', {}).get('grounding', {})
            grounding_score = grounding_vn.get('score', 0.0)
            accuracy = all(kw.lower() in conclusion.lower() for kw in item['expected_conclusion_keywords'])

            # Get final confidence and emergent edges
            final_confidences = {}
            for t in key_triples:
                match = triple_pattern.match(t)
                if match:
                    subj, pred, obj = [s.strip() for s in match.groups()]
                    final_confidences[t] = kg.get_edge_strength(subj, pred, obj)
            emergent_edges = orchestrator_output.get('hebbian_plasticity', {}).get('emergent_edges', [])

            if not accuracy:
                print(f"    - DEBUG: Accuracy failed. Orchestrator output: {orchestrator_output}")

            results.append({
                'cycle': cycle,
                'question_id': i + 1,
                'question': question,
                'hebbian_on': hebbian_on,
                'accuracy': accuracy,
                'grounding_score': grounding_score,
                'initial_confidence': json.dumps(initial_confidences),
                'final_confidence': json.dumps(final_confidences),
                'emergent_edges_created': len(emergent_edges) if isinstance(emergent_edges, list) else 0,
            })
            
            print(f"    - Accuracy: {'Pass' if accuracy else 'Fail'}")
            print(f"    - Grounding Score: {grounding_score}")

        if hebbian_on:
            output_kg_path = f'output/kg_after_cycle_{cycle}.json'
            kg.save_to_json(output_kg_path)
            print(f"  > Saved updated KG to {output_kg_path}")

    # --- Save results to CSV ---
    results_df = pd.DataFrame(results)
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_filename = os.path.join(output_dir, f'evaluation_results_{timestamp}.csv')
    results_df.to_csv(results_filename, index=False)

    # --- Print Summary --- 
    total_questions = len(results_df)
    correct_answers = len(results_df[results_df['accuracy'] == True])
    accuracy_percent = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

    print(f"\n--- Evaluation Summary ---")
    print(f"Total Questions: {total_questions}")
    print(f"Correct Answers: {correct_answers}")
    print(f"Accuracy: {accuracy_percent:.2f}%")
    print(f"Results saved to {results_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Kairos evaluation framework.")
    parser.add_argument(
        '--hebbian',
        action='store_true',
        help="Enable Hebbian learning during the evaluation."
    )
    parser.add_argument(
        '--cycles',
        type=int,
        default=3,
        help="Number of times to run through the evaluation dataset."
    )
    args = parser.parse_args()

    run_evaluation(hebbian_on=args.hebbian, num_cycles=args.cycles)
