from services.vector_store import list_documents


def normalize(text):

    text = text.lower()

    text = text.replace(".pdf", "")

    text = text.replace("_", " ")

    text = text.replace("-", " ")

    return text.strip()


def detect_document(question):

    question = normalize(question)

    documents = list_documents()

    for document in documents:

        normalized_document = normalize(document)

        if normalized_document in question:

            return document

    return None