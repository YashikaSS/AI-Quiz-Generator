import re


def clean_transcript(text: str) -> str:
    """
    Basic transcript cleanup.
    """

    text = re.sub(r"\s+", " ", text)

    fillers = [
        r"\bum\b",
        r"\buh\b",
        r"\ber\b",
        r"\bah\b",
    ]

    for filler in fillers:
        text = re.sub(filler, "", text, flags=re.IGNORECASE)

    text = re.sub(r"\s+", " ", text)

    return text.strip()