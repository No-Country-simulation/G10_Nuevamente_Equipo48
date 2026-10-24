"""
Tests para el flujo de Estudio Focalizado — selección múltiple de documentos.

Cubre:
  A. Validación del schema AdaptacionRequest (modelo_validator, compatibilidad legado)
  B. RAGService.retrieve_multi (documento único, múltiple, IDs inválidos, vacío)
  C. AgentService.generate_content con documento_ids (múltiple, parcialmente inválido,
     sin fuentes relevantes)
  D. Endpoint POST /api/v1/adaptacion — integración HTTP con varios documentos
  E. Regresión: flujo singular (documento_id legado) sigue funcionando sin cambios

Requisitos cubiertos: compatibilidad hacia atrás, trazabilidad de fuentes,
EmptySelectionError (HTTP 400), DocumentNotFoundError (HTTP 404),
NoRelevantSourcesError (HTTP 404).
"""

from __future__ import annotations

import numpy as np
import pytest
from unittest.mock import MagicMock, patch
from starlette.testclient import TestClient

from app.core.exceptions import (
    DocumentNotFoundError,
    EmptySelectionError,
    NoRelevantSourcesError,
)
from app.main import app
from app.schemas.adaptacion import (
    AdaptacionRequest,
    AdaptacionResponse,
    FormatoSalida,
    Nicho,
    NivelDetalle,
    PerfilDestinatario,
)
from app.services.agent_service import AgentService
from app.services.oci_service import OCIUploadResult
from app.services.rag_service import ChunkMetadata, RAGService
from app.core.config import Settings


# ---------------------------------------------------------------------------
# Constantes de prueba
# ---------------------------------------------------------------------------

DOC_A = "doc-alpha-001"
DOC_B = "doc-beta-002"
DOC_C = "doc-gamma-003"

CHUNKS_A = [
    ChunkMetadata(chunk_id="a1", documento_id=DOC_A,
                  texto="La tokenización permite pagos seguros en fintech.", posicion=0, score=0.90),
    ChunkMetadata(chunk_id="a2", documento_id=DOC_A,
                  texto="Los wallets digitales reducen la fricción en comercio.", posicion=1, score=0.80),
]
CHUNKS_B = [
    ChunkMetadata(chunk_id="b1", documento_id=DOC_B,
                  texto="Los smart contracts automatizan acuerdos sin intermediarios.", posicion=0, score=0.85),
    ChunkMetadata(chunk_id="b2", documento_id=DOC_B,
                  texto="DeFi redistribuye el acceso al crédito globalmente.", posicion=1, score=0.70),
]

CONTENIDO_PRUEBA = (
    "Paso 1: Tokenización en pagos digitales.\n"
    "Paso 2: Smart contracts para automatizar acuerdos.\n"
)

REQUEST_BASE = {
    "perfil_destinatario": "principiante",
    "formato_salida": "tutorial",
    "nicho": "fintech",
    "nivel_detalle": "didactico",
}


# ---------------------------------------------------------------------------
# Helpers de mocks
# ---------------------------------------------------------------------------

def _emb() -> np.ndarray:
    v = np.ones((1, 384), dtype=np.float32)
    return v / np.linalg.norm(v)


def _oci():
    m = MagicMock()
    m.upload_artifact.return_value = OCIUploadResult(status="no_configurado")
    return m


def _llm(contenido: str = CONTENIDO_PRUEBA):
    m = MagicMock()
    m.generate.return_value = contenido
    return m


def _rag_multi(docs: dict[str, list[ChunkMetadata]]):
    """
    Crea un mock de RAGService que simula retrieve_multi para los docs dados.
    """
    m = MagicMock()
    m._settings = MagicMock()
    m._settings.rag_top_k = 5
    m.generate_embeddings.return_value = _emb()

    def _retrieve_multi(query, documento_ids, top_k):
        validos = [d for d in documento_ids if d in docs]
        invalidos = [d for d in documento_ids if d not in docs]
        if not validos:
            raise DocumentNotFoundError(
                message="Ninguno de los documentos especificados existe en el índice.",
                detail=f"IDs no encontrados: {', '.join(documento_ids)}",
            )
        todos = []
        for d in validos:
            todos.extend(docs[d])
        todos.sort(key=lambda c: c.score, reverse=True)
        return todos[:top_k], invalidos

    m.retrieve_multi.side_effect = _retrieve_multi
    return m


# ---------------------------------------------------------------------------
# A. Validación de schema — AdaptacionRequest
# ---------------------------------------------------------------------------

class TestAdaptacionRequestSchema:
    """Pruebas del model_validator y compatibilidad del schema."""

    def test_legado_documento_id_se_normaliza_a_lista(self):
        """A1: documento_id singular se convierte a documento_ids de un elemento."""
        req = AdaptacionRequest(
            documento_id=DOC_A,
            **{k: v for k, v in REQUEST_BASE.items()},
        )
        assert req.documento_ids == [DOC_A]

    def test_documento_ids_tiene_precedencia_sobre_documento_id(self):
        """A2: Cuando se envían ambos campos, documento_ids prevalece."""
        req = AdaptacionRequest(
            documento_id=DOC_A,
            documento_ids=[DOC_A, DOC_B],
            **{k: v for k, v in REQUEST_BASE.items()},
        )
        assert req.documento_ids == [DOC_A, DOC_B]
        # El campo documento_id queda en su valor original (no se borra)
        assert req.documento_id == DOC_A

    def test_solo_documento_ids_valido(self):
        """A3: Solo documento_ids sin documento_id es válido."""
        req = AdaptacionRequest(
            documento_ids=[DOC_A, DOC_B],
            **{k: v for k, v in REQUEST_BASE.items()},
        )
        assert req.documento_ids == [DOC_A, DOC_B]

    def test_lista_vacia_lanza_validation_error(self):
        """A4: documento_ids vacía debe fallar la validación Pydantic."""
        with pytest.raises(Exception) as exc_info:
            AdaptacionRequest(
                documento_ids=[],
                **{k: v for k, v in REQUEST_BASE.items()},
            )
        assert "vacío" in str(exc_info.value).lower() or "vac" in str(exc_info.value).lower()

    def test_lista_solo_blancos_lanza_validation_error(self):
        """A5: documento_ids con solo strings vacíos debe fallar."""
        with pytest.raises(Exception):
            AdaptacionRequest(
                documento_ids=["  ", ""],
                **{k: v for k, v in REQUEST_BASE.items()},
            )

    def test_sin_documento_id_ni_documento_ids_lanza_validation_error(self):
        """A6: Sin ningún campo de documento debe fallar la validación."""
        with pytest.raises(Exception):
            AdaptacionRequest(**{k: v for k, v in REQUEST_BASE.items()})

    def test_ids_con_espacios_se_limpian(self):
        """A7: Los espacios al inicio/fin de los IDs se eliminan."""
        req = AdaptacionRequest(
            documento_ids=["  doc-a  ", " doc-b"],
            **{k: v for k, v in REQUEST_BASE.items()},
        )
        assert req.documento_ids == ["doc-a", "doc-b"]

    def test_documento_id_con_espacios_se_limpia(self):
        """A8: El campo legado documento_id también se normaliza sin espacios."""
        req = AdaptacionRequest(
            documento_id="  doc-x  ",
            **{k: v for k, v in REQUEST_BASE.items()},
        )
        assert req.documento_ids == ["doc-x"]


# ---------------------------------------------------------------------------
# B. RAGService.retrieve_multi
# ---------------------------------------------------------------------------

class TestRetrieveMulti:
    """Pruebas unitarias de RAGService.retrieve_multi usando un RAGService real."""

    @pytest.fixture
    def rag(self):
        """RAGService con dos documentos pre-ingestados usando chunks mockeados."""
        settings = MagicMock()
        settings.rag_chunk_size = 512
        settings.embedding_model = "all-MiniLM-L6-v2"

        svc = RAGService(settings)

        # Inyectar chunks y un índice FAISS mínimo directamente
        # para no depender de SentenceTransformer real
        emb_dim = 4
        svc._dimension = emb_dim

        import faiss  # noqa: PLC0415
        svc._index = faiss.IndexFlatIP(emb_dim)

        # Vectores normalizados L2 sintéticos
        rng = np.random.default_rng(42)
        vecs_a = rng.random((2, emb_dim), dtype=np.float32)
        vecs_b = rng.random((2, emb_dim), dtype=np.float32)
        for v in [*vecs_a, *vecs_b]:
            v /= np.linalg.norm(v)

        all_vecs = np.array([*vecs_a, *vecs_b], dtype=np.float32)
        svc._index.add(all_vecs)

        svc._chunks = [
            ChunkMetadata(chunk_id="a1", documento_id=DOC_A, texto="texto A1", posicion=0),
            ChunkMetadata(chunk_id="a2", documento_id=DOC_A, texto="texto A2", posicion=1),
            ChunkMetadata(chunk_id="b1", documento_id=DOC_B, texto="texto B1", posicion=0),
            ChunkMetadata(chunk_id="b2", documento_id=DOC_B, texto="texto B2", posicion=1),
        ]

        # Mock generate_embeddings para evitar carga de modelo
        query_vec = rng.random((1, emb_dim), dtype=np.float32)
        query_vec /= np.linalg.norm(query_vec)
        svc.generate_embeddings = MagicMock(return_value=query_vec)

        return svc

    def test_retorna_chunks_de_todos_los_documentos(self, rag):
        """B1: retrieve_multi devuelve chunks de cada documento solicitado."""
        chunks, invalidos = rag.retrieve_multi("query", [DOC_A, DOC_B], top_k=4)
        ids_doc = {c.documento_id for c in chunks}
        assert DOC_A in ids_doc
        assert DOC_B in ids_doc
        assert invalidos == []

    def test_top_k_limita_total_de_chunks(self, rag):
        """B2: El resultado global no supera top_k."""
        chunks, _ = rag.retrieve_multi("query", [DOC_A, DOC_B], top_k=3)
        assert len(chunks) <= 3

    def test_ids_invalidos_se_reportan(self, rag):
        """B3: IDs no existentes aparecen en la lista de inválidos."""
        chunks, invalidos = rag.retrieve_multi("query", [DOC_A, "doc-inexistente"], top_k=4)
        assert "doc-inexistente" in invalidos
        assert len(chunks) > 0  # Los válidos siguen devolviendo resultados

    def test_todos_invalidos_lanza_document_not_found(self, rag):
        """B4: Si todos los IDs son inválidos se lanza DocumentNotFoundError."""
        with pytest.raises(DocumentNotFoundError):
            rag.retrieve_multi("query", ["no-existe-1", "no-existe-2"], top_k=5)

    def test_lista_vacia_lanza_document_not_found(self, rag):
        """B5: Lista vacía de IDs lanza DocumentNotFoundError."""
        with pytest.raises(DocumentNotFoundError):
            rag.retrieve_multi("query", [], top_k=5)

    def test_chunks_ordenados_por_score_descendente(self, rag):
        """B6: Los chunks del resultado están ordenados de mayor a menor score."""
        chunks, _ = rag.retrieve_multi("query", [DOC_A, DOC_B], top_k=4)
        scores = [c.score for c in chunks]
        assert scores == sorted(scores, reverse=True)

    def test_trazabilidad_documento_id_en_cada_chunk(self, rag):
        """B7: Cada chunk retornado lleva su documento_id original."""
        chunks, _ = rag.retrieve_multi("query", [DOC_A, DOC_B], top_k=4)
        for c in chunks:
            assert c.documento_id in (DOC_A, DOC_B)


# ---------------------------------------------------------------------------
# C. AgentService.generate_content — multi-documento
# ---------------------------------------------------------------------------

class TestAgentServiceMultiDoc:
    """Pruebas de generate_content con documento_ids."""

    def _req(self, doc_ids: list[str] | None = None, doc_id: str | None = None):
        kwargs = {**REQUEST_BASE}
        if doc_ids is not None:
            kwargs["documento_ids"] = doc_ids
        if doc_id is not None:
            kwargs["documento_id"] = doc_id
        return AdaptacionRequest(**kwargs)

    def test_respuesta_incluye_documento_ids(self):
        """C1: La respuesta contiene la lista completa de documento_ids."""
        rag = _rag_multi({DOC_A: CHUNKS_A, DOC_B: CHUNKS_B})
        svc = AgentService(rag=rag, llm=_llm(), oci=_oci())
        resp = svc.generate_content(self._req(doc_ids=[DOC_A, DOC_B]))
        assert resp.documento_ids == [DOC_A, DOC_B]

    def test_document_id_es_primer_elemento(self):
        """C2: document_id (campo legado) es el primer elemento de documento_ids."""
        rag = _rag_multi({DOC_A: CHUNKS_A, DOC_B: CHUNKS_B})
        svc = AgentService(rag=rag, llm=_llm(), oci=_oci())
        resp = svc.generate_content(self._req(doc_ids=[DOC_A, DOC_B]))
        assert resp.document_id == DOC_A

    def test_fuentes_incluyen_documento_id_de_cada_chunk(self):
        """C3: Cada fuente en la respuesta lleva el documento_id de su origen."""
        rag = _rag_multi({DOC_A: CHUNKS_A, DOC_B: CHUNKS_B})
        svc = AgentService(rag=rag, llm=_llm(), oci=_oci())
        resp = svc.generate_content(self._req(doc_ids=[DOC_A, DOC_B]))
        ids_en_fuentes = {f.documento_id for f in resp.fuentes}
        # Al menos uno de los dos documentos debe estar representado
        assert len(ids_en_fuentes) >= 1
        assert ids_en_fuentes.issubset({DOC_A, DOC_B})

    def test_metadatos_contienen_documento_ids(self):
        """C4: Los metadatos de respuesta incluyen la lista documento_ids."""
        rag = _rag_multi({DOC_A: CHUNKS_A, DOC_B: CHUNKS_B})
        svc = AgentService(rag=rag, llm=_llm(), oci=_oci())
        resp = svc.generate_content(self._req(doc_ids=[DOC_A, DOC_B]))
        assert resp.metadatos.documento_ids == [DOC_A, DOC_B]

    def test_todos_invalidos_lanza_document_not_found(self):
        """C5: Si ningún ID existe, generate_content lanza DocumentNotFoundError."""
        rag = _rag_multi({})  # índice vacío
        svc = AgentService(rag=rag, llm=_llm(), oci=_oci())
        with pytest.raises(DocumentNotFoundError):
            svc.generate_content(self._req(doc_ids=["no-existe"]))

    def test_sin_chunks_lanza_no_relevant_sources(self):
        """C6: Si retrieve_multi devuelve lista vacía, lanza NoRelevantSourcesError."""
        rag = MagicMock()
        rag._settings = MagicMock()
        rag._settings.rag_top_k = 5
        rag.generate_embeddings.return_value = _emb()
        # retrieve_multi devuelve 0 chunks (documentos existen pero no hay resultados)
        rag.retrieve_multi.return_value = ([], [])
        svc = AgentService(rag=rag, llm=_llm(), oci=_oci())
        with pytest.raises(NoRelevantSourcesError):
            svc.generate_content(self._req(doc_ids=[DOC_A]))

    def test_id_invalido_parcial_no_impide_respuesta(self):
        """C7: Con un ID inválido y uno válido, la respuesta se genera igualmente."""
        rag = _rag_multi({DOC_A: CHUNKS_A})
        svc = AgentService(rag=rag, llm=_llm(), oci=_oci())
        resp = svc.generate_content(self._req(doc_ids=[DOC_A, "doc-inexistente"]))
        assert resp.status == "ok"
        assert resp.contenido_adaptado is not None

    # --- Regresión: modo singular (legado) ---

    def test_regresion_modo_singular_documento_id(self):
        """C8 (regresión): documento_id singular sigue produciendo respuesta válida."""
        rag = _rag_multi({DOC_A: CHUNKS_A})
        svc = AgentService(rag=rag, llm=_llm(), oci=_oci())
        resp = svc.generate_content(self._req(doc_id=DOC_A))
        assert resp.status == "ok"
        assert resp.document_id == DOC_A
        assert resp.documento_ids == [DOC_A]

    def test_regresion_campos_obligatorios_presentes_modo_singular(self):
        """C9 (regresión): Todos los campos obligatorios siguen presentes en modo singular."""
        rag = _rag_multi({DOC_A: CHUNKS_A})
        svc = AgentService(rag=rag, llm=_llm(), oci=_oci())
        resp = svc.generate_content(self._req(doc_id=DOC_A))
        data = resp.model_dump()
        for campo in ["status", "document_id", "documento_ids", "metadatos",
                      "contenido_adaptado", "evaluacion_calidad", "fuentes",
                      "almacenamiento_oci"]:
            assert campo in data, f"Campo obligatorio '{campo}' ausente"

    def test_regresion_score_en_rango(self):
        """C10 (regresión): anclaje_fuente_score en [0.0, 1.0] en modo singular."""
        rag = _rag_multi({DOC_A: CHUNKS_A})
        svc = AgentService(rag=rag, llm=_llm(), oci=_oci())
        resp = svc.generate_content(self._req(doc_id=DOC_A))
        assert 0.0 <= resp.evaluacion_calidad.anclaje_fuente_score <= 1.0


# ---------------------------------------------------------------------------
# D. Endpoint HTTP — integración
# ---------------------------------------------------------------------------

def _build_client(rag_mock, llm_mock=None, oci_mock=None):
    """Construye un TestClient con los servicios inyectados."""
    if llm_mock is None:
        llm_mock = _llm()
    if oci_mock is None:
        oci_mock = _oci()
    agent = AgentService(rag=rag_mock, llm=llm_mock, oci=oci_mock)
    app.state.agent_service = agent
    return TestClient(app)


class TestEndpointMultiDoc:
    """Pruebas de integración HTTP para Estudio Focalizado."""

    def test_documento_ids_retorna_200(self):
        """D1: Petición con documento_ids válidos retorna HTTP 200."""
        rag = _rag_multi({DOC_A: CHUNKS_A, DOC_B: CHUNKS_B})
        client = _build_client(rag)
        resp = client.post("/api/v1/adaptacion", json={
            **REQUEST_BASE,
            "documento_ids": [DOC_A, DOC_B],
        })
        assert resp.status_code == 200

    def test_respuesta_200_contiene_documento_ids(self):
        """D2: La respuesta 200 incluye el campo documento_ids."""
        rag = _rag_multi({DOC_A: CHUNKS_A, DOC_B: CHUNKS_B})
        client = _build_client(rag)
        resp = client.post("/api/v1/adaptacion", json={
            **REQUEST_BASE,
            "documento_ids": [DOC_A, DOC_B],
        })
        data = resp.json()
        assert "documento_ids" in data
        assert data["documento_ids"] == [DOC_A, DOC_B]

    def test_fuentes_trazan_documento_id(self):
        """D3: Cada fuente en la respuesta incluye su documento_id."""
        rag = _rag_multi({DOC_A: CHUNKS_A, DOC_B: CHUNKS_B})
        client = _build_client(rag)
        resp = client.post("/api/v1/adaptacion", json={
            **REQUEST_BASE,
            "documento_ids": [DOC_A, DOC_B],
        })
        data = resp.json()
        for fuente in data["fuentes"]:
            assert "documento_id" in fuente

    def test_todos_invalidos_retorna_404(self):
        """D4: IDs completamente inexistentes retornan HTTP 404."""
        rag = _rag_multi({})
        client = _build_client(rag)
        resp = client.post("/api/v1/adaptacion", json={
            **REQUEST_BASE,
            "documento_ids": ["no-existe-xyz"],
        })
        assert resp.status_code == 404

    def test_404_body_contiene_detalle(self):
        """D5: El cuerpo del 404 por IDs inválidos incluye información de error."""
        rag = _rag_multi({})
        client = _build_client(rag)
        resp = client.post("/api/v1/adaptacion", json={
            **REQUEST_BASE,
            "documento_ids": ["no-existe-xyz"],
        })
        data = resp.json()
        assert "detail" in data

    def test_lista_vacia_retorna_422(self):
        """D6: documento_ids vacío falla validación Pydantic → HTTP 422."""
        rag = _rag_multi({DOC_A: CHUNKS_A})
        client = _build_client(rag)
        resp = client.post("/api/v1/adaptacion", json={
            **REQUEST_BASE,
            "documento_ids": [],
        })
        assert resp.status_code == 422

    def test_sin_ningun_campo_documento_retorna_422(self):
        """D7: Sin documento_id ni documento_ids → HTTP 422."""
        rag = _rag_multi({DOC_A: CHUNKS_A})
        client = _build_client(rag)
        resp = client.post("/api/v1/adaptacion", json=REQUEST_BASE)
        assert resp.status_code == 422

    def test_no_relevant_sources_retorna_404(self):
        """D8: Documentos existentes sin chunks retornan HTTP 404 (NoRelevantSourcesError)."""
        rag = MagicMock()
        rag._settings = MagicMock()
        rag._settings.rag_top_k = 5
        rag.generate_embeddings.return_value = _emb()
        rag.retrieve_multi.return_value = ([], [])  # Sin chunks
        client = _build_client(rag)
        resp = client.post("/api/v1/adaptacion", json={
            **REQUEST_BASE,
            "documento_ids": [DOC_A],
        })
        assert resp.status_code == 404

    def test_id_invalido_parcial_retorna_200(self):
        """D9: Un ID inválido mezclado con uno válido produce HTTP 200 (degradación parcial)."""
        rag = _rag_multi({DOC_A: CHUNKS_A})
        client = _build_client(rag)
        resp = client.post("/api/v1/adaptacion", json={
            **REQUEST_BASE,
            "documento_ids": [DOC_A, "doc-inexistente"],
        })
        assert resp.status_code == 200

    # --- Regresión HTTP: modo singular (legado) ---

    def test_regresion_http_documento_id_singular_retorna_200(self):
        """D10 (regresión): documento_id singular sigue retornando HTTP 200."""
        rag = _rag_multi({DOC_A: CHUNKS_A})
        client = _build_client(rag)
        resp = client.post("/api/v1/adaptacion", json={
            **REQUEST_BASE,
            "documento_id": DOC_A,
        })
        assert resp.status_code == 200

    def test_regresion_http_document_id_en_respuesta(self):
        """D11 (regresión): El campo document_id sigue presente en modo singular."""
        rag = _rag_multi({DOC_A: CHUNKS_A})
        client = _build_client(rag)
        resp = client.post("/api/v1/adaptacion", json={
            **REQUEST_BASE,
            "documento_id": DOC_A,
        })
        assert resp.json()["document_id"] == DOC_A

    def test_regresion_http_404_documento_singular_inexistente(self):
        """D12 (regresión): documento_id inexistente en modo singular sigue retornando 404."""
        rag = _rag_multi({})
        client = _build_client(rag)
        resp = client.post("/api/v1/adaptacion", json={
            **REQUEST_BASE,
            "documento_id": "doc-que-no-existe",
        })
        assert resp.status_code == 404

    def test_regresion_http_campos_obligatorios_en_respuesta_singular(self):
        """D13 (regresión): Todos los campos obligatorios siguen presentes en modo singular."""
        rag = _rag_multi({DOC_A: CHUNKS_A})
        client = _build_client(rag)
        resp = client.post("/api/v1/adaptacion", json={
            **REQUEST_BASE,
            "documento_id": DOC_A,
        })
        data = resp.json()
        for campo in ["status", "document_id", "documento_ids", "metadatos",
                      "contenido_adaptado", "evaluacion_calidad", "fuentes",
                      "almacenamiento_oci"]:
            assert campo in data, f"Campo '{campo}' ausente en respuesta singular"


# ---------------------------------------------------------------------------
# E. Regresión: tests de agent_service existentes con nueva firma
# ---------------------------------------------------------------------------

class TestAgentServiceRegresionFirma:
    """Verifica que los tests existentes del agente siguen pasando con la nueva firma."""

    DOC_ID = "doc-agent-reg-001"

    def _rag(self):
        return _rag_multi({self.DOC_ID: [
            ChunkMetadata(chunk_id="r1", documento_id=self.DOC_ID,
                          texto="Riesgo de crédito es fundamental.", posicion=0, score=0.9),
        ]})

    def test_fallo_oci_no_impide_respuesta(self):
        """E1 (regresión): Un fallo de OCI no bloquea la entrega del contenido."""
        oci_falla = MagicMock()
        oci_falla.upload_artifact.return_value = OCIUploadResult(
            status="error", detalle="Timeout"
        )
        svc = AgentService(rag=self._rag(), llm=_llm(), oci=oci_falla)
        req = AdaptacionRequest(
            documento_id=self.DOC_ID,
            **{k: v for k, v in REQUEST_BASE.items()},
        )
        resp = svc.generate_content(req)
        assert resp.contenido_adaptado is not None
        assert resp.almacenamiento_oci.status_upload == "error"

    def test_metadatos_educativos_presentes(self):
        """E2 (regresión): tiempo_estimado_estudio_minutos y conceptos_clave siempre presentes."""
        svc = AgentService(rag=self._rag(), llm=_llm(), oci=_oci())
        req = AdaptacionRequest(
            documento_id=self.DOC_ID,
            **{k: v for k, v in REQUEST_BASE.items()},
        )
        resp = svc.generate_content(req)
        assert resp.metadatos.tiempo_estimado_estudio_minutos >= 1
        assert isinstance(resp.metadatos.conceptos_clave, list)


class TestApartadosEstudioFocalizado:
    """Pruebas para la selección y orientación por apartados en Estudio Focalizado."""

    def test_schema_apartados_se_limpian(self):
        """Los apartados con espacios en blanco o vacíos se normalizan."""
        req = AdaptacionRequest(
            documento_ids=["doc-1"],
            apartados=["  1.1 Introducción  ", " ", "2.1 Modelos"],
            **{k: v for k, v in REQUEST_BASE.items()},
        )
        assert req.apartados == ["1.1 Introducción", "2.1 Modelos"]

    def test_agent_service_con_apartados_enfoca_prompt_y_query(self):
        """AgentService incluye los apartados seleccionados en el prompt y en la query RAG."""
        mock_rag = MagicMock()
        mock_rag.document_exists.return_value = True
        mock_rag.retrieve_multi.return_value = (
            [ChunkMetadata(chunk_id="c1", documento_id="doc-1", texto="Contenido de modelos.", posicion=0, score=0.95)],
            [],
        )
        mock_rag.generate_embeddings.return_value = np.array([[0.95]], dtype=np.float32)

        mock_llm = MagicMock()
        mock_llm.generate.return_value = "Contenido adaptado sobre modelos."
        mock_oci = MagicMock()
        mock_oci.upload_artifact.return_value = OCIUploadResult(status="ok")

        svc = AgentService(rag=mock_rag, llm=mock_llm, oci=mock_oci)
        req = AdaptacionRequest(
            documento_ids=["doc-1"],
            apartados=["1.1 Introducción", "2.1 Modelos de Datos"],
            **{k: v for k, v in REQUEST_BASE.items()},
        )
        resp = svc.generate_content(req)

        # 1. Query RAG debe incluir los apartados
        call_query = mock_rag.retrieve_multi.call_args[1]["query"]
        assert "1.1 Introducción" in call_query or "2.1 Modelos" in call_query

        # 2. Prompts enviados al LLM deben referenciar los apartados
        user_prompt_sent = mock_llm.generate.call_args[0][0]
        system_prompt_sent = mock_llm.generate.call_args[0][1]
        assert "1.1 Introducción" in user_prompt_sent or "1.1 Introducción" in system_prompt_sent

        # 3. Metadatos de respuesta deben contener los apartados
        assert resp.metadatos.apartados == ["1.1 Introducción", "2.1 Modelos de Datos"]

    def test_endpoint_corpus_structure(self):
        """GET /api/v1/files/corpus/{id}/structure retorna apartados del documento si existe."""
        from app.services.document_service import DocumentService
        app.state.document_service = DocumentService()
        client = TestClient(app)
        resp = client.get("/api/v1/files/corpus/NM-006/structure")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["documento_id"] == "NM-006"
        assert "apartados" in data
        assert isinstance(data["apartados"], list)
        assert len(data["apartados"]) > 0

    def test_query_rag_combina_tema_y_apartados(self):
        """La consulta RAG combina tanto tema_o_pregunta como los apartados cuando ambos están presentes."""
        mock_rag = MagicMock()
        mock_rag.document_exists.return_value = True
        mock_rag.retrieve_multi.return_value = (
            [
                ChunkMetadata(chunk_id="c1", documento_id="doc-1", texto="Texto de BD.", posicion=0, score=0.92),
                ChunkMetadata(chunk_id="c2", documento_id="doc-2", texto="Texto de Seguridad.", posicion=0, score=0.88),
            ],
            [],
        )
        mock_rag.generate_embeddings.return_value = np.array([[0.92]], dtype=np.float32)

        mock_llm = MagicMock()
        mock_llm.generate.return_value = "Contenido adaptado combinado."
        mock_oci = MagicMock()
        mock_oci.upload_artifact.return_value = OCIUploadResult(status="ok")

        svc = AgentService(rag=mock_rag, llm=mock_llm, oci=mock_oci)
        req = AdaptacionRequest(
            documento_ids=["doc-1", "doc-2"],
            tema_o_pregunta="¿Cómo asegurar el almacenamiento relacional?",
            apartados=["1.4 Concepto de BD", "Medidas de Seguridad"],
            **{k: v for k, v in REQUEST_BASE.items()},
        )
        resp = svc.generate_content(req)

        # 1. Query RAG debe incluir TANTO la pregunta como los apartados
        call_query = mock_rag.retrieve_multi.call_args[1]["query"]
        assert "¿Cómo asegurar el almacenamiento relacional?" in call_query
        assert "1.4 Concepto de BD" in call_query
        assert "Medidas de Seguridad" in call_query

        # 2. La consulta debe respetar los documentos seleccionados
        call_doc_ids = mock_rag.retrieve_multi.call_args[1]["documento_ids"]
        assert call_doc_ids == ["doc-1", "doc-2"]

        # 3. Prompt al LLM debe incluir ambos
        user_prompt_sent = mock_llm.generate.call_args[0][0]
        system_prompt_sent = mock_llm.generate.call_args[0][1]
        assert "¿Cómo asegurar el almacenamiento relacional?" in user_prompt_sent or "¿Cómo asegurar el almacenamiento relacional?" in system_prompt_sent
        assert "1.4 Concepto de BD" in user_prompt_sent or "1.4 Concepto de BD" in system_prompt_sent

        # 4. Atribución de fuentes intacta
        assert len(resp.fuentes) == 2
        assert resp.fuentes[0].documento_id == "doc-1"
        assert resp.fuentes[1].documento_id == "doc-2"
        assert resp.fuentes[0].score_relevancia == 0.92

    def test_query_rag_solo_con_tema_sin_apartados(self):
        """Si solo hay tema_o_pregunta, la query RAG lo incluye y omite apartados."""
        mock_rag = MagicMock()
        mock_rag.document_exists.return_value = True
        mock_rag.retrieve_multi.return_value = (
            [ChunkMetadata(chunk_id="c1", documento_id="doc-1", texto="Texto.", posicion=0, score=0.9)],
            [],
        )
        mock_rag.generate_embeddings.return_value = np.array([[0.9]], dtype=np.float32)
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "Contenido."

        svc = AgentService(rag=mock_rag, llm=mock_llm, oci=MagicMock(upload_artifact=MagicMock(return_value=OCIUploadResult(status="ok"))))
        req = AdaptacionRequest(
            documento_ids=["doc-1"],
            tema_o_pregunta="Pregunta específica de estudio",
            apartados=[],
            **{k: v for k, v in REQUEST_BASE.items()},
        )
        svc.generate_content(req)
        call_query = mock_rag.retrieve_multi.call_args[1]["query"]
        assert "Pregunta específica de estudio" in call_query

    def test_query_rag_sin_tema_ni_apartados_usa_solo_enums(self):
        """Si no hay ni tema ni apartados, la query RAG se genera con los enums."""
        mock_rag = MagicMock()
        mock_rag.document_exists.return_value = True
        mock_rag.retrieve_multi.return_value = (
            [ChunkMetadata(chunk_id="c1", documento_id="doc-1", texto="Texto.", posicion=0, score=0.9)],
            [],
        )
        mock_rag.generate_embeddings.return_value = np.array([[0.9]], dtype=np.float32)
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "Contenido."

        svc = AgentService(rag=mock_rag, llm=mock_llm, oci=MagicMock(upload_artifact=MagicMock(return_value=OCIUploadResult(status="ok"))))
        req = AdaptacionRequest(
            documento_ids=["doc-1"],
            tema_o_pregunta=None,
            apartados=None,
            **{k: v for k, v in REQUEST_BASE.items()},
        )
        svc.generate_content(req)
        call_query = mock_rag.retrieve_multi.call_args[1]["query"]
        assert req.nicho.value in call_query
        assert req.nivel_detalle.value in call_query
        assert req.formato_salida.value in call_query

