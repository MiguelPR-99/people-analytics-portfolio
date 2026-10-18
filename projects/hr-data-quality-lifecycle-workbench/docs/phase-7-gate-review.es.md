# Revisión del gate — Fase 7 Power Automate

**Fecha:** 16 de octubre de 2026  
**Resultado:** PASS con una limitación de entorno documentada

## Componentes publicados

1. `DQ - Notify Case Assignment` — publicado.
2. `DQ - Validate and Route Approval` — publicado.

Ambos flujos pertenecen a la solución, usan referencias de conexión y consumen `DQ Approver UPN` y `DQ Operational App URL` en lugar de valores codificados.

## Criterios del gate

| Criterio | Evidencia | Resultado |
|---|---|---|
| Manejar éxito | Asignación inicial; Approved → Resolved; Approved → Waived; correo final al owner | PASS |
| Manejar rechazo | Rejected → Rejected con actividad y estado persistido | PASS |
| Manejar error/timeout | Scopes Catch, actividades técnicas y terminaciones `DQ_ASSIGNMENT_NOTIFICATION_FAILED` / `DQ_APPROVAL_PROCESSING_FAILED`; timeout probado y restaurado a `P7D` | PASS |
| Evitar duplicados | Relectura del owner, `Last Notified Owner ID`, concurrencia 1 y `Approval Request ID` persistido antes de esperar | PASS |
| Registrar respuesta | Outcome, estado terminal, marcas temporales y actividad en Dataverse | PASS |
| Portabilidad | Aprobador y URL mediante variables de entorno | PASS |
| Calidad del diseñador | Comprobadores de ambos flujos | 0 errores / 0 advertencias |

## Evidencia funcional consolidada

- Aprobación ordinaria movió el caso a `Resolved`.
- Rechazo movió el caso a `Rejected`.
- Exención aprobada movió el caso a `Waived`.
- La ausencia de evidencia impidió crear la aprobación y dejó actividad de validación.
- Una actualización irrelevante del caso no repitió el correo de asignación.
- El timeout controlado ejecutó `Catch Approval Processing`, registró `Approval processing error` y terminó con error controlado.
- La creación publicada desde Power Apps disparó ejecuciones correctas de `DQ - Notify Case Assignment`.
- Una auditoría FetchXML de sólo lectura confirmó que las dos aplicaciones, la Generative Page y ambos flujos están agregados explícitamente a `HR Data Quality & Lifecycle Workbench`.

## Limitaciones aceptadas

- No se ejecutó una reasignación real entre dos identidades porque el entorno sólo dispone de una cuenta. El flujo no considera una asignación al mismo GUID como evidencia de reasignación.
- El MVP resuelve owners de tipo usuario; Team owners requieren diseño adicional.
- La escalación periódica de SLA no forma parte del gate implementado. `Due At` queda disponible para visibilidad y análisis; un recordatorio programado es una mejora posterior.

Estas limitaciones no contradicen los tres criterios vinculantes del roadmap: éxito/rechazo/error, ausencia de duplicados y persistencia de la respuesta.

## Decisión

La Fase 7 queda cerrada. La Fase 8 — Power BI puede comenzar usando Gold para calidad analítica y Dataverse para estado operativo, aprobación, actividad y SLA.

El cierre queda operacionalizado mediante `scripts/verify_power_platform_phase7.ps1` y el runbook [Operación y mantenimiento de Power Platform](power-platform-maintenance.es.md). El gate local es de sólo lectura por defecto; navegador, regresión visual y creación real requieren opciones explícitas. Su ejecución de cierre pasó `5/5` pruebas de componente y `4/4` pruebas smoke publicadas, sin crear registros.
