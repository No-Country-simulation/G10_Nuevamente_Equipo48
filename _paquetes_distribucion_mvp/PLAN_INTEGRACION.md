# Plan de integración de PRs hacia `dev`

## Orden recomendado

1. **Alexis — corpus/RAG.** Aplicar `nuevo-corpus-loader.patch` y `precarga-corpus-y-rag.patch`. Confirmar de forma independiente los tres documentos APTO; no subir binarios sin autorización y procedencia.
2. **Mariana — API y esquemas.** Aplicar `backend-api-contract.patch` para fijar el contrato defensivo de la respuesta.
3. **Jaime — agentes y orquestación.** Aplicar `agentes-orquestacion.patch`; consume y completa los metadatos del contrato.
4. **Mónica — Streamlit/API.** Aplicar `frontend-streamlit-api.patch` una vez estabilizados endpoint y respuesta.
5. **Dayanara — QA.** Aplicar sus tres parches de pruebas solamente cuando los cuatro PRs funcionales estén integrados o presentes en la rama de prueba.

Los PRs 1 y 2 pueden revisarse en paralelo, pero no fusionar UI o QA antes de sus dependencias. Cada PR debe salir de un `dev` actualizado y contener exclusivamente los archivos de su paquete.

## Criterios de aceptación de coordinación

- Un revisor comprueba que cada parche aplica contra el `dev` vigente sin incluir `.env`, bytecode, cachés, entornos, archivos PDF, hojas de cálculo u otros binarios.
- El responsable confirma el origen de los cambios locales que no tienen commit antes de presentarlos como propios.
- QA conserva evidencia de su propia ejecución posterior; los informes locales preexistentes solo son antecedentes.
- La integración confirma el comportamiento por código y revisión/ejecución posterior autorizada; no se considera implementado por la sola presencia de archivos.

## Pendientes de decisión

- Aprobar la distribución de los materiales físicos de corpus y su licencia/procedencia.
- Resolver si la ruta absoluta de `corpus_loader.py` se acepta temporalmente o se sustituye antes del PR.
- Confirmar quién originó cada diff local y quién es propietario de las evidencias existentes.
