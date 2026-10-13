import logging

from config import DATA_FOLDER
from services.document_service import index_directory

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")

total = index_directory(DATA_FOLDER)

print(f"Done. Stored {total} chunks.")
