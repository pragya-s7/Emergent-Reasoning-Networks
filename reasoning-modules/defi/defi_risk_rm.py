import openai

def run_defi_risk_rm(query, kg, openai_key):
    openai.api_key = openai_key

    # Step 1: Extract relevant triples from the KG
    relevant_triples = kg.query(subject=None, predicate=None, object_=None)
    triples_text = "\n".join(
        f"{s.label} --{r.predicate}--> {o.label}" for s, r, o in relevant_triples
    )

    # Step 2: Ask GPT to reason over the facts and answer the query
    prompt = f"""
You are a DeFi risk analysis agent. You are given the following structured facts:

{triples_text}

User query: "{query}"

Based on the facts above, provide:
1. A short answer to the query
2. A step-by-step reasoning process leading to the answer
3. Which of the above facts support your reasoning

Respond in this exact format:

Answer: <short-answer>
Reasoning:
- Step 1: ...
- Step 2: ...
Sources:
- <subject> --<predicate>--> <object>
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response["choices"][0]["message"]["content"]

    # Step 3: Parse output
    try:
        answer = content.split("Answer:")[1].split("Reasoning:")[0].strip()
        reasoning_lines = content.split("Reasoning:")[1].split("Sources:")[0].strip().split("\n")
        reasoning_steps = [line.strip("- ").strip() for line in reasoning_lines if line.strip()]
        source_lines = content.split("Sources:")[1].strip().split("\n")
        source_triples = [line.strip("- ").strip() for line in source_lines if line.strip()]
    except Exception as e:
        print("Failed to parse RM output:", e)
        return {
            "module": "defi-risk",
            "answer": "Could not parse response.",
            "reasoning_steps": [],
            "source_triples": [],
            "confidence": 0.0
        }

    return {
        "module": "defi-risk",
        "answer": answer,
        "reasoning_steps": reasoning_steps,
        "source_triples": source_triples,
        "confidence": 0.9  # You can make this dynamic later
    }
