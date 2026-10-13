# Paquete Coordinación — integración y aceptación

## Objetivo

Coordinar PRs pequeños, sin reasignar autoría ni convertir el MVP en un solo paquete.

## Archivos y diferencia

Este paquete es documental y no trae parche de producto. El `.gitignore` local es no rastreado y no forma parte de la reconstrucción funcional; debe revisarse en un PR de mantenimiento independiente si se desea.

## Dependencias y PR

Seguir el orden de `../PLAN_INTEGRACION.md`. Cada responsable crea su propia rama desde el `dev` vigente, aplica únicamente el parche de su paquete, revisa el diff y abre su PR individual hacia `dev`. No se deben mezclar archivos de otro paquete ni artefactos binarios.

## Aceptación mínima

- Cada PR declara sus dependencias y queda revisable en aislamiento.
- Se resuelven antes de fusionar los pendientes de corpus, historial y evidencia.
- La equivalencia del MVP se valida después de integrar, no se presume de la existencia de archivos.
