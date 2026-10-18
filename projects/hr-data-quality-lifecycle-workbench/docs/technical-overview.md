# Technical overview

[← Case study](../README.md) · [Español](technical-overview.es.md)

This page is the technical entry point for Project 3. The public case study stays concise; the links below preserve the decisions, controls, and reproducible artifacts behind it.

## Architecture and boundaries

| Layer | Responsibility | Main artifacts |
|---|---|---|
| Synthetic sources | Reproducible worker, lifecycle, and organization records with controlled anomalies | [`config/`](../config/) · [`data/`](../data/) · [`scripts/generate_synthetic_data.py`](../scripts/generate_synthetic_data.py) |
| Microsoft Fabric | Bronze preservation, Silver normalization, Gold rules, recurrence, and reconciliation | [`notebooks/`](../notebooks/) · [`sql/`](../sql/) · [implementation notes](fabric-implementation.es.md) |
| Dataverse | Transactional cases, activities, evidence, status catalog, ownership, and audit | [`dataverse/`](../dataverse/) · [data model](dataverse-design.es.md) |
| Power Apps | React + TypeScript Generative Page for prioritization; model-driven app for governed transactions | [`power-apps/`](../power-apps/) · [architecture decision](generative-page-architecture.es.md) |
| Power Automate | Assignment, notification, approval, timeout, error logging, and idempotency | [automation design](phase-7-automation-design.es.md) · [gate review](phase-7-gate-review.es.md) |
| Power BI | PBIP/TMDL/PBIR semantic model and one-page executive scorecard | [`power-bi/`](../power-bi/) · [BI design](phase-8-bi-design.es.md) |

Fabric is the analytical source of truth. Dataverse stores only the exceptions selected for remediation and their operational history. Neither Power Apps nor Power Automate overwrites the source HR records.

## Reproducibility

The project uses a fixed seed, versioned schemas, parameterized connections, source-controlled Power BI artifacts, component tests, and machine-readable gate results.

From the project folder:

```powershell
python -m unittest discover -s scripts/tests -v
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify_phase9.ps1
```

Tenant smoke tests and the single controlled mutation remain opt-in because they require a connected Power Platform environment. Local credentials, authentication state, Power BI cache, and Desktop settings are ignored by Git.

## Public connection parameters

The checked-in semantic model contains safe example defaults:

- `contoso.datawarehouse.fabric.microsoft.com`
- `lh_hr_data_quality`
- `https://contoso.crm.dynamics.com`

Set the three Power Query parameters in Power BI Desktop to the target environment before refresh. No Fabric deployment is part of the GitHub publication.

## Validation trail

- [Synthetic data validation](synthetic-data-validation.es.md)
- [Fabric gate](phase-4-gate-review.es.md)
- [Dataverse gate](phase-5-gate-review.es.md)
- [Power Apps gate](phase-6-gate-review.es.md)
- [Power Automate gate](phase-7-gate-review.es.md)
- [Power BI gate](phase-8-gate-review.es.md)
- [Phase 9 publication gate](phase-9-test-and-publication-plan.es.md)
- [Curated evidence](../evidence/phase-9/evidence-manifest.md)

## Known limits

- The volumes and patterns are intentionally small and synthetic.
- The published-case subset demonstrates the workflow; it is not the full analytical population.
- The current sample has no SLA-eligible terminal cases, so the SLA card correctly reports no eligible cases.
- The Power Platform solution was validated in a development tenant, not as a production multi-environment deployment.
- Source-system correction is represented as a governed state; the project never writes back to a real HRIS.
