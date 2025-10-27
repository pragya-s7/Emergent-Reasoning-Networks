import anthropic

# === Novelty VN ===
def run_novelty_vn(reasoning_output, kg, anthropic_key):
    anthropic.api_key = anthropic_key

    # --- Step 1: Extract KG facts as text
    # Query all relations from KG
    all_triples = kg.query()
    kg_text = "\n".join(
        f"{s.label} --{r.predicate}--> {o.label}" for s, r, o in all_triples
    )

    # --- Step 2: Get reasoning steps - handle both formats
    if "reasoning_steps" in reasoning_output:
        reasoning = "\n".join(f"- {step}" for step in reasoning_output["reasoning_steps"])
    elif "reasoningPath" in reasoning_output:
        reasoning_steps = [
            step.get("data", step.get("inference", str(step)))
            for step in reasoning_output["reasoningPath"]
        ]
        reasoning = "\n".join(f"- {step}" for step in reasoning_steps)
    else:
        reasoning = str(reasoning_output)

    prompt = f"""
You are a novelty evaluator for AI reasoning.

You are given:
Known facts (from the knowledge graph):
{kg_text}

Reasoning steps from an AI module:
{reasoning}

Determine:
1. Does the reasoning combine facts in a new way?
2. Does it introduce any insights that are not already explicitly in the KG?
3. Is the conclusion creative, emergent, or merely obvious?

Respond in this format:

Novel: <true|false>
Score: <0-1>
Feedback: <short explanation>
"""

    client = anthropic.Anthropic(api_key=anthropic_key)
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    
    # Extract the response content
    validation_result = response.content[0].text

    # --- Step 3: Parse LLM output
    try:
        score = float(validation_result.lower().split("score:")[1].split("\n")[0].strip())
        novel = score > 0.2
        feedback = validation_result.split("Feedback:")[1].strip()
    except Exception as e:
        print("Failed to parse NoveltyVN output:", e)
        return {
            "vn_type": "NoveltyVN",
            "valid": False,
            "score": 0.0,
            "feedback": "Could not parse validator response."
        }

    result = {
        "vn_type": "NoveltyVN",
        "valid": novel,
        "score": round(score, 2),
        "feedback": feedback
    }

    return result
