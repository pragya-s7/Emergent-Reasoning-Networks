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

def run_evaluation(hebbian_on: bool, num_cycles: int):
    """Runs the evaluation framework."""
    # Load components
    kg_path = 'tests/mock_kg_for_eval.json'
    dataset_path = 'tests/evaluation_dataset.json'
    
    with open(dataset_path, 'r') as f:
        evaluation_data = json.load(f)

    questions = evaluation_data['evaluation_questions']
    results = []

    print(f"--- Running Evaluation --- Hebbian Learning: {'ON' if hebbian_on else 'OFF'}, Cycles: {num_cycles} ---")

    for cycle in range(1, num_cycles + 1):
        print(f"\n--- Cycle {cycle} ---")
        # Load a fresh KG for each cycle to ensure consistent starting conditions
        kg = KnowledgeGraph()
        kg.load_from_json(kg_path)

        # If Hebbian is off, we can disable the plasticity methods to be safe
        if not hebbian_on:
            kg.consolidate_memory = lambda: None
            kg.activate_relation = lambda *args, **kwargs: None
            kg.activate_entities = lambda *args, **kwargs: None

        for i, item in enumerate(questions):
            question = item['question']
            print(f"  [Q{i+1}] Asking: {question}")

            # Run the orchestrator
            # Note: We are not passing an OpenAI key, so only non-LLM modules will fully function.
            # This is sufficient for testing the SecurityAuditReasoningModule and grounding.
            orchestrator_output = orchestrate(question, kg, run_validation=False)

            if orchestrator_output is None:
                print(f"    - DEBUG: Orchestrator returned None.")
                continue

            # --- Analyze the result ---
            conclusion = orchestrator_output.get('reasoning', {}).get('conclusion', '')
            grounding_vn = orchestrator_output.get('validation', {}).get('grounding', {})
            grounding_score = grounding_vn.get('score', 0.0)

            # Check accuracy
            accuracy = all(kw.lower() in conclusion.lower() for kw in item['expected_conclusion_keywords'])

            if not accuracy:
                print(f"    - DEBUG: Accuracy failed. Orchestrator output: {orchestrator_output}")

            # Log results
            results.append({
                'cycle': cycle,
                'question_id': i + 1,
                'question': question,
                'hebbian_on': hebbian_on,
                'accuracy': accuracy,
                'conclusion': conclusion,
                'grounding_score': grounding_score,
                'kg_total_relations_before': len(kg.relations),
            })
            
            print(f"    - Accuracy: {'Pass' if accuracy else 'Fail'}")
            print(f"    - Grounding Score: {grounding_score}")

        # Save the state of the KG after a full cycle if Hebbian is on
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

    print(f"\n--- Evaluation Complete ---")
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
