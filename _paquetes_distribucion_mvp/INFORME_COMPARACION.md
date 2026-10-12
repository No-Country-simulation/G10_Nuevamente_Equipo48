# Comparación: MVP local consolidado frente a `origin/dev`

## Referencias verificadas

- Rama actual: `integration/mvp-consolidado`.
- Referencia remota disponible: `origin/dev` en `f56a0b3`.
- `integration/mvp-consolidado` también resuelve a `f56a0b3`; la divergencia de commits es `0`/`0`.
- La rama actual sigue una referencia remota eliminada: `origin/integration/mvp-consolidado [gone]`.
- Por tanto, el MVP adicional no está publicado en commits: vive en cambios locales modificados, eliminados y no rastreados.

## Estado local observado

El árbol tiene modificaciones en código, pruebas y frontend; además hay archivos no rastreados de corpus, documentación y evidencia. El diff rastreado frente a `origin/dev` contiene 35 rutas, 2.119 inserciones y 338 eliminaciones, incluyendo 24 eliminaciones de bytecode `__pycache__`. Esas eliminaciones binarias no se incluyen en ningún paquete porque no aportan funcionalidad. Los nuevos archivos fuente `corpus_loader.py` y dos suites de prueba se empaquetan como parches independientes.

## Ya presente en `dev`

`dev` contiene la base FastAPI, el endpoint de adaptación, los esquemas, `DocumentService`, `RAGService`, `LLMService`, `AgentService` y la interfaz Streamlit inicial. La revisión de código muestra que la UI de base es demostrativa y que los cambios de integración/API, precarga, telemetría y metadatos descritos abajo no están en la referencia `origin/dev`.

## Cambios adicionales para reproducir el MVP local

| Área | Cambio comprobado en código | Paquete |
| --- | --- | --- |
| API | Control de `agent_service` ausente; validación y nuevos metadatos de adaptación | Mariana |
| Orquestación | Telemetría LLM, reintentos Gemini y metadatos pedagógicos en la respuesta | Jaime |
| RAG/corpus | Búsqueda/estado por documento y precarga APTO no bloqueante | Alexis |
| UI | Carga HTTP, solicitud de adaptación, renderizado de respuesta y manejo de error | Mónica |
| QA | Suites para contrato, RAG, LLM, precarga y cliente UI | Dayanara |

## Cambios que requieren revisión antes de distribuir

- La precarga depende de tres archivos físicos del corpus. No se empaquetan: el árbol local de corpus incluye binarios y material de terceros (aprox. 245 MB). Deben confirmarse ruta, licencia, procedencia y hashes antes de afirmar que la precarga es reproducible.
- `corpus_loader.py` incluye una ruta absoluta local como último candidato. Es funcionalmente tolerante, pero no es portable y requiere decisión de revisión.
- `main.py` captura cualquier excepción de precarga y permite iniciar la API. Esto evita bloquear el MVP, pero debe revisarse que el registro sea suficiente para operación.
- El frontend renderiza texto generado con HTML permitido; revisar el tratamiento de contenido no confiable antes de exponerlo fuera del entorno controlado.
- Los reportes y JSON locales afirman ejecuciones históricas, pero esta tarea no ejecutó pruebas. No se tratan como resultados nuevos ni se atribuyen a Dayanara.

## Dependencias entre áreas

`Alexis (precarga/RAG)` y `Mariana (contrato)` preparan la base; `Jaime (orquestación)` llena parte de los metadatos del contrato; `Mónica (UI)` consume los endpoints y esos campos; `Dayanara (QA)` depende del producto integrado. La precarga puede entrar sin los binarios, pero no habilita corpus precargado hasta recibir los artefactos aprobados.

## Separación y atribución

Los parches se separaron por archivos sin solapamiento. No hay evidencia Git que atribuya los cambios locales no comprometidos a una persona concreta. Las asignaciones de paquete reflejan el área indicada en la tarea; la autoría de cada cambio queda pendiente de confirmación. El historial sí muestra antecedentes: Mónica para la base del frontend (`3304a3a`), Jaime para una rama histórica de agentes (`77c503a`) y Alexis para corpus (`5981e6e` en `origin/data-analytics-corpus`).
