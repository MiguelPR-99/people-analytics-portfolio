# Evidence and testing

[← Case study](../../README.en.md) · [Español](evidence-manifest.md)

This index brings together screenshots of the result and records describing what was checked. The images show the experience; phase reports describe controls and limitations. Detailed implementation reports linked below are retained in Spanish.

## Screenshots of the result

- [Power Apps Command Center](../../power-apps/tests/e2e/tests/dq-command-center.spec.ts-snapshots/dq-command-center-power-apps-edge-win32.png): exception queue, filters, and case context.
- [Power BI report](checkpoint-02-power-bi-public-scorecard.png): data-quality indicators, case tracking, and source-correction confirmation.

Both screenshots use synthetic data. The Dataverse case sample does not represent all analytical exceptions in Fabric.

## What was checked

| Project area | Evidence and scope |
|---|---|
| Synthetic data and Fabric | [Generator validation](../../docs/synthetic-data-validation.es.md) and [Fabric verification](../../docs/phase-4-gate-review.es.md): repeatable scenario, contracts, and reconciliation. |
| Power Apps | [Power Apps tests](../../docs/phase-6-gate-review.es.md): types, five component tests, four load and navigation tests, a separate real-creation test, and visual comparison. |
| Power Automate | [Flow verification](../../docs/phase-7-gate-review.es.md): approval, rejection, waiver, duplicate prevention, and timeout, with environment limitations. |
| Power BI | [Model and report reconciliation](../../docs/phase-8-gate-review.es.md) and [final visual review](power-bi-visual-review.json). |
| Local regression | [October 18, 2026 record](local-regression.json): generator, components, Power BI readiness, PBIR validation, and repository hygiene. It did not repeat tenant tests, visual comparison, or record creation. |

Reports retain the dates and scope of each run. The [Power Platform record](../power-apps/phase-7-verification.json) summarizes an earlier browser check without creating records.

[Verification commands and options](../../docs/phase-9-test-and-publication-plan.es.md)
