# NuevaMente Backend

Sistema Inteligente de Adaptación y Generación de Contenido Educativo.

Recibe documentos técnicos (PDF, Markdown, TXT), los procesa mediante un pipeline RAG (Retrieval-Augmented Generation) con embeddings reales y FAISS, y genera artefactos pedagógicos personalizados usando modelos LLM (OpenAI o Google Gemini), adaptados al perfil del destinatario, formato, sector y nivel de detalle requerido.

---

## Arquitectura

```
backend/
├── app/
│   ├── main.py                          # App FastAPI, CORS, routers, manejadores de error
│   ├── api/v1/endpoints/
│   │   ├── health.py                    # GET /health
│   │   ├── files.py                     # POST /api/v1/files/upload
│   │   └── adaptacion.py               # POST /api/v1/adaptacion
│   ├── core/
│   │   ├── config.py                    # Settings con pydantic-settings
│   │   └── exceptions.py               # Jerarquía de excepciones del dominio
│   ├── schemas/
│   │   ├── adaptacion.py               # Enums, AdaptacionRequest/Response
│   │   └── file.py                      # UploadResponse, ErrorResponse
│   └── services/
│       ├── document_service.py         # Extracción de texto PDF/MD/TXT
│       ├── rag_service.py              # Chunking + embeddings + FAISS
│       ├── llm_service.py              # Abstracción OpenAI / Google Gemini
│       ├── agent_service.py            # Orquestador del flujo completo
│       └── oci_service.py              # OCI Object Storage (con degradación elegante)
├── tests/
│   ├── conftest.py                      # Fixtures y mocks compartidos
│   ├── test_health.py
│   ├── test_schemas.py
│   └── test_adaptacion.py
├── main.py                              # Punto de entrada para uvicorn
├── requirements.txt
├── .env.example
└── .gitignore
```

**Decisiones técnicas clave:**

| Componente | Elección | Razón |
|---|---|---|
| Framework | FastAPI | Validación Pydantic nativa, OpenAPI automático |
| Vector Store | FAISS | Sin servidor, embebido, ideal para MVP |
| Embeddings | sentence-transformers `all-MiniLM-L6-v2` | Gratuito, local, sin API key |
| Embeddings (alt.) | OpenAI `text-embedding-ada-002` | Si `LLM_PROVIDER=openai` |
| PDF | PyMuPDF (fitz) | Extracción robusta de texto real |
| Orquestación | Agent Service propio | Sin LangChain, dependencias mínimas |
| OCI | SDK oficial `oci` | Integración con OCI Object Storage |

---

## Instalación

### 1. Clonar y posicionarse en la carpeta del backend

```bash
cd backend
```

### 2. Crear entorno virtual

```bash
python -m venv venv
```

### 3. Activar el entorno virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux / macOS:**
```bash
source venv/bin/activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

> **Nota:** La instalación de `sentence-transformers` y `faiss-cpu` puede tardar varios minutos. La primera vez que se use `sentence-transformers`, descargará el modelo `all-MiniLM-L6-v2` (~80 MB).

---

## Configuración

### 1. Copiar el archivo de variables de entorno

```bash
cp .env.example .env
```

### 2. Editar `.env` con tus valores

```env
# --- LLM (obligatorio para el endpoint /api/v1/adaptacion) ---
LLM_PROVIDER=openai          # openai | google_gemini
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=sk-...           # Tu API key real (nunca subir al repositorio)

# --- Embeddings ---
EMBEDDING_MODEL=all-MiniLM-L6-v2   # Modelo local gratuito (recomendado para desarrollo)

# --- RAG ---
RAG_CHUNK_SIZE=500
RAG_TOP_K=5
VECTOR_STORE_TYPE=faiss

# --- OCI (opcional — si no se configura, el sistema opera sin almacenamiento cloud) ---
OCI_NAMESPACE=
OCI_BUCKET_NAME=
OCI_USER_OCID=
OCI_FINGERPRINT=
OCI_TENANCY_OCID=
OCI_REGION=
OCI_PRIVATE_KEY_PATH=

# --- CORS ---
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## Iniciar el servidor

Desde la carpeta `backend/`:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

O directamente apuntando al módulo de la app:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

El servidor estará disponible en: **http://localhost:8000**

---

## Documentación interactiva

Una vez iniciado el servidor:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

---

## Endpoints

### GET /health

Verifica que el servicio está disponible.

**Request:**
```
GET http://localhost:8000/health
```

**Response (200):**
```json
{
  "status": "ok",
  "service": "nuevamente-backend"
}
```

---

### POST /api/v1/files/upload

Carga un documento (PDF, Markdown o TXT), extrae el texto, lo indexa en FAISS para RAG, y opcionalmente lo sube a OCI Object Storage.

**Request:** `multipart/form-data`

| Campo | Tipo | Descripción |
|---|---|---|
| `file` | File | Archivo PDF, .md o .txt (máx. 50 MB) |

**Ejemplo con curl:**
```bash
curl -X POST http://localhost:8000/api/v1/files/upload \
  -F "file=@documento_tecnico.pdf"
```

**Response (200):**
```json
{
  "status": "ok",
  "documento_id": "3f8a1b2c-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
  "filename": "documento_tecnico.pdf",
  "chunks_indexados": 24,
  "oci_status": "no_configurado"
}
```

**Errores posibles:**

| Código | Causa |
|---|---|
| 413 | Archivo mayor a 50 MB |
| 415 | Tipo de archivo no soportado (no es PDF, MD o TXT) |
| 422 | No se adjuntó archivo, o el archivo no tiene texto extraíble |

---

### POST /api/v1/adaptacion

Genera contenido educativo adaptado a partir de un documento previamente cargado.

**Request:** `application/json`

```json
{
  "documento_id": "3f8a1b2c-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
  "perfil_destinatario": "principiante",
  "formato_salida": "tutorial",
  "nicho": "general",
  "nivel_detalle": "didactico"
}
```

**Valores permitidos:**

| Campo | Valores |
|---|---|
| `perfil_destinatario` | `principiante` · `junior` · `lider_tecnico` · `ejecutivo` |
| `formato_salida` | `tutorial` · `flashcards` · `quiz` · `resumen_ejecutivo` · `guion_clase` |
| `nicho` | `fintech` · `salud` · `ecommerce` · `general` |
| `nivel_detalle` | `didactico` · `intermedio` · `tecnico` |

**Response (200):**
```json
{
  "status": "ok",
  "document_id": "3f8a1b2c-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
  "metadatos": {
    "documento_id": "3f8a1b2c-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
    "perfil_destinatario": "principiante",
    "formato_salida": "tutorial",
    "nicho": "general",
    "nivel_detalle": "didactico",
    "timestamp": "2024-11-01T14:30:00",
    "fragmentos_usados": 5
  },
  "contenido_adaptado": "Paso 1: ...\nPaso 2: ...",
  "evaluacion_calidad": {
    "anclaje_fuente_score": 0.82,
    "fragmentos_evaluados": 5,
    "nivel_confianza": "alto"
  },
  "fuentes": [
    {
      "chunk_id": "a1b2c3d4-...",
      "texto": "Fragmento del documento fuente...",
      "posicion": 0,
      "score_relevancia": 0.91
    }
  ],
  "almacenamiento_oci": {
    "status_upload": "no_configurado",
    "url_objeto": null,
    "detalle": null
  }
}
```

**Errores posibles:**

| Código | Causa |
|---|---|
| 404 | `documento_id` no existe (documento no cargado) |
| 422 | Parámetros inválidos o campos faltantes |
| 503 | LLM no configurado (`LLM_API_KEY` ausente) |
| 502 | Error en la llamada al API del LLM |

---

## Escenarios de prueba

### Escenario 1 — Documento OCI/VCN para principiantes

1. Subir un PDF sobre OCI/VCN:
```bash
curl -X POST http://localhost:8000/api/v1/files/upload \
  -F "file=@oci_vcn_guide.pdf"
```

2. Generar tutorial paso a paso:
```json
{
  "documento_id": "<id_del_paso_anterior>",
  "perfil_destinatario": "principiante",
  "formato_salida": "tutorial",
  "nicho": "general",
  "nivel_detalle": "didactico"
}
```

---

### Escenario 2 — Documento técnico para desarrolladores

1. Subir documentación técnica:
```bash
curl -X POST http://localhost:8000/api/v1/files/upload \
  -F "file=@api_docs.md"
```

2. Generar flashcards para e-commerce:
```json
{
  "documento_id": "<id_del_paso_anterior>",
  "perfil_destinatario": "junior",
  "formato_salida": "flashcards",
  "nicho": "ecommerce",
  "nivel_detalle": "intermedio"
}
```

---

### Escenario 3 — Documento ejecutivo para fintech

1. Subir informe técnico:
```bash
curl -X POST http://localhost:8000/api/v1/files/upload \
  -F "file=@technical_report.pdf"
```

2. Generar resumen ejecutivo:
```json
{
  "documento_id": "<id_del_paso_anterior>",
  "perfil_destinatario": "ejecutivo",
  "formato_salida": "resumen_ejecutivo",
  "nicho": "fintech",
  "nivel_detalle": "didactico"
}
```

---

## Ejecutar tests

Desde la carpeta `backend/` con el entorno virtual activado:

```bash
pytest tests/ -v
```

Para ver solo los fallos:
```bash
pytest tests/ -v --tb=short
```

> Los tests **no requieren credenciales reales**. Todos los servicios externos (LLM, OCI, embeddings) se mockean automáticamente.

---

## Configuración LLM

### OpenAI

```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=sk-proj-...
EMBEDDING_MODEL=text-embedding-ada-002
```

Obtén tu API key en: https://platform.openai.com/api-keys

### Google Gemini

```env
LLM_PROVIDER=google_gemini
LLM_MODEL=gemini-1.5-flash
LLM_API_KEY=AIza...
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

Obtén tu API key en: https://aistudio.google.com/app/apikey

> Si `LLM_API_KEY` no está configurado, el endpoint `/api/v1/adaptacion` responderá con HTTP 503 y un mensaje descriptivo. El endpoint `/api/v1/files/upload` funciona sin LLM.

---

## Configuración OCI Object Storage

OCI es **completamente opcional**. Si no se configura, el sistema funciona normalmente y los campos de almacenamiento retornan `"no_configurado"`.

Para activar OCI:

```env
OCI_NAMESPACE=axxxxxxxxxxx
OCI_BUCKET_NAME=nuevamente-bucket
OCI_USER_OCID=ocid1.user.oc1..aaaa...
OCI_FINGERPRINT=aa:bb:cc:dd:...
OCI_TENANCY_OCID=ocid1.tenancy.oc1..aaaa...
OCI_REGION=sa-santiago-1
OCI_PRIVATE_KEY_PATH=/ruta/a/tu/clave_privada.pem
```

Requisitos:
- Usuario OCI con permisos de escritura en el bucket
- Clave privada PEM generada y registrada en OCI IAM
- El bucket debe existir previamente

---

## Integración con Frontend

Esta sección permite que cualquier integrante del equipo conecte el frontend **sin necesitar consultar al backend developer**.

### URL Base

```
http://localhost:8000
```

En producción, reemplazar con la URL del servidor donde esté desplegado el backend.

### CORS

Para desarrollo local, el backend acepta cualquier origen (`*` por defecto).

Para producción, configurar en `.env`:
```env
CORS_ALLOWED_ORIGINS=https://tu-dominio-frontend.com,http://localhost:3000
```

---

### Flujo de integración

```
1. Usuario sube documento
   → Frontend: POST /api/v1/files/upload (multipart/form-data)
   → Backend retorna: { "documento_id": "uuid", "chunks_indexados": N, ... }

2. Usuario selecciona parámetros y solicita adaptación
   → Frontend: POST /api/v1/adaptacion (JSON)
   → Backend retorna: AdaptacionResponse con el contenido generado

3. Frontend muestra el resultado al usuario
```

---

### Endpoint 1: Subir documento

```
POST http://localhost:8000/api/v1/files/upload
Content-Type: multipart/form-data
```

**Body:** form-data con campo `file` (File)

**Ejemplo JavaScript (fetch):**
```javascript
const formData = new FormData();
formData.append('file', archivoSeleccionado);

const response = await fetch('http://localhost:8000/api/v1/files/upload', {
  method: 'POST',
  body: formData
  // No agregar Content-Type manualmente — el browser lo gestiona con el boundary
});

const data = await response.json();
const documentoId = data.documento_id; // Guardar este ID para el siguiente paso
```

**Respuesta exitosa (200):**
```json
{
  "status": "ok",
  "documento_id": "3f8a1b2c-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
  "filename": "mi_documento.pdf",
  "chunks_indexados": 24,
  "oci_status": "no_configurado"
}
```

---

### Endpoint 2: Generar contenido adaptado

```
POST http://localhost:8000/api/v1/adaptacion
Content-Type: application/json
```

**Body:**
```json
{
  "documento_id": "3f8a1b2c-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
  "perfil_destinatario": "principiante",
  "formato_salida": "tutorial",
  "nicho": "general",
  "nivel_detalle": "didactico"
}
```

**Ejemplo JavaScript (fetch):**
```javascript
const response = await fetch('http://localhost:8000/api/v1/adaptacion', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    documento_id: documentoId,
    perfil_destinatario: 'principiante',
    formato_salida: 'tutorial',
    nicho: 'general',
    nivel_detalle: 'didactico'
  })
});

const data = await response.json();

// Campos disponibles para mostrar en el UI:
console.log(data.contenido_adaptado);                          // El contenido generado
console.log(data.metadatos.fragmentos_usados);                 // Nº de fragmentos usados
console.log(data.evaluacion_calidad.anclaje_fuente_score);    // Score 0.0 - 1.0
console.log(data.evaluacion_calidad.nivel_confianza);          // "alto" | "medio" | "bajo"
console.log(data.fuentes);                                     // Fragmentos fuente usados
console.log(data.almacenamiento_oci.status_upload);            // Estado de almacenamiento
```

---

### Manejo de errores en el frontend

Todos los errores retornan JSON con la estructura:

```json
{
  "error": "Descripción del error en español",
  "detalle": "Información adicional para diagnóstico"
}
```

**Tabla de códigos HTTP:**

| Código | Causa | Acción sugerida en el UI |
|---|---|---|
| 200 | Éxito | Mostrar contenido |
| 404 | Documento no encontrado | "El documento no fue cargado. Intenta subirlo nuevamente." |
| 413 | Archivo demasiado grande | "El archivo supera el límite de 50 MB." |
| 415 | Tipo de archivo no soportado | "Solo se aceptan archivos PDF, Markdown (.md) y texto (.txt)." |
| 422 | Datos inválidos | Mostrar `detalle` del error para guiar al usuario |
| 503 | LLM no configurado | "El servicio de generación no está disponible. Contacta al administrador." |
| 502 | Error en el LLM | "Error al generar el contenido. Intenta nuevamente." |
| 500 | Error interno | "Error inesperado. Contacta al equipo técnico." |

**Ejemplo de manejo de errores:**
```javascript
const response = await fetch('http://localhost:8000/api/v1/adaptacion', { ... });

if (!response.ok) {
  const error = await response.json();
  
  switch (response.status) {
    case 404:
      mostrarError("Documento no encontrado. Por favor sube el documento nuevamente.");
      break;
    case 503:
      mostrarError("El servicio de IA no está disponible en este momento.");
      break;
    case 422:
      mostrarError(`Datos inválidos: ${error.detalle}`);
      break;
    default:
      mostrarError(error.error || "Error desconocido");
  }
  return;
}

const data = await response.json();
// Procesar respuesta exitosa...
```

---

### Campos del contenido adaptado por formato

El campo `contenido_adaptado` varía según el `formato_salida`:

| Formato | Tipo de `contenido_adaptado` | Descripción |
|---|---|---|
| `tutorial` | `string` | Texto con pasos numerados |
| `resumen_ejecutivo` | `string` | Párrafos con contexto, puntos clave y recomendaciones |
| `guion_clase` | `string` | Estructura de clase con introducción, desarrollo y cierre |
| `flashcards` | `array` o `string` | Lista `[{"pregunta": "...", "respuesta": "..."}]` si el LLM retornó JSON válido, o string en caso contrario |
| `quiz` | `array` o `string` | Lista `[{"pregunta": "...", "opciones": [...], "respuesta_correcta": "A", "justificacion": "..."}]` si es JSON válido, o string |

> Para `flashcards` y `quiz`, el frontend debe verificar si `contenido_adaptado` es un array (JSON estructurado) o un string, y renderizarlo apropiadamente en ambos casos.

---

### Nota sobre persistencia

El índice FAISS y los metadatos de documentos se mantienen **en memoria**. Al reiniciar el servidor, los documentos deben volver a cargarse. En una versión futura se añadirá persistencia en disco o en base de datos.

---

## Variables de entorno — Referencia completa

| Variable | Obligatoria | Default | Descripción |
|---|---|---|---|
| `LLM_PROVIDER` | Para adaptacion | `openai` | Proveedor LLM: `openai` o `google_gemini` |
| `LLM_MODEL` | Para adaptacion | `gpt-4o-mini` | Nombre del modelo |
| `LLM_API_KEY` | Para adaptacion | _(vacío)_ | API key del proveedor LLM |
| `EMBEDDING_MODEL` | No | `all-MiniLM-L6-v2` | Modelo de embeddings |
| `RAG_CHUNK_SIZE` | No | `500` | Tokens por fragmento (50-2000) |
| `RAG_TOP_K` | No | `5` | Fragmentos a recuperar por búsqueda (1-20) |
| `VECTOR_STORE_TYPE` | No | `faiss` | Tipo de almacén vectorial |
| `OCI_NAMESPACE` | No | _(vacío)_ | Namespace OCI |
| `OCI_BUCKET_NAME` | No | _(vacío)_ | Nombre del bucket OCI |
| `OCI_USER_OCID` | No | _(vacío)_ | OCID del usuario OCI |
| `OCI_FINGERPRINT` | No | _(vacío)_ | Fingerprint de la clave OCI |
| `OCI_TENANCY_OCID` | No | _(vacío)_ | OCID del tenancy OCI |
| `OCI_REGION` | No | _(vacío)_ | Región OCI (ej: `sa-santiago-1`) |
| `OCI_PRIVATE_KEY_PATH` | No | _(vacío)_ | Ruta a la clave privada PEM de OCI |
| `CORS_ALLOWED_ORIGINS` | No | `*` | Orígenes CORS permitidos (separados por coma) |

---

Desarrollado para el equipo G10 · Hackaton Oracle Nube 2024
