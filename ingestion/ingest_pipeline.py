import os
import dotenv
from typing import Dict, Any, Optional

from ingestion.triple_extractor import extract_triples_from_text, ingest_triples_into_kg
from core.knowledge_graph.knowledgeGraph import KnowledgeGraph

# Load environment variables from .env file
dotenv.load_dotenv()

def run_pipeline(filename: str, openai_key: Optional[str] = None, 
                output_dir: str = "output", existing_kg: Optional[KnowledgeGraph] = None):
    """
    Run the full document ingestion pipeline.
    
    Args:
        filename: Path to the document file
        openai_key: OpenAI API key (optional, will use environment variable if not provided)
        output_dir: Directory to save the knowledge graph
        existing_kg: Optional existing knowledge graph to update
        
    Returns:
        Updated knowledge graph
    """
    # Use provided API keys or get from environment
    openai_key = openai_key or os.environ.get("OPENAI_API_KEY")
    
    if not openai_key:
        raise ValueError("OpenAI API key not provided and not found in environment variables")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract document ID from filename
    doc_id = os.path.basename(filename)
    
    print(f"Processing document: {doc_id}")
    print("Extracting text from file...")
    
    try:
        # Extract text from file
        with open(filename, 'r') as f:
            raw_text = f.read()
        
        # Create document metadata
        doc_metadata = {
            "filename": doc_id,
            "confidence": 1.0, # Default confidence for text files
        }
        
        print(f"Extracted {len(raw_text)} characters")
        print("Extracting triples using OpenAI...")
        
        # Extract triples from text
        triples = extract_triples_from_text(raw_text, openai_key, doc_metadata)
        print(f"Extracted {len(triples)} triples")
        
        # Create or update knowledge graph
        if existing_kg:
            kg = existing_kg
            # Add triples to existing KG
            for subj, pred, obj in triples:
                kg.add_relation(
                    subj, pred, obj,
                    subject_type="Entity",
                    object_type="Entity",
                    confidence=doc_metadata["confidence"],
                    source="text_file",
                    metadata={
                        "doc_id": doc_id,
                    }
                )
        else:
            # Create new KG
            kg = ingest_triples_into_kg(triples, source="text_file", 
                                       doc_id=doc_id, doc_metadata=doc_metadata)
        
        # Save knowledge graph
        output_path = os.path.join(output_dir, "knowledge_graph.json")
        kg.save_to_json(output_path)
        print(f"KG saved to {output_path}")
        
        # Print summary
        print("\nIngestion Summary:")
        print(f"- Document: {doc_id}")
        print(f"- Text length: {len(raw_text)} characters")
        print(f"- Triples extracted: {len(triples)}")
        print(f"- Total entities: {len(kg.entities)}")
        print(f"- Total relations: {len(kg.relations)}")
        
        return kg
        
    except Exception as e:
        print(f"Error in ingestion pipeline: {str(e)}")
        raise


