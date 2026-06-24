import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR = os.path.join(BASE_DIR, "..", "storage")
UPLOADS_DIR = os.path.join(STORAGE_DIR, "uploads")

TRANSCRIPTS_DIR = os.path.join(STORAGE_DIR, "transcripts")
os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)

os.makedirs(UPLOADS_DIR, exist_ok=True)

MAX_VIDEO_DURATION_SECONDS = 30 * 60  # 30 minutes
MAX_PDF_SIZE_MB = 20
MAX_EXTRACTED_TEXT_CHARS = 50_000

WHISPER_MODEL = "base"