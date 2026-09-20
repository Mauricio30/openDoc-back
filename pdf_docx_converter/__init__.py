import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "25"))
    conversion_timeout_seconds: int = int(os.getenv("CONVERSION_TIMEOUT_SECONDS", "120"))
    libreoffice_path: str = os.getenv("LIBREOFFICE_PATH", "")
    ocr_enabled: bool = os.getenv("OCR_ENABLED", "true").lower() in {"1", "true", "yes"}
    ocr_language: str = os.getenv("OCR_LANGUAGE", "spa+eng")
    scanned_text_threshold: int = int(os.getenv("SCANNED_TEXT_THRESHOLD", "40"))

settings = Settings()
