from config import MAX_DISTANCE, TOP_K
from services.embedder import generate_embedding
from services.vector_store import search


def retrieve(query, top_k=TOP_K, file_name=None):
    """
    Returns a list of matching chunks, closest first:
    [{"text", "source", "chunk", "page", "distance"}, ...]

    Chunks further than MAX_DISTANCE are dropped, so an off-topic
    question returns an empty list instead of random notes.
    """

    query_embedding = generate_embedding(query)

    results = search(
        query_embedding,
        top_k=top_k,
        file_name=file_name
    )

    matches = []

    for text, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):

        if distance > MAX_DISTANCE:
            continue

        matches.append({
            "text": text,
            "source": metadata["source"],
            "chunk": metadata["chunk"],
            "page": metadata.get("page"),
            "distance": round(distance, 4)
        })

    return matches
