FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000 \
    MAX_FILE_SIZE_MB=25 \
    CONVERSION_TIMEOUT_SECONDS=120 \
    OCR_ENABLED=true \
    OCR_LANGUAGE=spa+eng

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libreoffice \
        libreoffice-writer \
        tesseract-ocr \
        tesseract-ocr-spa \
        tesseract-ocr-eng \
        fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY pdf_docx_converter ./pdf_docx_converter

RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/convert/health')"

CMD ["python", "-m", "pdf_docx_converter.run"]
