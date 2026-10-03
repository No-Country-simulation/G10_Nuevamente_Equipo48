> **HISTÓRICO — SUPERSEDIDO.** Este informe corresponde a rev5. Para el estado vigente utilizar `auditoria_integral_fase05_rev6.md` y `estado_consolidacion.md`.

# NuevaMente — Auditoría integral del corpus (Fase 05 rev5; HISTÓRICO)

> **SUPERSEDIDO POR REV6.** Este archivo conserva el corte de auditoría anterior (12 APTO, 8 APTO_CON_REVISIÓN, 2 NO_APTO). El estado vigente está en `auditoria_integral_fase05_rev6.md`.

**Fecha de consulta:** 2026-10-02\
**Base auditada:** `Data_Analyst_Consolidado_Fase05_rev5.zip`\
**Alcance:** 22 registros, matriz maestra, inventario CSV, criterios
C01--C08, hoja de finalistas, fuentes oficiales y repositorios
enlazados.

## 1. Resultado ejecutivo

La auditoría externa de las 22 referencias permitió corregir fuentes
genéricas o secundarias, precisar licencias y formatos, y separar los
documentos utilizables de aquellos que requieren condiciones
documentales concretas.

  Resultado auditado     Registros
  -------------------- -----------
  APTO                          12
  APTO_CON_REVISIÓN              8
  NO_APTO                        2
  **Total**                 **22**

La selección definitiva del MVP no se ha realizado. Los registros
mantienen `EN_EVALUACION` en el inventario. La hoja
`Finalistas propuestos` sigue siendo una propuesta y no una decisión del
equipo.

## 2. Principales correcciones consolidadas

-   **NM-003:** se reemplazó la URL del artículo de anuncio por el libro
    publicado en Runestone. Se incorporó la versión 0.1.2 y la licencia
    CC BY-SA 4.0.
-   **NM-004:** se sustituyó la portada genérica de la Universidad del
    Azuay por la ficha editorial específica; se confirmaron autor,
    fecha, 325 páginas, PDF y CC BY-NC 4.0.
-   **NM-007:** se cambió a `APTO_CON_REVISIÓN`. La fuente CATEDU
    presenta licencias distintas por capítulos: CC BY-SA 4.0 para
    secciones de Federico Coca y CC BY-NC-SA 4.0 para secciones de
    Javier Quintana Peiró. El contenido es dinámico y la exportación se
    ofrece por capítulo; el total de 368 páginas no quedó respaldado por
    la fuente primaria.
-   **NM-008:** se delimitó el registro al Volumen 1 (ISBN
    978-84-10368-22-4). Existe una segunda parte con ISBN diferente; no
    debe mezclarse bajo el mismo registro. Se retiró el número de 282
    páginas por falta de corroboración primaria.
-   **NM-011:** se cambió a `APTO_CON_REVISIÓN` porque la evidencia
    localizada para autores, licencia y páginas proviene de OpenLibro;
    falta cotejo con el PDF y/o una ficha primaria de Religación Press.
-   **NM-014:** se completó el año 2022 y se confirmó el PDF completo y
    la licencia CC BY-NC-SA 4.0 en SEDICI.
-   **NM-015:** se cerró la revisión de formato al identificar el PDF
    oficial directo de 85 páginas, con ISBN y licencia CC BY-NC-SA 4.0.
    Resultado actualizado a `APTO`.
-   **NM-017:** se corrigió la versión a v0p4 Complete Edition, marzo de
    2026, 20 capítulos, 6 apéndices y 18 laboratorios. Sigue en revisión
    por necesidad de fijar commit/snapshot.
-   **NM-020:** se aclaró que la página oficial declara CC BY-NC-SA 4.0
    para la traducción española. La revisión pendiente se concentra en
    fijar versión exacta porque `latest` es mutable.
-   **NM-021:** se conserva `NO_APTO`: la fuente está bajo CC BY-NC-ND
    4.0 y no permite distribuir adaptaciones; además, el repositorio
    indica que no hay PDF libre distribuible.
-   **NM-022:** se conserva `NO_APTO`: OpenStax prohíbe entrenamiento o
    ingestión en LLM/IA generativa sin permiso previo escrito.

## 3. Estado por documento

| ID \| Resultado \| Conclusión de auditoría \|
| NM-001 \| APTO \| Identificación y licencia corroboradas en el PDF
  institucional. El registro mantiene un PDF concreto; la página exacta
  debe conservarse como referencia. \|
| NM-002 \| APTO \| La licencia que debe regir el uso de la traducción
  es la declarada para esa versión española; no debe sustituirse por la
  licencia de otra edición/idioma sin comprobar el aviso aplicable. \|
| NM-003 \| APTO \| La URL de Fase 05 apuntaba a un artículo de anuncio,
  no al libro publicado. Se sustituye por la obra publicada. El
  repositorio de fuentes debe quedar fijado a un commit si se requiere
  reproducibilidad. \|
| NM-004 \| APTO \| La URL anterior era la portada institucional
  genérica. Se reemplaza por la ficha bibliográfica y de descarga
  específica. \|
| NM-005 \| APTO \| Edición y licencia están identificadas en el
  repositorio oficial. No se incorpora un número de páginas no
  corroborado en la fuente revisada. \|
| NM-006 \| APTO \| Fuente institucional y versión española verificadas.
  La ficha del editor identifica al NDI como publisher; se conserva Evan
  Summers como autor consignado en la documentación previa, sujeto al
  cotejo de créditos del PDF. \|
| NM-007 \| APTO_CON_REVISIÓN \| La licencia global CC BY-NC-SA 4.0 y el
  conteo de 368 páginas no describen de forma suficiente el contenido
  actual. El libro es compuesto y tiene licencias diferentes por
  secciones; además el contenido es dinámico y la exportación se muestra
  por capítulo. \|
| NM-008 \| APTO \| El registro debe delimitarse al Volumen 1; la
  segunda parte es una obra/registro distinto. Se elimina el dato de 282
  páginas por no quedar corroborado en la fuente primaria consultada. \|
| NM-009 \| APTO \| La fuente oficial directa del PDF y la licencia
  están identificadas. El número de páginas proviene de una ficha
  secundaria y debe tratarse como dato bibliográfico auxiliar. \|
| NM-010 \| APTO \| La URL es correcta como fuente del autor, pero el
  contenido se actualiza y la versión no queda congelada en la URL. 639
  páginas corresponden a la referencia 2020. \|
| NM-011 \| APTO_CON_REVISIÓN \| La ficha secundaria es detallada, pero
  no basta para cerrar procedencia/licencia bajo C01/C07. No se debe
  tratar como evidencia editorial primaria. \|
| NM-012 \| APTO_CON_REVISIÓN \| La fuente y la licencia general están
  identificadas, pero la obra es un libro interactivo con elementos
  excluidos y la ficha editorial no ofrece paquete descargable. La
  versión del repositorio debe fijarse y las figuras 9, 12 y 31 deben
  excluirse o licenciarse por separado. \|
| NM-013 \| APTO_CON_REVISIÓN \| La obra está disponible en formatos
  admitidos, pero la licencia incluye excepciones explícitas para
  materiales donde se indique otra cosa. Deben revisarse créditos de
  imágenes, H5P y materiales externos antes de ingerir/adaptar el
  conjunto completo. \|
| NM-014 \| APTO \| La ficha anterior no consignaba año; se completa con
  2022. La fuente confirma que es un libro completo con nueve capítulos
  y PDF íntegro. \|
| NM-015 \| APTO \| La revisión pendiente anterior se originaba en no
  haber fijado el PDF. La auditoría identificó el PDF oficial concreto y
  verificó 85 páginas; el requisito de archivo admitido queda resuelto a
  nivel de fuente. \|
| NM-016 \| APTO \| Fuente y formato compatibles identificados. La
  audiencia declarada en la ficha es Bachillerato/Universidad (16+). \|
| NM-017 \| APTO_CON_REVISIÓN \| La versión/fecha consignadas en Fase 05
  (diciembre 2025) estaban desactualizadas. El repositorio presenta una
  edición v0p4 de marzo 2026; debe fijarse el commit exacto y comprobar
  que el snapshot incluye todos los archivos vinculados a los
  laboratorios. \|
| NM-018 \| APTO_CON_REVISIÓN \| La ficha anterior coincide con versión
  y estructura. La naturaleza de borrador y la sincronización desde un
  repositorio privado hacen necesario fijar un commit/snapshot. \|
| NM-019 \| APTO_CON_REVISIÓN \| La fecha y estructura consignadas en
  Fase 05 se confirman. No se declara un número de versión y no se fijó
  el commit de los archivos del corpus. \|
| NM-020 \| APTO_CON_REVISIÓN \| La licencia de la traducción española
  queda aclarada por la declaración de la propia página; no debe
  confundirse con la licencia de otra versión/idioma. La URL latest es
  mutable y no fija el snapshot exacto. \|
| NM-021 \| NO_APTO \| La condición ND impide distribuir adaptaciones y
  el PDF compilado no se puede publicar libremente. La fuente LaTeX no
  figura entre los formatos de entrada admitidos por el MVP. \|
| NM-022 \| NO_APTO \| La condición no es una inferencia de la licencia
  Creative Commons: es una condición adicional expresamente declarada
  por OpenStax. Impide el uso previsto de NuevaMente sin autorización
  escrita. \|

## 4. Criterios de aceptación C01--C08

Se agregó a la matriz la hoja **`Auditoría integral`**, con una fila por
documento y trazabilidad de los ocho criterios.

-   **C01 Identificación:** se corroboró la identificación de las
    fuentes y la ubicación documental en los enlaces consultados.
-   **C02 Calidad:** se consultaron estructura, descripción, índice y
    contenido visible. Esto no equivale a una revisión técnica línea por
    línea de cada página.
-   **C03 Integridad:** se distingue entre PDF completo disponible,
    libro web/repositorio con snapshot pendiente y formato no admitido.
-   **C04 Pertinencia:** se confirmó la correspondencia temática con
    dominios técnicos/científicos del proyecto.
-   **C05 Potencial pedagógico:** se conserva el análisis de la matriz;
    deberá contrastarse con el snapshot exacto que se use.
-   **C06 Adaptación:** se conserva el potencial por formato registrado;
    no sustituye la prueba del MVP exigida por el hackathon.
-   **C07 Procedencia/licencia:** se registran licencias y condiciones
    especiales; los casos con excepciones permanecen en revisión.
-   **C08 Adecuación:** la evaluación NNA se mantiene separada del
    resultado general.

## 5. Pendientes de control que no impiden entregar esta versión candidata

1.  **Preservación de snapshots:** para libros web/repositorios mutables
    (NM-003, NM-007, NM-010, NM-012, NM-017, NM-018, NM-019 y NM-020),
    registrar fecha, versión y SHA/archivo exacto que el equipo decida
    incorporar.
2.  **Licencias por componente:** NM-007, NM-012 y NM-013 requieren
    aplicar la licencia por capítulo/figura/material cuando existan
    excepciones.
3.  **Cotejo de fuente primaria:** NM-011 requiere cotejo de licencia,
    autoría y versión contra el PDF/editorial.
4.  **Materiales externos:** revisar figuras, imágenes, H5P, enlaces y
    recursos de terceros en NM-008 y NM-013 antes de incorporarlos.
5.  **Hash de archivo final:** al materializar los archivos para el
    corpus, registrar SHA-256, tamaño, fecha de descarga y URL de
    origen. Este control es distinto de verificar que la fuente publique
    un documento completo.
6.  **Validación técnica:** ejecutar el validador desde la copia de
    trabajo y comprobar coherencia matriz/inventario tras la edición.

Estos controles están identificados como condiciones específicas, no
como solicitudes de nuevas micro-revisiones. Deben cerrarse de manera
conjunta cuando el equipo congele los archivos de entrada.

## 6. Decisiones que permanecen en manos del equipo

-   La selección definitiva del corpus del MVP.
-   La selección final entre contextos de Capacitación
    Corporativa/Upskilling y EdTech Académico.
-   Los perfiles y formatos concretos de la demostración.
-   La autorización para integrar cambios en GitHub o en `main`.

Data Analytics entrega evidencia y evaluación; no decide unilateralmente
la selección final.

## 7. Artefactos actualizados

-   `matriz/Matriz_Corpus_NuevaMente_Consolidada_v2_Poblacion.xlsx` ---
    matriz actualizada y nueva hoja `Auditoría integral`.
-   `inventario/inventario_corpus.csv` --- inventario reconciliado con
    los resultados auditados.
-   `reportes/registro_evidencias_fuentes.csv` --- registro de URL,
    evidencia, hallazgos y acciones por documento.
-   `reportes/auditoria_integral_fase05_rev5.md` --- este informe.
-   `reportes/validacion_integral_fase05.txt` --- resultado de
    validación técnica y reconciliación.

## 8. Referencias oficiales consultadas

Las URL principales están en el inventario y el registro de evidencias.
Entre las fuentes consultadas se incluyen:

-   idUS Universidad de Sevilla ---
    https://idus.us.es/bitstreams/cae782ff-8e0f-4ee2-a493-bf0c46782c5b/download
-   Runestone Academy ---
    https://runestone.academy/ns/books/published/practical_db/index.html
-   Universidad del Azuay Casa Editora ---
    https://publicaciones.uazuay.edu.ec/index.php/ceuazuay/catalog/book/5
-   NDI ---
    https://ndi.org/publications/cybersecurity-handbook-civil-society-organizations
-   CATEDU --- https://libros.catedu.es/books/esp32-en-el-aula
-   RED Descartes ---
    https://proyectodescartes.org/descartescms/otras-areas/ingenieria-y-tecnologia/item/4644-electronica-digital-ejemplos-y-ejercicios
-   TU Delft OPEN ---
    https://books.open.tudelft.nl/home/catalog/book/192
-   MavMatrix / UTA --- https://mavmatrix.uta.edu/oer_mavsopenpress/20/
-   SEDICI / UNLP --- https://sedici.unlp.edu.ar/handle/10915/149970
-   RED Descartes PDF ---
    https://proyectodescartes.org/iCartesiLibri/PDF/Como_funciona_la_energia.pdf
-   OpenStax ---
    https://openstax.org/books/college-physics-2e/pages/preface

------------------------------------------------------------------------

**Estado de entrega:** versión candidata consolidada de Fase 05 rev5. No
se ha modificado `Data_Analyst` original, GitHub ni la rama `main`.
