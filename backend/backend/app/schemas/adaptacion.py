"""
Schemas Pydantic para el endpoint de adaptación de contenido educativo.

Define los modelos de entrada y salida del flujo POST /api/v1/adaptacion,
incluyendo los enums de valores permitidos y todos los sub-modelos del
cuerpo de respuesta.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


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

    El campo `documento_id` debe corresponder a un documento previamente
    ingestado mediante el endpoint de carga de archivos.
    """

    documento_id: str = Field(
        ...,
        description="ID único del documento previamente cargado en el sistema.",
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


# ---------------------------------------------------------------------------
# Sub-modelos de respuesta
# ---------------------------------------------------------------------------


class FuenteFragmento(BaseModel):
    """
    Fragmento del documento fuente utilizado para generar el contenido.

    Incluye la puntuación de relevancia semántica asignada durante la
    recuperación del índice FAISS.
    """

    chunk_id: str = Field(..., description="Identificador único del fragmento (UUID).")
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

    documento_id: str = Field(..., description="ID del documento fuente utilizado.")
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
        default_factory=datetime.utcnow,
        description="Fecha y hora UTC en que se generó el contenido.",
    )
    fragmentos_usados: int = Field(
        ..., description="Número de fragmentos del documento utilizados en la generación."
    )


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

    Incluye el contenido generado, los fragmentos fuente utilizados,
    la evaluación pedagógica automática y el resultado del almacenamiento
    en OCI Object Storage.
    """

    status: str = Field(
        default="ok",
        description="Estado de la operación. Siempre 'ok' en respuestas exitosas.",
    )
    document_id: str = Field(
        ..., description="ID del documento fuente utilizado en la generación."
    )
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
        description="Lista de fragmentos del documento fuente utilizados en la generación.",
    )
    almacenamiento_oci: AlmacenamientoOCI = Field(
        ..., description="Resultado del intento de almacenamiento en OCI Object Storage."
    )
