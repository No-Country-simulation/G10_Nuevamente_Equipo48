# Informe de Auditoría del Corpus Documental — NuevaMente MVP

**Fecha:** 2026-10-11  
**Repositorio:** `C:\PROYECTOS\G10_Nuevamente_Equipo48`  
**Rama:** `integration/mvp-consolidado` (Commit base: `f56a0b3c63c43ca93a2638c2ebee36ec679dc412`)  
**Directorio analizado:** `_revision_corpus_fase05/`  

---

## 1. Resumen Ejecutivo de la Auditoría del Corpus

Se evaluaron los 22 documentos registrados en la auditoría integral de Fase 05 (`auditoria_integral_fase05_rev5.md`) y el inventario materializado en disco.

| Estado de Evaluación | Total Registros | Físicamente Verificados | Formato Principal | Integridad Textual |
| :--- | :---: | :---: | :---: | :---: |
| **APTO** | 12 | 12 | PDF / Repo | 100% legibles, texto extraíble |
| **APTO_CON_REVISIÓN** | 8 | 8 | PDF / HTML / Repo | 100% legibles (condiciones pendientes) |
| **NO_APTO** | 2 | 0 (No materializados) | N/A | Excluidos por licencia restrictiva |
| **Documentos Comparativos (COMP)** | 11 | 11 | PDF / HTML | Disponibles en subcarpetas |
| **Total Global Auditado** | **33** | **31 en disco** | PDF (22), HTML (3), MD/Git (6) | **0 archivos corruptos detectados** |

---

## 2. Integridad Documental y Extracción Textual

Se ejecutó una prueba de lectura y extracción mediante `DocumentService` (PyMuPDF) sobre los 22 archivos PDF físicos del repositorio:

| Archivo | Tamaño (Bytes) | Caracteres Extraídos | Estado Extracción | SHA-256 (prefijo) |
| :--- | :---: | :---: | :---: | :---: |
| `NM-001_Fundamentos_Programacion_Python.pdf` | 6.882.391 | 356.705 | APROBADO (OK) | `a8a273f011...` |
| `NM-002_Think_Python_3e_Espanol.pdf` | 6.799.471 | 432.754 | APROBADO (OK) | `f59643079a...` |
| `NM-004_Diseno_de_base_de_datos.pdf` | 1.083.273 | 485.109 | APROBADO (OK) | `5f0a44d15a...` |
| `NM-006_Manual_de_Ciberseguridad_OSC.pdf` | 12.117.201 | 231.558 | APROBADO (OK) | `d366e6ebf4...` |
| `NM-007_ESP32_en_el_Aula.pdf` | 12.426.137 | 224.851 | APROBADO (OK) | `dca7b33b28...` |
| `NM-008_Electronica_Digital.pdf` | 9.615.984 | 126.207 | APROBADO (OK) | `fa7fb6436a...` |
| `NM-009_Energia_Solar_Fotovoltaica.pdf` | 13.378.020 | 484.523 | APROBADO (OK) | `adc27fa0da...` |
| `NM-010_Sistemas_Informacion_Geografica.pdf` | 47.431.681 | 1.781.797 | APROBADO (OK) | `572534c46d...` |
| `NM-011_Desarrollo_Aplicaciones_Moviles_Google_Cloud.pdf` | 12.475.105 | 620.209 | APROBADO (OK) | `2b0fbc1d5d...` |
| `NM-014_Introduccion_a_la_Quimica_CEAEQ.pdf` | 4.159.853 | 388.809 | APROBADO (OK) | `366e20587f...` |
| `NM-015_Como_funciona_la_energia.pdf` | 5.616.007 | 34.447 | APROBADO (OK) | `897dd3efd3...` |
| `NM-016_Como_funciona_la_tecnologia.pdf` | 6.225.576 | 34.633 | APROBADO (OK) | `5213d0f693...` |
| `NM-020_Python_Intermedio.pdf` | 1.205.952 | 118.710 | APROBADO (OK) | `b42686b177...` |
| `COMP-01_Guia_GPC_Evaluacion_Economica_Salud_Colombia.pdf` | 4.168.843 | 442.013 | APROBADO (OK) | `d80a1dca88...` |
| `COMP-03_Manual_Operativo_MIPG_6_1.pdf` | 6.032.083 | 511.944 | APROBADO (OK) | `47bac67bde...` |
| `COMP-04_Guia_Oficial_Proteccion_Datos_Personales.pdf` | 3.334.426 | 49.548 | APROBADO (OK) | `1df0fc0bf1...` |
| `COMP-05_Lineamientos_Nacionales_Bioseguridad_Laboratorios.pdf` | 1.060.571 | 90.123 | APROBADO (OK) | `b86b4013ff...` |
| `COMP-06_Introducing_Marketing_John_Burnett.pdf` | 13.038.645 | 863.486 | APROBADO (OK) | `e5b01dee66...` |
| `COMP-07_Oficio_PTEE_Transicion_2026.pdf` | 263.716 | 9.882 | APROBADO (OK) | `48324891ae...` |
| `COMP-09_Tecnologias_de_la_vida_para_el_desarrollo.pdf` | 7.925.258 | 1.936.212 | APROBADO (OK) | `b93b6c228c...` |
| `COMP-10_Vendedor_Externo_SENA.pdf` | 9.083.512 | 146.059 | APROBADO (OK) | `627c157a98...` |
| `COMP-11_Sales_Leadership_Management.pdf` | 17.950.289 | 1.197.674 | APROBADO (OK) | `cfef6cb979...` |

**Hallazgo de Integridad:** El 100% de los archivos analizados existe físicamente, abre sin errores criptográficos o de cabecera, y permite extracción directa de texto plano. Ningún PDF presentó texto vacío.

---

## 3. Calidad de Metadatos y Clasificación Documental

### A. Documentos Excluidos (`NO_APTO`)
- **`NM-021` (Física Universitaria):** Clasificado como `NO_APTO` debido a licencia Creative Commons CC BY-NC-ND 4.0 (la cláusula **ND - Sin Derivadas** prohíbe generar adaptaciones educativas, y la fuente no ofrece PDF libre distribuible).
- **`NM-022` (College Physics 2e, OpenStax):** Clasificado como `NO_APTO` porque los términos de uso institucionales de OpenStax prohíben explícitamente el entrenamiento, ingestión o uso con modelos LLM / IA generativa sin permiso previo por escrito.
- **Verificación de Aislamiento:** Se constató que ni `NM-021` ni `NM-022` están incorporados al catálogo de precarga ni al índice FAISS activo del sistema.

### B. Documentos Observados (`APTO_CON_REVISIÓN`)
- **`NM-007` (ESP32 en el Aula):** Requiere revisión porque la fuente CATEDU tiene licencias compuestas por capítulos (CC BY-SA 4.0 y CC BY-NC-SA 4.0).
- **`NM-011` (Desarrollo Móvil con Cloud):** Requiere cotejo de procedencia editorial primaria.
- **`NM-012`, `NM-013`, `NM-017`, `NM-018`, `NM-019`, `NM-020`:** Libros web o repositorios donde se requiere congelar el snapshot o commit exacto antes de certificar la versión final.

### C. Documentos Verificados para Precarga Activa del MVP
El catálogo de arranque automático (`VERIFIED_APTO_CORPUS`) se configuró de forma rigurosa con tres documentos `APTO` definitivos:
1. `NM-006` (Ciberseguridad para OSC) -> 136 chunks en FAISS.
2. `NM-015` (Cómo funciona la energía) -> 22 chunks en FAISS.
3. `NM-004` (Diseño de Base de Datos) -> 321 chunks en FAISS.
Total en índice inicial: **479 chunks**.

---

## 4. Trazabilidad de Hashes SHA-256

Se compararon los hashes generados en tiempo real contra `manifest_sha256_documental.csv` y `manifest_sha256_materializado.csv`.
- Todos los documentos coinciden exactamente con los registros archivados en la auditoría de Fase 05.
- La trazabilidad por `documento_id` se mantiene a lo largo de toda la cadena (archivo físico -> `DocumentService` -> `RAGService._chunks` -> API `/api/v1/adaptacion`).
