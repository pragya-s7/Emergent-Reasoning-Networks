import json
from knowledgeGraph import KnowledgeGraph

# Load the saved KG
kg = KnowledgeGraph()
kg.load_from_json("output/knowledge_graph.json")

print("📊 Knowledge Graph Query Tool")
print("Enter filter criteria (press Enter to skip a filter):\n")

subject = input("Subject label: ").strip() or None
predicate = input("Predicate: ").strip() or None
object_ = input("Object label: ").strip() or None
subject_type = input("Subject type (e.g. Person, Protocol): ").strip() or None
object_type = input("Object type: ").strip() or None
min_conf = input("Minimum confidence (e.g. 0.8): ").strip()
min_confidence = float(min_conf) if min_conf else None

after = input("After timestamp (YYYY-MM-DD): ").strip() or None
before = input("Before timestamp (YYYY-MM-DD): ").strip() or None

print("\nOptional: Metadata filters (e.g., doc_id, extracted_at)")
meta_filters = {}
while True:
    k = input("Metadata key (press Enter to stop): ").strip()
    if not k:
        break
    v = input(f"Value for '{k}': ").strip()
    meta_filters[k] = v


# Run query
results = kg.query(
    subject=subject,
    predicate=predicate,
    object_=object_,
    subject_type=subject_type,
    object_type=object_type,
    min_confidence=min_confidence,
    after=after,
    before=before,
    metadata_filter=meta_filters if meta_filters else None
)


print(f"\n✅ {len(results)} results found:\n")
for subj, rel, obj in results:
    print(f"{subj.label} ({subj.type}) --{rel.predicate}--> {obj.label} ({obj.type})")
    print(f"  confidence: {rel.confidence}")
    print(f"  created_at: {rel.created_at}")
    print(f"  metadata: {json.dumps(rel.metadata)}\n")


