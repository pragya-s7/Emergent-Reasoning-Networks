# === GroundingVN ===
import re
import json

def run_grounding_vn(reasoning_output, kg):
    """
    Validate that reasoning claims are grounded in the knowledge graph.
    """
    print("--- GroundingVN --- ")
    claimed_triples = reasoning_output.get("source_triples", [])
    print(f"Received triples: {json.dumps(claimed_triples, indent=2)}")

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
    
    triple_pattern = re.compile(r"(.*?)\s*--(.+?)-->\s*(.*)")

    for triple_str in claimed_triples:
        match = triple_pattern.match(triple_str)
        if not match:
            print(f"  - No match for: {triple_str}")
            continue

        total += 1
        subj, pred, obj = [s.strip() for s in match.groups()]
        print(f"  - Parsed: ('{subj}', '{pred}', '{obj}')")

        matches = kg.query(subject=subj, predicate=pred, object_=obj)
        if matches:
            print("    - Found in KG")
            grounded += 1
        else:
            print("    - NOT found in KG")
            missing.append((subj, pred, obj))

    score = grounded / total if total > 0 else 1.0
    valid = (score >= 0.8)
    print(f"Score: {score}")

    feedback = "All claimed triples are grounded in the KG." if not missing else (
        f"Missing triples: {', '.join([f'{s} --{p}--> {o}' for s, p, o in missing])}"
    )

    return {
        "vn_type": "GroundingVN",
        "valid": valid,
        "score": round(score, 2),
        "feedback": feedback
    }
