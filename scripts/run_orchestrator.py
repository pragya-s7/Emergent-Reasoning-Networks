import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.orchestrator.index import orchestrate

class MockKnowledgeGraph:
    def queryGraph(self, topic):
        return {
            "mocked_fact": f"mocked data for {topic}"
        }

query = "Are there vulnerabilities in TokenX's smart contract?"
knowledge_graph = MockKnowledgeGraph()

result = orchestrate(query, knowledge_graph)

print("\n=== Kairos Orchestrator Output ===")
print("Query:", query)
print("Selected RM Result:")
print("Conclusion:", result["conclusion"])
print("Reasoning Path:")
for step in result["reasoningPath"]:
    print("  -", step)