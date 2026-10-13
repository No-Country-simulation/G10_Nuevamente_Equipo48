"""
Endpoint de generación de contenido educativo adaptativo — NuevaMente Backend.

Orquesta el flujo completo: RAG → LLM → evaluación pedagógica → respuesta estructurada.
"""

from fastapi import APIRouter, HTTPException, Request

from app.core.exceptions import (
    DocumentNotFoundError,
    LLMGenerationError,
    LLMNotConfiguredError,
)
from app.schemas.adaptacion import AdaptacionRequest, AdaptacionResponse
from app.services.agent_service import AgentService

router = APIRouter()


@router.post(
    "/adaptacion",
    response_model=AdaptacionResponse,
    tags=["Adaptación Educativa"],
    summary="Generar contenido educativo adaptado",
    description=(
        "Recibe un documento previamente ingestado y parámetros educativos, "
        "ejecuta el pipeline RAG + LLM, y retorna contenido pedagógico "
        "personalizado en el formato solicitado."
    ),
)
async def generar_contenido(
    adaptacion_request: AdaptacionRequest,
    request: Request,
) -> AdaptacionResponse:
    """
    Genera contenido educativo adaptativo.

    El documento debe haber sido previamente cargado mediante
    POST /api/v1/files/upload.

    Returns:
        AdaptacionResponse con el contenido generado y metadatos de evaluación.
    """
    # Obtener el agente orquestador desde el estado de la aplicación
    agent_service: AgentService = request.app.state.agent_service

    try:
        return agent_service.generate_content(adaptacion_request)

    except DocumentNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={"error": exc.message, "detalle": exc.detail},
        ) from exc

    except LLMNotConfiguredError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error": exc.message,
                "detalle": exc.detail,
            },
        ) from exc

    except LLMGenerationError as exc:
        raise HTTPException(
            status_code=502,
            detail={"error": exc.message, "detalle": exc.detail},
        ) from exc
