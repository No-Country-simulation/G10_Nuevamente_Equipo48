"""
Tests para el endpoint GET /health.

Verifica que:
- El endpoint responde con HTTP 200.
- El cuerpo de la respuesta contiene {"status": "ok", "service": "nuevamente-backend"}.
- El tiempo de respuesta es menor a 500ms.
"""

import time

import pytest
from starlette.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """
    TestClient sin servicios reales para el health check.

    El endpoint /health no depende de ningún servicio externo, por lo que
    se usa raise_server_exceptions=False para aislar el test del ciclo de
    vida completo de la app (lifespan), evitando fallos por falta de
    credenciales de LLM u OCI en el entorno de CI.
    """
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


class TestHealthEndpoint:
    """Tests del endpoint GET /health."""

    def test_health_returns_200(self, client):
        """El endpoint /health debe retornar HTTP 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_correct_body(self, client):
        """El endpoint /health debe retornar el body exacto esperado."""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "nuevamente-backend"

    def test_health_response_keys(self, client):
        """La respuesta debe contener exactamente los campos 'status' y 'service'."""
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert "service" in data

    def test_health_responds_under_500ms(self, client):
        """El endpoint debe responder en menos de 500ms."""
        inicio = time.perf_counter()
        response = client.get("/health")
        duracion_ms = (time.perf_counter() - inicio) * 1000
        assert response.status_code == 200
        assert duracion_ms < 500, (
            f"La respuesta tardó {duracion_ms:.1f}ms (límite: 500ms)"
        )

    def test_health_content_type_json(self, client):
        """La respuesta debe tener Content-Type application/json."""
        response = client.get("/health")
        assert "application/json" in response.headers.get("content-type", "")
