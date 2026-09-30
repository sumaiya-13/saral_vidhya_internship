import json
import os
from groq import Groq

def _client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured in the environment")
    return Groq(api_key=api_key)

def generate_summary(text: str) -> str:
    client = _client()
    prompt = f"""
Summarize the following educational PDF text.
Use clear headings and concise bullet points.
Do not invent information. Only use the supplied text.

TEXT:
{text[:30000]}
"""
    response = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        messages=[
            {"role": "system", "content": "You summarize educational material accurately."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content

def generate_quiz(text: str) -> str:
    client = _client()
    prompt = f"""
Create 10 multiple-choice questions from the supplied educational text.
Return valid JSON only in this format:
[
  {{
    "question": "...",
    "options": ["A", "B", "C", "D"],
    "answer": "A"
  }}
]
Do not use knowledge outside the supplied text.

TEXT:
{text[:30000]}
"""
    response = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        messages=[
            {"role": "system", "content": "You generate factual educational quizzes."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    content = response.choices[0].message.content.strip()
    try:
        return json.dumps(json.loads(content), indent=2)
    except json.JSONDecodeError:
        return content
