# Proyecto 3: HR Data Quality & Lifecycle Workbench

Una herramienta de Digital HR para revisar la calidad de los datos de personal y gestionar los casos que requieren atención.

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

RH registra un cambio de puesto, pero la ficha del empleado todavía muestra el anterior. Cuando los sistemas no coinciden, alguien tiene que revisar qué pasó y dejar constancia de cómo se resolvió.

Desarrollé este proyecto con datos sintéticos para cubrir ese proceso: detectar las diferencias, facilitar su revisión y dar seguimiento a los casos hasta su cierre.

## La aplicación y el dashboard

La app de Power Apps permite filtrar los problemas detectados, consultar los datos involucrados y crear o abrir un caso para registrar la investigación y su evidencia.

![Command Center de Power Apps con lista de problemas detectados y detalle del caso](power-apps/tests/e2e/tests/dq-command-center.spec.ts-snapshots/dq-command-center-power-apps-edge-win32.png)

El dashboard de Power BI muestra la calidad de los datos y el avance de los casos. También permite distinguir cuáles se cerraron y cuáles tienen confirmación de que el dato se corrigió en el sistema de origen.

![Dashboard de Power BI con indicadores de calidad y avance de los casos](evidence/phase-9/checkpoint-02-power-bi-public-scorecard.png)

## Cómo funciona

1. **Fabric analiza los datos.** Integra tres fuentes sintéticas —empleados, movimientos de personal y estructura organizacional— y aplica ocho reglas de calidad. Cada problema detectado queda registrado como una excepción.
2. **Dataverse guarda los casos y su historial.** Para la demostración, se importa una selección de excepciones que pueden convertirse en casos de revisión.
3. **Power Apps y Power Automate apoyan la gestión.** La app permite investigar y documentar; los flujos envían avisos, validan requisitos y coordinan las aprobaciones.
4. **Power BI muestra ambas perspectivas.** Presenta los resultados del análisis completo junto con el avance de los casos que se decidieron revisar.

## Por qué separé el análisis de la gestión de casos

Fabric conserva todos los resultados del análisis. Dataverse guarda sólo la información necesaria para gestionar los casos seleccionados. Así, detectar una inconsistencia no implica abrir automáticamente un caso ni asignarle trabajo a una persona.

También mantuve separados el cierre del caso y la confirmación de que el dato se corrigió en origen. Una aprobación no garantiza que el error haya desaparecido. La aplicación documenta la revisión, pero no cambia automáticamente la información de un sistema de RH.

## Desarrollo y aprendizaje

El Command Center utiliza una Generative Page de Power Apps con React y TypeScript. Me apoyé en IA durante el desarrollo e incorporé pruebas de componentes y pruebas con Playwright sobre la app publicada.

Durante las pruebas apareció un problema al crear casos: el formulario se abría vacío, pero algunos campos obligatorios estaban bloqueados. La solución fue crear primero el registro con los datos necesarios y después abrirlo. Resolverlo me ayudó a entender qué debía hacer la interfaz y qué debía quedar a cargo de Dataverse y los flujos.

## Más detalles

[Cómo está construido](docs/technical-overview.md) · [Evidencias y pruebas](evidence/phase-9/evidence-manifest.md) · [Código y archivos del proyecto](./)

Miguel — [Perfil de GitHub](https://github.com/MiguelPR-99)
