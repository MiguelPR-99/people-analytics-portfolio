# Project charter interno — HR Data Quality & Employee Lifecycle Workbench

> Documento interno de planeación. No es el README público del caso y no se presentará como trabajo terminado hasta que la solución, las pruebas y la evidencia estén completas.

## 1. Propósito

Diseñar una solución end-to-end de HR Data que convierta archivos de empleados y movimientos dispersos en información validada, excepciones accionables y evidencia de remediación.

El caso demostrará la capacidad de conectar ingeniería de datos, gobierno de información, operación de Recursos Humanos y Power Platform. El resultado debe permitir que un **HR Data Steward** detecte problemas, investigue el registro afectado, asigne la corrección, obtenga una aprobación cuando corresponda y conserve trazabilidad del cierre.

## 2. Contexto y posicionamiento

El escenario utilizará una empresa ficticia del sector industrial y energético, con operaciones en México y relación con una estructura global. La complejidad, los tipos de procesos y el stack se diseñarán con enfoque a competencias observadas en Siemens Energy, sin afirmar que representan su arquitectura, datos, políticas o procedimientos internos.

Todos los nombres, personas, identificadores, movimientos y resultados serán sintéticos. El proyecto es un artefacto independiente de aprendizaje y portafolio; no está afiliado, respaldado ni validado por Siemens Energy.

## 3. Problema de negocio

La organización recibe información laboral desde varios sistemas y equipos. Los archivos pueden ser técnicamente válidos de forma individual, pero presentar problemas al integrarse:

- empleados activos sin manager válido;
- centros de costo inexistentes o fuera de vigencia;
- posiciones duplicadas o asignaciones incompatibles;
- fechas de ingreso, movimiento o terminación incoherentes;
- estados diferentes entre el HRIS global y la operación local;
- campos obligatorios incompletos;
- eventos de ciclo de vida sin correspondencia con el estado actual;
- errores recurrentes que vuelven a aparecer después de una corrección.

Actualmente, las excepciones se revisarían manualmente en hojas separadas, sin una cola única, responsables, SLA ni historial de resolución.

## 4. Decisión que habilita

La solución permitirá responder semanalmente:

1. ¿Qué tan confiables son los datos de empleados por dimensión, dominio y sistema fuente?
2. ¿Qué excepciones requieren atención inmediata y quién es responsable?
3. ¿Qué registros presentan diferencias entre el estado actual y los eventos del ciclo de vida?
4. ¿Cuánto tardan las incidencias en resolverse y cuáles exceden el SLA?
5. ¿Qué reglas, fuentes o unidades generan errores recurrentes?
6. ¿La remediación mejora la calidad o solamente cierra casos de forma administrativa?

El producto apoyará la priorización y corrección humana. No modificará automáticamente un HRIS ni tomará decisiones laborales.

## 5. Usuarios

- **HR Data Steward:** revisa, asigna, documenta y propone la resolución de excepciones.
- **HR Operations Specialist:** valida movimientos y aporta evidencia operativa.
- **HR Data Owner / Approver:** aprueba correcciones de mayor impacto o excepciones justificadas.
- **People Analytics Lead:** monitorea calidad, recurrencia, aging y cumplimiento de SLA en forma agregada.
- **Auditor o responsable de gobierno:** consulta el historial de decisiones y cambios.

## 6. Alcance funcional del MVP

### Fuentes sintéticas

El MVP utilizará tres dominios de entrada:

1. **Global HRIS worker snapshot:** registro maestro vigente de empleados.
2. **Local employee lifecycle events:** altas, transferencias, cambios organizacionales, ausencias y bajas.
3. **Organizational reference data:** managers, posiciones, unidades, ubicaciones y centros de costo válidos con vigencias.

Los nombres finales de archivos, columnas, granularidad y llaves se definirán en el diseño de datos antes de generar registros.

### Ciclo de vida representado

- Pre-hire / alta preparada.
- Onboarding.
- Empleado activo.
- Transferencia o cambio organizacional.
- Ausencia temporal.
- Offboarding.
- Terminación.

### Dimensiones de calidad

- Completitud.
- Validez.
- Unicidad.
- Consistencia entre sistemas.
- Integridad referencial.
- Coherencia temporal.
- Oportunidad de actualización.

### Reglas iniciales

El MVP implementará entre cinco y ocho reglas. La propuesta inicial es:

1. Campos obligatorios completos según estado laboral.
2. Identificador de empleado único en el snapshot vigente.
3. Manager informado y existente para empleados que requieren supervisión.
4. Centro de costo válido y vigente en la fecha efectiva.
5. Posición y asignación organizacional compatibles y sin duplicidad activa.
6. Secuencia lógica de fechas de ingreso, movimientos y terminación.
7. Estado laboral coherente con el último evento del ciclo de vida.
8. Reconciliación de atributos críticos entre HRIS global y eventos locales.

Cada regla tendrá código, descripción, dimensión, severidad, campos evaluados, condición, resultado esperado, propietario funcional y SLA.

### Flujo de remediación

La cola operativa utilizará, como mínimo, estos estados:

`New → Triaged → In progress → Pending approval → Resolved`

También podrá registrar `Rejected` o `Waived` cuando exista una justificación aprobada. Cerrar un caso requerirá evidencia, comentario y marca temporal; no se sobrescribirá la excepción original.

## 7. Arquitectura objetivo

```text
Fuentes sintéticas CSV/JSON
          ↓
Microsoft Fabric Data Factory
          ↓
Lakehouse Bronze → Silver → Gold
          ↓
Reglas de calidad y reconciliación
          ↓
Gold: excepciones, métricas y trazabilidad analítica
          ↓
Power BI: HR Data Quality Scorecard

Gold / cola publicada
          ↓
Power Apps: workbench operativo
          ↓
Dataverse: asignación, comentarios, estado y auditoría
          ↓
Power Automate: avisos, aprobación y escalación por SLA
```

Fabric será la plataforma analítica y Dataverse el sistema transaccional de remediación. La aplicación no intentará editar directamente tablas analíticas de solo lectura.

La integración con Microsoft 365 Users podrá utilizarse para reconocer al usuario y proponer aprobadores. No será una dependencia obligatoria si la cuenta educativa no contiene una jerarquía organizacional útil.

## 8. Entregables del MVP

- Especificación reproducible de datos sintéticos.
- Generador y semilla documentada.
- Archivos raw y manifiesto de generación.
- Diccionario de datos y contrato de cada fuente.
- Matriz de reglas de calidad.
- Lakehouse con capas Bronze, Silver y Gold.
- Pipeline incremental en Fabric.
- Transformaciones SQL y al menos un notebook Python/PySpark.
- Tabla analítica de excepciones y métricas.
- Modelo de Dataverse para casos y actividades de remediación.
- Aplicación híbrida de Power Apps: Generative Page React + TypeScript como Command Center y aplicación basada en modelo como núcleo transaccional. El prototipo Canvas se conserva como respaldo.
- Dos flujos de Power Automate: asignación/notificación y aprobación/escalación.
- Una página ejecutiva de Power BI como mínimo.
- Pruebas de datos y casos funcionales.
- Evidencia visual y video end-to-end de 60–90 segundos.
- Documentación final bilingüe.
- Nota de limitaciones, privacidad y uso responsable.

## 9. Indicadores iniciales

- Data Quality Score global.
- Score por dimensión de calidad.
- Registros evaluados y registros con excepción.
- Excepciones por regla, severidad, fuente y dominio.
- Excepciones abiertas y resueltas.
- Aging promedio y por rango.
- Resolución dentro del SLA.
- First-time-right de la remediación.
- Tasa de recurrencia.
- Diferencias entre sistemas por atributo crítico.

Las fórmulas definitivas y sus denominadores se documentarán antes de construir Power BI.

## 10. Fuera de alcance del MVP

- Conexión con sistemas reales de Siemens Energy, SAP, Workday u otro HRIS.
- Uso de datos personales reales.
- Escritura automática sobre el sistema fuente.
- Decisiones automáticas sobre contratación, desempeño, compensación o terminación.
- Predicción de rotación o scoring individual de empleados.
- Master Data Management empresarial completo.
- Procesamiento en tiempo real.
- Aplicación productiva para múltiples organizaciones.
- Agente generativo o nueva solución de Copilot como componente central.

## 11. Controles de privacidad y uso responsable

- Los identificadores y perfiles serán completamente sintéticos.
- No se incluirán salario, información médica, desempeño individual ni texto libre sensible.
- Las capturas de la cuenta institucional ocultarán correo e identificadores técnicos.
- Power Apps mostrará solamente los atributos necesarios para investigar cada excepción.
- Las correcciones relevantes conservarán intervención y aprobación humana.
- Una incidencia resuelta no equivale automáticamente a que el dato fuente haya sido corregido; ambos estados deberán distinguirse.

## 12. Criterios de terminado

El proyecto se considerará terminado cuando:

- los datos puedan regenerarse con una semilla documentada;
- todas las reglas tengan definición, severidad, propietario y casos de prueba;
- Bronze preserve los datos de entrada y Silver aplique normalización trazable;
- Gold produzca excepciones y métricas reconciliables con las pruebas;
- Power Apps permita revisar, asignar y cerrar un caso con evidencia;
- Power Automate ejecute los dos flujos definidos y conserve su resultado;
- Power BI responda las seis preguntas de negocio;
- la demostración muestre al menos una excepción desde su detección hasta su resolución;
- la documentación permita comprender el caso sin acceso al tenant;
- el README público se redacte únicamente después de validar todas las evidencias.

## 13. Decisiones confirmadas

- El caso será ficticio, pero orientado a competencias relevantes para Siemens Energy.
- El desarrollo técnico y la documentación de trabajo vivirán localmente.
- GitHub mostrará la narrativa y los entregables seleccionados cuando el proyecto esté finalizado.
- La prueba de Fabric permanecerá sin activar hasta que estén aprobados el modelo, las fuentes y las reglas.
- El MVP priorizará profundidad y trazabilidad sobre cantidad de pantallas o tecnologías.
- El `DQ Command Center` se implementará como Generative Page oficial de Power Apps en React + TypeScript; este cambio sustituye únicamente el front-end inicialmente prototipado en Canvas y mantiene Dataverse y la aplicación basada en modelo.

## 14. Decisiones de diseño posteriores al charter

La Fase 2 resolvió el horizonte, frecuencia, volumen objetivo, atributos críticos, ocho reglas del MVP, severidades, SLA, fórmula del Data Quality Score y estructura analítica prevista. Estas decisiones se documentan en:

- `docs/data-design.es.md`
- `docs/data-dictionary.es.md`
- `docs/quality-rules.es.md`
- `config/synthetic-data-spec.yaml`

Permanecen abiertas para fases posteriores:

- diseño físico de Dataverse;
- estrategia técnica de intercambio entre Fabric y Dataverse compatible con el tenant;
- alcance visual final de Power Apps y Power BI.

