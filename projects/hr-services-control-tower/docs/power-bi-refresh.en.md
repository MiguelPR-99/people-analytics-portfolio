# Refresh the report data

[← Back to the case](../README.en.md) · [Español](power-bi-refresh.md)

To explore the report with its saved data, see the [opening guide](power-bi-fast-track.en.md). The following steps are only needed if you want to reload the CSV files.

## Reload data on another computer

The PBIX queries use local paths to thirteen CSV files. To reload them:

1. Download the repository and retain the project's data/processed folder.
2. In Power BI Desktop, change each CSV data source to its location on your computer. You can also inspect the paths in Power Query.
3. Keep the queries' types and locale settings; the CSV files use a decimal point.
4. Refresh the model and check the reference values in the metric dictionary.

The published version uses data/processed, not data/raw. Paths are defined individually in the PBIX queries.

For scenario regeneration, see the [generator guide in Spanish](generator-guide.es.md). Changing the seed or case count produces a different scenario, so reference values may no longer match.

## Inspect the implementation

[Methodology and model](technical-overview.en.md) · [Metrics and filters](metric-dictionary.en.md) · [DAX measures](../power-bi/measures-reference.dax)
