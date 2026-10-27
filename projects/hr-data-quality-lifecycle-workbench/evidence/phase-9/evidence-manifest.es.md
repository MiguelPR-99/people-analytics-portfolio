# Evidencias y pruebas

[← Caso principal](../../README.md) · [English](evidence-manifest.en.md)

Este índice reúne las capturas del resultado y los registros que permiten revisar qué se comprobó. Las imágenes muestran la experiencia; los informes de cada fase describen los controles y sus límites.

## Capturas del resultado

- [Command Center de Power Apps](../../power-apps/tests/e2e/tests/dq-command-center.spec.ts-snapshots/dq-command-center-power-apps-edge-win32.png): cola de excepciones, filtros y contexto del caso.
- [Reporte de Power BI](checkpoint-02-power-bi-public-scorecard.png): indicadores de calidad, seguimiento de casos y confirmación de corrección del origen.

Ambas capturas utilizan datos sintéticos. La muestra de casos de Dataverse no representa todas las excepciones analíticas de Fabric.

## Qué se comprobó

| Parte del proyecto | Evidencia y alcance |
|---|---|
| Datos sintéticos y Fabric | [Validación del generador](../../docs/synthetic-data-validation.es.md) y [verificación de Fabric](../../docs/phase-4-gate-review.es.md): escenario repetible, contratos y reconciliación. |
| Power Apps | [Pruebas de Power Apps](../../docs/phase-6-gate-review.es.md): tipos, cinco pruebas de componente, cuatro pruebas de carga y navegación, una prueba separada de creación real y comparación visual. |
| Power Automate | [Verificación de flujos](../../docs/phase-7-gate-review.es.md): aprobación, rechazo, exención, prevención de duplicados y timeout; incluye límites del entorno. |
| Power BI | [Reconciliación del modelo y reporte](../../docs/phase-8-gate-review.es.md) y [revisión visual final](power-bi-visual-review.json). |
| Regresión local | [Registro del 18 de octubre de 2026](local-regression.json): generador, componentes, preparación de Power BI, validación PBIR e higiene del repositorio. No repitió pruebas contra el tenant, comparación visual ni creación de registros. |

Los informes conservan las fechas y el alcance de cada ejecución. El [registro de Power Platform](../power-apps/phase-7-verification.json) resume una comprobación anterior con navegador, sin crear registros.

[Consultar los comandos y las opciones de verificación](../../docs/phase-9-test-and-publication-plan.es.md)
