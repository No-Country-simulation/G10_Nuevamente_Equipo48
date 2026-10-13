# Paquete Dayanara — QA y evidencias

## Serie incremental de rama

Aplicar y confirmar por separado: `incrementos/01-pruebas-contrato.patch`, `incrementos/02-pruebas-servicios.patch`, `incrementos/03-pruebas-precarga.patch` y `incrementos/04-pruebas-cliente-frontend.patch`. Los archivos de `patches/` son el consolidado de referencia y no deben aplicarse si ya se usó la serie.

## Objetivo

Ofrecer las suites de verificación y conservar una separación clara entre código de producto, pruebas y evidencia local.

## Archivos y diferencia

- `patches/tests-existentes.patch`: cambios en fixtures y pruebas de adaptación, agentes, documento, LLM, RAG y esquemas.
- `patches/nuevo-test-corpus-loader.patch`: prueba de catálogo, idempotencia, fallos y ciclo de vida de precarga.
- `patches/nuevo-test-cliente-frontend.patch`: prueba de mapeos y cliente HTTP de `frontend/app.py`.

No se incluyen resultados JSON/PDF ni se declaran como evidencias reproducidas: los documentos no rastreados en `docs/` y `auditoria_test_TC-*.json` son evidencia local y su autoría/ejecución no puede inferirse del estado Git actual.

## Dependencias y PR

Depende de todos los parches funcionales de Mariana, Mónica, Jaime y Alexis. Aplicar los parches de pruebas tras integrar el producto; conservar la trazabilidad de cualquier ejecución nueva en el PR de QA. No agregar los archivos `.pyc` eliminados localmente.

## Aceptación mínima

- Cada prueba se ejecuta contra el contrato finalmente integrado, sin claves ni llamadas a proveedores reales.
- Las pruebas de cliente no inician Streamlit ni una red real.
- La evidencia nueva identifica autor, fecha, comando y resultado verificable.

## Autoría

No hay historial Git que permita atribuir estas pruebas locales a Dayanara. El paquete corresponde a su área solicitada; la autoría queda pendiente de confirmación.
