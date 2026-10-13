"""
Tests para el endpoint POST /api/v1/adaptacion.

Todos los servicios externos (RAG, LLM, OCI) se mockean para que
los tests sean independientes de credenciales y conexiones externas.

Cubre los requisitos 9.3, 9.4 y 9.5:
  9.3 — Tests de ejemplo para el flujo de adaptación (HTTP 200, 404, 503).
  9.4 — Tests de propiedad: anclaje_fuente_score en [0.0, 1.0] y campos obligatorios.
  9.5 — Tests de propiedad: fallo de OCI no bloquea la generación de contenido.
"""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings as h_settings
from hypothesis import strategies as st
from unittest.mock import MagicMock
from starlette.testclient import TestClient

from app.core.exceptions import (
    DocumentNotFoundError,
    LLMGenerationError,
    LLMNotConfiguredError,
)
from app.schemas.adaptacion import (
    FormatoSalida,
    Nicho,
    NivelDetalle,
    PerfilDestinatario,
)
from app.services.agent_service import AgentService
from app.services.oci_service import OCIUploadResult
from app.services.rag_service import ChunkMetadata
from app.main import app


# ---------------------------------------------------------------------------
# Constantes de prueba
# ---------------------------------------------------------------------------

DOCUMENTO_ID_EXISTENTE = "doc-test-abc123"

CHUNKS_PRUEBA = [
    ChunkMetadata(
        chunk_id="chunk-001",
        documento_id=DOCUMENTO_ID_EXISTENTE,
        texto="La tokenización en fintech permite pagos digitales seguros.",
        posicion=0,
        score=0.88,
    ),
    ChunkMetadata(
        chunk_id="chunk-002",
        documento_id=DOCUMENTO_ID_EXISTENTE,
        texto="Los smart contracts automatizan acuerdos financieros sin intermediarios.",
        posicion=1,
        score=0.75,
    ),
]

REQUEST_VALIDO = {
    "documento_id": DOCUMENTO_ID_EXISTENTE,
    "perfil_destinatario": "principiante",
    "formato_salida": "tutorial",
    "nicho": "fintech",
    "nivel_detalle": "didactico",
}

# Todos los campos que la respuesta exitosa debe contener
CAMPOS_OBLIGATORIOS_RESPONSE = [
    "status",
    "document_id",
    "metadatos",
    "contenido_adaptado",
    "evaluacion_calidad",
    "fuentes",
    "almacenamiento_oci",
]

# Texto generado de prueba que devuelve el mock del LLM
CONTENIDO_LLM_PRUEBA = (
    "Paso 1: Introducción a la tokenización.\n"
    "La tokenización convierte datos sensibles en tokens únicos.\n"
    "Paso 2: Aplicación en pagos digitales.\n"
    "Permite transacciones seguras sin exponer datos bancarios reales."
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_rag():
    """Mock de RAGService con documento existente y chunks de prueba."""
    mock = MagicMock()
    mock.document_exists.return_value = True
    mock.retrieve.return_value = CHUNKS_PRUEBA
    mock._settings = MagicMock()
    mock._settings.rag_top_k = 5
    # Embeddings normalizados L2 de dimensión 384 para el cálculo del anclaje
    emb = np.ones((1, 384), dtype=np.float32)
    emb = emb / np.linalg.norm(emb)
    mock.generate_embeddings.return_value = emb
    return mock


@pytest.fixture
def mock_llm():
    """Mock de LLMService que devuelve contenido educativo de prueba."""
    mock = MagicMock()
    mock.generate.return_value = CONTENIDO_LLM_PRUEBA
    return mock


@pytest.fixture
def mock_oci():
    """Mock de OCIService en modo no configurado (comportamiento normal sin credenciales)."""
    mock = MagicMock()
    mock.upload_artifact.return_value = OCIUploadResult(status="no_configurado")
    mock.upload_document.return_value = OCIUploadResult(status="no_configurado")
    return mock


@pytest.fixture
def mock_oci_falla():
    """Mock de OCIService que simula un error de red durante la subida del artefacto."""
    mock = MagicMock()
    mock.upload_artifact.return_value = OCIUploadResult(
        status="error", detalle="Timeout de conexión a OCI"
    )
    mock.upload_document.return_value = OCIUploadResult(
        status="error", detalle="Timeout de conexión a OCI"
    )
    return mock


@pytest.fixture
def client_con_mocks(mock_rag, mock_llm, mock_oci):
    """
    TestClient con todos los servicios mockeados.

    Construye un AgentService real con los mocks inyectados e inyecta
    los servicios en app.state antes de iniciar el cliente.
    """
    agent = AgentService(rag=mock_rag, llm=mock_llm, oci=mock_oci)
    app.state.rag_service = mock_rag
    app.state.llm_service = mock_llm
    app.state.oci_service = mock_oci
    app.state.agent_service = agent
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Clase de tests de ejemplo — flujos principales
# ---------------------------------------------------------------------------


class TestAdaptacionEndpoint:
    """
    Tests de ejemplo para el endpoint POST /api/v1/adaptacion.

    Valida los flujos principales: respuesta exitosa, errores esperados
    por documento inexistente o LLM no configurado, y degradación ante
    fallos de OCI.
    """

    def test_solicitud_valida_retorna_200(self, client_con_mocks):
        """Una solicitud con todos los parámetros válidos debe retornar HTTP 200."""
        response = client_con_mocks.post("/api/v1/adaptacion", json=REQUEST_VALIDO)
        assert response.status_code == 200

    def test_respuesta_contiene_campos_obligatorios(self, client_con_mocks):
        """La respuesta exitosa debe contener todos los campos obligatorios del schema."""
        response = client_con_mocks.post("/api/v1/adaptacion", json=REQUEST_VALIDO)
        data = response.json()
        for campo in CAMPOS_OBLIGATORIOS_RESPONSE:
            assert campo in data, f"Campo obligatorio '{campo}' ausente en la respuesta"

    def test_metadatos_reflejan_parametros_de_entrada(self, client_con_mocks):
        """Los metadatos de la respuesta deben coincidir exactamente con los parámetros enviados."""
        response = client_con_mocks.post("/api/v1/adaptacion", json=REQUEST_VALIDO)
        data = response.json()
        assert data["metadatos"]["perfil_destinatario"] == REQUEST_VALIDO["perfil_destinatario"]
        assert data["metadatos"]["formato_salida"] == REQUEST_VALIDO["formato_salida"]
        assert data["metadatos"]["nicho"] == REQUEST_VALIDO["nicho"]
        assert data["metadatos"]["nivel_detalle"] == REQUEST_VALIDO["nivel_detalle"]

    def test_document_id_en_respuesta_coincide_con_request(self, client_con_mocks):
        """El document_id de la respuesta debe coincidir con el enviado en el request."""
        response = client_con_mocks.post("/api/v1/adaptacion", json=REQUEST_VALIDO)
        data = response.json()
        assert data["document_id"] == REQUEST_VALIDO["documento_id"]

    def test_evaluacion_calidad_score_en_rango(self, client_con_mocks):
        """El anclaje_fuente_score debe estar en el rango cerrado [0.0, 1.0]."""
        response = client_con_mocks.post("/api/v1/adaptacion", json=REQUEST_VALIDO)
        data = response.json()
        score = data["evaluacion_calidad"]["anclaje_fuente_score"]
        assert 0.0 <= score <= 1.0, (
            f"anclaje_fuente_score={score} fuera del rango esperado [0.0, 1.0]"
        )

    def test_nivel_confianza_valor_valido(self, client_con_mocks):
        """El nivel_confianza debe ser uno de los valores cualitativos válidos."""
        response = client_con_mocks.post("/api/v1/adaptacion", json=REQUEST_VALIDO)
        data = response.json()
        nivel = data["evaluacion_calidad"]["nivel_confianza"]
        assert nivel in ("alto", "medio", "bajo"), (
            f"nivel_confianza='{nivel}' no es un valor esperado"
        )

    def test_fuentes_no_vacias(self, client_con_mocks):
        """La lista de fuentes debe contener al menos un fragmento del documento."""
        response = client_con_mocks.post("/api/v1/adaptacion", json=REQUEST_VALIDO)
        data = response.json()
        assert len(data["fuentes"]) > 0

    def test_fuentes_tienen_score_relevancia_en_rango(self, client_con_mocks):
        """El score_relevancia de cada fuente debe estar en [0.0, 1.0]."""
        response = client_con_mocks.post("/api/v1/adaptacion", json=REQUEST_VALIDO)
        data = response.json()
        for fuente in data["fuentes"]:
            score = fuente["score_relevancia"]
            assert 0.0 <= score <= 1.0, (
                f"score_relevancia={score} fuera del rango en fuente chunk_id={fuente['chunk_id']}"
            )

    def test_contenido_adaptado_no_es_nulo(self, client_con_mocks):
        """El campo contenido_adaptado no debe ser None en una respuesta exitosa."""
        response = client_con_mocks.post("/api/v1/adaptacion", json=REQUEST_VALIDO)
        data = response.json()
        assert data["contenido_adaptado"] is not None

    # ------------------------------------------------------------------
    # Tests de error esperado
    # ------------------------------------------------------------------

    def test_documento_no_encontrado_retorna_404(self, mock_rag, mock_llm, mock_oci):
        """Un documento_id inexistente debe retornar HTTP 404."""
        mock_rag.document_exists.return_value = False
        agent = AgentService(rag=mock_rag, llm=mock_llm, oci=mock_oci)
        app.state.rag_service = mock_rag
        app.state.agent_service = agent
        with TestClient(app) as c:
            response = c.post("/api/v1/adaptacion", json={
                **REQUEST_VALIDO,
                "documento_id": "doc-inexistente-xyz",
            })
        assert response.status_code == 404

    def test_documento_no_encontrado_body_contiene_detalle(self, mock_rag, mock_llm, mock_oci):
        """La respuesta 404 debe incluir información de error en el cuerpo JSON."""
        mock_rag.document_exists.return_value = False
        agent = AgentService(rag=mock_rag, llm=mock_llm, oci=mock_oci)
        app.state.rag_service = mock_rag
        app.state.agent_service = agent
        with TestClient(app) as c:
            response = c.post("/api/v1/adaptacion", json={
                **REQUEST_VALIDO,
                "documento_id": "doc-inexistente-xyz",
            })
        # El endpoint usa HTTPException, el cuerpo viene bajo "detail"
        data = response.json()
        assert "detail" in data

    def test_llm_no_configurado_retorna_503(self, mock_rag, mock_oci):
        """Cuando el LLM lanza LLMNotConfiguredError, el endpoint debe retornar HTTP 503."""
        mock_llm_no_conf = MagicMock()
        mock_llm_no_conf.generate.side_effect = LLMNotConfiguredError(
            message="El proveedor LLM no está configurado.",
            detail="La variable LLM_API_KEY está ausente.",
        )
        agent = AgentService(rag=mock_rag, llm=mock_llm_no_conf, oci=mock_oci)
        app.state.agent_service = agent
        with TestClient(app) as c:
            response = c.post("/api/v1/adaptacion", json=REQUEST_VALIDO)
        assert response.status_code == 503

    def test_error_generacion_llm_retorna_502(self, mock_rag, mock_oci):
        """Cuando el LLM lanza LLMGenerationError, el endpoint debe retornar HTTP 502."""
        mock_llm_error = MagicMock()
        mock_llm_error.generate.side_effect = LLMGenerationError(
            message="Error al generar contenido con el LLM.",
            detail="Timeout al contactar la API.",
        )
        agent = AgentService(rag=mock_rag, llm=mock_llm_error, oci=mock_oci)
        app.state.agent_service = agent
        with TestClient(app) as c:
            response = c.post("/api/v1/adaptacion", json=REQUEST_VALIDO)
        assert response.status_code == 502

    # ------------------------------------------------------------------
    # Tests de degradación elegante ante fallos de OCI
    # ------------------------------------------------------------------

    def test_fallo_oci_no_bloquea_respuesta(self, mock_rag, mock_llm, mock_oci_falla):
        """Un fallo de OCI no debe impedir la entrega del contenido educativo (HTTP 200)."""
        agent = AgentService(rag=mock_rag, llm=mock_llm, oci=mock_oci_falla)
        app.state.agent_service = agent
        with TestClient(app) as c:
            response = c.post("/api/v1/adaptacion", json=REQUEST_VALIDO)
        assert response.status_code == 200

    def test_fallo_oci_se_refleja_en_almacenamiento(self, mock_rag, mock_llm, mock_oci_falla):
        """Cuando OCI falla, el campo almacenamiento_oci debe indicar el error."""
        agent = AgentService(rag=mock_rag, llm=mock_llm, oci=mock_oci_falla)
        app.state.agent_service = agent
        with TestClient(app) as c:
            response = c.post("/api/v1/adaptacion", json=REQUEST_VALIDO)
        data = response.json()
        assert data["almacenamiento_oci"]["status_upload"] == "error"

    def test_fallo_oci_contenido_adaptado_presente(self, mock_rag, mock_llm, mock_oci_falla):
        """Incluso con fallo de OCI, el contenido educativo debe estar presente en la respuesta."""
        agent = AgentService(rag=mock_rag, llm=mock_llm, oci=mock_oci_falla)
        app.state.agent_service = agent
        with TestClient(app) as c:
            response = c.post("/api/v1/adaptacion", json=REQUEST_VALIDO)
        data = response.json()
        assert data["contenido_adaptado"] is not None

    # ------------------------------------------------------------------
    # Tests de validación Pydantic (HTTP 422)
    # ------------------------------------------------------------------

    def test_parametros_invalidos_retornan_422(self, client_con_mocks):
        """Un valor de enum inválido en perfil_destinatario debe retornar HTTP 422."""
        response = client_con_mocks.post("/api/v1/adaptacion", json={
            **REQUEST_VALIDO,
            "perfil_destinatario": "valor_inexistente",
        })
        assert response.status_code == 422

    def test_formato_salida_invalido_retorna_422(self, client_con_mocks):
        """Un valor de enum inválido en formato_salida debe retornar HTTP 422."""
        response = client_con_mocks.post("/api/v1/adaptacion", json={
            **REQUEST_VALIDO,
            "formato_salida": "podcast",
        })
        assert response.status_code == 422

    def test_campo_obligatorio_faltante_retorna_422(self, client_con_mocks):
        """Una solicitud sin el campo obligatorio 'formato_salida' debe retornar HTTP 422."""
        request_incompleto = {k: v for k, v in REQUEST_VALIDO.items() if k != "formato_salida"}
        response = client_con_mocks.post("/api/v1/adaptacion", json=request_incompleto)
        assert response.status_code == 422

    def test_body_vacio_retorna_422(self, client_con_mocks):
        """Un body JSON vacío debe retornar HTTP 422."""
        response = client_con_mocks.post("/api/v1/adaptacion", json={})
        assert response.status_code == 422

    # ------------------------------------------------------------------
    # Tests parametrizados — cobertura de todos los valores de enum
    # ------------------------------------------------------------------

    @pytest.mark.parametrize(
        "formato",
        ["tutorial", "flashcards", "quiz", "resumen_ejecutivo", "guion_clase"],
    )
    def test_todos_los_formatos_retornan_200(self, client_con_mocks, formato):
        """Todos los valores válidos de formato_salida deben producir HTTP 200."""
        response = client_con_mocks.post("/api/v1/adaptacion", json={
            **REQUEST_VALIDO,
            "formato_salida": formato,
        })
        assert response.status_code == 200, (
            f"formato='{formato}' retornó {response.status_code}, esperado 200"
        )

    @pytest.mark.parametrize(
        "perfil",
        ["principiante", "junior", "lider_tecnico", "ejecutivo"],
    )
    def test_todos_los_perfiles_retornan_200(self, client_con_mocks, perfil):
        """Todos los valores válidos de perfil_destinatario deben producir HTTP 200."""
        response = client_con_mocks.post("/api/v1/adaptacion", json={
            **REQUEST_VALIDO,
            "perfil_destinatario": perfil,
        })
        assert response.status_code == 200, (
            f"perfil='{perfil}' retornó {response.status_code}, esperado 200"
        )

    @pytest.mark.parametrize(
        "nicho",
        ["fintech", "salud", "ecommerce", "general"],
    )
    def test_todos_los_nichos_retornan_200(self, client_con_mocks, nicho):
        """Todos los valores válidos de nicho deben producir HTTP 200."""
        response = client_con_mocks.post("/api/v1/adaptacion", json={
            **REQUEST_VALIDO,
            "nicho": nicho,
        })
        assert response.status_code == 200, (
            f"nicho='{nicho}' retornó {response.status_code}, esperado 200"
        )

    @pytest.mark.parametrize(
        "nivel",
        ["didactico", "intermedio", "tecnico"],
    )
    def test_todos_los_niveles_retornan_200(self, client_con_mocks, nivel):
        """Todos los valores válidos de nivel_detalle deben producir HTTP 200."""
        response = client_con_mocks.post("/api/v1/adaptacion", json={
            **REQUEST_VALIDO,
            "nivel_detalle": nivel,
        })
        assert response.status_code == 200, (
            f"nivel='{nivel}' retornó {response.status_code}, esperado 200"
        )


# ---------------------------------------------------------------------------
# Tests de propiedad con Hypothesis — Requisitos 9.4, 9.5
# ---------------------------------------------------------------------------


# Estrategias de generación para los valores de enum válidos
_st_perfil = st.sampled_from([e.value for e in PerfilDestinatario])
_st_formato = st.sampled_from([e.value for e in FormatoSalida])
_st_nicho = st.sampled_from([e.value for e in Nicho])
_st_nivel = st.sampled_from([e.value for e in NivelDetalle])


class TestAdaptacionPropiedades:
    """
    Tests de propiedad con Hypothesis para el endpoint de adaptación.

    Verifica invariantes que deben cumplirse para cualquier combinación
    válida de parámetros de entrada.
    """

    @h_settings(
        max_examples=20,
        suppress_health_check=[HealthCheck.too_slow],
    )
    @given(
        perfil=_st_perfil,
        formato=_st_formato,
        nicho=_st_nicho,
        nivel=_st_nivel,
    )
    def test_propiedad_campos_obligatorios_siempre_presentes(
        self, perfil, formato, nicho, nivel
    ):
        """
        **Propiedad 9: La respuesta de adaptación exitosa siempre contiene
        todos los campos obligatorios para cualquier combinación de enums válidos.**

        Valida: Requisitos 3.15, 3.16, 9.4
        """
        # Construir mocks frescos para cada ejemplo generado por Hypothesis
        mock_rag = MagicMock()
        mock_rag.document_exists.return_value = True
        mock_rag.retrieve.return_value = CHUNKS_PRUEBA
        mock_rag._settings = MagicMock()
        mock_rag._settings.rag_top_k = 5
        emb = np.ones((1, 384), dtype=np.float32)
        emb = emb / np.linalg.norm(emb)
        mock_rag.generate_embeddings.return_value = emb

        mock_llm = MagicMock()
        mock_llm.generate.return_value = CONTENIDO_LLM_PRUEBA

        mock_oci = MagicMock()
        mock_oci.upload_artifact.return_value = OCIUploadResult(status="no_configurado")

        agent = AgentService(rag=mock_rag, llm=mock_llm, oci=mock_oci)
        app.state.agent_service = agent

        with TestClient(app) as c:
            response = c.post("/api/v1/adaptacion", json={
                "documento_id": DOCUMENTO_ID_EXISTENTE,
                "perfil_destinatario": perfil,
                "formato_salida": formato,
                "nicho": nicho,
                "nivel_detalle": nivel,
            })

        assert response.status_code == 200
        data = response.json()
        for campo in CAMPOS_OBLIGATORIOS_RESPONSE:
            assert campo in data, (
                f"Campo obligatorio '{campo}' ausente con "
                f"perfil={perfil}, formato={formato}, nicho={nicho}, nivel={nivel}"
            )

    @h_settings(
        max_examples=20,
        suppress_health_check=[HealthCheck.too_slow],
    )
    @given(
        perfil=_st_perfil,
        formato=_st_formato,
        nicho=_st_nicho,
        nivel=_st_nivel,
    )
    def test_propiedad_score_en_rango_para_cualquier_combinacion(
        self, perfil, formato, nicho, nivel
    ):
        """
        **Propiedad 8: El anclaje_fuente_score siempre está en [0.0, 1.0]
        para cualquier combinación válida de parámetros.**

        Valida: Requisito 3.12, 9.4
        """
        mock_rag = MagicMock()
        mock_rag.document_exists.return_value = True
        mock_rag.retrieve.return_value = CHUNKS_PRUEBA
        mock_rag._settings = MagicMock()
        mock_rag._settings.rag_top_k = 5
        emb = np.ones((1, 384), dtype=np.float32)
        emb = emb / np.linalg.norm(emb)
        mock_rag.generate_embeddings.return_value = emb

        mock_llm = MagicMock()
        mock_llm.generate.return_value = CONTENIDO_LLM_PRUEBA

        mock_oci = MagicMock()
        mock_oci.upload_artifact.return_value = OCIUploadResult(status="no_configurado")

        agent = AgentService(rag=mock_rag, llm=mock_llm, oci=mock_oci)
        app.state.agent_service = agent

        with TestClient(app) as c:
            response = c.post("/api/v1/adaptacion", json={
                "documento_id": DOCUMENTO_ID_EXISTENTE,
                "perfil_destinatario": perfil,
                "formato_salida": formato,
                "nicho": nicho,
                "nivel_detalle": nivel,
            })

        assert response.status_code == 200
        score = response.json()["evaluacion_calidad"]["anclaje_fuente_score"]
        assert 0.0 <= score <= 1.0, (
            f"anclaje_fuente_score={score} fuera del rango [0.0, 1.0] con "
            f"perfil={perfil}, formato={formato}"
        )

    @h_settings(
        max_examples=20,
        suppress_health_check=[HealthCheck.too_slow],
    )
    @given(
        perfil=_st_perfil,
        formato=_st_formato,
        nicho=_st_nicho,
        nivel=_st_nivel,
    )
    def test_propiedad_fallo_oci_no_bloquea_generacion(
        self, perfil, formato, nicho, nivel
    ):
        """
        **Propiedad 11: Un fallo de OCI no interrumpe la generación de contenido.**

        Verifica que para cualquier combinación válida de parámetros, un error
        de OCI produce HTTP 200 con el contenido entregado y
        almacenamiento_oci.status_upload == "error" o "no_configurado".

        Valida: Requisito 5.4, 9.5
        """
        mock_rag = MagicMock()
        mock_rag.document_exists.return_value = True
        mock_rag.retrieve.return_value = CHUNKS_PRUEBA
        mock_rag._settings = MagicMock()
        mock_rag._settings.rag_top_k = 5
        emb = np.ones((1, 384), dtype=np.float32)
        emb = emb / np.linalg.norm(emb)
        mock_rag.generate_embeddings.return_value = emb

        mock_llm = MagicMock()
        mock_llm.generate.return_value = CONTENIDO_LLM_PRUEBA

        # OCI falla con error en todos los casos
        mock_oci_falla = MagicMock()
        mock_oci_falla.upload_artifact.return_value = OCIUploadResult(
            status="error", detalle="Timeout de conexión"
        )

        agent = AgentService(rag=mock_rag, llm=mock_llm, oci=mock_oci_falla)
        app.state.agent_service = agent

        with TestClient(app) as c:
            response = c.post("/api/v1/adaptacion", json={
                "documento_id": DOCUMENTO_ID_EXISTENTE,
                "perfil_destinatario": perfil,
                "formato_salida": formato,
                "nicho": nicho,
                "nivel_detalle": nivel,
            })

        # El contenido debe entregarse aunque OCI haya fallado
        assert response.status_code == 200, (
            f"HTTP {response.status_code} — OCI falla no debe bloquear la respuesta"
        )
        data = response.json()
        assert data["contenido_adaptado"] is not None
        assert data["almacenamiento_oci"]["status_upload"] in ("error", "no_configurado"), (
            f"status_upload inesperado: {data['almacenamiento_oci']['status_upload']}"
        )

    @h_settings(
        max_examples=20,
        suppress_health_check=[HealthCheck.too_slow],
    )
    @given(perfil_invalido=st.text().filter(
        lambda s: s not in {e.value for e in PerfilDestinatario} and len(s) > 0
    ))
    def test_propiedad_enum_invalido_retorna_422(self, perfil_invalido):
        """
        **Propiedad 7: Los campos de enum rechazan exactamente los valores
        fuera del conjunto permitido, retornando HTTP 422.**

        Valida: Requisitos 3.3, 3.4, 3.5, 3.6, 9.4
        """
        mock_rag = MagicMock()
        mock_rag.document_exists.return_value = True
        mock_llm = MagicMock()
        mock_oci = MagicMock()
        agent = AgentService(rag=mock_rag, llm=mock_llm, oci=mock_oci)
        app.state.agent_service = agent

        with TestClient(app) as c:
            response = c.post("/api/v1/adaptacion", json={
                **REQUEST_VALIDO,
                "perfil_destinatario": perfil_invalido,
            })

        assert response.status_code == 422, (
            f"perfil_invalido='{perfil_invalido}' retornó {response.status_code}, "
            f"esperado 422"
        )
