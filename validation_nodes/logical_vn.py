import anthropic
from typing import Dict, Any, Optional

# === LogicalVN ===
def run_logical_vn(reasoning_output: Dict[str, Any], anthropic_key: str) -> Dict[str, Any]:
    """
    Validate the logical coherence of reasoning steps.

    Args:
        reasoning_output: The output from a reasoning module
        anthropic_key: OpenAI API key

    Returns:
        Validation result with validity score and feedback
    """
    if not anthropic_key:
        raise ValueError("OpenAI API key is required for logical validation")
    
    anthropic.api_key = anthropic_key

    # Extract reasoning steps and answer - handle both formats
    try:
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
            raise KeyError("No reasoning steps found (expected 'reasoning_steps' or 'reasoningPath')")
    except KeyError as e:
        return {
            "vn_type": "LogicalVN",
            "valid": False,
            "score": 0.0,
            "feedback": f"Missing required field in reasoning output: {e}"
        }

    # Build prompt for validation
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

    # Call OpenAI API
    try:
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
    except Exception as e:
        return {
            "vn_type": "LogicalVN",
            "valid": False,
            "score": 0.0,
            "feedback": f"An error occurred: {str(e)}"
        }

    # Parse GPT Output
    try:
        valid = "true" in validation_result.lower().split("valid:")[1].split("\n")[0].strip()
        score = float(validation_result.lower().split("score:")[1].split("\n")[0].strip())
        feedback = validation_result.split("Feedback:")[1].strip()
    except Exception as e:
        return {
            "vn_type": "LogicalVN",
            "valid": False,
            "score": 0.0,
            "feedback": f"Could not parse validator response: {str(e)}"
        }

    result = {
        "vn_type": "LogicalVN",
        "valid": valid,
        "score": round(score, 2),
        "feedback": feedback
    }

    return result
