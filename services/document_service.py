import logging
import os

from services.chunker import chunk_pages
from services.embedder import generate_embeddings
from services.pdf_loader import extract_pages
from services.summarizer import delete_summary
from services.vector_store import delete_document, store_chunks

logger = logging.getLogger("brainybinder.documents")


def index_document(file_path):

    file_name = os.path.basename(file_path)

    logger.info("Reading: %s", file_name)

    # Replace any previous version of this file and its cached summary
    delete_document(file_name)
    delete_summary(file_name)

    pages = extract_pages(file_path)

    chunks = chunk_pages(pages)

    if not chunks:
        # Usually a scanned PDF (images only, no text layer)
        raise ValueError(
            f"No text could be extracted from {file_name}. "
            "If it is a scanned document, it needs OCR first."
        )

    embeddings = generate_embeddings([chunk["text"] for chunk in chunks])

    store_chunks(file_name, chunks, embeddings)

    logger.info("Stored %d chunks from %d pages", len(chunks), len(pages))

    return len(chunks)


def index_directory(folder_path):

    total_chunks = 0

    for file in sorted(os.listdir(folder_path)):

        if file.lower().endswith(".pdf"):

            path = os.path.join(folder_path, file)

            try:
                total_chunks += index_document(path)
            except ValueError as error:
                logger.warning("%s", error)

    return total_chunks
