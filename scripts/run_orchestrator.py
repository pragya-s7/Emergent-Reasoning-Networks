#!/usr/bin/env python3
"""
CLI wrapper for the Kairos orchestrator.
Accepts query arguments and returns JSON output.
"""

import sys
import os
import argparse
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.orchestrator.index import orchestrate
from core.knowledge_graph.knowledgeGraph import KnowledgeGraph

def main():
    parser = argparse.ArgumentParser(description='Run Kairos reasoning orchestrator')
    parser.add_argument('--query', type=str, required=True, help='User query')
    parser.add_argument('--kg-path', type=str, default='output/knowledge_graph.json',
                       help='Path to knowledge graph JSON file')
    parser.add_argument('--anthropic-key', type=str, help='OpenAI API key')
    parser.add_argument('--run-validation', action='store_true',
                       help='Run validation nodes')
    parser.add_argument('--alignment-profile', type=str,
                       help='JSON string of alignment profile')

    args = parser.parse_args()

    try:
        # Load knowledge graph
        kg = KnowledgeGraph()
        if os.path.exists(args.kg_path):
            kg.load_from_json(args.kg_path)
        else:
            # Create empty KG if file doesn't exist
            print(f"Warning: Knowledge graph file not found at {args.kg_path}. Using empty KG.",
                  file=sys.stderr)

        # Parse alignment profile if provided
        alignment_profile = None
        if args.alignment_profile:
            try:
                alignment_profile = json.loads(args.alignment_profile)
            except json.JSONDecodeError:
                print(f"Warning: Invalid alignment profile JSON. Ignoring.", file=sys.stderr)

        # Run orchestrator
        result = orchestrate(
            query=args.query,
            knowledge_graph=kg,
            anthropic_key=args.anthropic_key,
            run_validation=args.run_validation,
            alignment_profile=alignment_profile
        )

        # Save updated KG with Hebbian changes (if file path exists)
        if os.path.exists(args.kg_path):
            try:
                kg.save_to_json(args.kg_path)
                print(f"[KG] Saved updated knowledge graph with Hebbian changes to {args.kg_path}",
                      file=sys.stderr)
            except Exception as e:
                print(f"[KG] Warning: Failed to save updated KG: {str(e)}", file=sys.stderr)

        # Output result as JSON
        print(json.dumps(result, indent=2))
        sys.exit(0)

    except Exception as e:
        error_result = {
            "error": str(e),
            "reasoning": None,
            "validation": {}
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)

if __name__ == '__main__':
    main()
