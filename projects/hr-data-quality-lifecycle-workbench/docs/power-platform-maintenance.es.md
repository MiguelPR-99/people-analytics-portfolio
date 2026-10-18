# Operación y mantenimiento de Power Platform

## Propósito

Este runbook convierte el cierre de las fases 6 y 7 en una verificación repetible. Distingue entre pruebas locales, comprobación de la aplicación publicada y salud operativa de los flujos. Las verificaciones mutantes nunca se ejecutan por defecto.

## Gate local seguro

Desde la raíz del proyecto:

```powershell
pwsh -File scripts/verify_power_platform_phase7.ps1
```

El comando ejecuta el typecheck y las pruebas de componente de la Generative Page. No accede al entorno ni crea datos.

Para añadir la regresión funcional de la aplicación publicada:

```powershell
pwsh -File scripts/verify_power_platform_phase7.ps1 -IncludeE2E
```

La regresión visual continúa separada porque puede variar por cambios legítimos de renderizado:

```powershell
pwsh -File scripts/verify_power_platform_phase7.ps1 -IncludeE2E -IncludeVisual
```

La creación real de un caso requiere autorización explícita mediante una clave o `auto`:

```powershell
pwsh -File scripts/verify_power_platform_phase7.ps1 -MutationBusinessKey "auto"
```

Puede conservarse un resultado estructurado con `-ReportPath`, por ejemplo `evidence/power-apps/phase-7-verification.json`. El archivo registra qué pasos se ejecutaron y si hubo una prueba mutante; no almacena credenciales.

## Verificación de Power Automate

Antes de publicar cambios y mensualmente durante operación:

1. Confirmar que `DQ - Notify Case Assignment` y `DQ - Validate and Route Approval` están publicados.
2. Ejecutar el comprobador de flujo y exigir `0 errores / 0 advertencias`.
3. Revisar las cinco ejecuciones más recientes de cada flujo.
4. Investigar cualquier flujo con más del 50 % de fallos en esa muestra o cuyo último resultado sea `Failed`, `Timed out` o `Cancelled`.
5. Abrir la ejecución fallida, identificar la primera acción fallida y confirmar que el scope Catch registró una `DQ Case Activity` técnica.
6. Confirmar que las actualizaciones irrelevantes del caso siguen terminando sin correo duplicado.

El CLI `pac power-automate` disponible actualmente es una función Preview y no se usa como requisito automático del gate. Cuando se disponga de FlowAgent, sus operaciones de inventario, preflight, validación, smoke test, historial y diagnóstico pueden automatizar esta sección sin cambiar los criterios.

## Checklist de release y ALM

- La Generative Page, la aplicación model-driven, ambos flujos, las referencias de conexión y las variables de entorno pertenecen a la solución.
- El paquete de despliegue incluye explícitamente la Generative Page; no se presupone que viaje sólo por pertenecer a la aplicación.
- `DQ Approver UPN` y `DQ Operational App URL` tienen valores por ambiente y no aparecen codificados en acciones o TypeScript.
- Las conexiones de Dataverse, Approvals y Outlook están sanas y usan el propietario operativo documentado.
- Los roles conservan `Create`, `Append`, `Append To`, lectura de variables de entorno y privilegio `Assign` donde corresponda.
- El comando estándar `Assign` permanece disponible, ya que `Owner` es un campo controlado por plataforma.
- La exportación de la solución y sus settings se conserva antes de cambios relevantes.
- No se habilitan `custom-api` ni `custom-telemetry` sólo para cerrar el MVP: esas capacidades siguen marcadas como experimentales o en progreso en las skills oficiales.

La auditoría de cierre del 16 de octubre de 2026 confirmó por `solutioncomponent` que ambas aplicaciones, la Generative Page y los dos flujos forman parte explícita de `HR Data Quality & Lifecycle Workbench`.

## Cadencia recomendada

| Frecuencia | Actividad |
|---|---|
| En cada cambio de página | `npm run verify` y, tras publicar, smoke E2E |
| En cada cambio de flujo | Comprobador 0/0, prueba del camino afectado y revisión del Catch |
| Semanal durante piloto | Revisar última ejecución y fallos de ambos flujos |
| Mensual | Muestra de cinco ejecuciones, conexiones, variables de entorno y expiración de autenticación E2E |
| Antes de mover de ambiente | Exportar solución, revisar settings y ejecutar el gate completo |

## Alcance del cierre

Para el MVP, Playwright es verificación opcional de navegador, no una dependencia del funcionamiento. El gate vinculante continúa siendo: pruebas locales correctas, aplicación publicada funcional, datos persistidos en Dataverse, historial de flujos correcto y manejo observable de errores.
