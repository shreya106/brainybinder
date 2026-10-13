from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"

# Loaded once when the server starts, then reused for every request.
model = SentenceTransformer(MODEL_NAME)


def generate_embedding(text):

    return model.encode(
        text,
        normalize_embeddings=True
    ).tolist()


def generate_embeddings(chunks):

    # One batched call instead of one call per chunk: much faster
    # for long documents.
    return model.encode(
        chunks,
        batch_size=32,
        normalize_embeddings=True,
        show_progress_bar=False
    ).tolist()
