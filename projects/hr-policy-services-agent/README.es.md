# Proyecto 2: HR Policy & Services Agent

Un agente de autoservicio de RH para consultar políticas y crear tickets cuando se necesita seguimiento.

[← Volver al portafolio](../../README.md) · [English](README.en.md)

![Copilot Studio](https://img.shields.io/badge/Copilot%20Studio-5C2D91?logo=microsoftcopilot&logoColor=white)
![Power Automate](https://img.shields.io/badge/Power%20Automate-0066FF?logo=powerautomate&logoColor=white)
![Microsoft Lists](https://img.shields.io/badge/Microsoft%20Lists-0078D4?logo=microsoftlists&logoColor=white)
![Microsoft 365](https://img.shields.io/badge/Microsoft%20365-D83B01?logo=microsoftoffice&logoColor=white)

> Políticas, personas y solicitudes sintéticas. Proyecto independiente, sin afiliación ni respaldo de Siemens Energy.

## El problema

Una persona quiere saber cómo registrar a un dependiente en sus beneficios. Puede encontrar la respuesta en una política, pero quizá también necesite abrir una solicitud y saber qué sigue.

Desarrollé este proyecto para conectar ambos pasos: consultar la información disponible y crear un ticket con los datos necesarios, después de que el usuario lo confirme.

## Demostración end-to-end

El recorrido muestra una consulta sobre beneficios, la respuesta con su fuente y la creación de una solicitud. El agente presenta un resumen, espera la confirmación y devuelve el folio que generó Power Automate. El registro queda guardado en Microsoft Lists.

![Consulta y creación de un ticket con el HR Policy & Services Agent](assets/demo/hr-policy-services-agent-demo.gif)

[Ver el video en MP4](assets/demo/hr-policy-services-agent-demo.mp4)

## Cómo funciona

1. **Copilot Studio consulta cuatro PDF sintéticos.** Responde indicando la política y la sección utilizadas. Si no encuentra información suficiente, lo reconoce y ofrece seguimiento por parte de RH.
2. **El agente prepara la solicitud.** Recoge un resumen breve y datos de contacto sintéticos, muestra lo que va a registrar y espera una confirmación en un mensaje posterior.
3. **Power Automate crea el ticket.** Valida el servicio contra el catálogo, calcula las fechas de atención y guarda la solicitud en Microsoft Lists. El agente muestra el folio y los datos devueltos por el flujo.

## Decisiones importantes

Separé el permiso para que RH contacte al usuario de la confirmación para crear el ticket. Si el usuario cambia los datos, el agente debe mostrar un nuevo resumen y volver a pedir confirmación.

También configuré instrucciones para rechazar consultas sobre datos personales restringidos y ofrecer seguimiento con una persona de RH cuando el tema lo requiere. Los ejemplos publicados permiten revisar ese comportamiento.

[Ver una respuesta con su fuente](assets/screenshots/grounded-policy-answer.png) · [Ver un ejemplo de rechazo de información restringida](assets/screenshots/privacy-guardrail.png)

## Desarrollo y pruebas

Evalué quince preguntas sobre políticas, falta de información, privacidad e idioma. Esas pruebas revisan respuestas individuales; la demostración muestra por separado la conversación y la creación del ticket.

Durante la evaluación, una fuente duplicada de OneDrive pedía una conexión adicional. Al retirarla y conservar los PDF cargados directamente, el agente pudo consultar las políticas durante las pruebas. También ajusté las instrucciones de idioma y la pregunta bilingüe del conjunto de pruebas.

Aprendí a configurar las fuentes de conocimiento, establecer cuándo puede actuar el agente e interpretar los resultados de las pruebas.

## Más detalles

[Arquitectura y controles](docs/architecture.md) · [Método y resultados de evaluación](docs/evaluation-report.md) · [Instrucciones del agente](prompts/agent-instructions.txt)

Miguel — [Perfil de GitHub](https://github.com/MiguelPR-99)
