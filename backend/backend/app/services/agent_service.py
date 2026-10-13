"""
Agent Service - NuevaMente Backend.

Responsabilidad: Orquestacion del flujo completo de generacion de contenido educativo adaptativo.

Flujo:
  1. Verificar existencia del documento en el indice RAG.
  2. Recuperar chunks relevantes mediante busqueda semantica.
  3. Construir los prompts adaptados al perfil y formato solicitados.
  4. Invocar el LLM para generar el contenido educativo.
  5. Intentar parsear el contenido como JSON (solo para flashcards y quiz).
  6. Calcular el anclaje_fuente_score como evaluacion pedagogica automatica.
  7. Subir el artefacto a OCI Object Storage (con degradacion elegante).
  8. Construir y retornar la respuesta completa (AdaptacionResponse).
"""

from __future__ import annotations

import json
import logging

import numpy as np

from app.core.exceptions import DocumentNotFoundError
from app.schemas.adaptacion import (
    AdaptacionRequest,
    AdaptacionResponse,
    AlmacenamientoOCI,
    EvaluacionCalidad,
    FuenteFragmento,
    Metadatos,
)
from app.services.llm_service import LLMService
from app.services.oci_service import OCIService
from app.services.rag_service import ChunkMetadata, RAGService

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Instrucciones por perfil de destinatario
# ---------------------------------------------------------------------------

_INSTRUCCIONES_PERFIL: dict[str, str] = {
    "principiante": (
        "Explica con analogias simples, evita jerga tecnica, usa ejemplos cotidianos. "
        "Define todos los terminos tecnicos que debas mencionar."
    ),
    "junior": (
        "Explica el concepto con ejemplos de codigo simples y referencias a buenas practicas basicas. "
        "Asume conocimiento basico de programacion."
    ),
    "lider_tecnico": (
        "Asume experiencia tecnica solida, enfocate en decisiones de diseno, "
        "trade-offs y consideraciones de arquitectura."
    ),
    "ejecutivo": (
        "Usa lenguaje de negocio, enfocate en impacto, riesgos y valor para la organizacion. "
        "Evita detalles tecnicos de implementacion."
    ),
}

# ---------------------------------------------------------------------------
# Instrucciones por formato de salida
# ---------------------------------------------------------------------------

_INSTRUCCIONES_FORMATO: dict[str, str] = {
    "tutorial": (
        "Estructura el contenido como pasos numerados con: titulo del paso, explicacion, "
        "ejemplo o accion concreta, resultado esperado. Incluye prerequisitos al inicio."
    ),
    "flashcards": (
        "Genera una lista JSON de tarjetas con estructura: "
        '[{"pregunta": "...", "respuesta": "..."}]. '
        "Genera entre 5 y 15 tarjetas."
    ),
    "quiz": (
        "Genera una lista JSON de preguntas con estructura: "
        '[{"pregunta": "...", "opciones": ["A", "B", "C", "D"], '
        '"respuesta_correcta": "A", "justificacion": "..."}]. '
        "Genera entre 5 y 10 preguntas."
    ),
    "resumen_ejecutivo": (
        "Estructura el contenido en: contexto (1-2 parrafos), puntos clave (3-5 bullets), "
        "recomendaciones (1-3 bullets). Maximo 300 palabras."
    ),
    "guion_clase": (
        "Estructura como: introduccion (gancho de 2 min), desarrollo por secciones "
        "(5-7 min cada una), actividad/pregunta de reflexion, cierre con resumen de puntos clave."
    ),
}

# Formatos cuya respuesta se intenta parsear como JSON estructurado
_FORMATOS_JSON = {"flashcards", "quiz"}


class AgentService:
    """
    Orquestador del flujo de generacion de contenido educativo adaptativo.

    Coordina el RAG Service (recuperacion de contexto), el LLM Service
    (generacion de texto) y el OCI Service (almacenamiento de artefactos)
    para producir artefactos pedagogicos personalizados a partir de un
    documento previamente ingestado.
    """

    def __init__(self, rag: RAGService, llm: LLMService, oci: OCIService) -> None:
        """
        Inicializa el Agent Service con los servicios dependientes.

        Args:
            rag: Servicio de recuperacion aumentada por generacion.
            llm: Servicio de abstraccion sobre modelos LLM.
            oci: Servicio de almacenamiento en OCI Object Storage.
        """
        self.rag = rag
        self.llm = llm
        self.oci = oci

    # ------------------------------------------------------------------
    # _build_prompt - construccion de prompts adaptados
    # ------------------------------------------------------------------

    def _build_prompt(
        self,
        chunks: list[ChunkMetadata],
        perfil: str,
        formato: str,
        nicho: str,
        nivel: str,
    ) -> tuple[str, str]:
        """
        Construye el system_prompt y el user_prompt adaptados al perfil y formato.

        Args:
            chunks:  Lista de fragmentos del documento fuente recuperados por RAG.
            perfil:  Perfil del destinatario (valor string del enum PerfilDestinatario).
            formato: Formato de salida (valor string del enum FormatoSalida).
            nicho:   Sector de negocio (valor string del enum Nicho).
            nivel:   Nivel de detalle (valor string del enum NivelDetalle).

        Returns:
            Tupla (system_prompt, user_prompt) listos para enviar al LLM.
        """
        instruccion_perfil = _INSTRUCCIONES_PERFIL.get(
            perfil,
            "Adapta el contenido al nivel del destinatario.",
        )
        instruccion_formato = _INSTRUCCIONES_FORMATO.get(
            formato,
            "Estructura el contenido de manera clara y organizada.",
        )

        system_prompt = (
            f"Eres un experto en diseno instruccional y comunicacion tecnica especializado "
            f"en el sector {nicho}.\n"
            f"Tu tarea es generar contenido educativo en formato '{formato}' adaptado a un "
            f"destinatario con perfil '{perfil}' con nivel de detalle '{nivel}'.\n\n"
            f"Instrucciones de adaptacion para perfil {perfil}:\n"
            f"{instruccion_perfil}\n\n"
            f"Instrucciones de formato para {formato}:\n"
            f"{instruccion_formato}\n\n"
            f"IMPORTANTE: Basa tu respuesta EXCLUSIVAMENTE en los fragmentos del documento "
            f"fuente proporcionados.\n"
            f"Si la informacion solicitada no esta en los fragmentos, indicalo claramente.\n"
            f"No inventes informacion que no este en las fuentes."
        )

        # Concatenar los fragmentos numerados para el contexto del usuario
        chunks_concatenados = "\n\n".join(
            f"[Fragmento {i + 1}]\n{c.texto}" for i, c in enumerate(chunks)
        )

        user_prompt = (
            "Fragmentos del documento fuente:\n"
            "---\n"
            f"{chunks_concatenados}\n"
            "---\n\n"
            "Genera el contenido educativo solicitado basandote exclusivamente en los "
            "fragmentos anteriores."
        )

        return system_prompt, user_prompt

    # ------------------------------------------------------------------
    # _calculate_anclaje_score - evaluacion pedagogica automatica
    # ------------------------------------------------------------------

    def _calculate_anclaje_score(
        self,
        contenido_generado: str,
        source_chunks: list[ChunkMetadata],
    ) -> float:
        """
        Calcula el anclaje_fuente_score como similitud coseno promedio entre
        el embedding del contenido generado y los embeddings de los chunks fuente.

        Un score cercano a 1.0 indica que el contenido esta firmemente anclado
        en las fuentes; cercano a 0.0 sugiere posible alucinacion del LLM.

        Algoritmo:
          1. Generar embedding del contenido generado — shape (dim,).
          2. Generar embeddings de los chunks fuente — shape (k, dim).
          3. Calcular similitudes coseno: emb_chunks @ emb_contenido — shape (k,).
             (Los vectores estan normalizados L2, por lo que el producto interno
             equivale a la similitud coseno.)
          4. Calcular el promedio y garantizar el rango [0.0, 1.0].

        Args:
            contenido_generado: Texto del contenido educativo producido por el LLM.
            source_chunks:      Fragmentos del documento fuente utilizados como contexto.

        Returns:
            Float en el rango cerrado [0.0, 1.0].
        """
        if not source_chunks:
            logger.warning(
                "_calculate_anclaje_score: sin chunks fuente; retornando score=0.0"
            )
            return 0.0

        # Embedding del contenido generado — shape (dim,)
        emb_contenido = self.rag.generate_embeddings([contenido_generado])[0]

        # Embeddings de los chunks fuente — shape (k, dim)
        source_texts = [c.texto for c in source_chunks]
        emb_chunks = self.rag.generate_embeddings(source_texts)

        # Similitudes coseno: producto interno de vectores normalizados L2 — shape (k,)
        similarities = emb_chunks @ emb_contenido

        # Promedio de similitudes, garantizado en [0.0, 1.0]
        raw_score = float(np.mean(similarities))
        return max(0.0, min(1.0, raw_score))

    # ------------------------------------------------------------------
    # _nivel_confianza - clasificacion cualitativa del score
    # ------------------------------------------------------------------

    def _nivel_confianza(self, score: float) -> str:
        """
        Convierte el anclaje_fuente_score numerico en una etiqueta cualitativa.

        Args:
            score: Valor float en [0.0, 1.0].

        Returns:
            "alto" si score >= 0.7, "medio" si score >= 0.4, "bajo" si score < 0.4.
        """
        if score >= 0.7:
            return "alto"
        elif score >= 0.4:
            return "medio"
        return "bajo"

    # ------------------------------------------------------------------
    # generate_content - flujo principal de orquestacion
    # ------------------------------------------------------------------

    def generate_content(self, request: AdaptacionRequest) -> AdaptacionResponse:
        """
        Genera contenido educativo adaptativo a partir de un documento ingestado.

        Orquesta el flujo completo: RAG -> prompt -> LLM -> parseo -> score -> OCI -> respuesta.

        Args:
            request: Parametros de la solicitud de adaptacion (AdaptacionRequest).

        Returns:
            AdaptacionResponse con el contenido generado y todos los metadatos.

        Raises:
            DocumentNotFoundError: Si el documento_id no existe en el indice.
            LLMNotConfiguredError: Si LLM_API_KEY esta ausente o invalida.
            LLMGenerationError:    Si la llamada al LLM falla.
        """
        # 1. Verificar que el documento existe en el indice RAG
        if not self.rag.document_exists(request.documento_id):
            raise DocumentNotFoundError(
                message="El documento especificado no existe.",
                detail=(
                    f"No se encontro ningun chunk indexado para documento_id="
                    f"'{request.documento_id}'. "
                    f"Verifica que el documento fue cargado correctamente."
                ),
            )

        # 2. Construir query semantica que orienta la recuperacion de chunks
        query = (
            f"{request.nicho.value} {request.nivel_detalle.value} "
            f"{request.formato_salida.value}"
        )
        logger.info(
            "generate_content: recuperando chunks para documento_id=%s, query='%s'",
            request.documento_id,
            query,
        )

        # 3. Recuperar los chunks mas relevantes del documento
        chunks = self.rag.retrieve(
            query=query,
            documento_id=request.documento_id,
            top_k=self.rag._settings.rag_top_k,
        )
        logger.info(
            "generate_content: %d chunks recuperados para documento_id=%s",
            len(chunks),
            request.documento_id,
        )

        # 4. Construir los prompts adaptados al perfil, formato, nicho y nivel
        system_prompt, user_prompt = self._build_prompt(
            chunks=chunks,
            perfil=request.perfil_destinatario.value,
            formato=request.formato_salida.value,
            nicho=request.nicho.value,
            nivel=request.nivel_detalle.value,
        )

        # 5. Invocar el LLM (puede lanzar LLMNotConfiguredError o LLMGenerationError)
        contenido_raw = self.llm.generate(user_prompt, system_prompt)
        logger.info(
            "generate_content: contenido generado (%d caracteres) para documento_id=%s",
            len(contenido_raw),
            request.documento_id,
        )

        # 6. Intentar parsear el contenido como JSON para formatos estructurados
        contenido_adaptado = _parsear_contenido(contenido_raw, request.formato_salida.value)

        # 7. Calcular el score de anclaje a las fuentes
        score = self._calculate_anclaje_score(contenido_raw, chunks)

        # 8. Calcular el nivel de confianza cualitativo
        nivel_conf = self._nivel_confianza(score)
        logger.info(
            "generate_content: anclaje_fuente_score=%.4f, nivel_confianza='%s'",
            score,
            nivel_conf,
        )

        # 9. Subir el artefacto a OCI (con degradacion elegante ante fallos)
        artefacto = {
            "documento_id": request.documento_id,
            "contenido": contenido_raw,
        }
        oci_result = self.oci.upload_artifact(artefacto, request.documento_id)
        logger.info(
            "generate_content: OCI upload status='%s' para documento_id=%s",
            oci_result.status,
            request.documento_id,
        )

        # 10. Construir y retornar la respuesta completa
        return AdaptacionResponse(
            status="ok",
            document_id=request.documento_id,
            metadatos=Metadatos(
                documento_id=request.documento_id,
                perfil_destinatario=request.perfil_destinatario,
                formato_salida=request.formato_salida,
                nicho=request.nicho,
                nivel_detalle=request.nivel_detalle,
                fragmentos_usados=len(chunks),
            ),
            contenido_adaptado=contenido_adaptado,
            evaluacion_calidad=EvaluacionCalidad(
                anclaje_fuente_score=score,
                fragmentos_evaluados=len(chunks),
                nivel_confianza=nivel_conf,
            ),
            fuentes=[
                FuenteFragmento(
                    chunk_id=c.chunk_id,
                    texto=c.texto,
                    posicion=c.posicion,
                    score_relevancia=min(1.0, max(0.0, c.score)),
                )
                for c in chunks
            ],
            almacenamiento_oci=AlmacenamientoOCI(
                status_upload=oci_result.status,
                url_objeto=oci_result.url_objeto,
                detalle=oci_result.detalle,
            ),
        )


# ---------------------------------------------------------------------------
# Funcion auxiliar: parseo de contenido JSON estructurado
# ---------------------------------------------------------------------------

def _parsear_contenido(contenido_raw: str, formato: str):
    """
    Intenta parsear el contenido generado como JSON para formatos estructurados.

    Solo aplica para 'flashcards' y 'quiz'. Para otros formatos retorna el
    string sin modificar.

    El LLM puede devolver el JSON envuelto en un bloque de codigo Markdown
    (triple backtick json ... triple backtick), por lo que se intenta extraer
    el JSON antes de parsear.

    Args:
        contenido_raw: Texto bruto retornado por el LLM.
        formato:       Nombre del formato de salida (string del enum FormatoSalida).

    Returns:
        Objeto Python (list o dict) si el parseo fue exitoso para formatos JSON;
        string original en caso contrario o para formatos que no usan JSON.
    """
    if formato not in _FORMATOS_JSON:
        return contenido_raw

    # Intentar extraer JSON de un posible bloque de codigo Markdown
    texto_para_parsear = _extraer_json_de_markdown(contenido_raw)

    try:
        return json.loads(texto_para_parsear)
    except (json.JSONDecodeError, ValueError):
        logger.warning(
            "_parsear_contenido: no se pudo parsear como JSON para formato='%s'; "
            "retornando como string.",
            formato,
        )
        return contenido_raw


def _extraer_json_de_markdown(texto: str) -> str:
    """
    Extrae el contenido JSON de un bloque de codigo Markdown si esta presente.

    Los LLM frecuentemente envuelven respuestas JSON en bloques de codigo con
    triple backtick. Si no se detecta este patron, retorna el texto original.

    Args:
        texto: String bruto que puede contener un bloque de codigo Markdown.

    Returns:
        El contenido dentro del bloque de codigo, o el texto original.
    """
    stripped = texto.strip()

    # Detectar apertura de bloque de codigo con o sin lenguaje especificado
    for fence in ("```json", "```"):
        if stripped.startswith(fence):
            # Encontrar el primer salto de linea tras la apertura del bloque
            newline_pos = stripped.find("\n", len(fence) - 1)
            if newline_pos == -1:
                continue
            inicio_contenido = newline_pos + 1
            # Encontrar el cierre del bloque (ultima ocurrencia de ```)
            cierre = stripped.rfind("```")
            if cierre > inicio_contenido:
                return stripped[inicio_contenido:cierre].strip()

    return texto
