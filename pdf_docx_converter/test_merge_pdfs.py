from io import BytesIO

import fitz
from fastapi.testclient import TestClient

from pdf_docx_converter.config import app


client = TestClient(app)


def pdf_bytes(page_count: int = 1) -> bytes:
    document = fitz.open()
    for _ in range(page_count):
        document.new_page()
    content = document.tobytes()
    document.close()
    return content


def upload(name: str, content: bytes):
    return (name, BytesIO(content), "application/pdf")


def test_merge_pdfs_returns_combined_pdf():
    response = client.post(
        "/api/convert/merge-pdfs",
        files=[
            ("files", upload("uno.pdf", pdf_bytes())),
            ("files", upload("dos.pdf", pdf_bytes(2))),
        ],
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "documentos-unidos.pdf" in response.headers["content-disposition"]
    with fitz.open(stream=response.content, filetype="pdf") as document:
        assert document.page_count == 3


def test_merge_pdfs_rejects_invalid_file_count():
    response = client.post(
        "/api/convert/merge-pdfs",
        files=[("files", upload("uno.pdf", pdf_bytes()))],
    )

    assert response.status_code == 400


def test_merge_pdfs_rejects_invalid_pdf():
    response = client.post(
        "/api/convert/merge-pdfs",
        files=[
            ("files", upload("uno.pdf", b"not a pdf")),
            ("files", upload("dos.pdf", pdf_bytes())),
        ],
    )

    assert response.status_code == 400