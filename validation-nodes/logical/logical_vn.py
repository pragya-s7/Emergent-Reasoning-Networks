import openai

def run_logical_vn(reasoning_output, openai_key):
    openai.api_key = openai_key

    reasoning = "\n".join(f"- {step}" for step in reasoning_output["reasoning_steps"])
    answer = reasoning_output["answer"]

    prompt = f"""
You are a logical validation agent. Given the following reasoning steps and conclusion, check whether the reasoning follows logically.

Reasoning:
{reasoning}

Conclusion:
{answer}

Evaluate:
1. Does the reasoning follow logically?
2. Are there any gaps or fallacies?
3. How strong is the logical flow?

Respond in this format:

Valid: <true|false>
Score: <0-1>
Feedback: <your analysis>
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response["choices"][0]["message"]["content"]

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
            "feedback": "Could not parse validator response."
        }

    return {
        "vn_type": "LogicalVN",
        "valid": valid,
        "score": score,
        "feedback": feedback
    }
