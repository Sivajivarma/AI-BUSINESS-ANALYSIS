
import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:1b"


def generate_business_answer(question, business_context):
    system_prompt = """
You are an AI Business Analyst.

Answer the user's question using the supplied
business data.

Rules:
1. Use the provided data as your primary source.
2. Never invent sales figures or business metrics.
3. Explain your reasoning clearly.
4. Give practical recommendations when appropriate.
5. If the data is insufficient, say so.
6. Use a clear, professional format.
7. Distinguish data-supported findings from suggestions.
8. Treat the supplied business metrics as authoritative.
9. Never recalculate or invent percentages.
10. Never contradict the supplied product or region rankings.
11. Do not claim a product has the highest profit
    unless product-level profit data proves it.
"""

    prompt = f"""
{system_prompt}

BUSINESS DATA:
{business_context}

USER QUESTION:
{question}

Write your answer with these sections when appropriate:
Answer:
Analysis:
Recommendation:
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        },
        timeout=180,
    )

    response.raise_for_status()

    result = response.json()

    return result["response"].strip()