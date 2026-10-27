# Actualizar los datos del reporte

[← Volver al caso](../README.md) · [English](power-bi-refresh.en.md)

Para explorar el reporte con sus datos guardados, consulta la [guía de apertura](power-bi-fast-track.md). Los pasos siguientes solo son necesarios si quieres recargar los CSV.

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
