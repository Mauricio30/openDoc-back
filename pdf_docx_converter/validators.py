from pathlib import Path
from zipfile import BadZipFile, ZipFile

import fitz

from .exceptions import ValidationError

PDF_MAGIC = b"%PDF-"


def validate_pdf(path: Path) -> None:
    with path.open("rb") as file:
        if file.read(5) != PDF_MAGIC:
            raise ValidationError("El archivo no parece ser un PDF válido.")


def validate_pdf_document(path: Path) -> None:
    try:
        with fitz.open(path) as document:
            document.page_count
    except Exception as exc:
        raise ValidationError("El archivo no es un PDF válido o está dañado.") from exc


def validate_docx(path: Path) -> None:
    try:
        with ZipFile(path) as archive:
            names = set(archive.namelist())
            if "[Content_Types].xml" not in names or "word/document.xml" not in names:
                raise ValidationError("El archivo no parece ser un DOCX válido.")
    except BadZipFile as exc:
        raise ValidationError("El archivo DOCX está dañado o no es válido.") from exc


def validate_extension(filename: str, expected: str) -> None:
    if Path(filename).suffix.lower() != expected:
        raise ValidationError(f"Se esperaba un archivo {expected}.")
