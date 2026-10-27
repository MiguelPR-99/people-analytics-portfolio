# Project 3: HR Data Quality & Lifecycle Workbench

A Digital HR solution for detecting inconsistencies in workforce data and tracking their review.

[← Back to portfolio](../../README.en.md) · [Español](README.md)

![Microsoft Fabric](https://img.shields.io/badge/Microsoft%20Fabric-5B5FC7?logo=microsoft&logoColor=white)
![Dataverse](https://img.shields.io/badge/Dataverse-088142?logo=microsoftdataverse&logoColor=white)
![Power Apps](https://img.shields.io/badge/Power%20Apps-742774?logo=powerapps&logoColor=white)
![Power Automate](https://img.shields.io/badge/Power%20Automate-0066FF?logo=powerautomate&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?logo=powerbi&logoColor=black)
![Python / PySpark](https://img.shields.io/badge/Python%20%2F%20PySpark-3776AB?logo=python&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-CC2927?logo=microsoftsqlserver&logoColor=white)

> Synthetic data and scenarios. Independent project, not affiliated with or endorsed by Siemens Energy.

## The problem

A position change can appear as completed in a lifecycle event while the employee record still shows the previous position. That conflict makes it harder to know which information to use and who should review it.

I developed this case to connect inconsistency detection with investigation: identify what does not match, open a case when needed, and retain evidence of the actions taken.

## The solution in use

In Power Apps, the person responsible for reviewing data can filter exceptions, inspect their context, and create or open a case to document the investigation.

![Power Apps Command Center showing the exception queue and case context](power-apps/tests/e2e/tests/dq-command-center.spec.ts-snapshots/dq-command-center-power-apps-edge-win32.png)

In Power BI, the team can review data quality and case progress. The report distinguishes administrative closure from confirmed correction in the source system.

![Power BI report showing data quality and case progress](evidence/phase-9/checkpoint-02-power-bi-public-scorecard.png)

## How it works

1. **Fabric prepares and reconciles the data.** Three synthetic sources represent employees, lifecycle events, and organizational structure. Eight rules detect inconsistencies and retain their history.
2. **Dataverse holds a sample for review.** The demonstration publishes selected exceptions and keeps the detected issue, its case, and case activities separate.
3. **Power Apps and Power Automate coordinate the work.** The application brings context and evidence together; flows handle notifications, validation, and approvals.
4. **Power BI brings the tracking together.** It combines Fabric analytics with Dataverse cases without presenting the operational sample as the full population.

## Key decisions

I kept the full analytical population in Fabric and an operational sample in Dataverse. Detecting an issue and assigning it to a person are separate steps; publishing every result as a case would have made the review queue difficult to manage.

I also separated case outcome from source-correction confirmation. An approval or closure is not enough to show that an issue has stopped appearing. The application supports human review and does not automatically change a source HR system.

## Development and learning

The interface uses a Power Apps Generative Page built with React and TypeScript. I used AI assistance during development and included component tests and Playwright checks against the published application.

One iteration corrected case creation: the original form had required fields that were locked. The solution creates the record with the necessary data before opening it. This work helped me understand how to distribute responsibilities across the interface, data, and automation.

## Explore the case

[Technical walkthrough and design decisions](docs/technical-overview.en.md) · [Evidence and testing](evidence/phase-9/evidence-manifest.en.md) · [Code and artifacts](./)

Miguel — [GitHub profile](https://github.com/MiguelPR-99)
