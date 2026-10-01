"""
Punto de entrada principal de NuevaMente Backend.

Configura la instancia FastAPI, middlewares, servicios singleton,
routers y manejadores globales de excepciones.
"""

from __future__ import annotations

import logging
import logging.config

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.exceptions import (
    ConfigurationError,
    DocumentNotFoundError,
    ExtractionError,
    LLMGenerationError,
    LLMNotConfiguredError,
)
from app.api.v1.endpoints import health, files, adaptacion
from app.services.document_service import DocumentService
from app.services.rag_service import RAGService
from app.services.llm_service import LLMService
from app.services.oci_service import OCIService
from app.services.agent_service import AgentService

# ---------------------------------------------------------------------------
# Configuración de logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan — inicialización y limpieza de servicios
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Gestiona el ciclo de vida de la aplicación.

    Al arrancar: inicializa y registra los servicios singleton en app.state.
    Al cerrar: registra el evento de apagado.
    """
    logger.info("Iniciando NuevaMente Backend — inicializando servicios...")

    # Instanciar servicios independientes
    app.state.document_service = DocumentService()
    logger.info("DocumentService inicializado.")

    app.state.rag_service = RAGService(settings)
    logger.info("RAGService inicializado.")

    # LLMService puede lanzar ConfigurationError si LLM_PROVIDER es inválido.
    # En ese caso, registramos el error pero NO bloqueamos el arranque:
    # el endpoint de adaptación responderá con 503 si se intenta usar el LLM.
    try:
        app.state.llm_service = LLMService(settings)
        logger.info("LLMService inicializado.")
    except ConfigurationError as exc:
        logger.error(
            "LLMService no pudo inicializarse: %s — %s", exc.message, exc.detail
        )
        app.state.llm_service = None  # type: ignore[assignment]

    app.state.oci_service = OCIService(settings)
    logger.info("OCIService inicializado.")

    # AgentService requiere llm_service. Si no está disponible, también queda
    # en None; el endpoint de adaptación manejará ese caso con HTTP 503.
    if app.state.llm_service is not None:
        app.state.agent_service = AgentService(
            rag=app.state.rag_service,
            llm=app.state.llm_service,
            oci=app.state.oci_service,
        )
        logger.info("AgentService inicializado.")
    else:
        app.state.agent_service = None  # type: ignore[assignment]
        logger.warning(
            "AgentService no disponible porque LLMService no pudo inicializarse."
        )

    logger.info("NuevaMente Backend listo para recibir solicitudes.")

    yield  # La aplicación corre aquí

    logger.info("NuevaMente Backend apagándose.")


# ---------------------------------------------------------------------------
# Instancia principal FastAPI
# ---------------------------------------------------------------------------

app = FastAPI(
    title="NuevaMente Backend",
    version="1.0.0",
    description=(
        "Sistema Inteligente de Adaptación y Generación de Contenido Educativo. "
        "Procesa documentos técnicos (PDF, Markdown, TXT) mediante un pipeline RAG "
        "y genera artefactos pedagógicos personalizados con modelos LLM."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# ---------------------------------------------------------------------------
# Middlewares
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

# GET /health
app.include_router(health.router)

# POST /api/v1/files/upload
app.include_router(files.router, prefix="/api/v1/files")

# POST /api/v1/adaptacion
app.include_router(adaptacion.router, prefix="/api/v1")


# ---------------------------------------------------------------------------
# Manejadores globales de excepciones
# ---------------------------------------------------------------------------


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Maneja errores de validación Pydantic (HTTP 422).

    Convierte la lista interna de errores de Pydantic en un mensaje
    descriptivo en español, indicando qué campos son inválidos.
    """
    detalle = _formatear_errores_validacion(exc.errors())
    logger.warning(
        "Error de validación en %s %s: %s",
        request.method,
        request.url.path,
        detalle,
    )
    return JSONResponse(
        status_code=422,
        content={
            "error": "Los datos enviados contienen campos inválidos.",
            "detalle": detalle,
        },
    )


@app.exception_handler(DocumentNotFoundError)
async def document_not_found_handler(
    request: Request, exc: DocumentNotFoundError
) -> JSONResponse:
    """Maneja la excepción de documento no encontrado (HTTP 404)."""
    logger.warning(
        "Documento no encontrado en %s %s: %s",
        request.method,
        request.url.path,
        exc.detail,
    )
    return JSONResponse(
        status_code=404,
        content={"error": exc.message, "detalle": exc.detail},
    )


@app.exception_handler(LLMNotConfiguredError)
async def llm_not_configured_handler(
    request: Request, exc: LLMNotConfiguredError
) -> JSONResponse:
    """Maneja la excepción de LLM no configurado (HTTP 503)."""
    logger.error(
        "LLM no configurado en %s %s: %s",
        request.method,
        request.url.path,
        exc.detail,
    )
    return JSONResponse(
        status_code=503,
        content={"error": exc.message, "detalle": exc.detail},
    )


@app.exception_handler(LLMGenerationError)
async def llm_generation_error_handler(
    request: Request, exc: LLMGenerationError
) -> JSONResponse:
    """Maneja errores durante la generación con el LLM (HTTP 502)."""
    logger.error(
        "Error de generación LLM en %s %s: %s",
        request.method,
        request.url.path,
        exc.detail,
        exc_info=True,
    )
    return JSONResponse(
        status_code=502,
        content={"error": exc.message, "detalle": exc.detail},
    )


@app.exception_handler(ExtractionError)
async def extraction_error_handler(
    request: Request, exc: ExtractionError
) -> JSONResponse:
    """Maneja errores de extracción de texto de documentos (HTTP 422)."""
    logger.warning(
        "Error de extracción en %s %s: %s",
        request.method,
        request.url.path,
        exc.detail,
    )
    return JSONResponse(
        status_code=422,
        content={"error": exc.message, "detalle": exc.detail},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """
    Captura cualquier excepción no controlada (HTTP 500).

    Registra el traceback completo en el log con nivel ERROR,
    pero NO expone detalles internos ni trazas al cliente.
    """
    logger.error(
        "Error interno no controlado en %s %s",
        request.method,
        request.url.path,
        exc_info=exc,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error interno del servidor.",
            "detalle": "Contacte al equipo de soporte.",
        },
    )


# ---------------------------------------------------------------------------
# Utilidades internas
# ---------------------------------------------------------------------------


def _formatear_errores_validacion(errores: list[dict]) -> str:
    """
    Convierte la lista de errores de Pydantic en un string descriptivo en español.

    Cada error incluye la ubicación del campo y el mensaje de validación.

    Args:
        errores: Lista de dicts con la estructura de errores de Pydantic v2.

    Returns:
        String con los errores formateados, separados por "; ".
    """
    partes: list[str] = []
    for error in errores:
        # La ubicación es una tupla con el camino al campo (p.ej. ("body", "perfil"))
        ubicacion = " → ".join(str(parte) for parte in error.get("loc", []))
        mensaje = error.get("msg", "valor inválido")
        partes.append(f"[{ubicacion}]: {mensaje}")
    return "; ".join(partes) if partes else "Solicitud inválida."
