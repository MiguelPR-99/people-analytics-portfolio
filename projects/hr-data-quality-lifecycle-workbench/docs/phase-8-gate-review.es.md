# Revisión de gate — Fase 8 Power BI

## Dictamen

**Gate 8.2 aprobado el 18 de octubre de 2026.** El scorecard ejecutivo quedó construido como PBIP/TMDL/PBIR, reconciliado con las fuentes validadas, actualizado en Power BI Desktop y revisado mediante una captura automática. La publicación no forma parte de este gate y requiere autorización explícita en la Fase 9.

## Artefactos revisados

- Proyecto: `power-bi/HRDataQualityScorecard.pbip`.
- Modelo semántico: `power-bi/HRDataQualityScorecard.SemanticModel/definition/`.
- Reporte: `power-bi/HRDataQualityScorecard.Report/definition/`.
- Especificación aprobada: `_brief/report-spec.md`.
- Evidencia visual: `evidence/power-bi/checkpoint-01-executive-scorecard-gate-8.2.png`.

## Reconciliación

| Control | Resultado |
|---|---:|
| Cortes de calidad | 6 |
| Filas regla–corte | 48 |
| Excepciones Gold | 923 |
| Reglas | 8 |
| Casos publicados | 5 |
| Actividades del caso | 14 |
| Data Quality Score actual | 98.9 % |
| Variación frente al corte anterior | +0.7 pp |
| Tasa de excepción | 3.0 % |
| Tasa de recurrencia | 3.6 % |
| Cobertura de casos publicados | 0.9 % |

El cumplimiento de SLA devuelve `BLANK()` cuando no existen casos terminales elegibles y el reporte lo comunica como **Sin casos elegibles**, evitando presentar un cero engañoso.

## Controles técnicos

- Actualización completa de las consultas: correcta.
- Contrato de fecha: `Fecha de snapshot` tipada explícitamente como fecha en Power Query y `dateTime` en TMDL.
- Modelo: medidas, relaciones y columnas auxiliares persistidas en TMDL.
- Reporte: validación PBIR con 0 errores. El validador informó una advertencia ambiental `PBIR_SCHEMA_UNREACHABLE` porque no pudo obtener un esquema remoto de Microsoft; Desktop cargó el mismo PBIR y la captura se completó sin fallos.
- Preparación local: `scripts/verify_power_bi_phase8.ps1` aprobó 13/13 controles fuera del sandbox restringido.
- CLI–Desktop: estado `ready` para `HRDataQualityScorecard.Report`; el falso `HOST_UNAVAILABLE` se debía a `EPERM` sobre el named pipe cuando `status` se ejecutaba con permisos distintos a la apertura.
- Seguridad: no se versionaron credenciales, tokens ni archivos locales de usuario; las carpetas `.pbi` están ignoradas. Los identificadores de conexión permanecen como parámetros TMDL y deberán anonimizarse antes de la publicación pública de la Fase 9.

## Revisión visual

La página responde sin explicación oral a la salud actual, evolución temporal, riesgo por dimensión/regla, volumen y cobertura de casos, estado de SLA y eficacia de la remediación. La nota de datos sintéticos y la cobertura parcial de Dataverse permanecen visibles. No se observaron objetos vacíos inesperados, errores de carga ni cifras contradictorias.

## Resultado

La Fase 8 queda cerrada. La Fase 9 puede comenzar con pruebas de recorrido completo, selección de evidencia pública, narrativa del caso, README y publicación controlada.
