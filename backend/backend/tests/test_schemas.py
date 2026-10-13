"""
Tests para los schemas Pydantic de NuevaMente Backend.

Cubre:
  - Validación de enums (valores válidos e inválidos)
  - Construcción de AdaptacionRequest con campos obligatorios
  - Round-trip JSON de AdaptacionResponse
  - Construcción de UploadResponse y ErrorResponse

Requisitos: 9.2, 9.6
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas.adaptacion import (
    AdaptacionRequest,
    AdaptacionResponse,
    AlmacenamientoOCI,
    EvaluacionCalidad,
    FormatoSalida,
    FuenteFragmento,
    Metadatos,
    Nicho,
    NivelDetalle,
    PerfilDestinatario,
)
from app.schemas.file import ErrorResponse, UploadResponse

# ---------------------------------------------------------------------------
# Fixture: datos válidos reutilizables para AdaptacionRequest
# ---------------------------------------------------------------------------

VALID_REQUEST_DATA = {
    "documento_id": "test-doc-123",
    "perfil_destinatario": "principiante",
    "formato_salida": "tutorial",
    "nicho": "general",
    "nivel_detalle": "didactico",
}


# ---------------------------------------------------------------------------
# Tests de PerfilDestinatario
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("perfil", ["principiante", "junior", "lider_tecnico", "ejecutivo"])
def test_perfil_destinatario_valido(perfil):
    """Cada valor válido de PerfilDestinatario debe ser aceptado por AdaptacionRequest."""
    data = {**VALID_REQUEST_DATA, "perfil_destinatario": perfil}
    req = AdaptacionRequest(**data)
    assert req.perfil_destinatario.value == perfil


@pytest.mark.parametrize(
    "perfil_invalido", ["estudiante", "experto", "", "PRINCIPIANTE", "admin"]
)
def test_perfil_destinatario_invalido(perfil_invalido):
    """Valores fuera del enum PerfilDestinatario deben generar ValidationError."""
    data = {**VALID_REQUEST_DATA, "perfil_destinatario": perfil_invalido}
    with pytest.raises(ValidationError):
        AdaptacionRequest(**data)


# ---------------------------------------------------------------------------
# Tests de FormatoSalida
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "formato", ["tutorial", "flashcards", "quiz", "resumen_ejecutivo", "guion_clase"]
)
def test_formato_salida_valido(formato):
    """Cada valor válido de FormatoSalida debe ser aceptado por AdaptacionRequest."""
    data = {**VALID_REQUEST_DATA, "formato_salida": formato}
    req = AdaptacionRequest(**data)
    assert req.formato_salida.value == formato


@pytest.mark.parametrize(
    "formato_invalido", ["video", "podcast", "", "TUTORIAL", "presentacion"]
)
def test_formato_salida_invalido(formato_invalido):
    """Valores fuera del enum FormatoSalida deben generar ValidationError."""
    data = {**VALID_REQUEST_DATA, "formato_salida": formato_invalido}
    with pytest.raises(ValidationError):
        AdaptacionRequest(**data)


# ---------------------------------------------------------------------------
# Tests de Nicho
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("nicho", ["fintech", "salud", "ecommerce", "general"])
def test_nicho_valido(nicho):
    """Cada valor válido de Nicho debe ser aceptado por AdaptacionRequest."""
    data = {**VALID_REQUEST_DATA, "nicho": nicho}
    req = AdaptacionRequest(**data)
    assert req.nicho.value == nicho


@pytest.mark.parametrize("nicho_invalido", ["educacion", "turismo", "", "FINTECH", "retail"])
def test_nicho_invalido(nicho_invalido):
    """Valores fuera del enum Nicho deben generar ValidationError."""
    data = {**VALID_REQUEST_DATA, "nicho": nicho_invalido}
    with pytest.raises(ValidationError):
        AdaptacionRequest(**data)


# ---------------------------------------------------------------------------
# Tests de NivelDetalle
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("nivel", ["didactico", "intermedio", "tecnico"])
def test_nivel_detalle_valido(nivel):
    """Cada valor válido de NivelDetalle debe ser aceptado por AdaptacionRequest."""
    data = {**VALID_REQUEST_DATA, "nivel_detalle": nivel}
    req = AdaptacionRequest(**data)
    assert req.nivel_detalle.value == nivel


@pytest.mark.parametrize(
    "nivel_invalido", ["avanzado", "basico", "", "TECNICO", "experto"]
)
def test_nivel_detalle_invalido(nivel_invalido):
    """Valores fuera del enum NivelDetalle deben generar ValidationError."""
    data = {**VALID_REQUEST_DATA, "nivel_detalle": nivel_invalido}
    with pytest.raises(ValidationError):
        AdaptacionRequest(**data)


# ---------------------------------------------------------------------------
# Tests de AdaptacionRequest
# ---------------------------------------------------------------------------


def test_adaptacion_request_valido():
    """AdaptacionRequest debe construirse correctamente con todos los campos obligatorios."""
    req = AdaptacionRequest(**VALID_REQUEST_DATA)
    assert req.documento_id == "test-doc-123"
    assert req.perfil_destinatario == PerfilDestinatario.principiante
    assert req.formato_salida == FormatoSalida.tutorial
    assert req.nicho == Nicho.general
    assert req.nivel_detalle == NivelDetalle.didactico


def test_adaptacion_request_documento_id_vacio():
    """documento_id vacío debe generar ValidationError."""
    data = {**VALID_REQUEST_DATA, "documento_id": ""}
    with pytest.raises(ValidationError):
        AdaptacionRequest(**data)


def test_adaptacion_request_perfil_invalido():
    """perfil_destinatario con valor inválido debe generar ValidationError."""
    data = {**VALID_REQUEST_DATA, "perfil_destinatario": "invalido"}
    with pytest.raises(ValidationError):
        AdaptacionRequest(**data)


def test_adaptacion_request_formato_invalido():
    """formato_salida con valor inválido debe generar ValidationError."""
    data = {**VALID_REQUEST_DATA, "formato_salida": "invalido"}
    with pytest.raises(ValidationError):
        AdaptacionRequest(**data)


def test_adaptacion_request_nicho_invalido():
    """nicho con valor inválido debe generar ValidationError."""
    data = {**VALID_REQUEST_DATA, "nicho": "invalido"}
    with pytest.raises(ValidationError):
        AdaptacionRequest(**data)


def test_adaptacion_request_nivel_detalle_invalido():
    """nivel_detalle con valor inválido debe generar ValidationError."""
    data = {**VALID_REQUEST_DATA, "nivel_detalle": "invalido"}
    with pytest.raises(ValidationError):
        AdaptacionRequest(**data)


@pytest.mark.parametrize(
    "campo_faltante",
    ["documento_id", "perfil_destinatario", "formato_salida", "nicho", "nivel_detalle"],
)
def test_adaptacion_request_campo_obligatorio_faltante(campo_faltante):
    """Omitir cualquier campo obligatorio de AdaptacionRequest debe generar ValidationError."""
    data = {k: v for k, v in VALID_REQUEST_DATA.items() if k != campo_faltante}
    with pytest.raises(ValidationError):
        AdaptacionRequest(**data)


# ---------------------------------------------------------------------------
# Tests de AdaptacionResponse — round-trip JSON
# ---------------------------------------------------------------------------


def test_adaptacion_response_round_trip():
    """Serializar y deserializar AdaptacionResponse produce un objeto equivalente al original."""
    response = AdaptacionResponse(
        status="ok",
        document_id="doc-123",
        metadatos=Metadatos(
            documento_id="doc-123",
            perfil_destinatario=PerfilDestinatario.principiante,
            formato_salida=FormatoSalida.tutorial,
            nicho=Nicho.general,
            nivel_detalle=NivelDetalle.didactico,
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            fragmentos_usados=3,
        ),
        contenido_adaptado="Paso 1: Introducción...",
        evaluacion_calidad=EvaluacionCalidad(
            anclaje_fuente_score=0.75,
            fragmentos_evaluados=3,
            nivel_confianza="alto",
        ),
        fuentes=[
            FuenteFragmento(
                chunk_id="chunk-001",
                texto="Texto del fragmento",
                posicion=0,
                score_relevancia=0.85,
            )
        ],
        almacenamiento_oci=AlmacenamientoOCI(status_upload="no_configurado"),
    )

    # Serializar a JSON y reconstruir
    json_str = response.model_dump_json()
    reconstruido = AdaptacionResponse.model_validate_json(json_str)

    # Verificar equivalencia campo a campo
    assert reconstruido.status == response.status
    assert reconstruido.document_id == response.document_id
    assert reconstruido.metadatos.documento_id == response.metadatos.documento_id
    assert (
        reconstruido.metadatos.perfil_destinatario == response.metadatos.perfil_destinatario
    )
    assert reconstruido.metadatos.formato_salida == response.metadatos.formato_salida
    assert reconstruido.metadatos.nicho == response.metadatos.nicho
    assert reconstruido.metadatos.nivel_detalle == response.metadatos.nivel_detalle
    assert reconstruido.metadatos.fragmentos_usados == response.metadatos.fragmentos_usados
    assert reconstruido.contenido_adaptado == response.contenido_adaptado
    assert (
        reconstruido.evaluacion_calidad.anclaje_fuente_score
        == response.evaluacion_calidad.anclaje_fuente_score
    )
    assert (
        reconstruido.evaluacion_calidad.fragmentos_evaluados
        == response.evaluacion_calidad.fragmentos_evaluados
    )
    assert reconstruido.evaluacion_calidad.nivel_confianza == response.evaluacion_calidad.nivel_confianza
    assert len(reconstruido.fuentes) == len(response.fuentes)
    assert reconstruido.fuentes[0].chunk_id == response.fuentes[0].chunk_id
    assert reconstruido.fuentes[0].score_relevancia == response.fuentes[0].score_relevancia
    assert (
        reconstruido.almacenamiento_oci.status_upload
        == response.almacenamiento_oci.status_upload
    )


def test_adaptacion_response_contenido_adaptado_dict():
    """contenido_adaptado puede ser un dict (por ejemplo, para el formato flashcards)."""
    response = AdaptacionResponse(
        status="ok",
        document_id="doc-456",
        metadatos=Metadatos(
            documento_id="doc-456",
            perfil_destinatario=PerfilDestinatario.junior,
            formato_salida=FormatoSalida.flashcards,
            nicho=Nicho.fintech,
            nivel_detalle=NivelDetalle.intermedio,
            timestamp=datetime(2024, 6, 15, 9, 0, 0),
            fragmentos_usados=2,
        ),
        contenido_adaptado={"tarjetas": [{"pregunta": "¿Qué es DeFi?", "respuesta": "Finanzas descentralizadas"}]},
        evaluacion_calidad=EvaluacionCalidad(
            anclaje_fuente_score=0.60,
            fragmentos_evaluados=2,
            nivel_confianza="medio",
        ),
        fuentes=[],
        almacenamiento_oci=AlmacenamientoOCI(status_upload="exitoso", url_objeto="https://oci.example.com/obj1"),
    )

    json_str = response.model_dump_json()
    reconstruido = AdaptacionResponse.model_validate_json(json_str)

    assert isinstance(reconstruido.contenido_adaptado, dict)
    assert reconstruido.almacenamiento_oci.url_objeto == "https://oci.example.com/obj1"


# ---------------------------------------------------------------------------
# Tests de UploadResponse y ErrorResponse
# ---------------------------------------------------------------------------


def test_upload_response_construccion_valida():
    """UploadResponse debe construirse correctamente con todos los campos requeridos."""
    resp = UploadResponse(
        status="ok",
        documento_id="doc-789",
        filename="documento.pdf",
        chunks_indexados=10,
        oci_status="exitoso",
    )
    assert resp.status == "ok"
    assert resp.documento_id == "doc-789"
    assert resp.filename == "documento.pdf"
    assert resp.chunks_indexados == 10
    assert resp.oci_status == "exitoso"


def test_upload_response_tipos_correctos():
    """Los campos de UploadResponse deben ser del tipo correcto."""
    resp = UploadResponse(
        documento_id="doc-001",
        filename="test.pdf",
        chunks_indexados=5,
        oci_status="no_configurado",
    )
    assert isinstance(resp.status, str)
    assert isinstance(resp.documento_id, str)
    assert isinstance(resp.filename, str)
    assert isinstance(resp.chunks_indexados, int)
    assert isinstance(resp.oci_status, str)


def test_upload_response_status_por_defecto():
    """El campo status de UploadResponse debe tener 'ok' como valor por defecto."""
    resp = UploadResponse(
        documento_id="doc-002",
        filename="archivo.pdf",
        chunks_indexados=3,
        oci_status="error",
    )
    assert resp.status == "ok"


def test_error_response_construccion_valida():
    """ErrorResponse debe construirse correctamente con error y detalle."""
    err = ErrorResponse(
        error="Documento no encontrado",
        detalle="No existe un documento con el ID proporcionado.",
    )
    assert err.error == "Documento no encontrado"
    assert err.detalle == "No existe un documento con el ID proporcionado."


def test_error_response_tipos_correctos():
    """Los campos de ErrorResponse deben ser strings."""
    err = ErrorResponse(error="Error interno", detalle="")
    assert isinstance(err.error, str)
    assert isinstance(err.detalle, str)


def test_error_response_detalle_vacio():
    """ErrorResponse debe aceptar detalle vacío."""
    err = ErrorResponse(error="Fallo de validación", detalle="")
    assert err.detalle == ""
