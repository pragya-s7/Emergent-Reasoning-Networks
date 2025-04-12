import openai
import ast
from knowledgeGraph import KnowledgeGraph
from datetime import datetime

def extract_triples_from_text(text: str, openai_key: str):
    openai.api_key = openai_key

    prompt = f"""
You are an information extraction agent. From the following text, extract all relevant factual relationships and output them as subject-predicate-object triples.

Text:
{text}

Output format (Python list of tuples):
[("subject1", "predicate1", "object1"), ("subject2", "predicate2", "object2"), ...]
Only output valid Python list syntax. No explanations.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You extract structured triples from text."},
            {"role": "user", "content": prompt}
        ]
    )

    triples_text = response['choices'][0]['message']['content'].strip()

    try:
        return ast.literal_eval(triples_text)
    except Exception as e:
        print("Triple parsing error:", e)
        print("Raw response:", triples_text)
        return []

def ingest_triples_into_kg(triples, source="openai", doc_id="unknown") -> KnowledgeGraph:
    kg = KnowledgeGraph()
    extracted_at = datetime.utcnow().isoformat()

    for subj, pred, obj in triples:
        kg.add_relation(
            subj, pred, obj,
            subject_type="Entity",
            object_type="Entity",
            confidence=1.0,
            source=source,
            metadata={"extracted_at": extracted_at, "doc_id": doc_id}
        )

    return kg
