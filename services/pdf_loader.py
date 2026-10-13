from pypdf import PdfReader

from services.text_cleaner import clean_text


def extract_pages(pdf_path):
    """
    Returns a list of (page_number, text) pairs, 1-based.
    Keeping pages separate lets every chunk remember which page it came from.
    """

    reader = PdfReader(pdf_path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):

        extracted_text = page.extract_text()

        if extracted_text:

            text = clean_text(extracted_text)

            if text:
                pages.append((page_number, text))

    return pages
