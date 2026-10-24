"""
Schemas Pydantic para el endpoint de adaptación de contenido educativo.

Define los modelos de entrada y salida del flujo POST /api/v1/adaptacion,
incluyendo los enums de valores permitidos y todos los sub-modelos del
cuerpo de respuesta.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# Enums — conjuntos de valores permitidos para los campos del request
# ---------------------------------------------------------------------------


class PerfilDestinatario(str, Enum):
    """Perfil del destinatario del contenido educativo generado."""

    principiante = "principiante"
    junior = "junior"
    lider_tecnico = "lider_tecnico"
    ejecutivo = "ejecutivo"


class FormatoSalida(str, Enum):
    """Formato en el que se debe estructurar el contenido generado."""

    tutorial = "tutorial"
    flashcards = "flashcards"
    quiz = "quiz"
    resumen_ejecutivo = "resumen_ejecutivo"
    guion_clase = "guion_clase"


class Nicho(str, Enum):
    """Sector de negocio o dominio al que se adapta el contenido."""

    fintech = "fintech"
    salud = "salud"
    ecommerce = "ecommerce"
    general = "general"


class NivelDetalle(str, Enum):
    """Nivel de profundidad técnica del contenido generado."""

    didactico = "didactico"
    intermedio = "intermedio"
    tecnico = "tecnico"


# ---------------------------------------------------------------------------
# Request — modelo de entrada del endpoint
# ---------------------------------------------------------------------------


class AdaptacionRequest(BaseModel):
    """
    Parámetros requeridos para generar contenido educativo adaptativo.

    ## Selección de documentos

    El sistema soporta dos modos de selección, compatibles entre sí:

    - **Modo singular (legado):** se envía `documento_id` (string).  El campo se
      trata internamente como si `documento_ids` fuera `[documento_id]`.
    - **Modo múltiple (Estudio Focalizado):** se envía `documento_ids` (lista de
      strings).  Permite recuperar contexto de varios documentos a la vez.

    Si se envían ambos campos, `documento_ids` tiene precedencia.
    Al menos uno de los dos campos debe estar presente y no vacío.
    """

    documento_id: str | None = Field(
        default=None,
        min_length=1,
        description=(
            "ID único del documento previamente cargado en el sistema. "
            "Campo legado — se convierte internamente a documento_ids=[documento_id]. "
            "Si se proporciona documento_ids, este campo es ignorado."
        ),
    )
    documento_ids: list[str] | None = Field(
        default=None,
        description=(
            "Lista de IDs de documentos para Estudio Focalizado. "
            "Cada elemento debe ser un ID previamente ingestado mediante "
            "POST /api/v1/files/upload. "
            "Si se proporciona, tiene precedencia sobre documento_id. "
            "La lista no puede estar vacía ni contener solo cadenas en blanco."
        ),
    )
    perfil_destinatario: PerfilDestinatario = Field(
        ...,
        description="Perfil del destinatario que recibirá el contenido adaptado.",
    )
    formato_salida: FormatoSalida = Field(
        ...,
        description="Formato de presentación del contenido educativo generado.",
    )
    nicho: Nicho = Field(
        ...,
        description="Sector o dominio de negocio al que se contextualiza el contenido.",
    )
    nivel_detalle: NivelDetalle = Field(
        ...,
        description="Nivel de profundidad técnica esperado en el contenido generado.",
    )
    tema_o_pregunta: str | None = Field(
        default=None,
        max_length=500,
        description="Tema específico o pregunta orientadora que guía el estudio focalizado.",
    )
    apartados: list[str] | None = Field(
        default=None,
        description="Lista de apartados, títulos o subtítulos seleccionados para enfocar el estudio.",
    )

    @model_validator(mode="after")
    def _resolver_documento_ids(self) -> "AdaptacionRequest":
        """
        Reconcilia documento_id y documento_ids en una única lista normalizada,
        valida la restricción de 1 a 3 documentos y limpia el campo tema_o_pregunta y apartados.
        """
        ids = self.documento_ids
        singular = self.documento_id

        # Limpiar tema_o_pregunta si viene con espacios
        if self.tema_o_pregunta is not None:
            t_clean = self.tema_o_pregunta.strip()
            self.tema_o_pregunta = t_clean if t_clean else None

        # Limpiar apartados si viene lista
        if self.apartados is not None:
            ap_limpios = [a.strip() for a in self.apartados if a and a.strip()]
            self.apartados = ap_limpios if ap_limpios else None

        # Caso 1: documento_ids presente
        if ids is not None:
            ids_limpios = [d.strip() for d in ids if d and d.strip()]
            if not ids_limpios:
                raise ValueError(
                    "documento_ids no puede estar vacío ni contener solo cadenas en blanco."
                )
            if len(ids_limpios) > 3:
                raise ValueError(
                    "El Estudio Focalizado permite seleccionar entre 1 y 3 documentos como máximo."
                )
            self.documento_ids = ids_limpios
            return self

        # Caso 2: solo documento_id
        if singular and singular.strip():
            self.documento_ids = [singular.strip()]
            return self

        # Caso 3: ninguno
        raise ValueError(
            "Debe proporcionarse al menos uno de los campos: "
            "'documento_id' o 'documento_ids'."
        )


# ---------------------------------------------------------------------------
# Sub-modelos de respuesta
# ---------------------------------------------------------------------------


class FuenteFragmento(BaseModel):
    """
    Fragmento del documento fuente utilizado para generar el contenido.

    Incluye el documento_id del fragmento para trazabilidad en modo
    de selección múltiple, y la puntuación de relevancia semántica
    asignada durante la recuperación del índice FAISS.
    """

    chunk_id: str = Field(..., description="Identificador único del fragmento (UUID).")
    documento_id: str = Field(
        default="",
        description="ID del documento al que pertenece este fragmento.",
    )
    texto: str = Field(..., description="Texto del fragmento fuente.")
    posicion: int = Field(
        ..., description="Índice del fragmento dentro del documento original (base 0)."
    )
    score_relevancia: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Puntuación de similitud semántica respecto a la query. Rango [0.0, 1.0].",
    )


class Metadatos(BaseModel):
    """
    Metadatos de la solicitud de adaptación procesada.

    Registra los parámetros de entrada y el momento en que se generó
    el contenido para trazabilidad.
    """

    documento_id: str = Field(
        ...,
        description=(
            "ID del documento fuente principal utilizado. "
            "En modo singular coincide con el request; en modo múltiple "
            "contiene el primer elemento de documento_ids."
        ),
    )
    documento_ids: list[str] = Field(
        default_factory=list,
        description="Lista completa de IDs de documentos consultados para generar el contenido.",
    )
    tema_o_pregunta: str | None = Field(
        default=None,
        description="Tema o pregunta orientadora que guió la recuperación y generación.",
    )
    apartados: list[str] = Field(
        default_factory=list,
        description="Lista de apartados seleccionados que guiaron el contenido.",
    )
    perfil_destinatario: PerfilDestinatario = Field(
        ..., description="Perfil del destinatario especificado en el request."
    )
    formato_salida: FormatoSalida = Field(
        ..., description="Formato de salida especificado en el request."
    )
    nicho: Nicho = Field(..., description="Nicho especificado en el request.")
    nivel_detalle: NivelDetalle = Field(
        ..., description="Nivel de detalle especificado en el request."
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Fecha y hora UTC en que se generó el contenido.",
    )
    fragmentos_usados: int = Field(
        ..., description="Número de fragmentos del documento utilizados en la generación."
    )
    tiempo_estimado_estudio_minutos: int = Field(
        default=10,
        ge=1,
        description="Tiempo estimado de estudio en minutos calculado para el contenido pedagógico.",
    )
    conceptos_clave: list[str] = Field(
        default_factory=list,
        description="Lista de conceptos clave identificados en el contenido adaptado.",
    )
    tokens_entrada: int | None = Field(
        default=None,
        description="Tokens de entrada del prompt reportados por el proveedor LLM.",
    )
    tokens_salida: int | None = Field(
        default=None,
        description="Tokens de salida de la respuesta reportados por el proveedor LLM.",
    )
    latencia_segundos: float | None = Field(
        default=None,
        description="Latencia total en segundos de la llamada al modelo LLM.",
    )

    @model_validator(mode="after")
    def _reconciliar_documentos(self) -> "Metadatos":
        if not self.documento_ids and self.documento_id:
            self.documento_ids = [self.documento_id]
        elif self.documento_ids and not self.documento_id:
            self.documento_id = self.documento_ids[0]
        return self


class EvaluacionCalidad(BaseModel):
    """
    Evaluación pedagógica automática del contenido generado.

    El `anclaje_fuente_score` mide la similitud coseno promedio entre
    el embedding del contenido generado y los embeddings de los fragmentos
    fuente. Un valor cercano a 1.0 indica alta fidelidad a las fuentes;
    cercano a 0.0 sugiere posible alucinación del LLM.
    """

    anclaje_fuente_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description=(
            "Similitud coseno entre el contenido generado y los fragmentos fuente. "
            "Rango [0.0, 1.0]. Valores cercanos a 1.0 indican alta fidelidad a las fuentes."
        ),
    )
    fragmentos_evaluados: int = Field(
        ..., description="Número de fragmentos fuente considerados en el cálculo del score."
    )
    nivel_confianza: str = Field(
        ...,
        description=(
            "Interpretación cualitativa del anclaje_fuente_score: "
            "'alto' (≥ 0.7), 'medio' (≥ 0.4), 'bajo' (< 0.4)."
        ),
    )


class AlmacenamientoOCI(BaseModel):
    """
    Resultado del intento de almacenamiento del artefacto en OCI Object Storage.

    El sistema opera con degradación elegante: si OCI no está configurado
    o falla, el contenido educativo se entrega igualmente al cliente.
    """

    status_upload: str = Field(
        ...,
        description=(
            "Estado de la operación de almacenamiento: "
            "'exitoso', 'no_configurado' o 'error'."
        ),
    )
    url_objeto: str | None = Field(
        default=None,
        description="URL pública o privada del objeto almacenado en OCI. None si no se almacenó.",
    )
    detalle: str | None = Field(
        default=None,
        description="Mensaje de error o información adicional en caso de fallo. None si fue exitoso.",
    )


# ---------------------------------------------------------------------------
# Response — modelo de salida del endpoint
# ---------------------------------------------------------------------------


class AdaptacionResponse(BaseModel):
    """
    Respuesta completa del endpoint de adaptación de contenido educativo.

    Incluye el contenido generado, los fragmentos fuente utilizados (con
    trazabilidad por documento), la evaluación pedagógica automática y el
    resultado del almacenamiento en OCI Object Storage.
    """

    status: str = Field(
        default="ok",
        description="Estado de la operación. Siempre 'ok' en respuestas exitosas.",
    )
    document_id: str = Field(
        ...,
        description=(
            "ID del documento fuente principal. En modo múltiple, primer elemento "
            "de documento_ids. Mantenido por compatibilidad hacia atrás."
        ),
    )
    documento_ids: list[str] = Field(
        default_factory=list,
        description="Lista completa de IDs de documentos consultados.",
    )

    @model_validator(mode="after")
    def _reconciliar_documentos_resp(self) -> "AdaptacionResponse":
        if not self.documento_ids and self.document_id:
            self.documento_ids = [self.document_id]
        elif self.documento_ids and not self.document_id:
            self.document_id = self.documento_ids[0]
        return self
    metadatos: Metadatos = Field(
        ..., description="Metadatos de la solicitud procesada."
    )
    contenido_adaptado: Any = Field(
        ...,
        description=(
            "Contenido educativo generado. Puede ser un string (para formatos como "
            "tutorial, resumen_ejecutivo, guion_clase) o un dict/list JSON estructurado "
            "(para flashcards y quiz)."
        ),
    )
    evaluacion_calidad: EvaluacionCalidad = Field(
        ..., description="Evaluación pedagógica automática del contenido generado."
    )
    fuentes: list[FuenteFragmento] = Field(
        ...,
        description=(
            "Lista de fragmentos de los documentos fuente utilizados en la generación. "
            "Cada fragmento incluye su documento_id para trazabilidad."
        ),
    )
    almacenamiento_oci: AlmacenamientoOCI = Field(
        ..., description="Resultado del intento de almacenamiento en OCI Object Storage."
    )
