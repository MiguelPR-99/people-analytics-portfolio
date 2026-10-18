# Orquestación en Microsoft Fabric

## Propósito

Definir la ejecución reproducible de Bronze, Silver y Gold dentro de la Fase 4. La primera implementación se valida bajo demanda; la programación automática se decidirá después del gate técnico.

## Pipeline

- Nombre: `pl_hr_dq_refresh_dev`
- Workspace: `HR Data Quality Workbench - DEV - MPR`
- Ejecución: manual durante construcción y pruebas
- Política de dependencia: cada actividad continúa únicamente cuando la anterior termina correctamente
- Lakehouse predeterminado de los notebooks: `lh_hr_data_quality_dev`

## Actividades

| Orden | Actividad | Notebook | Responsabilidad |
|---:|---|---|---|
| 1 | `act_01_validate_bronze` | `01_bronze_contract_validation` | Validar estructura, hashes y cardinalidad de Bronze |
| 2 | `act_02_load_silver` | `02_bronze_to_silver` | Tipar, normalizar y materializar Silver de forma idempotente |
| 3 | `act_03_validate_silver` | `03_silver_quality_gate` | Detener el flujo si Silver no cumple los controles |
| 4 | `act_04_build_lifecycle_state` | `04_build_lifecycle_state` | Reconstruir el estado laboral por atributo |
| 5 | `act_05_evaluate_dq_rules` | `05_evaluate_dq_rules` | Evaluar DQ-001–DQ-008 y materializar resultados Gold |

Las dependencias deben formar una única cadena verde **On success**:

```text
act_01_validate_bronze
  -> act_02_load_silver
  -> act_03_validate_silver
  -> act_04_build_lifecycle_state
  -> act_05_evaluate_dq_rules
```

## Decisiones de ejecución inicial

- No se configuran parámetros porque los notebooks actuales consumen el manifiesto Bronze como contrato.
- No se activa High concurrency: las cinco actividades tienen dependencias de datos y deben ejecutarse en orden.
- No se programa un horario hasta aprobar dos ejecuciones manuales consecutivas.
- La primera ejecución valida orquestación y lineage.
- La segunda ejecución valida idempotencia: debe conservar las mismas cardinalidades y no duplicar resultados.

## Evidencia requerida

1. Canvas guardado con las cinco actividades y cuatro dependencias verdes.
2. Historial de una ejecución con las cinco actividades en estado correcto.
3. Segunda ejecución correcta con los mismos conteos Gold.
4. Vista de lineage del workspace mostrando el pipeline, los notebooks y el Lakehouse.
