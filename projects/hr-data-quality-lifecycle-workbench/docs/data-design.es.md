# Diseño de datos — HR Data Quality & Employee Lifecycle Workbench

## 1. Escenario cuantitativo

La simulación representa 18 meses de operación, del 1 de enero de 2025 al 30 de junio de 2026, con seis cortes trimestrales. La población comienza con aproximadamente 1,200 empleados activos y termina cerca de 1,320; durante el periodo participan alrededor de 1,500 identificadores sintéticos debido a altas y bajas.

Se utilizarán cuatro ubicaciones ficticias de México:

- Bajio Manufacturing Plant.
- Queretaro Engineering and Service Center.
- Mexico City Corporate Office.
- Monterrey Field Service Hub.

La estructura funcional cubre manufactura, ingeniería, servicio de campo, ejecución de proyectos, supply chain, comercial y funciones corporativas. El diseño busca reflejar complejidad industrial y energética sin representar la organización interna de Siemens Energy.

## 2. Por qué seis cortes trimestrales

Un único snapshot permitiría detectar errores, pero no demostraría recurrencia, mejora ni ingesta incremental. Un archivo diario o mensual elevaría el volumen de artefactos sin añadir suficiente valor al MVP.

Los seis cortes trimestrales permiten:

- comparar calidad a través del tiempo;
- distinguir una excepción nueva de una recurrente;
- reconstruir el estado laboral a una fecha;
- probar cargas incrementales e idempotentes;
- mostrar el efecto de una intervención controlada;
- mantener un volumen razonable para GitHub y Fabric Trial.

## 3. Fuentes

### 3.1 Global HRIS worker snapshot (`GHRIS`)

**Grano raw:** una fila fuente por empleado y fecha de snapshot, antes de tratar duplicados.

Contiene el estado laboral vigente y la asignación organizacional que el HRIS global considera oficial. Cada corte se entrega como un archivo completo; Fabric lo ingiere como un nuevo lote sin modificar snapshots anteriores.

```text
data/raw/global_hris/
└─ snapshot_date=YYYY-MM-DD/
   └─ workers.csv
```

### 3.2 Local employee lifecycle events (`LHROPS`)

**Grano raw:** un evento de ciclo de vida de un empleado.

Contiene eventos completados, pendientes o cancelados. Cada extracción trimestral incorpora eventos creados o actualizados desde la extracción anterior. Para reconstruir el estado solo se aplican eventos completados con fecha efectiva igual o anterior al corte.

```text
data/raw/local_hr_operations/
└─ extract_date=YYYY-MM-DD/
   └─ lifecycle_events.csv
```

### 3.3 Organization master data (`ORGMD`)

**Grano raw:** una versión efectiva de una posición visible en la fecha de snapshot.

La fuente reúne la posición, unidad, función, centro de costo, ubicación, capacidad máxima y elegibilidad como manager. Es la referencia contra la que se valida la asignación del empleado.

```text
data/raw/organization_master/
└─ snapshot_date=YYYY-MM-DD/
   └─ positions.csv
```

## 4. Identificadores y llaves

- `EmployeeID`: identificador sintético estable, formato `EMP-000001`.
- `PositionID`: identificador sintético estable, formato `POS-000001`.
- `EventID`: folio sintético único, formato `EVT-YYYY-NNNNN`.
- `SourceRecordID`: identifica la fila exacta recibida; permite conservar duplicados y rastrear el origen.
- `SnapshotDate` o `ExtractBatchDate`: identifica el lote de origen.
- `RunID`: identifica una ejecución de reglas en Fabric.
- `ExceptionInstanceID`: identifica una falla específica en una ejecución.
- `ExceptionFingerprint`: agrupa la misma combinación lógica de registro, regla y campo entre ejecuciones.

La clave empresarial del snapshot limpio será `SnapshotDate + EmployeeID`. La clave raw incluirá `SourceRecordID` para que una duplicación no se pierda durante la ingesta.

## 5. Semántica temporal

- `SnapshotDate` responde: “¿qué afirmaba la fuente al cierre de esta fecha?”.
- `EffectiveDate` indica cuándo un evento debe surtir efecto.
- `CompletedAt` indica cuándo el proceso local se marcó como completado.
- `SourceUpdatedAt` indica la última actualización en la fuente.
- `ExtractedAt` indica cuándo se produjo el archivo sintético.
- `ValidFrom` y `ValidTo` delimitan la vigencia de una posición; `ValidTo` es inclusiva.

Para reconciliar eventos con un snapshot se utiliza el último evento por empleado que cumpla:

1. `EventStatus = Completed`.
2. `EffectiveDate <= SnapshotDate`.
3. Si dos eventos comparten fecha efectiva, gana el mayor `CompletedAt` y después el mayor `EventID` como desempate determinista.

Los eventos futuros, pendientes y cancelados permanecen visibles para auditoría, pero no cambian el estado reconstruido.

## 6. Ciclo de vida

```text
PreHireCreated → Hire → Active
                         ├─ Transfer / Promotion / ManagerChange
                         ├─ LocationChange / CostCenterChange
                         ├─ LeaveStart → Leave → LeaveEnd → Active
                         └─ Termination → Terminated
```

Los cambios organizacionales pueden ocurrir en una misma fecha. El generador asignará una secuencia determinista y la reconciliación aplicará todos los eventos efectivos antes de comparar el estado final.

## 7. Capas analíticas

### Bronze

Preserva cada archivo y cada fila tal como fue recibida. Añade solamente metadatos técnicos:

- ruta del archivo;
- nombre del archivo;
- timestamp de ingesta;
- hash del archivo;
- identificador del lote.

No corrige duplicados, valores faltantes ni códigos inválidos.

### Silver

Normaliza tipos, mayúsculas, fechas y dominios, sin ocultar fallas de negocio. Tablas previstas:

- `silver_worker_snapshot`
- `silver_lifecycle_event`
- `silver_position_reference`

Las filas duplicadas permanecen detectables mediante conteos y banderas. Una tabla Silver puede marcar una fila como no canónica, pero no eliminar silenciosamente el registro raw.

### Gold

- `gold_employee_lifecycle_state`: estado reconstruido por empleado y corte.
- `gold_dq_rule_result`: una evaluación elegible por regla y registro, aprobada o fallida.
- `gold_dq_exception`: únicamente evaluaciones fallidas.
- `gold_dq_score_snapshot`: métricas agregadas por corte, regla, dimensión y fuente.
- `gold_dq_run_audit`: control de cada ejecución, entradas, totales y resultado.

## 8. Grano de la evaluación

La unidad base es un **check elegible de una regla sobre un registro o grupo de registros en un corte**.

Ejemplos:

- DQ-001 evalúa una fila de empleado.
- DQ-002 evalúa el grupo `SnapshotDate + EmployeeID`.
- DQ-005 evalúa el grupo `SnapshotDate + PositionID`.
- DQ-007 evalúa un empleado contra su estado reconstruido al corte.

Una regla no aplicable produce `EligibleFlag = false`; no cuenta como aprobado ni entra al denominador del score.

## 9. Excepción versus caso de remediación

Una excepción es evidencia analítica inmutable de que una regla falló en una ejecución. Un caso de remediación es el objeto operativo editable en Dataverse.

```text
Excepción Fabric (inmutable)
        ↓ referencia
Caso Dataverse (asignación, estado, comentarios, aprobación)
        ↓
Corrección simulada en una fuente posterior
        ↓
Nueva evaluación Fabric
        ↓
Regla aprobada y score actualizado
```

Cerrar un caso no cambia retroactivamente el resultado del snapshot ni el score. La mejora solo aparece cuando una extracción posterior contiene el dato corregido.

## 10. Patrones controlados

### Reorganización Q3 2025

Ingeniería, ejecución de proyectos y servicio de campo tendrán cambios concentrados. Una parte de los eventos locales llegará antes que la actualización global, elevando temporalmente fallas de manager y reconciliación.

### Ola de onboarding Q1 2026

Bajío y Monterrey tendrán más pre-hires y altas. Se incrementarán de forma controlada las omisiones de campos requeridos y la doble ocupación temporal de posiciones.

### Intervención de calidad Q2 2026

Se simulará una mejora del formulario y del seguimiento de interfaces desde el 1 de abril de 2026. El último corte deberá mostrar menor incompletitud y menor proporción de registros desactualizados.

Los patrones se validarán con pruebas estadísticas simples; no se redactarán como hallazgos definitivos hasta ejecutar y revisar el dataset.

## 11. Volumen esperado

| Artefacto | Orden de magnitud esperado |
|---|---:|
| Empleados distintos | ~1,500 |
| Empleados activos al inicio | ~1,200 |
| Empleados activos al corte final | ~1,320 |
| Filas de snapshots HRIS | 7,000–8,500 |
| Eventos de ciclo de vida | ~2,800 |
| Posiciones | ~1,450 |
| Filas de referencia por snapshots | 7,500–9,000 |
| Excepciones totales | Se fijará después del prototipo, dentro de los umbrales definidos |

Los rangos permiten variación por altas, bajas y cambios efectivos. El manifiesto final contendrá los totales exactos.

## 12. Contrato incremental

- Cada lote tiene fecha y hash.
- Reprocesar el mismo lote no duplica Bronze ni Gold.
- Un lote nuevo no modifica archivos anteriores.
- Una actualización de evento conserva el mismo `EventID` y eleva `RecordVersion`.
- Gold se puede reconstruir completamente desde Bronze.
- El watermark operativo será la combinación de fecha de lote y hash del archivo, no únicamente el timestamp del sistema.

