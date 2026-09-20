# OpenDoc PDF/DOCX converter

Backend FastAPI para conversiones síncronas entre PDF y DOCX. La aplicación
web estática se despliega por separado.

## Ejecución local

Desde la raíz de este repositorio:

```powershell
python -m pdf_docx_converter.run
```

Después abre `http://127.0.0.1:8000`.

## Docker

Construye la imagen desde la raíz de este repositorio:

```powershell
docker build -t opendoc-back:local .
docker run --rm -p 8000:8000 opendoc-back:local
```

Comprueba el servicio en `http://127.0.0.1:8000/api/convert/health`.

Las variables disponibles están en `env.example`. La imagen incluye
LibreOffice para DOCX a PDF y Tesseract para OCR de PDFs escaneados.

## Pruebas

```powershell
python -m pytest pdf_docx_converter/test_validators.py
```
