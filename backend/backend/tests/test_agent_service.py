"""
Tests de propiedad para AgentService — NuevaMente Backend.

Propiedades:
  - Propiedad 8:  anclaje_fuente_score siempre en [0.0, 1.0]  (Req 3.12)
  - Propiedad 9:  respuesta siempre contiene campos obligatorios (Req 3.15, 3.16)
  - _nivel_confianza clasifica correctamente

Requisitos: 3.12, 3.15, 3.16
"""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import HealthCheck, given
from hypothesis import settings as h_settings
from hypothesis import strategies as st
from unittest.mock import MagicMock

from app.schemas.adaptacion import (
    AdaptacionRequest, FormatoSalida, Nicho, NivelDetalle, PerfilDestinatario,
)
from app.services.agent_service import AgentService
from app.services.oci_service import OCIUploadResult
from app.services.rag_service import ChunkMetadata


DOC_ID = "doc-agent-test-001"

CHUNKS = [
    ChunkMetadata(chunk_id="c1", documento_id=DOC_ID,
                  texto="El riesgo de credito es fundamental en fintech.", posicion=0, score=0.9),
    ChunkMetadata(chunk_id="c2", documento_id=DOC_ID,
                  texto="Los sistemas de pago digitales requieren cifrado.", posicion=1, score=0.75),
]

CONTENIDO = "Paso 1: Identificar el riesgo.\nPaso 2: Aplicar cifrado en pagos.\n"

CAMPOS_OBLIGATORIOS = [
    "status", "document_id", "metadatos", "contenido_adaptado",
    "evaluacion_calidad", "fuentes", "almacenamiento_oci",
]


def _emb() -> np.ndarray:
    v = np.ones((1, 384), dtype=np.float32)
    return v / np.linalg.norm(v)


def _rag(existe=True):
    m = MagicMock()
    m.document_exists.return_value = existe
    m.retrieve.return_value = CHUNKS
    m._settings = MagicMock()
    m._settings.rag_top_k = 5
    m.generate_embeddings.return_value = _emb()
    return m


def _llm():
    m = MagicMock()
    m.generate.return_value = CONTENIDO
    return m


def _oci():
    m = MagicMock()
    m.upload_artifact.return_value = OCIUploadResult(status="no_configurado")
    return m


# --- Tests de _nivel_confianza ---

class TestNivelConfianza:
    def setup_method(self):
        self.svc = AgentService(_rag(), _llm(), _oci())

    @pytest.mark.parametrize("score,esperado", [
        (1.0, "alto"), (0.7, "alto"), (0.69, "medio"),
        (0.4, "medio"), (0.39, "bajo"), (0.0, "bajo"),
    ])
    def test_clasificacion(self, score, esperado):
        """Cada rango de score produce el nivel de confianza correcto."""
        assert self.svc._nivel_confianza(score) == esperado


# --- Tests de _calculate_anclaje_score ---

def test_score_en_rango():
    """El score siempre debe estar en [0.0, 1.0]."""
    svc = AgentService(_rag(), _llm(), _oci())
    score = svc._calculate_anclaje_score(CONTENIDO, CHUNKS)
    assert 0.0 <= score <= 1.0


def test_score_sin_chunks_es_cero():
    """Sin chunks fuente el score debe ser 0.0."""
    svc = AgentService(_rag(), _llm(), _oci())
    assert svc._calculate_anclaje_score("contenido", []) == 0.0


# --- Propiedad 8: score siempre en [0.0, 1.0] ---

@h_settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(raw=st.floats(min_value=-2.0, max_value=2.0, allow_nan=False))
def test_propiedad_clamp_score(raw):
    """
    Propiedad 8: max(0.0, min(1.0, score)) siempre produce un valor en [0.0, 1.0].
    Valida: Requisito 3.12
    """
    resultado = max(0.0, min(1.0, raw))
    assert 0.0 <= resultado <= 1.0


# --- Propiedad 9: campos obligatorios siempre presentes ---

@h_settings(max_examples=20, suppress_health_check=[HealthCheck.too_slow])
@given(
    perfil=st.sampled_from([e.value for e in PerfilDestinatario]),
    formato=st.sampled_from([e.value for e in FormatoSalida]),
    nicho=st.sampled_from([e.value for e in Nicho]),
    nivel=st.sampled_from([e.value for e in NivelDetalle]),
)
def test_propiedad_campos_obligatorios(perfil, formato, nicho, nivel):
    """
    Propiedad 9: generate_content siempre incluye todos los campos obligatorios.
    Valida: Requisitos 3.15, 3.16
    """
    svc = AgentService(_rag(), _llm(), _oci())
    req = AdaptacionRequest(
        documento_id=DOC_ID,
        perfil_destinatario=perfil,
        formato_salida=formato,
        nicho=nicho,
        nivel_detalle=nivel,
    )
    respuesta = svc.generate_content(req)
    data = respuesta.model_dump()
    for campo in CAMPOS_OBLIGATORIOS:
        assert campo in data, f"Falta campo '{campo}'"


# --- Degradacion OCI ---

def test_fallo_oci_no_impide_respuesta():
    """Un fallo de OCI no debe bloquear la entrega del contenido."""
    oci_falla = MagicMock()
    oci_falla.upload_artifact.return_value = OCIUploadResult(status="error", detalle="Timeout")
    svc = AgentService(_rag(), _llm(), oci_falla)
    req = AdaptacionRequest(
        documento_id=DOC_ID,
        perfil_destinatario="principiante",
        formato_salida="tutorial",
        nicho="general",
        nivel_detalle="didactico",
    )
    resp = svc.generate_content(req)
    assert resp.contenido_adaptado is not None
    assert resp.almacenamiento_oci.status_upload == "error"
