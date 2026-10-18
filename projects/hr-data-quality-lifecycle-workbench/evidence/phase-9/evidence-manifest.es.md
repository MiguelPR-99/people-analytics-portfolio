# Evidencia pública curada

[← Caso principal](../../README.es.md) · [English](evidence-manifest.md)

La narrativa pública utiliza únicamente dos imágenes:

1. [DQ Command Center](../../power-apps/tests/e2e/tests/dq-command-center.spec.ts-snapshots/dq-command-center-power-apps-edge-win32.png) — cola operativa y controles de preparación del caso con datos sintéticos.
2. [Scorecard de Power BI](checkpoint-02-power-bi-public-scorecard.png) — vista analítica y de remediación después de la actualización y revisión visual.

Evidencia legible por máquina:

- [`local-regression.json`](local-regression.json) — gate local transversal.
- [`power-bi-visual-review.json`](power-bi-visual-review.json) — checklist del render final.
- [`../power-apps/phase-7-verification.json`](../power-apps/phase-7-verification.json) — resultados de verificación de Power Apps y Power Automate.

El archivo de trabajo contenía numerosas capturas de construcción. Se excluyen intencionalmente del paquete público porque repiten estados intermedios de la interfaz y pueden mostrar elementos del entorno de desarrollo. La selección anterior permite explicar el resultado sin volver pesada la lectura del caso.
