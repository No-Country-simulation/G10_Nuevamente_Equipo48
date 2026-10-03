# NuevaMente — Estado consolidado de Data Analytics / Fase 05

**Fecha de corte documental:** 2026-10-02
**Base de trabajo:** paquete de auditoría Fase 05 rev6 y sus artefactos asociados.

## Estado vigente

El conjunto contiene 22 registros. El inventario CSV, la hoja **Matriz maestra**, la hoja **Auditoría integral** y el registro de evidencias se reconciliaron por identificador y resultado:

| Resultado de evaluación | Registros |
|---|---:|
| APTO | 18 |
| APTO_CON_REVISIÓN | 2 |
| NO_APTO | 2 |
| **Total** | **22** |

Los 22 registros conservan `EN_EVALUACION`. La matriz **Finalistas propuestos** contiene ocho propuestas; no representa una selección aprobada. La selección final y el contexto de aplicación corresponden al equipo. La población objetivo permanece abierta y se prevén perfiles configurables; la hoja **Adecuación NNA** es un análisis complementario, no una definición vigente de población ni un filtro de aceptación.

## Documentos APTO_CON_REVISIÓN

- **NM-007 — ESP32 en el Aula:** obra compuesta con licencias distintas por autor/sección y créditos de terceros. Debe definirse el conjunto exacto de capítulos, exportarlo íntegramente y aplicar las condiciones por sección antes de incorporarlo.
- **NM-020 — Python Intermedio:** se fija la referencia documental a ReadTheDocs 0.1 (`https://python-intermedio.readthedocs.io/es/0.1/`). La traducción declara CC BY-NC-SA 4.0. Debe preservarse el archivo exacto y confirmarse que el uso, las adaptaciones y su eventual distribución cumplen las condiciones NC/SA.

## Documentos NO_APTO

- **NM-021 — Introduction to Autonomous Robots:** la licencia CC BY-NC-ND 4.0 y las limitaciones de formato/derechos no permiten el uso de adaptación previsto en el MVP.
- **NM-022 — College Physics 2e:** OpenStax establece una restricción expresa para entrenamiento/ingestión en LLM o IA generativa sin autorización previa escrita.

## Controles específicos para documentos APTO

- **NM-011:** utilizar la ficha editorial primaria de Religación Press.
- **NM-012:** utilizar únicamente el snapshot fijado; excluir las figuras 2.2, 2.5 y 5.12 según los créditos/licencia.
- **NM-013:** limitar el uso al texto de capítulos cubierto por CC BY 4.0; excluir imágenes, diagramas, H5P y materiales externos no cubiertos.
- **NM-017:** conservar el commit fijado y la licencia CC BY 4.0.
- **NM-018:** conservar el commit fijado y mantener visible la condición `Draft v0p4`.
- **NM-019:** conservar el commit fijado y la versión v0p9.

## Límite de esta consolidación

Este paquete consolida los registros, la matriz, la evidencia documental y las restricciones conocidas. Los archivos originales PDF/EPUB/Markdown aún no se han descargado y no forman parte de esta entrega. Por tanto, no certifica su preservación en la copia local del usuario ni la identidad criptográfica de los archivos que eventualmente se utilicen. El manifiesto SHA-256 de este paquete corresponde a los artefactos de auditoría incluidos, no a los documentos fuente.

Antes de declarar un documento listo para ingestión/prueba del MVP, debe comprobarse en la copia local cuál es el archivo fuente exacto, su versión, integridad y SHA-256, y registrar fecha de descarga y ruta. El archivo `control_materializacion_fuentes.csv` deja ese control explícitamente abierto sin presumir que los originales no existan en el equipo.

## Alcance de Data Analytics

La fase cubre búsqueda y evaluación documental, calidad, pertinencia, integridad, procedencia, licencias, metadatos, adecuación, inventario, evidencia y trazabilidad. No incluye implementación de RAG, chunking, embeddings, vector database, retrieval, prompts, orquestación LLM, backend ni frontend.

## Historial

Los reportes rev3, rev4 y rev5 se conservan como historial. Sus distribuciones y pendientes son estados anteriores y no deben utilizarse para describir el resultado vigente. El informe `auditoria_integral_fase05_rev6.md` y este estado consolidado prevalecen.
