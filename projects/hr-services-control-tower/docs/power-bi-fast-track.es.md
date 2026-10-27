# Abrir y actualizar el reporte

[← Caso principal](../README.md) · [English](power-bi-fast-track.en.md)

Puedes revisar las capturas desde GitHub o descargar el archivo para explorar el reporte en Power BI Desktop. El PBIX publicado incluye los datos importados del escenario sintético.

## Revisar las capturas

[Vista ejecutiva](../assets/screenshots/executive-overview.png) · [SLA y backlog](../assets/screenshots/sla-backlog-analysis.png) · [Capacidad](../assets/screenshots/operational-drivers.png) · [Proceso y satisfacción](../assets/screenshots/process-experience.png)

## Abrir el PBIX

1. [Descarga el archivo](../power-bi/Project-1-HR-Services-Control-Tower.pbix?raw=true).
2. Ábrelo en una versión reciente de Power BI Desktop para Windows.
3. Explora las cuatro páginas y sus filtros con los datos guardados. No hace falta actualizar los datos para revisar esa versión del reporte.

[Instalar Power BI Desktop](https://learn.microsoft.com/power-bi/fundamentals/desktop-get-the-desktop)

El archivo es una copia del reporte completo con su modelo y datos sintéticos, no un enlace que dependa del acceso al reporte de la cuenta universitaria.

## Recargar los datos en otro equipo

Las consultas del PBIX utilizan rutas locales a trece CSV. Para recargarlos:

1. Descarga el repositorio y conserva la carpeta data/processed del proyecto.
2. En Power BI Desktop, cambia los orígenes de datos de cada CSV por sus ubicaciones en tu equipo. También puedes revisar las rutas desde Power Query.
3. Mantén los tipos y la configuración regional de las consultas; los CSV utilizan punto como separador decimal.
4. Actualiza el modelo y comprueba los valores de referencia del diccionario de métricas.

La versión publicada utiliza data/processed, no data/raw. Las rutas están definidas individualmente en las consultas del PBIX.

Si quieres regenerar el escenario, consulta la [guía del generador](generator-guide.es.md). Cambiar la semilla o el número de casos produce otro escenario y los valores de referencia pueden dejar de coincidir.

## Consultar la implementación

[Metodología y modelo](technical-overview.md) · [Métricas y filtros](metric-dictionary.md) · [Medidas DAX](../power-bi/measures-reference.dax)
