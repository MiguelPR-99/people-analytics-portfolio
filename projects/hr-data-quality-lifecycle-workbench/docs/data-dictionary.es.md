# Diccionario de datos raw — diseño previo a generación

Los nombres técnicos permanecen en inglés para coincidir con Python, Fabric, Dataverse y Power BI. Todos los identificadores son sintéticos.

Convenciones:

- Fechas en ISO `YYYY-MM-DD`.
- Timestamps en ISO 8601 y zona ficticia `America/Mexico_City`.
- Booleanos como `true` y `false` en Silver.
- Los archivos raw pueden contener valores faltantes o representaciones inválidas deliberadas.
- `SourceRecordID` siempre identifica la fila física, incluso cuando falta la llave de negocio.

## `global_hris/workers.csv`

**Grano:** una fila fuente por empleado y snapshot antes del tratamiento de calidad.

| Campo | Tipo objetivo | Nulo esperado | Descripción |
|---|---|---:|---|
| `SourceRecordID` | string | No | Identificador único de la fila raw |
| `SnapshotDate` | date | No | Fecha a la que corresponde el estado |
| `ExtractedAt` | datetime | No | Momento de creación del archivo |
| `EmployeeID` | string | No* | Identificador sintético `EMP-000001` |
| `EmploymentStatus` | string | No* | `PreHire`, `Active`, `Leave` o `Terminated` |
| `WorkerType` | string | No* | `Regular`, `Temporary` o `Intern` |
| `EmployeeGroup` | string | No* | `Salaried` o `Hourly` |
| `HireDate` | date | No* | Fecha de ingreso efectiva |
| `TerminationDate` | date | Sí | Obligatoria cuando el estado es `Terminated` |
| `LeaveStartDate` | date | Sí | Inicio de ausencia activa |
| `LeaveExpectedEndDate` | date | Sí | Fin esperado de ausencia |
| `ManagerEmployeeID` | string | Sí | Manager sintético; puede ser nulo en posiciones exentas |
| `PositionID` | string | No* | Posición asignada |
| `OrgUnitCode` | string | No* | Unidad organizacional informada por HRIS |
| `CostCenterCode` | string | No* | Centro de costo informado por HRIS |
| `LocationCode` | string | No* | Ubicación informada por HRIS |
| `CountryCode` | string | No* | `MX` en el MVP |
| `SourceUpdatedAt` | datetime | No* | Última modificación material del registro |
| `RecordConfirmedAt` | datetime | No* | Última confirmación de vigencia aunque no existan cambios |
| `RecordVersion` | integer | No | Versión técnica dentro de la fuente |

`*` El contrato espera el valor, pero el raw puede omitirlo deliberadamente para probar DQ-001.

## `local_hr_operations/lifecycle_events.csv`

**Grano:** un evento de ciclo de vida.

| Campo | Tipo objetivo | Nulo esperado | Descripción |
|---|---|---:|---|
| `SourceRecordID` | string | No | Identificador único de la fila raw |
| `ExtractBatchDate` | date | No | Fecha del lote incremental |
| `ExtractedAt` | datetime | No | Momento de extracción |
| `EventID` | string | No | Folio `EVT-YYYY-NNNNN` |
| `EmployeeID` | string | No | Persona sintética afectada |
| `EventType` | string | No | Tipo del catálogo de ciclo de vida |
| `EventStatus` | string | No | `Pending`, `Completed` o `Cancelled` |
| `EffectiveDate` | date | No | Fecha efectiva del evento |
| `CompletedAt` | datetime | Sí | Obligatoria si `EventStatus = Completed` |
| `PreviousEmploymentStatus` | string | Sí | Estado anterior, cuando aplica |
| `NewEmploymentStatus` | string | Sí | Estado posterior, cuando aplica |
| `PreviousManagerEmployeeID` | string | Sí | Manager anterior |
| `NewManagerEmployeeID` | string | Sí | Manager posterior |
| `PreviousPositionID` | string | Sí | Posición anterior |
| `NewPositionID` | string | Sí | Posición posterior |
| `PreviousOrgUnitCode` | string | Sí | Unidad anterior |
| `NewOrgUnitCode` | string | Sí | Unidad posterior |
| `PreviousCostCenterCode` | string | Sí | Centro anterior |
| `NewCostCenterCode` | string | Sí | Centro posterior |
| `PreviousLocationCode` | string | Sí | Ubicación anterior |
| `NewLocationCode` | string | Sí | Ubicación posterior |
| `SourceUpdatedAt` | datetime | No | Última actualización del evento |
| `RecordVersion` | integer | No | Versión del evento dentro de la fuente |

Los campos `Previous*` y `New*` son nulos cuando el evento no modifica ese atributo. No se incluirán comentarios abiertos.

## `organization_master/positions.csv`

**Grano:** una versión efectiva de posición visible en el snapshot.

| Campo | Tipo objetivo | Nulo esperado | Descripción |
|---|---|---:|---|
| `SourceRecordID` | string | No | Identificador único de la fila raw |
| `SnapshotDate` | date | No | Corte de referencia |
| `ExtractedAt` | datetime | No | Momento de extracción |
| `PositionID` | string | No | Posición sintética `POS-000001` |
| `PositionStatus` | string | No | `Active` o `Inactive` |
| `PositionFamily` | string | No | Familia genérica de trabajo |
| `OrgUnitCode` | string | No | Unidad organizacional válida |
| `OrgUnitName` | string | No | Nombre descriptivo |
| `FunctionGroup` | string | No | Grupo funcional agregado |
| `CostCenterCode` | string | No | Centro de costo válido |
| `CostCenterName` | string | No | Nombre sintético del centro |
| `LocationCode` | string | No | Ubicación válida |
| `LocationName` | string | No | Nombre de la ubicación |
| `LocationType` | string | No | Plant, Engineering and Service Center, Corporate Office o Field Service Hub |
| `CountryCode` | string | No | `MX` |
| `ManagerEligibleFlag` | boolean | No | La posición puede actuar como manager |
| `ManagerRequiredFlag` | boolean | No | El ocupante necesita manager; `false` para posiciones superiores exentas |
| `MaxIncumbents` | integer | No | Capacidad máxima permitida |
| `ValidFrom` | date | No | Inicio de vigencia |
| `ValidTo` | date | Sí | Fin inclusivo; nulo significa sin fecha final conocida |
| `SourceUpdatedAt` | datetime | No | Última actualización de la referencia |
| `RecordVersion` | integer | No | Versión técnica de la posición |

## Metadatos Bronze

Estos campos son añadidos por la ingesta, no por los CSV:

| Campo | Tipo | Descripción |
|---|---|---|
| `IngestionRunID` | string | Ejecución que recibió el archivo |
| `IngestedAt` | datetime | Timestamp de ingesta |
| `SourceFilePath` | string | Ruta relativa del archivo |
| `SourceFileHash` | string | SHA-256 del archivo |
| `SourceSystem` | string | `GHRIS`, `LHROPS` u `ORGMD` |
| `BatchDate` | date | Fecha identificadora del lote |

## Tablas Silver

Las tablas `silver_worker_snapshot`, `silver_lifecycle_event` y `silver_position_reference` conservan todas las columnas tipadas de su archivo fuente y añaden los siguientes campos técnicos:

| Campo | Tipo | Descripción |
|---|---|---|
| `SourceFilePath` | string | Ruta relativa exacta dentro de Bronze |
| `SourceFileHash` | string | SHA-256 registrado en el manifiesto |
| `SourceSystem` | string | Código de la fuente |
| `BatchDate` | date | Partición temporal normalizada |
| `IngestionRunID` | string | Identificador idempotente de la carga |
| `IngestedAt` | timestamp | Momento en que la carga fue materializada |
| `RecordContentHash` | string | Hash determinista del contenido fuente normalizado |
| `BusinessKeyRowCount` | long | Número de filas para la llave de negocio dentro del corte |
| `IsDuplicateBusinessKey` | boolean | Indica duplicidad elegible sin eliminar registros |
| `CanonicalRank` | integer | Orden determinista usado para seleccionar una fila canónica |
| `IsCanonical` | boolean | Fila utilizada por reglas posteriores que requieren estado único |

La selección canónica prioriza la versión más alta, la actualización más reciente y finalmente `SourceRecordID`. Una fila no canónica permanece en Silver para que DQ-002 pueda explicarla y rastrearla.

### `silver_load_audit`

**Grano:** una tabla Silver por ejecución de ingesta.

| Campo | Tipo | Descripción |
|---|---|---|
| `IngestionRunID` | string | Ejecución validada |
| `SourceSystem` | string | Fuente procesada |
| `TargetTable` | string | Tabla Delta materializada |
| `SourceFileCount` | integer | Archivos incluidos |
| `ExpectedRows` | long | Filas esperadas según manifiesto |
| `PersistedRows` | long | Filas verificadas después de escribir |
| `LoadStatus` | string | `PASS` cuando los controles coinciden |
| `AuditedAt` | timestamp | Momento de auditoría |

## `gold_employee_lifecycle_state`

**Grano:** un empleado con llave informada por fecha de snapshot.

| Campo | Tipo | Descripción |
|---|---|---|
| `RunID` | string | Ejecución analítica que reconstruyó el estado |
| `SnapshotDate` | date | Corte evaluado |
| `EmployeeID` | string | Empleado sintético |
| `Observed*` | string | Valor canónico observado en HRIS para cada atributo reconciliado |
| `Reconstructed*` | string | Valor reconstruido desde los eventos completados aplicables |
| `*EventID` | string | Evento determinante específico del atributo |
| `*EventType` | string | Tipo del evento determinante |
| `*EffectiveDate` | date | Fecha efectiva del evento determinante |
| `*CompletedAt` | timestamp | Finalización del evento determinante |
| `*BusinessDaysSinceCompletion` | integer | Días hábiles hasta el snapshot para aplicar tolerancia |
| `MismatchFields` | array<string> | Todos los atributos observados que difieren del estado reconstruido |
| `ActionableMismatchFields` | array<string> | Diferencias cuya tolerancia de dos días ya venció |
| `ReconciliationEligibleFlag` | boolean | Existen eventos suficientes para reconstruir los seis atributos |
| `ToleranceAppliedFlag` | boolean | Al menos una diferencia quedó dentro de la tolerancia |
| `ReconciliationPassFlag` | boolean | No existen diferencias accionables |
| `WorkerSourceRecordID` | string | Fila HRIS canónica utilizada |
| `WorkerSourceFilePath` | string | Archivo HRIS de origen |
| `EvaluatedAt` | timestamp | Momento de evaluación |

La reconstrucción es semántica por atributo: por ejemplo, `LeaveStart` puede actualizar `EmploymentStatus`, pero no sustituye una asignación organizacional determinada por `Transfer`. Esto evita tratar el evento más reciente como si necesariamente reemplazara el estado completo.

## `gold_dq_rule_result`

**Grano:** un check elegible o no elegible de una regla para un registro/grupo y ejecución.

| Campo | Tipo | Descripción |
|---|---|---|
| `RunID` | string | Ejecución de reglas |
| `RuleResultID` | string | Identificador único del resultado |
| `RuleCode` | string | `DQ-001`–`DQ-008` |
| `RuleName` | string | Nombre legible de la regla |
| `QualityDimension` | string | Dimensión de calidad evaluada |
| `SnapshotDate` | date | Corte evaluado |
| `SourceSystem` | string | Fuente principal evaluada |
| `BusinessKey` | string | Empleado, posición o grupo evaluado |
| `FieldScope` | string | Campo o conjunto de campos |
| `EligibleFlag` | boolean | El resultado entra al denominador |
| `PassFlag` | boolean | Aprobación; nulo si no es elegible |
| `Severity` | string | Severidad aplicable |
| `SeverityWeight` | integer | 4, 3, 2 o 1 |
| `OperationalSeverity` | string | Severidad operativa de la excepción concreta |
| `SlaBusinessDays` | integer | Plazo objetivo en días hábiles |
| `OwnerDomain` | string | Dominio funcional responsable |
| `ObservedValue` | string | Representación segura y estructurada |
| `ExpectedCondition` | string | Condición que debía cumplirse |
| `EvaluatedAt` | datetime | Momento de evaluación |

## `gold_dq_exception`

**Grano:** un resultado fallido de regla.

| Campo | Tipo | Descripción |
|---|---|---|
| `ExceptionInstanceID` | string | Instancia única dentro del run |
| `ExceptionFingerprint` | string | Identidad estable dentro del mismo corte |
| `RecurrenceKey` | string | Identidad comparable entre cortes |
| `RunID` | string | Ejecución de origen |
| `RuleResultID` | string | Resultado fallido correspondiente |
| `RuleCode` | string | Regla que falló |
| `RuleName` | string | Nombre legible de la regla |
| `QualityDimension` | string | Dimensión de calidad evaluada |
| `SnapshotDate` | date | Corte evaluado |
| `SourceSystem` | string | Fuente principal |
| `BusinessKey` | string | Registro o grupo afectado |
| `FieldScope` | string | Campo afectado |
| `OperationalSeverity` | string | Critical, High, Medium o Low |
| `SlaBusinessDays` | integer | Plazo objetivo en días hábiles |
| `OwnerDomain` | string | Propietario funcional |
| `ObservedValue` | string | Valor seguro observado |
| `ExpectedCondition` | string | Regla esperada |
| `EvaluatedAt` | datetime | Momento de evaluación y detección |

El estado operativo, asignado, aprobación, comentarios y cierre no pertenecen a esta tabla. Se almacenarán posteriormente en Dataverse y conservarán una referencia a `ExceptionInstanceID` y `RecurrenceKey`.

