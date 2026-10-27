# Proyecto 0: Talent Review & Calibration

Dashboard de Power BI para revisar evaluaciones de desempeño y potencial, comparar periodos y preparar conversaciones de calibración en RH.

[← Volver al portafolio](../../README.md) · [English](README.en.md)

[![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?logo=powerbi&logoColor=black)](https://app.powerbi.com/view?r=eyJrIjoiMjM2NGFkZjYtOWNiNy00MWZhLWJjOGEtYzY5ZGZhZTk2N2E3IiwidCI6ImY4NGNiMmZiLTQ0MDgtNDcxMC05NWY5LTQwYjBmMThlZDQ3ZiIsImMiOjR9)
![Power Query](https://img.shields.io/badge/Power%20Query-217346?logo=powerquery&logoColor=white)
![DAX](https://img.shields.io/badge/DAX-F2C811?logo=powerbi&logoColor=black)
![Excel](https://img.shields.io/badge/Excel-217346?logo=microsoftexcel&logoColor=white)

Caso de aprendizaje con evaluaciones de **100 empleados ficticios**. Todos los datos son sintéticos y el reporte apoya la revisión humana.

## El problema

En un proceso de Talent Review, RH necesita reunir evaluaciones de distintos equipos, revisar los criterios utilizados y entender qué cambió respecto al periodo anterior.

Construí cuatro vistas para explorar esas preguntas a partir de las evaluaciones existentes. La **calibración** es la conversación en la que se revisan los criterios y la evidencia que las sustentan.

## Explorar el reporte

**[Abrir la demo de Power BI](https://app.powerbi.com/view?r=eyJrIjoiMjM2NGFkZjYtOWNiNy00MWZhLWJjOGEtYzY5ZGZhZTk2N2E3IiwidCI6ImY4NGNiMmZiLTQ0MDgtNDcxMC05NWY5LTQwYjBmMThlZDQ3ZiIsImMiOjR9)** · [Descargar el PBIX](power-bi/Project-0-Talent-Review-Calibration.pbix)

![Talent Overview: distribución de las evaluaciones en la matriz 9-box y contexto del empleado seleccionado](assets/talent-overview.png)

La matriz **9-box** combina tres niveles de desempeño con tres de potencial en nueve categorías.

| Vista | Qué permite revisar |
|---|---|
| Talent Overview | La distribución en la matriz y el contexto de un empleado |
| [Talent Movement](assets/talent-movement.png) | Los cambios respecto a la evaluación anterior |
| [Calibration & Managers](assets/calibration-managers.png) | Las diferencias entre las evaluaciones promedio de cada manager y la población seleccionada |
| [Department Analysis](assets/department-analysis.png) | La distribución de evaluaciones por departamento, considerando su tamaño |

## Cómo lo construí

Partí de un archivo de Excel con empleados, evaluaciones anuales y la correspondencia con las categorías 9-box. Usé **Power Query** para preparar las tablas, un **modelo tipo estrella** para relacionarlas y **medidas DAX** para calcular los indicadores según los filtros del reporte.

Contrasté las medidas con el archivo de origen bajo distintos filtros de periodo y departamento.

## Un ejemplo de lectura

Entre **2025 y 2026**, el **66%** mantuvo su posición en la matriz, el **18%** tuvo un cambio positivo en las evaluaciones, el **14%** un cambio negativo y el **2%** un movimiento mixto.

El movimiento mixto distingue cuando una evaluación sube en desempeño y baja en potencial, o al revés. Estos cambios describen las evaluaciones registradas; no explican sus causas ni demuestran por sí solos una mejora o un deterioro de la persona.

## Cómo interpretar las métricas

- **Señal de calibración:** diferencia absoluta de al menos **0.25 puntos** en el promedio de desempeño o potencial, con un mínimo de **cinco empleados evaluados** por manager. La referencia es la población seleccionada con los filtros activos. Es una regla del ejercicio para priorizar conversaciones; no es una prueba estadística.
- **Talent Balance:** porcentaje en *Future Leader* menos porcentaje en *Under Performer*, las celdas de desempeño y potencial altos y bajos, respectivamente. Se expresa en **puntos porcentuales** y solo resume esas dos categorías.
- **Tamaño del grupo:** en el ejemplo de 2026, Customer Success tiene seis empleados; tres están en *Under Performer* y ninguno en *Future Leader*. Su Talent Balance es **−50 puntos porcentuales**. Ese resultado necesita contexto sobre las evaluaciones y los puestos antes de proponer acciones.

Las capturas conservan el formato **%** para Talent Balance y expresiones como *talent risk* o *pipeline strength*. Aquí se interpretan como diferencias en la distribución de evaluaciones, con los límites anteriores. El indicador no estima probabilidades de riesgo ni mide por sí solo la preparación para el liderazgo.

## Documentación y archivos

- [Dataset sintético en Excel](data/9box_powerbi_dataset_demo.xlsx).
- [Métricas y reglas de cálculo](docs/metric-dictionary.md).
- [Modelo de datos y notas de implementación](docs/data-model.md).
- [Uso responsable y apoyo de IA](docs/responsible-use.md).

Las diferencias entre managers no prueban sesgos ni la calidad de su gestión. Las decisiones sobre desarrollo, promoción o compensación requieren evidencia adicional y responsabilidad humana.

Miguel — [Perfil de GitHub](https://github.com/MiguelPR-99)
