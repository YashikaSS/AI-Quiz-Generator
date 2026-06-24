"""
summary_service.py
---------------------
OWNER: Member 4

WHAT THIS FILE DOES:
Takes a block of text (a transcript or extracted PDF text) and produces
a short, readable PARAGRAPH summary - the kind a student could read in
30 seconds to understand what the whole video/document was about.

HOW IT WORKS:
We try TWO strategies, in this order:

  1. LLM SUMMARY (preferred): We send the text to the shared LLM
     (via llm_service.generate_text) with an instruction like
     "summarize this in simple language." This produces natural,
     well-written summaries - similar to how a person would explain it.

  2. EXTRACTIVE FALLBACK: If the LLM is not available (not loaded yet,
     errors out, or USE_REAL_LLM is off), we fall back to LexRank
     (the same method used in notes_service.py) to pick a few important
     sentences and join them into a rough paragraph instead. It's not as
     smooth as an LLM summary, but it means this function ALWAYS returns
     something useful, and never crashes the whole pipeline.

WHY THIS MATTERS FOR YOUR TEAM:
Member 5 (quiz_service.py) likely needs a summary to generate quiz
questions from. If your function can throw an exception when the LLM
isn't ready, it could block their testing too. The fallback means your
function is dependable from day one.
"""

from backend.services.llm_service import generate_text
from backend.services.notes_service import generate_notes


def generate_summary(text: str, max_sentences_fallback: int = 4) -> str:
    """
    Produces a short paragraph summary of `text`.

    Args:
        text: The full transcript or extracted PDF text.
        max_sentences_fallback: How many sentences to use if we have to
            fall back to the extractive method (LLM not available).

    Returns:
        A single string containing the summary paragraph.
    """
    if not text or not text.strip():
        return ""

    try:
        return _generate_llm_summary(text)
    except Exception as error:
        # If ANYTHING goes wrong with the LLM (not loaded, out of memory,
        # network error if using an API model, etc.), we don't want the
        # whole app to crash. We log the problem and fall back instead.
        print(f"[summary_service] LLM summary failed, using fallback. Reason: {error}")
        return _generate_extractive_summary(text, max_sentences_fallback)


def _generate_llm_summary(text: str) -> str:
    """
    Strategy 1: Ask the LLM to write a summary in its own words.

    We build a clear, simple prompt. Being specific about format and
    length helps the model give consistent results instead of rambling.
    """
    prompt = (
        "Summarize the following text in 4-6 sentences, in simple, clear "
        "language suitable for a student studying this topic for an exam. "
        "Only include facts that are explicitly stated in the text below. "
        "Do not add information that isn't there.\n\n"
        f"TEXT:\n{text}\n\n"
        "SUMMARY:"
    )

    summary = generate_text(prompt, max_new_tokens=300)
    return summary.strip()


def _generate_extractive_summary(text: str, num_sentences: int) -> str:
    """
    Strategy 2 (fallback): Reuse the LexRank logic from notes_service.py
    to pick a few important sentences, then join them into one paragraph.

    This is intentionally simple - it reuses generate_notes() instead of
    duplicating the LexRank code, so there's only one place that logic
    lives (easier to maintain).
    """
    key_sentences = generate_notes(text, num_points=num_sentences)
    return " ".join(key_sentences)


# -----------------------------------------------------------------------
# QUICK MANUAL TEST
# Run this file directly (python summary_service.py) to see it work.
# Since USE_REAL_LLM defaults to "false", this will currently show the
# FALLBACK summary - that's expected and fine at this stage. Once a real
# model is wired up (USE_REAL_LLM=true), this same code will automatically
# start producing real LLM summaries instead, with no changes needed here.
# -----------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    import os

    # Allow running this file directly without installing the project
    # as a package - adds the backend/ parent folder to Python's search path.
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from backend.services.summary_service import generate_summary  # noqa: E402

    sample_path = os.path.join(
        os.path.dirname(__file__), "../../storage/transcripts/sample_transcript.txt"
    )
    with open(sample_path, "r", encoding="utf-8") as f:
        sample_text = f.read()

    print("=== SUMMARY ===\n")
    print(generate_summary(sample_text))
