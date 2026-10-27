# Project 0: Talent Review & Calibration

Power BI dashboard for reviewing performance and potential ratings, comparing review periods, and preparing HR calibration discussions.

[← Back to portfolio](../../README.en.md) · [Español](README.md)

[![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?logo=powerbi&logoColor=black)](https://app.powerbi.com/view?r=eyJrIjoiMjM2NGFkZjYtOWNiNy00MWZhLWJjOGEtYzY5ZGZhZTk2N2E3IiwidCI6ImY4NGNiMmZiLTQ0MDgtNDcxMC05NWY5LTQwYjBmMThlZDQ3ZiIsImMiOjR9)
![Power Query](https://img.shields.io/badge/Power%20Query-217346?logo=powerquery&logoColor=white)
![DAX](https://img.shields.io/badge/DAX-F2C811?logo=powerbi&logoColor=black)
![Excel](https://img.shields.io/badge/Excel-217346?logo=microsoftexcel&logoColor=white)

Learning project with reviews for **100 fictional employees**. All data is synthetic, and the report supports human review.

## The problem

During a Talent Review, HR needs to bring together assessments from different teams, review the criteria used, and understand changes since the previous review.

I built four views to explore these questions using existing assessments. **Calibration** is the discussion used to review the criteria and evidence behind them.

## Explore the report

**[Open the Power BI demo](https://app.powerbi.com/view?r=eyJrIjoiMjM2NGFkZjYtOWNiNy00MWZhLWJjOGEtYzY5ZGZhZTk2N2E3IiwidCI6ImY4NGNiMmZiLTQ0MDgtNDcxMC05NWY5LTQwYjBmMThlZDQ3ZiIsImMiOjR9)** · [Download the PBIX](power-bi/Project-0-Talent-Review-Calibration.pbix)

![Talent Overview: rating distribution across the 9-box matrix and context for the selected employee](assets/talent-overview.png)

The **9-box matrix** combines three performance levels with three potential levels into nine categories.

| View | What it helps review |
|---|---|
| Talent Overview | The distribution across the matrix and an employee's context |
| [Talent Movement](assets/talent-movement.png) | Changes from the previous review |
| [Calibration & Managers](assets/calibration-managers.png) | Differences between each manager's average ratings and the selected population |
| [Department Analysis](assets/department-analysis.png) | Rating distributions by department, with group size in view |

## How I built it

I started with an Excel workbook containing employees, annual reviews, and the mapping to 9-box categories. I used **Power Query** to prepare the tables, a **star-oriented model** to connect them, and **DAX measures** to calculate indicators under the report filters.

I checked measures against the source workbook under different period and department filters.

## A reading example

Between **2025 and 2026**, **66%** stayed in the same matrix position, **18%** had a positive change in their ratings, **14%** had a negative change, and **2%** showed mixed movement.

Mixed movement identifies cases where performance rises and potential falls, or vice versa. These changes describe recorded assessments; they do not explain their causes or independently establish that a person has improved or declined.

## Interpreting the metrics

- **Calibration signal:** an absolute difference of at least **0.25 points** in average performance or potential, with at least **five reviewed employees** per manager. The benchmark is the population selected by the active filters. This is an exercise rule for prioritizing discussions, not a statistical test.
- **Talent Balance:** the percentage in *Future Leader* minus the percentage in *Under Performer*, the high-performance/high-potential and low-performance/low-potential cells, respectively. It is a difference in **percentage points** that summarizes only those two categories.
- **Group size:** in the 2026 example, Customer Success has six employees; three are in *Under Performer* and none in *Future Leader*. Its Talent Balance is **−50 percentage points**. That result needs context about the ratings and roles before suggesting actions.

The screenshots retain the **%** format for Talent Balance and wording such as *talent risk* or *pipeline strength*. Here, these refer to differences in rating distributions, subject to the limits above. The indicator does not estimate risk probabilities or independently measure leadership readiness.

## Documentation and files

- [Synthetic Excel dataset](data/9box_powerbi_dataset_demo.xlsx).
- [Metrics and calculation rules](docs/metric-dictionary.en.md).
- [Data model and implementation notes](docs/data-model.en.md).
- [Responsible use and AI assistance](docs/responsible-use.en.md).

Differences between managers do not prove bias or management quality. Development, promotion, or compensation decisions require additional evidence and human accountability.

Miguel — [GitHub profile](https://github.com/MiguelPR-99)
