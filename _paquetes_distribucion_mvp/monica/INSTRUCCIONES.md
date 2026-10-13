# Paquete Mónica — Streamlit e integración API

## Serie incremental de rama

Aplicar y confirmar por separado: `incrementos/01-cliente-http.patch`, después `incrementos/02-flujo-ui-api.patch`. Los archivos de `patches/` son el consolidado de referencia y no deben aplicarse si ya se usó la serie.

## Objetivo

Reemplazar el flujo visual simulado de `origin/dev` por un cliente Streamlit que carga documentos y solicita adaptaciones a FastAPI.

## Archivos y diferencia

`patches/frontend-streamlit-api.patch` modifica únicamente `frontend/app.py`:

- Define URL configurable y funciones HTTP para `/api/v1/files/upload` y `/api/v1/adaptacion`.
- Mapea las opciones visibles a los enums del contrato API.
- Muestra contenido, métricas, fuentes y errores de la respuesta real.

No incluye logotipos ni archivos binarios. El archivo existente de `origin/dev` es una interfaz de demostración; el parche contiene la integración funcional adicional.

## Dependencias y PR

Depende del paquete de Mariana (contrato) y del de Jaime (generación). Aplicar solamente este parche en una rama desde `dev`, revisar el diff y abrir el PR individual. El test del cliente queda en el paquete de Dayanara para evitar mezclar producto y QA.

## Aceptación mínima

- El cliente usa ambos endpoints reales y propaga errores HTTP legibles.
- Las opciones enviadas coinciden con los valores permitidos por FastAPI.
- La interfaz no requiere secretos embebidos; admite `API_BASE_URL` o `BACKEND_URL`.

## Autoría

El historial sí asocia la base original de `frontend/app.py` a Mónica (`3304a3a`), pero el diff local actual no está comprometido; su autoría concreta queda pendiente de confirmación.
