import os
import re
import uuid
import logging

import yt_dlp

from backend.config import UPLOADS_DIR, MAX_VIDEO_DURATION_SECONDS
from backend.utils.exceptions import (
    InvalidYouTubeURLError,
    VideoTooLongError,
    AudioExtractionError,
)

logger = logging.getLogger(__name__)

YOUTUBE_URL_PATTERN = re.compile(
    r"(https?://)?(www\.)?(youtube\.com/(watch\?v=|shorts/)|youtu\.be/)[\w\-]+"
)


def is_valid_youtube_url(url: str) -> bool:
    """Quick regex check before we even hit the network."""
    return bool(YOUTUBE_URL_PATTERN.search(url.strip()))


def get_video_metadata(url: str) -> dict:
    """Fetch metadata only (no download) to check duration first."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except yt_dlp.utils.DownloadError as e:
        raise InvalidYouTubeURLError(f"Could not read video info: {e}") from e

    if info is None:
        raise InvalidYouTubeURLError("yt-dlp returned no info for this URL")

    return {
        "video_id": info.get("id"),
        "title": info.get("title", "Untitled"),
        "duration_seconds": int(info.get("duration") or 0),
        "uploader": info.get("uploader"),
    }


def download_audio(url: str, video_id: str) -> str:
    """Downloads ONLY the audio track and converts it to mp3."""
    output_template = os.path.join(UPLOADS_DIR, f"{video_id}.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except yt_dlp.utils.DownloadError as e:
        raise AudioExtractionError(f"Failed to download audio: {e}") from e

    expected_path = os.path.join(UPLOADS_DIR, f"{video_id}.mp3")
    if not os.path.exists(expected_path):
        raise AudioExtractionError(
            f"Download finished but expected file not found: {expected_path}"
        )

    return expected_path


def process_youtube_url(url: str) -> dict:
    """
    Main entry point Member 6 calls.

    Steps: validate URL -> check duration cap -> download audio only.
    Raises: InvalidYouTubeURLError, VideoTooLongError, AudioExtractionError
    """
    url = url.strip()

    if not is_valid_youtube_url(url):
        raise InvalidYouTubeURLError(f"'{url}' does not look like a valid YouTube URL")

    metadata = get_video_metadata(url)
    duration = metadata["duration_seconds"]

    if duration <= 0:
        raise InvalidYouTubeURLError("Could not determine video duration (possibly a live stream)")

    if duration > MAX_VIDEO_DURATION_SECONDS:
        raise VideoTooLongError(duration, MAX_VIDEO_DURATION_SECONDS)

    video_id = metadata["video_id"] or str(uuid.uuid4())
    audio_path = download_audio(url, video_id)

    logger.info(f"Audio extracted for video_id={video_id} -> {audio_path}")

    return {
        "video_id": video_id,
        "title": metadata["title"],
        "duration_seconds": duration,
        "audio_path": audio_path,
    }


if __name__ == "__main__":
    test_url = input("Enter a YouTube URL to test: ").strip()
    try:
        result = process_youtube_url(test_url)
        print("Success:", result)
    except Exception as e:
        print(f"Error ({type(e).__name__}): {e}")