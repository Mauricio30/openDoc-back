from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Annotated
import mimetypes
import os

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from . import settings
from .exceptions import ConversionError, ValidationError
from .validators import (
    validate_pdf,
    validate_pdf_document,
    validate_docx,
    validate_extension,
)
from .conversion_service import (
    convert_pdf_to_docx_file,
    convert_docx_to_pdf_file,
    merge_pdf_files,
)
from .libreoffice import find_libreoffice, libreoffice_version

app = FastAPI(
    title="PDF DOCX Converter",
    version="1.0.0",
    description="Conversor PDF ↔ DOCX integrado para una aplicación existente.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

MAX_BYTES = settings.max_file_size_mb * 1024 * 1024

def safe_name(filename: str | None, default: str) -> str:
    name = Path(filename or default).name
    # Keep only the final filename component; prevent traversal.
    if not name or name in {".", ".."}:
        return default
    return name

async def save_upload(upload: UploadFile, destination: Path) -> None:
    size = 0
    with destination.open("wb") as out:
        while True:
            chunk = await upload.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > MAX_BYTES:
                raise ValidationError(
                    f"El archivo supera el tamaño máximo de {settings.max_file_size_mb} MB."
                )
            out.write(chunk)

@app.get("/api/convert/health")
def health():
    executable = find_libreoffice()
    return {
        "status": "ok" if executable else "degraded",
        "libreoffice": bool(executable),
        "libreoffice_path": executable,
        "libreoffice_version": libreoffice_version(executable) if executable else None,
        "ocr_enabled": settings.ocr_enabled,
        "max_file_size_mb": settings.max_file_size_mb,
    }


@app.post("/api/convert/pdf-to-docx")
async def pdf_to_docx(file: Annotated[UploadFile, File(...)]):
    filename = safe_name(file.filename, "document.pdf")
    try:
        validate_extension(filename, ".pdf")
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    tmp = TemporaryDirectory(prefix="pdfdocx_")
    tmp_dir = Path(tmp.name)
    input_path = tmp_dir / filename
    output_path = tmp_dir / f"{Path(filename).stem}.docx"

    try:
        await save_upload(file, input_path)
        validate_pdf(input_path)
        analysis = convert_pdf_to_docx_file(input_path, output_path)
    except ValidationError as exc:
        tmp.cleanup()
        raise HTTPException(status_code=400, detail=str(exc))
    except ConversionError as exc:
        tmp.cleanup()
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception:
        tmp.cleanup()
        raise HTTPException(
            status_code=500,
            detail="Ocurrió un error inesperado durante la conversión.",
        )

    return FileResponse(
        path=output_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=output_path.name,
        headers={
            "X-Conversion-Engine": analysis["engine"],
            "X-PDF-Scanned": str(analysis["is_scanned"]).lower(),
        },
        background=BackgroundTask(tmp.cleanup),
    )


@app.post("/api/convert/docx-to-pdf")
async def docx_to_pdf(file: Annotated[UploadFile, File(...)]):
    filename = safe_name(file.filename, "document.docx")
    try:
        validate_extension(filename, ".docx")
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    tmp = TemporaryDirectory(prefix="docxpdf_")
    tmp_dir = Path(tmp.name)
    input_path = tmp_dir / filename
    output_path = tmp_dir / f"{Path(filename).stem}.pdf"

    try:
        await save_upload(file, input_path)
        validate_docx(input_path)
        convert_docx_to_pdf_file(input_path, output_path)
    except ValidationError as exc:
        tmp.cleanup()
        raise HTTPException(status_code=400, detail=str(exc))
    except ConversionError as exc:
        tmp.cleanup()
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception:
        tmp.cleanup()
        raise HTTPException(
            status_code=500,
            detail="Ocurrió un error inesperado durante la conversión.",
        )

    return FileResponse(
        path=output_path,
        media_type="application/pdf",
        filename=output_path.name,
        background=BackgroundTask(tmp.cleanup),
    )


@app.post("/api/convert/merge-pdfs")
async def merge_pdfs(
    files: Annotated[list[UploadFile] | None, File()] = None,
):
    files = files or []
    if not 2 <= len(files) <= 20:
        raise HTTPException(
            status_code=400,
            detail="Se requieren entre 2 y 20 archivos PDF.",
        )

    tmp = TemporaryDirectory(prefix="pdfmerge_")
    tmp_dir = Path(tmp.name)
    input_paths: list[Path] = []
    output_path = tmp_dir / "documentos-unidos.pdf"

    try:
        for index, file in enumerate(files):
            filename = safe_name(file.filename, f"documento-{index + 1}.pdf")
            validate_extension(filename, ".pdf")
            input_path = tmp_dir / f"{index}-{filename}"
            await save_upload(file, input_path)
            validate_pdf_document(input_path)
            input_paths.append(input_path)

        merge_pdf_files(input_paths, output_path)
    except ValidationError as exc:
        tmp.cleanup()
        raise HTTPException(status_code=400, detail=str(exc))
    except ConversionError as exc:
        tmp.cleanup()
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception:
        tmp.cleanup()
        raise HTTPException(
            status_code=500,
            detail="Ocurrió un error inesperado durante la unión de los archivos.",
        )

    return FileResponse(
        path=output_path,
        media_type="application/pdf",
        filename=output_path.name,
        background=BackgroundTask(tmp.cleanup),
    )

