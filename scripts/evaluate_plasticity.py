import argparse
import json
import os
import sys
import csv
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.knowledge_graph.knowledgeGraph import KnowledgeGraph
from core.orchestrator.index import orchestrate

def main():
    parser = argparse.ArgumentParser(description="Kairos Hebbian Plasticity Evaluation Script")
    parser.add_argument("--query", required=True, help="Query to run for evaluation")
    parser.add_argument("--cycles", type=int, default=10, help="Number of cycles to run")
    parser.add_argument("--kg-path", default="output/knowledge_graph.json", help="Path to knowledge graph")
    parser.add_argument("--openai-key", required=True, help="OpenAI API key")
    parser.add_argument("--output-dir", default="output", help="Output directory")
    args = parser.parse_args()

    # Load knowledge graph
    kg = KnowledgeGraph()
    kg.load_from_json(args.kg_path)

    # Prepare output file
    output_filename = f"plasticity_evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    output_path = os.path.join(args.output_dir, output_filename)
    with open(output_path, 'w', newline='') as csvfile:
        fieldnames = ['cycle', 'latency', 'emergent_connections', 'avg_top_k_strength']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Run evaluation cycles
        for i in range(args.cycles):
            print(f"Running cycle {i+1}/{args.cycles}...")

            start_time = time.time()
            result = orchestrate(args.query, kg, args.openai_key)
            latency = time.time() - start_time

            emergent_connections = len(result.get('hebbian_plasticity', {}).get('emergent_edges', []))
            
            top_k_edges = kg.get_strongest_edges(top_k=10)
            avg_top_k_strength = sum([edge[3] for edge in top_k_edges]) / len(top_k_edges) if top_k_edges else 0

            writer.writerow({
                'cycle': i + 1,
                'latency': latency,
                'emergent_connections': emergent_connections,
                'avg_top_k_strength': avg_top_k_strength
            })

            # Save the updated knowledge graph for the next cycle
            kg.save_to_json(args.kg_path)

    print(f"Evaluation complete. Results saved to {output_path}")

if __name__ == "__main__":
    main()
