from google import genai

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL
)

client = genai.Client(
    api_key=GEMINI_API_KEY
)


def build_prompt(question, context):

    return f"""
You are BrainyBinder, an AI assistant that answers questions using ONLY the provided context.

Instructions:

- Use ONLY the provided context.
- Never use outside knowledge.
- Write in clear, natural English.
- Do not use Markdown symbols such as **, ##, or bullet points unless the user explicitly asks.
- Organize the answer into short paragraphs with meaningful headings when appropriate.
- For summaries, group related ideas into sections and explain them in paragraph form.
- Do not say "Based on the provided context" or "Based on the retrieved excerpts." Start directly with the answer.
- If the context is insufficient, clearly mention that the answer is based only on the available retrieved information.
- Only say "I could not find that information in the provided documents." if there is no relevant information in the retrieved context.

Context:
-------------------------
{context}
-------------------------

Question:
{question}

Answer:
"""


def generate_answer(question, context):

    prompt = build_prompt(question, context)

    print("=" * 100)
    print(prompt)
    print("=" * 100)

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )

    return response.text