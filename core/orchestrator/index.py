import importlib
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

RM_REGISTRY = {
    "defi": {
        "description": "DeFi analysis of token behaviors, liquidity, and risks",
        "module": "reasoning_modules.defi.index",
        "class": "DeFiReasoningModule"
    },
    "audit": {
        "description": "Smart contract audit history and vulnerability risk detection",
        "module": "reasoning_modules.audit.index",
        "class": "AuditReasoningModule"
    },
    "macro": {
        "description": "Macroeconomic trends and global financial indicators",
        "module": "reasoning_modules.macro.index",
        "class": "MacroReasoningModule"
    },
    "sentiment": {
        "description": "Community and market sentiment analysis from social platforms",
        "module": "reasoning_modules.sentiment.index",
        "class": "SentimentReasoningModule"
    }
}

rm_names = list(RM_REGISTRY.keys())
rm_texts = [RM_REGISTRY[name]["description"] for name in rm_names]
rm_embeddings = model.encode(rm_texts, convert_to_tensor=True)

def orchestrate(query, knowledge_graph):
    query_embedding = model.encode(query, convert_to_tensor=True)
    similarity_scores = util.cos_sim(query_embedding, rm_embeddings)
    best_index = int(similarity_scores.argmax())
    selected_rm_name = rm_names[best_index]
    rm_info = RM_REGISTRY[selected_rm_name]

    print(f"[Kairos Orchestrator] Selected RM: {selected_rm_name}")

    rm_module = importlib.import_module(rm_info["module"])
    RMClass = getattr(rm_module, rm_info["class"])
    rm_instance = RMClass()

    return rm_instance.run(query, knowledge_graph)