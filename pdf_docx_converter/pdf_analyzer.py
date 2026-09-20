from pathlib import Path

import fitz


def analyze_pdf(path: Path, scanned_text_threshold: int = 40) -> dict:
    with fitz.open(path) as document:
        pages = len(document)
        text_chars = sum(len(page.get_text("text").strip()) for page in document)
        image_pages = sum(bool(page.get_images(full=True)) for page in document)

    chars_per_page = text_chars / pages if pages else 0
    return {
        "pages": pages,
        "text_chars": text_chars,
        "image_pages": image_pages,
        "chars_per_page": round(chars_per_page, 2),
        "is_scanned": pages > 0 and chars_per_page < scanned_text_threshold,
    }
