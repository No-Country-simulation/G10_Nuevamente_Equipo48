# Auditoría de integración — Jaime vs MVP integrado

**Estado:** auditoría ya realizada; este documento conserva sus conclusiones. No repetirla salvo cambios nuevos o discrepancias verificables.

## Componentes del MVP integrado
- `frontend/app.py`: interfaz Streamlit integrada con API; carga archivos, llama a adaptación, presenta metadatos, métricas y fragmentos fuente, muestra estado de servicio y permite descarga JSON.
- FastAPI con endpoint de adaptación.
- `AgentService`, `LLMService`, `RAGService`, `DocumentService`.
- RAG semántico con Sentence Transformers y FAISS.
- Suite de pruebas en `backend/backend/tests/`.

## Aporte de Jaime
- `agents/graph.py`: grafo LangGraph escritor → crítico → reintento condicional.
- `agents/nodes.py`: writer/critic con ChatGroq, configuración Qwen indicada en el código.
- `agents/state.py`, `agents/schemas.py`.
- `rag_core/rag.py`: recuperación léxica con `Counter` y similitud coseno.
- `run_pipeline.py`: pipeline CLI; trunca el documento a 12.000 caracteres.
- `app.py`: UI Streamlit independiente que invoca nodos directamente en lugar de usar el grafo.
- Hay archivos generados `__pycache__` y `.DS_Store` que deben excluirse.

## Evaluación
### A conservar
- El concepto escritor-crítico y el grafo condicional como patrón de orquestación, si se adapta a los contratos actuales.
- Esquemas/estado que resuelvan necesidades reales y puedan integrarse sin duplicar componentes.
- Pruebas o documentación funcional que pueda atribuirse con certeza a su autor.

### A no incorporar literalmente
- Un segundo RAG independiente como reemplazo del RAG semántico del MVP.
- La interfaz de Jaime como sustituto de `frontend/app.py`.
- Validación de crítico limitada a parseo JSON, estado no-error y presencia de `contenido_adaptado`.
- Archivos `.pyc`, `__pycache__`, `.DS_Store`.
- Configuración de dependencias sin conciliación con el entorno integrado.
- Suposiciones de que una interfaz o pipeline funciona solo porque el código existe.

## Decisión final
Adaptar el patrón escritor-crítico al `AgentService` existente, con comprobaciones de fidelidad a las fuentes y errores explícitos. Mantener el frontend y el RAG semántico del MVP. Preservar autoría e historial. No fusionar la rama completa de Jaime directamente.

## Git / PR
La comparación remota registrada en la conversación mostró `feature/backend-agentes` con dos commits propios y tres commits detrás de `main`, con divergencia respecto a la base común `12045d12943e5d1f9ad80dd1f8c9783dd19f47b1`. La consulta de PR no encontró PR registrados en ese momento. Antes de abrir el PR, verificar si `dev` contiene el baseline integrado esperado. El flujo acordado es PR hacia `dev`, no directamente a `main`, salvo que el usuario cambie expresamente la política.
