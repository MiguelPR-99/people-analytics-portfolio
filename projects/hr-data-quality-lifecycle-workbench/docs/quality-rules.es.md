# Matriz de reglas de calidad

## 1. Principios

- Una regla debe ser determinista, explicable y reproducible.
- Cada excepción debe indicar qué falló, qué se esperaba y quién es responsable del dominio.
- Las reglas evalúan calidad del dato, no calidad o desempeño de una persona.
- Un registro puede fallar varias reglas; cada falla conserva su propio identificador.
- Los casos cerrados en Dataverse no alteran el resultado histórico de Fabric.

## 2. Severidad y SLA

| Severidad | Peso del score | Objetivo de resolución | Uso previsto |
|---|---:|---:|---|
| Critical | 4 | 1 día hábil | Impide identificar o reconstruir correctamente el estado laboral |
| High | 3 | 3 días hábiles | Compromete estructura, responsable o asignación organizacional |
| Medium | 2 | 5 días hábiles | Reduce oportunidad o confiabilidad sin bloquear el registro completo |
| Low | 1 | 10 días hábiles | Mejora de calidad con impacto operativo limitado |

El SLA comienza cuando se crea el caso de remediación, no cuando se produjo originalmente el dato incorrecto. El aging analítico de la excepción y el aging operativo del caso se reportarán por separado.

## 3. Reglas del MVP

### DQ-001 — Required fields complete

- **Dimensión:** Completeness.
- **Grano:** fila de `GHRIS`.
- **Elegibilidad:** todas las filas.
- **Condición:** `EmployeeID`, `EmploymentStatus`, `WorkerType`, `EmployeeGroup`, `HireDate`, `PositionID`, `OrgUnitCode`, `CostCenterCode`, `LocationCode` y `SourceUpdatedAt` deben estar informados, con excepciones dependientes del estado.
- **Dependencias de estado:** `ManagerEmployeeID` puede faltar únicamente en posiciones explícitamente exentas; `TerminationDate` es obligatoria para `Terminated`; fechas de ausencia son obligatorias para `Leave`.
- **Severidad:** High; sube a Critical si falta `EmployeeID` o `EmploymentStatus`.
- **Propietario:** HR Operations Data.
- **Salida esperada:** lista de campos faltantes en forma estructurada, sin texto libre.

### DQ-002 — Employee snapshot key unique

- **Dimensión:** Uniqueness.
- **Grano:** grupo `SnapshotDate + EmployeeID`.
- **Elegibilidad:** filas con `EmployeeID` informado.
- **Condición:** debe existir exactamente una fila por empleado y snapshot.
- **Severidad:** Critical.
- **Propietario:** HRIS Integration.
- **Salida esperada:** cantidad de filas, `SourceRecordID` implicados y versiones observadas.
- **Tratamiento:** Bronze conserva todas las filas; Silver determina una fila canónica solo para continuar otras evaluaciones y marca la ambigüedad.

### DQ-003 — Manager reference valid and eligible

- **Dimensión:** Referential Integrity.
- **Grano:** empleado por snapshot.
- **Elegibilidad:** `PreHire`, `Active` o `Leave`, salvo posiciones exentas de manager.
- **Condición:** el manager debe existir en el mismo snapshot, estar `Active` o `Leave`, no ser el propio empleado y ocupar una posición con `ManagerEligibleFlag = true`.
- **Severidad:** High.
- **Propietario:** Organization Management.
- **Salida esperada:** manager observado y motivo estructurado: `Missing`, `NotFound`, `SelfReference`, `Inactive` o `NotEligible`.

### DQ-004 — Organizational assignment valid as of snapshot

- **Dimensión:** Validity.
- **Grano:** empleado por snapshot.
- **Elegibilidad:** filas con `PositionID` informado.
- **Condición:** la posición debe existir y estar vigente; `OrgUnitCode`, `CostCenterCode`, `LocationCode` y `CountryCode` deben coincidir con la versión efectiva de esa posición.
- **Severidad:** High.
- **Propietario:** Organization Management.
- **Salida esperada:** atributo discrepante, valor observado, valor de referencia y vigencia aplicable.

### DQ-005 — Position occupancy within allowed capacity

- **Dimensión:** Consistency.
- **Grano:** grupo `SnapshotDate + PositionID`.
- **Elegibilidad:** posiciones activas y empleados `PreHire`, `Active` o `Leave`.
- **Condición:** la cantidad de ocupantes no puede exceder `MaxIncumbents`.
- **Severidad:** High.
- **Propietario:** Organization Management.
- **Salida esperada:** capacidad permitida, ocupación observada y empleados sintéticos implicados.
- **Nota:** las posiciones colectivas pueden tener `MaxIncumbents > 1`; no se asumirá que toda posición es de ocupante único.

### DQ-006 — Employment dates temporally coherent

- **Dimensión:** Temporal Coherence.
- **Grano:** empleado por snapshot.
- **Elegibilidad:** todas las filas canónicas.
- **Condición:** `HireDate <= SnapshotDate`; `TerminationDate >= HireDate`; un empleado `Terminated` debe tener `TerminationDate <= SnapshotDate`; un empleado `Active` o `Leave` no debe tener una terminación efectiva anterior o igual al snapshot; las fechas de ausencia deben respetar inicio y fin.
- **Severidad:** Critical.
- **Propietario:** HR Operations Data.
- **Salida esperada:** código de contradicción temporal y fechas involucradas.

### DQ-007 — HRIS state reconciles to latest completed lifecycle event

- **Dimensión:** Cross-system Consistency.
- **Grano:** empleado por snapshot.
- **Elegibilidad:** empleados con al menos un evento completado efectivo al corte.
- **Condición:** después de aplicar la secuencia de eventos, `EmploymentStatus`, `ManagerEmployeeID`, `PositionID`, `OrgUnitCode`, `CostCenterCode` y `LocationCode` deben coincidir con `GHRIS`.
- **Tolerancia:** se permiten dos días hábiles desde la finalización del evento para la sincronización. La discrepancia se marca cuando el corte ocurre después de esa tolerancia.
- **Severidad:** Critical para estado laboral o terminación; High para atributos organizacionales.
- **Propietario:** HRIS Integration.
- **Salida esperada:** atributo, valor reconstruido, valor HRIS, evento determinante y días transcurridos.

### DQ-008 — Source record updated within freshness threshold

- **Dimensión:** Timeliness.
- **Grano:** empleado por snapshot.
- **Elegibilidad:** `PreHire`, `Active` o `Leave`.
- **Condición:** `SourceUpdatedAt` no puede ser futuro y debe encontrarse dentro de los cinco días hábiles anteriores al snapshot, excepto cuando el registro no tuvo cambios y existe una confirmación de vigencia en el lote. Para el MVP, el generador producirá una marca `RecordConfirmedAt` para distinguir ambos casos.
- **Severidad:** Medium.
- **Propietario:** HRIS Integration.
- **Salida esperada:** última actualización, última confirmación y días hábiles de antigüedad.

## 4. Data Quality Score

El score mide resultados de reglas, no casos de remediación:

```text
DQ Score = 100 × Σ(Peso de severidad × PassFlag)
                 ───────────────────────────────────
                 Σ(Peso de severidad de checks elegibles)
```

Donde:

- `PassFlag = 1` si el check elegible aprueba y `0` si falla.
- Un check no elegible queda fuera de ambos sumatorios.
- Los pesos son Critical 4, High 3, Medium 2 y Low 1.
- El resultado se redondea a un decimal.

Se calcularán scores por snapshot, fuente, dimensión, regla, ubicación y función. Para evitar interpretaciones incorrectas, siempre se mostrarán junto con:

- checks elegibles;
- checks fallidos;
- registros evaluados;
- registros con al menos una excepción.

Un score alto no implica ausencia de problemas críticos. Por ello, el tablero mostrará también el número de excepciones Critical abiertas.

## 5. Identidad y recurrencia de excepciones

### `ExceptionInstanceID`

Identificador único de la falla en una ejecución. Cambia en cada `RunID`.

### `ExceptionFingerprint`

Hash determinista de:

```text
RuleCode | SourceSystem | SnapshotDate | BusinessKey | FieldScope
```

Permite que una recarga idempotente reconozca la misma excepción. Para medir recurrencia entre snapshots se utilizará un segundo agrupador:

```text
RecurrenceKey = RuleCode | SourceSystem | BusinessKey | FieldScope
```

Así se distingue una falla duplicada dentro del mismo corte de una falla que reaparece en varios cortes.

## 6. Casos mínimos de prueba

Cada regla deberá incluir:

- **Caso positivo:** dato válido que aprueba.
- **Caso negativo:** anomalía deliberada que falla.
- **Caso de borde:** condición válida cercana al límite o excepción funcional documentada.
- **Caso no elegible:** cuando aplique, registro excluido correctamente del denominador.

Ejemplos de borde importantes:

- posición superior exenta de manager;
- ausencia que termina exactamente en la fecha de snapshot;
- evento completado dentro de la tolerancia de dos días;
- posición colectiva ocupada exactamente hasta `MaxIncumbents`;
- terminación efectiva exactamente en el corte;
- registro sin cambios, pero confirmado dentro del umbral de frescura.

## 7. Controles de reconciliación

- El número de filas fallidas en `gold_dq_rule_result` debe coincidir exactamente con `gold_dq_exception`.
- El score agregado debe poder recalcularse desde resultados de regla sin tolerancia.
- Ningún `ExceptionInstanceID` puede repetirse.
- Una recarga del mismo lote debe producir los mismos fingerprints y no crear casos duplicados.
- Toda anomalía inyectada por el generador debe aparecer en el manifiesto y mapear a una regla.
- Toda excepción publicada a Dataverse debe conservar `RunID`, `ExceptionInstanceID` y `RecurrenceKey`.

