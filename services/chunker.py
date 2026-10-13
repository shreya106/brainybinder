import re

from config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP
)


def _split_sentences(text, max_length):
    """
    Split text into sentences. Any "sentence" longer than max_length
    (titles, tables, text with no full stops) is cut into word-aligned
    pieces, so one oversized sentence can never be repeated across chunks.
    """

    sentences = re.split(r"(?<=[.!?])\s+", text)

    pieces = []

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        while len(sentence) > max_length:

            cut = sentence.rfind(" ", 0, max_length)

            if cut <= 0:
                cut = max_length

            pieces.append(sentence[:cut].strip())
            sentence = sentence[cut:].strip()

        if sentence:
            pieces.append(sentence)

    return pieces


def chunk_pages(pages,
                chunk_size=CHUNK_SIZE,
                overlap=CHUNK_OVERLAP):
    """
    pages: list of (page_number, text)
    returns: list of {"text": ..., "page": ...}

    Chunks are built from whole sentences up to chunk_size characters.
    The last ~overlap characters of sentences are carried into the next
    chunk so ideas that span a boundary are not lost.
    """

    # Flatten into (sentence, page) so chunks can cross page boundaries
    # while still knowing the page they start on.
    units = []

    for page_number, text in pages:
        for sentence in _split_sentences(text, chunk_size):
            units.append((sentence, page_number))

    chunks = []
    current = []          # list of (sentence, page)
    current_length = 0

    for sentence, page in units:

        added_length = len(sentence) + (1 if current else 0)

        if current and current_length + added_length > chunk_size:

            chunks.append({
                "text": " ".join(s for s, _ in current),
                "page": current[0][1]
            })

            # Carry over trailing sentences up to `overlap` characters,
            # but never the whole chunk (that is what caused duplicates).
            carried = []
            carried_length = 0

            for s, p in reversed(current[1:]):

                if carried_length + len(s) > overlap:
                    break

                carried.insert(0, (s, p))
                carried_length += len(s) + 1

            current = carried
            current_length = sum(len(s) for s, _ in current) + max(len(current) - 1, 0)
            added_length = len(sentence) + (1 if current else 0)

        current.append((sentence, page))
        current_length += added_length

    if current:
        chunks.append({
            "text": " ".join(s for s, _ in current),
            "page": current[0][1]
        })

    return chunks
