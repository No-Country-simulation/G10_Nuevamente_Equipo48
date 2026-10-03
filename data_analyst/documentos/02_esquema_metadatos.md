# NuevaMente — Esquema Consolidado de Metadatos del Corpus

## 1. Propósito

Definir un único modelo de información para registrar los documentos investigados y relacionar sus metadatos documentales con la evaluación realizada en la matriz consolidada v2.

El modelo se divide en dos capas para evitar que la matriz se sobrecargue con datos que cumplen funciones distintas.

## 2. Capa A — Metadatos documentales

| Campo | Tipo | Obligatorio | Regla |
|---|---|---:|---|
| identificador_documento | texto | Sí | ID único interno |
| titulo | texto | Sí | Título del documento |
| fuente | texto | Sí | Autor, institución u organización |
| direccion_fuente | texto/URL | Sí | Fuente principal o ubicación verificable |
| version | texto | No | Registrar cuando exista |
| fecha_publicacion | fecha/texto | No | Registrar cuando exista |
| ultima_actualizacion | fecha/texto | No | Registrar cuando exista |
| idioma | texto | Sí | Idioma del documento |
| formato | texto/lista | Sí | PDF / Markdown / TXT o descripción exacta del archivo |
| dominio | texto/lista | Sí | Dominio controlado del corpus |
| tema | texto | No | Tema específico, distinto del dominio |
| descripcion | texto | No | Caracterización del contenido basada en la fuente |
| cantidad_paginas | entero | No | Cuando aplique al formato |
| licencia | texto | Sí | Condiciones identificadas o `PENDIENTE_DE_VERIFICACION` |
| uso_previsto | texto | No | Uso previsto dentro del MVP o trabajo documental |

## 3. Capa B — Evaluación y control

| Campo | Tipo | Obligatorio | Regla |
|---|---|---:|---|
| integridad | control | Sí para cierre | Verificación de documento completo |
| pertinencia | escala | Sí para cierre | ALTA / MEDIA / BAJA o evidencia equivalente definida por la matriz |
| capacidad_adaptacion | escala | Sí para cierre | ALTA / MEDIA / BAJA cuando se consolide como valoración general |
| procedencia | control | Sí para cierre | VERIFICADA / PARCIAL / NO_VERIFICADA |
| estado_seleccion | control | Sí | Seguimiento de la conformación del corpus |
| resultado_evaluacion | control | Sí | APTO / APTO_CON_REVISIÓN / NO_APTO |
| observaciones_validacion | texto | No | Evidencia, restricciones y pendientes |

## 4. Relación con la matriz consolidada v2

La matriz conserva sus 17 columnas principales y sigue siendo el instrumento maestro de evaluación:

`ID`, `Documento`, `Dominio`, `Fuente / Autor`, `Formato`, `Idioma`, `Licencia / condiciones`, `Resultado`, `Observaciones`, `Fuente principal`, `Audiencia original`, `Complejidad para NNA`, `Adecuación a NNA`, `Adaptación requerida`, `Potencial por formato`, `Viabilidad de adaptación a NNA`, `Observación de adaptación a NNA`.

Los campos documentales de la Capa A complementan la matriz cuando esta no los contiene explícitamente. La Capa B formaliza controles que deben poder respaldar el resultado de evaluación.

Cuando `pertinencia` o `capacidad_adaptacion` aparecen como `PENDIENTE_DE_VERIFICACION` en el inventario, esto no invalida por sí solo un resultado de evaluación: su evidencia puede residir en la matriz maestra. El inventario funciona como registro documental complementario y no duplica obligatoriamente toda la valoración cualitativa de la matriz.

## 5. Vocabulario controlado

### Resultado de evaluación

- `APTO`
- `APTO_CON_REVISIÓN`
- `NO_APTO`

### Control de integridad

- `VERIFICADA`
- `NO_VERIFICADA`
- `PENDIENTE_DE_VERIFICACION`

### Procedencia

- `VERIFICADA`
- `PARCIAL`
- `NO_VERIFICADA`
- `PENDIENTE_DE_VERIFICACION`

### Valoración general de pertinencia/adaptación

- `ALTA`
- `MEDIA`
- `BAJA`
- `PENDIENTE_DE_VERIFICACION`

## 6. Reglas de ausencia de información

Cuando un dato no esté disponible en la fuente o todavía no se haya verificado, no se debe inventar. Se utilizará `PENDIENTE_DE_VERIFICACION` en campos controlados o se dejará vacío en campos descriptivos opcionales, acompañado de una observación cuando sea relevante.

## 7. Regla de sincronización

El ID es la llave de relación entre documentos, matriz, inventario y JSON. Cualquier modificación en el esquema debe reflejarse de forma coherente en los artefactos dependientes.
