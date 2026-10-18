# Curated public evidence

[← Case study](../../README.md) · [Español](evidence-manifest.es.md)

The public narrative uses only two images:

1. [DQ Command Center](../../power-apps/tests/e2e/tests/dq-command-center.spec.ts-snapshots/dq-command-center-power-apps-edge-win32.png) — the operational queue and case-readiness controls with synthetic data.
2. [Power BI scorecard](checkpoint-02-power-bi-public-scorecard.png) — the analytical and remediation view after refresh and visual review.

Machine-readable evidence:

- [`local-regression.json`](local-regression.json) — the cross-layer local gate.
- [`power-bi-visual-review.json`](power-bi-visual-review.json) — the final rendering checklist.
- [`../power-apps/phase-7-verification.json`](../power-apps/phase-7-verification.json) — Power Apps and Power Automate verification results.

The working archive contained many construction checkpoints. They are intentionally excluded from the public package because they repeat intermediate UI states and may contain development-environment chrome. The selected files are sufficient to explain the result without making the case study heavy.
