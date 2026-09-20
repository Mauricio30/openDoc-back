class ConversionError(Exception):
    pass


class ValidationError(Exception):
    pass
from pathlib import Path
from zipfile import ZipFile, BadZipFile
from .exceptions import ValidationError

PDF_MAGIC = b"%PDF-"

def validate_pdf(path: Path) -> None:
    with path.open("rb") as f:
        if f.read(5) != PDF_MAGIC:
            raise ValidationError("El archivo no parece ser un PDF válido.")

def validate_docx(path: Path) -> None:
    # DOCX is an OOXML ZIP package. Check both container and required entries.
    try:
        with ZipFile(path) as z:
            names = set(z.namelist())
            if "[Content_Types].xml" not in names or "word/document.xml" not in names:
                raise ValidationError("El archivo no parece ser un DOCX válido.")
    except BadZipFile as exc:
        raise ValidationError("El archivo DOCX está dañado o no es válido.") from exc

def validate_extension(filename: str, expected: str) -> None:
    if Path(filename).suffix.lower() != expected:
        raise ValidationError(f"Se esperaba un archivo {expected}.")
