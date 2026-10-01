"""
Servicio de abstracción sobre modelos LLM para NuevaMente Backend.

Permite invocar modelos de OpenAI o Google Gemini mediante una interfaz unificada.
El proveedor y el modelo se seleccionan a través de variables de entorno, sin
hardcodear ninguna clave de API en el código.
"""

import logging

from app.core.config import Settings
from app.core.exceptions import (
    ConfigurationError,
    LLMGenerationError,
    LLMNotConfiguredError,
)

logger = logging.getLogger(__name__)

# Conjunto de proveedores LLM soportados por el sistema
VALID_PROVIDERS = {"openai", "google_gemini"}


class LLMService:
    """
    Abstracción sobre proveedores de modelos de lenguaje grande (LLM).

    Soporta:
      - OpenAI: modelos de la familia GPT (p. ej. gpt-4o-mini)
      - Google Gemini: modelos Gemini de Google AI (p. ej. gemini-pro)

    La selección del proveedor y el modelo se realiza únicamente a través de
    las variables de entorno `LLM_PROVIDER`, `LLM_MODEL` y `LLM_API_KEY`.
    """

    def __init__(self, settings: Settings) -> None:
        """
        Inicializa el servicio LLM y valida la configuración del proveedor.

        Args:
            settings: Instancia de Settings con la configuración del sistema.

        Raises:
            ConfigurationError: Si `LLM_PROVIDER` no es un proveedor soportado.
        """
        if settings.llm_provider not in VALID_PROVIDERS:
            raise ConfigurationError(
                message=(
                    f"El proveedor LLM '{settings.llm_provider}' no está soportado. "
                    f"Valores válidos: {sorted(VALID_PROVIDERS)}"
                ),
                detail=(
                    f"Revisa la variable de entorno LLM_PROVIDER. "
                    f"Valores aceptados: {', '.join(sorted(VALID_PROVIDERS))}."
                ),
            )

        self._settings = settings
        logger.info(
            "LLMService inicializado con proveedor='%s', modelo='%s'.",
            settings.llm_provider,
            settings.llm_model,
        )

    # ------------------------------------------------------------------
    # Interfaz pública
    # ------------------------------------------------------------------

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """
        Genera texto usando el proveedor LLM configurado.

        Args:
            prompt:        Mensaje principal enviado al modelo (rol de usuario).
            system_prompt: Instrucciones de contexto para el modelo (rol de sistema).
                           Si está vacío, no se incluye en la solicitud.

        Returns:
            Texto generado por el modelo como string.

        Raises:
            LLMNotConfiguredError: Si `LLM_API_KEY` está ausente o vacía.
            LLMGenerationError:    Si la llamada al API del LLM falla.
        """
        if not self._settings.llm_api_key:
            raise LLMNotConfiguredError(
                message="El servicio LLM no está disponible.",
                detail=(
                    "La variable de entorno LLM_API_KEY está ausente o vacía. "
                    "Configura una clave de API válida para el proveedor seleccionado."
                ),
            )

        try:
            if self._settings.llm_provider == "openai":
                return self._generate_openai(prompt, system_prompt)
            else:  # google_gemini
                return self._generate_gemini(prompt, system_prompt)
        except (LLMNotConfiguredError, LLMGenerationError):
            # Re-lanzar excepciones propias sin envolver
            raise
        except Exception as exc:
            logger.error(
                "Error inesperado al invocar el LLM (%s): %s",
                self._settings.llm_provider,
                exc,
                exc_info=True,
            )
            raise LLMGenerationError(
                message="Error al generar contenido con el LLM.",
                detail=str(exc),
            ) from exc

    # ------------------------------------------------------------------
    # Implementaciones privadas por proveedor
    # ------------------------------------------------------------------

    def _generate_openai(self, prompt: str, system_prompt: str) -> str:
        """
        Genera texto utilizando la API de OpenAI (chat completions).

        Args:
            prompt:        Contenido del mensaje de usuario.
            system_prompt: Instrucciones para el rol de sistema.
                           Si está vacío, no se añade el mensaje de sistema.

        Returns:
            Texto generado por el modelo.

        Raises:
            LLMNotConfiguredError: Si la clave de API es inválida o fue revocada.
            LLMGenerationError:    Si la llamada a la API falla por cualquier otra razón.
        """
        try:
            import openai  # Importación diferida para evitar error si no está instalado
        except ImportError as exc:
            raise LLMGenerationError(
                message="Error al generar contenido con el LLM.",
                detail="El paquete 'openai' no está instalado. Ejecuta: pip install openai",
            ) from exc

        # Construir la lista de mensajes según disponibilidad de system_prompt
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            client = openai.OpenAI(api_key=self._settings.llm_api_key)
            response = client.chat.completions.create(
                model=self._settings.llm_model,
                messages=messages,  # type: ignore[arg-type]
            )
            contenido = response.choices[0].message.content
            if contenido is None:
                raise LLMGenerationError(
                    message="El LLM retornó una respuesta vacía.",
                    detail="La respuesta del modelo no contenía texto en choices[0].message.content.",
                )
            return contenido

        except openai.AuthenticationError as exc:
            raise LLMNotConfiguredError(
                message="El servicio LLM no está disponible.",
                detail=f"La clave de API de OpenAI es inválida o fue revocada: {exc}",
            ) from exc
        except openai.RateLimitError as exc:
            raise LLMGenerationError(
                message="Error al generar contenido con el LLM.",
                detail=f"Se alcanzó el límite de tasa de la API de OpenAI: {exc}",
            ) from exc
        except openai.APIError as exc:
            raise LLMGenerationError(
                message="Error al generar contenido con el LLM.",
                detail=f"Error en la API de OpenAI: {exc}",
            ) from exc

    def _generate_gemini(self, prompt: str, system_prompt: str) -> str:
        """
        Genera texto utilizando la API de Google Gemini (Generative AI).

        Args:
            prompt:        Contenido principal del mensaje.
            system_prompt: Instrucciones de contexto. Si no está vacío, se
                           antepone al prompt separado por dos saltos de línea.

        Returns:
            Texto generado por el modelo.

        Raises:
            LLMGenerationError: Si la llamada a la API de Gemini falla.
        """
        try:
            import google.generativeai as genai  # Importación diferida
        except ImportError as exc:
            raise LLMGenerationError(
                message="Error al generar contenido con el LLM.",
                detail=(
                    "El paquete 'google-generativeai' no está instalado. "
                    "Ejecuta: pip install google-generativeai"
                ),
            ) from exc

        # Construir el prompt completo: system_prompt (si existe) + prompt de usuario
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt

        try:
            genai.configure(api_key=self._settings.llm_api_key)
            modelo = genai.GenerativeModel(self._settings.llm_model)
            response = modelo.generate_content(full_prompt)
            return response.text

        except Exception as exc:
            logger.error("Error al invocar Google Gemini: %s", exc, exc_info=True)
            raise LLMGenerationError(
                message="Error al generar contenido con el LLM.",
                detail=f"Error en la API de Google Gemini: {exc}",
            ) from exc
