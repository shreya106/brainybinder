import re


def clean_text(text):

    # Replace all whitespace (tabs, newlines, multiple spaces)
    # with a single space
    text = re.sub(r"\s+", " ", text)

    # Remove leading/trailing spaces
    text = text.strip()

    return text