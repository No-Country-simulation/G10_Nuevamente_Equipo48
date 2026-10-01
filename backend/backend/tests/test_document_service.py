"""
Tests de propiedad y de ejemplo para DocumentService — NuevaMente Backend.

Cubre:
  - Propiedad 5: Extracción de TXT es un round-trip idempotente           (Requisito 2.7)
  - Propiedad 4: Extracción de Markdown produce salida no vacía            (Requisito 2.6)
  - Ejemplo: MIME type no soportado lanza ExtractionError
  - Ejemplo: PDF corrupto (bytes aleatorios) lanza ExtractionError
  - Ejemplo: Markdown simple extrae correctamente el texto visible
  - Ejemplo: TXT con caracteres especiales UTF-8 se extrae sin pérdida

Nota:  Los tests de propiedad usan el perfil hypothesis configurado en
       conftest.py (max_examples=100, suppress_health_check=[too_slow]).
"""

from __future__ import annotations

import io
import struct

import pytest
from hypothesis import given, settings, HealthCheck
import hypothesis.strategies as st

from app.core.exceptions import ExtractionError
from app.services.document_service import DocumentService


# ---------------------------------------------------------------------------
# Fixture: instancia del servicio reutilizable en todos los tests
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def service() -> DocumentService:
    """Instancia única de DocumentService para todos los tests del módulo."""
    return DocumentService()


# ---------------------------------------------------------------------------
# Estrategia compartida: textos seguros para round-trip
#
# Se excluye la categoría de sustitutos Unicode ("Cs") para evitar caracteres
# que no se pueden codificar/decodificar en UTF-8 de forma estable, y se
# excluye el byte nulo (\x00) porque algunos procesadores de texto lo omiten.
# El filtro adicional garantiza que el texto tenga contenido visible (strip),
# lo que corresponde al comportamiento de _extract_txt que lanza ExtractionError
# cuando el texto solo contiene espacios en blanco.
# ---------------------------------------------------------------------------

_TEXTO_SEGURO = st.text(
    min_size=1,
    max_size=300,
    alphabet=st.characters(
        blacklist_categories=("Cs",),
        blacklist_characters="\x00",
    ),
).filter(lambda s: s.strip())


# ===========================================================================
# Propiedad 5 — Extracción de TXT es un round-trip idempotente
# Valida: Requisito 2.7
#
# Para cualquier texto no vacío y sin caracteres problemáticos, codificarlo
# como UTF-8 y extraerlo con DocumentService debe devolver exactamente el
# mismo texto (o su equivalente normalizado).  Verificamos que:
#   1. No lanza ninguna excepción.
#   2. El resultado contiene al menos el texto original en la salida.
# ===========================================================================


@given(_TEXTO_SEGURO)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_propiedad_txt_round_trip(service: DocumentService, text: str) -> None:
    """
    Propiedad 5: extract_text sobre bytes UTF-8 de un texto no vacío debe
    retornar ese mismo texto sin modificarlo.

    **Valida: Requisito 2.7**
    """
    file_bytes = text.encode("utf-8")
    resultado = service.extract_text(file_bytes, "text/plain")

    # El texto devuelto debe ser idéntico al original (sin recortar ni transformar)
    assert resultado == text, (
        f"Round-trip falló.\n"
        f"  Entrada : {text!r}\n"
        f"  Salida  : {resultado!r}"
    )


# ===========================================================================
# Propiedad 4 — Extracción de Markdown produce salida no vacía
# Valida: Requisito 2.6
#
# Para cualquier texto no vacío envuelto en un bloque Markdown mínimo
# (párrafo plano), el servicio debe retornar una cadena con contenido visible.
# ===========================================================================


@given(_TEXTO_SEGURO)
@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
def test_propiedad_markdown_produce_salida_no_vacia(
    service: DocumentService, text: str
) -> None:
    """
    Propiedad 4: extract_text sobre un archivo Markdown que contiene texto
    visible siempre debe retornar una cadena no vacía.

    **Valida: Requisito 2.6**
    """
    # Construir un Markdown mínimo: párrafo con el texto como contenido
    markdown_content = f"# Título de prueba\n\n{text}\n"
    file_bytes = markdown_content.encode("utf-8")

    resultado = service.extract_text(file_bytes, "text/markdown")

    assert resultado.strip(), (
        f"Extracción de Markdown produjo cadena vacía para texto: {text!r}"
    )


# ===========================================================================
# Tests de ejemplo
# ===========================================================================


class TestMimeTypeInvalido:
    """Ejemplo: MIME type no soportado debe lanzar ExtractionError."""

    @pytest.mark.parametrize(
        "mime_invalido",
        [
            "application/json",
            "image/png",
            "video/mp4",
            "application/xml",
            "text/html",
            "application/octet-stream",
        ],
    )
    def test_mime_invalido_lanza_extraction_error(
        self, service: DocumentService, mime_invalido: str
    ) -> None:
        """
        Un MIME type fuera del conjunto soportado debe lanzar ExtractionError
        con un mensaje que identifique el tipo rechazado.
        """
        datos_arbitrarios = b"contenido de prueba"

        with pytest.raises(ExtractionError) as exc_info:
            service.extract_text(datos_arbitrarios, mime_invalido)

        # El mensaje de error debe mencionar el tipo MIME recibido
        assert mime_invalido in str(exc_info.value) or mime_invalido in exc_info.value.detail


class TestPDFInvalido:
    """Ejemplo: bytes que no corresponden a un PDF válido deben lanzar ExtractionError."""

    def test_bytes_aleatorios_lanza_extraction_error(
        self, service: DocumentService
    ) -> None:
        """
        Bytes aleatorios pasados como PDF deben lanzar ExtractionError porque
        PyMuPDF no puede abrirlos como documento válido.
        """
        bytes_random = bytes(range(256)) * 4  # 1 KB de basura binaria

        with pytest.raises(ExtractionError):
            service.extract_text(bytes_random, "application/pdf")

    def test_pdf_vacio_lanza_extraction_error(
        self, service: DocumentService
    ) -> None:
        """
        Un stream vacío pasado como PDF debe lanzar ExtractionError.
        PyMuPDF no puede abrir un stream sin cabecera PDF.
        """
        with pytest.raises(ExtractionError):
            service.extract_text(b"", "application/pdf")

    def test_pdf_truncado_lanza_extraction_error(
        self, service: DocumentService
    ) -> None:
        """
        Una cabecera PDF válida pero truncada debe lanzar ExtractionError.
        """
        cabecera_truncada = b"%PDF-1.4\n%%EOF"  # Cabecera sin contenido válido

        with pytest.raises(ExtractionError):
            service.extract_text(cabecera_truncada, "application/pdf")


class TestMarkdownSimple:
    """Ejemplo: extracción de Markdown simple produce el texto visible esperado."""

    def test_encabezado_y_parrafo(self, service: DocumentService) -> None:
        """
        Un archivo Markdown con un encabezado y un párrafo de texto debe
        retornar el texto visible sin las marcas de formato.
        """
        markdown = b"# Introducción a Python\n\nPython es un lenguaje interpretado.\n"
        resultado = service.extract_text(markdown, "text/markdown")

        # El texto del párrafo debe estar presente en el resultado
        assert "Python es un lenguaje interpretado" in resultado

    def test_negrita_e_italica_se_eliminan(self, service: DocumentService) -> None:
        """
        Los marcadores de negrita (**texto**) y cursiva (*texto*) deben
        eliminarse, conservando únicamente el texto visible.
        """
        markdown = b"El **concepto clave** es *fundamental* para entender el tema.\n"
        resultado = service.extract_text(markdown, "text/markdown")

        assert "concepto clave" in resultado
        assert "fundamental" in resultado
        # Los marcadores de formato no deben aparecer en el texto final
        assert "**" not in resultado

    def test_enlace_conserva_texto_visible(self, service: DocumentService) -> None:
        """
        Un enlace Markdown [texto](url) debe conservar el texto del enlace
        y descartar la URL en el resultado.
        """
        markdown = b"Visita la [documentación oficial](https://docs.python.org) para más info.\n"
        resultado = service.extract_text(markdown, "text/markdown")

        assert "documentación oficial" in resultado

    def test_markdown_solo_encabezado(self, service: DocumentService) -> None:
        """
        Un Markdown que contiene solo un encabezado produce texto no vacío.
        """
        markdown = b"# Solo un encabezado\n"
        resultado = service.extract_text(markdown, "text/markdown")

        assert resultado.strip()
        assert "Solo un encabezado" in resultado


class TestTXTUnicodeEspecial:
    """Ejemplo: archivos TXT con caracteres UTF-8 especiales se extraen sin pérdida."""

    def test_caracteres_latinos_extendidos(self, service: DocumentService) -> None:
        """
        Caracteres con tilde y diacríticos del español deben extraerse
        correctamente con codificación UTF-8.
        """
        texto = "Ñoño niño corazón crédito también había señal"
        resultado = service.extract_text(texto.encode("utf-8"), "text/plain")
        assert resultado == texto

    def test_caracteres_chinos(self, service: DocumentService) -> None:
        """
        Texto en caracteres CJK (chino) debe extraerse sin pérdida.
        """
        texto = "这是一段中文文本用于测试"
        resultado = service.extract_text(texto.encode("utf-8"), "text/plain")
        assert resultado == texto

    def test_emojis_y_simbolos(self, service: DocumentService) -> None:
        """
        Emojis y símbolos especiales en UTF-8 deben extraerse correctamente.
        """
        texto = "Estado del sistema: ✅ Operativo | Alertas: ⚠️ Ninguna"
        resultado = service.extract_text(texto.encode("utf-8"), "text/plain")
        assert resultado == texto

    def test_mezcla_idiomas_y_numeros(self, service: DocumentService) -> None:
        """
        Un texto que mezcla español, inglés, números y símbolos debe
        preservarse íntegramente en el round-trip.
        """
        texto = "NuevaMente Backend v1.0 — 'AI/ML' para el ámbito educativo: 100% funcional."
        resultado = service.extract_text(texto.encode("utf-8"), "text/plain")
        assert resultado == texto

    def test_texto_con_saltos_de_linea(self, service: DocumentService) -> None:
        """
        Texto con saltos de línea múltiples debe preservarse tal cual.
        """
        texto = "Primera línea\nSegunda línea\nTercera línea"
        resultado = service.extract_text(texto.encode("utf-8"), "text/plain")
        assert resultado == texto

    def test_mime_con_parametro_charset(self, service: DocumentService) -> None:
        """
        El MIME type 'text/plain; charset=utf-8' (con parámetros adicionales)
        debe ser aceptado correctamente por el dispatcher.
        """
        texto = "Archivo con charset explícito en el MIME type."
        resultado = service.extract_text(
            texto.encode("utf-8"), "text/plain; charset=utf-8"
        )
        assert resultado == texto
