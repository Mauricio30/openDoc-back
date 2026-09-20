from pathlib import Path

from .libreoffice import convert_docx_to_pdf
from .pdf_to_docx import convert_pdf_to_docx


def convert_pdf_to_docx_file(input_path: Path, output_path: Path) -> dict:
    return convert_pdf_to_docx(input_path, output_path)


def convert_docx_to_pdf_file(input_path: Path, output_path: Path) -> None:
    convert_docx_to_pdf(input_path, output_path)
