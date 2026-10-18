# Diseño de automatización — Fase 7 Power Automate

## Decisión

El MVP implementará dos flujos dentro de la solución `HR Data Quality & Lifecycle Workbench`:

1. `DQ - Notify Case Assignment`.
2. `DQ - Validate and Route Approval`.

Los flujos usarán referencias de conexión y variables de entorno. No se incluirán correos, GUID de usuario ni URL del tenant directamente en las acciones.

## Prerrequisitos mínimos de Dataverse

Agregar a `DQ Remediation Case` tres columnas técnicas ocultas del formulario funcional:

| Columna | Tipo | Propósito |
|---|---|---|
| `Last Notified Owner ID` | Text 100 | Idempotencia de la notificación de asignación |
| `Approval Request ID` | Text 100 | Evitar más de una aprobación activa por caso |
| `Approval Requested At` | Date and time | Trazabilidad y diagnóstico de solicitudes pendientes |

Agregar variables de entorno a la solución:

| Variable | Tipo | Uso |
|---|---|---|
| `DQ Approver UPN` | Text | Aprobador humano del MVP |
| `DQ Operational App URL` | Text | Enlace al registro dentro de la app operativa |

Referencias de conexión: Microsoft Dataverse, Approvals y Office 365 Outlook.

## Flujo 1 — `DQ - Notify Case Assignment`

### Disparador

`Microsoft Dataverse — When a row is added, modified or deleted`

- Change type: `Added or Modified`.
- Table: `DQ Remediation Case`.
- Scope: `Organization`.
- Filter rows: caso activo.
- Concurrency control: `On`, degree `1`.

`Owner` es un lookup y no debe colocarse en `Select columns`; el conector no admite lookups en ese parámetro. El flujo puede recibir otras actualizaciones, pero termina antes de enviar si el owner vigente coincide con `Last Notified Owner ID`.

### Camino principal

1. Obtener el caso y su owner actual.
2. Si el owner está vacío, terminar como `Skipped`.
3. Si el GUID del owner coincide con `Last Notified Owner ID`, terminar como `Idempotent skip`.
4. Obtener la excepción relacionada para título, severidad, dominio y SLA.
5. Enviar correo al owner con datos mínimos y enlace al caso.
6. Actualizar `Last Notified Owner ID` únicamente después del envío exitoso.
7. Crear `DQ Case Activity` con tipo `Assignment`, fecha UTC y una nota sin información sensible.

### Errores

La implementación final usa `Catch Assignment Notification` después de la última acción del camino positivo. Su opción **Ejecutar después** incluye error, omitido y timeout, pero excluye éxito. El scope crea una actividad técnica `Assignment notification error` y termina como `Failed` con `DQ_ASSIGNMENT_NOTIFICATION_FAILED`; nunca marca al owner como notificado.

## Flujo 2 — `DQ - Validate and Route Approval`

### Disparador

`Microsoft Dataverse — When a row is added, modified or deleted`

- Change type: `Modified`.
- Table: `DQ Remediation Case`.
- Scope: `Organization`.
- Select columns: `mprpa_approvaloutcome`.
- Filter rows: `mprpa_approvaloutcome eq 557440000` (`Pending`).
- Concurrency control: `On`, degree `1`.

### Validación previa

Antes de crear una aprobación:

1. volver a leer el caso;
2. terminar si `Approval Request ID` ya contiene valor;
3. comprobar que el estado actual sea `Pending Approval` consultando `DQ Status`;
4. exigir `Evidence Complete = Yes`;
5. exigir `Resolution Type` y `Resolution Summary` no vacíos;
6. exigir al menos un registro `DQ Case Evidence` con `Supports Closure = Yes`;
7. comprobar en `DQ Status Transition` que exista la transición desde el estado actual hacia el destino previsto.

Si una condición falla, crear una actividad `Evidence Request` o `Approval`, dejar el caso sin transición terminal y finalizar como `Rejected by validation`.

### Aprobación e idempotencia

1. Usar `Create an approval` con tipo `Approve/Reject — First to respond` y `DQ Approver UPN`.
2. Guardar inmediatamente el identificador devuelto en `Approval Request ID` y `utcNow()` en `Approval Requested At`.
3. Usar `Wait for an approval` con ese identificador.
4. Volver a leer el caso antes de persistir la respuesta.
5. Si se aprueba: establecer `Approval Outcome = Approved`; mover a `Resolved` o `Waived` según `Resolution Type`; completar `Resolved At` y `Last Transition At`.
6. Si se rechaza: establecer `Approval Outcome = Rejected`; mover a `Rejected`; completar `Last Transition At`.
7. Crear una actividad `Approval` con resultado, aprobador, fecha y comentario seguro.
8. Notificar al owner con el resultado y el enlace al caso.

El owner se vuelve a resolver desde el caso actualizado mediante `Get Case Owner After Approval`. Una única acción `Notify Owner of Approval Result`, colocada después de la condición completa Approved/Rejected, evita duplicar correos entre `Resolved`, `Waived` y `Rejected`. El asunto, estado final y enlace se construyen con contenido dinámico y `DQ Operational App URL`.

Separar `Create` y `Wait` permite persistir el ID de la aprobación antes de que el flujo quede suspendido y evita crear otra solicitud si Dataverse vuelve a entregar el evento.

`Wait for Approval` usa un timeout productivo ISO 8601 de `P7D`. `Catch Approval Processing` se ejecuta cuando el bloque terminal falla, se omite o agota el tiempo; crea `Approval processing error` y termina como `Failed` con `DQ_APPROVAL_PROCESSING_FAILED`. El timeout conserva el caso no terminal y el ID de aprobación para diagnóstico.

## Seguridad y alcance

- La aprobación siempre conserva intervención humana.
- Los correos no incluyen valores observados que puedan ser sensibles.
- El flujo opera con una cuenta de servicio o propietario documentado, no con credenciales incrustadas.
- El rol funcional no puede editar las columnas técnicas.
- `Resolved` no cambia automáticamente `Source Correction State`; la confirmación del origen sigue dependiendo de un snapshot posterior.

## Límite transaccional

Power Automate revalida el caso justo antes de escribir y serializa ejecuciones del flujo, pero varias acciones de Dataverse no forman una transacción ACID única. Para el MVP esta limitación se controla con relectura, idempotencia, auditoría y concurrencia `1`. Un despliegue productivo con escritores concurrentes deberá mover la validación y actualización terminal a una Custom API o plug-in de Dataverse.

## Matriz de aceptación

| Caso | Resultado esperado |
|---|---|
| Primera asignación | Un correo y una actividad |
| Actualización sin cambio de owner | Ningún correo adicional |
| Reasignación | Un correo al nuevo owner |
| Entrega duplicada del evento | Una sola notificación o aprobación |
| Pending Approval sin evidencia | Sin solicitud; actividad de validación |
| Aprobación válida | `Approved` + estado terminal + marcas temporales + actividad |
| Rechazo | `Rejected` + estado `Rejected` + actividad |
| Error del conector | Ejecución fallida trazable; sin falso estado terminal |
| Timeout | Caso permanece no terminal y conserva el ID de aprobación para diagnóstico |

## Implementación final verificada

Fecha de cierre: 16 de octubre de 2026.

### Configuración y portabilidad

- `DQ Approver UPN` reemplaza el aprobador codificado.
- `DQ Operational App URL` reemplaza la URL codificada en correos.
- Las conexiones de Dataverse, Approvals y Outlook permanecen como referencias de conexión de la solución.
- Ambos comprobadores quedaron en `0 errores / 0 advertencias`.

### Idempotencia de asignación

El disparador de asignación mantiene `Select columns` vacío porque `Owner` es lookup. Cada ejecución vuelve a leer `_ownerid_value` y `Last Notified Owner ID`, normaliza ambos GUID y continúa sólo si existe un propietario diferente. Concurrencia permanece en `1`.

La rama positiva obtiene el usuario vigente con el GUID releído, envía un único correo, actualiza `Last Notified Owner ID` después del envío y registra la actividad. Las actualizaciones irrelevantes producen ejecuciones cortas omitidas sin correo duplicado.

### Rutas de aprobación

- `Approved` con resolución ordinaria → `Resolved`.
- `Approved` con `Resolution Type = Waived` → `Waived`.
- `Rejected` → `Rejected`.
- Prerrequisitos incompletos → actividad de validación, sin solicitud.
- Resultado vigente → actualización terminal, actividad y un correo común al owner.
- Resultado obsoleto → actividad `Stale Approval`, sin sobrescribir el caso.

### Resultado de aceptación

| Caso | Resultado |
|---|---|
| Primera asignación | PASS — un correo y una actividad |
| Actualización sin cambio de owner | PASS — sin correo adicional |
| Reasignación real a segundo usuario | No ejecutada por disponer de una sola cuenta; lógica y relectura configuradas |
| Entrega/actualización duplicada | PASS — comparación fresca e idempotente |
| Pending Approval sin evidencia | PASS — actividad de validación, sin aprobación |
| Approved → Resolved | PASS |
| Approved → Waived | PASS |
| Rejected → Rejected | PASS |
| Correo final al owner | PASS en configuración y comprobador; acción común a las tres rutas |
| Catch de asignación | PASS — actividad y terminación controlada |
| Catch/timeout de aprobación | PASS — actividad registrada; timeout restaurado a `P7D` |

## Límites aceptados del MVP

- Los casos operativos se asignan a usuarios. Un owner de tipo Team requiere una rama adicional para resolver destinatarios.
- La prueba de reasignación entre identidades queda pendiente de un entorno con un segundo usuario; no se sustituye por una reasignación ficticia al mismo GUID.
- No se implementa un recordatorio programado independiente para casos vencidos. `Due At` alimentará la visibilidad de SLA en Power Apps y Power BI; una escalación periódica multicanal queda como mejora productiva fuera del gate aceptado.

## Referencias de implementación

- [Disparador de Dataverse y filtros](https://learn.microsoft.com/en-us/power-automate/dataverse/create-update-delete-trigger)
- [Optimización de disparadores](https://learn.microsoft.com/en-us/power-automate/guidance/coding-guidelines/optimize-power-automate-triggers)
- [Diferencias entre acciones de aprobación](https://learn.microsoft.com/troubleshoot/power-platform/power-automate/approvals/differences-between-flow-approval-actions)
- [Antipatrones e idempotencia](https://learn.microsoft.com/power-automate/guidance/coding-guidelines/avoid-anti-patterns)
