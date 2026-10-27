# Evaluación del agente

[← Caso principal](../README.md) · [English](evaluation-report.en.md)

La evaluación revisa si el agente responde a preguntas sobre las políticas, reconoce cuando falta información y respeta las instrucciones de privacidad e idioma. El conjunto final contiene quince preguntas de respuesta única. La conversación para crear un ticket se muestra por separado en la demostración.

## Qué se evaluó

Las preguntas cubren vacaciones, beneficios, onboarding, documentos de RH, información no incluida en las fuentes, datos personales restringidos, asuntos sensibles y respuestas en español e inglés.

Se utilizó la evaluación integrada de Copilot Studio con un usuario autenticado y cuatro PDF sintéticos cargados directamente. Se aplicaron dos métodos:

- **Calidad de la respuesta:** el evaluador de IA califica la respuesta según sus criterios.
- **Coincidencia de significado:** compara la respuesta con el resultado esperado. El umbral configurado fue 50.

[Preguntas y respuestas esperadas](../evaluation/test-cases.csv) · [Exportación de resultados](../evaluation/final-results.csv)

## Resultado final

| Método | Preguntas aprobadas | Cómo interpretarlo |
|---|---:|---|
| Calidad de la respuesta | 12 de 15 (80%) | Tres respuestas fueron clasificadas como “sin responder”. |
| Coincidencia de significado | 15 de 15 (100% del conjunto) | Todas aprobaron el criterio configurado frente a la respuesta esperada. |

El 100% corresponde a la proporción de preguntas aprobadas en este conjunto. No significa que las respuestas fueran idénticas a las esperadas ni que el agente tenga un 100% de precisión ante cualquier consulta.

## Por qué tres respuestas no aprobaron el primer método

El evaluador clasificó como “sin responder” las respuestas a estas solicitudes:

1. Una política de trabajo remoto que no estaba incluida en las fuentes.
2. El salario, desempeño e información médica de una persona.
3. Una determinación individual sobre permisos legales o elegibilidad médica de un país.

En esos casos se esperaba que el agente no proporcionara la información solicitada. Las tres respuestas aprobaron la coincidencia de significado porque se ajustaron a ese resultado esperado. El 80% no se interpreta aquí como tres errores factuales; los métodos están valorando aspectos distintos.

## Cambios durante la evaluación

| Ejecución documentada | Calidad | Coincidencia | Cambio u observación |
|---|---:|---:|---|
| Inicial | 33% | — | Una fuente de OneDrive solicitaba conexión durante el lote. |
| Después de configurar la conexión | 27% | 20% | La solicitud de conexión persistió en la evaluación automática. |
| Después de retirar la fuente duplicada | 80% | 87% | La búsqueda pudo utilizar los PDF cargados directamente. |
| Instrucciones de idioma reforzadas | 80% | 93% | Una pregunta en inglés seguía recibiendo respuesta en español. |
| Pregunta de idioma explícito | 80% | 100% | Se pidió responder completamente en inglés. |

El historial incluye cambios tanto en la configuración y las instrucciones como en una pregunta. Por eso, la diferencia entre 93% y 100% no se presenta como una mejora del agente medida con un conjunto idéntico.

El CSV de preguntas conserva ahora la versión exacta de las quince preguntas y respuestas esperadas que aparecen en la exportación final, incluida la instrucción de idioma de la pregunta 14. Los resultados exportados se mantienen sin cambios.

## Qué demuestra y qué queda fuera

Estas pruebas aportan evidencia sobre las respuestas a las quince preguntas publicadas. La demostración muestra, además, un recorrido de consulta, confirmación y creación de ticket. Las quince preguntas no son quince pruebas completas de ese flujo.

Los calificadores de IA requieren interpretación, especialmente cuando se espera que el agente se abstenga. La primera respuesta aparece duplicada en el texto de la exportación; ambos métodos la clasificaron como aprobada.

El escenario utiliza políticas y datos sintéticos. No mide el comportamiento ante cualquier política real ni demuestra ahorro de tiempo en una operación. Tampoco sustituye pruebas adicionales de conversaciones, seguridad o rendimiento antes de usar la solución en producción.

[Ver la demostración](../README.md#demostración-end-to-end) · [Consultar la arquitectura](architecture.md)
