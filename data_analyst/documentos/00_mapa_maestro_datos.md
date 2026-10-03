# NuevaMente — Mapa Maestro de Datos del Corpus

## 1. Propósito

Este documento establece la relación entre el esquema inicial de metadatos y la matriz consolidada v2, para que búsqueda, evaluación, inventario y trazabilidad trabajen sobre un modelo coherente sin duplicar información innecesariamente.

La matriz consolidada v2 permanece como instrumento maestro de evaluación. Los metadatos documentales complementan la investigación, identificación, verificación y control de las fuentes.

## 2. Modelo de trabajo

```text
BÚSQUEDA DOCUMENTAL
        ↓
IDENTIFICACIÓN + METADATOS + EVIDENCIA
        ↓
MATRIZ MAESTRA DE EVALUACIÓN
        ↓
RESULTADO: APTO / APTO_CON_REVISIÓN / NO_APTO
        ↓
SELECCIÓN DEL CORPUS DE PRUEBA
```

## 3. Mapeo de campos

| Campo original | Tratamiento consolidado | Representación / campo relacionado | Función | Validación mínima |
|---|---|---|---|---|
| identificador_documento | Se conserva | `ID` | Identificación única | No duplicado |
| titulo | Se conserva | `Documento` | Identificación documental | No vacío |
| fuente | Se conserva | `Fuente / Autor` | Autor, institución u organización | Fuente identificable |
| direccion_fuente | Se conserva | `Fuente principal` | URL/origen verificable | URL o referencia verificable |
| version | Se conserva como metadato complementario | Complementario | Identifica la versión evaluada | Registrar cuando la fuente la proporcione |
| fecha_publicacion | Se conserva como metadato complementario | Complementario | Contexto temporal | Registrar cuando exista |
| ultima_actualizacion | Se conserva como metadato complementario | Complementario | Vigencia/control documental | Registrar cuando exista |
| idioma | Se conserva | `Idioma` | Clasificación y uso | Valor controlado |
| formato | Se conserva | `Formato` | Compatibilidad con entradas del MVP | PDF / Markdown / TXT o descripción exacta |
| dominio | Se conserva | `Dominio` | Clasificación temática | Dominio controlado |
| tema | Se conserva como metadato complementario | Complementario | Mayor precisión temática | No confundir con dominio |
| descripcion | Se conserva como metadato complementario | Complementario | Caracterización del contenido | Basada en la fuente |
| cantidad_paginas | Se conserva como metadato complementario | Complementario | Control de extensión/integridad | Registrar cuando aplique |
| licencia | Se conserva | `Licencia / condiciones` | Condiciones de uso/adaptación | No asumir permiso; verificar |
| integridad | Se conserva como criterio de evaluación | Criterio `Integridad` + evidencia en observaciones | Comprobar documento completo | Completo, no fragmentado |
| pertinencia | Se conserva como criterio de evaluación | Criterio `Pertinencia` | Relación con NuevaMente | Justificación verificable |
| capacidad_adaptacion | Se conserva como criterio de evaluación | `Potencial por formato` + `Adaptación requerida` | Potencial de adaptación | Evaluación por formatos |
| procedencia | Se conserva como criterio de evaluación | Criterio `Procedencia/licencia` + `Fuente principal` | Verificación de origen | Evidencia de procedencia |
| estado_seleccion | Se conserva como control de proceso | Hoja `Finalistas propuestos` + control documental | Seguimiento de selección | No confundir con `Resultado` |
| observaciones_validacion | Se conserva | `Observaciones` | Evidencia y notas de revisión | Debe explicar excepciones/revisiones |
| uso_previsto | Se conserva como metadato contextual | Complementario | Contextualiza la utilización | Registrar cuando aporte información útil |

## 4. Campos actuales de la matriz consolidada v2

La matriz maestra mantiene 17 columnas principales:

1. ID
2. Documento
3. Dominio
4. Fuente / Autor
5. Formato
6. Idioma
7. Licencia / condiciones
8. Resultado
9. Observaciones
10. Fuente principal
11. Audiencia original
12. Complejidad para NNA
13. Adecuación a NNA
14. Adaptación requerida
15. Potencial por formato
16. Viabilidad de adaptación a NNA
17. Observación de adaptación a NNA

No se reemplazan estas columnas por el esquema inicial. Se complementan con metadatos documentales y con criterios de validación.

## 5. Diferencia entre Resultado y Estado de selección

`Resultado` responde a la aptitud del documento respecto de los criterios del corpus:

- `APTO`
- `APTO_CON_REVISIÓN`
- `NO_APTO`

El estado de selección responde al avance o decisión del proceso de conformación del corpus y no debe confundirse con el resultado de evaluación.

Los finalistas registrados en la matriz v2 son candidatos propuestos; mientras no exista una decisión del equipo, no deben presentarse como corpus final.

## 6. Reglas de consistencia

- Un documento debe conservar un único ID.
- El título de la matriz, inventario y JSON debe corresponder al mismo documento.
- La fuente principal debe poder rastrearse.
- La licencia debe registrarse con las condiciones concretas conocidas; no se debe inferir que todo contenido de Internet es reutilizable.
- Integridad, pertinencia y procedencia deben poder justificarse mediante evidencia.
- `APTO`, `APTO_CON_REVISIÓN` y `NO_APTO` son resultados de evaluación y no sustituyen el control de selección.
- La evaluación NNA es una dimensión separada y no sustituye el resultado general del corpus.
- Los metadatos no encontrados deben quedar explícitamente pendientes de verificación; no se deben inventar valores.

## 7. Fuente de verdad por artefacto

La URL registrada en el inventario puede apuntar al archivo concreto o a su ubicación de descarga, mientras que `Fuente principal` en la matriz puede apuntar a la página institucional que sirve como evidencia documental. No es una inconsistencia siempre que ambas referencias permitan rastrear el mismo documento.


| Artefacto | Fuente de verdad principal |
|---|---|
| Matriz maestra | Matriz consolidada v2 |
| Criterios | Criterios de la matriz consolidada v2 |
| Metadatos documentales | Este mapa + esquema de metadatos |
| Inventario CSV | Registros consolidados de la matriz + metadatos complementarios verificados |
| JSON | Esquema de metadatos consolidado |
| README | Estructura y procedimiento definidos en este paquete |

## 8. Criterio de cierre de esta consolidación

La consolidación se considera coherente cuando una misma fuente puede seguirse de extremo a extremo:

```text
fuente → documento → metadatos → evidencia → evaluación → resultado → selección → uso en pruebas
```

La existencia de un metadato faltante no debe convertirse automáticamente en `NO_APTO`; debe evaluarse según su impacto en identificación, trazabilidad, integridad, procedencia, licencia y uso previsto.
