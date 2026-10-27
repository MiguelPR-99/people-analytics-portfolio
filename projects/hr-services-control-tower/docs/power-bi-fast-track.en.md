# Open and refresh the report

[← Case study](../README.en.md) · [Español](power-bi-fast-track.md)

You can review screenshots on GitHub or download the file to explore the report in Power BI Desktop. The published PBIX includes imported data from the synthetic scenario.

## Review the screenshots

[Executive view](../assets/screenshots/executive-overview.png) · [SLA and backlog](../assets/screenshots/sla-backlog-analysis.png) · [Capacity](../assets/screenshots/operational-drivers.png) · [Process and satisfaction](../assets/screenshots/process-experience.png)

## Open the PBIX

1. [Download the file](../power-bi/Project-1-HR-Services-Control-Tower.pbix?raw=true).
2. Open it in a recent version of Power BI Desktop on Windows.
3. Explore the four pages and their filters using the saved data. Refresh is not needed to review this version of the report.

[Install Power BI Desktop](https://learn.microsoft.com/power-bi/fundamentals/desktop-get-the-desktop)

The file is a copy of the full report, model, and synthetic data, rather than a link requiring access to the university account's hosted report.

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
