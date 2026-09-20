
import os

import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "pdf_docx_converter.config:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("RELOAD", "false").lower() in {"1", "true", "yes"},
    )
