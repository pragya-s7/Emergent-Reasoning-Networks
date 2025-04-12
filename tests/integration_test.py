import os
import sys
import unittest

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.knowledge_graph.knowledgeGraph import KnowledgeGraph
from core.orchestrator.index import orchestrate

class IntegrationTest(unittest.TestCase):
    def setUp(self):
        # Create a test knowledge graph with sample data
        self.kg = KnowledgeGraph()
        # Add test data to the knowledge graph
        # ...
        
    def test_end_to_end_flow(self):
        """Test the complete flow from query to validated reasoning"""
        query = "What are the risks of investing in Ethereum?"
        openai_key = os.environ.get("OPENAI_API_KEY")
        
        # Skip test if no API key is available
        if not openai_key:
            self.skipTest("OpenAI API key not available")
        
        # Run the orchestrator
        result = orchestrate(
            query=query,
            knowledge_graph=self.kg,
            openai_key=openai_key,
            run_validation=True
        )
        
        # Verify the result structure
        self.assertIn("reasoning", result)
        self.assertIn("validation", result)
        
        # Check that reasoning was produced
        self.assertIsNotNone(result["reasoning"])
        self.assertIn("conclusion", result["reasoning"])
        
        # Check that validation was performed
        self.assertIn("logical", result["validation"])
        self.assertIn("grounding", result["validation"])

if __name__ == "__main__":
    unittest.main()