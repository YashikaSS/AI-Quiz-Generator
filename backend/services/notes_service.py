"""
notes_service.py
------------------
OWNER: Member 4

WHAT THIS FILE DOES:
Takes a block of text (a transcript from YouTube audio, or text extracted
from a PDF) and produces a list of "key points" — the most important
sentences from that text, picked automatically.

HOW IT WORKS (in plain English):
We use an algorithm called LexRank. Think of it like this: every sentence
in the text "votes" for other sentences that are similar to it in meaning.
Sentences that get the most votes from other sentences are considered the
most "central" or important ones — similar to how Google PageRank ranks
web pages by how many other pages link to them.

This is called an "EXTRACTIVE" method because it picks REAL sentences
from the original text. It does not invent new sentences. This makes it
fast, and it never makes up facts that weren't in the original text.

WHY NOT USE THE LLM FOR THIS?
We could ask the LLM to write key points instead, but:
1. LexRank is much faster (no GPU needed, runs instantly on CPU)
2. LexRank can't "hallucinate" - every point is a real sentence that
   was actually said/written in the source material
3. Key points are meant to be quick factual highlights, not creative
   writing - extractive summarization fits that purpose well
"""

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer


def generate_notes(text: str, num_points: int = 5) -> list[str]:
    """
    Extracts the most important sentences from `text` as key points.

    Args:
        text: The full transcript or extracted PDF text.
        num_points: How many key points to return. Default is 5.

    Returns:
        A list of strings, where each string is one key point/important
        sentence, e.g.:
        [
            "Photosynthesis converts light energy into chemical energy.",
            "RuBisCO is the key enzyme in the Calvin cycle.",
            ...
        ]
    """
    # Step 1: Basic safety check. Don't crash on empty input - return
    # an empty list instead, so the calling code (routes) can handle it
    # gracefully (e.g. show "no notes available" instead of a server error).
    if not text or not text.strip():
        return []

    # Step 2: Parse the raw text into sumy's internal sentence format.
    # Tokenizer("english") tells sumy to split sentences using English
    # grammar rules (it knows "Mr. Smith" isn't two sentences, for example).
    parser = PlaintextParser.from_string(text, Tokenizer("english"))

    # Step 3: Create the LexRank summarizer object and run it.
    # parser.document contains all sentences; we ask for the top `num_points`.
    summarizer = LexRankSummarizer()
    ranked_sentences = summarizer(parser.document, num_points)

    # Step 4: Convert sumy's internal sentence objects into plain strings.
    notes = [str(sentence) for sentence in ranked_sentences]

    return notes


# -----------------------------------------------------------------------
# QUICK MANUAL TEST
# Run this file directly (python notes_service.py) to see it work,
# without needing FastAPI, a database, or anything else running.
# -----------------------------------------------------------------------
if __name__ == "__main__":
    import os

    # Build the path relative to THIS FILE's location, not relative to
    # whatever folder the terminal happens to be in. This makes the test
    # work the same way whether you run it from the project root
    # (python -m backend.services.notes_service) or from inside
    # backend/services/ directly.
    sample_path = os.path.join(
        os.path.dirname(__file__), "../../storage/transcripts/sample_transcript.txt"
    )
    try:
        with open(sample_path, "r", encoding="utf-8") as f:
            sample_text = f.read()
    except FileNotFoundError:
        print(f"Could not find {sample_path}.")
        exit()

    print("=== KEY POINTS / NOTES ===\n")
    notes = generate_notes(sample_text, num_points=5)
    for i, point in enumerate(notes, 1):
        print(f"{i}. {point}\n")
