# === GroundingVN ===
import re

def run_grounding_vn(reasoning_output, kg):
    """
    Validate that reasoning claims are grounded in the knowledge graph.
    """
    claimed_triples = reasoning_output.get("source_triples", [])

    if not claimed_triples:
        return {
            "vn_type": "GroundingVN",
            "valid": True,
            "score": 1.0,
            "feedback": "No specific triples claimed (skipped grounding check)"
        }
    
    grounded = 0
    total = 0
    missing = []
    
    # Regex to capture subject, predicate, and object
    triple_pattern = re.compile(r"(.*?)\s*--(.+?)-->\s*(.*)")

    for triple_str in claimed_triples:
        match = triple_pattern.match(triple_str)
        if not match:
            continue

        total += 1
        subj, pred, obj = [s.strip() for s in match.groups()]

        matches = kg.query(subject=subj, predicate=pred, object_=obj)
        if matches:
            grounded += 1
        else:
            missing.append((subj, pred, obj))

    score = grounded / total if total > 0 else 1.0
    valid = (score >= 0.8)

    feedback = "All claimed triples are grounded in the KG." if not missing else (
        f"Missing triples: {', '.join([f'{s} --{p}--> {o}' for s, p, o in missing])}"
    )

    return {
        "vn_type": "GroundingVN",
        "valid": valid,
        "score": round(score, 2),
        "feedback": feedback
    }
