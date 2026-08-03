import os
import shutil
from fastapi.middleware.cors import CORSMiddleware
from services.document_matcher import detect_document

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from services.retriever import retrieve
from services.llm import generate_answer
from services.document_service import index_document
from services.vector_store import delete_document, list_documents
from config import DATA_FOLDER



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = DATA_FOLDER


class QueryRequest(BaseModel):
    question: str


@app.post("/query")
def query(request: QueryRequest):

    
    question = request.question.lower()

    top_k = 3

    SUMMARY_KEYWORDS = [
        "summarize",
        "summary",
        "overview",
        "main points",
        "explain the document",
        "describe the document"
    ]

    document = detect_document(request.question)

    if any(keyword in question for keyword in SUMMARY_KEYWORDS):

        top_k = 20

    results = retrieve(
    request.question,
    top_k=top_k,
    file_name=document
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    context = "\n\n".join(documents)
    print("=" * 80)
    print("Retrieved Context:")
    print(context)
    print("=" * 80)

    answer = generate_answer(
        request.question,
        context
    )

    sources = []

    for doc, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        sources.append(
            {
                "source": metadata["source"],
                "chunk": metadata["chunk"],
                "distance": round(distance, 4),
                "preview": doc[:250]
            }
        )

    return {
        "answer": answer,
        "sources": sources
    }


@app.post("/upload")
def upload_document(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    file_path = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    chunk_count = index_document(file_path)

    return {
        "message": "Document uploaded successfully.",
        "filename": file.filename,
        "chunks": chunk_count
    }


@app.get("/documents")
def get_documents():

    return {
        "documents": list_documents()
    }


@app.delete("/documents/{filename}")
def remove_document(filename: str):

    delete_document(filename)

    return {
        "message": f"{filename} deleted successfully."
    }