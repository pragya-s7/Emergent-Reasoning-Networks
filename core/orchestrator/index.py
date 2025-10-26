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
        "description": "Financial analysis of market behaviors, liquidity, and risk assessment",
        "module": "reasoning_modules.defi_risk.index",
        "function": "run_financial_analysis_rm",
        "requires_openai": True
    },
    "security_audit": {
        "description": "Security audit history and vulnerability risk detection",
        "module": "reasoning_modules.audit_rm",
        "class": "SecurityAuditReasoningModule",
        "requires_openai": False
    },
    "macro": {
        "description": "Macroeconomic trends and global financial indicators",
        "module": "reasoning_modules.macro_rm",
        "class": "MacroReasoningModule",
        "requires_openai": False
    },
    "sentiment": {
        "description": "Community and market sentiment analysis from social platforms",
        "module": "reasoning_modules.sentiment_rm",
        "class": "SentimentReasoningModule",
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
        
        # Combine results
        final_result = {
            "reasoning": rm_result,
            "validation": validation_results
        }
        
        return final_result
        
    except Exception as e:
        print(f"[Kairos Orchestrator] Error: {str(e)}")
        return {
            "error": str(e),
            "reasoning": None,
            "validation": {}
        }