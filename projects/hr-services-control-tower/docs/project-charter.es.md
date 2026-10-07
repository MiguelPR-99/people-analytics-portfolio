# Project charter — HR Services / Service Delivery Control Tower

## 1. Propósito

Diseñar un producto de analítica operativa para un equipo ficticio de **HR Services** que permita monitorear la demanda de solicitudes de empleados, el cumplimiento de acuerdos de servicio, la salud del backlog, la calidad de la resolución y la experiencia del empleado.

El caso está orientado a demostrar competencias relevantes para posiciones trainee de Recursos Humanos y HR Services en una empresa industrial y energética global: Excel y Power Query, Power BI, calidad de datos, documentación, mapeo de procesos, mejora continua, atención al detalle y mentalidad de servicio.

> Este es un proyecto personal de aprendizaje. La empresa, las personas, los procesos, los datos, los resultados y las metas son completamente ficticios. El caso no representa procedimientos ni información interna de Siemens Energy.

## 2. Escenario de negocio

**Empresa ficticia:** EnergiaNova Industrial México  
**Contexto:** fabricante y prestador de servicios para infraestructura energética con operaciones en México.  
**Población atendida:** aproximadamente 1,200 colaboradores distribuidos entre una planta, un centro de servicios y oficinas corporativas.  
**Equipo de atención:** HR Services recibe y resuelve solicitudes relacionadas con nómina, beneficios, tiempo y asistencia, documentación, datos personales y movimientos del ciclo de vida del empleado.

La información operativa se encuentra fragmentada entre archivos de seguimiento y canales de entrada. Los líderes pueden observar casos individuales, pero no cuentan con una vista consistente para responder:

- ¿Dónde se concentra la demanda?
- ¿Qué servicios incumplen con mayor frecuencia su SLA?
- ¿Qué casos forman el backlog y cuánto tiempo llevan abiertos?
- ¿Qué factores generan reaperturas, transferencias o contactos repetidos?
- ¿Cómo se relacionan la calidad de la resolución y la satisfacción del empleado?
- ¿Dónde conviene estandarizar, redistribuir capacidad o mejorar el proceso?

## 3. Decisión que habilita

El Control Tower ayudará a un responsable de HR Services a priorizar acciones operativas semanales y mejoras mensuales:

1. Redistribuir carga entre equipos o responsables.
2. Escalar casos vencidos o de alta prioridad.
3. Identificar servicios con retrabajo o solicitudes incompletas.
4. Revisar causas de incumplimiento y cuellos de botella.
5. Seleccionar procesos candidatos para estandarización o automatización.

El tablero será un producto de apoyo a decisiones. No asignará sanciones, evaluaciones de desempeño ni decisiones laborales automáticas.

## 4. Usuarios

- **HR Services Lead:** salud general de la operación, SLA, backlog y capacidad.
- **Service Delivery Analyst:** causas, tendencias, calidad, transferencias y reaperturas.
- **HR Operations Specialist:** cola de trabajo, antigüedad y prioridades.
- **HR Business Partner:** demanda y experiencia del empleado por unidad o ubicación, solo en forma agregada.

## 5. Alcance del MVP

El MVP abarcará 18 meses de operación sintética y analizará:

- Volumen recibido, cerrado y pendiente.
- Backlog total y por rangos de antigüedad.
- Cumplimiento de SLA de primera respuesta y resolución.
- Tiempo de primera respuesta y tiempo de resolución.
- Resolución en primer contacto.
- Reaperturas y transferencias.
- Casos incompletos al momento de la recepción.
- Satisfacción posterior al cierre.
- Cortes por servicio, prioridad, canal, ubicación, unidad organizacional, equipo y responsable.
- Evolución semanal y mensual.

Servicios incluidos:

1. Payroll & Compensation.
2. Benefits.
3. Time & Attendance.
4. Employee Data Changes.
5. HR Documents & Certificates.
6. Onboarding.
7. Offboarding.

Canales incluidos: portal, correo, Teams y teléfono.

## 6. Fuera de alcance del MVP

- Predicción del desempeño de agentes.
- Clasificación automática con inteligencia artificial.
- Información médica, salarios individuales o texto libre sensible.
- Integración real con SAP, ServiceNow, Workday u otro HRIS.
- Desarrollo inmediato de Power Apps o Power Automate.
- Afirmaciones sobre ahorros reales o mejoras ya implementadas.

Power Apps, Power Automate, process mining y un agente de triaje podrán plantearse después como extensiones, una vez que el Control Tower base esté terminado y validado.

## 7. Diseño de la historia analítica

Los datos sintéticos contendrán patrones controlados para que el análisis tenga una narrativa comprobable:

- Mayor demanda de nómina al cierre de mes.
- Mayor proporción de solicitudes incompletas por correo que por portal.
- Retrasos temporales de beneficios asociados a dependencias externas.
- Un incremento de backlog en una ubicación durante un periodo de capacidad reducida.
- Menor satisfacción cuando existen transferencias o reaperturas.
- Una mejora gradual en Employee Data Changes después de una estandarización hipotética del formulario.

Estos patrones se documentarán antes de generar los datos y se validarán después mediante pruebas reproducibles. Los hallazgos del reporte deberán derivarse de los datos, no redactarse de antemano como si fueran resultados reales.

## 8. Preguntas de negocio

1. ¿La operación está absorbiendo la demanda o el backlog está creciendo?
2. ¿Qué servicios, ubicaciones y prioridades explican los incumplimientos de SLA?
3. ¿Cuánto tiempo permanece el trabajo en cada estado y dónde se acumula la espera?
4. ¿Qué canales generan más solicitudes incompletas o retrabajo?
5. ¿Qué proporción se resuelve en el primer contacto?
6. ¿Qué combinación de reaperturas, transferencias y demoras deteriora la satisfacción?
7. ¿Qué proceso ofrece la mejor oportunidad de mejora continua?

## 9. Entregables end-to-end

- Generador reproducible de datos sintéticos.
- Archivos de datos crudos y dataset analítico.
- Diccionario de datos y catálogo de servicios/SLA.
- Reporte de validación y pruebas de calidad.
- Modelo estrella y documentación de relaciones.
- Medidas DAX y diccionario de KPIs.
- Reporte Power BI con capturas verificadas.
- SIPOC y propuesta as-is/to-be para un proceso seleccionado.
- Hallazgos, acciones, limitaciones y nota de uso responsable.
- README completo en inglés y español.
- Archivos publicados dentro del monorepo del portafolio.

## 10. Criterios de terminado

El proyecto se considerará terminado cuando:

- Los datos se puedan regenerar con una semilla documentada.
- Las reglas de calidad y los totales esperados pasen sus pruebas.
- Cada KPI tenga definición, fórmula, nivel de detalle y limitaciones.
- El reporte responda las siete preguntas de negocio sin exponer datos personales.
- Los hallazgos sean reproducibles desde el dataset publicado.
- La documentación permita a otra persona comprender el caso sin abrir Power BI.
- Los enlaces, archivos y capturas funcionen desde GitHub.

