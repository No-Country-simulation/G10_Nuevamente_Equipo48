"""
Módulo de precarga del corpus documental validado para NuevaMente.

Carga automáticamente documentos clasificados como estrictamente APTO
al iniciar FastAPI, garantizando que el pipeline RAG cuente con conocimiento
base sin requerir intervención manual del usuario.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from app.services.document_service import DocumentService
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CorpusDocumentSpec:
    """Especificación de un documento apto del corpus."""
    documento_id: str
    ruta_relativa: str
    titulo: str
    estado_auditoria: str
    descripcion: str


# Catálogo estricto de documentos APTO verificados física y auditorialmente
VERIFIED_APTO_CORPUS: tuple[CorpusDocumentSpec, ...] = (
    CorpusDocumentSpec(
        documento_id="NM-006",
        ruta_relativa="NM-006_Manual_de_Ciberseguridad_OSC/NM-006_Manual_de_Ciberseguridad_OSC.pdf",
        titulo="Manual de Ciberseguridad para OSC",
        estado_auditoria="APTO",
        descripcion="Manual de ciberseguridad y buenas prácticas digitales para OSC.",
    ),
    CorpusDocumentSpec(
        documento_id="NM-015",
        ruta_relativa="NM-015_Como_funciona_la_energia/NM-015_Como_funciona_la_energia.pdf",
        titulo="Cómo funciona la energía",
        estado_auditoria="APTO",
        descripcion="Material educativo sobre fuentes, tipos y transformaciones de energía.",
    ),
    CorpusDocumentSpec(
        documento_id="NM-004",
        ruta_relativa="NM-004_Diseno_de_base_de_datos/NM-004_Diseno_de_base_de_datos.pdf",
        titulo="Diseño de Base de Datos",
        estado_auditoria="APTO",
        descripcion="Fundamentos y diseño conceptual, lógico y relacional de bases de datos.",
    ),
)


@dataclass
class PreloadSummary:
    """Resumen de la operación de precarga."""
    total_catalogo: int
    cargados: int
    omitidos_existentes: int
    omitidos_no_aptos: int
    errores: int
    documentos_cargados: list[str]
    documentos_fallidos: list[str]


def find_corpus_root() -> Path | None:
    """
    Localiza la ruta del directorio de documentos del corpus verificado.
    Busca recursivamente hacia arriba desde la ubicación actual.
    """
    repo_root = Path(__file__).resolve().parents[4]
    candidatos = [
        # Ruta directa relativa a la raíz del repositorio
        repo_root / "_revision_corpus_fase05" / "documentos",
        # Rutas relativas al directorio de trabajo actual
        Path.cwd() / "_revision_corpus_fase05" / "documentos",
        Path.cwd().parent / "_revision_corpus_fase05" / "documentos",
        Path.cwd().parent.parent / "_revision_corpus_fase05" / "documentos",
    ]
    for ruta in candidatos:
        if ruta.is_dir():
            return ruta
    return None


def preload_verified_corpus(
    rag_service: RAGService,
    document_service: DocumentService,
    corpus_root: Path | None = None,
    catalog: Sequence[CorpusDocumentSpec] = VERIFIED_APTO_CORPUS,
) -> PreloadSummary:
    """
    Precarga los documentos APTO del corpus en RAGService de forma idempotente.

    Args:
        rag_service: Instancia activa de RAGService donde se indexarán los chunks.
        document_service: Instancia de DocumentService para extracción de texto.
        corpus_root: Directorio donde residen los PDFs. Si es None, se busca automáticamente.
        catalog: Lista o tupla de CorpusDocumentSpec a procesar.

    Returns:
        PreloadSummary con el balance de documentos procesados.
    """
    summary = PreloadSummary(
        total_catalogo=len(catalog),
        cargados=0,
        omitidos_existentes=0,
        omitidos_no_aptos=0,
        errores=0,
        documentos_cargados=[],
        documentos_fallidos=[],
    )

    if corpus_root is None:
        corpus_root = find_corpus_root()

    if corpus_root is None or not corpus_root.is_dir():
        logger.warning(
            "Directorio de corpus verificado no encontrado (%s). Omitiendo precarga de inicio.",
            corpus_root,
        )
        return summary

    for spec in catalog:
        # 1. Filtro estricto: solo APTO
        if spec.estado_auditoria != "APTO":
            logger.info("Omitiendo documento '%s' porque su estado es '%s'.", spec.documento_id, spec.estado_auditoria)
            summary.omitidos_no_aptos += 1
            continue

        # 2. Idempotencia: no reprocesar si ya existe en FAISS / metadatos
        if rag_service.document_exists(spec.documento_id):
            logger.info("Documento '%s' ya presente en RAGService. Omitiendo duplicación.", spec.documento_id)
            summary.omitidos_existentes += 1
            continue

        pdf_path = corpus_root / spec.ruta_relativa
        if not pdf_path.is_file():
            logger.error("Archivo físico no encontrado para '%s': %s", spec.documento_id, pdf_path)
            summary.errores += 1
            summary.documentos_fallidos.append(spec.documento_id)
            continue

        try:
            logger.info("Precargando documento '%s' (%s)...", spec.documento_id, spec.ruta_relativa)
            content_bytes = pdf_path.read_bytes()
            texto_completo = document_service.extract_text(
                file_bytes=content_bytes,
                mime_type="application/pdf",
            )

            if not texto_completo.strip():
                logger.warning("El documento '%s' no contiene texto extraíble.", spec.documento_id)
                summary.errores += 1
                summary.documentos_fallidos.append(spec.documento_id)
                continue

            num_chunks = rag_service.ingest_document(
                text=texto_completo,
                documento_id=spec.documento_id,
            )

            summary.cargados += 1
            summary.documentos_cargados.append(spec.documento_id)
            logger.info(
                "Documento '%s' precargado exitosamente con %d chunks (%d caracteres).",
                spec.documento_id,
                num_chunks,
                len(texto_completo),
            )

        except Exception as exc:
            logger.error("Error al precargar '%s': %s", spec.documento_id, exc, exc_info=True)
            summary.errores += 1
            summary.documentos_fallidos.append(spec.documento_id)

    logger.info(
        "Precarga de corpus finalizada: %d cargados, %d existentes, %d no aptos, %d errores.",
        summary.cargados,
        summary.omitidos_existentes,
        summary.omitidos_no_aptos,
        summary.errores,
    )
    return summary


def get_corpus_status(rag_service: RAGService | None = None) -> list[dict]:
    """
    Retorna el estado consolidado de los documentos del inventario oficial de Data Analytics,
    indicando para cada uno si está disponible físicamente, su aptitud y si se encuentra
    actualmente indexado en el motor RAG.
    """
    import csv

    corpus_root = find_corpus_root()
    repo_root = Path(__file__).resolve().parents[4]
    csv_candidates = [
        repo_root / "data_analyst" / "inventario" / "inventario_corpus.csv",
        Path.cwd() / "data_analyst" / "inventario" / "inventario_corpus.csv",
        Path.cwd().parent / "data_analyst" / "inventario" / "inventario_corpus.csv",
        Path.cwd().parent.parent / "data_analyst" / "inventario" / "inventario_corpus.csv",
    ]

    inventory_rows: list[dict] = []
    for csv_path in csv_candidates:
        if csv_path.is_file():
            try:
                with open(csv_path, encoding="utf-8-sig") as f:
                    inventory_rows = list(csv.DictReader(f))
                break
            except Exception as exc:
                logger.warning("Error leyendo inventario CSV %s: %s", csv_path, exc)

    indexed_docs = rag_service.list_indexed_documents() if rag_service else {}

    results = []
    for row in inventory_rows:
        doc_id = row.get("identificador_documento", "").strip()
        titulo = row.get("titulo", "").strip()
        eval_res = row.get("resultado_evaluacion", "PENDIENTE").strip()
        licencia = row.get("licencia", "No especificada").strip()
        fuente = row.get("fuente", "").strip()
        dominio = row.get("dominio", "General").strip()
        tema = row.get("tema", "").strip()
        descripcion = row.get("descripcion", "").strip()

        # Determinar existencia física del archivo
        archivo_fisico = False
        ruta_archivo = None
        if corpus_root and corpus_root.is_dir():
            matches = list(corpus_root.glob(f"{doc_id}*/*.*"))
            # Filtrar directorios o archivos git
            file_matches = [m for m in matches if m.is_file() and not m.name.startswith(".")]
            if file_matches:
                archivo_fisico = True
                ruta_archivo = str(file_matches[0].name)

        chunks_count = indexed_docs.get(doc_id, 0)
        esta_procesado = chunks_count > 0

        # Estado del documento
        if esta_procesado:
            estado_flujo = "PROCESADO"
        elif archivo_fisico and eval_res == "APTO":
            estado_flujo = "DISPONIBLE_APTO"
        elif archivo_fisico:
            estado_flujo = f"DISPONIBLE_{eval_res}"
        else:
            estado_flujo = f"REGISTRADO_{eval_res}"

        results.append({
            "identificador_documento": doc_id,
            "titulo": titulo,
            "dominio": dominio,
            "tema": tema,
            "descripcion": descripcion,
            "resultado_evaluacion": eval_res,
            "licencia": licencia,
            "fuente": fuente,
            "archivo_disponible": archivo_fisico,
            "nombre_archivo": ruta_archivo,
            "esta_procesado": esta_procesado,
            "chunks_indexados": chunks_count,
            "estado_flujo": estado_flujo,
        })

    return results
