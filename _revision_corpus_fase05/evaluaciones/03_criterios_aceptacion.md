# NuevaMente — Criterios de Aceptación y Pruebas del Corpus

## 1. Objetivo

Establecer pruebas verificables para determinar si un documento puede considerarse apto como fuente del corpus de NuevaMente.

El objetivo de estas pruebas es comprobar la calidad y utilidad de la fuente antes de que sea utilizada por las etapas posteriores del MVP.

## 2. Criterios

| ID | Criterio | Qué se verifica | Evidencia esperada |
|---|---|---|---|
| C01 | Identificación de fuente | Autor, organización, origen y ubicación verificable | Autor/institución + URL o referencia |
| C02 | Calidad | Contenido técnico claro, estructurado, coherente y suficientemente desarrollado | Documento legible y desarrollado |
| C03 | Integridad | Documento completo, no fragmentado y conservable en su versión original | Archivo completo / versión identificable |
| C04 | Pertinencia | El contenido aporta conocimiento técnico útil para NuevaMente | Tema y dominio justificables |
| C05 | Potencial pedagógico | Existen conceptos, explicaciones, procedimientos, ejemplos, prerrequisitos o profundidad aprovechables | Contenido estructurado y reutilizable pedagógicamente |
| C06 | Potencial de adaptación | El contenido permite construir uno o más formatos de salida previstos | Potencial documentado en matriz |
| C07 | Procedencia/licencia | El origen y las condiciones de uso son verificables | Licencia/condiciones + fuente |
| C08 | Adecuación | El documento puede adaptarse a perfiles configurables; la fuente no necesita estar dirigida originalmente a NNA | Análisis de complejidad/adaptación |

## 3. Pruebas mínimas

### P01 — Documento disponible

Debe existir un archivo concreto en un formato soportado por el MVP.

### P02 — Fuente verificable

Debe existir información suficiente para identificar y rastrear la procedencia del documento.

### P03 — Integridad

Debe poder demostrarse que el archivo utilizado representa el documento completo o la versión completa que se pretende incorporar.

### P04 — Condiciones de uso

La licencia o condiciones deben estar identificadas cuando existan. Una restricción que impida la adaptación prevista constituye una condición que debe reflejarse en la evaluación.

### P05 — Calidad y desarrollo

El documento debe contener información técnica suficientemente desarrollada para que la adaptación no dependa de completar el conocimiento con fuentes externas no registradas.

### P06 — Pertinencia

El contenido debe aportar conocimiento relevante para el propósito educativo/técnico de NuevaMente.

### P07 — Potencial de adaptación

Debe ser posible justificar al menos un uso pedagógico entre los formatos contemplados por el proyecto, teniendo en cuenta el perfil y el nivel de detalle.

### P08 — Trazabilidad

Debe poder relacionarse el registro con su fuente, archivo y observaciones de validación.

## 4. Regla de decisión

`APTO` requiere que no exista un incumplimiento crítico en identificación, integridad, pertinencia, procedencia/licencia o utilidad del contenido.

`APTO_CON_REVISIÓN` se utiliza cuando el documento presenta valor suficiente para continuar en evaluación, pero existe una verificación concreta pendiente que debe resolverse antes de incorporarlo definitivamente.

`NO_APTO` se utiliza cuando existe un incumplimiento que impide utilizar el documento en el corpus de prueba en su estado actual.

## 5. Evidencia y reproducibilidad

Cada decisión debe poder reconstruirse a partir del documento, sus metadatos, la evidencia disponible y la observación registrada.

No se debe declarar un documento como apto únicamente por la reputación de la fuente o por la disponibilidad del enlace.

## 6. Evaluación NNA

La evaluación de viabilidad para NNA se mantiene separada del resultado general. Un documento puede ser `APTO` como fuente y requerir una adaptación considerable para un escenario NNA.
