# Diseño de Dataverse — Fase 5

## Objetivo

Separar la evidencia analítica inmutable de Fabric de la gestión transaccional editable. Dataverse almacenará referencias de excepción, asignación, estados, actividades, evidencia y decisiones; nunca modificará el histórico Gold.

## Solución y publisher

| Propiedad | Valor |
|---|---|
| Solución | `HR Data Quality & Lifecycle Workbench` |
| Nombre único | `HRDataQualityLifecycleWorkbench` |
| Versión inicial | `1.0.0.0` |
| Publisher | `Miguel PR — People Analytics` |
| Nombre único del publisher | `MiguelPRPeopleAnalytics` |
| Prefijo | `mprpa` |
| Prefijo de valores Choice | `55744` |

Todos los componentes se crearán dentro de esta solución no administrada. El prefijo propio evita los nombres aleatorios del publisher predeterminado y permite exportar la solución posteriormente.

## Modelo lógico

```text
DQ Exception Reference (inmutable en la app)
        1
        │
        └── N DQ Remediation Case
                    │
                    ├── N DQ Case Activity
                    └── N DQ Case Evidence

DQ Status ──< DQ Remediation Case
     │
     └──< DQ Status Transition >── DQ Status
```

## Tablas

### `mprpa_dqexceptionreference` — DQ Exception Reference

Propiedad: **Organization-owned**. Contiene una copia de referencia de la excepción publicada desde Fabric; los usuarios de la aplicación no podrán editarla.

| Columna | Tipo | Requerida | Uso |
|---|---|---:|---|
| `Exception Label` | Text 200, primary name | Sí | Etiqueta legible para búsquedas |
| `Exception Instance ID` | Text 64 | Sí | Identificador de Gold y clave alternativa |
| `Exception Fingerprint` | Text 64 | Sí | Identidad estable dentro del corte |
| `Recurrence Key` | Text 64 | Sí | Agrupación entre snapshots |
| `Fabric Run ID` | Text 100 | Sí | Ejecución analítica de origen |
| `Rule Code` | Text 20 | Sí | `DQ-001`–`DQ-008` |
| `Rule Name` | Text 200 | Sí | Nombre legible de la regla |
| `Quality Dimension` | Text 100 | Sí | Dimensión de calidad |
| `Snapshot Date` | Date only | Sí | Corte analítico |
| `Source System` | Text 50 | Sí | Fuente evaluada |
| `Business Key` | Text 200 | Sí | Empleado, posición o grupo |
| `Field Scope` | Text 200 | Sí | Campo o conjunto de campos |
| `Operational Severity` | Choice global | Sí | Critical, High, Medium o Low |
| `SLA Business Days` | Whole number | Sí | Plazo objetivo |
| `Owner Domain` | Text 100 | Sí | Dominio funcional responsable |
| `Observed Value` | Multiline text 4,000 | Sí | Valor seguro observado |
| `Expected Condition` | Multiline text 2,000 | Sí | Condición esperada |
| `Fabric Evaluated At` | Date and time | Sí | Momento de detección en Fabric |

Clave alternativa: `AK_DQExceptionReference_ExceptionInstanceID` sobre `Exception Instance ID`.

### `mprpa_dqremediationcase` — DQ Remediation Case

Propiedad: **User or team-owned**. Es el objeto asignable y editable del workbench.

| Columna | Tipo | Requerida | Uso |
|---|---|---:|---|
| `Case Title` | Text 200, primary name | Sí | Descripción breve |
| `Case Number` | Autonumber `DQCASE-{SEQNUM:6}` | Sí | Folio operativo |
| `Exception Reference` | Lookup | Sí | Relación con la excepción inmutable |
| `Exception Instance ID` | Text 64 | Sí | Copia bloqueada y clave alternativa |
| `Recurrence Key` | Text 64 | Sí | Copia bloqueada para recurrencia |
| `Case Status` | Lookup a DQ Status | Sí | Estado operativo vigente |
| `SLA Start At` | Date and time | Sí | Inicio del aging operativo |
| `Due At` | Date and time | No | Vencimiento calculado posteriormente por flujo |
| `Triage Summary` | Multiline text 2,000 | No | Diagnóstico inicial |
| `Resolution Type` | Choice global | No | Corrected, Not an Issue o Waived |
| `Resolution Summary` | Multiline text 4,000 | No | Justificación del cierre |
| `Evidence Complete` | Yes/No | Sí | Control previo a aprobación |
| `Approval Outcome` | Choice global | No | Pending, Approved o Rejected |
| `Resolved At` | Date and time | No | Marca temporal de resolución |
| `Source Correction State` | Choice global | Sí | Not Checked, Still Failing o Confirmed Later |
| `Source Correction Snapshot` | Date only | No | Corte que confirmó la corrección |
| `Last Transition At` | Date and time | Sí | Último cambio de estado |

Se utiliza la columna estándar `Owner` para la asignación. Clave alternativa: `AK_DQRemediationCase_ExceptionInstanceID` sobre `Exception Instance ID`, de modo que una misma excepción no cree dos casos.

### `mprpa_dqcaseactivity` — DQ Case Activity

Propiedad: **User or team-owned**.

| Columna | Tipo | Requerida | Uso |
|---|---|---:|---|
| `Activity Title` | Text 200, primary name | Sí | Resumen legible |
| `Activity Number` | Autonumber `DQACT-{SEQNUM:7}` | Sí | Folio de actividad |
| `Remediation Case` | Lookup | Sí | Caso relacionado |
| `Activity Type` | Choice global | Sí | Comment, Assignment, Status Change, Evidence Request, Approval, Escalation o Reopen |
| `From Status` | Lookup a DQ Status | No | Estado previo |
| `To Status` | Lookup a DQ Status | No | Estado posterior |
| `Activity Note` | Multiline text 4,000 | No | Comentario o justificación |
| `Occurred At` | Date and time | Sí | Momento de la actividad |
| `System Generated` | Yes/No | Sí | Distingue usuario de automatización |

`Created By` conserva automáticamente al autor Dataverse.

### `mprpa_dqcaseevidence` — DQ Case Evidence

Propiedad: **User or team-owned**.

| Columna | Tipo | Requerida | Uso |
|---|---|---:|---|
| `Evidence Title` | Text 200, primary name | Sí | Nombre legible |
| `Evidence Number` | Autonumber `DQEVD-{SEQNUM:7}` | Sí | Folio de evidencia |
| `Remediation Case` | Lookup | Sí | Caso relacionado |
| `Evidence Type` | Choice global | Sí | File, Link, Screenshot o Data Reference |
| `Evidence File` | File, máximo 10 MB | No | Archivo seguro de demostración |
| `Evidence URL` | URL 500 | No | Referencia externa permitida |
| `Evidence Note` | Multiline text 2,000 | No | Contexto de la evidencia |
| `Supports Closure` | Yes/No | Sí | Indica si satisface el requisito de cierre |

Nunca se almacenarán documentos reales de empleados; toda evidencia será sintética.

### `mprpa_dqstatus` — DQ Status

Propiedad: **Organization-owned**.

| Columna | Tipo | Requerida | Uso |
|---|---|---:|---|
| `Status Name` | Text 100, primary name | Sí | Etiqueta visible |
| `Status Code` | Text 50 | Sí | Clave alternativa estable |
| `Sequence` | Whole number | Sí | Orden de presentación |
| `Initial` | Yes/No | Sí | Estado inicial |
| `Terminal` | Yes/No | Sí | Estado de cierre |
| `Requires Evidence` | Yes/No | Sí | Evidencia obligatoria al entrar |
| `Requires Comment` | Yes/No | Sí | Comentario obligatorio al entrar |
| `Requires Approval` | Yes/No | Sí | Aprobación obligatoria al entrar |
| `Available` | Yes/No | Sí | Estado utilizable |

Clave alternativa: `AK_DQStatus_StatusCode` sobre `Status Code`.

### `mprpa_dqstatustransition` — DQ Status Transition

Propiedad: **Organization-owned**. Es la lista blanca de cambios válidos.

| Columna | Tipo | Requerida | Uso |
|---|---|---:|---|
| `Transition Name` | Text 150, primary name | Sí | Etiqueta legible |
| `Transition Code` | Text 100 | Sí | Clave alternativa estable |
| `From Status` | Lookup a DQ Status | Sí | Origen permitido |
| `To Status` | Lookup a DQ Status | Sí | Destino permitido |
| `Requires Evidence` | Yes/No | Sí | Requisito adicional |
| `Requires Comment` | Yes/No | Sí | Requisito adicional |
| `Requires Approval` | Yes/No | Sí | Requisito adicional |
| `Available` | Yes/No | Sí | Transición utilizable |

Clave alternativa: `AK_DQStatusTransition_TransitionCode` sobre `Transition Code`.

## Relaciones y eliminación

| Relación | Cardinalidad | Comportamiento de eliminación |
|---|---|---|
| Exception Reference → Remediation Case | 1:N | Restrict |
| DQ Status → Remediation Case | 1:N | Restrict |
| Remediation Case → Case Activity | 1:N | Restrict |
| Remediation Case → Case Evidence | 1:N | Restrict |
| DQ Status → Status Transition (From/To) | 1:N | Restrict |

Los roles funcionales no recibirán privilegio para eliminar casos, actividades, evidencia o referencias. Las correcciones se registran como nuevas actividades.

## Estados y transiciones válidas

```text
New → Triaged → In Progress → Pending Approval → Resolved
                              Pending Approval → Rejected → In Progress
                              Pending Approval → Waived
Resolved → In Progress  (reapertura controlada)
```

El catálogo y la tabla de transiciones serán la fuente de verdad. La aplicación validará la transición y Power Automate volverá a validarla antes de persistir decisiones de aprobación.

## Auditoría

- Activar auditoría del entorno si los permisos institucionales lo permiten.
- Activar auditoría en las seis tablas.
- Auditar especialmente `Owner`, `Case Status`, `Due At`, `Approval Outcome`, `Resolution Type`, `Resolution Summary`, `Resolved At` y `Source Correction State`.
- Mantener `Exception Instance ID`, `Recurrence Key` y los datos de la referencia como campos no editables en la app.
- No usar el log de auditoría como sustituto de `DQ Case Activity`; uno prueba cambios técnicos y el otro conserva la narrativa operativa.

## Secuencia de construcción

1. Crear publisher y solución.
2. Crear choices globales y tablas de catálogo.
3. Crear referencia de excepción y tablas transaccionales.
4. Configurar relaciones, claves alternativas y auditoría.
5. Cargar catálogos y un subconjunto sintético de excepciones.
6. Probar creación, asignación, transición, evidencia, resolución, rechazo y auditoría.

## Gate de la fase

- Se puede crear, asignar, actualizar y auditar un caso.
- La excepción de referencia no es editable por el rol funcional.
- Una misma `Exception Instance ID` no produce dos casos.
- Una transición fuera de la lista blanca es rechazada.
- Resolver o eximir exige evidencia, comentario, aprobación y marca temporal.
- `Resolved` no equivale a `Confirmed Later`; la corrección del origen se confirma únicamente con un snapshot posterior.

## Implementación verificada

La implementación de Dataverse materializa seis tablas, seis opciones globales, relaciones con eliminación restringida, claves alternativas y auditoría. Se cargaron siete estados, ocho transiciones permitidas y ocho referencias de excepción sintéticas exportadas desde Fabric. También se creó un caso demostrativo con actividad y evidencia relacionadas.

Controles probados en la capa de datos:

- `AK_DQRemediationCase_ExceptionInstanceID` rechaza un segundo caso para la misma `Exception Instance ID`.
- `BR - Resolved requires complete evidence` bloquea `Resolved` cuando `Evidence Complete = No`.
- `BR - Waived requires complete evidence` bloquea `Waived` cuando `Evidence Complete = No`.
- La auditoría registra creación, cambio de estado, resumen de triage y marca temporal de transición.

El diseñador de reglas de negocio no permitió expresar limpiamente el control compuesto de estado terminal más aprobación, comentario y marca temporal: una segunda condición se convirtió en una rama `else-if` y la validación exigió una acción en la rama verdadera anterior. Se descartó el borrador antes de guardarlo. Para evitar acciones ficticias o una proliferación frágil de reglas, los controles restantes se implementarán en capas posteriores:

- Power Apps limitará las transiciones expuestas, presentará los campos requeridos y mantendrá la referencia de Fabric como solo lectura.
- Power Automate volverá a validar la lista blanca de transición y, antes de persistir `Resolved` o `Waived`, exigirá evidencia, comentario, aprobación y marca temporal en una sola condición atómica.

Esta distribución no cambia la fuente de verdad: `DQ Status Transition` conserva la lista blanca y Dataverse conserva los datos y la auditoría; la aplicación guía la interacción y la automatización protege la decisión terminal.
