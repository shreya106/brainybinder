from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def generate_embedding(text):
    return model.encode(text).tolist()


def generate_embeddings(chunks):

    embeddings = []

    for chunk in chunks:
        embeddings.append(generate_embedding(chunk))

    return embeddings