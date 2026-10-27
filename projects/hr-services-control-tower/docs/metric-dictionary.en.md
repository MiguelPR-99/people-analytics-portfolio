# Control Tower metric dictionary

[← Case study](../README.en.md) · [Español](metric-dictionary.md)

These definitions reflect the measures in the published PBIX. Durations and flags are generated in Python; DAX counts, filters, and aggregates those fields. Measure names are retained as they appear in Power BI.

## Definitions and denominators

| Measure | Calculation and population |
|---|---|
| Casos recibidos | Distinct CaseKey values in fact_cases. The calendar filters CreatedDateKey. |
| Casos cerrados por fecha | Distinct cases with Closed status, using the ClosedDateKey relationship. |
| Backlog actual | Cases with statuses other than Closed and Cancelled at the dataset's fixed cutoff. Ignores dim_date filters. |
| Backlog al corte | Distinct cases in the snapshot for the maximum selected date. Does not sum cases across all days. |
| Backlog vencido al corte | Cases in that snapshot with ResolutionSLABreachedAtSnapshotFlag=true. |
| Backlog vencido % | Backlog vencido al corte / Backlog al corte. The denominator is pending cases on that date. |
| Cumplimiento SLA primera respuesta % | Cases with FirstResponseWithinSLAFlag=true / cases where that flag is not blank. |
| Cumplimiento SLA resolución % | Cases with ResolutionWithinSLAFlag=true / cases where that flag is not blank. |
| Resolución primer contacto % (FCR) | Cases with FirstContactResolvedFlag=true / cases where that flag is not blank. |
| Tiempo promedio resolución neta (h) | Average NetResolutionBusinessHours; blank values are excluded. |
| Disponibilidad de capacidad % | Sum of AvailableHours / sum of ScheduledHours. Not a simple average of weekly percentages. |
| Ausencia sobre capacidad % | Sum of AbsenceHours / sum of ScheduledHours. Not the proportion of people absent. |
| Solicitudes completas al primer envío % | Cases with InformationCompleteAtSubmissionFlag=true / Casos recibidos. |
| Casos reabiertos % | Cases with ReopenCount>0, populated ResolvedAt, and CancelledFlag=false / eligible resolved cases meeting the last two conditions. |
| Encuestas respondidas | Valid rows in fact_surveys. Not the total number of serviced cases. |
| CSAT promedio | Average OverallSatisfactionScore across available surveys, on a 1–5 scale. |
| Calificaciones bajas % | Surveys with LowRatingFlag=true / Encuestas respondidas. The flag identifies scores of 1 or 2. |

Ratios use DIVIDE. Without a valid denominator, a measure can return BLANK instead of an interpretable percentage.

FCR uses a probabilistically generated synthetic flag. The measure does not recheck TransferCount, ReopenCount, or InteractionCount; it is not equivalent to separately filtering for zero transfers and zero reopenings.

## Meaning of the selected date

- Indicators based on fact_cases primarily filter by creation date. Closure-by-date measures use the closure relationship.
- Backlog actual removes the calendar filter. Backlog al corte uses the maximum selected snapshot date.
- Capacity is recorded by WeekStartDateKey: included weeks are those starting within the filter.
- Surveys relate to cases. The main calendar period filters the cohort by case creation, not directly by survey response date.

For example, selecting January 2025 returns 116 for Backlog al corte while Backlog actual retains the 679 cases at the final cutoff.

## Hours and SLA

The synthetic schedule is Monday–Friday, 08:00–16:00, with non-working days defined in the scenario. First response uses business hours elapsed since case creation.

Net resolution starts with business hours until resolution and excludes waiting for employee information. Approval and vendor waits are not excluded. A case without final resolution does not have an evaluable resolution-SLA flag.

Visible report targets—85% for first response, 80% for resolution, 50% for FCR, and 24 hours for average resolution—are illustrative case references, not commitments by a real company.

## Reference results

With the full period through June 30, 2026, queries against the PBIX returned:

| Indicator | Value |
|---|---:|
| Cases received | 9,000 |
| Current backlog and backlog at final cutoff | 679 |
| Overdue backlog | 503 (74.1%) |
| Resolution-SLA compliance | 73.4%, across 8,199 eligible cases |
| FCR | 45.5% |
| Average net resolution | 26.37 business hours |
| Capacity availability | 86.6% |
| Surveys | 2,543 |
| Average CSAT | 3.91/5 |

The satisfaction comparison between cases without rework and cases with both transfer and reopening uses 2,061 and 21 responses, respectively. Sample sizes differ and patterns are synthetic. The chart should be read as an observed relationship even though its original title uses the word “impact.”

[Extracted DAX expressions](../power-bi/measures-reference.dax) · [Verification record](../evidence/model-verification.json) · [Methodology and model](technical-overview.en.md)
