# Arquitectura y controles

[← Volver al caso](../README.es.md) · [English](architecture.md)

## Componentes

| Componente | Función |
|---|---|
| Copilot Studio | Orquesta conversación, recuperación de conocimiento, reglas y uso de herramientas |
| Cuatro PDF sintéticos | Aportan políticas sobre ausencias, beneficios, onboarding y documentación de RH |
| Power Automate | Valida el servicio, genera el folio, calcula fechas objetivo y crea el registro |
| HR Service Catalog | Define código, servicio, prioridad, cola y SLA aplicables |
| HR Service Requests | Conserva solicitudes sintéticas y su estado operativo |
| Evaluación de Copilot Studio | Ejecuta preguntas repetibles y compara las respuestas con el resultado esperado |

## Flujo de conocimiento

El agente responde únicamente cuando las fuentes configuradas contienen evidencia suficiente. La respuesta conserva la cita recuperada e identifica el documento y la sección. Si no existe evidencia, no completa la respuesta con conocimiento general: ofrece revisión humana.

Las fuentes son archivos cargados directamente. Durante las pruebas se eliminó una fuente duplicada de OneDrive porque añadía una solicitud de conexión en la evaluación automática.

## Flujo de creación

1. El usuario elige o proporciona un código de servicio.
2. El agente obtiene un resumen no sensible, nombre sintético, correo `@example.com` y consentimiento de contacto.
3. Muestra esos datos y pide confirmación.
4. Espera un nuevo mensaje; el consentimiento de contacto no cuenta como confirmación de creación.
5. Power Automate valida el código contra el catálogo activo.
6. El flujo genera `TicketNumber`, prioridad, cola, estado y fechas de primera respuesta y resolución.
7. El agente muestra únicamente los datos devueltos por la herramienta.

## Controles principales

| Riesgo | Control aplicado |
|---|---|
| Respuesta inventada | Evidencia obligatoria y respuesta explícita cuando la fuente es insuficiente |
| Fuente incorrecta | Solo se cita un documento realmente recuperado |
| Acción sin autorización | Resumen, pregunta de confirmación y espera de un nuevo mensaje |
| Duplicación de tickets | Una llamada por confirmación explícita |
| Uso de datos reales | Nombres sintéticos y dominio obligatorio `@example.com` |
| Información restringida | Prohibición de solicitar, revelar o inferir salario, desempeño o datos médicos individuales |
| Caso sensible | Enrutamiento a `ESC-01` y revisión humana |
| Falsa promesa de servicio | Solo se comunican los SLA devueltos por la herramienta |

## Alcance técnico

El repositorio documenta el diseño y aporta datos sintéticos, instrucciones, resultados y evidencia visual. Las conexiones de Power Platform, identificadores del tenant y credenciales no se publican. El flujo depende de conexiones autenticadas del entorno donde se implemente.
