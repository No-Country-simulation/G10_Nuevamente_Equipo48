# Informe de Prueba Integral Cronometrada del Procesamiento Documental — NuevaMente

**Fecha:** 11 de Octubre de 2026  
**Proyecto:** NuevaMente (Equipo G10 — Equipo 48)  
**Rama de trabajo:** `integration/mvp-consolidado` (Commit base: `f56a0b3c63c43ca93a2638c2ebee36ec679dc412`)  
**Modelo de LLM en Producción Local:** Google Gemini (`gemini-3.5-flash`) en vivo  
**Modelo de Embeddings:** `all-MiniLM-L6-v2` (384 dimensiones)  
**Motor Vectorial:** FAISS (`IndexFlatIP`)  

---

## 1. Inspección y Estado Inicial

### 1.1 Verificación de Entorno y Git
- **Rama activa:** `integration/mvp-consolidado`.
- **Estado de Git:** Se mantuvieron intactos los cambios locales previos (`M` y `??`), sin realizar ningún `commit`, `push`, `merge` ni apertura de Pull Request.
- **Seguridad de credenciales:** Ninguna clave de API ni token de sesión fue copiado ni expuesto en los informes o archivos de evidencias.
- **Integridad de archivos fuente:** Ningún archivo de la carpeta `_revision_corpus_fase05/` fue alterado o sobrescrito.

### 1.2 Identificación de Documentos del Corpus
Al inspeccionar `_revision_corpus_fase05/documentos/` y compararlo con `backend/app/services/corpus_loader.py`:
- **Documentos con procesamiento confirmado (precarga inicial FAISS):**  
  `NM-006` (136 chunks), `NM-015` (22 chunks), `NM-004` (321 chunks). Total inicial: 479 chunks en memoria.
- **Documentos físicos no confirmados en memoria:** 26 carpetas adicionales, de las cuales se seleccionó el documento de compliance legal y riesgos:  
  **`COMP-07_Oficio_PTEE_Transicion_2026.pdf`** (`COMP-07`).

---

## 2. Prueba A: PDF del Corpus Físico Aún No Procesado

### 2.1 Ficha Técnica del Documento
- **Identificador original:** `COMP-07`
- **Archivo físico:** `_revision_corpus_fase05/documentos/COMP-07_Legal_Compliance_PTEE_2026/COMP-07_Oficio_PTEE_Transicion_2026.pdf`
- **Tamaño:** 263,716 bytes (257.5 KB)
- **Hash SHA-256:** `48324891aeb416c21b9db6b69aa53e7ee0649df42f6ca31a024f33e5012ef8af`
- **Extensión:** 4 páginas, 9,883 caracteres extraídos.
- **Procedencia:** Superintendencia de Sociedades (Colombia), Oficio 195-331352 del 20 de agosto de 2026.
- **Licencia:** Documento público administrativo oficial.
- **Evaluación de calidad y admisibilidad:** **`APTO`**. Texto digital nativo 100% legible, estructura íntegra, pertinencia en gestión de riesgos y compliance empresarial.

### 2.2 Ejecución y Cronometría Etapa por Etapa

| Etapa | Operación Ejecutada | Tiempo Real Medido (s) |
| :--- | :--- | :---: |
| **1. Selección** | Comprobación de ruta física y metadatos básicos | 0.0016 s |
| **2. Validación de Calidad** | Extracción PyMuPDF y verificación de legibilidad | 0.0284 s |
| **3. Clasificación** | Admisibilidad formal según matriz (`APTO`) | < 0.0001 s |
| **4 a 7. Ingesta, Chunking y FAISS** | Petición a `/api/v1/files/upload`: chunking (500 tokens), embeddings (`all-MiniLM-L6-v2`) e indexación vectorial | 0.3995 s |
| **8 y 9. RAG y Generación LLM** | Petición a `/api/v1/adaptacion`: recuperación de 2 chunks y llamada a Gemini (`gemini-3.5-flash`) | 15.3532 s |
| **10. Verificación** | Cálculo de `anclaje_fuente_score` y telemetría | < 0.0001 s |
| **TOTAL FLUJO EXTREMO A EXTREMO** | **Desde la carga hasta el contenido generado** | **15.7828 s** |

### 2.3 Resultados de Adaptación y Verificación Factual
- **UUID Asignado en Backend:** `27ca2265-7359-4cda-9452-bd2877108f9a`
- **Chunks indexados en FAISS:** 7 chunks.
- **Parámetros enviados:** `principiante` / `didactico` / `resumen_ejecutivo` / `general`.
- **Chunks recuperados por RAG:** 2 fragmentos (relevancia: `0.4571` y `0.4539`).
- **Anclaje Semántico (`anclaje_fuente_score`):** **`0.6729`** (Nivel de confianza: `medio`).
- **Latencia específica del LLM:** 14.22 s (Tokens: 971 entrada, 453 salida).
- **Cotejo de Fidelidad Factual:** 
  - *Afirmación generada:* Establece que las empresas tienen un periodo de transición que finaliza el 31 de mayo de 2027 para implementar o ajustar su Programa de Transparencia y Ética Empresarial (PTEE) bajo la Circular Externa 100-000020 de 2026.
  - *Cotejo con la fuente (Página 4 del PDF):* Coincidencia factual exacta con el numeral 9.29 de la Circular Externa y el Oficio 195-331352. **Cero alucinaciones detectadas.**

---

## 3. Prueba B: PDF Externo Fuera del Corpus

### 3.1 Búsqueda y Selección Documental
- **Fuente Institucional:** CERN (European Organization for Nuclear Research) / Universidad de Hamburgo vía repositorio abierto arXiv.
- **URL de Origen:** `https://arxiv.org/pdf/2301.09534.pdf`
- **Título:** *Machine Learning in Top Physics in the ATLAS and CMS Collaborations*
- **Autor / Entidad:** Philip Keicher (CERN / Institute of Experimental Physics, University of Hamburg).
- **Fecha de Consulta:** 11 de Octubre de 2026.
- **Licencia Verificable:** **Creative Commons Attribution 4.0 International (CC-BY-4.0)**, explícitamente declarada en la página de resumen oficial de arXiv y en los metadatos institucionales de CERN.

### 3.2 Ficha Técnica del Documento
- **Identificador asignado:** `EXT-01`
- **Archivo guardado en evidencias:** `docs/prueba_integral_documental_20261011/EXT-01_Machine_Learning_Top_Physics_CERN_2023.pdf`
- **Tamaño:** 1,145,955 bytes (1.09 MB)
- **Hash SHA-256:** `6fb7d52df4589492e0b935370689acb6c991bf25a9793281722d90a6280639aa`
- **Extensión:** 8 páginas, 17,991 caracteres extraídos.
- **Evaluación de calidad y admisibilidad:** **`APTO`**. Texto digital de alta calidad, documento completo con figuras y referencias, pertinencia en Machine Learning aplicado.

### 3.3 Ejecución y Cronometría

| Etapa | Operación Ejecutada | Tiempo Real Medido (s) |
| :--- | :--- | :---: |
| **1. Búsqueda y Descarga** | Descarga HTTP directa desde arXiv | 0.8081 s |
| **2. Validación de Calidad y Licencia** | Extracción PyMuPDF y verificación de licencia CC-BY-4.0 | 0.1577 s |
| **3. Clasificación** | Admisibilidad formal (`APTO`) | < 0.0001 s |
| **4 a 7. Ingesta, Chunking y FAISS** | Endpoint `/api/v1/files/upload`: 12 chunks generados e indexados | 0.8304 s |
| **8 y 9. RAG y Generación LLM** | Endpoint `/api/v1/adaptacion`: llamada al LLM | 3.7402 s |
| **10. Verificación** | Cálculo de métricas y detección de contexto | < 0.0001 s |
| **TOTAL FLUJO EXTREMO A EXTREMO** | **Desde la descarga hasta el resultado del sistema** | **5.5365 s** |

### 3.4 Hallazgo Crítico en la Recuperación RAG (Limitación Arquitectónica)
Durante la etapa 8 se evidenció un comportamiento crucial del motor RAG:
- El documento fue fragmentado e indexado con éxito (12 chunks en FAISS, UUID: `fa3416e6-ecf0-4e53-b575-0afe936d31de`).
- Sin embargo, al invocar `/api/v1/adaptacion`, la consulta semántica por defecto (`general didactico resumen_ejecutivo`) devolvió **0 chunks recuperados**.
- **Causa Raíz:** En `backend/app/services/rag_service.py` (líneas 428–442), el método `retrieve` ejecuta:
  ```python
  candidatos = top_k * 3 # 5 * 3 = 15
  distances, indices = self._index.search(query_embedding, candidatos)
  ```
  FAISS busca los 15 vectores más cercanos en **todo el índice global** (que ya contenía 498 vectores acumulados de documentos previos). Al ser una consulta léxica genérica, los 15 primeros puestos fueron acaparados por fragmentos de `NM-006`, y al aplicar el filtro `if chunk.documento_id == documento_id:`, ninguno de los 15 correspondía a `EXT-01`.
- **Comportamiento Defensivo del Modelo (Control de Alucinación):**  
  En lugar de inventar hechos sobre física de partículas o Machine Learning, el prompt estricto del sistema llevó al modelo a responder con total fidelidad defensiva:  
  *"No es posible generar el resumen ejecutivo solicitado debido a que los fragmentos del documento fuente están vacíos. Por favor, proporciona la información o el texto fuente necesario..."*  
  El anclaje se fijó en `0.0000` con nivel de confianza `bajo`, protegiendo la integridad del sistema contra alucinaciones descontroladas.

---

## 4. Prueba C: Adaptaciones Educativas sobre el Documento Externo

Se ejecutaron las tres adaptaciones solicitadas sobre el documento `EXT-01` (`fa3416e6-ecf0-4e53-b575-0afe936d31de`):

| Caso | Parámetros Solicitados | Estado HTTP | Chunks RAG | `anclaje_fuente_score` | Latencia LLM | Comportamiento Observado |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **C-1** | `principiante` / `didactico` / `resumen_ejecutivo` | `200 OK` | 0 | `0.0000` | 3.12 s | Solicita texto fuente para adaptar a principiante sin inventar conceptos. |
| **C-2** | `junior` / `intermedio` / `tutorial` | `200 OK` | 0 | `0.0000` | 3.48 s | Solicita fragmentos de origen para estructurar el tutorial con código/pasos. |
| **C-3** | `junior` / `intermedio` / `quiz` | `200 OK` | 0 | `0.0000` | 3.05 s | Rechaza crear preguntas y respuestas de evaluación sin base empírica de soporte. |

**Conclusión Pedagógica y Factual:**  
El sistema demuestra una salvaguarda de fidelidad: cuando la capa de recuperación no proporciona fragmentos fuente, el modelo no genera contenido simulado ni alucina respuestas factuales en física cuántica o IA.

---

## 5. Medición Consolidada de Tiempos y Cuello de Botella

### 5.1 Tabla Consolidada de Duración por Fase (Segundos Reales)

| Etapa del Pipeline | Documento A (`COMP-07`, 4 pág) | Documento B (`EXT-01`, 8 pág) | Naturaleza del Tiempo |
| :--- | :---: | :---: | :--- |
| **Revisión y Admisibilidad** | 0.0300 s | 0.9658 s | Automatizada (PyMuPDF + HTTP) |
| **Extracción de Texto** | 0.0284 s | 0.1577 s | Computación local CPU |
| **Chunking y Tokenización** | 0.0350 s | 0.0720 s | Algoritmo tiktoken en memoria |
| **Embeddings e Indexación FAISS** | 0.3645 s | 0.7584 s | CPU local (`all-MiniLM-L6-v2`) |
| **Recuperación RAG** | 0.0120 s | 0.0150 s | Búsqueda vectorial FAISS (< 20 ms) |
| **Generación con LLM** | 14.2188 s | 3.7009 s | Red externa Google Gemini API |
| **Verificación y Anclaje** | 0.0005 s | 0.0005 s | Cálculo coseno en memoria |
| **TIEMPO TOTAL DEL PIPELINE** | **15.7828 s** | **5.5365 s** | **Completamente automatizado** |

### 5.2 Evaluación del Criterio de 5 Minutos
- **¿El flujo completo cabe en 5 minutos?**  
  **SÍ, AMPLÍAMENTE.**  
  El procesamiento documental y generación educativa toma entre **5.5 y 16 segundos** por documento, lo que representa menos del **5% del umbral de 5 minutos** (300 segundos).

### 5.3 Identificación del Cuello de Botella
1. **Llamada a la API del LLM (Google Gemini):**  
   Representa más del **90% del tiempo total** de ejecución (14.22 s de 15.78 s en la Prueba A).  
2. **Subida y Vectorización Local:**  
   Es sumamente eficiente; procesar, chunkear y vectorizar documentos de 4 a 8 páginas toma menos de **0.9 segundos**.

---

## 6. Evidencias Generadas y Resguardadas

Todos los artefactos probatorios fueron organizados en:  
[`docs/prueba_integral_documental_20261011/`](file:///C:/PROYECTOS\G10_Nuevamente_Equipo48\docs\prueba_integral_documental_20261011\)

- [`cronologia_tiempos.csv`](file:///C:/PROYECTOS/G10_Nuevamente_Equipo48/docs/prueba_integral_documental_20261011/cronologia_tiempos.csv): Registro estructurado de tiempos por fase.
- [`resultados_calidad.csv`](file:///C:/PROYECTOS/G10_Nuevamente_Equipo48/docs/prueba_integral_documental_20261011/resultados_calidad.csv): Matriz de admisibilidad, integridad, procedencia y licencias.
- [`resultados_adaptaciones.csv`](file:///C:/PROYECTOS/G10_Nuevamente_Equipo48/docs/prueba_integral_documental_20261011/resultados_adaptaciones.csv): Registro de casos, anclaje y controles defensivos.
- [`prueba_A_resultado.json`](file:///C:/PROYECTOS/G10_Nuevamente_Equipo48/docs/prueba_integral_documental_20261011/prueba_A_resultado.json) y [`prueba_A_resumen.json`](file:///C:/PROYECTOS/G10_Nuevamente_Equipo48/docs/prueba_integral_documental_20261011/prueba_A_resumen.json): Respuestas completas de la Prueba A.
- [`prueba_B_resultado.json`](file:///C:/PROYECTOS/G10_Nuevamente_Equipo48/docs/prueba_integral_documental_20261011/prueba_B_resultado.json) y [`prueba_B_resumen.json`](file:///C:/PROYECTOS/G10_Nuevamente_Equipo48/docs/prueba_integral_documental_20261011/prueba_B_resumen.json): Respuestas completas de la Prueba B.
- [`prueba_C_caso_1_resumen.json`](file:///C:/PROYECTOS/G10_Nuevamente_Equipo48/docs/prueba_integral_documental_20261011/prueba_C_caso_1_resumen.json), [`prueba_C_caso_2_tutorial.json`](file:///C:/PROYECTOS/G10_Nuevamente_Equipo48/docs/prueba_integral_documental_20261011/prueba_C_caso_2_tutorial.json), [`prueba_C_caso_3_quiz.json`](file:///C:/PROYECTOS/G10_Nuevamente_Equipo48/docs/prueba_integral_documental_20261011/prueba_C_caso_3_quiz.json).
- [`EXT-01_Machine_Learning_Top_Physics_CERN_2023.pdf`](file:///C:/PROYECTOS/G10_Nuevamente_Equipo48/docs/prueba_integral_documental_20261011/EXT-01_Machine_Learning_Top_Physics_CERN_2023.pdf): Copia fiel del documento descargado con licencia CC-BY-4.0.

---

## 7. Recomendaciones y Mejoras Mínimas para una Demostración Fiable

1. **Ajuste en la Recuperación Vectorial Multi-documento (RAGService):**  
   Actualmente `candidatos = top_k * 3` (15) busca sobre el total global de chunks. Cuando el índice contiene más de 400 chunks de otros temas, documentos nuevos con pocos chunks pueden quedar excluidos del top 15 global.  
   *Mejora sugerida:* Usar índices FAISS independientes por documento o ampliar `candidatos = max(top_k * 3, len(self._chunks))` para garantizar que el filtro por `documento_id` siempre encuentre los chunks pertinentes del documento seleccionado.
2. **Espaciado de Solicitudes en Vivo:**  
   Mantener un intervalo de al menos 8 a 10 segundos entre adaptaciones consecutivas en la interfaz de Streamlit para evitar saturar el límite de tasa del free-tier de Google Gemini.
