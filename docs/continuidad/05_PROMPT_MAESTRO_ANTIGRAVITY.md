# Prompt maestro para Google Antigravity — NuevaMente

Trabaja en `C:\PROYECTOS\G10_Nuevamente_Equipo48`.

Antes de actuar, lee los documentos de continuidad de esta carpeta:
- `00_INFORME_EJECUTIVO.md`
- `01_DOCUMENTO_MAESTRO.md`
- `02_AUDITORIA_JAIME_Y_DECISIONES.md`
- `03_ESTADO_Y_PROXIMOS_PASOS.md`
- `04_GUIA_OPERATIVA_ANTIGRAVITY.md`

## Contexto obligatorio
La auditoría de `feature/backend-agentes` ya fue realizada. No la repitas desde cero. Sus conclusiones son: conservar el frontend integrado del MVP, conservar el RAG semántico con embeddings/FAISS, y adaptar selectivamente el patrón escritor-crítico de Jaime al `AgentService` existente. Excluir `__pycache__`, `.pyc` y `.DS_Store`. La crítica debe evaluar fidelidad a las fuentes, no solo JSON válido.

El commit `5ef29fd9ac1529a631a2f8371fb03866c68147d8` del MVP ya está publicado en `main`; no se debe reintroducir como PR. El flujo acordado es que los PR individuales se dirijan a `dev`, pero primero confirma que `dev` contiene el baseline del MVP integrado. Si no, detente y presenta opciones; no modifiques ramas para arreglarlo por iniciativa propia.

## Tarea inicial
Solo auditoría de estado, sin cambios:
1. `git status --short --branch`
2. inspeccionar ramas locales y remotas;
3. verificar los HEAD de `main`, `dev`, `feature/backend-agentes`, `data-analytics-corpus`;
4. comprobar si existe `integration/mvp-consolidado` local/remota sin recrearla;
5. identificar cambios locales y no asumir que se pueden descartar;
6. comparar el estado actual con los documentos de continuidad.

No ejecutar cambios de archivos, crear ramas, commits, push, PR, merge, rebase, reset, clean ni operaciones de stash.

## Entregable
Devuelve un informe breve:
- estado local;
- referencias/HEAD comprobados;
- discrepancias frente al registro;
- si `dev` tiene el baseline adecuado;
- próximo paso recomendado;
- cualquier bloqueo.

Espera autorización antes de modificar archivos o ejecutar operaciones remotas. Una vez aprobado un bloque, puedes trabajar de forma autónoma dentro del alcance, ejecutar pruebas, corregir y repetir. Al finalizar, informa archivos cambiados, pruebas y resultados reales, fallos pendientes y actualiza el estado del proyecto.
