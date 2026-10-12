# Paquete Jaime — agentes y orquestación MVP

## Serie incremental de rama

Aplicar y confirmar por separado: `incrementos/01-telemetria-llm.patch`, después `incrementos/02-orquestacion-pedagogica.patch`. Los archivos de `patches/` son el consolidado de referencia y no deben aplicarse si ya se usó la serie.

## Objetivo

Incorporar solo las mejoras necesarias del orquestador pedagógico y de su proveedor LLM: telemetría por solicitud, manejo limitado de reintentos de Gemini y metadatos educativos.

## Archivos y diferencia

`patches/agentes-orquestacion.patch` contiene:

- `backend/backend/app/services/agent_service.py`: selecciona generación con telemetría cuando existe, calcula conceptos/tiempo de estudio y conserva la respuesta estructurada.
- `backend/backend/app/services/llm_service.py`: añade `LLMTelemetry`, extracción de uso y política acotada para errores transitorios de Gemini.

No incorpora el árbol histórico `agents/` de la rama de Jaime ni dependencias nuevas; por ello no sustituye el pipeline RAG/FastAPI existente.

## Dependencias y PR

Depende del contrato de Mariana, que expone los nuevos metadatos. No depende de los artefactos físicos del corpus. Aplicar este único parche a una rama desde `dev`, revisar los cambios de manejo de errores y presentar un PR separado.

## Aceptación mínima

- `generate()` conserva retorno `str`; `generate_with_telemetry()` retorna `(contenido, telemetría)`.
- Los fallos de cuota y tasa no exponen claves ni duplican una generación.
- El orquestador sigue generando contenido cuando el proveedor no publica telemetría.

## Autoría

Hay antecedentes de Jaime en `77c503a` para agentes, pero este diff local no está en un commit. La asignación es funcional; no confirma que cada línea sea de Jaime.
