import chromadb

from config import (
    VECTOR_DB_PATH,
    COLLECTION_NAME
)

client = chromadb.PersistentClient(
    path=VECTOR_DB_PATH
)

# Cosine distance suits sentence-transformer embeddings and gives
# distances between 0 (same meaning) and ~1 (unrelated), which makes
# the relevance cutoff in config.MAX_DISTANCE easy to reason about.
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"}
)


def store_chunks(file_name, chunks, embeddings):
    """
    chunks: list of {"text": ..., "page": ...}
    Added in one batch instead of one call per chunk.
    """

    if not chunks:
        return

    collection.add(
        ids=[f"{file_name}_{index}" for index in range(len(chunks))],
        documents=[chunk["text"] for chunk in chunks],
        embeddings=embeddings,
        metadatas=[
            {
                "source": file_name,
                "chunk": index,
                "page": chunk["page"]
            }
            for index, chunk in enumerate(chunks)
        ]
    )


def search(query_embedding, top_k=5, file_name=None):

    if collection.count() == 0:
        return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

    arguments = {
        "query_embeddings": [query_embedding],
        "n_results": top_k
    }

    if file_name:
        arguments["where"] = {"source": file_name}

    return collection.query(**arguments)


def get_document_chunks(file_name):
    """
    Every chunk of one document, in reading order. Used for summaries,
    which need the whole document rather than the closest matches.
    """

    results = collection.get(
        where={"source": file_name},
        include=["documents", "metadatas"]
    )

    rows = sorted(
        zip(results["documents"], results["metadatas"]),
        key=lambda row: row[1]["chunk"]
    )

    return [document for document, _ in rows]


def delete_document(file_name):

    collection.delete(
        where={
            "source": file_name
        }
    )


def list_documents():

    # Only fetch metadata, not every chunk's text and embedding.
    results = collection.get(include=["metadatas"])

    return sorted({metadata["source"] for metadata in results["metadatas"]})
