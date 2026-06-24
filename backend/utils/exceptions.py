"""Shared custom exceptions for the processing pipeline."""


class ProcessingError(Exception):
    """Base class for all pipeline processing errors."""
    pass


class InvalidYouTubeURLError(ProcessingError):
    pass


class VideoTooLongError(ProcessingError):
    def __init__(self, duration_seconds: int, max_seconds: int):
        self.duration_seconds = duration_seconds
        self.max_seconds = max_seconds
        super().__init__(
            f"Video duration {duration_seconds}s exceeds max allowed {max_seconds}s"
        )


class AudioExtractionError(ProcessingError):
    pass


class PDFTooLargeError(ProcessingError):
    pass


class PDFExtractionError(ProcessingError):
    pass


class EmptyContentError(ProcessingError):
    pass