# Documento Maestro — NuevaMente

## Identidad
- Nombre: NuevaMente — Sistema Inteligente de Adaptación y Generación de Contenido Educativo.
- Programa: Hackathon ONE / Oracle Next Education & Alura.
- Equipo: G10, Equipo 48.
- Repositorio: https://github.com/No-Country-simulation/G10_Nuevamente_Equipo48
- Ruta local: `C:\PROYECTOS\G10_Nuevamente_Equipo48`

## Objetivo
Construir un MVP que adapte o genere contenido educativo a partir de documentos curados, usando perfiles configurables y preservando trazabilidad de fuentes. La población objetivo se mantiene abierta; no asumir que el sistema es exclusivamente para niños o adolescentes.

## Arquitectura de referencia
1. Frontend: Streamlit, `frontend/app.py`.
2. API: FastAPI.
3. Coordinación de agentes y flujo de negocio: `AgentService`.
4. Modelo/LLM: `LLMService`.
5. Recuperación documental: `RAGService` con embeddings semánticos y FAISS.
6. Gestión documental: `DocumentService` y cargador de corpus.
7. Pruebas automatizadas: carpeta `backend/backend/tests/` y validaciones frontend/API.

No introducir servicios duplicados sin una decisión arquitectónica explícita.

## Principios
- Corpus documental, curado y con metadatos, procedencia y licencia.
- Respuestas rastreables a fuentes.
- Separar perfil del destinatario de nicho/contexto.
- Demostrar al menos dos perfiles y dos formatos, y tres escenarios de adaptación de un mismo documento, conforme a acuerdos previos.
- Manejar la ausencia del LLM como error explícito; no disfrazar respuestas simuladas como resultados reales.
- No inventar métricas de calidad ni estado de carga.
- Priorizar MVP funcional, integrado, probado, ejecutable por otra persona y documentado mínimamente.

## Perfiles y corpus
- Población abierta y perfiles configurables.
- Data Analytics verifica calidad, completitud, pertinencia, metadatos, procedencia y licencias.
- Data Analytics no decide unilateralmente la selección final ni el contexto del MVP.
- La matriz/inventario y los informes de `_revision_corpus_fase05/` son evidencia de gobierno; revisar la versión actual antes de publicar recuentos.
- El cargador del MVP solo contempla tres documentos APTO y debe dejar de depender de una ruta absoluta local.

## Contratos y responsabilidades
- Frontend solicita adaptación mediante API; no debe llamar directamente a nodos internos de agentes.
- API valida solicitudes y devuelve errores HTTP coherentes.
- `AgentService` coordina RAG y LLM.
- `RAGService` recupera fragmentos pertinentes y debe exponer fuentes usadas.
- La crítica de contenido debe evaluar fidelidad a las fuentes, no solo validez de JSON.
- Los metadatos y métricas deben derivarse de mediciones reales.

## Git y trazabilidad
- `main`: rama estable; no integrar sin validación.
- `dev`: rama de integración de PR individuales, según el flujo acordado.
- `feature/backend-agentes`: aportación original de Jaime.
- `data-analytics-corpus`: aportación de corpus y gobernanza.
- `integration/mvp-consolidado`: rama local de integración previamente acordada; no publicar ni recrear sin autorización.
- `5ef29fd9ac1529a631a2f8371fb03866c68147d8`: commit del MVP integrado ya publicado en `main`; no volver a proponerlo como PR.
- No reescribir historial, no descartar cambios de terceros y no inferir autoría a partir de una sola señal.

## Definition of Done
- Cambios dentro del alcance.
- Contratos frontend/API compatibles.
- Pruebas automatizadas ejecutadas y resultados registrados.
- Escenario completo reproducible.
- Fuentes y metadatos visibles.
- Errores de servicio controlados.
- Sin archivos generados o secretos accidentales.
- Documentación de configuración y ejecución actualizada.
- PR revisable, con procedencia y limitaciones descritas.
