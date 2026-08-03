import chromadb

from config import (
    VECTOR_DB_PATH,
    COLLECTION_NAME
)

client = chromadb.PersistentClient(
    path=VECTOR_DB_PATH
)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)


def store_chunks(file_name, chunks, embeddings):

    for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):

        collection.add(
            ids=[f"{file_name}_{index}"],
            documents=[chunk],
            embeddings=[embedding],
            metadatas=[
                {
                    "source": file_name,
                    "chunk": index
                }
            ]
        )


def search(query_embedding, top_k=3):

    return collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )


def delete_document(file_name):

    collection.delete(
        where={
            "source": file_name
        }
    )


def list_documents():

    results = collection.get()

    documents = set()

    for metadata in results["metadatas"]:
        documents.add(metadata["source"])

    return sorted(list(documents))

def search_document(query_embedding,
                    file_name,
                    top_k=3):

    return collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={
            "source": file_name
        }
    )