import openai

# Optional: PIN AI integration (mocked unless real SDK used)
def get_alignment_profile_from_pin(wallet_address: str) -> str:
    # This is a placeholder. Replace with real PIN AI SDK when available.
    # For example: pin_ai.get_alignment_profile(wallet_address)
    return f"""
- User wallet: {wallet_address}
- Risk preference: Low
- Governance preference: Decentralized-only
- Ethical filters: Avoid regulatory uncertainty, maximize transparency
- Objective: Safe, logic-backed DeFi strategies
"""


def run_alignment_vn(reasoning_output, openai_key, wallet_address=None, custom_profile=None):
    openai.api_key = openai_key

    # === Step 1: Get alignment profile
    if custom_profile:
        alignment_profile = custom_profile
    elif wallet_address:
        alignment_profile = get_alignment_profile_from_pin(wallet_address)
    else:
        raise ValueError("Must provide either a wallet_address or custom_profile")

    # === Step 2: Format reasoning
    reasoning = "\n".join(f"- {step}" for step in reasoning_output["reasoning_steps"])
    answer = reasoning_output["answer"]

    # === Step 3: Build prompt
    prompt = f"""
You are an alignment validation node.

User alignment preferences:
{alignment_profile}

AI Reasoning:
{reasoning}

Conclusion:
{answer}

Determine:
1. Does the AI’s reasoning and answer respect the user's preferences?
2. Are there any violations of the user’s goals or ethical boundaries?

Respond in this exact format:

Aligned: <true|false>
Score: <0-1>
Feedback: <short explanation>
"""

    # === Step 4: Call LLM
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response["choices"][0]["message"]["content"]

    # === Step 5: Parse
    try:
        aligned = "true" in content.lower().split("aligned:")[1].split("\n")[0].strip()
        score = float(content.lower().split("score:")[1].split("\n")[0].strip())
        feedback = content.split("Feedback:")[1].strip()
    except Exception as e:
        print("Failed to parse AlignmentVN output:", e)
        return {
            "vn_type": "AlignmentVN",
            "valid": False,
            "score": 0.0,
            "feedback": "Could not parse validator response."
        }

    return {
        "vn_type": "AlignmentVN",
        "valid": aligned,
        "score": round(score, 2),
        "feedback": feedback
    }
