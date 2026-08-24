"""
LLM provider abstraction. LLM_PROVIDER env var picks Groq or OpenAI at
startup — the rest of the app only ever calls generate_answer(), so
switching providers later never touches rag_pipeline.py.
"""
import logging

from app.config import settings

logger = logging.getLogger("docuchat.llm")

SYSTEM_PROMPT = """You are DocuChat, a document question-answering assistant.

Answer the user's question using ONLY the provided context below.

Rules:
- Do not use outside knowledge.
- Do not invent or hallucinate information not present in the context.
- If the answer is not contained in the context, say exactly: "I couldn't find this information in the uploaded documents."
- Cite which source(s) support your answer when relevant.
- Prefer precise, concise answers over unnecessarily long ones.
"""


class LLMConfigError(Exception):
    pass


def _build_context(chunks: list[dict]) -> str:
    parts = []
    for c in chunks:
        loc = f"{c['source']}" + (f" (page {c['page']})" if c.get("page") else "")
        parts.append(f"[{loc}]\n{c['text']}")
    return "\n\n---\n\n".join(parts)


def _call_groq(prompt: str) -> str:
    if not settings.GROQ_API_KEY:
        raise LLMConfigError(
            "GROQ_API_KEY is not set. Add it to your .env file (see .env.example)."
        )
    from groq import Groq

    client = Groq(api_key=settings.GROQ_API_KEY)
    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_tokens=800,
    )
    return response.choices[0].message.content


def _call_openai(prompt: str) -> str:
    if not settings.OPENAI_API_KEY:
        raise LLMConfigError(
            "OPENAI_API_KEY is not set. Add it to your .env file (see .env.example)."
        )
    from openai import OpenAI

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_tokens=800,
    )
    return response.choices[0].message.content


def generate_answer(question: str, chunks: list[dict]) -> str:
    if not chunks:
        return "I couldn't find this information in the uploaded documents."

    context = _build_context(chunks)
    prompt = f"Context:\n{context}\n\nQuestion:\n{question}\n\nAnswer:"

    provider = settings.LLM_PROVIDER.lower()
    try:
        if provider == "groq":
            return _call_groq(prompt)
        elif provider == "openai":
            return _call_openai(prompt)
        else:
            raise LLMConfigError(f"Unknown LLM_PROVIDER: {provider}")
    except LLMConfigError:
        raise
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise
