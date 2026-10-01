"""
Servicio de integración con OCI Object Storage.

Gestiona la subida de documentos y artefactos al almacenamiento de Oracle Cloud.
Opera en modo degradado cuando OCI no está configurado, sin interrumpir el flujo
principal de generación de contenido.

Nunca lanza excepciones al llamador: todos los errores se capturan y se retornan
como OCIUploadResult con status="error".
"""

import io
import json
import logging
from dataclasses import dataclass, field

from app.core.config import Settings

logger = logging.getLogger(__name__)


@dataclass
class OCIUploadResult:
    """
    Resultado de una operación de subida a OCI Object Storage.

    Atributos:
        status:      Estado de la operación:
                       - "exitoso"        → objeto subido correctamente.
                       - "no_configurado" → OCI no está configurado; modo degradado.
                       - "error"          → la operación falló; ver `detalle`.
        url_objeto:  URL pública (o de acceso) al objeto subido. Solo presente
                     cuando status="exitoso".
        detalle:     Información adicional sobre el resultado o el error.
                     Útil para depuración; no se expone al cliente final.
    """

    status: str
    url_objeto: str | None = field(default=None)
    detalle: str | None = field(default=None)


class OCIService:
    """
    Servicio para operaciones con OCI Object Storage.

    Si OCI no está completamente configurado (faltan variables de entorno),
    el servicio opera en modo degradado: todas las operaciones retornan
    OCIUploadResult(status="no_configurado") sin intentar ninguna conexión.

    Nunca bloquea el flujo de generación de contenido — todos los errores
    se capturan internamente y se reflejan en el resultado retornado.
    """

    def __init__(self, settings: Settings) -> None:
        """
        Inicializa el servicio OCI.

        Args:
            settings: Instancia de configuración con las variables de entorno.
        """
        self._settings = settings
        self._client = None
        self._modo_degradado: bool = True  # Por defecto, modo seguro

        if not settings.oci_configured:
            # OCI no configurado — operar en modo degradado
            logger.warning(
                "OCI Object Storage no está configurado. El servicio operará en modo "
                "degradado: las subidas de documentos y artefactos serán omitidas. "
                "Configure las variables OCI_* en el archivo .env para habilitar OCI."
            )
            return

        # OCI configurado — intentar inicializar el cliente
        try:
            import oci  # Importación diferida: solo se necesita si OCI está configurado

            # Construir config desde variables de entorno (sin depender de ~/.oci/config)
            oci_config = {
                "user": settings.oci_user_ocid,
                "fingerprint": settings.oci_fingerprint,
                "tenancy": settings.oci_tenancy_ocid,
                "region": settings.oci_region,
                "key_file": settings.oci_private_key_path,
            }

            self._client = oci.object_storage.ObjectStorageClient(oci_config)
            self._modo_degradado = False
            logger.info(
                "OCI Object Storage inicializado correctamente. "
                "Namespace: %s | Bucket: %s",
                settings.oci_namespace,
                settings.oci_bucket_name,
            )

        except Exception as e:
            # Fallo en la inicialización → caer en modo degradado sin propagar el error
            logger.error(
                "Error al inicializar el cliente OCI Object Storage. "
                "Se activará el modo degradado. Detalle: %s",
                str(e),
                exc_info=True,
            )
            self._modo_degradado = True

    def upload_object(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> OCIUploadResult:
        """
        Sube un objeto binario a OCI Object Storage bajo la clave indicada.

        Args:
            key:          Nombre/ruta del objeto dentro del bucket (ej: "docs/abc/file.pdf").
            data:         Contenido binario del objeto a subir.
            content_type: Tipo MIME del contenido (por defecto "application/octet-stream").

        Returns:
            OCIUploadResult con:
              - status="no_configurado" si el servicio está en modo degradado.
              - status="exitoso" y url_objeto si la subida fue exitosa.
              - status="error" y detalle si la operación falló.

        Note:
            Este método NUNCA lanza excepciones al llamador.
        """
        # Modo degradado: retornar inmediatamente sin intentar ninguna subida
        if self._modo_degradado:
            return OCIUploadResult(status="no_configurado")

        try:
            # Realizar la subida al bucket configurado
            self._client.put_object(
                namespace_name=self._settings.oci_namespace,
                bucket_name=self._settings.oci_bucket_name,
                object_name=key,
                put_object_body=io.BytesIO(data),
                content_type=content_type,
            )

            # Construir la URL de acceso al objeto subido
            url_objeto = (
                f"https://objectstorage.{self._settings.oci_region}.oraclecloud.com"
                f"/n/{self._settings.oci_namespace}"
                f"/b/{self._settings.oci_bucket_name}"
                f"/o/{key}"
            )

            logger.info("Objeto subido exitosamente a OCI: %s", key)

            return OCIUploadResult(status="exitoso", url_objeto=url_objeto)

        except Exception as e:
            # Capturar cualquier error de OCI y retornar resultado de fallo
            logger.error(
                "Error al subir objeto a OCI Object Storage. "
                "Clave: %s | Detalle: %s",
                key,
                str(e),
                exc_info=True,
            )
            return OCIUploadResult(status="error", detalle=str(e))

    def upload_document(
        self,
        file_bytes: bytes,
        documento_id: str,
        filename: str,
    ) -> OCIUploadResult:
        """
        Sube el documento original al bucket OCI.

        La clave del objeto sigue la convención:
            documentos/{documento_id}/{filename}

        Args:
            file_bytes:    Contenido binario del documento.
            documento_id:  Identificador único del documento (UUID).
            filename:      Nombre original del archivo (ej: "manual.pdf").

        Returns:
            OCIUploadResult con el resultado de la operación.
        """
        # Determinar el Content-Type según la extensión del archivo
        content_type = _infer_content_type(filename)

        # Construir la clave del objeto en el bucket
        key = f"documentos/{documento_id}/{filename}"

        return self.upload_object(key, file_bytes, content_type)

    def upload_artifact(
        self,
        artefacto: dict,
        documento_id: str,
    ) -> OCIUploadResult:
        """
        Sube el artefacto JSON de adaptación al bucket OCI.

        El artefacto se serializa a JSON UTF-8 y se almacena bajo la clave:
            artefactos/{documento_id}/resultado.json

        Args:
            artefacto:     Diccionario con el resultado de la adaptación pedagógica.
            documento_id:  Identificador único del documento fuente (UUID).

        Returns:
            OCIUploadResult con el resultado de la operación.
        """
        # Serializar el artefacto a bytes JSON (UTF-8, sin escapar caracteres no-ASCII).
        # Se usa default=str para serializar tipos no nativos de JSON (datetime, UUID, etc.)
        json_bytes = json.dumps(artefacto, ensure_ascii=False, default=str).encode("utf-8")

        # Construir la clave del objeto en el bucket
        key = f"artefactos/{documento_id}/resultado.json"

        return self.upload_object(key, json_bytes, "application/json")


# ---------------------------------------------------------------------------
# Utilidades internas
# ---------------------------------------------------------------------------

def _infer_content_type(filename: str) -> str:
    """
    Infiere el Content-Type MIME a partir de la extensión del nombre de archivo.

    Soporta los tipos aceptados por el endpoint de upload: PDF, Markdown y TXT.
    Para extensiones no reconocidas retorna "application/octet-stream".

    Args:
        filename: Nombre del archivo con extensión (ej: "documento.pdf").

    Returns:
        Cadena MIME type correspondiente.
    """
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    tipos = {
        "pdf": "application/pdf",
        "md": "text/markdown",
        "markdown": "text/markdown",
        "txt": "text/plain",
    }

    return tipos.get(extension, "application/octet-stream")
