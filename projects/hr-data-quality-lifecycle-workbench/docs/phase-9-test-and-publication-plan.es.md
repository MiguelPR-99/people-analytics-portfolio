# Plan de pruebas, evidencia y publicación — Fase 9

## Estado

**Fase 9 cerrada el 18 de octubre de 2026.** El gate local y el paquete público quedaron aprobados y el caso se integró en el repositorio del portafolio. La publicación en Fabric y cualquier nueva prueba mutante permanecen fuera de este cierre y requieren autorización independiente.

## Objetivo de aceptación

Demostrar con evidencia reproducible el recorrido:

```text
datos sintéticos → Fabric Bronze/Silver/Gold → excepción publicada →
Power Apps/Dataverse → Power Automate/aprobación → Power BI actualizado
```

La fase distingue tres resultados independientes:

1. **Regresión local aprobada:** código, contratos y artefactos reproducibles.
2. **Recorrido tenant aprobado:** smoke tests no mutantes y una prueba controlada cuando se autorice.
3. **Publicación aprobada:** material anonimizado, narrativa bilingüe, enlaces y evidencia curada.

## Matriz de aceptación

| Capa | Control | Automatización | Estado inicial |
|---|---|---|---|
| Datos sintéticos | determinismo, esquemas, población, anomalías y ausencia de columnas prohibidas | `python -m unittest discover -s scripts/tests -v` | PASS 7/7 |
| Fabric | Bronze conserva origen; Silver normaliza; Gold reconcilia; segunda ejecución idempotente | evidencia de Fase 4 + revisión del manifiesto | PASS histórico |
| Dataverse | caso, actividad, evidencia, auditoría y reglas de negocio | evidencia de Fase 5 | PASS histórico |
| Power Apps | typecheck, filtros, navegación, estados de error y creación simulada | `scripts/verify_power_platform_phase7.ps1` | PASS 5/5 |
| Power Apps publicado | carga y navegación contra el runtime real | `-IncludeE2E` | Pendiente de revalidación final |
| Power Automate | éxito, rechazo, waived, timeout, Catch, idempotencia | evidencia/historial de Fase 7 | PASS histórico |
| Power BI | entorno 13/13, PBIR sin errores, reconciliación y captura | verificadores de Fase 8 y captura final de Fase 9 | PASS técnico y visual |
| Seguridad Git | `.env`, `.auth`, `.pbi`, cachés y credenciales fuera del repositorio | `scripts/verify_phase9.ps1` | PASS |
| Publicación | parámetros anonimizados, README ES/EN y manifiesto reducido de evidencia | auditoría del gate | PASS |

## Gate automatizado

Ejecución local completa:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify_phase9.ps1
```

Smoke test publicado, sin mutación:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify_phase9.ps1 -IncludeTenantE2E
```

La regresión visual es una capa separada para evitar falsos negativos por datos dinámicos:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify_phase9.ps1 -IncludeTenantE2E -IncludeVisual
```

La creación real permanece opt-in y exige una clave o `auto`; no debe formar parte de cada ejecución:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify_phase9.ps1 -MutationBusinessKey auto
```

## Evidencia pública

Se conservará únicamente una selección que explique el flujo sin exponer nombres de cuenta, URLs institucionales, tenant, correos, tokens ni información de sesión. La selección final deberá incluir:

- arquitectura simplificada;
- una prueba de calidad/reconciliación Fabric;
- Command Center y caso operativo;
- aprobación y manejo de error;
- scorecard final de Power BI;
- guía para un video opcional de 60–90 segundos.

Las capturas de trabajo completas permanecen como evidencia interna; no todas deben publicarse.

## Bloqueadores iniciales resueltos

1. Los valores institucionales de los parámetros Power BI fueron sustituidos por valores de ejemplo seguros.
2. Se crearon README del proyecto en español e inglés.
3. Se curó un manifiesto reducido de evidencia pública con dos capturas esenciales.
4. El video se reclasificó como complemento opcional y se añadió una guía bilingüe de grabación.
5. La revalidación local transversal quedó aprobada; la evidencia tenant de las fases 6 y 7 se conserva sin repetir una mutación.
6. La publicación en GitHub fue autorizada; Fabric continúa fuera de alcance.

## Primera ejecución

La primera regresión local del 18 de octubre de 2026 produjo `evidence/phase-9/local-regression.json` con estos resultados:

- generador sintético: 7/7 pruebas;
- Generative Page: typecheck y 5/5 pruebas de componente;
- preparación Power BI/Fabric: 13/13 controles;
- PBIR: 0 errores y 0 advertencias;
- revisión visual: aprobada; etiquetas y valores KPI completos, sin elipsis;
- higiene del repositorio: aprobada;
- Playwright contra el tenant: no ejecutado en este lote;
- publicación: gate local aprobado; video pendiente únicamente como mejora opcional.

## Criterio de cierre

La Fase 9 se cerrará cuando la regresión local esté aprobada, la evidencia tenant previa permanezca trazable, el paquete público esté anonimizado, los enlaces funcionen desde GitHub y la publicación autorizada se verifique mediante lectura posterior. El video no condiciona el cierre.

