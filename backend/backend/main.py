"""
Punto de entrada de uvicorn para NuevaMente Backend.

Uso:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

O directamente:
    python main.py
"""

import uvicorn

from app.main import app  # noqa: F401 — reexportado para uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
