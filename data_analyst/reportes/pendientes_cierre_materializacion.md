# Controles pendientes antes de declarar el corpus materializado

## Alcance

La auditoría documental está consolidada a nivel de 22 registros. Los archivos originales aún no se han descargado. El control `control_materializacion_fuentes.csv` mantiene los 22 registros en `PENDIENTE_DESCARGA`; esta condición corresponde al estado acordado de la fase y no altera la evaluación documental.

## Control obligatorio para cada documento que el equipo seleccione

1. Descargar o recuperar el documento original desde la URL y versión registradas.
2. Confirmar que el archivo corresponde al documento y versión evaluados.
3. Comprobar apertura, integridad y completitud.
4. Registrar nombre/ruta, formato, tamaño, fecha de descarga y SHA-256.
5. Conservar atribución, licencia y exclusiones aplicables.
6. Actualizar `control_materializacion_fuentes.csv` y la evidencia asociada.

## Restricciones que no deben perderse

- **NM-007:** seleccionar capítulos concretos; licencias CC BY-SA 4.0 y CC BY-NC-SA 4.0 varían por autor/sección; revisar terceros.
- **NM-012:** snapshot fijado; excluir figuras 2.2, 2.5 y 5.12.
- **NM-013:** limitar al texto de capítulos cubierto por CC BY 4.0; excluir materiales de terceros, visuales e interactivos fuera del alcance.
- **NM-018:** mantener la etiqueta `Draft v0p4`.
- **NM-020:** usar versión 0.1 fijada; licencia de traducción CC BY-NC-SA 4.0; verificar condición NoComercial y CompartirIgual para el uso y las adaptaciones previstas.
- **NM-021 y NM-022:** permanecen NO_APTO para el uso previsto mientras no cambien las autorizaciones/condiciones documentadas.

La selección de documentos y el contexto de aplicación siguen siendo decisiones del equipo.
