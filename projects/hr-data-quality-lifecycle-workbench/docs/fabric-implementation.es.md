# Implementación en Microsoft Fabric

## Propósito

Este documento registra las decisiones internas de implementación de la Fase 4. No sustituye la narrativa pública del proyecto ni el README final.

## Recursos y nomenclatura

| Recurso | Nombre definitivo | Propósito |
|---|---|---|
| Workspace | `HR Data Quality Workbench - DEV - MPR` | Entorno aislado de construcción y validación |
| Lakehouse | `lh_hr_data_quality_dev` | Almacenamiento y procesamiento analítico del caso |
| SQL analytics endpoint | Generado por Fabric para `lh_hr_data_quality_dev` | Consulta y validación SQL de tablas Delta |

Los nombres técnicos usan minúsculas y guiones bajos. El sufijo `dev` distingue el entorno de desarrollo y evita presentar el prototipo como una solución productiva.

## Patrón de arquitectura

Se utilizará un único Lakehouse con separación lógica Bronze, Silver y Gold:

- **Bronze:** copia inmutable de los CSV sintéticos, organizada por fuente y fecha de corte. Conserva nombres, valores y estructura de origen.
- **Silver:** tablas Delta normalizadas, tipadas y reconciliadas. Mantiene columnas de trazabilidad hacia archivo, fuente y fecha de carga.
- **Gold:** tablas Delta orientadas al consumo: excepciones de calidad, métricas, conciliación del ciclo de vida y dimensiones analíticas.

Esta decisión mantiene el alcance del portafolio manejable sin perder la separación conceptual entre capas. La promoción entre capas se realizará mediante procesos reproducibles, no con edición manual de registros.

## Estructura prevista

```text
lh_hr_data_quality_dev
├── Files
│   └── bronze
│       ├── global_hris
│       ├── local_hr_operations
│       └── organization_master
└── Tables
    ├── silver_*
    └── gold_*
```

Dentro de cada fuente Bronze se conservarán las particiones `snapshot_date=YYYY-MM-DD` o `extract_date=YYYY-MM-DD` provenientes del generador local.

## Controles iniciales

- El Lakehouse debe pertenecer al workspace de desarrollo aprobado.
- La creación debe generar un SQL analytics endpoint asociado.
- No se cargarán archivos hasta comprobar que el Lakehouse abre correctamente.
- No se crearán todavía modelos semánticos, reportes ni accesos adicionales.

## Estado de implementación

| Fecha | Componente | Resultado |
|---|---|---|
| 2026-10-13 | Workspace `HR Data Quality Workbench - DEV - MPR` | Creado y asignado a la capacidad de prueba |
| 2026-10-13 | Lakehouse `lh_hr_data_quality_dev` | Creado; `Files`, `Tables` y esquema `dbo` visibles |
| 2026-10-13 | SQL analytics endpoint | Provisionamiento automático confirmado desde el Lakehouse |
| 2026-10-13 | Bronze | 18 CSV y manifiesto cargados preservando fuente y partición |
| 2026-10-13 | Contrato Bronze | Notebook ejecutado: 18 archivos, 19,926 filas y estado `PASS` |
| 2026-10-13 | Silver | Tres tablas Delta y auditoría materializadas; conteos persistidos en estado `PASS` |
| 2026-10-13 | Gate Silver | 18 controles técnicos y funcionales ejecutados en estado `PASS` |
| 2026-10-13 | Estado de ciclo de vida Gold | 8,335 estados canónicos reconstruidos; conciliación por atributo validada en estado `PASS` |
| 2026-10-13 | Motor de reglas Gold | DQ-001–DQ-008 ejecutadas: 64,185 checks elegibles, 923 excepciones y seis scores conciliados en estado `PASS` |
| 2026-10-13 | Capa SQL de consumo | Cuatro vistas T-SQL creadas y validadas: 6 snapshots, 48 resultados de regla, 923 excepciones y score más reciente de 98.9 |
| 2026-10-13 | Orquestación | Dos ejecuciones consecutivas completadas: cinco de cinco actividades en estado `Correcto` en ambos runs |
| 2026-10-13 | Idempotencia | Reprocesamiento validado sin duplicados: 6 snapshots, 48 agregados de regla y 923 excepciones después del segundo run |
| 2026-10-13 | Lineage | Lakehouse, endpoint SQL, cinco notebooks y pipeline conectados en la vista del workspace |
| 2026-10-13 | Gate de Fase 4 | Revisión técnica en `PASS` y cierre aprobado por el owner del proyecto |

## Capa SQL de consumo

El endpoint SQL expone objetos de presentación sin duplicar ni modificar las tablas Delta administradas por Spark:

| Vista | Uso |
|---|---|
| `dbo.vw_dq_score_trend` | Serie histórica del score global por snapshot |
| `dbo.vw_dq_rule_performance` | Resultados agregados por regla y snapshot |
| `dbo.vw_dq_exception_register` | Registro analítico de excepciones detectadas |
| `dbo.vw_dq_latest_snapshot` | KPI global del corte más reciente |

Los scripts versionados están en `sql/01_create_gold_consumption_views.sql` y `sql/02_validate_gold_consumption_views.sql`. El segundo devuelve un único checkpoint técnico para comprobar existencia, cardinalidad y último score.

## Evidencia requerida

- Vista del workspace con el Lakehouse creado.
- Lakehouse Explorer mostrando `Files` y `Tables`.
- SQL analytics endpoint asociado visible en el workspace o desde el selector del Lakehouse.
- Resultado del checkpoint SQL con cuatro vistas y score más reciente de `98.9`.
