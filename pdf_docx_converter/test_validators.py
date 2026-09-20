from pathlib import Path
from zipfile import ZipFile

from pdf_docx_converter.validators import validate_docx, validate_pdf


def test_validate_pdf(tmp_path: Path):
    path = tmp_path / "document.pdf"
    path.write_bytes(b"%PDF-1.7\n")
    validate_pdf(path)


def test_validate_docx(tmp_path: Path):
    path = tmp_path / "document.docx"
    with ZipFile(path, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types/>")
        archive.writestr("word/document.xml", "<document/>")
    validate_docx(path)
