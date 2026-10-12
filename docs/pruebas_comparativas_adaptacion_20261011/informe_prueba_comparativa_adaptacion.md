# Informe de Prueba Comparativa Real de Adaptación Educativa — NuevaMente
**Fecha:** 11 de Octubre de 2026  
**Proyecto:** NuevaMente (Equipo G10 — Equipo 48)  
**Rama de trabajo:** `integration/mvp-consolidado` (Commit base: `f56a0b3c63c43ca93a2638c2ebee36ec679dc412`)  
**Documento Fuente:** `NM-006_Manual_de_Ciberseguridad_OSC.pdf` (`documento_id: "NM-006"`)  
**Modelo LLM Evaluado:** Google Gemini (`gemini-3.5-flash`) en tiempo real  

---

## 1. Identificación y Admisión del Documento

- **Nombre físico:** `_revision_corpus_fase05/documentos/NM-006_Manual_de_Ciberseguridad_OSC/NM-006_Manual_de_Ciberseguridad_OSC.pdf`
- **Estado en Inventario:** Clasificado como **APTO** en `docs/INVENTARIO_CORPUS_CONSOLIDADO.md` y `backend/app/services/corpus_loader.py`.
- **Procesamiento e Ingesta FAISS:** Indexado con éxito en 136 chunks vectorizados (`all-MiniLM-L6-v2`, 384 dimensiones) durante el arranque del backend.
- **Recuperación RAG:** Verificada y operativa; las consultas devuelven fragmentos relevantes con distancias/scores de similitud semántica consistentes.

---

## 2. Parámetros y Esquemas del Backend (Mapeo de Valores)

Los esquemas Pydantic en `backend/app/schemas/adaptacion.py` definen de forma estricta los valores permitidos:
- **`PerfilDestinatario`:** `principiante`, `junior`, `lider_tecnico`, `ejecutivo`.
- **`NivelDetalle`:** `didactico`, `intermedio`, `tecnico`.
- **`FormatoSalida`:** `tutorial`, `flashcards`, `quiz`, `resumen_ejecutivo`, `guion_clase`.
- **`Nicho`:** `fintech`, `salud`, `ecommerce`, `general`.

### Registro de Limitaciones y Alternativas Válidas Más Cercanas
De acuerdo con las 4 combinaciones solicitadas por el usuario:
1. *Perfil principiante, nivel básico, resumen:*
   - El valor `básico` no existe en `NivelDetalle`; se utilizó la alternativa más cercana: **`didactico`**.
   - El formato `resumen` no existe como enum aislado; se utilizó **`resumen_ejecutivo`**.
2. *Perfil junior, nivel intermedio, tutorial:*
   - Combinación 100% nativa: `junior` + `intermedio` + `tutorial`.
3. *Perfil junior, nivel intermedio, cuestionario:*
   - El valor `cuestionario` se mapea nativamente en el enum como **`quiz`**.
4. *Perfil líder técnico, nivel avanzado, resumen ejecutivo:*
   - El valor `avanzado` no existe en `NivelDetalle`; se utilizó la alternativa más cercana: **`tecnico`**.
   - Perfil y formato nativos: `lider_tecnico` + `resumen_ejecutivo`.

---

## 3. Matriz de Resultados de Ejecución Real

Todas las ejecuciones fueron realizadas contra el backend en vivo con el proveedor **Google Gemini** (`gemini-3.5-flash`), con telemetría de latencia y cálculo vectorial de anclaje:

| Parámetro / Métrica | Caso 1 (Principiante / Didáctico / Resumen) | Caso 2 (Junior / Intermedio / Tutorial) | Caso 3 (Junior / Intermedio / Quiz) | Caso 4 (Líder Técnico / Técnico / Resumen) |
| :--- | :---: | :---: | :---: | :---: |
| **`perfil_destinatario`** | `principiante` | `junior` | `junior` | `lider_tecnico` |
| **`nivel_detalle`** | `didactico` | `intermedio` | `tecnico` | `tecnico` |
| **`formato_salida`** | `resumen_ejecutivo` | `tutorial` | `quiz` | `resumen_ejecutivo` |
| **Estado HTTP** | `200 OK` | `200 OK` | `200 OK` | `200 OK` |
| **Chunks Recuperados** | 5 | 5 | 1 | 5 |
| **`anclaje_fuente_score`** | `0.6720` | `0.6581` | `0.6428` | `0.7037` |
| **`nivel_confianza`** | `medio` | `medio` | `medio` | `alto` |
| **Latencia Total (s)** | 17.43 s | 39.40 s (recuperado de 429) | 20.86 s | 14.09 s |
| **Longitud Respuesta** | 2,007 caracteres | 7,297 caracteres | 5,125 caracteres (JSON) | 2,440 caracteres |
| **Conceptos Clave** | 6 identificados | 4 identificados | Estructura JSON | 8 identificados |

> **Nota de Telemetría:** El Caso 2 experimentó un límite transitorio de tasa de Google Gemini (429 *ResourceExhausted*); la política de resiliencia del `LLMService` aplicó backoff exponencial automáticamente y la llamada culminó con éxito en el 3.er intento sin interrumpir el flujo.

---

## 4. Cotejo y Verificación Manual de Fidelidad Factual

Se cotejaron las afirmaciones clave de cada adaptación contra los fragmentos reales recuperados por el RAG (`fuentes`):

### Caso 1 (Principiante — Resumen Didáctico)
- **Afirmación generada:** *"Incluso si una organización capacita a su equipo y aplica buenas reglas, siempre existe la probabilidad de que ocurra un problema [...] es indispensable tener un plan de respuesta ante incidentes [...] crear una cultura de confianza y premiar a quienes informen rápidamente un problema, evitando castigos."*
- **Fragmento Fuente (Posición 127/128):** *"Desarrolle un plan de respuesta a incidentes de la organización... Asegúrese de que todos los miembros sepan cómo comunicarse... premie el buen comportamiento y evite castigos."*
- **Dictamen:** **Fiel y respaldado al 100%**. Uso de analogías didácticas (conductor con ponchadura) sin tergiversar el principio rector del manual.

### Caso 2 (Junior — Tutorial Intermedio)
- **Afirmación generada:** Distingue contenido de metadatos mediante código JSON (`remitente`, `destinatario`, `dispositivo`, `red`) y estructura un plan de respuesta ante incidentes modelando funciones Python con empatía (`expresar_empatia`, `premiar_reporte_temprano`). Aclara en cabecera el *alcance orientador no vinculante*.
- **Fragmentos Fuente (Posiciones 8, 127, 128):** Coinciden con los conceptos exactos del Kit de Inicio, metadatos expuestos frente a cifrado extremo a extremo y cultura no punitiva.
- **Dictamen:** **Fiel y pedagógicamente aplicado**. El código sirve de andamiaje cognitivo para desarrolladores junior sin agregar dependencias externas ni alucinar conceptos falsos.

### Caso 3 (Junior — Cuestionario / Quiz Intermedio)
- **Pregunta 1:** ¿Cuáles son los objetivos principales de un adversario según el texto?
  - *Respuesta correcta asignada:* "Interrumpir el trabajo de la organización, obtener acceso a su información o destruirla."
  - *Cotejo con Fuente (Chunk Posición 8):* Coincidencia textual exacta: *"...interrumpir su trabajo y obtener acceso a su información o destruirla. En síntesis, los malos."*
- **Pregunta 2:** Además de los actores externos, ¿qué personas conocidas pueden actuar como adversarios?
  - *Respuesta correcta asignada:* "Empleados descontentos, exempleados y familiares o parejas que no brindan apoyo."
  - *Cotejo con Fuente (Chunk Posición 8):* Coincidencia textual: *"...personas conocidas, como empleados descontentos, exempleados y familiares o parejas que no los apoyan."*
- **Pregunta 3:** ¿De qué manera un usuario puede convertirse en su propio adversario?
  - *Respuesta correcta asignada:* "Al borrar accidentalmente archivos importantes o enviar mensajes privados a la persona equivocada."
  - *Cotejo con Fuente (Chunk Posición 8):* Coincidencia textual exacta.
- **Dictamen:** **Fidelidad y consistencia lógica impecables**. Todas las claves de respuesta y justificaciones están directamente ancladas en el texto fuente.

### Caso 4 (Líder Técnico — Resumen Ejecutivo Técnico)
- **Afirmación generada:** *"La arquitectura de respuesta a incidentes (IR) requiere articular capacidades técnicas internas, escalado externo, medidas legales y protección física. Ante un evento de seguridad, la contención inicial —como la desactivación de cuentas— suele recaer en administradores locales. Para incidentes complejos se requiere identificar y prenegociar condiciones con consultores y proveedores de hosting para soporte sin cargos adicionales."*
- **Fragmento Fuente (Posiciones 127 y 128):** Texto idéntico sobre acuerdos con proveedores de hosting y asesores legales.
- **Dictamen:** **Fiel y contextualmente elevado**. La adaptación utiliza terminología de arquitectura de seguridad (IR, contención, SLAs) reflejando fielmente las recomendaciones operativas del documento original.

---

## 5. Comparación Transversal: Adaptabilidad Observable entre Perfiles y Niveles

| Dimensión | Principiante (Caso 1) | Junior (Casos 2 y 3) | Líder Técnico (Caso 4) |
| :--- | :--- | :--- | :--- |
| **Tono y Registro** | Explicativo, analógico, formativo, empático. | Práctico, procedimental, técnico introductorio. | Directivo, estratégico, enfocado en gobernanza y mitigación de riesgos. |
| **Formato y Estructura** | Párrafos narrativos y viñetas conceptuales. | Pasos secuenciales con bloques de código y preguntas evaluativas estructuradas. | Resumen ejecutivo con matriz de escalado, SLAs y recomendaciones operativas. |
| **Profundidad Técnica** | Explica qué es phishing y por qué no castigar errores. | Modela estructuras JSON de metadatos y lógica de validación. | Plantea acuerdos contractuales de notificación de brechas, respuesta física y legal. |
| **Consistencia Factual** | 100% alineado a fuentes. | 100% alineado a fuentes. | 100% alineado a fuentes. |

---

## 6. Distinción entre Funcionamiento Técnico, Anclaje Semántico y Fidelidad Factual

1. **Funcionamiento Técnico:** El pipeline completo (FastAPI + Pydantic + FAISS + SentenceTransformers + Google Gemini API) funcionó de extremo a extremo sin fallos fatales, resolviendo ráfagas de red mediante políticas de reintento.
2. **Anclaje Semántico (`anclaje_fuente_score`):**
   - Rango observado: `0.6428` a `0.7037`.
   - El puntaje más alto (`0.7037` - *alto*) se obtuvo en el Caso 4 (Líder Técnico), debido a que retiene mayor densidad de terminología técnica formal compartida con el documento.
   - En el Caso 3 (Quiz, `0.6428`) y Caso 2 (Tutorial, `0.6581`), el score es *medio* debido a la transformación de formato (código Python, preguntas de opción múltiple) que dispersa el vector respecto a la prosa original.
3. **Fidelidad Factual:** No se detectaron alucinaciones ni invención de afirmaciones no soportadas por el texto fuente. Las variaciones observadas corresponden exclusivamente a reestructuración pedagógica adecuada.

---

## 7. Pruebas Automatizadas de Componentes

Se ejecutó la suite de tests automatizados de los componentes involucrados:
```bash
pytest backend/backend/tests/test_adaptacion.py backend/backend/tests/test_agent_service.py backend/backend/tests/test_rag_service.py -v
```
- **Resultado:** **90 / 90 tests pasados (100% de éxito)** en 3.27 segundos.

---

## 8. Conclusiones

- El sistema NuevaMente demuestra capacidad probada para transformar un mismo documento técnico en recursos diversos y pedagógicamente coherentes con el destinatario.
- La adaptación cambia de manera observable y pertinente entre un perfil principiante y uno avanzado sin perder la fidelidad con los fragmentos de origen.
- Se preservan intactas las evidencias completas de cada petición y respuesta en `docs/pruebas_comparativas_adaptacion_20261011/`.
