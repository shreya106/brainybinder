import os

from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")

CHUNK_SIZE = 500
OVERLAP_SENTENCES = 1

DATA_FOLDER = "data"

VECTOR_DB_PATH = "vector_store"

COLLECTION_NAME = "brainybinder"