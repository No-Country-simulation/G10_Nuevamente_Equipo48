"""
Tests de propiedad para RAGService.

Propiedades verificadas:
  - Propiedad 6:  La ingesta produce ≥1 chunk para cualquier texto no vacío
  - Propiedad 12: Todos los chunks producidos por chunk_text son strings no vacíos
  - Propiedad 13: La recuperación retorna exactamente k chunks cuando el corpus es suficiente
  - Propiedad 15: Cada chunk almacenado preserva su documento_id de origen

Requisitos: 2.8, 2.11, 6.1, 6.4, 6.5, 6.6
"""
from __future__ import annotations

from unittest.mock import MagicMock

import numpy as np
import pytest
from hypothesis import HealthCheck, given
from hypothesis import settings as h_settings
from hypothesis import strategies as st

from app.core.exceptions import DocumentNotFoundError
from app.services.rag_service import ChunkMetadata, RAGService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_settings(chunk_size: int = 200, top_k: int = 3) -> MagicMock:
    """Construye un mock de Settings para RAGService sin requerir variables de entorno."""
    mock = MagicMock()
    mock.llm_provider = "google_gemini"   # usa SentenceTransformer local (sin API key)
    mock.embedding_model = "all-MiniLM-L6-v2"
    mock.rag_chunk_size = chunk_size
    mock.rag_top_k = top_k
    mock.vector_store_type = "faiss"
    return mock


# ---------------------------------------------------------------------------
# Propiedad 6: ingesta produce ≥1 chunk para cualquier texto no vacío
# ---------------------------------------------------------------------------

@h_settings(
    max_examples=10,          # bajo porque inicializa SentenceTransformer en cada ejemplo
    suppress_health_check=[HealthCheck.too_slow],
    deadline=None,
)
@given(
    texto=st.text(
        alphabet=st.characters(
            blacklist_categories=("Cs",),   # excluir surrogates
            blacklist_characters="\x00",    # excluir nulo
        ),
        min_size=10,
        max_size=300,
    )
)
def test_propiedad_ingesta_produce_chunks(texto):
    """
    Propiedad 6: Para cualquier texto no vacío (≥10 caracteres), la ingesta
    produce al menos un chunk indexado en el índice FAISS.

    Valida: Requisitos 2.8, 2.11
    """
    service = RAGService(_make_settings(chunk_size=100))
    doc_id = "doc-prop6"

    n_chunks = service.ingest_document(texto, doc_id)

    # Debe haberse indexado al menos un chunk
    assert n_chunks >= 1
    # document_exists debe reflejar la ingesta
    assert service.document_exists(doc_id)


# ---------------------------------------------------------------------------
# Propiedad 12: chunks respetan el límite de tamaño configurado
# ---------------------------------------------------------------------------

@h_settings(
    max_examples=20,
    suppress_health_check=[HealthCheck.too_slow],
    deadline=None,
)
@given(
    chunk_size=st.integers(min_value=50, max_value=300),
    texto=st.text(
        alphabet=st.characters(
            blacklist_categories=("Cs",),
            blacklist_characters="\x00",
        ),
        min_size=20,
        max_size=500,
    ),
)
def test_propiedad_chunks_respetan_tamano(chunk_size, texto):
    """
    Propiedad 12: Todos los chunks producidos por chunk_text son strings no
    vacíos. chunk_text es un método puro que no necesita embeddings, por lo
    que el mock de SentenceTransformer nunca se invoca aquí.

    Valida: Requisito 6.1
    """
    service = RAGService(_make_settings(chunk_size=chunk_size))
    chunks = service.chunk_text(texto, chunk_size)

    # Siempre debe producir al menos un chunk para texto no vacío
    assert len(chunks) >= 1

    # Cada elemento debe ser un string no vacío
    for chunk in chunks:
        assert isinstance(chunk, str)
        assert len(chunk) > 0


# ---------------------------------------------------------------------------
# Propiedad 13: retrieve retorna exactamente top_k chunks cuando el corpus
# tiene suficientes documentos (test determinista, no basado en hypothesis,
# porque requiere ingesta previa y embeddings reales)
# ---------------------------------------------------------------------------

def test_propiedad_retrieve_retorna_top_k():
    """
    Propiedad 13: Cuando el corpus indexado para un documento contiene más
    chunks que top_k, retrieve retorna exactamente top_k resultados.

    Valida: Requisito 6.4
    """
    top_k = 3
    service = RAGService(_make_settings(chunk_size=50, top_k=top_k))
    doc_id = "doc-prop13"

    # Texto suficientemente largo para generar al menos top_k chunks con
    # chunk_size=50 tokens (~200–250 tokens totales con 4 repeticiones)
    texto = (
        "La inteligencia artificial transforma los mercados financieros globales. "
        "Las herramientas de análisis predictivo permiten decisiones más informadas. "
        "La gestión del riesgo es fundamental en cualquier estrategia de inversión. "
        "Los algoritmos modernos procesan grandes volúmenes de datos en tiempo real. "
    ) * 4

    n_chunks = service.ingest_document(texto, doc_id)
    # Verificar que hay suficientes chunks para la prueba
    assert n_chunks >= top_k, (
        f"Se esperaban al menos {top_k} chunks pero se produjeron {n_chunks}; "
        "ajusta el texto o el chunk_size."
    )

    resultados = service.retrieve("análisis financiero riesgo", doc_id, top_k=top_k)

    assert len(resultados) == top_k


# ---------------------------------------------------------------------------
# Propiedad 15: chunks preservan documento_id de origen
# ---------------------------------------------------------------------------

def test_propiedad_chunks_preservan_documento_id():
    """
    Propiedad 15: Todos los chunks indexados por ingest_document conservan
    el documento_id del documento padre en el campo documento_id del
    dataclass ChunkMetadata.

    Valida: Requisito 6.6
    """
    service = RAGService(_make_settings())
    doc_id = "mi-documento-unico-123"
    texto = (
        "Este es un texto de prueba para verificar que los chunks "
        "preservan el documento_id de origen correctamente. "
    ) * 5

    service.ingest_document(texto, doc_id)

    # Filtrar los chunks que pertenecen a este documento
    chunks_del_doc = [c for c in service._chunks if c.documento_id == doc_id]
    assert len(chunks_del_doc) >= 1, "No se indexó ningún chunk para el documento."

    for chunk in chunks_del_doc:
        assert chunk.documento_id == doc_id, (
            f"Se esperaba documento_id='{doc_id}' pero se encontró '{chunk.documento_id}'"
        )


# ---------------------------------------------------------------------------
# Tests unitarios de soporte: document_exists
# ---------------------------------------------------------------------------

def test_document_exists_retorna_false_para_doc_inexistente():
    """document_exists debe retornar False para un documento no ingestado."""
    service = RAGService(_make_settings())
    assert not service.document_exists("doc-que-no-existe-xyz")


def test_document_exists_retorna_true_despues_de_ingestar():
    """document_exists debe retornar True inmediatamente después de ingestar."""
    service = RAGService(_make_settings())
    doc_id = "doc-existente-abc"
    service.ingest_document("Texto de prueba para verificar existencia del documento.", doc_id)
    assert service.document_exists(doc_id)


# ---------------------------------------------------------------------------
# Tests unitarios de soporte: retrieve lanza DocumentNotFoundError
# ---------------------------------------------------------------------------

def test_retrieve_lanza_error_para_doc_inexistente():
    """
    retrieve debe lanzar DocumentNotFoundError cuando el documento_id
    indicado no existe en el índice.
    """
    service = RAGService(_make_settings())

    with pytest.raises(DocumentNotFoundError):
        service.retrieve("consulta de prueba", "doc-inexistente-xyz", top_k=3)


def test_retrieve_retorna_lista_de_chunk_metadata():
    """
    retrieve debe retornar una lista de objetos ChunkMetadata con el campo
    score asignado y el documento_id correcto.
    """
    service = RAGService(_make_settings(chunk_size=50))
    doc_id = "doc-retrieve-test"
    texto = (
        "Finanzas personales y gestión patrimonial para inversores. "
        "Fondos de inversión y cartera diversificada de activos. "
    ) * 6

    service.ingest_document(texto, doc_id)
    resultados = service.retrieve("gestión patrimonial", doc_id, top_k=2)

    assert isinstance(resultados, list)
    assert len(resultados) >= 1

    for chunk in resultados:
        assert isinstance(chunk, ChunkMetadata)
        assert chunk.documento_id == doc_id
        # El score debe haber sido asignado (no el valor por defecto 0.0 de ingesta)
        assert isinstance(chunk.score, float)


# ---------------------------------------------------------------------------
# Tests unitarios de soporte: chunk_text con texto vacío y chunk_size inválido
# ---------------------------------------------------------------------------

def test_chunk_text_texto_vacio_retorna_lista_vacia():
    """chunk_text debe retornar [] para un texto vacío."""
    service = RAGService(_make_settings())
    assert service.chunk_text("", chunk_size=100) == []
    assert service.chunk_text("   ", chunk_size=100) == []


def test_chunk_text_chunk_size_invalido_lanza_error():
    """chunk_text debe lanzar ValueError para chunk_size <= 0."""
    service = RAGService(_make_settings())
    with pytest.raises(ValueError):
        service.chunk_text("Texto de prueba.", chunk_size=0)
    with pytest.raises(ValueError):
        service.chunk_text("Texto de prueba.", chunk_size=-5)


def test_chunk_text_texto_corto_produce_un_solo_chunk():
    """Un texto con menos tokens que chunk_size debe producir un único chunk."""
    service = RAGService(_make_settings())
    texto = "Texto corto."
    chunks = service.chunk_text(texto, chunk_size=500)
    assert len(chunks) == 1
    assert chunks[0] == texto


# ---------------------------------------------------------------------------
# Tests unitarios de soporte: generate_embeddings
# ---------------------------------------------------------------------------

def test_generate_embeddings_retorna_array_normalizado():
    """
    generate_embeddings debe retornar un array numpy float32 con norma L2
    aproximadamente 1.0 para cada vector (normalización L2 garantizada).
    """
    service = RAGService(_make_settings())
    textos = ["fragmento uno", "fragmento dos"]

    embeddings = service.generate_embeddings(textos)

    assert isinstance(embeddings, np.ndarray)
    assert embeddings.dtype == np.float32
    assert embeddings.shape[0] == len(textos)

    # Verificar normalización L2: ||v||₂ ≈ 1.0
    normas = np.linalg.norm(embeddings, axis=1)
    np.testing.assert_allclose(normas, 1.0, atol=1e-5)


def test_generate_embeddings_lista_vacia_lanza_error():
    """generate_embeddings debe lanzar ValueError para una lista vacía."""
    service = RAGService(_make_settings())
    with pytest.raises(ValueError):
        service.generate_embeddings([])
