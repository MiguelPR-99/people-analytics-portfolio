# Proyecto 3: HR Data Quality & Lifecycle Workbench

Una solución de Digital HR para detectar inconsistencias en datos laborales y dar seguimiento a su revisión.

[← Volver al portafolio](../../README.md) · [English](README.en.md)

![Microsoft Fabric](https://img.shields.io/badge/Microsoft%20Fabric-5B5FC7?logo=microsoft&logoColor=white)
![Dataverse](https://img.shields.io/badge/Dataverse-088142?logo=microsoftdataverse&logoColor=white)
![Power Apps](https://img.shields.io/badge/Power%20Apps-742774?logo=powerapps&logoColor=white)
![Power Automate](https://img.shields.io/badge/Power%20Automate-0066FF?logo=powerautomate&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?logo=powerbi&logoColor=black)
![Python / PySpark](https://img.shields.io/badge/Python%20%2F%20PySpark-3776AB?logo=python&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-CC2927?logo=microsoftsqlserver&logoColor=white)

> Datos y escenarios sintéticos. Proyecto independiente, sin afiliación ni respaldo de Siemens Energy.

## El problema

Un cambio de puesto puede aparecer como completado en los movimientos laborales y seguir sin reflejarse en el registro del empleado. Esa diferencia dificulta saber qué información utilizar y quién debe revisarla.

Desarrollé este caso para conectar la detección de inconsistencias con su investigación: identificar qué no coincide, abrir un caso cuando sea necesario y conservar la evidencia de lo que se hizo.

## La solución en uso

En Power Apps, la persona responsable de revisar los datos puede filtrar excepciones, consultar su contexto y crear o abrir un caso para documentar la investigación.

![Command Center de Power Apps con cola de excepciones y contexto del caso](power-apps/tests/e2e/tests/dq-command-center.spec.ts-snapshots/dq-command-center-power-apps-edge-win32.png)

En Power BI, el equipo puede consultar la calidad de los datos y el avance de los casos. El reporte distingue un cierre administrativo de una corrección confirmada en el sistema de origen.

![Reporte de Power BI con indicadores de calidad y seguimiento de casos](evidence/phase-9/checkpoint-02-power-bi-public-scorecard.png)

## Cómo funciona

1. **Fabric prepara y contrasta los datos.** Tres fuentes sintéticas representan empleados, movimientos laborales y estructura organizacional. Ocho reglas detectan inconsistencias y conservan su historial.
2. **Dataverse registra una muestra para revisión.** La demostración publica excepciones seleccionadas y mantiene separados el problema detectado, el caso y sus actividades.
3. **Power Apps y Power Automate coordinan el trabajo.** La aplicación reúne el contexto y la evidencia; los flujos gestionan avisos, validaciones y aprobaciones.
4. **Power BI reúne el seguimiento.** Combina el análisis de Fabric con los casos de Dataverse, sin presentar la muestra operativa como si fuera toda la población.

## Decisiones importantes

Conservé el análisis completo en Fabric y una muestra operativa en Dataverse. Detectar un problema y asignarlo a una persona son pasos distintos; publicar todos los resultados como casos habría convertido la revisión en una cola difícil de gestionar.

También separé el resultado del caso de la confirmación de corrección del origen. Una aprobación o un cierre no bastan para demostrar que el problema dejó de aparecer. La aplicación apoya la revisión humana y no modifica automáticamente un sistema de RH.

## Construcción y aprendizaje

La interfaz utiliza una Generative Page de Power Apps con React y TypeScript. Me apoyé en IA durante el desarrollo e incorporé pruebas de componentes y comprobaciones con Playwright sobre la aplicación publicada.

Una iteración corrigió la creación de casos: el formulario inicial tenía campos obligatorios bloqueados. La solución crea el registro con los datos necesarios antes de abrirlo. Este trabajo me ayudó a entender cómo distribuir responsabilidades entre la interfaz, los datos y la automatización.

## Explorar el caso

[Recorrido técnico y decisiones de diseño](docs/technical-overview.md) · [Evidencias y pruebas](evidence/phase-9/evidence-manifest.md) · [Código y artefactos](./)

Miguel — [Perfil de GitHub](https://github.com/MiguelPR-99)
