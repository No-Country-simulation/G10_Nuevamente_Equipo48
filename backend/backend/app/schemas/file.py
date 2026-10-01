"""
Schemas Pydantic para el endpoint de carga de documentos.

Modelos:
  - UploadResponse  → respuesta exitosa de POST /api/v1/files/upload
  - ErrorResponse   → estructura uniforme para todas las respuestas de error (4xx / 5xx)
"""

from pydantic import BaseModel


class UploadResponse(BaseModel):
    """
    Respuesta devuelta al cliente tras una carga de documento exitosa.

    Campos:
        status:           Siempre "ok" cuando la operación fue exitosa.
        documento_id:     Identificador único (UUID) asignado al documento ingestado.
        filename:         Nombre original del archivo recibido.
        chunks_indexados: Número de fragmentos de texto indexados en FAISS.
        oci_status:       Estado del intento de subida a OCI Object Storage.
                          Valores posibles: "exitoso" | "no_configurado" | "error".
    """

    status: str = "ok"
    documento_id: str
    filename: str
    chunks_indexados: int
    oci_status: str  # "exitoso" | "no_configurado" | "error"


class ErrorResponse(BaseModel):
    """
    Estructura uniforme para todas las respuestas de error de la API.

    Todos los errores (4xx y 5xx) retornan este schema para facilitar el
    manejo consistente en el cliente.

    Campos:
        error:   Descripción breve del error en español, adecuada para mostrar al usuario.
        detalle: Información adicional para diagnóstico: campos inválidos, variable de
                 entorno faltante, motivo del fallo, etc. Puede estar vacío.
    """

    error: str
    detalle: str
