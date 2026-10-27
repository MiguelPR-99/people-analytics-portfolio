# Metodología y modelo del Control Tower

[← Caso principal](../README.md) · [English](technical-overview.en.md)

El proyecto analiza la operación de un equipo ficticio de HR Services entre enero de 2025 y junio de 2026. El objetivo es revisar demanda, pendientes y tiempos de atención, y explorar cómo se relacionan con la capacidad y la satisfacción.

## Qué hace cada herramienta

Python genera los datos sintéticos y comprueba su consistencia. También calcula los tiempos hábiles, las esperas, las banderas de SLA y los snapshots diarios del backlog.

El generador produce dos conjuntos: tablas coherentes en data/processed y versiones con problemas deliberados en data/raw. No es un proceso de limpieza que toma los raw y los transforma en processed.

El PBIX publicado importa los trece CSV de data/processed. Power Query promueve encabezados y ajusta los tipos, incluida la configuración regional de campos numéricos. El modelo relaciona las tablas y las medidas DAX calculan los indicadores bajo los filtros seleccionados.

La carpeta raw se conserva para revisar el diseño del escenario y practicar limpieza. El [diseño inicial](synthetic-data-design.es.md) contemplaba cargarla en Power Query; esa parte no se implementó en el PBIX publicado.

[Generador](../scripts/generate_synthetic_data.py) · [Guía para regenerar los datos](generator-guide.es.md) · [Diccionario de campos](data-dictionary.es.md)

## Cómo se organizan los datos

Las ocho dimensiones incluyen calendario, ubicaciones, organización, equipos, solicitantes, agentes, servicios y políticas de SLA. Las cinco tablas de hechos tienen niveles de detalle diferentes:

| Tabla | Una fila representa |
|---|---|
| fact_cases | Un caso único. |
| fact_case_events | Un evento dentro de un caso. |
| fact_surveys | Una respuesta válida a encuesta. |
| fact_backlog_daily | Un caso pendiente al final de un día. |
| fact_queue_capacity_weekly | La capacidad de un equipo para una ubicación durante una semana. |

Las dimensiones comparten filtros con los hechos que corresponden. El modelo también relaciona casos con eventos y encuestas. La relación entre casos y encuestas es 1:1 y bidireccional en la versión publicada; es importante considerarla al interpretar los filtros.

## Fechas y backlog

En fact_cases, la relación activa con el calendario utiliza la fecha de creación. Las medidas que cuentan cierres por fecha activan la relación con ClosedDateKey.

El backlog necesita otra lógica. Contar todas las filas de fact_backlog_daily sumaría el mismo caso varias veces si permaneció abierto durante varios días. La medida Backlog al corte cuenta casos distintos sólo en la fecha máxima seleccionada.

Backlog actual, en cambio, utiliza el estado final del caso y elimina el filtro de calendario. Por eso representa el corte fijo del dataset, aunque cambie el periodo del reporte. Ambas medidas dan 679 al 30 de junio de 2026; al seleccionar enero de 2025, Backlog al corte da 116 y Backlog actual sigue en 679.

Se consideran pendientes los estados distintos de Closed y Cancelled. Esto incluye un caso Resolved que todavía no se haya cerrado.

## Tiempos y SLA

El calendario sintético usa un horario de lunes a viernes de 08:00 a 16:00 y días no laborables definidos en la simulación. Las duraciones no son horas calendario.

El tiempo neto de resolución descuenta la espera por información del empleado. Las esperas por aprobación y proveedor permanecen incluidas. Python calcula esas duraciones y compara el resultado con el SLA de la prioridad; Power BI agrega las banderas resultantes.

Los porcentajes de cumplimiento usan sólo casos con una bandera de SLA informada. Los pendientes sin resolución no se tratan como casos resueltos fuera de SLA: su exposición se consulta en el backlog vencido.

[Definiciones y denominadores](metric-dictionary.md) · [Extracto de las medidas DAX](../power-bi/measures-reference.dax)

## Cómo leer los resultados

El periodo completo contiene 9,000 casos y 2,543 encuestas. El backlog final es de 679 casos, con 503 vencidos. El SLA de resolución alcanza 73.4% entre sus 8,199 casos elegibles; no utiliza los 9,000 como denominador.

En satisfacción, el grupo sin transferencia ni reapertura promedia 4.03 con 2,061 encuestas. El grupo que combina ambas condiciones promedia 2.67 con sólo 21 respuestas. Es una comparación del escenario sintético, no evidencia de que el retrabajo cause una caída concreta en satisfacción.

Los patrones se incorporaron al generador para comprobar el análisis. Las metas de las tarjetas también son ilustrativas, no benchmarks de Siemens Energy.

## Qué se comprobó

El [manifiesto del generador](../data/manifest.json) conserva conteos, hashes y controles de integridad, secuencia temporal, reconciliación del backlog y patrones sintéticos. La [prueba automatizada](../scripts/tests/test_generator.py) compara dos generaciones de 500 casos para comprobar la reproducción de archivos.

Para esta revisión se consultaron las fuentes y 28 medidas del mismo PBIX disponible en GitHub. Se verificaron valores globales, los grupos de satisfacción y el comportamiento de las dos medidas de backlog con un filtro de fecha. No se modificó el modelo ni se actualizaron sus datos.

[Registro de comprobación](../evidence/model-verification.json)

## Archivos y alcance

La [guía de visualización y descarga](power-bi-fast-track.md) reúne las opciones para consultar el reporte en la web o abrir el PBIX y revisar el modelo en Desktop. Las capturas permiten revisar el resultado sin instalarlo. La [guía de actualización](power-bi-refresh.md) explica cómo cambiar las rutas si se quiere recargar los CSV.

El proyecto estudia procesos de servicio con datos sintéticos. No mide productividad individual ni acredita ahorros o mejoras reales.
