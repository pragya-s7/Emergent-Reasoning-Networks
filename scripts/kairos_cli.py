#!/usr/bin/env python3
import argparse
import os
import sys
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.knowledge_graph.knowledgeGraph import KnowledgeGraph
from core.orchestrator.index import orchestrate

def main():
    parser = argparse.ArgumentParser(description="Kairos Emergent Reasoning Network CLI")
    parser.add_argument("--query", "-q", required=True, help="Query to process")
    parser.add_argument("--kg-path", default="output/knowledge_graph.json", 
                        help="Path to knowledge graph JSON file")
    parser.add_argument("--openai-key", help="OpenAI API key (or set OPENAI_API_KEY env var)")
    parser.add_argument("--no-validation", action="store_true", 
                        help="Skip validation nodes")
    parser.add_argument("--output", "-o", help="Output file for results (JSON)")
    
    args = parser.parse_args()
    
    # Get OpenAI key from args or environment
    openai_key = args.openai_key or os.environ.get("OPENAI_API_KEY")
    if not openai_key:
        print("Warning: No OpenAI API key provided. Some features may not work.")
    
    # Load knowledge graph
    print(f"Loading knowledge graph from {args.kg_path}...")
    kg = KnowledgeGraph()
    kg.load_from_json(args.kg_path)
    
    # Process query
    print(f"Processing query: {args.query}")
    result = orchestrate(
        query=args.query,
        knowledge_graph=kg,
        openai_key=openai_key,
        run_validation=not args.no_validation
    )
    
    # Display results
    print("\n=== Reasoning Results ===")
    print(f"Module: {result['reasoning'].get('module_used', 'unknown')}")
    print(f"Conclusion: {result['reasoning'].get('conclusion', 'No conclusion')}")
    
    print("\n=== Reasoning Steps ===")
    for step in result['reasoning'].get('reasoningPath', []):
        if isinstance(step, dict):
            print(f"- {step.get('step', 'Step')}: {step.get('data', '')}")
            print(f"  Inference: {step.get('inference', '')}")
        else:
            print(f"- {step}")
    
    if 'validation' in result and result['validation']:
        print("\n=== Validation Results ===")
        for vn_name, vn_result in result['validation'].items():
            valid = vn_result.get('valid', False)
            score = vn_result.get('score', 0.0)
            status = "✅ PASSED" if valid else "❌ FAILED"
            print(f"{vn_name}: {status} (Score: {score})")
            print(f"  Feedback: {vn_result.get('feedback', 'No feedback')}")
    
    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nResults saved to {args.output}")

if __name__ == "__main__":
    main()