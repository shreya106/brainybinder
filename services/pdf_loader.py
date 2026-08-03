from pypdf import PdfReader
from services.text_cleaner import clean_text


def extract_text(pdf_path):
    reader = PdfReader(pdf_path)

    text = ""

    for page in reader.pages:
        extracted_text = page.extract_text()

        if extracted_text:
            text += extracted_text

    return clean_text(text)