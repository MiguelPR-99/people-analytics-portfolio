# Project 1: HR Services Control Tower

A Power BI dashboard for reviewing HR requests and deciding where the team should focus its attention.

[← Back to portfolio](../../README.en.md) · [Español](README.md)

![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?logo=powerbi&logoColor=black)
![Power Query](https://img.shields.io/badge/Power%20Query-217346?logo=powerquery&logoColor=white)
![DAX](https://img.shields.io/badge/DAX-F2C811?logo=powerbi&logoColor=black)
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)

> Synthetic data and results. Independent project, not affiliated with or endorsed by Siemens Energy.

## The problem

An HR Services team receives requests about payroll, benefits, documents, and employee changes. To organize its work, it needs to know whether cases are being resolved as fast as they arrive and where pending work is accumulating.

I developed this case using 9,000 synthetic requests to explore those questions alongside service times, capacity, and satisfaction.

## View the project

You can review the screenshots on GitHub or [view or download the report](docs/power-bi-fast-track.en.md).

The executive view shows demand, pending cases, and compliance with service-level agreement (SLA) targets.

![HR Services Control Tower executive view](assets/screenshots/executive-overview.png)

The walkthrough continues with [SLA and backlog](assets/screenshots/sla-backlog-analysis.png), [service capacity](assets/screenshots/operational-drivers.png), and [process and satisfaction](assets/screenshots/process-experience.png).

## One result to explore

At the scenario cutoff, 503 of the 679 pending cases had exceeded their resolution target. The dashboard lets the reader review their distribution by service and explore waiting times, available capacity, and requests submitted with incomplete information.

The patterns were designed in synthetic data. Proposed actions relate to that scenario; they are not improvements already implemented in an organization.

## How I built it

1. **Python generates the scenario.** It creates cases, events, surveys, and capacity data, and calculates business-hour durations and consistency checks.
2. **Power Query loads the processed CSV files.** It imports tables and sets data types. The published version does not use the raw files as input.
3. **The model and DAX support the analysis.** They relate service data and calculate indicators under the report's filters.

## Decisions and learning

I retained daily backlog snapshots—the cases still open at the end of each day—to study how work accumulates. I also distinguished creation and closure dates and which cases are eligible for each SLA calculation.

When comparing satisfaction, I included the number of survey responses in each group. This helps interpret small samples and present observed relationships without attributing causality.

The project helped me connect data preparation with operational questions and check what each indicator measures before recommending an action.

## More details

[Methodology and model](docs/technical-overview.en.md) · [Metric dictionary](docs/metric-dictionary.en.md) · [Formula and value checks](evidence/model-verification.json) · [Refresh the data](docs/power-bi-refresh.en.md)

Miguel — [GitHub profile](https://github.com/MiguelPR-99)
