# Project 0: Talent Review & Calibration

Power BI dashboard for reviewing performance and potential ratings and preparing HR calibration discussions.

[← Back to portfolio](../../README.en.md) · [Español](README.md)

[![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?logo=powerbi&logoColor=black)](https://app.powerbi.com/view?r=eyJrIjoiMjM2NGFkZjYtOWNiNy00MWZhLWJjOGEtYzY5ZGZhZTk2N2E3IiwidCI6ImY4NGNiMmZiLTQ0MDgtNDcxMC05NWY5LTQwYjBmMThlZDQ3ZiIsImMiOjR9)
![Power Query](https://img.shields.io/badge/Power%20Query-217346?logo=powerquery&logoColor=white)
![DAX](https://img.shields.io/badge/DAX-F2C811?logo=powerbi&logoColor=black)
![Excel](https://img.shields.io/badge/Excel-217346?logo=microsoftexcel&logoColor=white)

Learning project with reviews for **100 fictional employees**. All data is synthetic.

## The problem

During a Talent Review, HR brings together assessments from different teams and reviews what has changed since the previous period. Calibration provides a discussion of the criteria and evidence used in those assessments.

I developed this dashboard to organize that information and support reviews by employee, manager, and department.

## View the project

You can review the screenshots on GitHub or [download and open the report in Power BI Desktop](docs/power-bi-fast-track.en.md).

![Talent Overview: rating distribution across the 9-box matrix and context for the selected employee](assets/talent-overview.png)

The main view uses a **9-box matrix**, which combines three performance levels with three potential levels into nine categories.

The walkthrough continues with [movement between reviews](assets/talent-movement.png), [calibration across managers](assets/calibration-managers.png), and [department comparison](assets/department-analysis.png).

[Power BI demo](https://app.powerbi.com/view?r=eyJrIjoiMjM2NGFkZjYtOWNiNy00MWZhLWJjOGEtYzY5ZGZhZTk2N2E3IiwidCI6ImY4NGNiMmZiLTQ0MDgtNDcxMC05NWY5LTQwYjBmMThlZDQ3ZiIsImMiOjR9).

## One result to explore

Between **2025 and 2026**, **66%** stayed in the same matrix position, **18%** had a positive change in their ratings, **14%** had a negative change, and **2%** showed mixed movement.

The dashboard lets the reader review these transitions. For example, it distinguishes cases where performance rises and potential falls, or vice versa, to preserve both changes in the discussion.

These are changes in synthetic assessments. They do not independently explain their causes or establish that a person has improved or declined.

## How I built it

I started with an **Excel** workbook containing employees, annual reviews, and the mapping to 9-box categories. I used **Power Query** to prepare the tables, a **star-oriented model** to connect them, and **DAX measures** to calculate indicators under the selected filters.

I checked measures against the source workbook under different period and department filters.

## Decisions and learning

When comparing managers, I used the selected population's average as the benchmark and considered team size. Calibration signals help identify criteria worth reviewing; they do not prove bias or management quality.

I also limited the interpretation of **Talent Balance**: it compares two matrix categories and is expressed in percentage points. Interpreting a department requires reviewing the rest of its assessments and how many employees each percentage represents.

The project helped me work with period comparisons and filter contexts, and explain an indicator's limits before suggesting actions. Development, promotion, or compensation decisions require additional evidence and human review.

## More details

[Metrics and calculation rules](docs/metric-dictionary.en.md) · [Data model](docs/data-model.en.md) · [Synthetic dataset](data/9box_powerbi_dataset_demo.xlsx)

Miguel — [GitHub profile](https://github.com/MiguelPR-99)
