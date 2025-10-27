import anthropic

def get_default_alignment_profile() -> str:
    """Return a default alignment profile for demo purposes."""
    return """
- Risk preference: Moderate
- Decision style: Evidence-based and transparent
- Ethical filters: Prioritize accuracy and verifiable claims
- Objective: Balanced, well-reasoned analysis
"""


def run_alignment_vn(reasoning_output, anthropic_key, alignment_profile=None):
    """
    Validate that reasoning aligns with user preferences and constraints.

    Args:
        reasoning_output: The reasoning module output
        anthropic_key: OpenAI API key
        alignment_profile: Optional user alignment profile (dict or str)

    Returns:
        Validation result with alignment score and feedback
    """
    anthropic.api_key = anthropic_key

    # === Step 1: Get alignment profile
    if alignment_profile:
        if isinstance(alignment_profile, dict):
            # Convert dict to formatted string
            profile_lines = [f"- {k}: {v}" for k, v in alignment_profile.items()]
            alignment_profile_str = "\n".join(profile_lines)
        else:
            alignment_profile_str = str(alignment_profile)
    else:
        alignment_profile_str = get_default_alignment_profile()

    # === Step 2: Format reasoning
    # Handle both old format (reasoning_steps/answer) and new format (reasoningPath/conclusion)
    if "reasoning_steps" in reasoning_output:
        reasoning = "\n".join(f"- {step}" for step in reasoning_output["reasoning_steps"])
        answer = reasoning_output.get("answer", reasoning_output.get("conclusion", ""))
    elif "reasoningPath" in reasoning_output:
        reasoning_steps = [
            step.get("data", step.get("inference", str(step)))
            for step in reasoning_output["reasoningPath"]
        ]
        reasoning = "\n".join(f"- {step}" for step in reasoning_steps)
        answer = reasoning_output.get("conclusion", "")
    else:
        reasoning = str(reasoning_output)
        answer = reasoning_output.get("conclusion", reasoning_output.get("answer", ""))

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

    # === Step 5: Parse
    try:
        aligned = "true" in validation_result.lower().split("aligned:")[1].split("\n")[0].strip()
        score = float(validation_result.lower().split("score:")[1].split("\n")[0].strip())
        feedback = validation_result.split("Feedback:")[1].strip()
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
