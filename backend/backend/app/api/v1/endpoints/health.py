"""
Endpoint de verificación de estado del servicio NuevaMente Backend.
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["Estado"])
async def health_check():
    """
    Verifica que el servicio está disponible y respondiendo.

    Retorna status=ok cuando el servicio está operativo.
    """
    return {"status": "ok", "service": "nuevamente-backend"}
