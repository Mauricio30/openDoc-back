from pathlib import Path

import fitz

from .exceptions import ConversionError
from .libreoffice import convert_docx_to_pdf
from .pdf_to_docx import convert_pdf_to_docx


def convert_pdf_to_docx_file(input_path: Path, output_path: Path) -> dict:
    return convert_pdf_to_docx(input_path, output_path)


def convert_docx_to_pdf_file(input_path: Path, output_path: Path) -> None:
    convert_docx_to_pdf(input_path, output_path)


def merge_pdf_files(input_paths: list[Path], output_path: Path) -> None:
    merged = fitz.open()
    try:
        for input_path in input_paths:
            with fitz.open(input_path) as document:
                merged.insert_pdf(document)
        merged.save(output_path)
    except RuntimeError as exc:
        raise ConversionError("No se pudieron unir los archivos PDF.") from exc
    finally:
        merged.close()
