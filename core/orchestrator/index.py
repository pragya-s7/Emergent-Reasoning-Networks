import importlib
import os
import sys
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
        "requires_openai": True
    },
    "security_audit": {
        "description": "Analyzes entities in the knowledge graph against a predefined set of security rules to flag potential risks.",
        "module": "reasoning_modules.audit_rm",
        "class": "SecurityAuditReasoningModule",
        "requires_openai": False
    },
    "macro_analysis": {
        "description": "Analyzes local macroeconomic data from a CSV file to identify trends in interest rates and inflation.",
        "module": "reasoning_modules.macro_rm",
        "class": "MacroReasoningModule",
        "requires_openai": False
    },
    "corporate_communications": {
        "description": "Analyzes official company announcements from a local JSON file to gauge sentiment and key messages.",
        "module": "reasoning_modules.corporate_communications_rm",
        "class": "CorporateCommunicationsReasoningModule",
        "requires_openai": False
    }
}

# Validation nodes registry
VN_REGISTRY = {
    "logical": {
        "module": "validation_nodes.logical_vn",
        "function": "run_logical_vn",
        "requires_openai": True,
        "requires_kg": False
    },
    "grounding": {
        "module": "validation_nodes.grounding_vn",
        "function": "run_grounding_vn",
        "requires_openai": False,
        "requires_kg": True
    },
    "novelty": {
        "module": "validation_nodes.novelty_vn",
        "function": "run_novelty_vn",
        "requires_openai": True,
        "requires_kg": True
    },
    "alignment": {
        "module": "validation_nodes.alignment_vn",
        "function": "run_alignment_vn",
        "requires_openai": True,
        "requires_kg": False
    }
}

# Prepare embeddings for module selection
rm_names = list(RM_REGISTRY.keys())
rm_texts = [RM_REGISTRY[name]["description"] for name in rm_names]
rm_embeddings = model.encode(rm_texts, convert_to_tensor=True)

def apply_hebbian_learning(knowledge_graph: Any, reasoning_output: Dict, validation_results: Dict) -> Dict:
    """
    Apply Hebbian plasticity to the knowledge graph based on reasoning patterns.

    Implements three types of learning:
    1. Edge strengthening: Edges used in reasoning get stronger
    2. Entity co-activation: Track concepts that appear together
    3. Memory consolidation: Form emergent connections and apply decay

    Args:
        knowledge_graph: KnowledgeGraph instance
        reasoning_output: Output from reasoning module
        validation_results: Output from validation nodes

    Returns:
        Dictionary with plasticity statistics
    """
    stats = {
        "edges_strengthened": 0,
        "entities_activated": 0,
        "emergent_edges": 0,
        "decayed_edges": 0
    }

    try:
        # 1. Strengthen edges explicitly used in reasoning (if source_triples provided)
        source_triples = reasoning_output.get("source_triples", [])
        for triple_str in source_triples:
            try:
                # Parse triple format: "Subject --predicate--> Object"
                if "--" in triple_str and "-->" in triple_str:
                    parts = triple_str.split("--")
                    subj = parts[0].strip()
                    pred_obj = parts[1].split("-->")
                    pred = pred_obj[0].strip()
                    obj = pred_obj[1].strip() if len(pred_obj) > 1 else ""

                    if subj and pred and obj:
                        knowledge_graph.activate_relation(subj, pred, obj)
                        stats["edges_strengthened"] += 1
            except Exception as e:
                print(f"[Hebbian] Failed to parse triple: {triple_str} - {e}")

        # 2. Track entity co-activations from reasoning context
        # Extract all entities mentioned in reasoning path
        activated_entities = set()

        if "reasoningPath" in reasoning_output:
            for step in reasoning_output["reasoningPath"]:
                # Extract entity references from step data
                step_data = step.get("data", "") + " " + step.get("inference", "")
                # Simple heuristic: collect entity labels that appear in KG
                for entity_label in knowledge_graph.label_to_id.keys():
                    if entity_label in step_data:
                        activated_entities.add(entity_label)

        if activated_entities:
            knowledge_graph.activate_entities(list(activated_entities))
            stats["entities_activated"] = len(activated_entities)

        # 3. Periodically consolidate memory (form emergent edges and decay)
        # Only do this if validation passed (to avoid reinforcing bad reasoning)
        validation_passed = all(
            v.get("valid", False) for v in validation_results.values()
            if isinstance(v, dict)
        )

        if validation_passed:
            consolidation_result = knowledge_graph.consolidate_memory()
            stats["emergent_edges"] = len(consolidation_result.get("emergent_edges", []))
            stats["decayed_edges"] = consolidation_result.get("decayed_edges", 0)

        # Log summary
        if stats["edges_strengthened"] > 0 or stats["entities_activated"] > 0:
            print(f"\n[Hebbian] Learning applied: {stats['edges_strengthened']} edges strengthened, "
                  f"{stats['entities_activated']} entities activated")

    except Exception as e:
        print(f"[Hebbian] Error during plasticity application: {str(e)}")

    return stats

def orchestrate(query: str, knowledge_graph: Any, openai_key: Optional[str] = None, 
               run_validation: bool = True, alignment_profile: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Orchestrate the reasoning process by selecting and running the appropriate reasoning module
    and validation nodes.
    
    Args:
        query: User query
        knowledge_graph: Knowledge graph instance
        openai_key: OpenAI API key (required for some modules)
        run_validation: Whether to run validation nodes
        alignment_profile: Optional user alignment profile
        
    Returns:
        Dictionary containing reasoning results and validation results
    """
    try:
        # Select the most appropriate reasoning module
        query_embedding = model.encode(query, convert_to_tensor=True)
        similarity_scores = util.cos_sim(query_embedding, rm_embeddings)
        best_index = int(similarity_scores.argmax())
        selected_rm_name = rm_names[best_index]
        rm_info = RM_REGISTRY[selected_rm_name]

        print(f"[Kairos Orchestrator] Selected RM: {selected_rm_name}")
        
        # Check if OpenAI key is required but not provided
        if rm_info.get("requires_openai", False) and not openai_key:
            raise ValueError(f"The selected reasoning module '{selected_rm_name}' requires an OpenAI API key")
        
        # Import and instantiate the reasoning module
        rm_module = importlib.import_module(rm_info["module"])
        
        # Handle both class-based and function-based modules
        if "class" in rm_info:
            RMClass = getattr(rm_module, rm_info["class"])
            rm_instance = RMClass()
            rm_result = rm_instance.run(query, knowledge_graph)
        else:
            rm_function = getattr(rm_module, rm_info["function"])
            # Pass OpenAI key if the function accepts it
            if rm_info.get("requires_openai", False):
                rm_result = rm_function(query, knowledge_graph, openai_key)
            else:
                rm_result = rm_function(query, knowledge_graph)
        
        # Add metadata about which module was used
        rm_result["module_used"] = selected_rm_name
        
        # Run validation nodes if requested
        validation_results = {}
        if run_validation and openai_key:
            for vn_name, vn_info in VN_REGISTRY.items():
                try:
                    print(f"[Kairos Orchestrator] Running validation node: {vn_name}")
                    vn_module = importlib.import_module(vn_info["module"])
                    vn_function = getattr(vn_module, vn_info["function"])
                    
                    # Prepare arguments based on requirements
                    vn_args = [rm_result]
                    if vn_info.get("requires_kg", False):
                        vn_args.append(knowledge_graph)
                    if vn_info.get("requires_openai", False):
                        vn_args.append(openai_key)
                    
                    # Special case for alignment VN which needs a profile
                    if vn_name == "alignment" and alignment_profile:
                        vn_args.append(alignment_profile)
                    
                    # Run the validation node
                    vn_result = vn_function(*vn_args)
                    validation_results[vn_name] = vn_result
                except Exception as e:
                    print(f"[Kairos Orchestrator] Error in validation node {vn_name}: {str(e)}")
                    validation_results[vn_name] = {
                        "valid": False,
                        "score": 0.0,
                        "feedback": f"Error: {str(e)}"
                    }
        
        # ==================== HEBBIAN PLASTICITY INTEGRATION ====================
        # Apply Hebbian learning: strengthen edges used in reasoning
        hebbian_stats = apply_hebbian_learning(knowledge_graph, rm_result, validation_results)

        # Combine results
        final_result = {
            "reasoning": rm_result,
            "validation": validation_results,
            "hebbian_plasticity": hebbian_stats  # Include plasticity stats in response
        }

        return final_result
        
    except Exception as e:
        print(f"[Kairos Orchestrator] Error: {str(e)}")
        return {
            "error": str(e),
            "reasoning": None,
            "validation": {}
        }