import logging
import os
import shutil
import time
from collections import deque
from typing import List, Optional

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import DATA_FOLDER, HISTORY_TURNS, TOP_K
from services.document_matcher import detect_document, is_summary_request
from services.document_service import index_document
from services.llm import LLMUnavailable, generate_answer
from services.retriever import retrieve
from services.summarizer import delete_summary, get_summary, precompute_summary
from services.vector_store import delete_document, get_document_chunks, list_documents

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s  %(message)s")
logger = logging.getLogger("brainybinder")

os.makedirs(DATA_FOLDER, exist_ok=True)

app = FastAPI(title="BrainyBinder")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BUSY_MESSAGE = (
    "The AI model is busy right now. Please try again in a minute."
)

# Personal single-user app: the last few exchanges are kept in memory so
# follow-ups like "explain that more simply" work without frontend changes.
# A client can also send its own history, which takes priority.
recent_history = deque(maxlen=HISTORY_TURNS)


class Turn(BaseModel):
    question: str
    answer: str


class QueryRequest(BaseModel):
    question: str
    history: Optional[List[Turn]] = None


def _retrieve_with_history(question, history, file_name):
    """
    A follow-up such as "explain that more simply" has nothing to search
    for on its own, so we also search with the previous question attached
    and keep the best matches from both searches.
    """

    matches = retrieve(question, top_k=TOP_K, file_name=file_name)

    if history:
        combined_query = f"{history[-1]['question']} {question}"
        matches += retrieve(combined_query, top_k=TOP_K, file_name=file_name)

    best = {}

    for match in matches:
        key = (match["source"], match["chunk"])
        if key not in best or match["distance"] < best[key]["distance"]:
            best[key] = match

    return sorted(best.values(), key=lambda match: match["distance"])[:TOP_K]


@app.post("/query")
def query(request: QueryRequest):

    started = time.perf_counter()

    question = request.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Please type a question.")

    if request.history is not None:
        history = [turn.model_dump() for turn in request.history][-HISTORY_TURNS:]
    else:
        history = list(recent_history)

    document = detect_document(question)

    try:

        # ---------------- Summary of a named document: uses EVERY chunk
        if document and is_summary_request(question):

            summary = get_summary(document)

            if summary is None:
                raise HTTPException(status_code=404, detail=f"{document} has no stored text.")

            chunk_count = len(get_document_chunks(document))

            logger.info("Summary of %s served in %.1fs", document, time.perf_counter() - started)

            recent_history.append({"question": question, "answer": summary})

            return {
                "answer": summary,
                "mode": "summary",
                "sources": [{
                    "source": document,
                    "chunk": "all",
                    "page": None,
                    "distance": 0,
                    "preview": f"Summary built from all {chunk_count} sections of {document}."
                }]
            }

        # ---------------- Question: search notes, then answer
        matches = _retrieve_with_history(question, history, document)

        retrieval_seconds = time.perf_counter() - started

        logger.info(
            "Retrieved %d chunk(s) in %.2fs: %s",
            len(matches),
            retrieval_seconds,
            [(m["source"], m["chunk"], m["distance"]) for m in matches]
        )

        answer = generate_answer(question, matches, history)

    except LLMUnavailable as error:
        logger.error("LLM unavailable: %s", error)
        raise HTTPException(status_code=503, detail=BUSY_MESSAGE)

    except HTTPException:
        raise

    except Exception:
        # Any unexpected error still returns a normal JSON response, so the
        # browser shows a message instead of "Failed to fetch".
        logger.exception("Query failed")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while answering. Check the server log."
        )

    logger.info(
        "Answered in %.1fs total (retrieval %.2fs)",
        time.perf_counter() - started,
        retrieval_seconds
    )

    recent_history.append({"question": question, "answer": answer})

    return {
        "answer": answer,
        "mode": "question",
        "sources": [
            {
                "source": match["source"],
                "chunk": match["chunk"],
                "page": match["page"],
                "distance": match["distance"],
                "preview": match["text"][:250]
            }
            for match in matches
        ]
    }


@app.post("/conversation/reset")
def reset_conversation():

    recent_history.clear()

    return {"message": "Conversation cleared."}


@app.post("/upload")
def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):

    # basename() stops names like "../../etc/x.pdf" escaping the data folder
    file_name = os.path.basename(file.filename or "")

    if not file_name.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_path = os.path.join(DATA_FOLDER, file_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        chunk_count = index_document(file_path)
    except ValueError as error:
        os.remove(file_path)
        raise HTTPException(status_code=400, detail=str(error))


    return {
        "message": "Document uploaded successfully.",
        "filename": file_name,
        "chunks": chunk_count
    }


@app.get("/documents")
def get_documents():

    return {"documents": list_documents()}


@app.delete("/documents/{filename}")
def remove_document(filename: str):

    file_name = os.path.basename(filename)

    delete_document(file_name)
    delete_summary(file_name)

    file_path = os.path.join(DATA_FOLDER, file_name)

    if os.path.exists(file_path):
        os.remove(file_path)

    return {"message": f"{file_name} deleted successfully."}