# Ruta interna de desarrollo — Proyecto 3

> Esta ruta organiza el trabajo incremental. Cada fase termina con una revisión antes de avanzar; el README público se construirá al final.

## Estado general

| Fase | Resultado | Estado |
|---|---|---|
| 0 | Accesos y permisos validados | Completada |
| 1 | Charter y alcance aprobados | Completada |
| 2 | Diseño de datos y reglas | Completada |
| 3 | Generador sintético validado | Completada |
| 4 | Fabric Bronze/Silver/Gold | Completada |
| 5 | Modelo transaccional en Dataverse | Completada |
| 6 | Workbench en Power Apps | Completada |
| 7 | Automatización y aprobaciones | Completada |
| 8 | Scorecard en Power BI | Completada |
| 9 | Pruebas, evidencia y publicación | Completada |

## Fase 0 — Accesos y permisos

### Objetivo

Confirmar que la cuenta institucional permite trabajar con los componentes previstos sin iniciar prematuramente la prueba de Fabric.

### Evidencia de salida

- Power Apps y Dataverse disponibles.
- Power Automate disponible.
- Power BI disponible.
- Fabric accesible y prueba todavía sin consumir.

### Gate

Completado según la comprobación realizada por el usuario.

## Fase 1 — Charter y alcance

### Objetivo

Acordar problema, usuarios, decisiones, límites, arquitectura objetivo y definición de terminado.

### Entregables

- `docs/project-charter.es.md`
- `docs/roadmap.es.md`

### Gate para avanzar

- Escenario aprobado.
- Alcance del MVP aprobado.
- Confirmación de que el documento es interno y no sustituye al README final.

## Fase 2 — Diseño de datos y reglas

### Objetivo

Definir el contrato de las tres fuentes, el ciclo de vida, las llaves, las vigencias y la matriz de calidad antes de generar información.

### Entregables

- Especificación de datos sintéticos.
- Diccionario preliminar.
- Modelo conceptual y granularidad.
- Matriz de cinco a ocho reglas.
- Catálogo de severidad y SLA.
- Casos positivos, negativos y de borde.

### Gate para avanzar

- Cada campo existe por una razón funcional.
- Cada anomalía planeada activa una regla conocida.
- No se incluyen datos sensibles innecesarios.
- Los resultados esperados se pueden probar automáticamente.

## Fase 3 — Generación sintética

### Objetivo

Construir una fuente reproducible con patrones controlados y errores deliberados.

### Entregables

- Configuración versionada.
- Script generador.
- Semilla fija.
- Archivos raw.
- Manifiesto con totales y anomalías esperadas.
- Pruebas automatizadas del generador.

### Gate para avanzar

- La regeneración produce los mismos resultados.
- Los totales coinciden con el manifiesto.
- Cada regla tiene suficientes casos válidos e inválidos.

## Fase 4 — Microsoft Fabric

### Objetivo

Implementar la arquitectura analítica y la detección reproducible de excepciones.

### Activación controlada

La prueba de Fabric se activará al inicio de esta fase, no antes. Para entonces estarán terminados los archivos, contratos y pruebas locales, reduciendo el tiempo consumido en diseño exploratorio.

### Entregables

- Workspace de desarrollo.
- Lakehouse Bronze/Silver/Gold.
- Pipeline de ingesta incremental.
- Transformaciones SQL.
- Notebook Python/PySpark.
- Tablas Gold de excepciones, métricas y reconciliación.
- Evidencia de ejecuciones y lineage.

### Gate para avanzar

- Bronze conserva el origen.
- Silver normaliza sin perder trazabilidad.
- Gold reproduce los resultados esperados del manifiesto.
- Una nueva carga no duplica registros procesados.

## Fase 5 — Dataverse

### Objetivo

Modelar la gestión transaccional de casos sin mezclarla con el histórico analítico.

### Entregables

- Tablas de casos, actividades, evidencia y catálogo de estados.
- Relaciones y reglas de negocio.
- Identificador que vincule el caso con la excepción de Fabric.
- Datos de demostración seguros.

### Gate para avanzar

- Se puede crear, asignar, actualizar y auditar un caso.
- La excepción original permanece inmutable.
- Los estados inválidos están controlados.

## Fase 6 — Power Apps

### Objetivo

Construir la interfaz de trabajo del HR Data Steward mediante una arquitectura híbrida:

- `DQ Command Center` como Generative Page oficial de Power Apps desarrollada en React + TypeScript.
- aplicación basada en modelo como núcleo transaccional para formularios, vistas, reglas, seguridad y auditoría.
- Dataverse como fuente compartida de verdad.
- prototipo Canvas conservado únicamente como respaldo y referencia visual.

### Pantallas candidatas

1. Resumen de calidad.
2. Cola de excepciones.
3. Comparación entre fuentes.
4. Detalle y evidencia.
5. Asignación y aprobación.
6. Historial.

El MVP podrá combinar pantallas si esto mejora la claridad y reduce complejidad.

### Decisión de implementación

La Generative Page sustituye solamente la implementación del front-end del Command Center. No reemplaza el modelo de Dataverse, la aplicación basada en modelo ni sus formularios, vistas y reglas ya validados. El código local se versionará como React + TypeScript y se publicará mediante Power Platform CLI.

### Gate para avanzar

- El usuario puede completar el flujo principal sin editar tablas directamente.
- Filtros, estados y mensajes de validación funcionan.
- La app no expone información innecesaria.
- La Generative Page consulta Dataverse con las API soportadas, conserva la excepción como solo lectura y abre el formulario transaccional existente para las operaciones completas.

### Cierre

El gate fue revalidado el 16 de octubre de 2026 después de corregir `Create remediation case`. La página publicada crea primero un caso completo mediante `dataApi.createRow`, usa la variable `DQ Operational App URL`, inicializa estado y SLA, y abre el GUID creado. La validación incluye typecheck, 5/5 pruebas de componente, 4/4 pruebas E2E no mutantes y 1/1 prueba E2E controlada de creación.

## Fase 7 — Power Automate

### Objetivo

Automatizar coordinación y control, manteniendo la decisión humana.

### Flujos mínimos

1. Asignación y notificación de una excepción.
2. Aprobación y escalación por SLA.

### Gate para avanzar

- Los flujos manejan éxito, rechazo y error.
- No generan notificaciones duplicadas.
- La respuesta queda registrada en Dataverse.

### Cierre

Gate aprobado el 16 de octubre de 2026. Los dos flujos están publicados, usan referencias de conexión y variables de entorno, registran errores mediante scopes Catch, conservan idempotencia y pasaron los caminos Approved, Rejected, Waived, validación y timeout. Véase `docs/phase-7-gate-review.es.md`.

## Fase 8 — Power BI

### Objetivo

Presentar la salud de los datos y del proceso de remediación en una página ejecutiva clara.

### Inicio formal

La fase comenzó el 17 de octubre de 2026 con una preparación local reproducible y una decisión de arquitectura documentada. El flujo de trabajo será `PBIP + TMDL + PBIR`, con autoría asistida por las skills oficiales de Microsoft, modelado mediante el MCP local de Power BI, validación estructural por CLI y revisión visual en Power BI Desktop. Véanse `docs/phase-8-bi-design.es.md` y `docs/phase-8-local-environment.es.md`.

La especificación bloqueada fue aprobada y los artefactos PBIP/TMDL/PBIR fueron construidos y validados. Las credenciales permanecen fuera del repositorio y no se ha publicado al tenant.

### Entregables

- Modelo semántico.
- Diccionario de medidas.
- Página ejecutiva.
- Validación de cifras contra Gold.

### Gate para avanzar

- Cada KPI tiene definición y denominador.
- Los totales se reconcilian con Fabric.
- La página responde las preguntas de negocio sin depender de explicación oral.

### Cierre

Gate aprobado el 18 de octubre de 2026. El modelo reconcilia 6 cortes, 48 filas regla-corte y 923 excepciones; el PBIR no presenta errores estructurales; Desktop actualiza y renderiza correctamente; y la captura automatizada quedó conservada en `evidence/power-bi/`. Véase `docs/phase-8-gate-review.es.md`. La publicación permanece fuera de alcance hasta una autorización explícita en la Fase 9.

## Fase 9 — Pruebas, evidencia y publicación

### Objetivo

Demostrar el recorrido completo y convertir la implementación en un caso comprensible para reclutadores y perfiles técnicos.

### Inicio formal

La fase se cerró el 18 de octubre de 2026. El gate transversal, la matriz de aceptación y los límites de publicación están definidos en `docs/phase-9-test-and-publication-plan.es.md`. Los parámetros se anonimizaron, se completó la narrativa bilingüe, se redujo la evidencia pública a dos capturas esenciales y el caso se integró en el repositorio del portafolio. Fabric permanece fuera de alcance.

### Entregables

- Pruebas finales de datos y funciones.
- Capturas verificadas.
- Guía para video opcional de 60–90 segundos.
- Arquitectura y limitaciones.
- README en español e inglés.
- Selección de artefactos publicables.
- Integración del caso en la portada del portafolio.

### Gate de terminado

- La evidencia muestra detección, priorización, remediación, aprobación y actualización de métricas.
- No hay secretos, datos reales ni identificadores institucionales.
- Todos los enlaces funcionan desde GitHub.
- La narrativa distingue claramente simulación, resultados y limitaciones.

## Forma de trabajo

1. Se trabaja una fase a la vez.
2. Cada fase comienza con una decisión de diseño y termina con evidencia verificable.
3. No se activan servicios con vencimiento antes de necesitarlos.
4. No se construye Power BI ni Power Apps antes de estabilizar los contratos de datos.
5. El README público describe lo que realmente se construyó, no lo que se planeó construir.

