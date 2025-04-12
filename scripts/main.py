import argparse
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ingestion.ingest_pipeline import run_pipeline
from core.knowledge_graph.knowledgeGraph import KnowledgeGraph

def main():
    parser = argparse.ArgumentParser(description="Kairos Document Ingestion Pipeline")
    parser.add_argument("--file", "-f", required=True, help="Path to document file")
    parser.add_argument("--openai-key", required=True, help="OpenAI API key")
    parser.add_argument("--output-dir", default="output", help="Output directory")
    parser.add_argument("--update-existing", action="store_true", 
                       help="Update existing knowledge graph instead of creating new one")
    
    args = parser.parse_args()
    
    # Load existing KG if requested
    existing_kg = None
    if args.update_existing:
        kg_path = os.path.join(args.output_dir, "knowledge_graph.json")
        if os.path.exists(kg_path):
            print(f"Loading existing knowledge graph from {kg_path}")
            existing_kg = KnowledgeGraph()
            existing_kg.load_from_json(kg_path)
        else:
            print(f"Warning: Could not find existing knowledge graph at {kg_path}")
    
    # Run the pipeline
    kg = run_pipeline(
        filename=args.file,
        openai_key=args.openai_key,
        output_dir=args.output_dir,
        existing_kg=existing_kg
    )
    
    print("\nPipeline completed successfully!")
    
if __name__ == "__main__":
    main()
