# Panorama técnico

[← Caso principal](../README.es.md) · [English](technical-overview.md)

Esta página es el punto de entrada técnico del Proyecto 3. El caso público se mantiene breve; los enlaces siguientes conservan las decisiones, controles y artefactos reproducibles que lo respaldan.

## Arquitectura y límites

| Capa | Responsabilidad | Artefactos principales |
|---|---|---|
| Fuentes sintéticas | Registros reproducibles de empleados, ciclo de vida y organización con anomalías controladas | [`config/`](../config/) · [`data/`](../data/) · [`scripts/generate_synthetic_data.py`](../scripts/generate_synthetic_data.py) |
| Microsoft Fabric | Preservación Bronze, normalización Silver, reglas Gold, recurrencia y reconciliación | [`notebooks/`](../notebooks/) · [`sql/`](../sql/) · [implementación](fabric-implementation.es.md) |
| Dataverse | Casos transaccionales, actividades, evidencia, catálogo de estados, propiedad y auditoría | [`dataverse/`](../dataverse/) · [modelo](dataverse-design.es.md) |
| Power Apps | Generative Page React + TypeScript para priorización y app basada en modelo para transacciones controladas | [`power-apps/`](../power-apps/) · [decisión de arquitectura](generative-page-architecture.es.md) |
| Power Automate | Asignación, notificación, aprobación, timeout, registro de errores e idempotencia | [diseño](phase-7-automation-design.es.md) · [revisión del gate](phase-7-gate-review.es.md) |
| Power BI | Modelo semántico PBIP/TMDL/PBIR y scorecard ejecutivo de una página | [`power-bi/`](../power-bi/) · [diseño BI](phase-8-bi-design.es.md) |

Fabric es la fuente de verdad analítica. Dataverse almacena únicamente las excepciones elegidas para remediación y su historial operativo. Power Apps y Power Automate no sobrescriben los registros del sistema fuente.

## Reproducibilidad

El proyecto utiliza semilla fija, esquemas versionados, conexiones parametrizadas, artefactos Power BI en control de versiones, pruebas de componentes y resultados de gate legibles por máquina.

Desde la carpeta del proyecto:

```powershell
python -m unittest discover -s scripts/tests -v
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify_phase9.ps1
```

Los smoke tests del tenant y la única mutación controlada son opt-in porque requieren un entorno Power Platform conectado. Credenciales, estado de autenticación, caché de Power BI y configuración local de Desktop están excluidos por Git.

## Parámetros públicos de conexión

El modelo semántico versionado contiene valores de ejemplo seguros:

- `contoso.datawarehouse.fabric.microsoft.com`
- `lh_hr_data_quality`
- `https://contoso.crm.dynamics.com`

Antes de actualizar, se deben configurar los tres parámetros de Power Query en Power BI Desktop con los valores del entorno destino. La publicación en GitHub no incluye despliegue en Fabric.

## Ruta de validación

- [Validación de datos sintéticos](synthetic-data-validation.es.md)
- [Gate de Fabric](phase-4-gate-review.es.md)
- [Gate de Dataverse](phase-5-gate-review.es.md)
- [Gate de Power Apps](phase-6-gate-review.es.md)
- [Gate de Power Automate](phase-7-gate-review.es.md)
- [Gate de Power BI](phase-8-gate-review.es.md)
- [Gate de publicación de Fase 9](phase-9-test-and-publication-plan.es.md)
- [Evidencia curada](../evidence/phase-9/evidence-manifest.es.md)

## Límites conocidos

- Los volúmenes y patrones son intencionalmente pequeños y sintéticos.
- El subconjunto de casos publicados demuestra el flujo; no representa toda la población analítica.
- La muestra actual no contiene cierres elegibles para SLA, por lo que la tarjeta informa correctamente que no hay casos elegibles.
- Power Platform se validó en un tenant de desarrollo, no como despliegue productivo multientorno.
- La corrección del sistema fuente se representa como un estado gobernado; el proyecto nunca escribe en un HRIS real.
