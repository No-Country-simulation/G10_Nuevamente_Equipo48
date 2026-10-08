# Verificación estructural — Fase 05

- Matriz maestra presente en `matriz/`.
- Inventario CSV contiene 22 registros.
- IDs del inventario son únicos y coinciden con la matriz maestra.
- Resultado de evaluación solo usa APTO / APTO_CON_REVISIÓN / NO_APTO.
- Las columnas de NNA del inventario están pobladas a partir de la matriz.
- JSON de ejemplo es JSON válido.
- `Finalistas propuestos` contiene 8 propuestas y no modifica `estado_seleccion`.
- Esta verificación no determina la calidad sustantiva de los documentos ni reemplaza la revisión de fuentes.

- Las observaciones de adaptación NNA se conservan completas en el inventario; no se aceptan truncamientos con puntos suspensivos.
- Las referencias `direccion_fuente` del inventario y `Fuente principal` de la matriz pueden diferir cuando una apunta al archivo/descarga y la otra a la evidencia institucional, siempre que ambas sean trazables al mismo documento.
