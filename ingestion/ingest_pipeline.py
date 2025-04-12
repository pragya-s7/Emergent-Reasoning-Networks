from ingestion.upstage_ocr import extract_text_from_file
from ingestion.triple_extractor import extract_triples_from_text, ingest_triples_into_kg

def run_pipeline(filename: str, upstage_key: str, openai_key: str):
    print("Extracting text from file...")
    raw_text = extract_text_from_file(filename, upstage_key)

    print("Extracting triples using OpenAI...")
    triples = extract_triples_from_text(raw_text, openai_key)

    print("Embedding triples into Knowledge Graph...")
    kg = ingest_triples_into_kg(triples)

    print("Pipeline completed.\n")
    print(kg)

    kg.save_to_json("output/knowledge_graph.json")
    print("KG saved to output/knowledge_graph.json")

    return kg


