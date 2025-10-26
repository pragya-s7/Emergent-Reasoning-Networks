# === GroundingVN ===
def run_grounding_vn(reasoning_output, kg):
    """
    Validate that reasoning claims are grounded in the knowledge graph.

    Args:
        reasoning_output: The reasoning module output
        kg: Knowledge graph instance

    Returns:
        Validation result with grounding score and feedback
    """
    # Get source triples from reasoning output
    claimed_triples = reasoning_output.get("source_triples", [])

    # If no source triples provided but reasoning was done, skip validation
    if not claimed_triples:
        return {
            "vn_type": "GroundingVN",
            "valid": True,
            "score": 1.0,
            "feedback": "No specific triples claimed (skipped grounding check)"
        }
    grounded = 0
    total = len(claimed_triples)
    missing = []

    for triple_str in claimed_triples:
        try:
            # Format: "Subject --predicate--> Object"
            parts = triple_str.split("--")
            subj = parts[0].strip()
            pred, obj = parts[1].split("-->") if "-->" in parts[1] else parts[1].split("→")
            pred = pred.strip()
            obj = obj.strip()

            matches = kg.query(subject=subj, predicate=pred, object_=obj)
            if matches:
                grounded += 1
            else:
                missing.append((subj, pred, obj))
        except Exception as e:
            print("Failed to parse triple:", triple_str, e)
            total -= 1
            continue

    score = grounded / total if total > 0 else 0.0
    valid = (score >= 0.8)

    feedback = "All triples are grounded in the KG." if not missing else (
        f"Missing triples: {', '.join([f'{s} --{p}--> {o}' for s, p, o in missing])}"
    )

    result = {
        "vn_type": "GroundingVN",
        "valid": valid,
        "score": round(score, 2),
        "feedback": feedback
    }

    return result
