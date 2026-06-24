"""
test_summary_and_notes.py
---------------------------
Basic tests for Member 4's modules: summary_service.py and notes_service.py

HOW TO RUN:
From the project root folder, run:
    python -m pytest backend/tests/test_summary_and_notes.py -v

(Install pytest first if you don't have it: pip install pytest)
"""

import os
from backend.services.notes_service import generate_notes
from backend.services.summary_service import generate_summary

SAMPLE_PATH = os.path.join(
    os.path.dirname(__file__), "../../storage/transcripts/sample_transcript.txt"
)


def load_sample_text():
    with open(SAMPLE_PATH, "r", encoding="utf-8") as f:
        return f.read()


def test_generate_notes_returns_list():
    text = load_sample_text()
    notes = generate_notes(text, num_points=5)
    assert isinstance(notes, list)
    assert len(notes) == 5
    for point in notes:
        assert isinstance(point, str)
        assert len(point) > 0


def test_generate_notes_handles_empty_text():
    notes = generate_notes("", num_points=5)
    assert notes == []


def test_generate_summary_returns_nonempty_string():
    text = load_sample_text()
    summary = generate_summary(text)
    assert isinstance(summary, str)
    assert len(summary) > 0


def test_generate_summary_handles_empty_text():
    summary = generate_summary("")
    assert summary == ""