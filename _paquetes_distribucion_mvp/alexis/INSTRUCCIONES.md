# Paquete Alexis — corpus, catálogo y trazabilidad

## Serie incremental de rama

Aplicar y confirmar por separado: `incrementos/01-cargador-corpus.patch`, `incrementos/02-rag-por-documento.patch` y `incrementos/03-arranque-precarga.patch`. Los archivos de `patches/` son el consolidado de referencia y no deben aplicarse si ya se usó la serie.

## Objetivo

Añadir la precarga controlada de un catálogo APTO y conservar la trazabilidad del corpus sin empaquetar materiales binarios ni de procedencia no confirmada.

## Archivos y diferencia

- `patches/nuevo-corpus-loader.patch`: añade `backend/backend/app/services/corpus_loader.py`, con catálogo explícito `NM-004`, `NM-006` y `NM-015`, filtro `APTO`, idempotencia y resumen de fallos.
- `patches/precarga-corpus-y-rag.patch`: cambia `backend/backend/app/main.py` para invocar la precarga no crítica y `rag_service.py` para la operación necesaria de existencia/recuperación.

Los PDF, HTML, hojas de cálculo y directorios auxiliares de `_revision_corpus_fase05/` no están incluidos: el árbol local contiene 969 archivos y aproximadamente 245 MB, incluidos binarios y materiales de terceros. Los archivos de metadatos existentes son evidencia local no rastreada, no una fuente publicada en `dev`.

## Dependencias y PR

Requiere que el equipo suministre por un canal aprobado los tres documentos físicos cuya ruta coincide con el catálogo, junto con licencia/procedencia verificadas. El código puede integrarse sin ellos porque falla de forma no crítica, pero la precarga real no queda demostrada. Depende de la API RAG existente en `dev` y debe entrar antes de QA que cubra precarga.

## Aceptación mínima

- Solo registros `APTO` son candidatos a ingesta.
- Un documento ya indexado no se duplica.
- Archivo inexistente, extracción vacía o fallo de ingesta queda en el resumen sin bloquear el arranque.
- Se confirma por separado la procedencia y hash de los tres artefactos físicos.

## Autoría

El historial publicado de corpus está en `5981e6e` de Alexis, en `origin/data-analytics-corpus`; estos parches locales no están comprometidos. La relación se marca como pendiente de confirmación, no como atribución de autoría.
