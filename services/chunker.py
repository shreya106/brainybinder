import re

from config import (
    CHUNK_SIZE,
    OVERLAP_SENTENCES
)


def chunk_text(
    text,
    chunk_size=CHUNK_SIZE,
    overlap_sentences=OVERLAP_SENTENCES
):

    # Split document into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current_sentences = []
    current_length = 0

    for sentence in sentences:

        # If adding this sentence stays within chunk size
        if current_length + len(sentence) <= chunk_size:

            current_sentences.append(sentence)
            current_length += len(sentence)

        else:

            # Save current chunk
            chunks.append(" ".join(current_sentences))

            # Keep the last N sentences as overlap
            current_sentences = current_sentences[-overlap_sentences:]

            # Recalculate current length
            current_length = sum(len(s) for s in current_sentences)

            # Add the new sentence
            current_sentences.append(sentence)
            current_length += len(sentence)

    # Store last chunk
    if current_sentences:
        chunks.append(" ".join(current_sentences))

    return chunks