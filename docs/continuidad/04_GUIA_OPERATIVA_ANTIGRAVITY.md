# Guía operativa — Google Antigravity para NuevaMente

## Objetivo
Delegar a Antigravity la mayor parte de la ejecución técnica local, trabajando por objetivos y criterios de aceptación en lugar de instrucciones manuales archivo por archivo.

## Modo de operación
### Fase 1 — Preflight de solo lectura
- Leer `00_INFORME_EJECUTIVO.md`, `01_DOCUMENTO_MAESTRO.md`, `02_AUDITORIA_JAIME_Y_DECISIONES.md` y `03_ESTADO_Y_PROXIMOS_PASOS.md`.
- Inspeccionar rama actual, cambios locales, referencias y estructura.
- Informar qué está confirmado, qué difiere de los documentos y qué archivos planea tocar.
- No modificar archivos ni ejecutar operaciones remotas.

### Fase 2 — Plan acotado
Proponer una tarea con:
- objetivo;
- archivos previstos;
- archivos que no se deben tocar;
- pruebas;
- criterios de aceptación;
- riesgos y reversibilidad.

### Fase 3 — Ejecución autónoma autorizada
Una vez aprobado el alcance, Antigravity puede implementar, ejecutar pruebas, corregir errores relacionados y repetirlas sin pedir permiso para cada cambio de archivo.

### Fase 4 — Informe de cierre
Entregar:
1. resumen;
2. archivos modificados y razón;
3. comandos/pruebas ejecutados;
4. resultados reales y evidencia;
5. problemas no resueltos;
6. siguiente paso;
7. actualización propuesta para `03_ESTADO_Y_PROXIMOS_PASOS.md`.

## Límites obligatorios
Sin autorización explícita, no:
- crear/eliminar ramas;
- hacer `push`;
- abrir, actualizar o fusionar PR;
- hacer merge/rebase;
- ejecutar `reset --hard`, `clean -fd`, `checkout` que sobrescriba cambios, `stash pop` o equivalente destructivo;
- borrar cambios de compañeros;
- reescribir historial;
- cambiar arquitectura o contratos;
- cambiar la selección final del corpus;
- subir secretos o datos sensibles.

Detenerse y consultar si:
- hay cambios locales inesperados;
- `dev` no contiene el baseline necesario;
- aparecen conflictos de autoría o integración;
- una corrección requiere cambiar arquitectura/alcance;
- se exponen credenciales;
- las pruebas no pueden ejecutarse por red/SSL/dependencias.

## Decisiones ya cerradas
- Mantener un frontend Streamlit integrado, una API FastAPI, `AgentService` y `RAGService`.
- Mantener el RAG semántico del MVP como motor principal.
- Adaptar selectivamente el patrón escritor-crítico de Jaime.
- No sustituir el frontend integrado por la UI independiente de Jaime.
- No integrar `__pycache__` ni `.DS_Store`.
- No volver a auditar desde cero si no hay cambios nuevos.
- `5ef29fd` ya está en `main`; no crear un PR para reintroducirlo.
- PR individuales se dirigen a `dev`, previa comprobación de que `dev` tiene el baseline correcto.
