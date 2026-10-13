# Informe de Pruebas Técnicas y Cobertura — NuevaMente MVP

**Fecha:** 2026-10-11  
**Repositorio:** `C:\PROYECTOS\G10_Nuevamente_Equipo48`  
**Entorno de Pruebas:** Python 3.12.10, Pytest 8.3.3, Starlette TestClient, FAISS (AVX2), SentenceTransformer (`all-MiniLM-L6-v2`).

---

## 1. Resumen Consolidado de la Suite Automatizada

Se ejecutó la suite completa de pruebas unitarias e integración en `backend/backend/tests/`:

```powershell
$env:PYTHONPATH = "C:\PROYECTOS\G10_Nuevamente_Equipo48;C:\PROYECTOS\G10_Nuevamente_Equipo48\backend\backend"
.\backend\backend\.venv\Scripts\python.exe -m pytest backend/backend/tests -v --tb=short
```

| Módulo de Pruebas | Alcance Evaluado | Total Tests | Aprobados | Fallidos |
| :--- | :--- | :---: | :---: | :---: |
| `test_schemas.py` | Esquemas Pydantic, contratos de entrada/salida, enums | 58 | 58 | 0 |
| `test_document_service.py` | Extracción PDF, Markdown, TXT, validación MIME | 22 | 22 | 0 |
| `test_rag_service.py` | Chunking de tokens, normalización L2, indexación FAISS, búsqueda | 17 | 17 | 0 |
| `test_llm_service.py` | Clientes OpenAI/Gemini, telemetría, reintentos y excepciones | 17 | 17 | 0 |
| `test_agent_service.py` | Orquestación RAG + LLM, prompts, evaluación de calidad | 32 | 32 | 0 |
| `test_oci_service.py` | Subida de archivos, modo degradado sin credenciales | 8 | 8 | 0 |
| `test_corpus_loader.py` | Precarga estricta APTO, idempotencia, resiliencia ante errores | 12 | 12 | 0 |
| `test_health.py` | Endpoint de salud `/health` | 5 | 5 | 0 |
| `test_error_handling.py` | Excepciones globales (404, 422, 502, 503) | 15 | 15 | 0 |
| `test_adaptacion.py` | Integración E2E del endpoint `/api/v1/adaptacion` | 41 | 41 | 0 |
| `test_frontend_client.py` | Cliente HTTP de Streamlit frente a la API | 12 | 12 | 0 |
| **TOTAL GENERAL** | **Suite Completa Consolidada** | **239** | **239 (100%)** | **0** |

---

## 2. Pruebas de Casos Adversos y Negativos en Vivo

Se ejecutaron pruebas directas contra el servidor FastAPI en vivo (`http://127.0.0.1:8000/api/v1/adaptacion`) para evaluar el comportamiento ante entradas anómalas:

1. **`NEG-01` (Documento Inexistente):**
   - Entrada: `documento_id: "NM-INEXISTENTE-999"`.
   - Resultado: **HTTP 404 Not Found**. Mensaje descriptivo indicando ausencia de fragmentos indexados.
   - Estado: `PASO`.
2. **`NEG-02` (Parámetros Inválidos):**
   - Entrada: `perfil_destinatario: "perfil_invalido"`.
   - Resultado: **HTTP 422 Unprocessable Entity**. Mensaje descriptivo en español indicando el campo inválido y las opciones permitidas.
   - Estado: `PASO`.
3. **`NEG-03` (Documento No Precargado):**
   - Entrada: `documento_id: "NM-002"` (documento existente en corpus pero reservado para ingesta bajo demanda).
   - Resultado: **HTTP 404 Not Found**. El sistema no inventa contenido y comunica con precisión que no está en el índice activo.
   - Estado: `PASO`.
4. **`NEG-04` (Saturación de Cuota del LLM):**
   - Entrada: Disparo rápido de peticiones sobrepasando la cuota del tier gratuito de Gemini.
   - Resultado: **HTTP 502 Bad Gateway**. Respuesta controlada con mensaje de reintento posterior, sin interrupción del servidor uvicorn.
   - Estado: `PASO`.

---

## 3. Bloqueos Técnicos y Dependencias Externas

- **OCI Object Storage:**
  - El servicio opera correctamente en **modo degradado seguro** (`status_upload: 'no_configurado'`).
  - No constituye bloqueo para la ejecución local ni para la demostración del flujo pedagógico.
- **Cuota de API Gemini:**
  - Se recomienda espaciar las solicitudes al menos 10-15 segundos en demostraciones en vivo, o utilizar una clave de API con cuota ampliada.
