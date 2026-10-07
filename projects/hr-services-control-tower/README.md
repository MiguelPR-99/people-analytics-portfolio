# Project 1: HR Services Control Tower

Power BI portfolio case for monitoring demand, service levels, backlog, capacity, process quality, and employee experience in a simulated HR Services operation.

[← Back to portfolio](../../README.md) · [Español](README.es.md)

[![Live report](https://img.shields.io/badge/Power%20BI-Live%20Report-F2C811?logo=powerbi&logoColor=black)](https://app.powerbi.com/view?r=eyJrIjoiMjU5MDEzODEtMDBkMi00MmUzLTlhNTgtMmQ4N2E1NDkyZDM2IiwidCI6ImY4NGNiMmZiLTQ0MDgtNDcxMC05NWY5LTQwYjBmMThlZDQ3ZiIsImMiOjR9)
![Status](https://img.shields.io/badge/status-completed-14866d)
![Data](https://img.shields.io/badge/data-100%25%20synthetic-4c78a8)

> Independent portfolio project. The visual language is inspired by public Siemens Energy brand cues, but the project is not affiliated with or endorsed by Siemens Energy.

## Live demo

**[Open the interactive Power BI report](https://app.powerbi.com/view?r=eyJrIjoiMjU5MDEzODEtMDBkMi00MmUzLTlhNTgtMmQ4N2E1NDkyZDM2IiwidCI6ImY4NGNiMmZiLTQ0MDgtNDcxMC05NWY5LTQwYjBmMThlZDQ3ZiIsImMiOjR9)**

The public report contains only synthetic data.

## What the project solves

The report turns 9,000 synthetic HR service cases into four decision-oriented views. It helps answer:

- Is demand being absorbed, or is backlog growing?
- Which services explain SLA breaches?
- Where are capacity and process delays occurring?
- How do incomplete requests, transfers, and reopens relate to employee experience?

## Report pages

### Executive Overview

Demand, backlog, SLA, resolution time, and first-contact resolution.

![Executive Overview](assets/screenshots/executive-overview.png)

### SLA & Backlog Analysis

Overdue work, backlog age, service-level exposure, and monthly evolution.

![SLA and Backlog Analysis](assets/screenshots/sla-backlog-analysis.png)

### Operational Drivers

Scheduled hours, available capacity, capacity-loss causes, and weekly trends.

![Operational Drivers](assets/screenshots/operational-drivers.png)

### Process & Experience

Waiting time, intake completeness, rework, CSAT, and low-rating risk.

![Process and Experience](assets/screenshots/process-experience.png)

## Method in plain language

1. A Python generator creates reproducible, fully synthetic case, event, survey, backlog, and capacity data.
2. Power Query validates types and prepares the analytical tables.
3. A star-oriented model connects shared dimensions—date, service, location, and team—to the fact tables.
4. DAX measures calculate the KPIs under the filters selected in the report.
5. Automated tests and direct source-data checks validate row counts, keys, business rules, and published findings.

### HR Services terms

| Term | Plain-language meaning |
|---|---|
| SLA | Agreed time target for the first response or final resolution |
| Backlog | Cases that remain open at a point in time |
| Overdue backlog | Open cases that already exceeded their resolution target |
| FCR | Cases resolved during the first contact, without transfer or reopen |
| Rework | Extra work caused by a transfer or reopening of a case |
| CSAT | Average satisfaction score from 1 to 5 |
| Capacity availability | Available service hours divided by scheduled hours |

## Selected findings

- The cutoff contains **679 open cases**; **503 (74.1%)** are overdue.
- **Offboarding** has the lowest resolution-SLA compliance at **31.2%**.
- Capacity availability is **86.6%**; absence represents **6.6%** of scheduled hours.
- Request completeness ranges from **79.1% for Email** to **95.4% for Portal**.
- Cases with no transfer or reopen average **4.03 CSAT**. Cases with both average **2.67**, but this last segment contains only **21 survey responses** and requires caution.

These are designed patterns in synthetic data, not claims about a real organization.

## Recommended actions

1. Prioritize breached backlog in Offboarding and Onboarding.
2. Standardize Email intake and guide employees toward the higher-completeness Portal flow.
3. Monitor transferred and reopened cases as a quality queue and always interpret experience percentages with their sample size.

## Files and documentation

- [Power BI report](power-bi/Project-1-HR-Services-Control-Tower.pbix)
- [Processed analytical tables](data/processed/)
- [Raw synthetic exports](data/raw/)
- [Data dictionary](docs/data-dictionary.es.md)
- [Synthetic-data design](docs/synthetic-data-design.es.md)
- [Power BI setup guide](docs/power-bi-fast-track.es.md)
- [Power BI theme](assets/power-bi/siemens-energy-inspired-theme.json)

To regenerate the data:

```powershell
.\scripts\run_generator.ps1
```

## Responsible use

- All people, cases, locations, dates, and survey responses are synthetic.
- The dashboard evaluates service processes, not individual employee performance.
- Small samples can produce unstable percentages; survey counts are included in the relevant tooltip.
- Designed associations demonstrate analysis and do not establish causality.

## Author

Miguel — [GitHub profile](https://github.com/MiguelPR-99)
