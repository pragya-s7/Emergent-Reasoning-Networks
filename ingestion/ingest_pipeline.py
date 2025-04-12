import os
from typing import Dict, Any, Optional

from ingestion.upstage_ocr import extract_text_from_file
from ingestion.triple_extractor import extract_triples_from_text, ingest_triples_into_kg
from core.knowledge_graph.knowledgeGraph import KnowledgeGraph

def run_pipeline(filename: str, upstage_key: str, openai_key: str, 
                output_dir: str = "output", existing_kg: Optional[KnowledgeGraph] = None):
    """
    Run the full document ingestion pipeline.
    
    Args:
        filename: Path to the document file
        upstage_key: Upstage API key
        openai_key: OpenAI API key
        output_dir: Directory to save the knowledge graph
        existing_kg: Optional existing knowledge graph to update
        
    Returns:
        Updated knowledge graph
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract document ID from filename
    doc_id = os.path.basename(filename)
    
    print(f"Processing document: {doc_id}")
    print("Extracting text from file...")
    
    try:
        # Extract text using Upstage OCR
        ocr_result = extract_text_from_file(filename, upstage_key)
        raw_text = ocr_result["text"]
        
        # Create document metadata
        doc_metadata = {
            "filename": doc_id,
            "confidence": ocr_result["confidence"],
            "page_count": len(ocr_result.get("pages", [])),
            "model_version": ocr_result.get("model_version", "")
        }
        
        print(f"Extracted {len(raw_text)} characters with confidence {doc_metadata['confidence']:.2f}")
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
                    source="upstage_openai",
                    metadata={
                        "doc_id": doc_id,
                        "extracted_at": doc_metadata.get("extracted_at", ""),
                        "ocr_confidence": doc_metadata["confidence"]
                    }
                )
        else:
            # Create new KG
            kg = ingest_triples_into_kg(triples, source="upstage_openai", 
                                       doc_id=doc_id, doc_metadata=doc_metadata)
        
        # Save knowledge graph
        output_path = os.path.join(output_dir, "knowledge_graph.json")
        kg.save_to_json(output_path)
        print(f"KG saved to {output_path}")
        
        # Print summary
        print("\nIngestion Summary:")
        print(f"- Document: {doc_id}")
        print(f"- Text length: {len(raw_text)} characters")
        print(f"- OCR confidence: {doc_metadata['confidence']:.2f}")
        print(f"- Triples extracted: {len(triples)}")
        print(f"- Total entities: {len(kg.entities)}")
        print(f"- Total relations: {len(kg.relations)}")
        
        return kg
        
    except Exception as e:
        print(f"Error in ingestion pipeline: {str(e)}")
        raise


