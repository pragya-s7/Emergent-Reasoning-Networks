import anthropic
import datetime
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from reasoning_modules.base.module import ReasoningModule

class FinancialAnalysisReasoningModule(ReasoningModule):
    def __init__(self):
        super().__init__('financial-analysis')
        self.sources = {
            "financial_data": "Financial Data Repository",
            "market_data": "Market Analytics",
            "risk_data": "Risk Assessment Database"
        }

    def run(self, subquery, knowledgeGraph, anthropic_key=None):
        if not anthropic_key:
            raise ValueError("Anthropic API key is required for financial analysis")

        # Extract relevant triples from the KG
        relevant_triples = knowledgeGraph.query(subject=None, predicate=None, object_=None)
        triples_text = "\n".join(
            f"{s.label} --{r.predicate}--> {o.label}" for s, r, o in relevant_triples
        )

        # Ask Claude to reason over the facts and answer the query
        prompt = f"""You are a financial analysis reasoning agent. You are given the following structured facts from a knowledge graph:

{triples_text}

User query: "{subquery}"

Based on the facts above, provide:
1. A short answer to the query
2. A step-by-step reasoning process leading to the answer
3. Which of the above facts support your reasoning

Respond in this exact format:

Answer: <short-answer>
Reasoning:
- Step 1: ...
- Step 2: ...
Sources:
- <subject> --<predicate>--> <object>
"""

        client = anthropic.Anthropic(api_key=anthropic_key)
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4096,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        # Extract the response content
        response_content = response.content[0].text

        # Parse output
        try:
            answer = response_content.split("Answer:")[1].split("Reasoning:")[0].strip()
            reasoning_lines = response_content.split("Reasoning:")[1].split("Sources:")[0].strip().split("\n")
            reasoning_steps = [line.strip("- ").strip() for line in reasoning_lines if line.strip()]
            source_lines = response_content.split("Sources:")[1].strip().split("\n")
            source_triples = [line.strip("- ").strip() for line in source_lines if line.strip()]

            # Convert reasoning steps to structured format
            structured_steps = []
            for i, step in enumerate(reasoning_steps):
                structured_steps.append({
                    "step": f"Step {i+1}",
                    "data": step,
                    "source": self.sources.get("financial_data", "Analysis"),
                    "inference": step
                })

            # Calculate confidence based on number of sources
            confidence = min(0.95, 0.5 + (len(source_triples) * 0.1))

            return {
                "subquery": subquery,
                "timestamp": datetime.datetime.now().isoformat(),
                "reasoningPath": structured_steps,
                "sources": self.sources,
                "conclusion": answer,
                "confidence": confidence,
                "source_triples": source_triples,
                "relevantMetrics": {
                    "source_count": len(source_triples),
                    "reasoning_steps": len(reasoning_steps)
                }
            }

        except Exception as e:
            print(f"Failed to parse financial RM output: {e}")
            return {
                "subquery": subquery,
                "timestamp": datetime.datetime.now().isoformat(),
                "reasoningPath": [],
                "sources": self.sources,
                "conclusion": "Could not parse response.",
                "confidence": 0.0,
                "source_triples": [],
                "relevantMetrics": {}
            }


# For backward compatibility
def run_financial_analysis_rm(query, kg, anthropic_key):
    """Legacy function for backward compatibility"""
    rm = FinancialAnalysisReasoningModule()
    result = rm.run(query, kg, anthropic_key)

    # Convert to old format for compatibility
    return {
        "module": "financial-analysis",
        "answer": result["conclusion"],
        "reasoning_steps": [step["data"] for step in result["reasoningPath"]],
        "source_triples": result["source_triples"],
        "confidence": result["confidence"]
    }

# Legacy alias for backward compatibility
def run_defi_risk_rm(query, kg, anthropic_key):
    """Deprecated: use run_financial_analysis_rm instead"""
    return run_financial_analysis_rm(query, kg, anthropic_key)
