import os
import logging

from faster_whisper import WhisperModel

from backend.config import (
    WHISPER_MODEL,
    TRANSCRIPTS_DIR
)

from backend.utils.text_cleaning import clean_transcript


logger = logging.getLogger(__name__)


model = WhisperModel(
    WHISPER_MODEL,
    device="cpu",
    compute_type="int8"
)


def transcribe_audio(audio_path: str) -> dict:
    """
    Convert mp3 audio to text using Faster-Whisper.
    """

    if not os.path.exists(audio_path):
        raise FileNotFoundError(
            f"Audio file not found: {audio_path}"
        )

    logger.info(f"Starting transcription: {audio_path}")

    segments, info = model.transcribe(
        audio_path,
        beam_size=5
    )

    transcript = ""

    for segment in segments:
        transcript += segment.text + " "

    transcript = clean_transcript(transcript)

    audio_name = os.path.splitext(
        os.path.basename(audio_path)
    )[0]

    transcript_file = os.path.join(
        TRANSCRIPTS_DIR,
        f"{audio_name}.txt"
    )

    with open(
        transcript_file,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(transcript)

    logger.info(f"Transcript saved: {transcript_file}")

    return {
        "language": info.language,
        "duration": getattr(info, "duration", None),
        "transcript_path": transcript_file,
        "text": transcript,
        "char_count": len(transcript),
    }


if __name__ == "__main__":
    audio_path = input("Enter audio path: ").strip()

    try:
        result = transcribe_audio(audio_path)

        print("\n=== TRANSCRIPTION SUCCESS ===")
        print("Language:", result["language"])
        print("Characters:", result["char_count"])
        print("Transcript File:", result["transcript_path"])

        print("\nPreview:")
        print(result["text"][:1000])

    except Exception as e:
        print(f"\nError ({type(e).__name__}): {e}")