# NuevaMente — Especificación del Corpus Fuente

## 1. Propósito

Construir y mantener un corpus de documentos fuente técnicos, completos, pertinentes, trazables y con condiciones de uso identificables, destinado a servir como base documental para las pruebas del MVP de NuevaMente.

El corpus debe permitir demostrar que los documentos seleccionados contienen información suficiente y de calidad para la posterior adaptación educativa a los perfiles y formatos previstos por el proyecto.

## 2. Alcance de Data Analyst

Data Analyst comprende:

- búsqueda e identificación de documentos fuente;
- caracterización y registro de metadatos;
- verificación de fuente, procedencia y condiciones de uso;
- revisión de integridad y disponibilidad del documento completo;
- evaluación de calidad, pertinencia y potencial pedagógico;
- evaluación del potencial de adaptación a los formatos previstos;
- inventario, trazabilidad y control de selección;
- validación de consistencia entre matriz, inventario y registros de metadatos.

No comprende, en esta fase, la implementación del RAG, chunking, embeddings, Vector Store, prompts, generación de contenidos, backend o frontend.

## 3. Entradas documentales

El corpus de prueba debe trabajar con documentos en los formatos soportados por el MVP:

- PDF;
- Markdown (`.md`);
- texto plano (`.txt`).

Una fuente web puede utilizarse para localizar el documento, pero la unidad de corpus debe ser el documento fuente que pueda conservarse y trazarse como original.

## 4. Dominios

La clasificación de dominio se toma de la matriz consolidada v2 y podrá ampliarse cuando la búsqueda documental lo justifique, sin crear un dominio únicamente por conveniencia de registro.

Los dominios actualmente representados incluyen:

- Programación
- Bases de datos
- Redes
- Ciberseguridad
- IoT / Microcontroladores
- Electrónica
- Energía renovable
- GIS / Geoespacial
- Cloud / Desarrollo móvil
- Ingeniería / confiabilidad
- Ingeniería industrial
- Química
- Energía / Física aplicada
- Tecnología / sistemas
- Gráficos por computador
- Estructuras de datos / sistemas
- Rendimiento / sistemas
- Robótica
- Física

## 5. Criterios de aceptación

Un documento se evalúa mediante ocho criterios:

1. Identificación de fuente.
2. Calidad.
3. Integridad.
4. Pertinencia.
5. Potencial pedagógico.
6. Potencial de adaptación.
7. Procedencia/licencia.
8. Adecuación a perfiles configurables.

La evaluación de adecuación NNA se mantiene como dimensión separada cuando corresponda al MVP y no sustituye el resultado general del corpus.

## 6. Resultados de evaluación

- `APTO`: cumple las condiciones necesarias para considerarse fuente utilizable según la evaluación realizada.
- `APTO_CON_REVISIÓN`: presenta utilidad documental, pero mantiene una o más verificaciones o condiciones pendientes que deben resolverse antes de su incorporación definitiva.
- `NO_APTO`: no debe incorporarse al corpus de prueba en su estado actual.

El resultado de evaluación no equivale al estado de selección final del corpus.

## 7. Regla de integridad

El corpus conserva el documento completo como fuente. Un fragmento, una página aislada o un conjunto disperso de páginas web no sustituye al documento completo cuando el registro exige una fuente íntegra.

## 8. Regla de trazabilidad

Cada registro debe poder relacionarse con:

- un ID interno único;
- la fuente o autor;
- la fuente principal o URL cuando exista;
- la versión o fecha cuando la fuente las proporcione;
- el documento concreto utilizado para la evaluación;
- las observaciones que expliquen verificaciones, restricciones o decisiones.

## 9. Regla de licencia

Las condiciones de uso deben verificarse. No se presume que un documento disponible en Internet pueda ser modificado o reutilizado por el sistema.

Las condiciones que restrinjan la adaptación o generen incertidumbre relevante deben reflejarse en el resultado y en las observaciones.

## 10. Relación con las pruebas del MVP

El corpus debe proporcionar fuentes suficientes para construir los escenarios de demostración previstos por NuevaMente. La selección final debe considerar la posibilidad de adaptar una misma fuente a diferentes perfiles y formatos pedagógicos.

La calidad del documento fuente se evalúa aquí. La calidad de los contenidos generados posteriormente se valida en una fase distinta.

## 11. Control del proceso

La matriz consolidada v2 es el instrumento maestro de evaluación. El inventario y los registros de metadatos complementan la matriz y deben permanecer consistentes con ella.

Los candidatos de la hoja `Finalistas propuestos` son propuestas de trabajo y no constituyen por sí mismos el corpus final hasta que el equipo tome la decisión correspondiente.
