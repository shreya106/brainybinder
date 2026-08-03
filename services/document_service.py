import os

from services.pdf_loader import extract_text
from services.chunker import chunk_text
from services.embedder import generate_embeddings
from services.vector_store import (
    store_chunks,
    delete_document
)


def index_document(file_path):

    file_name = os.path.basename(file_path)

    print(f"\nReading: {file_name}")

    # Delete previous version if it exists
    delete_document(file_name)

    text = extract_text(file_path)

    chunks = chunk_text(text)

    embeddings = generate_embeddings(chunks)

    store_chunks(
        file_name,
        chunks,
        embeddings
    )

    print(f"Stored {len(chunks)} chunks")

    return len(chunks)


def index_directory(folder_path):

    total_chunks = 0

    for file in os.listdir(folder_path):

        if file.endswith(".pdf"):

            path = os.path.join(folder_path, file)

            total_chunks += index_document(path)

    return total_chunks