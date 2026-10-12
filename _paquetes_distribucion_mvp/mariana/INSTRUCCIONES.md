# Paquete Mariana — backend y contrato API

## Serie incremental de rama

Aplicar y confirmar por separado: `incrementos/01-esquemas-contrato.patch`, después `incrementos/02-endpoint-defensivo.patch`. Los archivos de `patches/` son el consolidado de referencia y no deben aplicarse si ya se usó la serie.

## Objetivo

Incorporar los ajustes de contrato HTTP defensivo y de esquema que el MVP local necesita frente a `origin/dev`.

## Archivos y diferencia

`patches/backend-api-contract.patch` contiene cambios separados por archivo en:

- `backend/backend/app/api/v1/endpoints/adaptacion.py`: responde con error de configuración controlado si falta el servicio de agentes.
- `backend/backend/app/schemas/adaptacion.py`: rechaza `documento_id` vacío, usa tiempo UTC con zona y añade metadatos pedagógicos y de telemetría.

No duplica cambios de `origin/dev`: ambos archivos difieren del commit `f56a0b3`, que es la referencia actual de `origin/dev`.

## Dependencias y PR

Depende del paquete de Jaime para que los campos de telemetría sean poblados, aunque los valores opcionales conservan compatibilidad sin él. Presentar un PR hacia `dev` aplicando solo este parche, revisar el diff y no incluir archivos `__pycache__`.

## Aceptación mínima

- Peticiones sin `agent_service` devuelven el error configurado, no un `AttributeError`.
- El contrato acepta los campos nuevos y conserva los existentes.
- `timestamp` tiene zona UTC y `documento_id` vacío es inválido.

## Autoría

El estado local no contiene commits para estos cambios; la asignación a Mariana es por área solicitada, no una atribución histórica confirmada.
