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
import re
import unicodedata

import numpy as np

from app.core.exceptions import DocumentNotFoundError, NoRelevantSourcesError
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
        "ejemplo o accion concreta, resultado esperado. Incluye prerequisitos al inicio. "
        "Si la fuente corresponde a un concepto u oficio administrativo en instancia consultiva, "
        "explicita su alcance orientador no vinculante y distinguelo claramente de las circulares, "
        "leyes o decretos de caracter vinculante que cite."
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
        tema_o_pregunta: str | None = None,
    ) -> tuple[str, str]:
        """
        Construye el system_prompt y el user_prompt adaptados al perfil, formato y tema/pregunta.

        Args:
            chunks:          Lista de fragmentos del documento fuente recuperados por RAG.
            perfil:          Perfil del destinatario (valor string del enum PerfilDestinatario).
            formato:         Formato de salida (valor string del enum FormatoSalida).
            nicho:           Sector de negocio (valor string del enum Nicho).
            nivel:           Nivel de detalle (valor string del enum NivelDetalle).
            tema_o_pregunta: Tema o pregunta orientadora ingresada por el usuario (opcional).

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

        seccion_tema = ""
        if tema_o_pregunta and tema_o_pregunta.strip():
            seccion_tema = (
                f"\n\nTEMA O PREGUNTA ORIENTADORA DEL ESTUDIO:\n"
                f"El contenido debe enfocarse y responder específicamente a: '{tema_o_pregunta.strip()}'.\n"
                f"Aborda este tema o pregunta con prioridad pedagógica, manteniendo siempre la fundamentación documental."
            )

        system_prompt = (
            f"Eres un experto en diseno instruccional y comunicacion tecnica especializado "
            f"en el sector {nicho}.\n"
            f"Tu tarea es generar contenido educativo en formato '{formato}' adaptado a un "
            f"destinatario con perfil '{perfil}' con nivel de detalle '{nivel}'.{seccion_tema}\n\n"
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

        instruccion_usuario = "Genera el contenido educativo solicitado basandote exclusivamente en los fragmentos anteriores."
        if tema_o_pregunta and tema_o_pregunta.strip():
            instruccion_usuario = (
                f"Tema o pregunta orientadora: '{tema_o_pregunta.strip()}'.\n"
                f"Genera el contenido educativo enfocado en este tema/pregunta basándote exclusivamente en los fragmentos anteriores."
            )

        user_prompt = (
            "Fragmentos del documento fuente:\n"
            "---\n"
            f"{chunks_concatenados}\n"
            "---\n\n"
            f"{instruccion_usuario}"
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
        Genera contenido educativo adaptativo a partir de uno o varios documentos ingestados.

        Soporta dos modos de operación:
          - **Singular (legado):** ``request.documento_ids`` contiene un único ID.
          - **Múltiple (Estudio Focalizado):** ``request.documento_ids`` contiene
            varios IDs; los chunks de todos los documentos se fusionan y re-ordenan
            por score antes de construir el prompt.

        El validador Pydantic de :class:`AdaptacionRequest` garantiza que
        ``documento_ids`` siempre esté normalizado antes de llegar aquí.

        Flujo: RAG multi → prompt → LLM → parseo → score → OCI → respuesta.

        Args:
            request: Parámetros de la solicitud de adaptación.

        Returns:
            AdaptacionResponse con el contenido generado y todos los metadatos.

        Raises:
            DocumentNotFoundError:    Si ningún documento_id existe en el índice.
            NoRelevantSourcesError:   Si los documentos existen pero no hay chunks relevantes.
            LLMNotConfiguredError:    Si LLM_API_KEY está ausente o inválida.
            LLMGenerationError:       Si la llamada al LLM falla.
        """
        # documento_ids está siempre normalizado por el model_validator del schema
        doc_ids: list[str] = request.documento_ids  # type: ignore[assignment]

        # 1. Construir query semántica orientada por tema o parámetros
        tema_clean = (request.tema_o_pregunta or "").strip()
        if tema_clean:
            query = (
                f"{tema_clean} {request.nicho.value} {request.nivel_detalle.value} "
                f"{request.formato_salida.value}"
            )
        else:
            query = (
                f"{request.nicho.value} {request.nivel_detalle.value} "
                f"{request.formato_salida.value}"
            )
        logger.info(
            "generate_content: recuperando chunks para documento_ids=%s, query='%s'",
            doc_ids,
            query,
        )

        # 2. Recuperar chunks de todos los documentos seleccionados
        rag_top_k = getattr(getattr(self.rag, "_settings", None), "rag_top_k", 5)
        if hasattr(self.rag, "retrieve_multi") and callable(getattr(self.rag, "retrieve_multi")):
            res_multi = self.rag.retrieve_multi(
                query=query,
                documento_ids=doc_ids,
                top_k=rag_top_k,
            )
            if isinstance(res_multi, tuple) and len(res_multi) == 2:
                chunks, ids_invalidos = res_multi
            elif isinstance(res_multi, list):
                chunks, ids_invalidos = res_multi, []
            else:
                chunks, ids_invalidos = [], []
        else:
            chunks = self.rag.retrieve(
                query=query,
                documento_id=doc_ids[0],
                top_k=rag_top_k,
            )
            ids_invalidos = []

        if ids_invalidos:
            logger.warning(
                "generate_content: %d documento(s) no encontrado(s) en el índice: %s",
                len(ids_invalidos),
                ids_invalidos,
            )

        logger.info(
            "generate_content: %d chunks recuperados de %d documento(s)",
            len(chunks),
            len(doc_ids) - len(ids_invalidos),
        )

        # 3. Verificar que hay chunks para trabajar
        if not chunks:
            ids_validos_str = ", ".join(
                f"'{d}'" for d in doc_ids if d not in ids_invalidos
            )
            raise NoRelevantSourcesError(
                message="No se encontraron fragmentos relevantes en los documentos seleccionados.",
                detail=(
                    f"Los documentos {ids_validos_str} están indexados pero no "
                    "retornaron chunks para la consulta actual. "
                    "Verifica que el contenido de los documentos sea suficientemente extenso."
                ),
            )

        # 4. ID principal para campos de compatibilidad hacia atrás
        doc_id_principal = doc_ids[0]

        # 5. Construir prompts adaptados
        system_prompt, user_prompt = self._build_prompt(
            chunks=chunks,
            perfil=request.perfil_destinatario.value,
            formato=request.formato_salida.value,
            nicho=request.nicho.value,
            nivel=request.nivel_detalle.value,
            tema_o_pregunta=request.tema_o_pregunta,
        )

        # 6. Invocar el LLM
        telemetria = None
        tiene_telemetria = (
            hasattr(type(self.llm), "generate_with_telemetry")
            and callable(getattr(type(self.llm), "generate_with_telemetry"))
        ) or (
            hasattr(self.llm, "_mock_children")
            and "generate_with_telemetry" in getattr(self.llm, "_mock_children", {})
        )

        if tiene_telemetria:
            res = self.llm.generate_with_telemetry(user_prompt, system_prompt)
            if not (isinstance(res, tuple) and len(res) == 2):
                raise TypeError(
                    f"El método generate_with_telemetry debe retornar una tupla de 2 elementos "
                    f"(contenido, telemetria), pero retornó {type(res).__name__}."
                )
            contenido_raw, telemetria = res
        else:
            contenido_raw = self.llm.generate(user_prompt, system_prompt)

        logger.info(
            "generate_content: contenido generado (%d caracteres) para documento_ids=%s",
            len(contenido_raw),
            doc_ids,
        )

        # 7. Parsear contenido JSON para formatos estructurados
        contenido_adaptado = _parsear_contenido(contenido_raw, request.formato_salida.value)

        # 8. Calcular score de anclaje
        score = self._calculate_anclaje_score(contenido_raw, chunks)
        nivel_conf = self._nivel_confianza(score)
        logger.info(
            "generate_content: anclaje_fuente_score=%.4f, nivel_confianza='%s'",
            score,
            nivel_conf,
        )

        # 9. Subir artefacto a OCI (degradación elegante)
        artefacto = {
            "documento_ids": doc_ids,
            "documento_id": doc_id_principal,
            "tema_o_pregunta": request.tema_o_pregunta,
            "contenido": contenido_raw,
        }
        oci_result = self.oci.upload_artifact(artefacto, doc_id_principal)
        logger.info(
            "generate_content: OCI upload status='%s'",
            oci_result.status,
        )

        # 10. Metadatos educativos
        tiempo_estudio = _estimar_tiempo_estudio(contenido_raw, request.formato_salida.value)
        conceptos = _extraer_conceptos_clave(contenido_raw, chunks)

        # 11. Construir respuesta
        return AdaptacionResponse(
            status="ok",
            document_id=doc_id_principal,
            documento_ids=doc_ids,
            metadatos=Metadatos(
                documento_id=doc_id_principal,
                documento_ids=doc_ids,
                tema_o_pregunta=request.tema_o_pregunta,
                perfil_destinatario=request.perfil_destinatario,
                formato_salida=request.formato_salida,
                nicho=request.nicho,
                nivel_detalle=request.nivel_detalle,
                fragmentos_usados=len(chunks),
                tiempo_estimado_estudio_minutos=tiempo_estudio,
                conceptos_clave=conceptos,
                tokens_entrada=telemetria.tokens_entrada if telemetria else None,
                tokens_salida=telemetria.tokens_salida if telemetria else None,
                latencia_segundos=telemetria.latencia_total_segundos if telemetria else None,
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
                    documento_id=c.documento_id,
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


# ---------------------------------------------------------------------------
# Funciones auxiliares: metadatos educativos (QA-007)
# ---------------------------------------------------------------------------

def _estimar_tiempo_estudio(contenido_raw: str, formato: str) -> int:
    """
    Estima el tiempo de estudio en minutos a partir de la extension y formato del contenido.
    Basado en lectura analitica tecnica (~150 palabras/minuto), con minimo de 5 minutos
    y maximo de 60 minutos.
    """
    palabras = len(contenido_raw.split())
    if formato in ("quiz", "flashcards"):
        lineas_items = max(1, contenido_raw.count('"pregunta"') or contenido_raw.count("?"))
        return max(5, min(60, lineas_items * 2))
    minutos = max(5, round(palabras / 150))
    return min(60, minutos)


_STOPWORDS_CONCEPTOS = {
    "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "a", "al", "en",
    "para", "por", "con", "sin", "sobre", "entre", "tras", "durante", "mediante",
    "que", "como", "cual", "cuales", "donde", "cuando", "este", "esta", "estos", "estas",
    "ese", "esa", "esos", "esas", "aquel", "aquella", "aquello", "aquellos", "aquellas",
    "paso", "etapa", "fase", "parte", "nota", "ejemplo", "resumen", "tutorial", "guia",
    "introduccion", "conclusion", "objetivo", "prerrequisito", "prerrequisitos", "modulo",
    "tema", "titulo", "seccion", "contenido", "descripcion", "explicacion", "resultado",
    "accion", "proceso", "definicion", "termino", "terminos", "glosario", "documento",
    # Ordinales
    "primero", "primera", "primeros", "primeras",
    "segundo", "segunda", "segundos", "segundas",
    "tercero", "tercera", "terceros", "terceras",
    "cuarto", "cuarta", "cuartos", "cuartas",
    "quinto", "quinta", "quintos", "quintas",
    # Conectores discursivos, adverbios y marcadores
    "asi", "asimismo", "ademas", "tambien", "incluso", "entonces", "luego",
    "finalmente", "respecto", "conforme", "segun", "dado", "debido", "tanto",
    # Verbos existenciales, auxiliares y modales genéricos
    "existe", "existen", "cuenta", "cuentan", "debe", "deben", "puede", "pueden",
    "tiene", "tienen", "presenta", "presentan", "realiza", "realizan", "incluye", "incluyen",
    # Términos procedimentales / genéricos regulatorios o de interrogación
    "pregunta", "preguntas", "respuesta", "respuestas", "consulta", "consultas",
    "articulo", "articulos", "capitulo", "capitulos", "numeral", "numerales",
    "paragrafo", "paragrafos", "literal", "literales", "caso", "casos",
    # Términos bibliográficos, referencias de pie de página y metadatos de cita
    "disponible en", "disponible", "recuperado", "consultado", "fuente", "fuentes",
    "pagina", "paginas", "pag", "edicion", "editorial", "autor", "autores",
    "ibidem", "op cit", "enlace", "url", "sitio web", "sitio",
}


def _extraer_conceptos_clave(contenido_raw: str, chunks: list[ChunkMetadata]) -> list[str]:
    """
    Extrae conceptos clave verificables y pedagógicamente relevantes.

    Estrategia determinista jerárquica con complementación multinivel:
      1. Extrae términos destacados en negrita Markdown (`**término**`) en el texto generado.
      2. Si no alcanza el rango objetivo (< 4 conceptos), complementa con términos definidos
         explícitamente (`Término:` o `- Término:`).
      3. Si aún tiene < 4 conceptos, complementa con estructuras JSON (`concepto`, `titulo`, `tema`, `frente`).
      4. Si aún tiene < 4 conceptos, complementa recurriendo a fragmentos fuente (`chunks`):
         4a. Negritas en chunks fuente.
         4b. Definiciones explícitas en chunks fuente.
         4c. Términos técnicos compuestos o sustantivos capitalizados no aislados de inicio de frase.
      5. Normaliza y filtra palabras vacías (stopwords normalizadas sin tildes),
         longitud (< 3 o > 40), deduplica preservando orden, descarta subcadenas redundantes,
         descarta términos truncados incompletos y limita a un máximo de 8 conceptos.
      6. Si no existe contenido ni en la fuente ni en el texto generado, retorna lista vacía [].
    """
    conceptos: list[str] = []
    vistos: set[str] = set()

    def _normalizar(s: str) -> str:
        s_lower = s.lower().strip()
        return "".join(
            c for c in unicodedata.normalize("NFD", s_lower)
            if unicodedata.category(c) != "Mn"
        )

    # Precomputar stopwords normalizadas para chequeo uniforme sin tildes
    stopwords_norm = {_normalizar(w) for w in _STOPWORDS_CONCEPTOS}

    def _es_termino_valido(term: str) -> bool:
        t_clean = term.strip().strip(".:;,-\"'`()")
        if len(t_clean) < 3 or len(t_clean) > 40:
            return False
        t_norm = _normalizar(t_clean)
        if t_clean.lower() in _STOPWORDS_CONCEPTOS or t_norm in stopwords_norm:
            return False
        if t_clean.lower() in vistos or t_norm in vistos:
            return False
        if t_clean.startswith("http") or t_clean.isdigit():
            return False
        # Descartar si son solo números o palabras genéricas de paso (ej: "Paso 1")
        if re.match(r"^(?:paso|etapa|fase)\s*\d+$", t_norm):
            return False
        # Descartar términos truncados que terminan en partículas o abreviaturas (ej: "Circular Externa No")
        if re.search(r"\b(?:no|num|nro|del|de|la|el|en|y)\b$", t_clean, re.IGNORECASE):
            return False
        # Si es una sola palabra con solo números o caracteres especiales
        if not re.search(r"[a-zA-ZáéíóúÁÉÍÓÚñÑ]", t_clean):
            return False
        # Si todas las palabras que componen el término son stopwords individuales (ej: "Disponible en")
        palabras_norm = [_normalizar(w.strip(".:;,-\"'`()")) for w in t_clean.split()]
        if palabras_norm and all(w in stopwords_norm or w in _STOPWORDS_CONCEPTOS for w in palabras_norm):
            return False
        return True

    def _agregar_termino(term: str) -> bool:
        t_clean = term.strip().strip(".:;,-\"'`()")
        if _es_termino_valido(t_clean):
            t_norm = _normalizar(t_clean)

            # Deduplicación por subcadena / supercadena respecto a los conceptos existentes
            for idx, c_existente in enumerate(conceptos):
                c_exist_norm = _normalizar(c_existente)
                # Si el nuevo término es subcadena propia de uno ya existente que tiene más palabras (ej: "Contencioso Administrativo" dentro de "Código Contencioso Administrativo")
                if len(t_clean.split()) < len(c_existente.split()) and t_norm in c_exist_norm:
                    return False
                # Si el nuevo término es más específico y contiene por completo al ya existente (ej: llega "Código Contencioso Administrativo" y ya estaba "Contencioso Administrativo")
                if len(t_clean.split()) > len(c_existente.split()) and c_exist_norm in t_norm:
                    # Reemplazar el concepto menos específico por el más completo
                    vistos.discard(c_existente.lower())
                    vistos.discard(c_exist_norm)
                    conceptos[idx] = t_clean
                    vistos.add(t_clean.lower())
                    vistos.add(t_norm)
                    return len(conceptos) >= 8

            vistos.add(t_clean.lower())
            vistos.add(t_norm)
            conceptos.append(t_clean)
            return len(conceptos) >= 8
        return False

    # 1. Buscar términos resaltados en negrita tipo **concepto** en el contenido generado
    destacados = re.findall(r"\*\*([a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s_\-]{3,40})\*\*", contenido_raw)
    for d in destacados:
        if _agregar_termino(d):
            return conceptos

    # 2. Complementar con términos antes de dos puntos en listas o glosarios (ej: "- Fotosíntesis: ..." o "Cloroplastos: ...")
    if len(conceptos) < 4:
        lineas_definicion = re.findall(r"(?:^|\n)(?:[-*•]\s*)?([A-ZÁÉÍÓÚÑ][a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s_\-]{2,35})\s*:\s*[A-ZÁÉÍÓÚÑa-z0-9]", contenido_raw)
        for ld in lineas_definicion:
            if _agregar_termino(ld):
                return conceptos

    # 3. Complementar con estructuras JSON ("concepto", "titulo", "tema", etc.)
    if len(conceptos) < 4:
        claves_json = re.findall(r'"(?:concepto|titulo|tema|frente)":\s*"([^"]{3,40})"', contenido_raw, re.IGNORECASE)
        for c in claves_json:
            if _agregar_termino(c):
                return conceptos

    # 4. Complementar desde fragmentos fuente (chunks)
    if len(conceptos) < 4 and chunks:
        texto_fuente = " ".join(c.texto for c in chunks if getattr(c, "texto", None))
        # 4a. Buscar negritas en la fuente
        destacados_fuente = re.findall(r"\*\*([a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s_\-]{3,40})\*\*", texto_fuente)
        for df in destacados_fuente:
            if _agregar_termino(df):
                return conceptos

        # 4b. Buscar definiciones en la fuente (Termino: definicion)
        if len(conceptos) < 4:
            defs_fuente = re.findall(r"(?:^|\n)(?:[-*•]\s*)?([A-ZÁÉÍÓÚÑ][a-zA-ZáéíóúÁÉÍÓÚñÑ0-9\s_\-]{2,35})\s*:\s*", texto_fuente)
            for dff in defs_fuente:
                if _agregar_termino(dff):
                    return conceptos

        # 4c. Buscar términos técnicos en la fuente:
        # Primero compuestos multipalabra (ej: "Circular Externa", "Oficial de Cumplimiento", "Ciclo de Calvin")
        if len(conceptos) < 4:
            compuestos_fuente = re.findall(r"\b([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+(?:de\s+|del\s+)?[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)+)\b", texto_fuente)
            for cf in compuestos_fuente:
                if _agregar_termino(cf):
                    return conceptos

        # Segundo sustantivos técnicos individuales precedidos por minúscula (evita mayúsculas de inicio de frase)
        if len(conceptos) < 4:
            sustantivos_internos = re.findall(r"(?<=[a-záéíóúñ]\s)([A-ZÁÉÍÓÚÑ][a-záéíóúñ]{3,30})\b", texto_fuente)
            for si in sustantivos_internos:
                if _agregar_termino(si):
                    return conceptos

    return conceptos

