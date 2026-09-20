from pathlib import Path
import shutil
import subprocess

from . import settings
from .exceptions import ConversionError


def find_libreoffice() -> str | None:
    candidates = [
        settings.libreoffice_path,
        "libreoffice",
        "soffice",
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ]
    return next((resolved for candidate in candidates if candidate and (resolved := shutil.which(candidate) or (candidate if Path(candidate).exists() else None))), None)


def libreoffice_version(executable: str) -> str | None:
    result = subprocess.run([executable, "--version"], capture_output=True, text=True, timeout=10, check=False)
    return (result.stdout or result.stderr).strip() or None


def convert_docx_to_pdf(input_docx: Path, output_pdf: Path) -> None:
    executable = find_libreoffice()
    if not executable:
        raise ConversionError("LibreOffice no está instalado o no se encontró su ejecutable.")
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    command = [executable, "--headless", "--convert-to", "pdf:writer_pdf_Export", "--outdir", str(output_pdf.parent), str(input_docx)]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=settings.conversion_timeout_seconds, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ConversionError("La conversión con LibreOffice no pudo completarse.") from exc
    generated = output_pdf.parent / f"{input_docx.stem}.pdf"
    if result.returncode != 0 or not generated.exists():
        raise ConversionError((result.stderr or result.stdout or "LibreOffice no generó el PDF.").strip())
    generated.replace(output_pdf)
