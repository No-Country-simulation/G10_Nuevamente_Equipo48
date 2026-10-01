"""
Endpoint de carga e ingesta de documentos — NuevaMente Backend.

Acepta archivos PDF, Markdown y TXT.
Extrae el texto, lo indexa en FAISS mediante el RAG Service,
e intenta almacenar el original en OCI Object Storage.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, File, HTTPException, Request, UploadFile

from app.core.exceptions import ExtractionError
from app.schemas.file import UploadResponse
from app.services.document_service import DocumentService
from app.services.oci_service import OCIService
from app.services.rag_service import RAGService

router = APIRouter()

# ---------------------------------------------------------------------------
# Constantes de validación
# ---------------------------------------------------------------------------

# Límite de tamaño de archivo aceptado: 50 MB en bytes
MAX_FILE_SIZE = 50 * 1024 * 1024

# Conjunto de tipos MIME permitidos por el endpoint
MIME_TYPES_PERMITIDOS = {"application/pdf", "text/markdown", "text/plain"}


# ---------------------------------------------------------------------------
# Endpoint principal
# ---------------------------------------------------------------------------


@router.post("/upload", response_model=UploadResponse, tags=["Documentos"])
async def upload_file(
    file: UploadFile = File(..., description="Archivo PDF, Markdown o TXT"),
    request: Request = None,
):
    """
    Carga e ingesta un documento en el sistema NuevaMente.

    Flujo:
      1. Valida que se adjuntó un archivo.
      2. Normaliza y valida el tipo MIME del archivo.
      3. Lee el contenido y valida que no exceda el límite de 50 MB.
      4. Extrae el texto plano mediante el Document Service.
      5. Indexa el texto en FAISS mediante el RAG Service.
      6. Intenta almacenar el archivo original en OCI Object Storage.
      7. Retorna el resultado con el identificador del documento y los chunks indexados.

    Args:
        file:    Archivo subido por el cliente (PDF, Markdown o TXT).
        request: Objeto de solicitud FastAPI para acceder al estado de la aplicación.

    Returns:
        UploadResponse con el documento_id, nombre del archivo, número de chunks
        indexados y estado de almacenamiento OCI.

    Raises:
        HTTPException 415: Si el tipo MIME no está entre los permitidos.
        HTTPException 413: Si el archivo excede el límite de 50 MB.
        HTTPException 422: Si no se puede extraer texto del archivo.
    """
    # ------------------------------------------------------------------
    # 1. Validar que se recibió un archivo
    # ------------------------------------------------------------------
    if file is None or not file.filename:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "No se adjuntó ningún archivo.",
                "detalle": "El campo 'file' es obligatorio.",
            },
        )

    # ------------------------------------------------------------------
    # 2. Normalizar el MIME type (eliminar parámetros como "; charset=utf-8")
    # ------------------------------------------------------------------
    mime_raw = file.content_type or ""
    mime_base = mime_raw.split(";")[0].strip().lower()

    # ------------------------------------------------------------------
    # 3. Validar que el MIME type sea uno de los permitidos
    # ------------------------------------------------------------------
    if mime_base not in MIME_TYPES_PERMITIDOS:
        raise HTTPException(
            status_code=415,
            detail={
                "error": f"Tipo de archivo '{mime_base}' no soportado.",
                "detalle": (
                    f"Tipos permitidos: {', '.join(sorted(MIME_TYPES_PERMITIDOS))}. "
                    f"Tipo recibido: {mime_raw!r}."
                ),
            },
        )

    # ------------------------------------------------------------------
    # 4. Leer el contenido binario del archivo
    # ------------------------------------------------------------------
    file_bytes: bytes = await file.read()

    # ------------------------------------------------------------------
    # 5. Validar tamaño ≤ 50 MB
    # ------------------------------------------------------------------
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail={
                "error": "El archivo excede el tamaño máximo permitido de 50 MB.",
                "detalle": (
                    f"Tamaño recibido: {len(file_bytes)} bytes "
                    f"({len(file_bytes) / (1024 * 1024):.2f} MB). "
                    f"Límite: {MAX_FILE_SIZE // (1024 * 1024)} MB."
                ),
            },
        )

    # ------------------------------------------------------------------
    # 6. Obtener servicios desde el estado de la aplicación
    # ------------------------------------------------------------------
    document_service: DocumentService = request.app.state.document_service
    rag_service: RAGService = request.app.state.rag_service
    oci_service: OCIService = request.app.state.oci_service

    # ------------------------------------------------------------------
    # 7. Extraer texto plano mediante el Document Service
    # ------------------------------------------------------------------
    try:
        text: str = document_service.extract_text(file_bytes, mime_base)
    except ExtractionError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "error": exc.message,
                "detalle": exc.detail,
            },
        ) from exc

    # ------------------------------------------------------------------
    # 8. Generar identificador único para el documento
    # ------------------------------------------------------------------
    documento_id: str = str(uuid.uuid4())

    # ------------------------------------------------------------------
    # 9. Indexar el texto en FAISS mediante el RAG Service
    # ------------------------------------------------------------------
    chunks_count: int = rag_service.ingest_document(text, documento_id)

    # ------------------------------------------------------------------
    # 10. Intentar almacenar el archivo original en OCI Object Storage
    # ------------------------------------------------------------------
    nombre_archivo = file.filename or "archivo"
    oci_result = oci_service.upload_document(file_bytes, documento_id, nombre_archivo)

    # ------------------------------------------------------------------
    # 11. Retornar respuesta exitosa
    # ------------------------------------------------------------------
    return UploadResponse(
        status="ok",
        documento_id=documento_id,
        filename=nombre_archivo,
        chunks_indexados=chunks_count,
        oci_status=oci_result.status,
    )
