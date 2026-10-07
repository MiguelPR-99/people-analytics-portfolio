# Diccionario de datos — diseño previo a generación

Este documento define la estructura objetivo de la capa procesada. Los nombres están en inglés para que coincidan con los archivos, Power Query y el modelo de Power BI; las explicaciones se mantienen en español.

Convenciones:

- Las claves terminadas en `Key` son enteros sin significado de negocio.
- Los identificadores terminados en `ID` son códigos ficticios legibles.
- Los timestamps se almacenan en hora local ficticia de México y formato ISO 8601.
- Los valores lógicos se normalizan a `true` y `false`.
- Los valores `Unknown` utilizan una fila explícita en cada dimensión cuando corresponda.

## `dim_date`

**Grano:** una fila por fecha entre 2025-01-01 y 2026-06-30.

| Campo | Tipo | Nulo | Descripción |
|---|---|---:|---|
| `DateKey` | integer | No | Fecha en formato `YYYYMMDD`; clave primaria |
| `Date` | date | No | Fecha calendario |
| `Year` | integer | No | Año |
| `Quarter` | string | No | `Q1`–`Q4` |
| `MonthNumber` | integer | No | 1–12 |
| `MonthName` | string | No | Nombre corto en inglés |
| `YearMonth` | string | No | `YYYY-MM` |
| `ISOWeek` | integer | No | Semana ISO |
| `WeekStartDate` | date | No | Lunes de la semana |
| `DayOfWeekNumber` | integer | No | Lunes = 1; domingo = 7 |
| `DayOfWeekName` | string | No | Nombre corto en inglés |
| `IsWeekend` | boolean | No | Sábado o domingo |
| `IsHoliday` | boolean | No | Fecha no laborable definida por la simulación |
| `HolidayName` | string | Sí | Nombre ilustrativo de la fecha no laborable |
| `IsBusinessDay` | boolean | No | Día que consume el reloj de SLA |
| `BusinessHoursAvailable` | decimal | No | 8 en día laborable; 0 en otro caso |

## `dim_location`

**Grano:** una ubicación ficticia atendida.

| Campo | Tipo | Nulo | Descripción |
|---|---|---:|---|
| `LocationKey` | integer | No | Clave primaria |
| `LocationCode` | string | No | Código: `BJPL`, `QHSC` o `MXCO` |
| `LocationName` | string | No | Nombre de la ubicación |
| `LocationType` | string | No | Plant, Service Center o Corporate Office |
| `Region` | string | No | Región ficticia de reporte |

## `dim_organization`

**Grano:** una unidad organizacional ficticia.

| Campo | Tipo | Nulo | Descripción |
|---|---|---:|---|
| `OrgUnitKey` | integer | No | Clave primaria |
| `OrgUnitCode` | string | No | Código corto |
| `OrgUnitName` | string | No | Nombre de la unidad |
| `FunctionGroup` | string | No | Operations, Commercial o Corporate |

## `dim_team`

**Grano:** un equipo de HR Services.

| Campo | Tipo | Nulo | Descripción |
|---|---|---:|---|
| `TeamKey` | integer | No | Clave primaria |
| `TeamCode` | string | No | Código corto |
| `TeamName` | string | No | Nombre del equipo |
| `ServiceScope` | string | No | Resumen del alcance funcional |

## `dim_requester`

**Grano:** una persona solicitante completamente ficticia y anónima.

| Campo | Tipo | Nulo | Descripción |
|---|---|---:|---|
| `RequesterKey` | integer | No | Clave primaria |
| `RequesterID` | string | No | Código anónimo `REQ-0001`–`REQ-1200` |
| `HomeLocationKey` | integer | No | Ubicación principal; FK a `dim_location` |
| `OrgUnitKey` | integer | No | Unidad organizacional; FK a `dim_organization` |
| `EmployeeGroup` | string | No | Hourly o Salaried |
| `WorkerType` | string | No | Regular, Temporary o Intern |
| `PreferredLanguage` | string | No | Spanish o English; solo para contexto de servicio |
| `JoinDate` | date | No | Fecha ficticia de ingreso |
| `ExitDate` | date | Sí | Fecha ficticia de salida, si aplica |
| `ActiveAtCutoffFlag` | boolean | No | Activo al 2026-06-30 |

No habrá nombre, género, edad, correo, teléfono, salario, identificadores nacionales ni texto personal.

## `dim_agent`

**Grano:** un agente ficticio de HR Services.

| Campo | Tipo | Nulo | Descripción |
|---|---|---:|---|
| `AgentKey` | integer | No | Clave primaria |
| `AgentID` | string | No | Código `AGT-001`–`AGT-018` |
| `AgentAlias` | string | No | Alias ficticio no asociado a una persona real |
| `PrimaryTeamKey` | integer | No | FK a `dim_team` |
| `WorkLocationKey` | integer | No | FK a `dim_location` |
| `ExperienceBand` | string | No | 0–1 year, 1–3 years o 3+ years |
| `ActiveFrom` | date | No | Inicio ficticio de actividad |
| `ActiveTo` | date | Sí | Fin ficticio de actividad |
| `WeeklyContractHours` | decimal | No | Horas nominales semanales |
| `ActiveAtCutoffFlag` | boolean | No | Activo al corte |

Los datos de agente se utilizarán para analizar carga y flujo, no para crear rankings de desempeño individual.

## `dim_service_catalog`

**Grano:** un tipo de solicitud.

| Campo | Tipo | Nulo | Descripción |
|---|---|---:|---|
| `ServiceKey` | integer | No | Clave primaria |
| `ServiceCode` | string | No | Código único del tipo de solicitud |
| `ServiceGroup` | string | No | Uno de los siete grupos de servicio |
| `RequestType` | string | No | Tipo específico de solicitud |
| `OwnerTeamKey` | integer | No | Equipo propietario; FK a `dim_team` |
| `BaseComplexity` | string | No | Low, Medium o High |
| `DefaultPriority` | string | No | Prioridad más probable |
| `ApprovalProbability` | decimal | No | Parámetro de simulación entre 0 y 1 |
| `VendorDependencyProbability` | decimal | No | Parámetro de simulación entre 0 y 1 |
| `FirstContactResolutionBaseProbability` | decimal | No | Parámetro de simulación entre 0 y 1 |
| `ActiveFlag` | boolean | No | Tipo disponible durante el periodo |

## `dim_sla_policy`

**Grano:** una prioridad.

| Campo | Tipo | Nulo | Descripción |
|---|---|---:|---|
| `SLAPolicyKey` | integer | No | Clave primaria |
| `Priority` | string | No | Critical, High, Standard o Low |
| `FirstResponseSLAHours` | decimal | No | Meta en horas hábiles |
| `ResolutionSLAHours` | decimal | No | Meta en horas hábiles netas |
| `PauseOnEmployeeWaitFlag` | boolean | No | Si el reloj se pausa esperando al solicitante |
| `PolicyVersion` | string | No | Versión ilustrativa del SLA |

## `fact_cases`

**Grano:** una fila por caso único después de limpieza.

| Campo | Tipo | Nulo | Descripción |
|---|---|---:|---|
| `CaseKey` | integer | No | Clave sustituta del hecho |
| `CaseID` | string | No | Folio ficticio `CASE-YYYY-NNNNN` |
| `RequesterKey` | integer | No | Solicitante anónimo |
| `CreatedDateKey` | integer | No | Fecha de creación; relación activa con calendario |
| `FirstResponseDateKey` | integer | Sí | Fecha de primera respuesta |
| `ResolvedDateKey` | integer | Sí | Fecha de resolución |
| `ClosedDateKey` | integer | Sí | Fecha de cierre |
| `LocationKey` | integer | No | Snapshot de ubicación al crear el caso |
| `OrgUnitKey` | integer | No | Snapshot de unidad al crear el caso |
| `ServiceKey` | integer | No | Tipo de solicitud |
| `SLAPolicyKey` | integer | No | Política aplicable |
| `InitialAgentKey` | integer | Sí | Primer agente asignado |
| `FinalAgentKey` | integer | Sí | Agente responsable al cierre o corte |
| `InitialTeamKey` | integer | Sí | Equipo de primera asignación |
| `FinalTeamKey` | integer | Sí | Equipo al cierre o corte |
| `SourceChannel` | string | No | Portal, Email, Teams, Phone o Unknown |
| `CreatedAt` | datetime | No | Timestamp de recepción |
| `FirstResponseAt` | datetime | Sí | Primer contacto de HR Services |
| `ResolvedAt` | datetime | Sí | Momento en que se propone resolución |
| `ClosedAt` | datetime | Sí | Cierre definitivo |
| `CurrentStatusAtCutoff` | string | No | Estado al 2026-06-30 |
| `Priority` | string | No | Copia legible de la prioridad para reconciliación |
| `ComplexityBand` | string | No | Low, Medium o High después de variación del caso |
| `InformationCompleteAtSubmissionFlag` | boolean | No | Requisitos completos en el primer envío |
| `ApprovalRequiredFlag` | boolean | No | El caso necesitó aprobación |
| `VendorDependentFlag` | boolean | No | El caso dependió de un proveedor externo |
| `CancelledFlag` | boolean | No | Caso cancelado antes de resolución normal |
| `TransferCount` | integer | No | Número de reasignaciones válidas |
| `ReopenCount` | integer | No | Número de reaperturas |
| `InteractionCount` | integer | No | Contactos registrados durante el caso |
| `WaitingEmployeeBusinessHours` | decimal | No | Espera atribuida a información del solicitante |
| `WaitingApprovalBusinessHours` | decimal | No | Espera por aprobación |
| `WaitingVendorBusinessHours` | decimal | No | Espera por proveedor |
| `GrossResolutionBusinessHours` | decimal | Sí | Horas hábiles desde creación hasta resolución |
| `SLAExcludedBusinessHours` | decimal | No | Espera por empleado excluida por la política |
| `NetResolutionBusinessHours` | decimal | Sí | Horas consideradas para SLA de resolución |
| `FirstResponseBusinessHours` | decimal | Sí | Horas hábiles hasta primera respuesta |
| `FirstResponseWithinSLAFlag` | boolean | Sí | Cumplimiento; nulo si no es elegible |
| `ResolutionWithinSLAFlag` | boolean | Sí | Cumplimiento; nulo si no es elegible |
| `FirstContactResolvedFlag` | boolean | Sí | Resolución sin transferencia, reapertura o contacto adicional |
| `SurveyInvitedFlag` | boolean | No | Se envió invitación después del cierre |
| `ProcessInterventionEligibleFlag` | boolean | No | Employee Data Changes por portal elegible para comparación pre/post |
| `ExtractedAt` | datetime | No | Timestamp sintético de extracción |

### Elegibilidad de banderas

- `FirstResponseWithinSLAFlag` será nulo si el caso se cancela antes de recibir respuesta o sigue sin respuesta al corte.
- `ResolutionWithinSLAFlag` será nulo si el caso está abierto o cancelado.
- `FirstContactResolvedFlag` será nulo si el caso no se ha resuelto.
- `NetResolutionBusinessHours = GrossResolutionBusinessHours - SLAExcludedBusinessHours` y nunca será negativo.

## `fact_case_events`

**Grano:** un evento ordenado dentro de un caso.

| Campo | Tipo | Nulo | Descripción |
|---|---|---:|---|
| `EventKey` | integer | No | Clave primaria |
| `CaseKey` | integer | No | FK a `fact_cases` |
| `CaseID` | string | No | Folio legible para reconciliación |
| `EventSequence` | integer | No | Secuencia que inicia en 1 por caso |
| `EventType` | string | No | Created, Assigned, First Response, Status Change, Transfer, Resolved, Reopened, Closed o Cancelled |
| `StatusFrom` | string | Sí | Estado anterior |
| `StatusTo` | string | No | Estado resultante |
| `EventAt` | datetime | No | Timestamp del evento |
| `EventDateKey` | integer | No | FK a calendario |
| `AgentKey` | integer | Sí | Agente asociado al evento |
| `TeamKey` | integer | Sí | Equipo asociado al evento |
| `ReasonCode` | string | Sí | Razón estructurada; nunca texto libre |
| `BusinessHoursSincePriorEvent` | decimal | No | Duración desde el evento anterior |
| `IsWaitingStateFlag` | boolean | No | El nuevo estado es una espera |
| `ExtractedAt` | datetime | No | Timestamp de extracción |

La combinación `CaseKey + EventSequence` debe ser única en la capa procesada.

## `fact_surveys`

**Grano:** una respuesta válida a encuesta por caso cerrado.

| Campo | Tipo | Nulo | Descripción |
|---|---|---:|---|
| `SurveyKey` | integer | No | Clave primaria |
| `CaseKey` | integer | No | FK a `fact_cases`; una respuesta máxima por caso |
| `CaseID` | string | No | Folio legible |
| `InvitationDateKey` | integer | No | Fecha de invitación |
| `ResponseDateKey` | integer | No | Fecha de respuesta |
| `InvitedAt` | datetime | No | Timestamp de invitación |
| `RespondedAt` | datetime | No | Timestamp de respuesta |
| `OverallSatisfactionScore` | integer | No | Escala 1–5 |
| `EaseScore` | integer | No | Escala 1–5 |
| `ResolutionConfirmedFlag` | boolean | No | El solicitante confirmó resolución |
| `FeedbackTopic` | string | No | Speed, Communication, Accuracy, Self-Service u Other |
| `LowRatingFlag` | boolean | No | `true` cuando satisfacción <= 2 |

No se generarán comentarios abiertos.

## `fact_backlog_daily`

**Grano:** un caso abierto al final de un día calendario.

| Campo | Tipo | Nulo | Descripción |
|---|---|---:|---|
| `SnapshotDateKey` | integer | No | Fecha del snapshot |
| `CaseKey` | integer | No | Caso abierto |
| `ServiceKey` | integer | No | Servicio |
| `LocationKey` | integer | No | Ubicación del solicitante al crear el caso |
| `CurrentAgentKey` | integer | Sí | Agente responsable al final del día |
| `CurrentTeamKey` | integer | Sí | Equipo responsable al final del día |
| `StatusAtEndOfDay` | string | No | Estado al cierre del día |
| `WaitingReason` | string | Sí | Employee, Approval, Vendor o nulo |
| `BacklogAgeBusinessDays` | decimal | No | Edad hábil al final del día |
| `AgeBucket` | string | No | 0–2, 3–5, 6–10, 11–20 o 21+ business days |
| `ResolutionSLABreachedAtSnapshotFlag` | boolean | No | El tiempo neto acumulado ya supera SLA |

La combinación `SnapshotDateKey + CaseKey` debe ser única.

## `fact_queue_capacity_weekly`

**Grano:** un equipo de HR Services atendiendo una ubicación durante una semana.

| Campo | Tipo | Nulo | Descripción |
|---|---|---:|---|
| `WeekStartDateKey` | integer | No | Lunes de la semana |
| `TeamKey` | integer | No | Equipo de HR Services |
| `LocationKey` | integer | No | Cola geográfica atendida |
| `PlannedFTE` | decimal | No | FTE planeados para la cola |
| `ScheduledHours` | decimal | No | Horas planeadas |
| `AbsenceHours` | decimal | No | Ausencias sintéticas |
| `TrainingHours` | decimal | No | Tiempo de formación sintético |
| `OtherUnavailableHours` | decimal | No | Otras indisponibilidades |
| `AvailableHours` | decimal | No | `Scheduled - Absence - Training - Other` |
| `CapacityReductionEventFlag` | boolean | No | Marca del patrón controlado de Planta Bajío |

La tabla permite explicar capacidad agregada. No pretende estimar productividad individual ni tiempos estándar reales.

## Campos exclusivos de la capa raw

| Campo | Archivo | Uso |
|---|---|---|
| `SourceRowNumber` | Todos | Trazabilidad de la exportación |
| `SourceSystem` | Todos | Nombre ficticio del origen |
| `RawExtractID` | Todos | Identificador de lote |
| `RawChannel` | Casos | Valor antes de homologar |
| `RawServiceName` | Casos | Valor antes de homologar |
| `RawBoolean*` | Casos | Representaciones inconsistentes controladas |

Los campos raw no deben llegar al modelo final salvo que se utilicen explícitamente para auditoría de calidad.

