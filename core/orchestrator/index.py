import importlib
import os
import sys
import datetime
import re
from typing import Dict, Any, List, Optional
from sentence_transformers import SentenceTransformer, util

# Add project root to path to ensure imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Load the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Registry of available reasoning modules
RM_REGISTRY = {
    "financial_analysis": {
        "description": "Performs dynamic financial analysis of market behaviors, liquidity, and risk assessment using an LLM.",
        "module": "reasoning_modules.defi_risk.index",
        "function": "run_financial_analysis_rm",
        "requires_anthropic": True
    },
    "security_audit": {
        "description": "Analyzes entities in the knowledge graph against a predefined set of security rules to flag potential risks.",
        "module": "reasoning_modules.audit_rm",
        "class": "SecurityAuditReasoningModule",
        "requires_anthropic": False
    },
    "macro_analysis": {
        "description": "Analyzes local macroeconomic data from a CSV file to identify trends in interest rates and inflation.",
        "module": "reasoning_modules.macro_rm",
        "class": "MacroReasoningModule",
        "requires_anthropic": False
    },
    "corporate_communications": {
        "description": "Analyzes official company announcements from a local JSON file to gauge sentiment and key messages.",
        "module": "reasoning_modules.corporate_communications_rm",
        "class": "CorporateCommunicationsReasoningModule",
        "requires_anthropic": False
    }
}

# Validation nodes registry
VN_REGISTRY = {
    "logical": {
        "module": "validation_nodes.logical_vn",
        "function": "run_logical_vn",
        "requires_anthropic": True,
        "requires_kg": False
    },
    "grounding": {
        "module": "validation_nodes.grounding_vn",
        "function": "run_grounding_vn",
        "requires_anthropic": False,
        "requires_kg": True
    },
    "novelty": {
        "module": "validation_nodes.novelty_vn",
        "function": "run_novelty_vn",
        "requires_anthropic": True,
        "requires_kg": True
    },
    "alignment": {
        "module": "validation_nodes.alignment_vn",
        "function": "run_alignment_vn",
        "requires_anthropic": True,
        "requires_kg": False
    }
}

# Prepare embeddings for module selection
rm_names = list(RM_REGISTRY.keys())
rm_texts = [RM_REGISTRY[name]["description"] for name in rm_names]
rm_embeddings = model.encode(rm_texts, convert_to_tensor=True)

def apply_hebbian_learning(knowledge_graph: Any, reasoning_output: Dict, validation_results: Optional[Dict]) -> Dict:
    """
    Apply Hebbian plasticity to the knowledge graph based on reasoning patterns.

    Implements three types of learning:
    1. Edge strengthening: Edges used in reasoning get stronger
    2. Entity co-activation: Track concepts that appear together
    3. Memory consolidation: Form emergent connections and apply decay

    Args:
        knowledge_graph: KnowledgeGraph instance
        reasoning_output: Output from reasoning module
        validation_results: Output from validation nodes (can be None)

    Returns:
        Dictionary with plasticity statistics
    """
    stats = {
        "edges_strengthened": 0,
        "entities_activated": 0,
        "emergent_edges": [],
        "decayed_edges": 0
    }

    try:
        # increment cycle counters at the start of each reasoning cycle
        # this increases the inactivity counter for all previously-activated edges
        knowledge_graph.increment_cycle_counters()
        # 1. Strengthen edges explicitly used in reasoning (if source_triples provided)
        source_triples = reasoning_output.get("source_triples", [])
        triple_pattern = re.compile(r"(.*?)\s*--(.+?)-->\s*(.*)")

        for triple_str in source_triples:
            try:
                match = triple_pattern.match(triple_str)
                if match:
                    subj, pred, obj = [s.strip() for s in match.groups()]
                    if subj and pred and obj:
                        knowledge_graph.activate_relation(subj, pred, obj)
                        stats["edges_strengthened"] += 1
            except Exception as e:
                print(f"[Hebbian] Failed to parse triple: {triple_str} - {e}")

        # 2. Track entity co-activations from reasoning context
        activated_entities = set()
        if "reasoningPath" in reasoning_output:
            for step in reasoning_output["reasoningPath"]:
                step_data = step.get("data", "") + " " + step.get("inference", "")
                for entity_label in knowledge_graph.label_to_id.keys():
                    if entity_label in step_data:
                        activated_entities.add(entity_label)

        if activated_entities:
            knowledge_graph.activate_entities(list(activated_entities))
            stats["entities_activated"] = len(activated_entities)

        # 3. Periodically consolidate memory (form emergent edges and decay)
        # Only do this if validation was run and passed
        validation_passed = False
        if validation_results:
            validation_passed = all(
                v.get("valid", False) for v in validation_results.values()
                if isinstance(v, dict)
            )

        if validation_passed:
            consolidation_result = knowledge_graph.consolidate_memory()
            stats["emergent_edges"] = len(consolidation_result.get("emergent_edges", []))
            stats["decayed_edges"] = consolidation_result.get("decayed_edges", [])

        if stats["edges_strengthened"] > 0 or stats["entities_activated"] > 0:
            print(f"\n[Hebbian] Learning applied: {stats['edges_strengthened']} edges strengthened, "
                  f"{stats['entities_activated']} entities activated")

    except Exception as e:
        print(f"[Hebbian] Error during plasticity application: {str(e)}")

    return stats

def orchestrate_chain(query: str, knowledge_graph: Any, module_chain: List[str], anthropic_key: Optional[str] = None) -> Dict[str, Any]:
    """Runs a chain of reasoning modules in sequence."""
    print(f"[Kairos Orchestrator] Running chain: {' -> '.join(module_chain)}")
    
    final_conclusion = ""
    cumulative_reasoning_path = []
    cumulative_source_triples = []
    
    for i, rm_name in enumerate(module_chain):
        print(f"  - Running module: {rm_name}")
        rm_info = RM_REGISTRY[rm_name]
        rm_module = importlib.import_module(rm_info["module"])
        RMClass = getattr(rm_module, rm_info["class"])
        rm_instance = RMClass()
        
        # Pass the original query and the conclusion of the previous step
        sub_query = query if i == 0 else f"{query} - context: {final_conclusion}"
        
        rm_result = rm_instance.run(sub_query, knowledge_graph)
        
        final_conclusion = rm_result.get('conclusion', '')
        cumulative_reasoning_path.extend(rm_result.get('reasoningPath', []))
        cumulative_source_triples.extend(rm_result.get('source_triples', []))

    # In a real implementation, a final synthesis step would be needed here.
    # For now, we just combine the outputs.
    final_result = {
        "subquery": query,
        "timestamp": datetime.datetime.now().isoformat(),
        "reasoningPath": cumulative_reasoning_path,
        "sources": {"chain": module_chain},
        "conclusion": final_conclusion,
        "confidence": 0.75, # Confidence would be calculated based on the chain
        "source_triples": cumulative_source_triples,
        "module_used": f"chain:{'->'.join(module_chain)}"
    }
    
    return final_result

def orchestrate(query: str, knowledge_graph: Any, anthropic_key: Optional[str] = None, 
               run_validation: bool = True, alignment_profile: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Orchestrate the reasoning process by selecting and running the appropriate reasoning module
    and validation nodes.
    """
    try:
        # Simple keyword-based detection for multi-domain queries
        if "and" in query.lower() and "security" in query.lower() and "communications" in query.lower():
            rm_result = orchestrate_chain(query, knowledge_graph, ["corporate_communications", "security_audit"])
        else:
            # Select the most appropriate reasoning module
            query_embedding = model.encode(query, convert_to_tensor=True)
            similarity_scores = util.cos_sim(query_embedding, rm_embeddings)
            best_index = int(similarity_scores.argmax())
            selected_rm_name = rm_names[best_index]
            rm_info = RM_REGISTRY[selected_rm_name]

            print(f"[Kairos Orchestrator] Selected RM: {selected_rm_name}")
            
            if rm_info.get("requires_anthropic", False) and not anthropic_key:
                raise ValueError(f"The selected reasoning module '{selected_rm_name}' requires an OpenAI API key")
            
            rm_module = importlib.import_module(rm_info["module"])
            
            if "class" in rm_info:
                RMClass = getattr(rm_module, rm_info["class"])
                rm_instance = RMClass()
                rm_result = rm_instance.run(query, knowledge_graph)
            else:
                rm_function = getattr(rm_module, rm_info["function"])
                if rm_info.get("requires_anthropic", False):
                    rm_result = rm_function(query, knowledge_graph, anthropic_key)
                else:
                    rm_result = rm_function(query, knowledge_graph)
            
            rm_result["module_used"] = selected_rm_name
        
        validation_results = {}
        if run_validation:
            for vn_name, vn_info in VN_REGISTRY.items():
                # Check if the VN can be run with the provided arguments
                can_run = True
                if vn_info.get("requires_anthropic", False) and not anthropic_key:
                    can_run = False
                
                if can_run:
                    try:
                        print(f"[Kairos Orchestrator] Running validation node: {vn_name}")
                        vn_module = importlib.import_module(vn_info["module"])
                        vn_function = getattr(vn_module, vn_info["function"])
                        
                        vn_args = [rm_result]
                        if vn_info.get("requires_kg", False):
                            vn_args.append(knowledge_graph)
                        if vn_info.get("requires_anthropic", False):
                            vn_args.append(anthropic_key)
                        
                        if vn_name == "alignment" and alignment_profile:
                            vn_args.append(alignment_profile)
                        
                        vn_result = vn_function(*vn_args)
                        validation_results[vn_name] = vn_result
                    except Exception as e:
                        print(f"[Kairos Orchestrator] Error in validation node {vn_name}: {str(e)}")
                        validation_results[vn_name] = {"valid": False, "score": 0.0, "feedback": f"Error: {str(e)}"}



        hebbian_stats = apply_hebbian_learning(knowledge_graph, rm_result, validation_results)

        # Compute trust score as average of all validation scores
        trust_score = 0.0
        if validation_results:
            scores = [v.get("score", 0.0) for v in validation_results.values() if isinstance(v, dict) and "score" in v]
            trust_score = sum(scores) / len(scores) if scores else 0.0

        final_result = {
            "reasoning": rm_result,
            "validation": validation_results,
            "hebbian_plasticity": hebbian_stats,
            "trust_score": round(trust_score, 3)
        }

        return final_result
        
    except Exception as e:
        print(f"[Kairos Orchestrator] Error: {str(e)}")
        return {
            "error": str(e),
            "reasoning": None,
            "validation": {}
        }