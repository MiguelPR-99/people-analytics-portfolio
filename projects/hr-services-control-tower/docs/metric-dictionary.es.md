# Diccionario de métricas del Control Tower

[← Caso principal](../README.md) · [English](metric-dictionary.en.md)

Estas definiciones corresponden a las medidas del PBIX publicado. Las duraciones y banderas se generan en Python; DAX cuenta, filtra y agrega esos campos. Los nombres de medida se conservan como aparecen en Power BI.

## Definiciones y denominadores

| Medida | Cálculo y población |
|---|---|
| Casos recibidos | Casos distintos por CaseKey en fact_cases. El calendario filtra por CreatedDateKey. |
| Casos cerrados por fecha | Casos distintos con estado Closed, usando la relación con ClosedDateKey. |
| Backlog actual | Casos con estado distinto de Closed y Cancelled al corte fijo del dataset. Ignora los filtros de dim_date. |
| Backlog al corte | Casos distintos del snapshot cuya fecha es la máxima seleccionada. No suma los casos de todos los días. |
| Backlog vencido al corte | Subconjunto del mismo snapshot con ResolutionSLABreachedAtSnapshotFlag=true. |
| Backlog vencido % | Backlog vencido al corte / Backlog al corte. El denominador son los pendientes de esa fecha. |
| Cumplimiento SLA primera respuesta % | Casos con FirstResponseWithinSLAFlag=true / casos con esa bandera no vacía. |
| Cumplimiento SLA resolución % | Casos con ResolutionWithinSLAFlag=true / casos con esa bandera no vacía. |
| Resolución primer contacto % (FCR) | Casos con FirstContactResolvedFlag=true / casos con esa bandera no vacía. |
| Tiempo promedio resolución neta (h) | Promedio de NetResolutionBusinessHours; los valores vacíos quedan fuera. |
| Disponibilidad de capacidad % | Suma de AvailableHours / suma de ScheduledHours. No es un promedio simple de porcentajes semanales. |
| Ausencia sobre capacidad % | Suma de AbsenceHours / suma de ScheduledHours. No representa la proporción de personas ausentes. |
| Solicitudes completas al primer envío % | Casos con InformationCompleteAtSubmissionFlag=true / Casos recibidos. |
| Casos reabiertos % | Casos con ReopenCount>0, ResolvedAt informado y CancelledFlag=false / casos resueltos elegibles con esas dos últimas condiciones. |
| Encuestas respondidas | Número de filas válidas en fact_surveys. No equivale al total de casos atendidos. |
| CSAT promedio | Promedio de OverallSatisfactionScore en las encuestas disponibles, en escala de 1 a 5. |
| Calificaciones bajas % | Encuestas con LowRatingFlag=true / Encuestas respondidas. La bandera corresponde a puntuaciones de 1 o 2. |

Las divisiones utilizan DIVIDE. Si no hay denominador válido, la medida puede devolver BLANK en lugar de un porcentaje interpretable.

FCR utiliza una bandera sintética generada probabilísticamente. La medida no vuelve a comprobar TransferCount, ReopenCount o InteractionCount; no equivale a aplicar por separado filtros de cero transferencias y cero reaperturas.

## Qué significa la fecha seleccionada

- En los indicadores basados en fact_cases, el filtro principal corresponde a la fecha de creación. Las medidas de cierres por fecha utilizan la relación de cierre.
- Backlog actual elimina el filtro de calendario. Backlog al corte utiliza la fecha máxima seleccionada en los snapshots.
- La capacidad se registra por WeekStartDateKey: las semanas incluidas son las que tienen su inicio dentro del filtro.
- Las encuestas se relacionan con los casos. El periodo del calendario principal filtra la cohorte por creación del caso, no directamente por fecha de respuesta a la encuesta.

Por ejemplo, seleccionar enero de 2025 da 116 en Backlog al corte, mientras Backlog actual conserva los 679 casos del corte final.

## Horas y SLA

El horario sintético es de lunes a viernes de 08:00 a 16:00, con los días no laborables definidos en el escenario. La primera respuesta usa horas hábiles transcurridas desde la creación.

La resolución neta parte de las horas hábiles hasta la resolución y descuenta la espera por información del empleado. No descuenta las esperas por aprobación o proveedor. Un caso sin resolución final no tiene una bandera de SLA de resolución evaluable.

Las metas visibles del reporte —85% en primera respuesta, 80% en resolución, 50% en FCR y 24 horas de resolución promedio— son referencias ilustrativas del caso, no compromisos de una empresa real.

## Resultados de referencia

Con el periodo completo hasta el 30 de junio de 2026, las consultas al PBIX devolvieron:

| Indicador | Valor |
|---|---:|
| Casos recibidos | 9,000 |
| Backlog actual y al corte final | 679 |
| Backlog vencido | 503 (74.1%) |
| SLA de resolución | 73.4%, sobre 8,199 casos elegibles |
| FCR | 45.5% |
| Resolución neta promedio | 26.37 horas hábiles |
| Disponibilidad de capacidad | 86.6% |
| Encuestas | 2,543 |
| CSAT promedio | 3.91/5 |

La comparación de satisfacción entre casos sin retrabajo y casos con transferencia y reapertura usa 2,061 y 21 encuestas, respectivamente. Los tamaños de muestra son distintos y los patrones son sintéticos. La gráfica debe leerse como una relación observada, aunque su título original use la palabra “impacto”.

[Expresiones DAX consultadas](../power-bi/measures-reference.dax) · [Registro de comprobación](../evidence/model-verification.json) · [Metodología y modelo](technical-overview.md)
