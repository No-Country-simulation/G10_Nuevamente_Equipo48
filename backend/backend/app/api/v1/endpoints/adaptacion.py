"""
Endpoint de generación de contenido educativo adaptativo — NuevaMente Backend.

Orquesta el flujo completo: RAG → LLM → evaluación pedagógica → respuesta estructurada.
"""

from fastapi import APIRouter, HTTPException, Request

from app.core.exceptions import (
    DocumentNotFoundError,
    EmptySelectionError,
    LLMGenerationError,
    LLMNotConfiguredError,
    NoRelevantSourcesError,
    RAGTechnicalError,
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
        "Recibe uno o varios documentos previamente ingestados y parámetros educativos, "
        "ejecuta el pipeline RAG + LLM, y retorna contenido pedagógico "
        "personalizado en el formato solicitado.\n\n"
        "**Selección de documentos:**\n"
        "- `documento_id` (legado): un único documento.\n"
        "- `documento_ids` (nuevo): lista de documentos para Estudio Focalizado. "
        "Si se envían ambos, `documento_ids` tiene precedencia."
    ),
)
async def generar_contenido(
    adaptacion_request: AdaptacionRequest,
    request: Request,
) -> AdaptacionResponse:
    """
    Genera contenido educativo adaptativo.

    Los documentos deben haber sido previamente cargados mediante
    POST /api/v1/files/upload.

    Returns:
        AdaptacionResponse con el contenido generado y metadatos de evaluación.

    Raises:
        400: documento_ids vacío o con solo cadenas en blanco (EmptySelectionError).
        404: Ningún documento_id existe en el índice (DocumentNotFoundError), o
             los documentos existen pero no hay chunks relevantes (NoRelevantSourcesError).
        500: Fallo técnico en el servicio RAG (RAGTechnicalError).
        503: Servicio LLM no configurado (LLMNotConfiguredError).
        502: Error durante la generación con el LLM (LLMGenerationError).
    """
    agent_service = getattr(request.app.state, "agent_service", None)

    if agent_service is None:
        raise LLMNotConfiguredError(
            message="Servicio de Agentes no disponible.",
            detail="El servicio LLM requerido no está configurado correctamente."
        )

    try:
        return agent_service.generate_content(adaptacion_request)

    except EmptySelectionError as exc:
        raise HTTPException(
            status_code=400,
            detail={"error": exc.message, "detalle": exc.detail},
        ) from exc

    except DocumentNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={"error": exc.message, "detalle": exc.detail},
        ) from exc

    except NoRelevantSourcesError as exc:
        raise HTTPException(
            status_code=404,
            detail={"error": exc.message, "detalle": exc.detail},
        ) from exc

    except RAGTechnicalError as exc:
        raise HTTPException(
            status_code=500,
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
