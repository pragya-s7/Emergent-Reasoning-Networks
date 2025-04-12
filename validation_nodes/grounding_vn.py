# === Optional: Story Protocol Integration ===
def register_grounding_to_story(reasoning_output):
    print("📘 [Story Protocol] Registered fully grounded insight path as composable IP.")
    return {
        "status": "registered",
        "cid": "ipfs://mockedCID-grounded-45678",
        "hash": "0xGROUND_HASH"
    }

# === GroundingVN with AVS & Story Protocol ===
def run_grounding_vn(reasoning_output, kg, story_threshold=1.0):
    claimed_triples = reasoning_output.get("source_triples", [])
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
        "feedback": feedback,
        "story_protocol": None
    }

    # === Story Protocol Trigger (perfect grounding = reusable logical subgraph)
    if valid and score >= story_threshold:
        story_result = register_grounding_to_story(reasoning_output)
        result["story_protocol"] = story_result

    return result
