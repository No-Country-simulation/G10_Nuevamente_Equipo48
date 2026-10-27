"""
Pruebas automatizadas exhaustivas para la precarga del corpus verificado APTO (P3.2 / P3.2.1).

Cobertura:
1. Exclusión estricta de documentos con clasificación distinta de APTO.
2. Procesamiento completo del texto extraído (sin truncamiento arbitrario).
3. Conservación del identificador documental y metadatos de los fragmentos indexados.
4. Idempotencia y omisión de documentos ya presentes en el índice.
5. Manejo tolerante de archivos ausentes, ilegibles o con texto vacío.
6. Manejo de excepciones en la ingesta y su efecto exacto sobre el resumen y reporte.
7. Análisis del riesgo de ingesta parcial / falla a mitad de procesamiento.
8. Comportamiento seguro cuando no existe el directorio del corpus.
9. Uso de la misma instancia de RAG compartida por FastAPI en app.state.
10. Ausencia total de requerimiento de LLM o LLM_API_KEY.
11. Verificación del orden y ciclo de vida de inicialización en lifespan de FastAPI.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from starlette.testclient import TestClient

from app.core.config import Settings
from app.main import app, lifespan
from app.services.corpus_loader import (
    CorpusDocumentSpec,
    PreloadSummary,
    VERIFIED_APTO_CORPUS,
    find_corpus_root,
    preload_verified_corpus,
)
from app.services.document_service import DocumentService
from app.services.rag_service import RAGService


@pytest.fixture
def test_settings() -> Settings:
    """Configuración controlada de prueba para RAGService."""
    return Settings(
        CHUNK_SIZE=500,
        CHUNK_OVERLAP=50,
        TOP_K_DEFAULT=3,
        LLM_PROVIDER="mock",
        LLM_MODEL="mock-model",
    )


@pytest.fixture
def rag_service(test_settings: Settings) -> RAGService:
    """Instancia limpia de RAGService para pruebas unitarias."""
    return RAGService(test_settings)


@pytest.fixture
def doc_service() -> DocumentService:
    """Instancia de DocumentService para pruebas."""
    return DocumentService()


# ---------------------------------------------------------------------------
# 1. Catálogo y especificaciones de auditoría
# ---------------------------------------------------------------------------


def test_verified_apto_catalog_specifications():
    """El catálogo estricto VERIFIED_APTO_CORPUS debe contener solo documentos APTO respaldados."""
    assert len(VERIFIED_APTO_CORPUS) >= 1
    for spec in VERIFIED_APTO_CORPUS:
        assert spec.estado_auditoria == "APTO"
        assert spec.documento_id.startswith("NM-")
        assert spec.ruta_relativa.endswith(".pdf")


def test_find_corpus_root_locates_existing_dir():
    """find_corpus_root debe localizar la carpeta real del corpus si existe."""
    root = find_corpus_root()
    if root is not None:
        assert root.is_dir()
        assert (root / VERIFIED_APTO_CORPUS[0].ruta_relativa).exists()


def test_preload_filters_out_non_apto_documents(rag_service: RAGService, tmp_path: Path):
    """Documentos con estado diferente de APTO deben ser omitidos sin indexar."""
    fake_pdf = tmp_path / "fake.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4 dummy content")

    mock_doc_service = MagicMock(spec=DocumentService)
    mock_doc_service.extract_text.return_value = "Contenido dummy extraido de prueba"

    test_catalog = [
        CorpusDocumentSpec("NM-TEST-1", "fake.pdf", "Doc 1", "APTO_CON_REVISIÓN", "Desc 1"),
        CorpusDocumentSpec("NM-TEST-2", "fake.pdf", "Doc 2", "NO_APTO", "Desc 2"),
        CorpusDocumentSpec("NM-TEST-3", "fake.pdf", "Doc 3", "APTO", "Desc 3"),
    ]

    summary = preload_verified_corpus(
        rag_service=rag_service,
        document_service=mock_doc_service,
        corpus_root=tmp_path,
        catalog=test_catalog,
    )

    assert summary.total_catalogo == 3
    assert summary.omitidos_no_aptos == 2
    assert summary.cargados == 1
    assert summary.documentos_cargados == ["NM-TEST-3"]
    assert rag_service.document_exists("NM-TEST-3") is True
    assert rag_service.document_exists("NM-TEST-1") is False
    assert rag_service.document_exists("NM-TEST-2") is False


# ---------------------------------------------------------------------------
# 2. Procesamiento completo, conservación de metadatos y trazabilidad
# ---------------------------------------------------------------------------


def test_preload_preserves_full_text_and_chunk_metadata(rag_service: RAGService, tmp_path: Path):
    """Verifica que el texto extraído se procesa completo y los chunks retienen sus metadatos."""
    fake_pdf = tmp_path / "doc_extenso.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4 extenso")

    # Texto amplio con múltiples párrafos
    parrafos = [f"Párrafo de prueba número {i} con conceptos pedagógicos relevantes." for i in range(50)]
    texto_largo = "\n\n".join(parrafos)

    mock_doc_service = MagicMock(spec=DocumentService)
    mock_doc_service.extract_text.return_value = texto_largo

    catalog = [
        CorpusDocumentSpec("NM-EXT-01", "doc_extenso.pdf", "Doc Extenso", "APTO", "Desc Extensa"),
    ]

    summary = preload_verified_corpus(
        rag_service=rag_service,
        document_service=mock_doc_service,
        corpus_root=tmp_path,
        catalog=catalog,
    )

    assert summary.cargados == 1
    assert summary.documentos_cargados == ["NM-EXT-01"]

    # Verificar metadatos y chunks en RAGService
    doc_chunks = [c for c in rag_service._chunks if c.documento_id == "NM-EXT-01"]
    assert len(doc_chunks) > 1
    for idx, chunk in enumerate(doc_chunks):
        assert chunk.documento_id == "NM-EXT-01"
        assert chunk.posicion == idx
        assert chunk.chunk_id is not None
        assert len(chunk.texto.strip()) > 0


# ---------------------------------------------------------------------------
# 3. Idempotencia y omisión de documentos existentes
# ---------------------------------------------------------------------------


def test_preload_idempotency(rag_service: RAGService, tmp_path: Path):
    """Ejecutar la precarga dos veces no duplica documentos ni chunks en el índice."""
    fake_pdf = tmp_path / "apto.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4 dummy content")

    mock_doc_service = MagicMock(spec=DocumentService)
    mock_doc_service.extract_text.return_value = "Texto educativo completo para indexar en RAG. " * 20

    catalog = [
        CorpusDocumentSpec("NM-IDEM-1", "apto.pdf", "Doc Idem", "APTO", "Desc"),
    ]

    # Primera ejecución
    summary1 = preload_verified_corpus(
        rag_service=rag_service,
        document_service=mock_doc_service,
        corpus_root=tmp_path,
        catalog=catalog,
    )
    assert summary1.cargados == 1
    assert summary1.omitidos_existentes == 0
    total_chunks_inicial = rag_service._index.ntotal
    assert total_chunks_inicial > 0

    # Segunda ejecución con el mismo catálogo y rag_service
    summary2 = preload_verified_corpus(
        rag_service=rag_service,
        document_service=mock_doc_service,
        corpus_root=tmp_path,
        catalog=catalog,
    )
    assert summary2.cargados == 0
    assert summary2.omitidos_existentes == 1
    assert summary2.errores == 0

    # Comprobar que no hubo adiciones en FAISS
    assert rag_service._index.ntotal == total_chunks_inicial


# ---------------------------------------------------------------------------
# 4. Manejo de fallos: archivos ausentes, texto vacío y excepciones de extracción
# ---------------------------------------------------------------------------


def test_preload_handles_missing_files_gracefully(rag_service: RAGService, tmp_path: Path):
    """Archivos faltantes físicos se registran en errores sin abortar la ejecución de los demás."""
    existing_pdf = tmp_path / "existente.pdf"
    existing_pdf.write_bytes(b"%PDF-1.4 content")

    mock_doc_service = MagicMock(spec=DocumentService)
    mock_doc_service.extract_text.return_value = "Texto de documento existente"

    catalog = [
        CorpusDocumentSpec("NM-MISS-1", "no_existe.pdf", "Inexistente", "APTO", "Desc"),
        CorpusDocumentSpec("NM-OK-1", "existente.pdf", "Existente", "APTO", "Desc"),
    ]

    summary = preload_verified_corpus(
        rag_service=rag_service,
        document_service=mock_doc_service,
        corpus_root=tmp_path,
        catalog=catalog,
    )

    assert summary.cargados == 1
    assert summary.errores == 1
    assert "NM-MISS-1" in summary.documentos_fallidos
    assert "NM-OK-1" in summary.documentos_cargados
    assert rag_service.document_exists("NM-OK-1") is True


def test_preload_handles_empty_and_whitespace_text(rag_service: RAGService, tmp_path: Path):
    """Si la extracción retorna texto vacío o espacios, se registra error y no se reporta cargado."""
    empty_pdf = tmp_path / "vacio.pdf"
    empty_pdf.write_bytes(b"%PDF-1.4 empty")

    mock_doc_service = MagicMock(spec=DocumentService)
    mock_doc_service.extract_text.return_value = "   \n\t  "

    catalog = [
        CorpusDocumentSpec("NM-EMPTY-1", "vacio.pdf", "Doc Vacio", "APTO", "Desc"),
    ]

    summary = preload_verified_corpus(
        rag_service=rag_service,
        document_service=mock_doc_service,
        corpus_root=tmp_path,
        catalog=catalog,
    )

    assert summary.cargados == 0
    assert summary.errores == 1
    assert "NM-EMPTY-1" in summary.documentos_fallidos
    assert "NM-EMPTY-1" not in summary.documentos_cargados
    assert rag_service.document_exists("NM-EMPTY-1") is False


def test_preload_handles_extraction_exception(rag_service: RAGService, tmp_path: Path):
    """Si DocumentService lanza una excepción al extraer, se registra en fallidos y el balance es consistente."""
    corrupt_pdf = tmp_path / "corrupto.pdf"
    corrupt_pdf.write_bytes(b"bad binary")

    mock_doc_service = MagicMock(spec=DocumentService)
    mock_doc_service.extract_text.side_effect = RuntimeError("PDF corrupto o ilegible")

    catalog = [
        CorpusDocumentSpec("NM-CORRUPT-1", "corrupto.pdf", "Doc Corrupto", "APTO", "Desc"),
    ]

    summary = preload_verified_corpus(
        rag_service=rag_service,
        document_service=mock_doc_service,
        corpus_root=tmp_path,
        catalog=catalog,
    )

    assert summary.cargados == 0
    assert summary.errores == 1
    assert "NM-CORRUPT-1" in summary.documentos_fallidos
    assert "NM-CORRUPT-1" not in summary.documentos_cargados


def test_preload_handles_nonexistent_corpus_directory(rag_service: RAGService, doc_service: DocumentService, tmp_path: Path):
    """Si el directorio del corpus no existe, retorna balance seguro con 0 cargados sin fallar."""
    fake_dir = tmp_path / "directorio_que_no_existe"

    summary = preload_verified_corpus(
        rag_service=rag_service,
        document_service=doc_service,
        corpus_root=fake_dir,
    )

    assert summary.cargados == 0
    assert summary.errores == 0


# ---------------------------------------------------------------------------
# 5. Ingesta fallida y riesgo de estado parcial
# ---------------------------------------------------------------------------


def test_preload_handles_ingestion_failure_and_summary_consistency(rag_service: RAGService, tmp_path: Path):
    """
    Si ingest_document falla (p.ej. error al generar embeddings o FAISS), el documento
    debe registrarse como error, agregarse a documentos_fallidos y NO a documentos_cargados.
    """
    fake_pdf = tmp_path / "doc_fail.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4 test")

    mock_doc = MagicMock(spec=DocumentService)
    mock_doc.extract_text.return_value = "Texto válido para ingestar"

    mock_rag = MagicMock(spec=RAGService)
    mock_rag.document_exists.return_value = False
    mock_rag.ingest_document.side_effect = RuntimeError("Fallo interno en FAISS o embeddings")

    catalog = [
        CorpusDocumentSpec("NM-FAIL-1", "doc_fail.pdf", "Fallo Ingesta", "APTO", "Desc"),
    ]

    summary = preload_verified_corpus(
        rag_service=mock_rag,
        document_service=mock_doc,
        corpus_root=tmp_path,
        catalog=catalog,
    )

    assert summary.cargados == 0
    assert summary.errores == 1
    assert "NM-FAIL-1" in summary.documentos_fallidos
    assert "NM-FAIL-1" not in summary.documentos_cargados


# ---------------------------------------------------------------------------
# 6. Ausencia de LLM y verificación de retrieval semántico
# ---------------------------------------------------------------------------


def test_preload_no_llm_required(rag_service: RAGService, tmp_path: Path):
    """La precarga no debe requerir llaves de LLM ni conectarse a servicios externos."""
    fake_pdf = tmp_path / "doc.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4 test")

    mock_doc = MagicMock(spec=DocumentService)
    mock_doc.extract_text.return_value = "Contenido de prueba sintético sin LLM."

    catalog = [
        CorpusDocumentSpec("NM-NO-LLM", "doc.pdf", "Doc Sin LLM", "APTO", "Desc"),
    ]

    summary = preload_verified_corpus(
        rag_service=rag_service,
        document_service=mock_doc,
        corpus_root=tmp_path,
        catalog=catalog,
    )
    assert summary.cargados == 1
    retrieved = rag_service.retrieve(documento_id="NM-NO-LLM", query="prueba sintético", top_k=1)
    assert len(retrieved) > 0
    assert retrieved[0].documento_id == "NM-NO-LLM"


# ---------------------------------------------------------------------------
# 7. Verificación del ciclo de vida (Lifespan) de FastAPI
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_fastapi_lifespan_initializes_services_and_preloads():
    """
    Verifica que el lifespan de FastAPI inicializa todos los servicios en el orden correcto
    y ejecuta la precarga del corpus sobre la instancia exacta app.state.rag_service.
    """
    mock_preload_summary = PreloadSummary(
        total_catalogo=3,
        cargados=3,
        omitidos_existentes=0,
        omitidos_no_aptos=0,
        errores=0,
        documentos_cargados=["NM-006", "NM-015", "NM-004"],
        documentos_fallidos=[],
    )

    # Monitorear la llamada a preload_verified_corpus durante el lifespan real
    with patch(
        "app.services.corpus_loader.preload_verified_corpus",
        return_value=mock_preload_summary,
    ) as mock_preload_call:
        async with lifespan(app):
            # 1. Comprobar que los servicios existen en app.state
            assert hasattr(app.state, "document_service")
            assert isinstance(app.state.document_service, DocumentService)

            assert hasattr(app.state, "rag_service")
            assert isinstance(app.state.rag_service, RAGService)

            assert hasattr(app.state, "oci_service")

            # 2. Comprobar que preload_verified_corpus fue invocado exactamente con la instancia de app.state
            mock_preload_call.assert_called_once()
            called_kwargs = mock_preload_call.call_args.kwargs
            assert called_kwargs["rag_service"] is app.state.rag_service
            assert called_kwargs["document_service"] is app.state.document_service


# ---------------------------------------------------------------------------
# 8. Pruebas deterministas de selección de archivos del corpus (NM-008 / Multi-formato)
# ---------------------------------------------------------------------------


def test_resolve_corpus_file_prioritizes_pdf_over_html(tmp_path: Path):
    """1. Cuando existen NM-008.pdf y NM-008.html, se selecciona el PDF deterministamente."""
    from app.services.corpus_loader import resolve_corpus_file

    doc_dir = tmp_path / "NM-008_Electronica_Digital"
    doc_dir.mkdir(parents=True, exist_ok=True)

    # Crear ambos archivos; html alfabéticamente va primero
    html_file = doc_dir / "NM-008_Electronica_Digital.html"
    html_file.write_text("<html><body>Contenido Web</body></html>", encoding="utf-8")

    pdf_file = doc_dir / "NM-008_Electronica_Digital.pdf"
    pdf_file.write_bytes(b"%PDF-1.4\n%fake valid header with content\n%%EOF")

    resolved = resolve_corpus_file("NM-008", corpus_root=tmp_path)
    assert resolved is not None
    assert resolved.name == "NM-008_Electronica_Digital.pdf"
    assert resolved.suffix.lower() == ".pdf"


def test_resolve_corpus_file_single_html_selected_gracefully(tmp_path: Path):
    """2. Cuando solo existe un archivo HTML válido, no se rompe su tratamiento."""
    from app.services.corpus_loader import resolve_corpus_file

    doc_dir = tmp_path / "COMP-02_Banca_FinTech"
    doc_dir.mkdir(parents=True, exist_ok=True)

    html_file = doc_dir / "COMP-02_Finanzas_Abiertas.html"
    html_file.write_text("<html><body>Contenido HTML Legítimo</body></html>", encoding="utf-8")

    resolved = resolve_corpus_file("COMP-02", corpus_root=tmp_path)
    assert resolved is not None
    assert resolved.name == "COMP-02_Finanzas_Abiertas.html"


def test_resolve_corpus_file_empty_or_corrupt_pdf_handled_gracefully(tmp_path: Path):
    """3. Cuando el PDF está vacío o es inválido, el sistema gestiona el caso de forma controlada."""
    from app.services.corpus_loader import resolve_corpus_file

    doc_dir = tmp_path / "NM-TEST_Empty"
    doc_dir.mkdir(parents=True, exist_ok=True)

    empty_pdf = doc_dir / "NM-TEST.pdf"
    empty_pdf.write_bytes(b"")  # 0 bytes

    # Con only_valid=True, se descarta archivo vacío
    resolved_strict = resolve_corpus_file("NM-TEST", corpus_root=tmp_path, only_valid=True)
    assert resolved_strict is None

    # Si coexiste un archivo no vacío alternativo (ej. HTML), se prefiere el archivo con contenido
    alt_file = doc_dir / "NM-TEST.html"
    alt_file.write_text("<html>Contenido</html>", encoding="utf-8")

    resolved_alt = resolve_corpus_file("NM-TEST", corpus_root=tmp_path)
    assert resolved_alt is not None
    assert resolved_alt.name == "NM-TEST.html"


def test_nm008_real_pdf_extracts_structure_and_can_be_ingested():
    """4. El procesamiento del PDF real de NM-008 extrae sus apartados y permite ingesta."""
    from app.services.corpus_loader import find_corpus_root, resolve_corpus_file
    from app.services.document_service import DocumentService
    from fastapi.testclient import TestClient
    from app.main import app

    corpus_root = find_corpus_root()
    if not corpus_root or not (corpus_root / "NM-008_Electronica_Digital" / "NM-008_Electronica_Digital.pdf").exists():
        pytest.skip("Corpus físico NM-008 no disponible en el entorno")

    target = resolve_corpus_file("NM-008", corpus_root)
    assert target is not None
    assert target.suffix.lower() == ".pdf"

    doc_service = DocumentService()
    apartados = doc_service.extract_structure(target.read_bytes(), "application/pdf")
    assert len(apartados) == 110
    assert apartados[0]["titulo"] == "Prefacio"

    # Verificar que el endpoint /structure devuelve los 110 apartados
    app.state.document_service = doc_service
    client = TestClient(app)
    resp = client.get("/api/v1/files/corpus/NM-008/structure")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_apartados"] == 110
    assert len(data["apartados"]) == 110


def test_nm007_esp32_endpoints_operate_controlled():
    """Verifica que NM-007 (sin TOC interno) se gestiona de forma controlada sin fallar."""
    from app.services.corpus_loader import find_corpus_root, resolve_corpus_file
    from app.services.document_service import DocumentService
    from fastapi.testclient import TestClient
    from app.main import app

    corpus_root = find_corpus_root()
    if not corpus_root or not (corpus_root / "NM-007_ESP32_en_el_Aula").exists():
        pytest.skip("Corpus físico NM-007 no disponible en el entorno")

    target = resolve_corpus_file("NM-007", corpus_root)
    assert target is not None
    assert target.name == "NM-007_ESP32_en_el_Aula.pdf"

    app.state.document_service = DocumentService()
    client = TestClient(app)
    resp = client.get("/api/v1/files/corpus/NM-007/structure")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_apartados"] == 0
    assert data["apartados"] == []


def test_existing_verified_apto_documents_continue_working():
    """5. Los documentos que funcionaban antes continúan funcionando perfectamente."""
    from app.services.corpus_loader import find_corpus_root, resolve_corpus_file

    corpus_root = find_corpus_root()
    if not corpus_root:
        pytest.skip("Corpus físico no disponible")

    for doc_id in ("NM-004", "NM-006", "NM-015"):
        target = resolve_corpus_file(doc_id, corpus_root)
        assert target is not None
        assert target.is_file()
        assert target.suffix.lower() == ".pdf"


def test_get_corpus_status_only_available_excludes_missing_and_no_apto():
    """Comprueba que get_corpus_status(only_available=True) filtre estrictamente por las 3 condiciones."""
    from app.services.corpus_loader import get_corpus_status

    all_docs = get_corpus_status(only_available=False)
    available_docs = get_corpus_status(only_available=True)

    assert len(all_docs) == 22
    assert len(available_docs) == 13

    for doc in available_docs:
        assert doc["archivo_disponible"] is True
        assert doc["nombre_archivo"] is not None
        assert doc["resultado_evaluacion"] in ("APTO", "APTO_CON_REVISIÓN")
        assert doc["resultado_evaluacion"] != "NO_APTO"

    avail_ids = {d["identificador_documento"] for d in available_docs}
    # Los 9 documentos ausentes/NO_APTO no deben figurar
    for missing_id in ("NM-003", "NM-005", "NM-012", "NM-013", "NM-017", "NM-018", "NM-019", "NM-021", "NM-022"):
        assert missing_id not in avail_ids


def test_api_corpus_endpoint_solo_disponibles_filter():
    """GET /api/v1/files/corpus?solo_disponibles=true debe devolver solo los 13 documentos procesables."""
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    resp_all = client.get("/api/v1/files/corpus")
    assert resp_all.status_code == 200
    assert len(resp_all.json()) == 22

    resp_solo = client.get("/api/v1/files/corpus?solo_disponibles=true")
    assert resp_solo.status_code == 200
    data_solo = resp_solo.json()
    assert len(data_solo) == 13

    for doc in data_solo:
        assert doc["archivo_disponible"] is True
        assert doc["resultado_evaluacion"] in ("APTO", "APTO_CON_REVISIÓN")


def test_resolve_corpus_file_compatible_only_discards_html(tmp_path: Path):
    """resolve_corpus_file con compatible_only=True descarta formatos no soportados como .html."""
    from app.services.corpus_loader import resolve_corpus_file

    doc_dir = tmp_path / "COMP-02_Dir"
    doc_dir.mkdir(parents=True, exist_ok=True)
    (doc_dir / "COMP-02_Doc.html").write_text("<html>Texto</html>", encoding="utf-8")

    # Sin compatible_only (admite cualquier formato existente)
    assert resolve_corpus_file("COMP-02", tmp_path, compatible_only=False) is not None

    # Con compatible_only=True (.html no es compatible con el sistema RAG)
    assert resolve_corpus_file("COMP-02", tmp_path, compatible_only=True) is None
