# NuevaMente — Verificación prioritaria de fuentes (Fase 05)

Fecha de revisión: 2026-10-02

## Reconciliación ejecutada

| ID | Evidencia consultada | Resultado de la reconciliación | Estado |
|---|---|---|---|
| NM-001 | PDF oficial en idUS; 2.ª edición 2023 y licencia CC BY-NC-SA 4.0 declarada en la obra. | Se fija el PDF oficial como fuente principal y se conserva el dato de 271 páginas. | CERRADO para metadatos; preservar archivo exacto |
| NM-002 | Sitio de Think Python + PDF de la traducción española; el PDF identifica la traducción, autores y licencia. | Se agregan traductor, año/páginas reportados y URL concreta del PDF. | CERRADO para identificación; preservar archivo exacto |
| NM-005 | Sitio y repositorio oficiales de Computer Networking: Principles, Protocols and Practice; 3.ª edición en PDF y CC BY-SA 3.0 Unported. | Se identifica un PDF concreto y se elimina la condición genérica de licencia. `APTO` se conserva/cierra. | CERRADO para formato/licencia |
| NM-006 | NDI: publicación y PDF oficial en español; licencia CC BY-SA 4.0. OpenLibro aporta 87 páginas. | Se enriquecen autoría, URL, fecha, páginas, licencia, integridad y procedencia. `APTO` se conserva. | CERRADO para metadatos; conservar archivo exacto |
| NM-011 | OpenLibro: cinco autores, 2023, 633 páginas, CC BY 4.0. | Se corrige autoría, URL, fecha, páginas y evidencia de licencia. `APTO` se conserva. | CERRADO para metadatos; conservar archivo exacto |
| NM-012 | TU Delft OPEN: página de créditos y repositorio público; Jupyter Book escrito con Markdown/notebooks/Python; CC BY 4.0 excepto Fig. 9, 12 y 31. | Se corrige el formato soportado y se mantiene `APTO_CON_REVISIÓN` por snapshot exacto y tratamiento de las tres figuras excluidas. | PENDIENTE control de archivo/licencia |
| NM-013 | Mavs Open Press: PDF disponible; Bonnie Boardman autora, Jane Fraser contributor; publicación 26-06-2020. Pressbooks: CC BY 4.0 excepto donde se indique lo contrario; última actualización 15-05-2026. | Se completan autoría, fuente, fecha y actualización. `APTO_CON_REVISIÓN` permanece por revisión de materiales externos. | PENDIENTE delimitación de elementos externos |
| NM-015 | RED Descartes: ficha oficial de ¿Cómo funciona la energía?; castellano, 16+, Juan Guillermo Rivera Berrío, ISBN 978-84-10368-59-0, versión PDF y CC BY-NC-SA 4.0; libro interactivo 2026. | Se fija la ficha oficial específica y se registra 2026. `APTO_CON_REVISIÓN` se mantiene hasta preservar y verificar el PDF exacto. | PENDIENTE archivo exacto |
| NM-016 | Ficha oficial de Project Descartes y PDF oficial directo; audiencia 16+, licencia CC BY-NC-SA 4.0, PDF de 91 páginas, 2026. | Se identifica archivo compatible con el MVP, se corrigen audiencia, formato, páginas y fecha. `APTO` se cierra. | CERRADO para formato/metadatos |
| NM-017 | Repositorio oficial: Draft v0p4, diciembre de 2025, 20 capítulos + 6 apéndices, Markdown, CC BY 4.0. | Se corrige el año y se mantiene `APTO_CON_REVISIÓN` por madurez/estabilidad del contenido en desarrollo. | REVISIÓN de madurez |
| NM-018 | Repositorio oficial: Draft v0p4, diciembre de 2025, 20 capítulos + 6 apéndices, Markdown, CC BY 4.0; sincronización pública de solo lectura. | Se corrigen versión/fecha y se mantiene `APTO_CON_REVISIÓN`. | REVISIÓN de madurez |
| NM-019 | Repositorio oficial: 35 capítulos + 8 apéndices, enero de 2026, Markdown, CC BY 4.0; sincronización pública de solo lectura. | Se corrige la fecha y se mantiene `APTO_CON_REVISIÓN` por madurez/versionado. | REVISIÓN de madurez |
| NM-020 | ReadTheDocs oficial: PDF descargable, CC BY-NC-SA 4.0 para la traducción y autor original identificado. Una fuente secundaria reporta otra licencia. | Se mantiene `APTO_CON_REVISIÓN` hasta fijar versión/archivo/licencia exactos del corpus. | REVISIÓN de versión/licencia |
| NM-022 | OpenStax: CC BY-NC-SA 4.0 y restricción expresa de ingestión en LLM/IA generativa sin permiso previo. | Se conserva `NO_APTO`. | CERRADO para decisión actual |

## Regla aplicada

Los cambios de resultado solo se realizaron cuando la evidencia consultada afecta directamente a un criterio de aceptación ya definido: formato de entrada, completitud del documento, procedencia o condiciones de uso. La evaluación NNA no se utilizó por sí sola para cambiar el resultado general.

## Nota de integridad

`VERIFICADA` en este paquete significa que la fuente concreta y el documento/archivo referenciado fueron identificados de forma suficiente para la evaluación documental. No equivale todavía a un hash o control de identidad criptográfica de la copia local final que se incorpore al corpus.

## Pendientes

Para todos los documentos aprobados debe preservarse el archivo exacto utilizado por el MVP. NM-012 requiere fijar snapshot y tratamiento de las figuras excluidas; NM-013 requiere delimitar materiales externos; NM-015 requiere preservar y verificar el PDF exacto; NM-020 requiere fijar una versión exacta y resolver la discrepancia de licencia; NM-022 permanece excluido mientras no exista autorización compatible con el uso previsto.
