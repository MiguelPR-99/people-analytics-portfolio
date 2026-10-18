# Decisión de arquitectura — Fase 8 Power BI

## Estado

**Arquitectura aprobada el 17 de octubre de 2026; Gate 8.2 completado el 18 de octubre de 2026.**

Este documento fija la arquitectura aplicada para convertir Gold y Dataverse en un scorecard ejecutivo reproducible. El PBIP/TMDL/PBIR ya fue construido y validado contra `_brief/report-spec.md`; la publicación en Fabric conserva un gate de autorización explícita independiente.

## Decisión principal

La solución se desarrollará como proyecto de Power BI versionable:

```text
Fabric Gold SQL endpoint ─┐
                          ├─ Import → modelo semántico estrella (TMDL)
Dataverse operativo ─────┘                         ↓
                                         reporte PBIR/PBIP
                                                   ↓
                                  Power BI Desktop → Fabric
```

Se elige **Import** para el MVP porque combina dos fuentes, ofrece un comportamiento predecible para el volumen sintético y permite validar cada actualización antes de publicar. DirectQuery solo se reconsiderará si aparece un requisito de latencia que lo justifique. Direct Lake no se usará para el modelo compuesto inicial porque Dataverse sigue siendo una fuente operativa separada.

## Fuentes y responsabilidades

### Fabric Gold — verdad analítica

| Vista | Grano | Uso |
|---|---|---|
| `dbo.vw_dq_score_trend` | snapshot / run global | score, cobertura y tendencia |
| `dbo.vw_dq_rule_performance` | snapshot / regla / fuente | desempeño por regla, dimensión y origen |
| `dbo.vw_dq_exception_register` | instancia de excepción por snapshot | severidad, recurrencia y responsabilidad |
| `dbo.vw_dq_latest_snapshot` | corte global más reciente | KPI ejecutivo actual |

### Dataverse — verdad operativa

- `DQ Remediation Case`: estado, owner, SLA, aprobación, tipo de resolución y confirmación de corrección.
- `DQ Case Activity`: cambios, aprobaciones, escalaciones y reaperturas.
- `DQ Case Evidence`: evidencia de cierre en forma agregada; el reporte no expondrá archivos.
- `DQ Status`: catálogo de estados y orden.
- `DQ Exception Reference`: vínculo estable mediante `Exception Instance ID` y `Recurrence Key`.

La muestra de Dataverse contiene solo un subconjunto de las 923 excepciones Gold. Los KPI operativos se etiquetarán como **casos publicados** y nunca se presentarán como cobertura de toda la población analítica.

## Modelo estrella propuesto

### Hechos

- `FactDQSnapshot`: una fila por corte global.
- `FactRulePerformance`: una fila por corte, regla y fuente.
- `FactException`: una fila por `ExceptionInstanceID`.
- `FactRemediationCase`: una fila por caso publicado.
- `FactCaseActivity`: una fila por evento operativo.

### Dimensiones conformadas

- `DimDate` con roles de snapshot, evaluación, inicio, vencimiento, resolución y actividad.
- `DimRule` con regla, dimensión de calidad, SLA y dominio propietario.
- `DimSourceSystem`.
- `DimSeverity` con orden explícito Critical → Low.
- `DimStatus` con secuencia del ciclo de vida.
- `DimOwner` para el responsable operativo, sin correo visible en la página ejecutiva.
- `DimException` como puente único de `ExceptionInstanceID`; `RecurrenceKey` se conserva para recurrencia entre cortes.

Las relaciones serán `1:*`, de dirección simple desde dimensiones hacia hechos. No se crearán relaciones hecho-a-hecho ni filtros bidireccionales salvo una excepción documentada y probada.

## KPI y denominadores

| KPI | Definición | Denominador / población |
|---|---|---|
| Data Quality Score | `WeightedPassed / WeightedEligible` | checks elegibles ponderados del contexto |
| Exception Rate | `RecordsWithException / RecordsEvaluated` | registros evaluados del contexto |
| Open Published Cases | casos publicados no terminales | casos existentes en Dataverse |
| SLA Compliance | casos terminales resueltos a tiempo / casos terminales con vencimiento | casos publicados elegibles para SLA |
| Confirmed Correction Rate | casos con `Source Correction State = Confirmed Later` / casos Resolved o Waived | casos publicados terminales |
| Recurrence Rate | recurrencias posteriores / claves de recurrencia observadas | excepciones Gold del periodo |

El diccionario definitivo de medidas incluirá nombre técnico, nombre visible, DAX, formato, filtro temporal, numerador, denominador, cero frente a `BLANK()` y prueba de reconciliación.

## Página ejecutiva propuesta

Primera entrega: una página FHD `1920 × 1080`, orientada a People Analytics Lead y Data Owner.

1. Encabezado con corte, estado de actualización y filtros compactos de periodo, fuente y dimensión.
2. Banda ejecutiva compuesta: score actual con delta, tasa de excepción, casos abiertos publicados y cumplimiento de SLA; ningún KPI aislado ocupará el hero completo.
3. Tendencia del score y volumen de excepciones por snapshot.
4. Matriz de riesgo por regla/dimensión con score, fallos, severidad y recurrencia.
5. Distribución de casos publicados por estado y owner.
6. Panel de eficacia: tipo de resolución frente a confirmación posterior de la corrección.
7. Nota visible sobre datos sintéticos y cobertura parcial de Dataverse.

La página debe responder las seis preguntas del charter sin explicación oral. Un detalle operativo o drillthrough se pospone hasta que la página ejecutiva pase reconciliación y revisión visual.

## Parámetros y secretos

El proyecto utilizará parámetros descriptivos, nunca valores codificados:

- `pFabricSqlServer`;
- `pFabricSqlDatabase`;
- `pDataverseEnvironmentUrl`.

Los valores y credenciales se asignarán mediante conexiones de Power BI Desktop/Fabric. Los archivos locales de usuario y credenciales no se versionarán.

## Flujo agentic aprobado para la fase

1. Inspeccionar y reconciliar el esquema fuente.
2. Aprobar la especificación bloqueada del reporte.
3. Crear el modelo completo en una sesión mediante `powerbi-modeling-mcp` y persistirlo como TMDL/PBIP.
4. Crear el reporte mediante `powerbi-report-author`, sin inventar esquemas PBIR.
5. Validar JSON/PBIR después de cada lote lógico.
6. Abrir o recargar en Desktop, capturar las páginas y corregir visualmente.
7. Publicar solo después de reconciliación y aprobación explícita.

## Gates

### Gate 8.0 — preparación

- [x] Desktop disponible.
- [x] CLI de autoría disponible y sano.
- [x] MCP local registrado sin duplicado hospedado.
- [x] Skills oficiales instaladas y fijadas.
- [x] Azure CLI y Fabric CLI aislados en `D:`.
- [x] Arquitectura y límites documentados.
- [x] EULA del MCP revisada por el usuario y aceptación registrada mediante el MCP oficial.

### Gate 8.1 — contrato de datos y especificación

- [x] Endpoint SQL de Fabric y URL de Dataverse identificados sin guardarlos en Git.
- [x] Esquema fuente inspeccionado en vivo.
- [x] Medidas y denominadores aprobados mediante la especificación bloqueada.
- [x] `_brief/report-spec.md` completo.
- [x] `_brief/report-spec.md` aprobado explícitamente para construir.

### Gate 8.2 — modelo y reporte

- [x] PBIP/TMDL/PBIR versionables en el repositorio.
- [x] Totales reconciliados: 6 snapshots, 48 filas regla-snapshot y 923 excepciones para la carga validada de Fase 4.
- [x] Validación estructural sin errores.
- [x] Preview Desktop y revisión por capturas completados.
- [x] Credenciales y archivos locales excluidos del repositorio.

## Estado tras Gate 8.2

1. El modelo importado, las medidas, relaciones y parámetros quedaron persistidos como TMDL.
2. La página ejecutiva quedó persistida como PBIR y se validó con datos actualizados en Desktop.
3. La asociación automática CLI–Desktop quedó verificada usando el `.pbip` propietario y acceso al named pipe local.
4. La publicación y cualquier autenticación de despliegue se reservan para la Fase 9 y requieren autorización separada.

La revisión completa y sus cifras están en `docs/phase-8-gate-review.es.md`.

## Referencias Microsoft

- [Guía de esquema estrella](https://learn.microsoft.com/power-bi/guidance/star-schema)
- [Conector de Dataverse](https://learn.microsoft.com/power-query/connectors/dataverse)
- [Power BI Project (PBIP)](https://learn.microsoft.com/power-bi/developer/projects/projects-overview)
- [Power BI agentic development](https://learn.microsoft.com/power-bi/developer/agentic/power-bi-agentic-overview)
- [Power BI Authoring MCP](https://learn.microsoft.com/power-bi/developer/mcp/power-bi-authoring-mcp)
