# NuevaMente — Especificación del Corpus

## Propósito
Construir un corpus de documentos fuente confiables, completos, pertinentes y trazables para NuevaMente.

## Alcance
Selección, identificación, clasificación y validación de documentos fuente. No incluye la implementación del RAG.

## Formatos admitidos
- PDF
- Markdown (.md)
- Texto plano (.txt)

## Dominios
- Python / Programación
- Inteligencia Artificial / Datos
- Nube / Infraestructura
- Ciberseguridad

## Criterios mínimos
1. Ser un archivo completo.
2. Estar en PDF, Markdown o texto plano.
3. Tener fuente identificable.
4. Tener contenido pertinente al dominio.
5. Contener información suficiente para adaptación educativa.
6. Permitir identificar su procedencia.
7. Registrar versión y fecha cuando la fuente las proporcione.
8. Superar la revisión de integridad y pertinencia.

## Estados de selección
- CANDIDATO: encontrado y pendiente de revisión.
- EN EVALUACIÓN: revisión en curso.
- APROBADO: cumple los criterios y puede integrar el corpus.
- RECHAZADO: no cumple los criterios.
- RESERVA: válido, pero no seleccionado para la versión actual.

## Regla de integridad
Se conserva el documento original completo como fuente. Una página, fragmento o conjunto disperso de páginas web no sustituye al documento completo cuando se exige un documento íntegro.

## Trazabilidad
Cada documento debe poder relacionarse con su fuente de origen, versión o fecha cuando exista y su registro interno en el corpus.
