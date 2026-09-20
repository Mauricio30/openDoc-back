from pathlib import Path
import shutil

import fitz
from docx import Document
from pdf2docx import Converter

from . import settings
from .exceptions import ConversionError
from .pdf_analyzer import analyze_pdf


def convert_with_pdf2docx(input_pdf: Path, output_docx: Path) -> None:
    try:
        converter = Converter(str(input_pdf))
        try:
            converter.convert(str(output_docx))
        finally:
            converter.close()
    except Exception as exc:
        raise ConversionError(f"No fue posible convertir el PDF: {exc}") from exc


def convert_scanned_pdf_with_ocr(input_pdf: Path, output_docx: Path) -> None:
    if not settings.ocr_enabled:
        raise ConversionError("El OCR está desactivado en el servidor.")

    try:
        import pytesseract
        from PIL import Image
    except ImportError as exc:
        raise ConversionError("Instala pytesseract, Pillow y Tesseract OCR para PDFs escaneados.") from exc

    tesseract = shutil.which("tesseract") or r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if not Path(tesseract).exists():
        raise ConversionError("Tesseract OCR no está instalado o no se encontró su ejecutable.")
    pytesseract.pytesseract.tesseract_cmd = tesseract
    languages = pytesseract.get_languages(config="")
    language = settings.ocr_language if all(item in languages for item in settings.ocr_language.split("+")) else "eng"

    document = Document()
    try:
        with fitz.open(input_pdf) as pdf:
            for page_index, page in enumerate(pdf):
                if page_index:
                    document.add_page_break()
                pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
                text = pytesseract.image_to_string(image, lang=language).strip()
                for paragraph in text.splitlines():
                    if paragraph.strip():
                        document.add_paragraph(paragraph.strip())
        document.save(output_docx)
    except Exception as exc:
        raise ConversionError(f"No fue posible ejecutar OCR sobre el PDF: {exc}") from exc


def convert_pdf_to_docx(input_pdf: Path, output_docx: Path) -> dict:
    analysis = analyze_pdf(input_pdf, settings.scanned_text_threshold)
    if analysis["is_scanned"]:
        convert_scanned_pdf_with_ocr(input_pdf, output_docx)
        engine = "ocr"
    else:
        convert_with_pdf2docx(input_pdf, output_docx)
        engine = "pdf2docx"

    if not output_docx.exists() or output_docx.stat().st_size == 0:
        raise ConversionError("El motor no generó un DOCX válido.")
    return {**analysis, "engine": engine}
