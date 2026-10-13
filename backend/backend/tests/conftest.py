"""
Fixtures de pytest compartidas para la suite de tests de NuevaMente Backend.

Este módulo define los mocks de servicios y la app FastAPI configurada para
operar en modo de prueba, de forma que los tests no dependan de credenciales
externas (OCI, OpenAI, etc.) ni de estado persistente entre ejecuciones.
"""

from __future__ import annotations

import pytest
import numpy as np
from unittest.mock import MagicMock

from starlette.testclient import TestClient

from app.services.rag_service import ChunkMetadata
from app.services.oci_service import OCIUploadResult


# ---------------------------------------------------------------------------
# Fixtures de mocks de servicios
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_rag_service():
    """Mock de RAGService con comportamiento esperado para tests."""
    mock = MagicMock()
    mock.document_exists.return_value = True
    mock.ingest_document.return_value = 3  # 3 chunks indexados
    # Retorna chunks de prueba representativos del dominio fintech
    mock.retrieve.return_value = [
        ChunkMetadata(
            chunk_id="chunk-001",
            documento_id="doc-test-123",
            texto="Este es un fragmento de prueba sobre tecnología financiera.",
            posicion=0,
            score=0.85,
        ),
        ChunkMetadata(
            chunk_id="chunk-002",
            documento_id="doc-test-123",
            texto="Las APIs REST permiten integración entre sistemas bancarios.",
            posicion=1,
            score=0.72,
        ),
    ]
    # generate_embeddings retorna un array numpy normalizado de dimensión 384
    mock.generate_embeddings.return_value = (
        np.ones((1, 384), dtype=np.float32) / np.sqrt(384)
    )
    mock._settings = MagicMock()
    mock._settings.rag_top_k = 5
    return mock


@pytest.fixture
def mock_llm_service():
    """Mock de LLMService que retorna contenido educativo de prueba."""
    mock = MagicMock()
    mock.generate.return_value = (
        "Paso 1: Introducción al tema\n"
        "Este es el contenido educativo generado por el LLM para propósitos de prueba.\n"
        "Paso 2: Desarrollo del concepto\n"
        "Aplicación práctica del tema en el contexto financiero."
    )
    return mock


@pytest.fixture
def mock_oci_service():
    """Mock de OCIService en modo no configurado (comportamiento normal sin credenciales)."""
    mock = MagicMock()
    mock.upload_document.return_value = OCIUploadResult(status="no_configurado")
    mock.upload_artifact.return_value = OCIUploadResult(status="no_configurado")
    return mock


@pytest.fixture
def mock_oci_failing():
    """Mock de OCIService que simula un fallo durante la subida."""
    mock = MagicMock()
    mock.upload_document.return_value = OCIUploadResult(
        status="error", detalle="Conexión rechazada"
    )
    mock.upload_artifact.return_value = OCIUploadResult(
        status="error", detalle="Conexión rechazada"
    )
    return mock


# ---------------------------------------------------------------------------
# Fixture de app con servicios mockeados
# ---------------------------------------------------------------------------


@pytest.fixture
def app_with_mocks(mock_rag_service, mock_llm_service, mock_oci_service):
    """
    App FastAPI con todos los servicios reemplazados por mocks.

    Incluye un documento 'doc-test-123' pre-registrado en el RAG mock,
    por lo que las llamadas a document_exists('doc-test-123') retornan True
    sin necesidad de ingestar ningún documento real.
    """
    from app.main import app
    from app.services.agent_service import AgentService

    agent = AgentService(
        rag=mock_rag_service,
        llm=mock_llm_service,
        oci=mock_oci_service,
    )
    app.state.document_service = MagicMock()
    app.state.rag_service = mock_rag_service
    app.state.llm_service = mock_llm_service
    app.state.oci_service = mock_oci_service
    app.state.agent_service = agent
    return app


@pytest.fixture
def client(app_with_mocks):
    """TestClient de httpx para hacer requests HTTP a la app en tests."""
    with TestClient(app_with_mocks) as c:
        yield c
