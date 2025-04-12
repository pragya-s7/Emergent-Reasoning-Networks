import openai

# === Optional: Story Protocol Integration ===
def register_logic_to_story(reasoning_output):
    print("📜 [Story Protocol] Registered logical reasoning path as reusable IP.")
    return {
        "status": "registered",
        "cid": "ipfs://mockedCID-logical-12345",
        "hash": "0xLOGIC_HASH"
    }

# === LogicalVN with AVS & Story Protocol ===
def run_logical_vn(reasoning_output, openai_key, story_threshold=0.9):
    openai.api_key = openai_key

    reasoning = "\n".join(f"- {step}" for step in reasoning_output["reasoning_steps"])
    answer = reasoning_output["answer"]

    prompt = f"""
You are a logical validator.

Your task is to evaluate whether the reasoning steps provided below form a coherent logical flow that supports the conclusion.

Reasoning Steps:
{reasoning}

Conclusion:
{answer}

Determine:
1. Does each step follow logically from the last?
2. Are there any contradictions, fallacies, or jumps in logic?
3. Would this pass peer review?

Respond in this format:

Valid: <true|false>
Score: <0-1>
Feedback: <brief explanation>
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response["choices"][0]["message"]["content"]

    # === Parse GPT Output ===
    try:
        valid = "true" in content.lower().split("valid:")[1].split("\n")[0].strip()
        score = float(content.lower().split("score:")[1].split("\n")[0].strip())
        feedback = content.split("Feedback:")[1].strip()
    except Exception as e:
        print("Failed to parse LogicalVN output:", e)
        return {
            "vn_type": "LogicalVN",
            "valid": False,
            "score": 0.0,
            "feedback": "Could not parse validator response.",
            "story_protocol": None
        }

    result = {
        "vn_type": "LogicalVN",
        "valid": valid,
        "score": round(score, 2),
        "feedback": feedback,
        "story_protocol": None
    }

    # === Story Protocol Trigger (Optional IP registration)
    if valid and score >= story_threshold:
        story_result = register_logic_to_story(reasoning_output)
        result["story_protocol"] = story_result

    return result
