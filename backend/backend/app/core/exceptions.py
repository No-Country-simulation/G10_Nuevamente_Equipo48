"""
Jerarquía de excepciones personalizadas para NuevaMente Backend.

Todas las excepciones heredan de NuevaMenteError e incluyen dos atributos:
  - message: descripción legible del error (mostrada al cliente).
  - detail:  información adicional para diagnóstico (puede quedar vacía).
"""


class NuevaMenteError(Exception):
    """
    Clase base para todas las excepciones del sistema NuevaMente.

    Centraliza el manejo de los atributos `message` y `detail` que son
    devueltos en las respuestas de error JSON con estructura uniforme.
    """

    def __init__(self, message: str, detail: str = "") -> None:
        """
        Inicializa la excepción base.

        Args:
            message: Descripción breve del error en español (se expone al cliente).
            detail:  Información adicional para depuración (opcional).
        """
        super().__init__(message)
        self.message = message
        self.detail = detail

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, detail={self.detail!r})"


class ExtractionError(NuevaMenteError):
    """
    Lanzada cuando el Document Service no puede extraer texto de un archivo.

    Causas comunes:
      - Archivo PDF corrupto o protegido por contraseña.
      - PDF sin texto seleccionable (solo imágenes sin OCR).
      - Error de decodificación irrecuperable en archivos TXT/Markdown.
      - Tipo MIME no soportado por el servicio de extracción.
    """


class DocumentNotFoundError(NuevaMenteError):
    """
    Lanzada cuando el `documento_id` referenciado no existe en el store de chunks.

    Se produce en el RAG Service cuando se intenta recuperar chunks o verificar
    la existencia de un documento que nunca fue ingestado (o cuyo estado se perdió
    al reiniciar el servidor, dado que el almacenamiento es en memoria).
    """


class LLMNotConfiguredError(NuevaMenteError):
    """
    Lanzada cuando el LLM Service no puede operar por falta de credenciales.

    Causas:
      - La variable de entorno `LLM_API_KEY` está ausente o vacía.
      - La clave de API proporcionada es inválida o fue revocada.

    El endpoint que recibe esta excepción debe responder con HTTP 503.
    """


class LLMGenerationError(NuevaMenteError):
    """
    Lanzada cuando la llamada al API del LLM falla durante la generación de contenido.

    Causas:
      - Error de red o timeout al contactar la API del proveedor LLM.
      - Respuesta inesperada del proveedor (estructura de respuesta no reconocida).
      - Límite de tasa (rate limit) alcanzado.
      - Error interno del proveedor LLM (HTTP 5xx del proveedor).
    """


class ConfigurationError(NuevaMenteError):
    """
    Lanzada cuando un servicio detecta una configuración inválida al inicializarse.

    Causas:
      - `LLM_PROVIDER` tiene un valor diferente de `"openai"` o `"google_gemini"`.
      - Combinación de parámetros de configuración mutuamente incompatibles.

    Esta excepción es de inicio (startup): si se lanza, el servicio afectado
    no debería haberse iniciado correctamente.
    """
