# Auditoría de consolidación del corpus — Fase 03

Fecha de ejecución: 2026-10-02

## 1. Resultado estructural

- Matriz maestra: 22 registros, 17 columnas.
- IDs únicos en matriz: True.
- Inventario CSV: 22 registros, 29 columnas.
- Correspondencia de IDs matriz ↔ CSV: True.
- Correspondencia de título y resultado: True.

## 2. Distribución actual

### Resultado de evaluación
{
  "APTO": 12,
  "APTO_CON_REVISIÓN": 8,
  "NO_APTO": 2
}

### Estado de selección
{
  "EN_EVALUACION": 22
}

Los 22 registros permanecen en `EN_EVALUACION`; esto es coherente con que los finalistas actuales todavía sean propuestas y no exista una selección final cerrada.

## 3. Hallazgo crítico de metodología

Se encontraron **3 documentos marcados `APTO` en el resultado de la matriz mientras `integridad` permanece `PENDIENTE_DE_VERIFICACION` en el inventario**: NM-006, NM-011, NM-012.

Esto no se corrige automáticamente. Debe resolverse mediante una de estas dos acciones antes del cierre del corpus:

1. Verificar el archivo exacto y cerrar la integridad como verificada; o
2. Si la verificación sigue pendiente, reclasificar el resultado como `APTO_CON_REVISIÓN`.

La segunda decisión solo debe aplicarse cuando la evidencia confirme que la pendiente afecta un requisito crítico.

## 4. Cobertura de metadatos complementarios

{
  "version": {
    "missing_or_pending": 19,
    "total": 22
  },
  "fecha_publicacion": {
    "missing_or_pending": 18,
    "total": 22
  },
  "ultima_actualizacion": {
    "missing_or_pending": 22,
    "total": 22
  },
  "cantidad_paginas": {
    "missing_or_pending": 18,
    "total": 22
  }
}

URL/fuente principal ausente en: NM-022.

La ausencia de versión, fechas o páginas no implica por sí misma que un documento sea no apto; son metadatos que deben recuperarse cuando la fuente los proporcione.

## 5. Evaluación de la consolidación

### Se considera correcto
- La matriz v2 sigue siendo la referencia de evaluación.
- El inventario contiene los mismos 22 IDs.
- El vocabulario de resultados está alineado.
- El inventario conserva los campos documentales inicialmente planteados.
- Los finalistas no se convierten en selección definitiva.

### Debe corregirse antes del cierre
- Definir formalmente cuándo un resultado `APTO` se considera cerrado.
- Verificar los documentos con integridad pendiente.
- Completar procedencia, pertinencia y capacidad de adaptación con evidencia/mapeo explícito.
- Completar la URL de NM-022 si se confirma una fuente válida o documentar por qué no existe.

## 6. Próximo paso

La siguiente ejecución debe ser la **reconciliación de evidencia por documento**, empezando por los campos críticos: archivo exacto, integridad, procedencia/licencia y fuente principal. Después se completan versión, fechas y páginas cuando la fuente las proporcione.
