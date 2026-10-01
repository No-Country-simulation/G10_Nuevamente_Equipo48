"""
Configuración central de NuevaMente Backend.
Lee todas las variables de entorno desde el archivo .env mediante pydantic-settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Clase de configuración principal del sistema.
    Todos los valores se leen desde variables de entorno o desde el archivo .env
    ubicado en el directorio de trabajo al momento de iniciar la aplicación.
    """

    # -------------------------------------------------------------------------
    # Configuración del proveedor LLM
    # -------------------------------------------------------------------------
    # Proveedor del modelo de lenguaje: "openai" o "google_gemini"
    llm_provider: str = "openai"
    # Nombre del modelo a utilizar (ej: "gpt-4o-mini", "gemini-pro")
    llm_model: str = "gpt-4o-mini"
    # Clave de autenticación de la API del LLM (nunca incluir en el código)
    llm_api_key: str = ""

    # -------------------------------------------------------------------------
    # Configuración del modelo de embeddings
    # -------------------------------------------------------------------------
    # Nombre del modelo sentence-transformers o identificador de OpenAI
    embedding_model: str = "all-MiniLM-L6-v2"

    # -------------------------------------------------------------------------
    # Configuración del pipeline RAG
    # -------------------------------------------------------------------------
    # Tamaño máximo de cada fragmento (chunk) en tokens
    rag_chunk_size: int = 500
    # Número de fragmentos más relevantes a recuperar por consulta
    rag_top_k: int = 5
    # Tipo de almacén vectorial: "faiss" o "chroma"
    vector_store_type: str = "faiss"

    # -------------------------------------------------------------------------
    # Configuración de OCI Object Storage
    # -------------------------------------------------------------------------
    # Namespace del tenancy en OCI
    oci_namespace: str = ""
    # Nombre del bucket donde se almacenan documentos y artefactos
    oci_bucket_name: str = ""
    # OCID del usuario de OCI
    oci_user_ocid: str = ""
    # Fingerprint de la clave pública registrada en OCI
    oci_fingerprint: str = ""
    # OCID del tenancy en OCI
    oci_tenancy_ocid: str = ""
    # Región de OCI (ej: "us-ashburn-1", "sa-saopaulo-1")
    oci_region: str = ""
    # Ruta al archivo de clave privada PEM para autenticación OCI
    oci_private_key_path: str = ""

    # -------------------------------------------------------------------------
    # Configuración de CORS
    # -------------------------------------------------------------------------
    # Lista de orígenes permitidos separados por coma. Usar "*" para permitir todos.
    cors_allowed_origins: str = "*"

    # -------------------------------------------------------------------------
    # Configuración de pydantic-settings
    # -------------------------------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        # Permite sobreescribir valores con variables de entorno del sistema
        env_file_encoding="utf-8",
    )

    # -------------------------------------------------------------------------
    # Propiedades calculadas
    # -------------------------------------------------------------------------

    @property
    def cors_origins_list(self) -> list[str]:
        """
        Retorna la lista de orígenes CORS permitidos.
        Divide la cadena `cors_allowed_origins` por comas y elimina espacios.
        """
        return [origen.strip() for origen in self.cors_allowed_origins.split(",")]

    @property
    def oci_configured(self) -> bool:
        """
        Retorna True si todas las variables requeridas de OCI están configuradas.
        Si alguna está vacía, el servicio OCI opera en modo degradado.
        """
        campos_requeridos = [
            self.oci_namespace,
            self.oci_bucket_name,
            self.oci_user_ocid,
            self.oci_fingerprint,
            self.oci_tenancy_ocid,
            self.oci_region,
            self.oci_private_key_path,
        ]
        return all(campos_requeridos)

    @property
    def llm_configured(self) -> bool:
        """
        Retorna True si la clave de API del LLM está presente y no está vacía.
        """
        return bool(self.llm_api_key)


# Instancia singleton: importar desde otros módulos con `from app.core.config import settings`
settings = Settings()
