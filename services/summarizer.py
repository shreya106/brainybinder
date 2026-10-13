import logging
import os
import threading

from config import SUMMARY_FOLDER
from services.llm import combine_summaries, summarize_text
from services.vector_store import get_document_chunks

logger = logging.getLogger("brainybinder.summarizer")

# Gemini models accept very long inputs, so most notes fit in one call.
# Only very long documents are summarized section by section.
SINGLE_CALL_LIMIT = 300_000   # characters (~75k tokens)
SECTION_SIZE = 200_000        # characters per section for very long documents

_locks = {}
_locks_guard = threading.Lock()


def _lock_for(file_name):

    with _locks_guard:
        return _locks.setdefault(file_name, threading.Lock())


def _cache_path(file_name):

    return os.path.join(SUMMARY_FOLDER, f"{file_name}.txt")


def delete_summary(file_name):

    path = _cache_path(file_name)

    if os.path.exists(path):
        os.remove(path)


def get_summary(file_name):
    """
    Returns the cached summary if there is one; otherwise builds it from
    EVERY chunk of the document (in order), caches it, and returns it.
    """

    with _lock_for(file_name):

        path = _cache_path(file_name)

        if os.path.exists(path):
            with open(path, encoding="utf-8") as cached:
                return cached.read()

        chunks = get_document_chunks(file_name)

        if not chunks:
            return None

        # Neighbouring chunks overlap slightly; that is harmless here.
        text = "\n".join(chunks)

        if len(text) <= SINGLE_CALL_LIMIT:
            summary = summarize_text(text, file_name)
        else:
            sections = [
                text[start:start + SECTION_SIZE]
                for start in range(0, len(text), SECTION_SIZE)
            ]
            partials = [
                summarize_text(section, file_name, partial=True)
                for section in sections
            ]
            summary = combine_summaries(partials, file_name)

        os.makedirs(SUMMARY_FOLDER, exist_ok=True)

        with open(path, "w", encoding="utf-8") as cached:
            cached.write(summary)

        return summary


def precompute_summary(file_name):
    """Run after upload, in the background, so the first request is instant."""

    try:
        get_summary(file_name)
        logger.info("Summary ready for %s", file_name)
    except Exception as error:
        # Not fatal: it will be generated on first request instead.
        logger.warning("Could not precompute summary for %s: %s", file_name, error)
