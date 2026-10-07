# Ruta rápida para Power BI

## Fuente de datos

Usa exclusivamente los CSV de `data/processed/`. Estos archivos ya están limpios, tipificados, relacionados mediante claves y validados. La carpeta `data/raw/` queda como evidencia del origen y para practicar limpieza más adelante.

## Primera carga recomendada

Para construir la primera versión del dashboard, importa estas nueve tablas:

1. `dim_date.csv`
2. `dim_location.csv`
3. `dim_organization.csv`
4. `dim_team.csv`
5. `dim_requester.csv`
6. `dim_agent.csv`
7. `dim_service_catalog.csv`
8. `dim_sla_policy.csv`
9. `fact_cases.csv`

En Power BI Desktop selecciona **Obtener datos > Texto/CSV**, abre cada archivo y elige **Transformar datos**. Confirma los tipos y después selecciona **Cerrar y aplicar**.

## Tipos de datos

- Columnas terminadas en `Key`: número entero.
- `Date`: fecha.
- Columnas terminadas en `At`: fecha/hora.
- Columnas terminadas en `Flag`: verdadero/falso.
- Columnas terminadas en `Hours`: número decimal.
- Identificadores, nombres, estados y categorías: texto.

## Relaciones del modelo inicial

Configura relaciones de uno a varios (`1:*`) y filtro en una sola dirección, desde la dimensión hacia `fact_cases`:

| Dimensión | Columna | Hecho | Columna |
|---|---|---|---|
| `dim_date` | `DateKey` | `fact_cases` | `CreatedDateKey` |
| `dim_location` | `LocationKey` | `fact_cases` | `LocationKey` |
| `dim_organization` | `OrgUnitKey` | `fact_cases` | `OrgUnitKey` |
| `dim_requester` | `RequesterKey` | `fact_cases` | `RequesterKey` |
| `dim_service_catalog` | `ServiceKey` | `fact_cases` | `ServiceKey` |
| `dim_sla_policy` | `SLAPolicyKey` | `fact_cases` | `SLAPolicyKey` |
| `dim_agent` | `AgentKey` | `fact_cases` | `FinalAgentKey` |
| `dim_team` | `TeamKey` | `fact_cases` | `FinalTeamKey` |

Mantén activas estas ocho relaciones. No conectes todavía `InitialAgentKey`, `InitialTeamKey`, `FirstResponseDateKey`, `ResolvedDateKey` ni `ClosedDateKey`; se incorporarán después para análisis más avanzados.

## Tablas para la segunda etapa

Cuando el dashboard principal funcione, agrega:

- `fact_surveys.csv`: satisfacción y facilidad.
- `fact_backlog_daily.csv`: evolución diaria del backlog.
- `fact_queue_capacity_weekly.csv`: capacidad semanal.
- `fact_case_events.csv`: flujo detallado y process mining.

El manifiesto `data/manifest.json` documenta los volúmenes, hashes y validaciones. El diccionario completo está en `docs/data-dictionary.es.md`.
