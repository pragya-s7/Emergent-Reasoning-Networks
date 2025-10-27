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
from reasoning_modules.base.module import ReasoningModule

class NoisySecurityAuditReasoningModule(ReasoningModule):
    """
    A reasoning module that intentionally produces flawed reasoning for evaluation purposes.
    """
    def run(self, query: str, knowledge_graph: KnowledgeGraph) -> dict:
        # Intentionally introduce a logical fallacy
        reasoning_path = [
            {
                "step": "Step 1",
                "data": "System-Alpha has a known vulnerability (CVE-2024-1234)",
                "source": "NVD",
                "inference": "All systems with known vulnerabilities are high-risk."
            },
            {
                "step": "Step 2",
                "data": "System-Alpha is a system.",
                "source": "System Inventory",
                "inference": "Therefore, System-Alpha is high-risk."
            },
            {
                "step": "Step 3",
                "data": "The sky is blue.",
                "source": "Observation",
                "inference": "Therefore, we should immediately disconnect System-Alpha."
            }
        ]

        return {
            "subquery": query,
            "timestamp": datetime.now().isoformat(),
            "reasoningPath": reasoning_path,
            "sources": {},
            "conclusion": "System-Alpha should be disconnected due to a critical risk, and also because the sky is blue.",
            "confidence": 0.99,
            "source_triples": ["System-Alpha --has_vulnerability--> CVE-2024-1234"],
            "relevantMetrics": {}
        }

def main():
    parser = argparse.ArgumentParser(description="Kairos Validation Evaluation Script")
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
    output_filename = f"validation_evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    output_path = os.path.join(args.output_dir, output_filename)
    with open(output_path, 'w', newline='') as csvfile:
        fieldnames = ['query', 'module_type', 'trust_score', 'logical_score', 'grounding_score', 'novelty_score', 'alignment_score']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Run evaluation
        for item in dataset:
            query = item['query']

            # Run with standard module
            print(f"Running query '{query}' with standard module...")
            standard_result = orchestrate(query, kg, args.anthropic_key)
            writer.writerow({
                'query': query,
                'module_type': 'standard',
                'trust_score': standard_result.get('trust_score', 0),
                'logical_score': standard_result['validation']['logical']['score'],
                'grounding_score': standard_result['validation']['grounding']['score'],
                'novelty_score': standard_result['validation']['novelty']['score'],
                'alignment_score': standard_result['validation']['alignment']['score']
            })

            # Run with noisy module
            print(f"Running query '{query}' with noisy module...")
            # Temporarily replace the security audit module with the noisy one
            original_module = orchestrate.RM_REGISTRY['security_audit']
            orchestrate.RM_REGISTRY['security_audit'] = {
                "description": "A noisy module for testing validation.",
                "module": "__main__",
                "class": "NoisySecurityAuditReasoningModule",
                "requires_anthropic": False
            }
            noisy_result = orchestrate(query, kg, args.anthropic_key)
            writer.writerow({
                'query': query,
                'module_type': 'noisy',
                'trust_score': noisy_result.get('trust_score', 0),
                'logical_score': noisy_result['validation']['logical']['score'],
                'grounding_score': noisy_result['validation']['grounding']['score'],
                'novelty_score': noisy_result['validation']['novelty']['score'],
                'alignment_score': noisy_result['validation']['alignment']['score']
            })
            orchestrate.RM_REGISTRY['security_audit'] = original_module

    print(f"Evaluation complete. Results saved to {output_path}")

if __name__ == "__main__":
    main()
