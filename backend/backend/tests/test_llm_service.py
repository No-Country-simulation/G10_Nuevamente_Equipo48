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


# ===========================================================================
# FASE B: 11 Pruebas con Mocks para Telemetría y Manejo de Errores (Gemini)
# ===========================================================================
from unittest.mock import patch
import google.api_core.exceptions as g_exc
from app.core.exceptions import LLMGenerationError
from app.services.llm_service import LLMTelemetry


def test_captura_usage_metadata_completa():
    """Escenario 1: Captura de metadatos de tokens completos cuando Gemini los retorna."""
    settings = _make_settings("google_gemini", api_key="test-key")
    service = LLMService(settings)

    mock_resp = MagicMock()
    mock_resp.text = "Contenido adaptado generado"
    mock_resp.usage_metadata.prompt_token_count = 120
    mock_resp.usage_metadata.candidates_token_count = 45
    mock_resp.usage_metadata.total_token_count = 165

    with patch("google.generativeai.GenerativeModel") as mock_model_cls, \
         patch("google.generativeai.configure"):
        mock_model = mock_model_cls.return_value
        mock_model.generate_content.return_value = mock_resp

        texto, telemetria = service.generate_with_telemetry("Hola")

        assert texto == "Contenido adaptado generado"
        assert telemetria.tokens_entrada == 120
        assert telemetria.tokens_salida == 45
        assert telemetria.tokens_total == 165
        assert telemetria.intentos == 1
        assert telemetria.estado_final == "exitoso"


def test_respuesta_exitosa_sin_usage_metadata():
    """Escenario 2: Respuesta válida pero usage_metadata es None (sin inventar tokens)."""
    settings = _make_settings("google_gemini", api_key="test-key")
    service = LLMService(settings)

    mock_resp = MagicMock()
    mock_resp.text = "Respuesta sin tokens"
    mock_resp.usage_metadata = None

    with patch("google.generativeai.GenerativeModel") as mock_model_cls, \
         patch("google.generativeai.configure"):
        mock_model = mock_model_cls.return_value
        mock_model.generate_content.return_value = mock_resp

        texto, telemetria = service.generate_with_telemetry("Hola")

        assert texto == "Respuesta sin tokens"
        assert telemetria.tokens_entrada is None
        assert telemetria.tokens_salida is None
        assert telemetria.tokens_total is None
        assert telemetria.estado_final == "exitoso"


def test_reintento_exitoso_tras_429_transitorio():
    """Escenario 3: Recuperación tras un 429 transitorio en intento 2."""
    settings = _make_settings("google_gemini", api_key="test-key")
    service = LLMService(settings)

    mock_resp = MagicMock()
    mock_resp.text = "Éxito al segundo intento"
    mock_resp.usage_metadata.prompt_token_count = 80
    mock_resp.usage_metadata.candidates_token_count = 20
    mock_resp.usage_metadata.total_token_count = 100

    error_429 = g_exc.ResourceExhausted("Rate limit exceeded")

    with patch("google.generativeai.GenerativeModel") as mock_model_cls, \
         patch("google.generativeai.configure"), \
         patch("time.sleep"):  # Mockear sleep para evitar espera real
        mock_model = mock_model_cls.return_value
        mock_model.generate_content.side_effect = [error_429, mock_resp]

        texto, telemetria = service.generate_with_telemetry("Hola")

        assert texto == "Éxito al segundo intento"
        assert telemetria.intentos == 2
        assert telemetria.estado_final == "429_transitorio_recuperado"


def test_cuota_diaria_agotada_corta_inmediatamente():
    """Escenario 4: Cuota diaria comprobada corta de inmediato sin reintentar."""
    settings = _make_settings("google_gemini", api_key="test-key")
    service = LLMService(settings)

    error_cuota = g_exc.ResourceExhausted(
        "Quota exceeded for quota metric 'GenerateContent requests per day' and limit 'Requests per day'"
    )

    with patch("google.generativeai.GenerativeModel") as mock_model_cls, \
         patch("google.generativeai.configure"), \
         patch("time.sleep") as mock_sleep:
        mock_model = mock_model_cls.return_value
        mock_model.generate_content.side_effect = error_cuota

        with pytest.raises(LLMGenerationError) as exc_info:
            service.generate_with_telemetry("Hola")

        assert "cuota" in exc_info.value.message.lower()
        # No debe haber dormido / reintentado
        assert mock_sleep.call_count == 0
        assert mock_model.generate_content.call_count == 1


def test_error_429_ambiguo_reintenta_hasta_limite():
    """Escenario 5: Error 429 ambiguo agota los 3 intentos autorizados y falla."""
    settings = _make_settings("google_gemini", api_key="test-key")
    service = LLMService(settings)

    error_429 = g_exc.ResourceExhausted("429 Resource has been exhausted")

    with patch("google.generativeai.GenerativeModel") as mock_model_cls, \
         patch("google.generativeai.configure"), \
         patch("time.sleep") as mock_sleep:
        mock_model = mock_model_cls.return_value
        mock_model.generate_content.side_effect = error_429

        with pytest.raises(LLMGenerationError) as exc_info:
            service.generate_with_telemetry("Hola")

        assert mock_model.generate_content.call_count == 3
        assert mock_sleep.call_count == 2
        assert "saturado" in exc_info.value.message.lower() or "tasa" in exc_info.value.detail.lower()


def test_error_red_transitorio_503_se_recupera():
    """Escenario 6: Recuperación tras error 503 ServiceUnavailable transitorio."""
    settings = _make_settings("google_gemini", api_key="test-key")
    service = LLMService(settings)

    error_503 = g_exc.ServiceUnavailable("503 Backend temporarily unavailable")
    mock_resp = MagicMock(text="OK tras 503", usage_metadata=None)

    with patch("google.generativeai.GenerativeModel") as mock_model_cls, \
         patch("google.generativeai.configure"), \
         patch("time.sleep"):
        mock_model = mock_model_cls.return_value
        mock_model.generate_content.side_effect = [error_503, mock_resp]

        texto, telemetria = service.generate_with_telemetry("Hola")

        assert texto == "OK tras 503"
        assert telemetria.intentos == 2


def test_error_definitivo_400_no_reintenta():
    """Escenario 7: Error 400 InvalidArgument de cliente no reintenta."""
    settings = _make_settings("google_gemini", api_key="test-key")
    service = LLMService(settings)

    error_400 = g_exc.InvalidArgument("400 Invalid prompt structure")

    with patch("google.generativeai.GenerativeModel") as mock_model_cls, \
         patch("google.generativeai.configure"), \
         patch("time.sleep") as mock_sleep:
        mock_model = mock_model_cls.return_value
        mock_model.generate_content.side_effect = error_400

        with pytest.raises(LLMGenerationError):
            service.generate_with_telemetry("Hola")

        assert mock_model.generate_content.call_count == 1
        assert mock_sleep.call_count == 0


def test_registro_telemetria_sanitizado():
    """Escenario 8: Verificación de que la telemetría logueada no expone secretos ni prompts."""
    settings = _make_settings("google_gemini", api_key="super-secret-key-123")
    service = LLMService(settings)

    mock_resp = MagicMock(text="Contenido secreto de respuesta", usage_metadata=None)

    with patch("google.generativeai.GenerativeModel") as mock_model_cls, \
         patch("google.generativeai.configure"), \
         patch("app.services.llm_service.telemetry_logger.info") as mock_log:
        mock_model = mock_model_cls.return_value
        mock_model.generate_content.return_value = mock_resp

        service.generate_with_telemetry("Prompt confidencial sobre leyes y finanzas")

        assert mock_log.called
        log_payload = mock_log.call_args[0][0]
        # Ningún secreto ni texto sensible debe estar en el log de telemetría
        assert "super-secret-key-123" not in log_payload
        assert "Prompt confidencial" not in log_payload
        assert "Contenido secreto de respuesta" not in log_payload
        assert "llm_generacion" in log_payload


def test_medicion_latencias_diferenciadas():
    """Escenario 9: Registro y medición de latencias válidas."""
    settings = _make_settings("google_gemini", api_key="test-key")
    service = LLMService(settings)

    mock_resp = MagicMock(text="Respuesta rápida", usage_metadata=None)

    with patch("google.generativeai.GenerativeModel") as mock_model_cls, \
         patch("google.generativeai.configure"):
        mock_model = mock_model_cls.return_value
        mock_model.generate_content.return_value = mock_resp

        _, telemetria = service.generate_with_telemetry("Hola")

        assert telemetria.latencia_llamada_segundos >= 0.0
        assert telemetria.latencia_total_segundos >= telemetria.latencia_llamada_segundos


def test_aislamiento_concurrente_telemetria():
    """Escenario 10: Cada llamada concurrentemente retorna su propio objeto inmutable de telemetría."""
    settings = _make_settings("google_gemini", api_key="test-key")
    service = LLMService(settings)

    resp1 = MagicMock(text="Resp 1")
    resp1.usage_metadata.prompt_token_count = 10
    resp1.usage_metadata.candidates_token_count = 5
    resp1.usage_metadata.total_token_count = 15

    resp2 = MagicMock(text="Resp 2")
    resp2.usage_metadata.prompt_token_count = 50
    resp2.usage_metadata.candidates_token_count = 25
    resp2.usage_metadata.total_token_count = 75

    with patch("google.generativeai.GenerativeModel") as mock_model_cls, \
         patch("google.generativeai.configure"):
        mock_model = mock_model_cls.return_value
        mock_model.generate_content.side_effect = [resp1, resp2]

        t1_texto, t1_tel = service.generate_with_telemetry("Prompt 1")
        t2_texto, t2_tel = service.generate_with_telemetry("Prompt 2")

        assert t1_texto == "Resp 1"
        assert t1_tel.tokens_total == 15
        assert t2_texto == "Resp 2"
        assert t2_tel.tokens_total == 75
        # Los objetos deben ser independientes
        assert t1_tel is not t2_tel


def test_generate_conserva_contrato_retorno_str():
    """Escenario 11: generate() sigue devolviendo un str primitivo."""
    settings = _make_settings("google_gemini", api_key="test-key")
    service = LLMService(settings)

    mock_resp = MagicMock(text="Solo texto primitivo", usage_metadata=None)

    with patch("google.generativeai.GenerativeModel") as mock_model_cls, \
         patch("google.generativeai.configure"):
        mock_model = mock_model_cls.return_value
        mock_model.generate_content.return_value = mock_resp

        resultado = service.generate("Prueba contrato")

        assert isinstance(resultado, str)
        assert resultado == "Solo texto primitivo"

