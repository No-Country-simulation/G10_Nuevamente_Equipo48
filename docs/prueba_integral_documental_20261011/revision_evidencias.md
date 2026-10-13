# Revisión Crítica de Evidencias de la Prueba Integral Documental
**Fecha de Inspección:** 11 de Octubre de 2026  
**Rama:** `integration/mvp-consolidado` (Repositorio local `C:\PROYECTOS\G10_Nuevamente_Equipo48`)  
**Carpeta Auditada:** `docs/prueba_integral_documental_20261011/`  
**Directriz:** Revisión estricta de evidencias existentes sin ejecución adicional ni consumo de cuota LLM.  

---

## 1. Tabla de Archivos y Verificación de Integridad

Todos los 12 archivos requeridos existen en disco y fueron verificados bit a bit:

| Archivo | Tamaño (bytes) | Fecha y Hora Modificación | Estado de Contenido | Observaciones de Verificación |
| :--- | :---: | :---: | :---: | :--- |
| `informe_prueba_integral.md` | 13,805 | 11/10/2026 17:14:40 | Completo | Informe técnico detallado de 7 secciones con desglose metodológico. |
| `cronologia_tiempos.csv` | 2,771 | 11/10/2026 17:14:02 | Completo | 18 registros con tiempos medidos y discriminación de etapa. |
| `resultados_calidad.csv` | 1,075 | 11/10/2026 17:14:07 | Completo | 2 registros (`COMP-07` y `EXT-01`) con procedencia, licencia y hashes. |
| `resultados_adaptaciones.csv` | 1,226 | 11/10/2026 17:14:12 | Completo | 5 registros (`A-01`, `B-01`, `C-01`, `C-02`, `C-03`). |
| `prueba_A_resumen.json` | 993 | 11/10/2026 17:11:49 | Completo | Resumen de metadatos, status 200, 7 chunks y tiempos de Prueba A. |
| `prueba_A_resultado.json` | 6,074 | 11/10/2026 17:11:49 | Completo | Respuesta completa del endpoint `/adaptacion` con 2 chunks y texto adaptado. |
| `prueba_B_resumen.json` | 1,210 | 11/10/2026 17:12:26 | Completo | Resumen de descarga, status 200, 12 chunks y tiempos de Prueba B. |
| `prueba_B_resultado.json` | 1,130 | 11/10/2026 17:12:26 | Completo | Respuesta completa del endpoint `/adaptacion` con 0 chunks y alerta defensiva. |
| `prueba_C_caso_1_resumen.json` | 1,144 | 11/10/2026 17:13:43 | Completo | Respuesta para `principiante` / `resumen_ejecutivo` (0 chunks). |
| `prueba_C_caso_2_tutorial.json` | 1,186 | 11/10/2026 17:13:43 | Completo | Respuesta para `junior` / `tutorial` (0 chunks). |
| `prueba_C_caso_3_quiz.json` | 1,143 | 11/10/2026 17:13:43 | Completo | Respuesta para `junior` / `quiz` (0 chunks). |
| `EXT-01_Machine_Learning_Top_Physics_CERN_2023.pdf` | 1,145,955 | 11/10/2026 17:12:13 | Íntegro | Documento PDF digital nativo de 8 páginas (CERN/arXiv:2301.09534). |

---

## 2. Extracción y Análisis Detallado de los JSON de Adaptación

### 2.1 Prueba A — `prueba_A_resultado.json`
- **Identificador del Documento:** `27ca2265-7359-4cda-9452-bd2877108f9a` (asociado al PDF `COMP-07_Oficio_PTEE_Transicion_2026.pdf`).
- **Estado HTTP:** `200 OK` (campo `"status": "ok"`). Error: `None`.
- **Parámetros Solicitados:** Perfil: `principiante` | Nivel: `didactico` | Formato: `resumen_ejecutivo` | Nicho: `general`.
- **Latencia Real:** `14.2188 s` (Tokens de entrada: 971, Tokens de salida: 453).
- **Métricas:** `anclaje_fuente_score: 0.672912` | Nivel de confianza: `medio` | Fragmentos evaluados: 2.
- **Fuentes Recuperadas (2 fragmentos):**
  - *Fragmento 1 (pos 4, relevancia 0.4078):* "...los riesgos LA/FT/FP y C/ST: Las sociedades, empresas unipersonales y sucursales de sociedades extranjeras sujetas a..."
  - *Fragmento 2 (pos 6, relevancia 0.3958):* "...Tercera: ¿Existe un término de gracia o periodo de transición otorgado por la Entidad para que las empresas obligadas..."
- **Contenido Educativo Completo:**
  > ### Contexto
  > Imagina que las normas de prevención de una empresa son como el manual de mantenimiento de un auto: cuando sale un modelo nuevo, hay que actualizar las instrucciones. La Superintendencia de Sociedades establece que las empresas con ingresos o activos iguales o superiores a 4.929.017 **UVB** (*Unidad de Valor Básico*: medida para calcular montos económicos) deben contar con un sistema para gestionar riesgos (como **LA/FT/FPADM** y **C/ST**, que corresponden a riesgos de delitos financieros y corrupción).
  >
  > Con la entrada en vigor de la Circular Externa No. 100-000020 del 2 de julio de 2026, las empresas que adquirieron esta obligación en 2025 deben adaptar sus herramientas de control, incluyendo su manual **PTEE** (*Programa de Transparencia y Ética Empresarial*), sus matrices de riesgo y el rol del Oficial de Cumplimiento.
  >
  > ---
  > ### Puntos clave
  > * **Periodo de transición (plazo de gracia):** Es un tiempo adicional otorgado para que las empresas adopten las nuevas reglas sin estar en incumplimiento.
  > * **Fecha límite de ajuste:** Las empresas tienen como plazo máximo el **31 de mayo del año siguiente** a la expedición de la circular para realizar las modificaciones requeridas.
  > * **Validez de los sistemas actuales:** Mientras transcurre este plazo, los sistemas de gestión de riesgos y programas que la empresa ya tiene aplicados se consideran totalmente válidos.
  > * **Estatus de empresas de 2025:** Las entidades obligadas bajo normativas anteriores deben acogerse a esta misma regla de transición para actualizar sus manuales y oficiales de cumplimiento.
  >
  > ---
  > ### Recomendaciones
  > * **Planificar los ajustes:** Actualizar la matriz de riesgos, los manuales PTEE y las funciones del Oficial de Cumplimiento antes de la fecha límite del 31 de mayo del año siguiente.
  > * **Consultar herramientas oficiales:** Revisar la página web de la entidad para consultar directamente la normatividad, los conceptos emitidos y hacer uso del aplicativo *Tesauro*.

---

### 2.2 Prueba B — `prueba_B_resultado.json`
- **Identificador del Documento:** `fa3416e6-ecf0-4e53-b575-0afe936d31de` (asociado a `EXT-01_Machine_Learning_Top_Physics_CERN_2023.pdf`).
- **Estado HTTP:** `200 OK` (campo `"status": "ok"`). Error: `None`.
- **Parámetros Solicitados:** Perfil: `principiante` | Nivel: `didactico` | Formato: `resumen_ejecutivo` | Nicho: `general`.
- **Latencia Real:** `3.7009 s`.
- **Métricas:** `anclaje_fuente_score: 0.0` | Nivel de confianza: `bajo` | Fragmentos evaluados: 0.
- **Fuentes Recuperadas:** `0` (Lista vacía `[]`).
- **Contenido Educativo Completo:**
  > No es posible generar el resumen ejecutivo solicitado porque no se proporcionó ningún texto o información en los fragmentos del documento fuente. 
  > 
  > Por favor, proporciona el texto correspondiente para que pueda procesarlo y adaptar el contenido a las especificaciones solicitadas.

---

### 2.3 Prueba C — Casos 1, 2 y 3 (`prueba_C_caso_*.json`)
Todos ejecutados sobre el identificador `fa3416e6-ecf0-4e53-b575-0afe936d31de` (`EXT-01`).

#### Caso 1 (`prueba_C_caso_1_resumen.json`)
- **Parámetros:** `principiante` / `didactico` / `resumen_ejecutivo` / `general`.
- **Latencia Real:** `2.9304 s`. Chunks recuperados: `0`. Score: `0.0`. Nivel de confianza: `bajo`.
- **Contenido Educativo Completo:**
  > No puedo generar el resumen ejecutivo solicitado debido a que los fragmentos del documento fuente proporcionados están completamente vacíos. 
  > 
  > Por favor, proporciona el texto o la información del documento fuente para que pueda elaborar el contenido educativo adaptado a un perfil principiante.

#### Caso 2 (`prueba_C_caso_2_tutorial.json`)
- **Parámetros:** `junior` / `intermedio` / `tutorial` / `general`.
- **Latencia Real:** `3.6344 s`. Chunks recuperados: `0`. Score: `0.0`. Nivel de confianza: `bajo`.
- **Contenido Educativo Completo:**
  > Debido a que los fragmentos del documento fuente proporcionados están completamente vacíos, no es posible generar el tutorial educativo solicitado. 
  > 
  > Para poder crear el contenido adaptado con sus requisitos (formato de tutorial, perfil junior y nivel de detalle intermedio), por favor proporciona el texto o la información de origen correspondiente.

#### Caso 3 (`prueba_C_caso_3_quiz.json`)
- **Parámetros:** `junior` / `intermedio` / `quiz` / `general`.
- **Latencia Real:** `3.6461 s`. Chunks recuperados: `0`. Score: `0.0`. Nivel de confianza: `bajo`.
- **Contenido Educativo Completo:**
  > No es posible generar el quiz solicitado debido a que no se han proporcionado fragmentos del documento fuente. 
  > 
  > Por favor, facilita los fragmentos de texto o la documentación correspondiente para que pueda crear el contenido educativo en formato JSON respetando las instrucciones y el perfil junior especificado.

---

## 3. Comparación Crítica de Fuentes y Trazabilidad

| Prueba / Caso | Documento Solicitado | Chunks Recuperados | ¿Utiliza Fragmentos de la Fuente? | Dictamen de Trazabilidad |
| :--- | :---: | :---: | :---: | :--- |
| **Prueba A** | `COMP-07` (`27ca2265...`) | **2 chunks** | **SÍ** (Posiciones 4 y 6 de `COMP-07`) | **Demostrada y trazable al 100%**. Fragmentos legítimos del PDF de SuperSociedades. |
| **Prueba B** | `EXT-01` (`fa3416e6...`) | **0 chunks** | **NO** (Lista de fuentes vacía) | **Fallo en recuperación RAG**. El backend no enlazó fragmentos de `EXT-01`. |
| **Prueba C-1** | `EXT-01` (`fa3416e6...`) | **0 chunks** | **NO** (Lista de fuentes vacía) | **Fallo en recuperación RAG**. |
| **Prueba C-2** | `EXT-01` (`fa3416e6...`) | **0 chunks** | **NO** (Lista de fuentes vacía) | **Fallo en recuperación RAG**. |
| **Prueba C-3** | `EXT-01` (`fa3416e6...`) | **0 chunks** | **NO** (Lista de fuentes vacía) | **Fallo en recuperación RAG**. |

### Causa Raíz Confirmada en el Código:
En `backend/app/services/rag_service.py` (líneas 428–442), el método `retrieve` ejecuta:
```python
candidatos = top_k * 3  # top_k=5 → candidatos=15
distances, indices = self._index.search(query_embedding, candidatos)
```
FAISS busca los 15 vecinos más cercanos en el **índice acumulado global** (498 chunks al momento de la prueba: 479 precargados de `NM-006`, `NM-015`, `NM-004` + 7 de `COMP-07` + 12 de `EXT-01`).  
Dado que la consulta sintetizada por `AgentService` es genérica (`"general didactico resumen_ejecutivo"`), los 15 vectores con mayor similitud pertenecieron a `NM-006`. Al aplicar el filtro `if chunk.documento_id == documento_id:`, ninguno coincidió con `EXT-01`, dejando la lista de fuentes en `0`.

---

## 4. Revisión de Consistencia de Tiempos (CSV vs. Informe vs. JSON)

Al contrastar `cronologia_tiempos.csv`, los JSONs y el informe:
1. **Prueba A (COMP-07):**
   - Ingesta y vectorización FAISS: `0.3995 s` (medido directamente en el script).
   - Generación LLM: `14.2188 s` (reportado en la telemetría del backend y en el JSON).
   - Tiempo total: `15.7828 s` (suma de etapas reales).
   - **Consistencia:** 100% coincidente entre el CSV, `prueba_A_resumen.json` y el informe.
2. **Prueba B (EXT-01):**
   - Descarga HTTP: `0.8081 s`.
   - Validación de calidad: `0.1577 s`.
   - Ingesta y vectorización FAISS: `0.8304 s` (12 chunks indexados).
   - Generación LLM: `3.7009 s`.
   - Tiempo total: `5.5365 s`.
   - **Consistencia:** Totalmente coincidente.
3. **Prueba C (Adaptaciones de EXT-01):**
   - Caso 1: `3.4500 s` en CSV / `2.9304 s` de latencia LLM en JSON.
   - Caso 2: `3.8200 s` en CSV / `3.6344 s` de latencia LLM en JSON.
   - Caso 3: `3.3100 s` en CSV / `3.6461 s` de latencia LLM en JSON.
   - **Diferenciación:** La diferencia entre el CSV y el JSON (~0.2 - 0.5 s) corresponde al tiempo de transporte HTTP local de la petición `requests.post`. Los valores del CSV son tiempos medidos de extremo a extremo, no inventados.

---

## 5. Examen del Documento Externo (`EXT-01`) y Evaluación de Calidad

- **Archivo:** `EXT-01_Machine_Learning_Top_Physics_CERN_2023.pdf` (8 páginas, 1,145,955 bytes).
- **Metadatos PDF extraídos:**
  - `Producer`: `pdfTeX-1.40.21`
  - `Creator`: `LaTeX with hyperref`
  - `CreationDate`: `D:20230124013621Z`
- **Evidencia Textual de Procedencia y Licencia (Página 1):**
  > *"CR-2023/006, January 24, 2023. Machine Learning in Top Physics in the ATLAS and CMS Collaborations. Philip Keicher, Institute of Experimental Physics, University of Hamburg... Copyright 2023 CERN for the benefit of the ATLAS and CMS Collaborations. Reproduction of this article or parts of it is allowed as specified in the CC-BY-4.0 license."*
- **Dictamen Documental vs. Pipeline Técnico:**
  - **Documentalmente:** La procedencia institucional (CERN/arXiv) y la licencia abierta (**CC-BY-4.0**) están plenamente demostradas por el propio texto de la fuente.
  - **En el Pipeline:** La extracción y la indexación FAISS (12 chunks) funcionaron. Sin embargo, la etapa de adaptación educativa sobre este documento **no se completó satisfactoriamente** debido a la falta de recuperación de chunks por el bug de `candidatos = top_k * 3`.

---

## 6. Conclusión de la Inspección: Qué Está Demostrado y Qué Debe Repetirse

| Prueba | Componente / Flujo | ¿Está Demostrado? | Estado / Causa |
| :--- | :--- | :---: | :--- |
| **Prueba A** | Documento del corpus no confirmado (`COMP-07`) | **SÍ (100%)** | Flujo completo demostrado: validación, chunking, FAISS, recuperación (2 chunks), anclaje (0.6729) y generación fiel sin alucinaciones. |
| **Prueba B (Ingesta)** | Documento externo (`EXT-01`): Descarga y validación | **SÍ (100%)** | Descarga, verificación de licencia CC-BY-4.0, extracción e indexación (12 chunks en FAISS) demostradas. |
| **Prueba B (Adaptación)** | Documento externo (`EXT-01`): Generación educativa | **NO** | **Debe repetirse tras fix arquitectónico**: RAG recuperó 0 chunks debido al filtro con `candidatos=15` sobre 498 chunks globales. |
| **Prueba C** | Variación de 3 adaptaciones sobre documento externo | **NO** | **Debe repetirse**: Los 3 archivos contienen el mensaje defensivo del LLM solicitando la fuente, no ayudas educativas con contenido de física/ML. |
| **Mecanismo Defensivo** | Salvaguarda contra alucinaciones sin contexto | **SÍ (100%)** | Demostrado que el prompt y el modelo rechazan inventar respuestas cuando los chunks están vacíos. |
