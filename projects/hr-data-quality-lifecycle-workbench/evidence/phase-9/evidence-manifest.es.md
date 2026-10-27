# Evidencias y pruebas

[← Caso principal](../../README.md) · [English](evidence-manifest.en.md)

Aquí están las capturas de la aplicación y el dashboard, junto con los informes de las pruebas. Cada informe indica qué se revisó, cuándo se hizo y qué quedó pendiente.

## Capturas

- [Command Center de Power Apps](../../power-apps/tests/e2e/tests/dq-command-center.spec.ts-snapshots/dq-command-center-power-apps-edge-win32.png): filtros, lista de excepciones y detalle del caso.
- [Dashboard de Power BI](checkpoint-02-power-bi-public-scorecard.png): calidad de los datos, avance de los casos y confirmación de correcciones en origen.

Las capturas muestran datos sintéticos. Los casos gestionados en Dataverse son sólo una selección de los problemas detectados en Fabric.

## Pruebas realizadas

| Componente | Qué se comprobó y dónde consultarlo |
|---|---|
| Datos sintéticos y Fabric | [Pruebas del generador](../../docs/synthetic-data-validation.es.md) y [validación de Fabric](../../docs/phase-4-gate-review.es.md): reproducción del escenario, estructura de los datos y coincidencia de resultados. |
| Power Apps | [Pruebas de la app](../../docs/phase-6-gate-review.es.md): revisión de tipos (typecheck), cinco pruebas de componentes, cuatro pruebas de funcionamiento y navegación, una prueba separada de creación de un caso y comparación visual. |
| Power Automate | [Pruebas de los flujos](../../docs/phase-7-gate-review.es.md): aprobación, rechazo, exención, prevención de duplicados y timeout. El informe incluye las limitaciones del entorno. |
| Power BI | [Comprobación del modelo y el reporte](../../docs/phase-8-gate-review.es.md) y [revisión visual final](power-bi-visual-review.json). |
| Regresión local | [Ejecución del 18 de octubre de 2026](local-regression.json): generador, componentes, preparación de Power BI, validación PBIR y exclusión de credenciales y archivos locales. Esta ejecución no repitió las pruebas en el tenant, la comparación visual ni la creación de registros. |

El [registro de Power Platform](../power-apps/phase-7-verification.json) resume una ejecución anterior con pruebas en navegador, sin crear registros.

[Comandos y opciones para ejecutar las comprobaciones](../../docs/phase-9-test-and-publication-plan.es.md)
