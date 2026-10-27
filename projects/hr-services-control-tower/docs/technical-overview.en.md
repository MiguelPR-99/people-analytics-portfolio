# Control Tower methodology and model

[← Case study](../README.en.md) · [Español](technical-overview.md)

The project analyzes a fictional HR Services operation from January 2025 through June 2026. It reviews demand, pending work, and service times, and explores their relationships with capacity and satisfaction.

## What each tool does

Python generates the synthetic data and checks consistency. It also calculates business-hour durations, waiting times, SLA flags, and daily backlog snapshots.

The generator produces two sets: coherent tables in data/processed and deliberately imperfect versions in data/raw. It is not a cleaning process that transforms raw files into processed ones.

The published PBIX imports all thirteen CSV files from data/processed. Power Query promotes headers and sets types, including locale-specific numeric conversion. The model relates the tables, and DAX measures calculate indicators under the selected filters.

The raw folder remains available for reviewing the scenario design and practicing data cleaning. The [initial design](synthetic-data-design.es.md), retained in Spanish, proposed loading it into Power Query; that part was not implemented in the published PBIX.

[Generator](../scripts/generate_synthetic_data.py) · [Data regeneration guide in Spanish](generator-guide.es.md) · [Field dictionary in Spanish](data-dictionary.es.md)

## How the data is organized

The eight dimensions cover calendar, locations, organization, teams, requesters, agents, services, and SLA policies. The five fact tables have different levels of detail:

| Table | One row represents |
|---|---|
| fact_cases | One unique case. |
| fact_case_events | One event within a case. |
| fact_surveys | One valid survey response. |
| fact_backlog_daily | One case pending at the end of a day. |
| fact_queue_capacity_weekly | One team's capacity for a location during a week. |

Dimensions filter the relevant facts. The model also relates cases to events and surveys. The case-to-survey relationship is 1:1 and bidirectional in the published version; this matters when interpreting filters.

## Dates and backlog

In fact_cases, the active calendar relationship uses creation date. Measures counting closures by date activate the relationship with ClosedDateKey.

Backlog requires different logic. Counting every fact_backlog_daily row would count the same case multiple times if it remained open for several days. Backlog al corte counts distinct cases only on the maximum selected date.

Backlog actual instead uses final case status and removes calendar filters. It therefore represents the dataset's fixed cutoff even when the report period changes. Both return 679 on June 30, 2026; selecting January 2025 gives 116 for Backlog al corte while Backlog actual remains 679.

Statuses other than Closed and Cancelled count as pending. This includes a Resolved case that has not yet been closed.

## Durations and SLA

The synthetic calendar uses Monday–Friday service hours of 08:00–16:00 and non-working dates defined by the simulation. Durations are not calendar hours.

Net resolution time excludes waiting for employee information. Approval and vendor waits remain included. Python calculates these durations and compares them with the priority's SLA; Power BI aggregates the resulting flags.

Compliance percentages include only cases with a populated SLA flag. Pending cases without a resolution are not treated as resolved cases missing their SLA; their exposure is shown in overdue backlog.

[Definitions and denominators](metric-dictionary.en.md) · [Extracted DAX measures](../power-bi/measures-reference.dax)

## Reading the results

The full period contains 9,000 cases and 2,543 surveys. Final backlog is 679 cases, of which 503 are overdue. Resolution-SLA compliance is 73.4% across 8,199 eligible cases; its denominator is not all 9,000 cases.

For satisfaction, the group without transfers or reopenings averages 4.03 across 2,061 responses. The group with both averages 2.67 across just 21 responses. This is a comparison within the synthetic scenario, not evidence that rework causes a specific drop in satisfaction.

Patterns were built into the generator to check the analysis. Card targets are also illustrative, not Siemens Energy benchmarks.

## What was checked

The [generator manifest](../data/manifest.json) retains counts, hashes, and checks for integrity, event ordering, backlog reconciliation, and synthetic patterns. The [automated test](../scripts/tests/test_generator.py) compares two 500-case generations to check file reproducibility.

For this review, sources and 28 measures were inspected in the same PBIX available on GitHub. Global values, satisfaction groups, and the behavior of both backlog measures under a date filter were checked. The model was not modified and its data was not refreshed.

[Verification record](../evidence/model-verification.json)

## Files and scope

The [PBIX](../power-bi/Project-1-HR-Services-Control-Tower.pbix?raw=true) supports report exploration and model inspection in Desktop. Screenshots show the result without requiring installation. The [opening guide](power-bi-fast-track.en.md) explains how to update paths when reloading CSV files.

The project studies service processes using synthetic data. It does not measure individual productivity or establish real savings or improvements.
