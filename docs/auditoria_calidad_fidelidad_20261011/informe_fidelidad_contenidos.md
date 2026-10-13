# Informe de Fidelidad de Contenidos Educativos Generados — NuevaMente MVP

**Fecha de Auditoría:** 2026-10-11  
**Entorno de Ejecución:** FastAPI Backend v1.0.0 local en Windows con Google Gemini (`gemini-flash-latest`) y pipeline FAISS (`all-MiniLM-L6-v2`).  
**Documento Fuente Principal Auditado:** `NM-006` (*Manual de Ciberseguridad para Organizaciones de la Sociedad Civil* — NDI / Evan Summers).  

---

## 1. Casos Evaluados en Producción Local y Respuestas Reales

Se ejecutaron llamadas reales al endpoint `/api/v1/adaptacion` para contrastar el contenido devuelto contra los fragmentos fuente originales recuperados del índice FAISS.

### Caso TC-01: Tutorial para Principiantes
- **Documento:** `NM-006`
- **Parámetros:** `perfil: principiante`, `formato: tutorial`, `nicho: general`, `nivel: didactico`.
- **Fuentes RAG recuperadas:** 4 fragmentos (`chunk_id: afeefe25...`, `bb98dde3...`, `02431b52...`, `b4b5ffa1...`).
- **Puntuación de anclaje semántico automático:** `0.6248` (Nivel de confianza: `medio`).
- **Contenido generado:** Guía paso a paso sobre el "Kit de Inicio del Plan de Seguridad", inventario de cuentas y dispositivos, y activación de autenticación en dos factores (2FA).
- **Evaluación humana de fidelidad:**
  - **Fidelidad factual:** APROBADO. Los conceptos (riesgos de robo de credenciales, copias de seguridad desconectadas, uso de gestores de contraseñas) coinciden con el texto del manual.
  - **Inclusión de advertencias requeridas:** El modelo generó explícitamente: *"Este contenido tiene un carácter exclusivamente orientador y no vinculante..."*, reflejando el aviso legal presente en los primeros chunks de `NM-006`.
  - **Ausencia de información inventada:** APROBADO. No inventó herramientas inexistentes; recomienda las señaladas en el manual.
  - **Estado final:** `APROBADO`.

---

### Caso TC-02: Flashcards Técnicas para Líder Técnico
- **Documento:** `NM-006`
- **Parámetros:** `perfil: lider_tecnico`, `formato: flashcards`, `nicho: general`, `nivel: tecnico`.
- **Fuentes RAG recuperadas:** 1 fragmento (`chunk_id: e478260f...`, pos=104, score=0.2832).
- **Puntuación de anclaje semántico automático:** `0.6742` (Nivel de confianza: `medio`).
- **Contenido generado:** Formato JSON estructurado (lista de objetos `[{"pregunta": "...", "respuesta": "..."}]`).
- **Evaluación humana de fidelidad:**
  - **Fidelidad factual:** APROBADO. El fragmento fuente recuperado aborda ataques mediante extensiones del navegador y complementos maliciosos (caso "Componentes de actualización de Flash"). La flashcard generada sintetiza con exactitud ese vector de ataque técnico.
  - **Estructura y parseo:** APROBADO. El sistema validó y convirtió la respuesta a una lista nativa en Python sin fallos de esquema.
  - **Estado final:** `APROBADO`.

---

### Caso TC-03: Resumen Ejecutivo
- **Documento:** `NM-006`
- **Parámetros:** `perfil: ejecutivo`, `formato: resumen_ejecutivo`, `nicho: general`, `nivel: intermedio`.
- **Fuentes RAG recuperadas:** 5 fragmentos (`score: 0.33 - 0.38`).
- **Puntuación de anclaje semántico automático:** `0.6415` (Nivel de confianza: `medio`).
- **Contenido generado:** Síntesis orientada a toma de decisiones, dividida en: *Contexto de Riesgo*, *Impacto Operativo*, *Líneas de Acción Inmediatas* y *Políticas Organizacionales*.
- **Evaluación humana de fidelidad:**
  - **Fidelidad factual:** APROBADO. Resume con precisión que la capacitación continua reduce pero no elimina los incidentes, por lo que se requiere un protocolo formal de respuesta a incidentes.
  - **Adecuación al perfil:** APROBADO. Lenguaje ejecutivo sin perder el fundamento técnico de los fragmentos fuente.
  - **Estado final:** `APROBADO`.

---

## 2. Hallazgos sobre la Evaluación Automatizada de Calidad (`anclaje_fuente_score`)

1. **Rango de Calidad Observado:** En todas las generaciones exitosas, el `anclaje_fuente_score` se ubicó entre `0.61` y `0.67` (clasificado como `medio`).
2. **Interpretación:** No indica alucinación. Dado que el modelo traduce de un lenguaje técnico/normativo extenso hacia formatos pedagógicos didácticos o esquemáticos (flashcards, listas), la distancia en el espacio de embeddings es naturalmente mayor a una repetición textual literal.
3. **Observación crítica de auditoría:** El puntaje de similitud coseno es un indicador auxiliar útil pero **no sustituye la revisión de fidelidad factual**. En la auditoría humana se confirmó que la fidelidad fáctica es del 100% respecto a los fragmentos entregados.

---

## 3. Limitaciones Identificadas en Pruebas con Servicios Reales

- **Cuota de Tasa de Gemini (Error 429 / 502):** La clave gratuita de Gemini impone un límite de peticiones por minuto. Al disparar ráfagas consecutivas de generación, el backend activó sus 3 reintentos exponenciales y, al persistir el bloqueo, retornó controladamente HTTP 502 (`El servicio LLM está temporalmente saturado`).
- **Manejo en el MVP:** El backend no crasheó ni perdió estado en FAISS; manejó el fallo defensivamente mediante `LLMGenerationError`.
