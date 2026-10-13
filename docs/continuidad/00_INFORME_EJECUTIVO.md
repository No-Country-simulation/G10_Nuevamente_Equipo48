# NuevaMente — Informe ejecutivo de continuidad

**Proyecto:** Hackathon ONE / Oracle Next Education & Alura  
**Equipo:** G10, Equipo 48  
**Fecha de consolidación:** 12 de octubre de 2026  
**Propósito:** cerrar contradicciones operativas, conservar las decisiones existentes y permitir que el trabajo continúe sin repetir auditorías ni depender de memoria conversacional.

## 1. Decisión ejecutiva

Continuar desde las auditorías ya realizadas. No rehacer la auditoría de Jaime salvo que cambie el código o aparezca evidencia nueva. Aprovechar Google Antigravity para ejecutar tareas técnicas por objetivos, con verificación automática y límites explícitos de seguridad. Mantener trazabilidad de autoría y no fusionar ni publicar cambios sin autorización.

La arquitectura objetivo es **un frontend Streamlit, una API FastAPI, un servicio coordinador de agentes (`AgentService`) y un servicio RAG (`RAGService`)**. La solución debe reutilizar los componentes sólidos del MVP integrado y adaptar selectivamente el patrón escritor-crítico de Jaime. No crear un segundo motor RAG ni sustituir el frontend integrado por la interfaz independiente de Jaime.

## 2. Estado de Git y política de integración

- Repositorio: `https://github.com/No-Country-simulation/G10_Nuevamente_Equipo48`
- Ruta local habitual: `C:\PROYECTOS\G10_Nuevamente_Equipo48`
- El commit `5ef29fd9ac1529a631a2f8371fb03866c68147d8` se publicó en `main` como MVP integrado. No requiere otro PR para volver a introducir el mismo cambio.
- `5ef29fd` también se identificó como referencia de auditoría: no tratarlo como una rama o propuesta nueva que deba fusionarse de nuevo.
- La rama `feature/backend-agentes` contiene la aportación de Jaime. La comparación de GitHub registrada en esta conversación indica que `main` y dicha rama están divergidas: `feature/backend-agentes` tiene 2 commits propios y está 3 commits detrás de `main`; base común reportada: `12045d12943e5d1f9ad80dd1f8c9783dd19f47b1`.
- La búsqueda de PR no encontró ninguno para el repositorio en la consulta realizada.
- Flujo de equipo previamente acordado: aportes individuales → PR a `dev` → integración y validación en `dev` → `main` estable. Antes de preparar el PR de Jaime, comprobar que `dev` tenga el baseline del MVP integrado; si no lo tiene, detenerse y resolver la divergencia de base. No abrir un PR a `main` por defecto.
- No crear ramas ni realizar escrituras remotas hasta completar la comprobación del estado y tener autorización explícita para esa operación.
- No reescribir historial, borrar ramas de compañeros ni descartar modificaciones locales.
- `integration/mvp-consolidado` se había definido como rama local de integración; no publicarla ni recrearla por iniciativa propia. `referencia/mvp-consolidado` fue eliminada anteriormente: no recrearla.

## 3. Auditoría de Jaime — conclusiones ya establecidas

Esta sección resume la auditoría ya realizada; no es una solicitud de repetirla.

### Backend y agentes
- El MVP integrado ya contiene `AgentService`, `LLMService`, `RAGService` y `DocumentService`, además de contratos API y pruebas.
- Jaime aporta un grafo LangGraph escritor → crítico → reintento condicional (`agents/graph.py`), nodos (`agents/nodes.py`), estado y esquemas.
- Su crítica verifica principalmente estructura JSON, estado de error y presencia de `contenido_adaptado`; eso no constituye verificación semántica suficiente de fidelidad a las fuentes.
- La interfaz independiente de Jaime invoca nodos directamente en lugar de usar el grafo completo; `run_pipeline.py` sí invoca el grafo.
- Decisión: adaptar selectivamente el patrón escritor-crítico al coordinador existente, no reemplazar todo el backend por el de Jaime. Mantener procedencia y atribución de su aporte. Jaime autorizó integrar los aportes funcionales conservando su autoría; se encuentra ausente/sin acceso al equipo según el contexto registrado.

### RAG
- MVP: embeddings semánticos y FAISS.
- Jaime: recuperación léxica con frecuencias de palabras y similitud coseno.
- Decisión: conservar el RAG semántico del MVP como motor principal; no duplicar motores. Evaluar el código léxico de Jaime solo si aporta una función concreta y probada.

### Frontend
- MVP: `frontend/app.py`, interfaz Streamlit integrada con FastAPI, carga de documentos, adaptación, metadatos, métricas, fragmentos fuente, estado de servicio y descarga JSON.
- Jaime: `app.py` independiente, Streamlit que llama escritor/crítico directamente y procesa PDF localmente.
- Decisión: conservar el frontend del MVP como interfaz principal; no sustituirlo por la app independiente de Jaime. Reutilizar solo elementos que encajen con los contratos API existentes.

### Archivos y limpieza
- La comparación mostró archivos `__pycache__/*.pyc` y `.DS_Store` en la rama de Jaime: excluirlos de cualquier integración.
- Revisar los aparentes renombramientos que aparecen en el diff de GitHub antes de preparar cambios; no asumir que el detector de renombres representa la intención funcional.
- `requirements.txt` y `.env.example` difieren y deben conciliarse conscientemente.
- No atribuir automáticamente cambios nuevos a Jaime solo porque se trabaje sobre su código. Registrar autoría original y autoría de adaptación.

## 4. Estado de pruebas y calidad

- No hay evidencia disponible que certifique que la rama de Jaime pase pruebas integrales.
- Historial de pruebas local del MVP: 174 pruebas recogidas; 122 pasaron, 42 fallaron y 10 dieron error; 27 advertencias. Fallos conocidos incluían problemas de verificación SSL al descargar `sentence-transformers/all-MiniLM-L6-v2` y pruebas que esperaban HTTP 200 mientras el servicio LLM no configurado respondía 503.
- Esos resultados son históricos y no deben presentarse como estado actual sin volver a ejecutar pruebas.
- La presencia de pruebas no significa que estén aprobadas.
- Deben probarse el contrato frontend/API, carga y procedencia documental, recuperación RAG, generación y crítica, fallos del LLM, telemetría y recorrido de extremo a extremo.
- El contenido educativo debe ser verificable contra las fuentes. No presentar respuestas simuladas como generación real ni métricas ficticias como `anclaje_fuente_score: 0.98` o `status_upload: completado` sin medición real.

## 5. Corpus y Data Analytics

- La rama `data-analytics-corpus` contiene documentación de gobernanza y material de `data_analyst/` que no está todo en `main`; no se debe fusionar la rama completa indiscriminadamente.
- La revisión reportó 22 registros; 8 finalistas eran propuestas, no una aprobación final del equipo. El estado de evaluación debe verificarse contra los artefactos vigentes antes de publicar cifras como actuales.
- La decisión de alcance es mantener abierta la población objetivo y usar perfiles configurables. Data Analytics valida evidencia, calidad, pertinencia, metadatos, procedencia y licencias; no decide unilateralmente el contexto o la selección final del MVP.
- Incorporar selectivamente los artefactos de gobierno necesarios después de revisar diferencias y archivos compartidos. Verificar los recuentos y el estado de evaluación en los documentos originales antes de consolidar un número definitivo.
- El cargador actual del MVP tiene tres documentos APTO codificados y una ruta alternativa absoluta de Windows (`C:/PROYECTOS/G10_Nuevamente_Equipo48/_revision_corpus_fase05/documentos`); corregir portabilidad antes de depender de ella.

## 6. Plan de ejecución acordado

1. **Preflight de solo lectura:** comprobar rama, estado local, referencias remotas y baseline de `dev`; no modificar nada.
2. **Consolidar la especificación:** confirmar contratos y arquitectura existentes desde el código real.
3. **Integración selectiva:** adaptar el patrón escritor-crítico de Jaime al `AgentService`, conservando el RAG y frontend del MVP.
4. **Portabilidad y corpus:** corregir rutas absolutas y recuperar selectivamente los artefactos de gobernanza.
5. **Pruebas:** ejecutar por bloques, corregir y repetir; documentar fallos no resolubles por dependencias o red.
6. **PR:** cuando los cambios estén probados, preparar una rama de integración autorizada y PR a `dev`, previa comprobación de que `dev` contiene el baseline correcto.
7. **Validación final:** ejecutar la suite y los criterios de aceptación; solo después considerar promoción a `main`.

## 7. Reglas de operación con Antigravity

- Trabajar por objetivos, criterios de aceptación y ciclos autónomos; no pedir al usuario aprobación por cada archivo.
- Primera fase de cada tarea: lectura y diagnóstico. Mostrar rama, cambios existentes y archivos que pretende modificar.
- No crear ramas, hacer push, abrir PR, fusionar, borrar, resetear, limpiar el working tree ni reescribir historial sin autorización explícita.
- No sobrescribir cambios de terceros. No modificar la autoría histórica.
- Antigravity puede implementar, probar, corregir y repetir dentro del alcance aprobado.
- Detenerse si descubre un conflicto de arquitectura, una decisión de producto pendiente, cambios destructivos, secretos expuestos o una discrepancia entre `dev` y el baseline esperado.
- Entregar al terminar: archivos cambiados, motivo, comandos/pruebas ejecutados, resultados reales, fallos pendientes y siguiente acción.
- Actualizar `ESTADO_ACTUAL.md` al finalizar cada hito.

## 8. Próxima acción exacta

No volver a auditar el código de Jaime desde cero. Comenzar con una inspección de solo lectura del estado local y de las referencias `main`, `dev`, `feature/backend-agentes` e `integration/mvp-consolidado`, sin crear ni modificar ramas. Confirmar que el registro de esta auditoría coincide con el estado remoto actual. Después, proceder con la integración controlada, manteniendo el PR como pendiente hasta que haya cambios listos y probados.

## 9. Registro de cambios a este informe

Este documento es una consolidación operativa basada en la conversación y el contexto de proyecto disponible al 12-10-2026. Los estados de ramas, PR y pruebas son observaciones fechadas; se deben verificar solo cuando una operación posterior dependa de su vigencia. No reemplaza evidencia de ejecución ni autoriza por sí mismo operaciones de Git.
