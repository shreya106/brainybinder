import os

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------- LLM
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")

# Optional second model, tried when the main one is overloaded (503)
# or rate-limited (429). Leave empty to disable.
GEMINI_FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL")

# Set to 0 to turn off "thinking" on Gemini Flash models (much faster
# for Q&A). Leave unset for Pro models, which cannot turn it off.
_thinking = os.getenv("GEMINI_THINKING_BUDGET")
GEMINI_THINKING_BUDGET = int(_thinking) if _thinking not in (None, "") else None

# Fail fast instead of silently retrying for minutes.
LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
SUMMARY_TIMEOUT_SECONDS = int(os.getenv("SUMMARY_TIMEOUT_SECONDS", "120"))
LLM_MAX_ATTEMPTS = int(os.getenv("LLM_MAX_ATTEMPTS", "2"))  # includes the first try

# true  -> answer from notes first, then may add a clearly labeled
#          "Beyond your notes:" section with general explanation
# false -> strictly notes only
ALLOW_GENERAL_KNOWLEDGE = os.getenv("ALLOW_GENERAL_KNOWLEDGE", "true").lower() == "true"

# ---------------------------------------------------------------- Chunking
# all-MiniLM-L6-v2 ignores text past ~256 tokens (~1,000 characters),
# so chunks stay a little under that.
CHUNK_SIZE = 900      # characters
CHUNK_OVERLAP = 150   # characters carried into the next chunk

# ---------------------------------------------------------------- Retrieval
TOP_K = 5
# Cosine distance: 0 = same meaning, 1 = unrelated.
# Chunks further away than this are dropped. Tune by watching the
# distances printed in the server log for good and bad matches.
MAX_DISTANCE = 0.65
HISTORY_TURNS = 3     # previous question/answer pairs used for follow-ups

# ---------------------------------------------------------------- Storage
DATA_FOLDER = "data"
VECTOR_DB_PATH = "vector_store"
# New name: the collection now uses cosine distance and page metadata,
# so documents must be re-ingested once (python ingest.py).
COLLECTION_NAME = "brainybinder_v2"
SUMMARY_FOLDER = "summaries"
