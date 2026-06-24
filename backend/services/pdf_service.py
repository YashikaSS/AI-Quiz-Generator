import os
import logging

import fitz  # PyMuPDF

from backend.config import MAX_PDF_SIZE_MB, MAX_EXTRACTED_TEXT_CHARS
from backend.utils.exceptions import (
    PDFTooLargeError,
    PDFExtractionError,
    EmptyContentError,
)

logger = logging.getLogger(__name__)


def validate_pdf_file(file_path: str) -> None:
    """Checks file exists, has a .pdf extension, and isn't oversized."""
    if not os.path.exists(file_path):
        raise PDFExtractionError(f"File not found: {file_path}")

    if not file_path.lower().endswith(".pdf"):
        raise PDFExtractionError(f"File is not a PDF: {file_path}")

    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if size_mb > MAX_PDF_SIZE_MB:
        raise PDFTooLargeError(
            f"PDF is {size_mb:.1f}MB, exceeds limit of {MAX_PDF_SIZE_MB}MB"
        )


def clean_text(raw_text: str) -> str:
    """Collapses repeated blank lines, strips trailing whitespace, removes form-feeds."""
    raw_text = raw_text.replace("\x0c", "\n")
    lines = [line.strip() for line in raw_text.splitlines()]

    cleaned_lines = []
    blank_streak = 0
    for line in lines:
        if line == "":
            blank_streak += 1
            if blank_streak > 1:
                continue
        else:
            blank_streak = 0
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def extract_text_from_pdf(file_path: str) -> dict:
    """Opens the PDF with PyMuPDF and extracts text from every page."""
    try:
        doc = fitz.open(file_path)
    except Exception as e:
        raise PDFExtractionError(f"Could not open PDF: {e}") from e

    page_texts = []
    try:
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_texts.append(page.get_text())
    except Exception as e:
        raise PDFExtractionError(f"Failed while extracting text: {e}") from e
    finally:
        doc.close()

    raw_text = "\n".join(page_texts)

    return {
        "page_count": len(page_texts),
        "raw_text": raw_text,
        "page_texts": page_texts,
    }


def process_pdf_file(file_path: str) -> dict:
    """
    Main entry point Member 6 calls.

    Steps: validate -> extract text -> clean -> truncate if too long.
    Raises: PDFTooLargeError, PDFExtractionError, EmptyContentError
    """
    validate_pdf_file(file_path)

    extraction = extract_text_from_pdf(file_path)
    cleaned = clean_text(extraction["raw_text"])

    if not cleaned or len(cleaned) < 20:
        raise EmptyContentError(
            "No usable text found in PDF (it may be scanned/image-only — "
            "OCR is not currently supported in this pipeline)"
        )

    truncated = False
    if len(cleaned) > MAX_EXTRACTED_TEXT_CHARS:
        cleaned = cleaned[:MAX_EXTRACTED_TEXT_CHARS]
        truncated = True
        logger.warning(f"PDF text truncated to {MAX_EXTRACTED_TEXT_CHARS} chars")

    filename = os.path.basename(file_path)
    logger.info(f"Extracted {len(cleaned)} chars from {filename} "
                f"({extraction['page_count']} pages)")

    return {
        "filename": filename,
        "page_count": extraction["page_count"],
        "text": cleaned,
        "char_count": len(cleaned),
        "truncated": truncated,
    }


if __name__ == "__main__":
    test_path = input("Enter path to a PDF file to test: ").strip()
    try:
        result = process_pdf_file(test_path)
        print(f"Success: {result['page_count']} pages, {result['char_count']} chars extracted")
        print("Preview:", result["text"][:300])
    except Exception as e:
        print(f"Error ({type(e).__name__}): {e}")