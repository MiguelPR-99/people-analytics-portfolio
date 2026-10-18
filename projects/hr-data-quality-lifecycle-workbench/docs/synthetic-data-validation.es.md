# Validación de datos sintéticos — Fase 3

## Resultado

La generación oficial utiliza la semilla `20261012` y produce seis lotes trimestrales para cada una de las tres fuentes. Los 18 CSV y el manifiesto se generaron correctamente.

| Control | Resultado |
|---|---:|
| Empleados sintéticos distintos | 1,500 |
| Población empleada inicial | 1,200 |
| Población empleada al corte final | 1,320 |
| Posiciones | 1,450 |
| Eventos de ciclo de vida | 2,867 |
| Archivos CSV | 18 |
| Pruebas automatizadas | 7/7 aprobadas |

## Volumen por fuente

| Fuente | Archivos | Filas |
|---|---:|---:|
| Global HRIS | 6 | 8,359 |
| Local HR Operations | 6 | 2,867 |
| Organization Master | 6 | 8,700 |

Los conteos excluyen la fila de encabezados. Cada archivo tiene hash SHA-256 en `data/manifest.json`.

## Data Quality Score esperado

| Snapshot | Score |
|---|---:|
| 2025-03-31 | 98.5 |
| 2025-06-30 | 98.6 |
| 2025-09-30 | 97.9 |
| 2025-12-31 | 98.6 |
| 2026-03-31 | 98.2 |
| 2026-06-30 | 98.9 |

El score cae durante la reorganización de Q3 2025 y la ola de onboarding de Q1 2026. Mejora en el corte final después de la intervención controlada. Estas cifras son resultados esperados del generador y deberán reproducirse en Fabric antes de tratarlas como evidencia final del caso.

## Excepciones esperadas en el corte final

| Regla | Checks elegibles | Fallas |
|---|---:|---:|
| DQ-001 | 1,504 | 4 |
| DQ-002 | 1,500 | 4 |
| DQ-003 | 1,313 | 15 |
| DQ-004 | 1,500 | 16 |
| DQ-005 | 1,135 | 7 |
| DQ-006 | 1,500 | 4 |
| DQ-007 | 1,500 | 57 |
| DQ-008 | 1,320 | 6 |

Una anomalía primaria puede provocar más de una falla. Por ejemplo, un centro de costo modificado para DQ-004 también puede generar una discrepancia contra el último evento en DQ-007. El manifiesto conserva por separado las anomalías primarias inyectadas y los resultados efectivos de todas las reglas.

## Patrones controlados

Las tres comprobaciones fueron aprobadas:

- Q3 2025 muestra más excepciones de manager y reconciliación que el corte anterior.
- Q1 2026 muestra más incompletitud y sobreocupación de posiciones que Q4 2025.
- Q2 2026 reduce incompletitud y registros desactualizados respecto de Q1 2026.

## Pruebas ejecutadas

Las pruebas automatizadas validan:

1. Particiones, encabezados, filas, columnas y hashes.
2. Reconciliación de población y estados.
3. Presencia y aritmética de las ocho reglas.
4. Ejemplos inyectados para cada regla.
5. Ausencia de columnas sensibles prohibidas.
6. Reproducibilidad entre procesos con distinto `PYTHONHASHSEED`.
7. Bloqueo de sobrescritura cuando no se utiliza `--force`.

También se importó el último CSV de cada fuente mediante un parser de hojas de cálculo. Los tres archivos conservaron sus encabezados, columnas y filas sin errores de estructura.

## Limitación de esta fase

La evaluación incluida en el generador funciona como oráculo de prueba. Fabric deberá implementar nuevamente la lógica de transformación y las reglas. La reconciliación entre ambos resultados será el control de aceptación de la Fase 4.

