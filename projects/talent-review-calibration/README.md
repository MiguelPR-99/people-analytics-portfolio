# Proyecto 0: Talent Review & Calibration

Dashboard de Power BI para revisar evaluaciones de desempeño y potencial y preparar conversaciones de calibración en RH.

[← Volver al portafolio](../../README.md) · [English](README.en.md)

[![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?logo=powerbi&logoColor=black)](https://app.powerbi.com/view?r=eyJrIjoiMjM2NGFkZjYtOWNiNy00MWZhLWJjOGEtYzY5ZGZhZTk2N2E3IiwidCI6ImY4NGNiMmZiLTQ0MDgtNDcxMC05NWY5LTQwYjBmMThlZDQ3ZiIsImMiOjR9)
![Power Query](https://img.shields.io/badge/Power%20Query-217346?logo=powerquery&logoColor=white)
![DAX](https://img.shields.io/badge/DAX-F2C811?logo=powerbi&logoColor=black)
![Excel](https://img.shields.io/badge/Excel-217346?logo=microsoftexcel&logoColor=white)

Caso de aprendizaje con evaluaciones de **100 empleados ficticios**. Todos los datos son sintéticos.

## El problema

En un proceso de Talent Review, RH reúne las evaluaciones de distintos equipos y revisa qué cambió respecto al periodo anterior. La calibración permite conversar sobre los criterios y la evidencia utilizados para evaluar.

Desarrollé este dashboard para organizar esa información y facilitar la revisión de las evaluaciones por empleado, manager y departamento.

## Ver el proyecto

Puedes revisar las capturas en GitHub o [descargar y abrir el reporte en Power BI Desktop](docs/power-bi-fast-track.md).

![Talent Overview: distribución de las evaluaciones en la matriz 9-box y contexto del empleado seleccionado](assets/talent-overview.png)

La vista principal utiliza una matriz **9-box**, que combina tres niveles de desempeño con tres de potencial en nueve categorías.

El recorrido continúa con [movimientos entre evaluaciones](assets/talent-movement.png), [calibración entre managers](assets/calibration-managers.png) y [comparación por departamento](assets/department-analysis.png).

[Demo de Power BI](https://app.powerbi.com/view?r=eyJrIjoiMjM2NGFkZjYtOWNiNy00MWZhLWJjOGEtYzY5ZGZhZTk2N2E3IiwidCI6ImY4NGNiMmZiLTQ0MDgtNDcxMC05NWY5LTQwYjBmMThlZDQ3ZiIsImMiOjR9).

## Un resultado que permite explorar

Entre **2025 y 2026**, el **66%** mantuvo su posición en la matriz, el **18%** tuvo un cambio positivo en las evaluaciones, el **14%** un cambio negativo y el **2%** un movimiento mixto.

El dashboard permite revisar esas transiciones. Por ejemplo, distingue cuando sube el desempeño y baja el potencial, o al revés, para conservar ambos cambios en la conversación.

Son cambios en evaluaciones sintéticas. Por sí solos no explican sus causas ni demuestran una mejora o un deterioro de la persona.

## Cómo lo construí

Partí de un archivo de **Excel** con empleados, evaluaciones anuales y la correspondencia con las categorías 9-box. Usé **Power Query** para preparar las tablas, un **modelo tipo estrella** para relacionarlas y **medidas DAX** para calcular los indicadores según los filtros.

Contrasté las medidas con el archivo de origen bajo distintos filtros de periodo y departamento.

## Decisiones y aprendizaje

Al comparar managers, usé como referencia el promedio de la población seleccionada y consideré el tamaño de sus equipos. Las señales de calibración ayudan a decidir qué criterios conviene revisar; no prueban sesgos ni la calidad de la gestión.

También acoté el alcance de **Talent Balance**: compara dos categorías de la matriz y se expresa en puntos porcentuales. Para interpretar un departamento hace falta revisar el resto de las evaluaciones y cuántos empleados representa cada porcentaje.

El proyecto me ayudó a trabajar con comparaciones entre periodos y contextos de filtro, y a explicar los límites de un indicador antes de proponer acciones. Las decisiones sobre desarrollo, promoción o compensación requieren evidencia adicional y revisión humana.

## Más detalles

[Métricas y reglas de cálculo](docs/metric-dictionary.md) · [Modelo de datos](docs/data-model.md) · [Dataset sintético](data/9box_powerbi_dataset_demo.xlsx)

Miguel — [Perfil de GitHub](https://github.com/MiguelPR-99)
