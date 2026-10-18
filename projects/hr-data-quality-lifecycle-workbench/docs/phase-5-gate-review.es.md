# Revisión del gate — Fase 5 Dataverse

## Resultado

**PASS aprobado por el owner del proyecto el 2026-10-14.**

El modelo transaccional está construido y probado. Los controles que requieren contexto de interfaz o una validación compuesta se asignan explícitamente a Power Apps y Power Automate; no se simulan mediante acciones ficticias en reglas de negocio.

## Entregables

| Entregable | Implementación | Estado |
|---|---|---|
| Solución y publisher | `HR Data Quality & Lifecycle Workbench`, publisher `Miguel PR — People Analytics`, prefijo `mprpa` | PASS |
| Tablas | Seis tablas: estado, transición, referencia, caso, actividad y evidencia | PASS |
| Catálogos | Siete estados y ocho transiciones permitidas | PASS |
| Opciones globales | Severidad, resolución, aprobación, corrección del origen, actividad y evidencia | PASS |
| Relaciones | Relaciones 1:N con comportamiento de eliminación `Restrict` | PASS |
| Integridad | Claves alternativas para catálogos, referencias y caso por `Exception Instance ID` | PASS |
| Auditoría | Entorno, seis tablas y columnas críticas auditables | PASS |
| Datos de demostración | Ocho referencias de Fabric, un caso, una actividad y una evidencia | PASS |
| Reglas de negocio | Bloqueo de `Resolved` y `Waived` sin evidencia completa | PASS |

## Pruebas ejecutadas

| Prueba | Resultado |
|---|---|
| Importar ocho excepciones sintéticas desde Fabric | PASS |
| Crear y asignar `DQCASE-000001` | PASS |
| Repetir la misma `Exception Instance ID` | PASS: rechazo por `AK_DQRemediationCase_ExceptionInstanceID` |
| Actualizar `New → Triaged` y registrar actividad | PASS |
| Relacionar una evidencia de tipo `Data Reference` | PASS |
| Revisar historial de auditoría | PASS |
| Intentar `Triaged → Resolved` con evidencia incompleta | PASS: guardado rechazado y estado persistido `Triaged` |
| Intentar `Triaged → Waived` con evidencia incompleta | PASS: guardado rechazado y estado persistido `Triaged` |

## Evaluación del gate

| Criterio | Resultado | Tratamiento |
|---|---|---|
| Crear, asignar, actualizar y auditar un caso | PASS | Verificado con el caso demostrativo y el historial de auditoría |
| Conservar inmutable la excepción original | PASS de modelo | Tabla de referencia separada; Power Apps no expondrá sus campos como editables al rol funcional |
| Evitar dos casos por la misma excepción | PASS | Clave alternativa probada mediante intento duplicado |
| Controlar estados inválidos | PASS de diseño, integración pendiente | Catálogo y lista blanca en Dataverse; Power Apps limitará la selección y Power Automate revalidará antes de persistir |
| Exigir requisitos al resolver o eximir | PASS parcial en Dataverse | Evidencia protegida por reglas activas; comentario, aprobación y marca temporal se validarán atómicamente en Power Automate |
| Separar resolución de corrección confirmada | PASS de modelo | `Resolution Type` y `Source Correction State` permanecen separados |

## Decisión de arquitectura

El intento de condensar aprobación, resumen y marca temporal en una regla de negocio compuesta se descartó antes de guardar. El diseñador conectó la condición adicional como `else-if` y exigió una acción en la rama anterior. Se evita introducir una acción sin efecto o múltiples reglas difíciles de mantener.

La defensa queda distribuida por responsabilidad:

1. Dataverse protege identidad, relaciones, auditoría y evidencia mínima de cierre.
2. Power Apps guiará únicamente transiciones permitidas y mantendrá la referencia analítica como solo lectura.
3. Power Automate comprobará nuevamente transición, evidencia, comentario, aprobación y marca temporal antes de registrar una decisión terminal.

Estas obligaciones son criterios de aceptación vinculantes para las fases posteriores; no se presentan como capacidades ya implementadas.

## Evidencias principales

- `checkpoint-105-exception-reference-import-8-records.png`
- `checkpoint-109-first-remediation-case-created.png`
- `checkpoint-112-alternate-key-violation-detail.png`
- `checkpoint-116-status-change-activity-created.png`
- `checkpoint-118-data-reference-evidence-created.png`
- `checkpoint-120-remediation-case-audit-history-verified.png`
- `checkpoint-128-business-rule-activated.png`
- `checkpoint-132-business-rule-negative-test-reverted.png`
- `checkpoint-138-resolved-and-waived-evidence-rules-active.png`
- `checkpoint-140-waived-evidence-rule-negative-test-reverted.png`
- `checkpoint-145-composite-business-rule-designer-limitation.png`
- `checkpoint-146-business-rules-final-active-list.png`

## Cierre

El owner aprobó explícitamente el gate y aceptó la distribución documentada de controles entre Dataverse, Power Apps y Power Automate. La Fase 5 queda completada y habilita la Fase 6 — Power Apps. Los controles diferidos permanecen como requisitos obligatorios y verificables; la aprobación no los convierte en capacidades ya implementadas.
