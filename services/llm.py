import logging
import time

import httpx
from google import genai
from google.genai import errors, types

from config import (
    ALLOW_GENERAL_KNOWLEDGE,
    GEMINI_API_KEY,
    GEMINI_FALLBACK_MODEL,
    GEMINI_MODEL,
    GEMINI_THINKING_BUDGET,
    LLM_MAX_ATTEMPTS,
    LLM_TIMEOUT_SECONDS,
    SUMMARY_TIMEOUT_SECONDS
)

logger = logging.getLogger("brainybinder.llm")

NOT_FOUND_MESSAGE = "I couldn't find that in your notes."


class LLMUnavailable(Exception):
    """Raised when every model and attempt failed (overloaded, rate-limited or timed out)."""


def _make_client(timeout_seconds):
    """
    Client with a hard timeout and the SDK's own silent retries turned off,
    so we decide how many retries happen (that is where the 2-3 minute
    waits were coming from).
    """

    try:
        http_options = types.HttpOptions(
            timeout=timeout_seconds * 1000,              # milliseconds
            retry_options=types.HttpRetryOptions(attempts=1)
        )
    except (AttributeError, TypeError):
        # Older google-genai versions have no retry_options
        http_options = types.HttpOptions(timeout=timeout_seconds * 1000)

    return genai.Client(api_key=GEMINI_API_KEY, http_options=http_options)


answer_client = _make_client(LLM_TIMEOUT_SECONDS)
summary_client = _make_client(SUMMARY_TIMEOUT_SECONDS)


def _generation_config():

    config = {}

    if GEMINI_THINKING_BUDGET is not None:
        # 0 turns "thinking" off on Flash models: much faster for Q&A
        config["thinking_config"] = types.ThinkingConfig(
            thinking_budget=GEMINI_THINKING_BUDGET
        )

    return types.GenerateContentConfig(**config) if config else None


def _is_retryable(error):

    if isinstance(error, errors.ServerError):           # 500 / 503 overloaded
        return True

    if isinstance(error, errors.ClientError) and getattr(error, "code", None) == 429:
        return True                                     # rate limited

    return isinstance(error, (httpx.TimeoutException, httpx.TransportError))


def _generate(prompt, client):

    models = [GEMINI_MODEL]

    if GEMINI_FALLBACK_MODEL and GEMINI_FALLBACK_MODEL != GEMINI_MODEL:
        models.append(GEMINI_FALLBACK_MODEL)

    last_error = None

    for model in models:

        generation_config = _generation_config()

        for attempt in range(1, LLM_MAX_ATTEMPTS + 1):

            started = time.perf_counter()

            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=generation_config
                )

                logger.info(
                    "LLM %s answered in %.1fs (attempt %d)",
                    model, time.perf_counter() - started, attempt
                )

                return (response.text or "").strip()

            except Exception as error:

                last_error = error

                is_bad_request = (
                    isinstance(error, errors.ClientError)
                    and getattr(error, "code", None) == 400
                )

                if is_bad_request and generation_config is not None:
                    # Some models reject the thinking setting.
                    # Retry this model once without it.
                    logger.warning(
                        "LLM %s rejected the request settings, retrying without them: %s",
                        model, error
                    )
                    generation_config = None
                    continue

                is_quota_error = (
                    isinstance(error, errors.ClientError)
                    and getattr(error, "code", None) == 429
                )
                if is_quota_error:
                    # Daily/minute limit reached: retrying this model won't help,
                    # move straight to the fallback model.
                    logger.warning("LLM %s quota exceeded, trying next model", model)
                    break
                
                if not _is_retryable(error):
                    # Wrong model name, bad key, etc.: skip to the next
                    # model instead of crashing the request.
                    logger.error("LLM %s cannot be used: %s", model, error)
                    break

                logger.warning(
                    "LLM %s failed after %.1fs (attempt %d): %s",
                    model, time.perf_counter() - started, attempt, error
                )

                if attempt < LLM_MAX_ATTEMPTS:
                    time.sleep(attempt)                 # 1s, 2s, ...

    raise LLMUnavailable(str(last_error))


# ------------------------------------------------------------------ prompts

FORMAT_RULES = """
- Write in clear, natural English and start directly with the answer.
- Do not use Markdown symbols such as **, ##, or bullet points unless the user explicitly asks.
- Use short paragraphs, with simple headings on their own line when the answer is long.
- Follow any style the user asks for (simpler, shorter, more detailed, an example, exam-style, etc.).
"""


def _history_block(history):

    if not history:
        return ""

    turns = "\n\n".join(
        f"User: {turn['question']}\nBrainyBinder: {turn['answer']}"
        for turn in history
    )

    return f"""
Earlier in this conversation:
-------------------------
{turns}
-------------------------
Use this only to understand follow-up questions such as "explain that more simply".
"""


def _grounding_rules(has_context):

    if ALLOW_GENERAL_KNOWLEDGE:

        if not has_context:
            return f"""
- None of the user's notes matched this question.
- Begin your answer with exactly: "{NOT_FOUND_MESSAGE}"
- Then add a section headed "Beyond your notes:" with a short, accurate general explanation.
"""

        return """
- Answer from the notes first. They are the source of truth.
- If the notes are thin, or the user asks for a simpler or deeper explanation, you may add a short section headed "Beyond your notes:" with general knowledge. Never mix general knowledge into the notes-based part.
- If the notes do not cover the question at all, say so plainly before any "Beyond your notes:" section.
"""

    if not has_context:
        return f"""
- None of the user's notes matched this question.
- Reply with exactly: "{NOT_FOUND_MESSAGE}"
"""

    return f"""
- Use ONLY the notes below. Never use outside knowledge.
- You may rephrase and simplify what the notes say.
- If the notes only partly answer the question, answer what they cover and say what is missing.
- If they do not answer it at all, reply with exactly: "{NOT_FOUND_MESSAGE}"
"""


def build_answer_prompt(question, chunks, history):

    if chunks:
        context = "\n\n".join(
            f"[{chunk['source']}, page {chunk['page']}]\n{chunk['text']}"
            for chunk in chunks
        )
    else:
        context = "(no matching notes)"

    return f"""
You are BrainyBinder, a study assistant that answers questions from the user's own uploaded notes.

Rules:
{_grounding_rules(bool(chunks))}
{FORMAT_RULES}
{_history_block(history)}
Notes:
-------------------------
{context}
-------------------------

Question:
{question}

Answer:
"""


def generate_answer(question, chunks, history=None):

    if not chunks and not ALLOW_GENERAL_KNOWLEDGE:
        # Nothing relevant and no general knowledge allowed:
        # no need to spend an API call.
        return NOT_FOUND_MESSAGE

    prompt = build_answer_prompt(question, chunks, history or [])

    return _generate(prompt, answer_client)


def summarize_text(text, file_name, partial=False):
    """
    partial=True is used for one section of a very long document;
    the section summaries are then combined with combine_summaries().
    """

    if partial:
        task = "Summarize this section of the document. Keep every key fact, number, name and decision."
    else:
        task = """Summarize the whole document. Cover every major section, not just the start.
Group related ideas under short headings and explain each in paragraph form.
Keep key facts, numbers, names and decisions."""

    prompt = f"""
You are BrainyBinder. {task}
Use only the document text below.
{FORMAT_RULES}
Document: {file_name}
-------------------------
{text}
-------------------------

Summary:
"""

    return _generate(prompt, summary_client)


def combine_summaries(section_summaries, file_name):

    joined = "\n\n".join(
        f"Section {index}:\n{summary}"
        for index, summary in enumerate(section_summaries, start=1)
    )

    prompt = f"""
You are BrainyBinder. Below are summaries of consecutive sections of one document.
Combine them into one summary of the whole document. Cover every section,
remove repetition, and group related ideas under short headings.
{FORMAT_RULES}
Document: {file_name}
-------------------------
{joined}
-------------------------

Summary:
"""

    return _generate(prompt, summary_client)