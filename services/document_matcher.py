import re

from services.vector_store import list_documents

SUMMARY_PATTERNS = [
    r"\bsummari[sz]e\b",
    r"\bsummary\b",
    r"\boverview\b",
    r"\bmain points\b",
    r"\bkey points\b",
    r"\bwhat is .+ about\b",
    r"\bexplain the (document|file|pdf|notes)\b",
    r"\bdescribe the (document|file|pdf|notes)\b",
]


def normalize(text):

    text = text.lower()
    text = text.replace(".pdf", "")
    text = re.sub(r"[_\-]+", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def detect_document(question):
    """
    Returns the uploaded file the question names, or None.
    Longer names are checked first so "java advanced.pdf" wins over "java.pdf".
    """

    normalized_question = normalize(question)

    documents = sorted(list_documents(), key=len, reverse=True)

    for document in documents:

        if normalize(document) in normalized_question:
            return document

    return None


def is_summary_request(question):

    question = question.lower()

    return any(re.search(pattern, question) for pattern in SUMMARY_PATTERNS)
