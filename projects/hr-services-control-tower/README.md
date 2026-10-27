# Proyecto 1: HR Services Control Tower

Un dashboard de Power BI para revisar las solicitudes de RH y decidir dónde concentrar la atención del equipo.

[← Volver al portafolio](../../README.md) · [English](README.en.md)

![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?logo=powerbi&logoColor=black)
![Power Query](https://img.shields.io/badge/Power%20Query-217346?logo=powerquery&logoColor=white)
![DAX](https://img.shields.io/badge/DAX-F2C811?logo=powerbi&logoColor=black)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)

> Datos y resultados sintéticos. Proyecto independiente, sin afiliación ni respaldo de Siemens Energy.

## El problema

Un equipo de HR Services recibe solicitudes de nómina, beneficios, documentos y movimientos de personal. Para organizar el trabajo necesita saber si está resolviendo los casos al ritmo en que llegan y dónde se acumulan los pendientes.

Desarrollé este caso con 9,000 solicitudes sintéticas para explorar esas preguntas y relacionarlas con los tiempos de atención, la capacidad y la satisfacción.

## Ver el proyecto

Puedes revisar las capturas en GitHub o [descargar y abrir el reporte en Power BI Desktop](docs/power-bi-fast-track.md).

La vista ejecutiva muestra la demanda, los casos pendientes y el cumplimiento de los plazos de atención acordados (SLA).

![Vista ejecutiva de HR Services Control Tower](assets/screenshots/executive-overview.png)

El recorrido continúa con [SLA y backlog](assets/screenshots/sla-backlog-analysis.png), [capacidad de atención](assets/screenshots/operational-drivers.png) y [proceso y satisfacción](assets/screenshots/process-experience.png).

## Un resultado que permite explorar

Al corte del escenario, 503 de los 679 casos pendientes habían superado su plazo de resolución. El dashboard permite revisar cómo se distribuyen por servicio y explorar las esperas, la capacidad disponible y las solicitudes que llegaron incompletas.

Los patrones se diseñaron en datos sintéticos. Las acciones que se plantean son propuestas para ese escenario, no mejoras ya implementadas en una organización.

## Cómo lo construí

1. **Python genera el escenario.** Crea los casos, sus eventos, las encuestas y la capacidad, además de calcular tiempos hábiles y comprobaciones de consistencia.
2. **Power Query carga los CSV procesados.** Importa las tablas y ajusta los tipos de dato. La versión publicada no utiliza los archivos raw como entrada.
3. **El modelo y DAX permiten analizar los resultados.** Relacionan los datos de servicio y calculan indicadores según los filtros del reporte.

## Decisiones y aprendizaje

Conservé snapshots diarios del backlog —los casos que seguían abiertos al final de cada día— para estudiar cómo se acumula el trabajo. También distinguí las fechas de creación y cierre y los casos que pueden entrar en cada cálculo de SLA.

Al comparar satisfacción, incluí el número de encuestas de cada grupo. Esto ayuda a interpretar los resultados cuando hay pocas respuestas y a presentar las relaciones observadas sin atribuirles causalidad.

El proyecto me ayudó a conectar la preparación de datos con preguntas operativas y a revisar qué mide cada indicador antes de recomendar una acción.

## Más detalles

[Metodología y modelo](docs/technical-overview.md) · [Diccionario de métricas](docs/metric-dictionary.md) · [Comprobación de medidas y valores](evidence/model-verification.json) · [Actualizar los datos](docs/power-bi-refresh.md)

Miguel — [Perfil de GitHub](https://github.com/MiguelPR-99)
