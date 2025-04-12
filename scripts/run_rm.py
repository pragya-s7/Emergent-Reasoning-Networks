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


from validation-nodes.logical_vn import run_logical_vn

vn_result = run_logical_vn(result, openai_key)

print("\n🧪 LogicalVN Result:")
print("Valid:", vn_result["valid"])
print("Score:", vn_result["score"])
print("Feedback:", vn_result["feedback"])


from validation-nodes.grounding_vn import run_grounding_vn

grounding_result = run_grounding_vn(result, kg)

print("\n🔍 GroundingVN Result:")
print("Valid:", grounding_result["valid"])
print("Score:", grounding_result["score"])
print("Feedback:", grounding_result["feedback"])


from validation-nodes.novelty_vn import run_novelty_vn

novelty_result = run_novelty_vn(result, kg, openai_key)

print("\n🧬 NoveltyVN Result:")
print("Novel:", novelty_result["valid"])
print("Score:", novelty_result["score"])
print("Feedback:", novelty_result["feedback"])


from validation_nodes.alignment_vn import run_alignment_vn

alignment_result = run_alignment_vn(result, alignment_profile, openai_key)

print("\n🎯 AlignmentVN Result:")
print("Aligned:", alignment_result["valid"])
print("Score:", alignment_result["score"])
print("Feedback:", alignment_result["feedback"])
