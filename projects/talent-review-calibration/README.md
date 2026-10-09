# Project 0: Talent Review & Calibration

Power BI portfolio case for understanding talent distribution, year-over-year movement, rating consistency, and department-level talent risk.

[← Back to portfolio](../../README.md) · [Español](README.es.md)

[![Live report](https://img.shields.io/badge/Power%20BI-Live%20Report-F2C811?logo=powerbi&logoColor=black)](https://app.powerbi.com/view?r=eyJrIjoiMjM2NGFkZjYtOWNiNy00MWZhLWJjOGEtYzY5ZGZhZTk2N2E3IiwidCI6ImY4NGNiMmZiLTQ0MDgtNDcxMC05NWY5LTQwYjBmMThlZDQ3ZiIsImMiOjR9)
![Status](https://img.shields.io/badge/status-completed-14866d)
![Data](https://img.shields.io/badge/data-100%25%20synthetic-4c78a8)

> Portfolio demonstration with synthetic employees and reviews. The report supports structured discussion; it does not automate employment decisions.

## Live demo

**[Open the interactive Power BI report](https://app.powerbi.com/view?r=eyJrIjoiMjM2NGFkZjYtOWNiNy00MWZhLWJjOGEtYzY5ZGZhZTk2N2E3IiwidCI6ImY4NGNiMmZiLTQ0MDgtNDcxMC05NWY5LTQwYjBmMThlZDQ3ZiIsImMiOjR9)**

The public report contains only synthetic data.

## What the project solves

The report turns annual reviews for 100 synthetic employees into four decision-oriented views. It helps answer:

- How is talent distributed across performance and potential levels?
- Is the overall talent position improving, stable, or declining?
- Which manager rating patterns require a calibration discussion?
- Which departments show a stronger leadership pipeline or greater talent risk?

## Report pages

### Talent Overview

Interactive 9-box matrix with the selected review period and concise employee context.

![Talent Overview](assets/talent-overview.png)

### Talent Movement

Movement between the selected review period and the immediately preceding review.

![Talent Movement](assets/talent-movement.png)

### Calibration & Managers

Comparison of manager rating patterns against the selected population. Bubble size represents employees reviewed.

![Calibration and Managers](assets/calibration-managers.png)

### Department Analysis

Comparison of leadership-pipeline strength and talent-risk concentration by department.

![Department Analysis](assets/department-analysis.png)

## Method in plain language

1. A synthetic workbook provides employee information, annual reviews, and the 9-box mapping.
2. Power Query prepares the tables and validates the data types.
3. A star-oriented model connects employees and talent-position definitions to annual reviews.
4. DAX measures calculate distribution, movement, calibration, and department indicators under the selected filters.
5. The measures and published results are checked directly against the synthetic source data.

### Talent Review terms

| Term | Plain-language meaning |
|---|---|
| 9-box matrix | Framework that combines three performance levels with three potential levels |
| Performance | Assessment of results and behaviors during the review period |
| Potential | Organizational assessment of readiness for broader or more complex responsibilities |
| Future Leader | 9-box position with high performance and high potential |
| Under Performer | 9-box position with low performance and low potential |
| Movement | Change in an employee's 9-box position from the prior review |
| Calibration | Structured discussion to apply rating criteria more consistently across teams |
| Calibration signal | Rating pattern that should be reviewed; it is not proof of bias or manager quality |
| Talent Balance | Future Leader percentage minus Under Performer percentage |

## Selected findings

- In 2025, **12%** of employees are Future Leaders and **24%** are Under Performers.
- From 2025 to 2026, **66%** remained stable, **18%** improved, **14%** declined, and **2%** showed mixed movement.
- In the 2024 example, **3 of 8 managers** meet the rule for a calibration review.
- In 2026, Human Resources has the strongest Talent Balance (**+30 percentage points**), while Customer Success has the lowest (**−50 percentage points**).

These are designed patterns in synthetic data, not claims about a real organization.

## Recommended actions

1. Prioritize structured talent reviews in Customer Success and Operations.
2. Discuss flagged rating patterns during calibration before drawing conclusions about bias or manager quality.
3. Build development and mobility plans for leadership-pipeline employees while monitoring department size and context.

## Files and documentation

- [Power BI report](power-bi/Project-0-Talent-Review-Calibration.pbix)
- [Synthetic dataset](data/9box_powerbi_dataset_demo.xlsx)
- [Metric dictionary](docs/metric-dictionary.md)
- [Data model and implementation notes](docs/data-model.md)
- [Responsible-use statement](docs/responsible-use.md)

## Responsible use

- All employees, names, assignments, and reviews are synthetic.
- A 9-box matrix simplifies complex performance and potential discussions.
- Calibration signals identify review priorities, not confirmed bias.
- Small groups can produce unstable percentages and require organizational context.
- The dashboard supports human review; it should not determine promotion, compensation, succession, or termination decisions.

## Author

Miguel — [GitHub profile](https://github.com/MiguelPR-99)
