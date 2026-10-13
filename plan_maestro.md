# Plan Maestro — MVP G10_Nuevamente_Equipo48

## 1. Objetivo

Consolidar una versión local, ejecutable, coherente y verificable del MVP de NuevaMente, aprovechando los aportes existentes del equipo y evitando duplicaciones de arquitectura.

La consolidación local es una fase de laboratorio. No constituye una nueva versión oficial del producto ni debe publicarse en el repositorio remoto.

## 2. Roles y responsabilidades

### ChatGPT — Director técnico y arquitectónico

- Definir el orden de trabajo y los objetivos de cada iteración.
- Evaluar la arquitectura, los contratos entre componentes y los riesgos.
- Entregar prompts acotados para el agente local.
- Revisar resultados, errores, pruebas y evidencias.
- Decidir el siguiente paso a partir del reporte de ejecución.
- Evitar modificaciones especulativas y cambios de alcance no justificados.

### Google Antigravity — Agente ejecutor local

- Leer y analizar el código real antes de modificarlo.
- Ejecutar las tareas autorizadas dentro de su alcance.
- Resolver detalles de implementación que no alteren la arquitectura ni los requisitos.
- Ejecutar pruebas, diagnosticar fallos y corregir errores relacionados con la tarea.
- Informar únicamente los archivos modificados, las pruebas ejecutadas, sus resultados y los bloqueos relevantes.
- Conservar los cambios existentes que no sean parte de la tarea.

### Usuario — Coordinación y supervisión

- Transmitir los prompts y devolver los reportes de ejecución.
- Aprobar operaciones que impliquen riesgos, cambios de alcance o decisiones reservadas.
- No tener que intervenir en cada comando rutinario.

## 3. Reglas permanentes de Git

### Rama de trabajo

La consolidación se realiza exclusivamente en la rama local:

`integration/mvp-consolidado`

### Restricciones

- No ejecutar `git push` desde esta rama.
- No crear PR desde esta rama.
- No modificar las ramas `dev` ni `main`.
- No cambiar de rama sin autorización explícita.
- No ejecutar `git reset --hard`, `git clean`, borrados masivos ni otros comandos destructivos sin autorización.
- No descartar, sobrescribir ni incorporar indiscriminadamente cambios preexistentes.
- No añadir archivos al repositorio por el simple hecho de que estén presentes.
- No versionar entornos virtuales, credenciales, archivos `.env`, cachés ni artefactos generados.
- No asumir que un archivo sin seguimiento es prescindible.
- Antes de cada tarea, revisar la rama actual, `git status` y el diff relevante.

Si la rama o el estado del repositorio no coinciden con lo esperado, el agente debe detener las operaciones de escritura, conservar el estado encontrado e informar la discrepancia.

## 4. Método obligatorio de trabajo

Toda tarea debe seguir este ciclo:

**PLAN → VERIFICAR → EJECUTAR → PROBAR → CORREGIR → REVERIFICAR**

1. **PLAN:** identificar objetivo, alcance, archivos probables y criterios de aceptación.
2. **VERIFICAR:** leer la implementación real, revisar dependencias, estado de Git y pruebas existentes.
3. **EJECUTAR:** hacer el cambio mínimo suficiente para cumplir el objetivo.
4. **PROBAR:** ejecutar primero las pruebas específicas y después las pruebas de regresión pertinentes.
5. **CORREGIR:** investigar los errores relacionados con el cambio y corregirlos sin ampliar arbitrariamente el alcance.
6. **REVERIFICAR:** repetir las pruebas, inspeccionar el diff y comprobar que no se hayan alterado archivos ajenos a la tarea.

No se debe afirmar que una tarea está validada si las pruebas correspondientes no se ejecutaron o fallaron.

## 5. Autonomía operativa controlada

El agente puede, sin pedir confirmación en cada paso:

- Leer archivos, explorar directorios y revisar historial y diferencias de Git.
- Ejecutar comandos de diagnóstico y pruebas.
- Usar el entorno virtual existente.
- Instalar dependencias declaradas en el proyecto cuando sea necesario y seguro.
- Implementar cambios acotados autorizados.
- Corregir defectos directamente relacionados con la tarea.
- Repetir pruebas y entregar evidencias.

Debe detenerse y consultar al director técnico cuando sea necesario:

- Cambiar la arquitectura o el alcance funcional.
- Sustituir tecnologías, añadir servicios o introducir nuevas dependencias estructurales.
- Cambiar contratos de API o formatos de datos públicos.
- Eliminar funcionalidades, archivos fuente o datos.
- Modificar la configuración de producción o gestionar credenciales.
- Desactivar controles de seguridad, certificados SSL o validaciones para hacer pasar una prueba.
- Realizar operaciones destructivas o alterar ramas protegidas.
- Resolver un conflicto entre los requisitos del MVP y la implementación existente.

Un bloqueo en una tarea no debe impedir que se completen otras actividades independientes que sean seguras y estén autorizadas.

## 6. Estado técnico conocido

### Repositorio y entorno

- Repositorio local: `C:\PROYECTOS\G10_Nuevamente_Equipo48`
- Rama de consolidación: `integration/mvp-consolidado`
- Sistema operativo: Windows 10 Pro de 64 bits.
- Python: 3.12.10.
- Git, GitHub CLI, Docker, Node.js y npm están instalados.
- Existe un entorno virtual en `backend\backend\.venv`.
- El equipo dispone de 32 GB de RAM y no cuenta con GPU NVIDIA/CUDA.

El agente debe verificar las versiones y rutas actuales en lugar de reinstalar herramientas o repetir inventarios completos innecesariamente.

### Estado de cambios conocido

En la última revisión se encontraban:

- Modificado: `backend/backend/app/api/v1/endpoints/adaptacion.py`
- Modificado: `backend/backend/tests/test_document_service.py`
- Sin seguimiento: `.gitignore`
- Sin seguimiento: `_revision_corpus_fase05/`

Estos cambios deben conservarse y revisarse antes de cualquier nueva escritura. No se debe asumir que el estado actual sigue siendo idéntico.

### Backend existente

La implementación de Mariana constituye la base técnica principal identificada:

- `backend/backend/app/main.py`
- `backend/backend/app/services/document_service.py`
- `backend/backend/app/services/rag_service.py`
- `backend/backend/app/services/llm_service.py`
- `backend/backend/app/services/agent_service.py`
- `backend/backend/app/services/oci_service.py`
- `backend/backend/app/api/v1/endpoints/`
- `backend/backend/tests/`

El backend utiliza FastAPI y contempla carga y procesamiento documental, recuperación de contexto mediante RAG, generación de contenido pedagógico, validaciones y pruebas automatizadas.

La estructura de carpetas tiene un anidamiento `backend/backend`. No se debe reorganizar sin necesidad demostrada.

### Frontend

`frontend/app.py` contiene una interfaz Streamlit que, según el análisis previo, presenta resultados de ejemplo y no consume todavía los endpoints reales de FastAPI. Esta integración debe verificarse y abordarse después de estabilizar el backend.

### Aportes alternativos

La rama `feature/backend-agentes`, asociada al trabajo de Jaime, incluye ideas de agentes pedagógicos, escritor/crítico, frontend y procesamiento documental.

No se debe fusionar la rama completa de manera mecánica ni mantener dos pipelines paralelos de RAG o LLM. Las ideas que aporten valor se evaluarán para adaptarlas a los servicios existentes, después de validar su utilidad.

## 7. Arquitectura objetivo del MVP

### Flujo funcional esperado

1. El usuario selecciona o carga un documento elegible.
2. El sistema extrae y divide el contenido en fragmentos.
3. El sistema genera embeddings y recupera contexto pertinente.
4. El usuario define el perfil, el formato y el nicho.
5. El servicio de agentes genera el contenido apoyándose en el contexto recuperado.
6. El sistema valida la estructura y las restricciones del resultado.
7. El frontend presenta el contenido y los errores de forma comprensible.
8. Los metadatos y la trazabilidad permiten identificar las fuentes utilizadas.

### Componentes principales

- **DocumentService:** extracción y segmentación documental.
- **RAGService:** embeddings, índice y recuperación de fragmentos pertinentes.
- **LLMService:** integración con el proveedor de modelos configurado.
- **AgentService:** orquestación pedagógica y generación de contenido.
- **OCIService:** almacenamiento externo opcional, con degradación controlada si no está configurado.
- **API FastAPI:** contratos y exposición de funcionalidades.
- **Frontend Streamlit:** interfaz conectada a la API real.

La arquitectura debe reutilizar los componentes existentes siempre que satisfagan los requisitos. No se añadirá infraestructura nueva sin justificación.

### Perfiles previstos

- `principiante`
- `junior`
- `lider_tecnico`
- `ejecutivo`

### Formatos previstos

- `tutorial`
- `flashcards`
- `quiz`
- `resumen_ejecutivo`
- `guion_clase`

### Nichos previstos

- `fintech`
- `salud`
- `ecommerce`
- `general`

Los valores deben verificarse contra los esquemas y contratos reales del código antes de usarse como especificación definitiva.

## 8. Estrategia de modelos y recursos

- Priorizar los servicios de LLM externos ya contemplados en el proyecto.
- No instalar un modelo generativo local por defecto.
- Mantener el procesamiento documental y el backend en el equipo local.
- Usar Sentence Transformers y FAISS si las dependencias y el flujo existente lo requieren.
- Evitar descargas repetidas de modelos y dependencias.
- No desactivar SSL ni introducir soluciones inseguras para superar errores de descarga.
- Si falta una credencial o un proveedor LLM no está configurado, el sistema debe responder con un error controlado y documentado, no con un fallo interno inesperado.
- Las pruebas unitarias deben poder simular las dependencias externas cuando corresponda.

## 9. Corpus y trazabilidad

La carpeta `_revision_corpus_fase05/` contiene material de revisión que debe tratarse como datos locales pendientes de evaluación.

El inventario identificado previamente contiene 22 registros:

- 18 clasificados como `APTO`.
- 2 clasificados como `APTO_CON_REVISIÓN`.
- 2 clasificados como `NO_APTO`.

Estas clasificaciones deben verificarse contra los archivos actuales. No se deben incorporar automáticamente documentos `NO_APTO` ni materiales con licencias o permisos ambiguos.

La primera integración del corpus debe centrarse en metadatos, elegibilidad, procedencia y trazabilidad. La incorporación de documentos al RAG requerirá una validación específica de licencias, disponibilidad, integridad y pertinencia.

## 10. Criterios de calidad del MVP

- La API inicia de forma reproducible.
- El endpoint de salud funciona.
- Las solicitudes inválidas se rechazan con errores claros.
- La ausencia de un servicio externo se maneja de forma controlada.
- La carga y el procesamiento documental funcionan.
- La recuperación de contexto respeta el documento solicitado.
- Los formatos generados cumplen su estructura y los requisitos pedagógicos.
- El frontend consume la API real y presenta los errores adecuadamente.
- Las pruebas son reproducibles sin depender innecesariamente de descargas externas.
- No se presentan como verificadas capacidades que no se han probado.
- Se preservan la procedencia y las restricciones de los materiales.
- Los cambios son pequeños, revisables y coherentes con el MVP.

No se exigirá que todas las pruebas pasen antes de comprender sus fallos. Los errores de implementación, configuración, dependencias externas y pruebas mal configuradas deben identificarse por separado.

## 11. Clasificación de cada aporte

Todo aporte existente y cada necesidad identificada se clasificará como:

- **A — Conservar:** funciona y satisface el MVP.
- **B — Adaptar:** aporta valor, pero requiere ajustes.
- **C — Reemplazar:** no satisface los requisitos y existe una alternativa justificada.
- **D — Descartar:** no aporta valor al alcance acordado o genera duplicación injustificada.
- **E — Falta implementar:** funcionalidad requerida que todavía no existe.

La clasificación debe basarse en código inspeccionado, pruebas, requisitos y evidencias, no únicamente en el nombre de la rama o en descripciones previas.

## 12. Fases de trabajo

### Fase 1 — Verificar y estabilizar la base local

- Confirmar el estado real de Git y preservar los cambios.
- Resolver los defectos de validación y manejo de errores.
- Separar fallos de código, pruebas, configuración y servicios externos.
- Establecer pruebas reproducibles para el backend.

### Fase 2 — Consolidar los servicios del backend

- Verificar el flujo de carga documental.
- Verificar la recuperación RAG.
- Verificar la generación y validación de contenidos.
- Evitar duplicar los servicios existentes.
- Comprobar degradación controlada cuando falten servicios externos.

### Fase 3 — Conectar el frontend

- Integrar Streamlit con los endpoints reales.
- Manejar estados de carga, respuestas, errores y configuración.
- Validar el flujo completo de usuario.

### Fase 4 — Integrar corpus y trazabilidad

- Verificar metadatos y elegibilidad.
- Incorporar únicamente material autorizado y pertinente.
- Probar la trazabilidad del contexto recuperado.

### Fase 5 — Validación integral

- Ejecutar pruebas unitarias, de integración y del flujo principal.
- Documentar dependencias y configuración.
- Registrar limitaciones pendientes y criterios de aceptación cumplidos.
- Confirmar que el MVP puede ejecutarse desde un entorno limpio y reproducible.

### Fase 6 — Distribución del trabajo al equipo

Solo después de estabilizar y validar el MVP local:

- Descomponer los cambios validados por área y responsabilidad.
- Asignar tareas a los responsables correspondientes.
- Implementar cada tarea en su rama de trabajo.
- Abrir PR hacia `dev`.
- Validar el MVP integrado en `dev`.
- Finalmente, integrar `dev` en `main` conforme al proceso del equipo.

La rama `integration/mvp-consolidado` no se publicará ni se fusionará como una unidad.

## 13. Distribución de responsabilidades propuesta

Sujeta a confirmar con el equipo:

- **Mariana:** backend y servicios.
- **Jaime:** lógica pedagógica y agentes.
- **Alexis:** corpus, datos y trazabilidad.
- **Responsable de frontend:** integración Streamlit y experiencia de usuario.
- **Equipo:** integración y validación transversal.

La distribución definitiva se realizará después de identificar los cambios realmente necesarios.

## 14. Protocolo de iteración y reportes

ChatGPT definirá una tarea por iteración, con:

- Objetivo.
- Alcance y archivos previsibles.
- Restricciones.
- Criterios de aceptación.
- Pruebas concretas.
- Condiciones de detención.

Antigravity devolverá un reporte conciso con:

1. Archivos modificados.
2. Resumen de cambios.
3. Comandos y pruebas ejecutadas.
4. Resultados exactos: aprobados, fallidos o no ejecutados.
5. Errores relevantes y causa identificada o pendiente.
6. Estado de Git final.
7. Bloqueos o decisiones que requieran evaluación técnica.

No deberá incluir largos volcados de consola salvo que se soliciten o sean necesarios para diagnosticar un error.

## 15. Regla final

El objetivo no es maximizar la cantidad de cambios, sino conseguir el MVP más pequeño que satisfaga los requisitos, sea ejecutable, tenga pruebas reproducibles y preserve la integridad del trabajo del equipo.

Ninguna instrucción de este documento autoriza por sí sola operaciones destructivas, cambios de arquitectura, publicación remota o ampliaciones de alcance. Las tareas concretas se autorizan mediante los prompts de cada iteración.
