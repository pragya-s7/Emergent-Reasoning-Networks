from knowledgeGraph import KnowledgeGraph
from reasoning_modules.defi_risk_rm import run_defi_risk_rm

kg = KnowledgeGraph()
kg.load_from_json("output/knowledge_graph.json")

query = "What are the major risks to Ethereum?"
openai_key = "YOUR_KEY"

result = run_defi_risk_rm(query, kg, openai_key)

print("\n💡 RM Output:")
print("Answer:", result["answer"])
print("Reasoning:")
for step in result["reasoning_steps"]:
    print("-", step)
print("Source Triples:")
for src in result["source_triples"]:
    print("-", src)


from validation_nodes.logical_vn import run_logical_vn

vn_result = run_logical_vn(result, openai_key)

print("\n🧪 LogicalVN Result:")
print("Valid:", vn_result["valid"])
print("Score:", vn_result["score"])
print("Feedback:", vn_result["feedback"])
