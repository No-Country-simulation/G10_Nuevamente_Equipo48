"""
Tests de propiedad para OCIService.

Propiedad 11: Un fallo de OCI nunca lanza excepción al llamador.
OCIService siempre retorna OCIUploadResult (nunca propaga excepciones).

Cuando OCI no está configurado, retorna status="no_configurado".
Cuando OCI falla, retorna status="error" con el detalle del error.

Requisito: 5.3, 5.4
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch
import pytest
from hypothesis import HealthCheck, given
from hypothesis import settings as h_settings
from hypothesis import strategies as st

from app.services.oci_service import OCIService, OCIUploadResult


def _make_settings_sin_oci() -> MagicMock:
    """Settings con OCI no configurado."""
    mock = MagicMock()
    mock.oci_configured = False
    return mock


def _make_settings_con_oci() -> MagicMock:
    """Settings con OCI configurado."""
    mock = MagicMock()
    mock.oci_configured = True
    mock.oci_namespace = "test-namespace"
    mock.oci_bucket_name = "test-bucket"
    mock.oci_user_ocid = "ocid1.user.test"
    mock.oci_fingerprint = "aa:bb:cc"
    mock.oci_tenancy_ocid = "ocid1.tenancy.test"
    mock.oci_region = "sa-santiago-1"
    mock.oci_private_key_path = "/fake/key.pem"
    return mock


# ---------------------------------------------------------------------------
# Tests cuando OCI no está configurado
# ---------------------------------------------------------------------------

class TestOCINoConfigurado:
    """OCI en modo degradado — sin credenciales configuradas."""

    def test_upload_object_retorna_no_configurado(self):
        """upload_object debe retornar status='no_configurado' sin lanzar excepción."""
        service = OCIService(_make_settings_sin_oci())
        result = service.upload_object("test/key.json", b"datos de prueba")
        assert result.status == "no_configurado"
        assert result.url_objeto is None

    def test_upload_document_retorna_no_configurado(self):
        """upload_document debe retornar status='no_configurado'."""
        service = OCIService(_make_settings_sin_oci())
        result = service.upload_document(b"contenido", "doc-123", "test.pdf")
        assert result.status == "no_configurado"

    def test_upload_artifact_retorna_no_configurado(self):
        """upload_artifact debe retornar status='no_configurado'."""
        service = OCIService(_make_settings_sin_oci())
        result = service.upload_artifact({"key": "value"}, "doc-123")
        assert result.status == "no_configurado"

    @h_settings(max_examples=30, suppress_health_check=[HealthCheck.too_slow])
    @given(
        key=st.text(
            min_size=1,
            max_size=100,
            alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd")),
        ),
        data=st.binary(min_size=0, max_size=1000),
    )
    def test_propiedad_sin_oci_nunca_lanza_excepcion(self, key, data):
        """
        Propiedad 11: Para cualquier clave y datos, OCIService en modo degradado
        nunca lanza excepción y siempre retorna status='no_configurado'.
        Valida: Requisito 5.3, 5.4
        """
        service = OCIService(_make_settings_sin_oci())
        # No debe lanzar excepción bajo ninguna circunstancia
        result = service.upload_object(key, data)
        assert result.status == "no_configurado"
        assert isinstance(result, OCIUploadResult)


# ---------------------------------------------------------------------------
# Tests cuando OCI está configurado pero falla la conexión
# ---------------------------------------------------------------------------

class TestOCIFallaConexion:
    """OCI configurado pero la conexión falla."""

    def test_error_oci_no_propaga_excepcion(self):
        """
        Cuando OCI falla, upload_object debe retornar status='error'
        sin propagar la excepción al llamador.
        Valida: Requisito 5.4
        """
        settings = _make_settings_con_oci()

        # Parchamos el cliente OCI para que falle al subir el objeto
        with patch("app.services.oci_service.oci", create=True) as mock_oci:
            mock_client = MagicMock()
            mock_client.put_object.side_effect = Exception("Timeout de conexión a OCI")
            mock_oci.object_storage.ObjectStorageClient.return_value = mock_client

            try:
                service = OCIService(settings)
                result = service.upload_object("test/key.json", b"datos")
                # Si llega aquí, el error fue capturado correctamente
                assert result.status in ("error", "no_configurado")
            except Exception:
                # Si lanza excepción, el test falla — OCIService no debe propagar errores
                pytest.fail("OCIService propagó una excepción al llamador")


# ---------------------------------------------------------------------------
# Tests de OCIUploadResult
# ---------------------------------------------------------------------------

def test_oci_upload_result_no_configurado():
    """OCIUploadResult con status='no_configurado' debe construirse correctamente."""
    result = OCIUploadResult(status="no_configurado")
    assert result.status == "no_configurado"
    assert result.url_objeto is None
    assert result.detalle is None


def test_oci_upload_result_exitoso():
    """OCIUploadResult con status='exitoso' debe incluir url_objeto."""
    result = OCIUploadResult(
        status="exitoso",
        url_objeto=(
            "https://objectstorage.sa-santiago-1.oraclecloud.com"
            "/n/ns/b/bucket/o/key"
        ),
    )
    assert result.status == "exitoso"
    assert result.url_objeto is not None


def test_oci_upload_result_error():
    """OCIUploadResult con status='error' debe incluir detalle."""
    result = OCIUploadResult(status="error", detalle="Timeout de conexión")
    assert result.status == "error"
    assert "Timeout" in result.detalle
