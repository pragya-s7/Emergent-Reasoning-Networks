"""
Baseline systems for comparison in evaluation.

This module provides baseline implementations to compare against the full Kairos system:
1. Naive KG Query: Direct knowledge graph lookups without reasoning
2. No-Validation Baseline: Reasoning without validation layer
3. No-Hebbian Baseline: Full system without plasticity
4. Single-Agent Baseline: Single LLM without specialized modules
"""

import sys
import os
import re
from typing import Dict, Any, List

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.knowledge_graph.knowledgeGraph import KnowledgeGraph
import anthropic


class NaiveKGQueryBaseline:
    """
    Baseline 1: Direct KG query without any reasoning.
    Simply searches for entities mentioned in the query and returns connected facts.
    """

    def __init__(self):
        self.name = "Naive_KG_Query"

    def run(self, query: str, kg: KnowledgeGraph) -> Dict[str, Any]:
        """Run naive keyword-based KG query."""
        # Extract potential entity names from query (simple word extraction)
        words = re.findall(r'\b[A-Z][a-zA-Z]+\b', query)

        results = []
        source_triples = []

        for word in words:
            if word in kg.label_to_id:
                # Find all relations involving this entity
                entity_id = kg.label_to_id[word]
                # Subject relations
                for rel in kg.relations:
                    if rel.subject_id == entity_id:
                        subj = kg.entities[rel.subject_id]
                        obj = kg.entities[rel.object_id]
                        triple_str = f"{subj.label} --{rel.predicate}--> {obj.label}"
                        results.append(triple_str)
                        source_triples.append(triple_str)
                    # Object relations
                    elif rel.object_id == entity_id:
                        subj = kg.entities[rel.subject_id]
                        obj = kg.entities[rel.object_id]
                        triple_str = f"{subj.label} --{rel.predicate}--> {obj.label}"
                        results.append(triple_str)
                        source_triples.append(triple_str)

        conclusion = "Found facts: " + "; ".join(results) if results else "No relevant facts found"

        return {
            "subquery": query,
            "reasoningPath": [
                {
                    "step": "Step 1",
                    "data": f"Searched KG for entities: {', '.join(words)}",
                    "source": "Knowledge Graph",
                    "inference": "Direct lookup without reasoning"
                }
            ],
            "conclusion": conclusion,
            "confidence": 1.0 if results else 0.0,
            "source_triples": source_triples,
            "module_used": "naive_kg_query",
            "baseline": True
        }


class SingleAgentBaseline:
    """
    Baseline 2: Single general-purpose LLM without specialized modules.
    Uses one LLM to answer all queries without domain specialization.
    """

    def __init__(self):
        self.name = "Single_Agent_LLM"

    def run(self, query: str, kg: KnowledgeGraph, anthropic_key: str) -> Dict[str, Any]:
        """Run single-agent LLM reasoning."""
        # Get all KG facts as context
        all_triples = kg.query()
        kg_context = "\n".join([
            f"- {s.label} --{r.predicate}--> {o.label}"
            for s, r, o in all_triples[:100]  # Limit context size
        ])

        prompt = f"""You are an AI assistant analyzing a knowledge graph.

Knowledge Graph Facts:
{kg_context}

User Query: {query}

Provide a structured analysis with:
1. Reasoning steps
2. Conclusion
3. Confidence (0-1)

Format your response as:
REASONING:
- Step 1: [observation]
- Step 2: [inference]
...

CONCLUSION: [your conclusion]

CONFIDENCE: [0-1 score]
"""

        try:
            client = anthropic.Anthropic(api_key=anthropic_key)
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2048,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text

            # Parse response
            reasoning_steps = []
            if "REASONING:" in response_text:
                reasoning_section = response_text.split("REASONING:")[1].split("CONCLUSION:")[0]
                steps = [s.strip() for s in reasoning_section.split("\n") if s.strip().startswith("-")]
                for i, step in enumerate(steps, 1):
                    reasoning_steps.append({
                        "step": f"Step {i}",
                        "data": step.replace("-", "").strip(),
                        "source": "LLM Analysis",
                        "inference": "General reasoning"
                    })

            conclusion = "Unable to determine"
            if "CONCLUSION:" in response_text:
                conclusion = response_text.split("CONCLUSION:")[1].split("CONFIDENCE:")[0].strip()

            confidence = 0.5
            if "CONFIDENCE:" in response_text:
                try:
                    conf_str = response_text.split("CONFIDENCE:")[1].strip().split()[0]
                    confidence = float(conf_str)
                except:
                    pass

            return {
                "subquery": query,
                "reasoningPath": reasoning_steps,
                "conclusion": conclusion,
                "confidence": confidence,
                "source_triples": [],
                "module_used": "single_agent_llm",
                "baseline": True
            }

        except Exception as e:
            return {
                "subquery": query,
                "reasoningPath": [{"step": "Error", "data": str(e), "source": "System", "inference": "Failed"}],
                "conclusion": f"Error: {str(e)}",
                "confidence": 0.0,
                "source_triples": [],
                "module_used": "single_agent_llm",
                "baseline": True
            }


class NoValidationBaseline:
    """
    Baseline 3: Full reasoning modules but no validation layer.
    Uses the orchestrator but skips all validation nodes.
    """

    def __init__(self):
        self.name = "No_Validation"

    def run(self, query: str, kg: KnowledgeGraph, anthropic_key: str) -> Dict[str, Any]:
        """Run reasoning without validation."""
        from core.orchestrator.index import orchestrate

        # Run orchestrator with validation disabled
        result = orchestrate(query, kg, anthropic_key, run_validation=False)

        # Mark as baseline
        if result and "reasoning" in result:
            result["reasoning"]["baseline"] = True
            result["baseline_type"] = "no_validation"

        return result


class NoHebbianBaseline:
    """
    Baseline 4: Full system but with Hebbian plasticity disabled.
    All reasoning and validation runs, but KG doesn't adapt.
    """

    def __init__(self):
        self.name = "No_Hebbian_Plasticity"

    def run(self, query: str, kg: KnowledgeGraph, anthropic_key: str) -> Dict[str, Any]:
        """Run full system without Hebbian learning."""
        from core.orchestrator.index import orchestrate, apply_hebbian_learning

        # Temporarily disable Hebbian learning by replacing it with no-op
        original_hebbian = apply_hebbian_learning

        def no_op_hebbian(kg, reasoning, validation):
            return {
                "edges_strengthened": 0,
                "entities_activated": 0,
                "emergent_edges": [],
                "decayed_edges": 0
            }

        # Monkey patch temporarily
        import core.orchestrator.index as orch_module
        orch_module.apply_hebbian_learning = no_op_hebbian

        try:
            result = orchestrate(query, kg, anthropic_key, run_validation=True)

            # Mark as baseline
            if result and "reasoning" in result:
                result["reasoning"]["baseline"] = True
                result["baseline_type"] = "no_hebbian"
        finally:
            # Restore original
            orch_module.apply_hebbian_learning = original_hebbian

        return result


def get_baseline(baseline_name: str):
    """Factory function to get baseline by name."""
    baselines = {
        "naive_kg": NaiveKGQueryBaseline(),
        "single_agent": SingleAgentBaseline(),
        "no_validation": NoValidationBaseline(),
        "no_hebbian": NoHebbianBaseline()
    }
    return baselines.get(baseline_name)


def run_baseline_comparison(query: str, kg: KnowledgeGraph, anthropic_key: str,
                           baselines: List[str] = None) -> Dict[str, Any]:
    """
    Run query against multiple baselines and return results.

    Args:
        query: The query to evaluate
        kg: Knowledge graph instance
        anthropic_key: API key for LLM calls
        baselines: List of baseline names to run (default: all)

    Returns:
        Dict mapping baseline names to their results
    """
    if baselines is None:
        baselines = ["naive_kg", "single_agent", "no_validation", "no_hebbian"]

    results = {}

    for baseline_name in baselines:
        baseline = get_baseline(baseline_name)
        if baseline:
            print(f"Running baseline: {baseline_name}")
            try:
                if baseline_name == "naive_kg":
                    results[baseline_name] = baseline.run(query, kg)
                else:
                    results[baseline_name] = baseline.run(query, kg, anthropic_key)
            except Exception as e:
                print(f"Error in baseline {baseline_name}: {e}")
                results[baseline_name] = {
                    "error": str(e),
                    "baseline": True,
                    "baseline_type": baseline_name
                }

    return results


if __name__ == "__main__":
    # Test baselines
    import argparse

    parser = argparse.ArgumentParser(description="Test baseline systems")
    parser.add_argument("--query", required=True, help="Query to test")
    parser.add_argument("--kg-path", default="output/knowledge_graph.json", help="Path to KG")
    parser.add_argument("--anthropic-key", help="Anthropic API key")
    parser.add_argument("--baseline", choices=["naive_kg", "single_agent", "no_validation", "no_hebbian"],
                       help="Specific baseline to test")

    args = parser.parse_args()

    kg = KnowledgeGraph()
    kg.load_from_json(args.kg_path)

    baselines_to_run = [args.baseline] if args.baseline else None
    results = run_baseline_comparison(args.query, kg, args.anthropic_key, baselines_to_run)

    import json
    print(json.dumps(results, indent=2))
