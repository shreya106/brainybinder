from services.embedder import generate_embedding
from services.vector_store import (
    search,
    search_document
)


def retrieve(query,
             top_k=3,
             file_name=None):

    query_embedding = generate_embedding(query)

    if file_name:

        return search_document(
            query_embedding,
            file_name,
            top_k
        )

    return search(
        query_embedding,
        top_k
    )