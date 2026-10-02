# NuevaMente — Esquema de Metadatos del Corpus

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---:|---|
| identificador_documento | texto | Sí | Identificador único interno |
| titulo | texto | Sí | Título del documento |
| fuente | texto | Sí | Autor, institución u organización |
| direccion_fuente | texto | Sí | Ubicación de procedencia |
| version | texto | No | Versión declarada por la fuente |
| fecha_publicacion | fecha/texto | No | Fecha de publicación |
| ultima_actualizacion | fecha/texto | No | Última actualización conocida |
| idioma | texto | Sí | Idioma del documento |
| formato | lista | Sí | PDF / Markdown / TXT |
| dominio | lista | Sí | Dominio del corpus |
| tema | texto | Sí | Tema principal |
| descripcion | texto | Sí | Descripción breve del contenido |
| cantidad_paginas | entero | No | Número de páginas, cuando aplique |
| licencia | texto | No | Licencia o condiciones de uso conocidas |
| integridad | lista | Sí | VERIFICADA / NO_VERIFICADA |
| pertinencia | lista | Sí | ALTA / MEDIA / BAJA |
| capacidad_adaptacion | lista | Sí | ALTA / MEDIA / BAJA |
| procedencia | lista | Sí | VERIFICADA / PARCIAL / NO_VERIFICADA |
| estado_seleccion | lista | Sí | CANDIDATO / EN_EVALUACION / APROBADO / RECHAZADO / RESERVA |
| observaciones_validacion | texto | No | Observaciones de la revisión |
| uso_previsto | texto | No | Incorporación / capacitación / educación técnica / reconversión profesional |
