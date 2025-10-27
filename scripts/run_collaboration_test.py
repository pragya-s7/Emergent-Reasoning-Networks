import json
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.knowledge_graph.knowledgeGraph import KnowledgeGraph
from core.orchestrator.index import orchestrate

def run_collaboration_test():
    """Runs the collaboration test."""
    # Load components
    kg_path = 'tests/mock_kg_for_eval.json' # Using the same mock KG for simplicity
    dataset_path = 'tests/collaboration_test_dataset.json'
    
    with open(dataset_path, 'r') as f:
        test_data = json.load(f)

    question_data = test_data['collaboration_questions'][0]
    question = question_data['question']

    print(f"--- Running Collaboration Test ---")
    print(f"  Asking: {question}")

    kg = KnowledgeGraph()
    kg.load_from_json(kg_path)

    # Run the orchestrator
    orchestrator_output = orchestrate(question, kg, run_validation=False)

    # --- Analyze the result ---
    if orchestrator_output and 'reasoning' in orchestrator_output:
        module_used = orchestrator_output['reasoning'].get('module_used', '')
        conclusion = orchestrator_output['reasoning'].get('conclusion', '')

        print(f"  - Module(s) used: {module_used}")
        print(f"  - Conclusion: {conclusion}")

        # Check if the correct chain was used
        expected_chain = question_data['expected_module_chain']
        if all(m in module_used for m in expected_chain):
            print("  - Chain selection: Pass")
        else:
            print(f"  - Chain selection: Fail (Expected to contain {expected_chain})")

        # Check if the conclusion is reasonable
        expected_keywords = question_data['expected_conclusion_keywords']
        if all(kw.lower() in conclusion.lower() for kw in expected_keywords):
            print("  - Conclusion check: Pass")
        else:
            print(f"  - Conclusion check: Fail (Expected to contain {expected_keywords})")
    else:
        print("  - Test failed: No reasoning output from orchestrator.")

    print(f"\n--- Collaboration Test Complete ---")

if __name__ == "__main__":
    run_collaboration_test()
