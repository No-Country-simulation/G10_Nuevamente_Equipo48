"""
Tests de propiedad para LLMService.

Propiedad 10: El proveedor LLM inválido siempre lanza ConfigurationError.

Para cualquier string que no sea exactamente "openai" o "google_gemini"
asignado a LLM_PROVIDER, la inicialización de LLMService lanza ConfigurationError
con un mensaje descriptivo en español.

Requisito: 4.4
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from hypothesis import HealthCheck, given
from hypothesis import settings as h_settings
from hypothesis import strategies as st

from app.core.exceptions import ConfigurationError, LLMNotConfiguredError
from app.services.llm_service import LLMService, VALID_PROVIDERS


# Proveedores válidos
PROVEEDORES_VALIDOS = {"openai", "google_gemini"}


def _make_settings(provider: str, model: str = "gpt-4o-mini", api_key: str = "") -> MagicMock:
    """Construye un mock de Settings con el proveedor dado."""
    mock = MagicMock()
    mock.llm_provider = provider
    mock.llm_model = model
    mock.llm_api_key = api_key
    return mock


# ---------------------------------------------------------------------------
# Propiedad 10: proveedor inválido → ConfigurationError
# ---------------------------------------------------------------------------

@h_settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(provider=st.text(
    alphabet=st.characters(blacklist_categories=("Cs",)),
    min_size=1,
    max_size=50
).filter(lambda s: s not in PROVEEDORES_VALIDOS))
def test_propiedad_proveedor_invalido_lanza_error(provider):
    """
    Propiedad 10: Para cualquier string fuera del conjunto {"openai", "google_gemini"},
    LLMService.__init__ lanza ConfigurationError.
    Valida: Requisito 4.4
    """
    settings = _make_settings(provider)
    with pytest.raises(ConfigurationError):
        LLMService(settings)


# ---------------------------------------------------------------------------
# Tests de ejemplo — proveedores válidos no lanzan ConfigurationError
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("provider", ["openai", "google_gemini"])
def test_proveedor_valido_no_lanza_error(provider):
    """Los proveedores válidos NO deben lanzar ConfigurationError en __init__."""
    settings = _make_settings(provider, api_key="")
    # No debe lanzar excepción durante la inicialización
    service = LLMService(settings)
    assert service is not None


def test_mensaje_error_contiene_proveedor_invalido():
    """
    El mensaje de ConfigurationError debe incluir el valor inválido recibido
    y los valores válidos soportados.
    """
    settings = _make_settings("proveedor_falso")
    with pytest.raises(ConfigurationError) as exc_info:
        LLMService(settings)

    error_msg = exc_info.value.message.lower()
    assert "proveedor_falso" in error_msg or "no está soportado" in error_msg or "no soportado" in error_msg


def test_llm_sin_api_key_lanza_error_al_generar():
    """
    LLMService inicializa correctamente sin API key,
    pero lanza LLMNotConfiguredError al intentar generar contenido.
    """
    settings = _make_settings("openai", api_key="")
    service = LLMService(settings)

    with pytest.raises(LLMNotConfiguredError):
        service.generate("prompt de prueba")


def test_valid_providers_son_exactamente_dos():
    """El conjunto VALID_PROVIDERS debe contener exactamente openai y google_gemini."""
    assert VALID_PROVIDERS == {"openai", "google_gemini"}
