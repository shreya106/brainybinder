import re


def clean_text(text):

    # Re-join words that the PDF split across lines with a hyphen:
    # "pro-\ncessed" -> "processed"
    text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)

    # Replace all remaining whitespace (tabs, newlines, multiple spaces)
    # with a single space
    text = re.sub(r"\s+", " ", text)

    return text.strip()
