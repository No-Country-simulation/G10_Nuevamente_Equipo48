# NuevaMente — Auditoría integral del corpus (Fase 05 rev6)

**Fecha de actualización:** 2026-10-02  
**Base:** Fase 05 rev5 + verificación de fuentes primarias y snapshots  
**Alcance:** 22 registros; actualización focalizada de los 8 documentos en APTO_CON_REVISIÓN.

## 1. Resultado de subsanación

| Resultado | Registros |
|---|---:|
| APTO | 18 |
| APTO_CON_REVISIÓN | 2 |
| NO_APTO | 2 |
| **Total** | **22** |

Se subsanaron **6 de los 8** registros que estaban en APTO_CON_REVISIÓN. Los cambios se limitan a evidencia primaria, fijación de snapshots y delimitación explícita de materiales con derechos de terceros. No se ha cambiado la selección definitiva del corpus: los 22 registros siguen en `EN_EVALUACION`.

## 2. Documentos que pasan a APTO

| ID | Documento | Subsanación aplicada |
|---|---|---|
| NM-011 | Desarrollo de aplicaciones móviles usando APIs de Google Cloud Platform | Se reemplazó la ficha secundaria de OpenLibro por el catálogo editorial primario de Religación Press. La editorial declara cinco autores, fecha 2023-12-07, ISBN, PDF/EPUB y CC BY 4.0. |
| NM-012 | Risk and Reliability for Engineers | Se fijó el commit `5675de335e16588c33e481fe2f84e1a8b81abf2b`. La ingesta queda restringida a texto y componentes cubiertos por CC BY 4.0; se excluyen las figuras 2.2, 2.5 y 5.12 expresamente exceptuadas en créditos. |
| NM-013 | Introduction to Industrial Engineering | Se delimitó la ingesta al texto de los capítulos cubierto por CC BY 4.0. Se excluyen imágenes, diagramas, actividades H5P y recursos externos con licencias propias. |
| NM-017 | Computer Graphics Fundamentals | Se fijó el commit de lanzamiento v0p4 `50a3bbe6a7c4259cb04db87e38163a5cd1f8043d`, con CC BY 4.0. |
| NM-018 | Data Structures in Practice | Se fijó el commit `d9391e7ce8b1b8041a37783f2fa74756b74b4c3a`. Se conserva expresamente el metadato `Draft v0p4`; no se presenta como edición final. |
| NM-019 | Performance and Benchmarking | Se fijó el commit de lanzamiento `cbc2dad298b3599ff61f5fa68b0ff8a986136781`; README identifica v0p9 y CC BY 4.0. |

## 3. Documentos que permanecen en APTO_CON_REVISIÓN

- **NM-007 — ESP32 en el Aula:** obra compuesta con licencias diferentes por autor/sección (CC BY-SA 4.0 y CC BY-NC-SA 4.0), más créditos de terceros. Para pasarla a APTO se debe elegir el conjunto concreto de capítulos y confirmar que el uso previsto respeta las restricciones NC/SA y los derechos de terceros. No se seleccionan capítulos por cuenta del equipo.
- **NM-020 — Python Intermedio:** la versión española declara CC BY-NC-SA 4.0. Aunque se identifica la versión 0.1 y existe PDF, el uso está sujeto a la condición NoComercial y CompartirIgual. Se conserva en revisión hasta confirmar que el alcance de uso del proyecto es no comercial y que las adaptaciones/distribuciones respetarán ShareAlike.

## 4. Controles de materialización que siguen pendientes para todos los documentos

El estado APTO confirma la elegibilidad documental dentro del alcance declarado; no afirma que los archivos binarios ya estén descargados y almacenados. Al materializar el corpus, se debe registrar para cada archivo: URL exacta, fecha de descarga, nombre, tamaño, SHA-256 y versión/commit. En NM-012 y NM-013 deben respetarse las exclusiones de componentes descritas. En NM-018 debe mantenerse visible que la fuente es un borrador.

## 5. Documentos NO_APTO que no cambian

- **NM-021:** licencia CC BY-NC-ND 4.0 y limitaciones de formato/derechos que impiden el uso previsto de adaptación.
- **NM-022:** OpenStax establece una restricción expresa sobre entrenamiento/ingestión en LLM o IA generativa sin permiso previo escrito.

## 6. Alcance y decisiones del equipo

- No se modificó GitHub, `Data_Analyst` ni `main`.
- No se alteró `estado_seleccion`: los 22 registros continúan en `EN_EVALUACION`.
- La selección final del corpus y los perfiles/formatos de demostración siguen siendo decisiones del equipo. La población objetivo permanece abierta; se contemplan perfiles configurables. El análisis NNA de la matriz es complementario y condicional, no define la población vigente ni filtra la aceptación general.
- La revisión de calidad técnica línea por línea y la generación de hashes requieren la materialización de los archivos originales; no se afirman como completadas en esta auditoría.

## 7. Fuentes primarias y snapshots fijados

- NM-011: https://press.religacion.com/index.php/press/catalog/book/130
- NM-012: https://github.com/prob-design/risk-reliability/commit/5675de335e16588c33e481fe2f84e1a8b81abf2b
- NM-013: https://uta.pressbooks.pub/industrialengineeringintro/
- NM-017: https://github.com/djiangtw/computer-graphics-fundamentals-public/commit/50a3bbe6a7c4259cb04db87e38163a5cd1f8043d
- NM-018: https://github.com/djiangtw/data-structures-in-practice-public/commit/d9391e7ce8b1b8041a37783f2fa74756b74b4c3a
- NM-019: https://github.com/djiangtw/performance-and-benchmarking-public/commit/cbc2dad298b3599ff61f5fa68b0ff8a986136781
- NM-020: https://python-intermedio.readthedocs.io/es/0.1/

## 8. Archivos actualizados

- `inventario/inventario_corpus.csv`
- `matriz/Matriz_Corpus_NuevaMente_Consolidada_v2_Poblacion.xlsx`
- `reportes/registro_evidencias_fuentes.csv`
- `reportes/auditoria_integral_fase05_rev6.md`
- `reportes/validacion_integral_fase05_rev6.txt`


## 9. Límite de materialización

Esta auditoría consolida la evaluación documental, las fuentes y las restricciones de los 22 registros. Los archivos originales PDF/EPUB/Markdown aún no se han descargado, según el estado de trabajo confirmado para esta fase. La identidad de cada archivo que se incorpore al MVP deberá cerrarse mediante versión, ruta, fecha de descarga, tamaño y SHA-256. El manifiesto del paquete identifica únicamente los artefactos de auditoría.
