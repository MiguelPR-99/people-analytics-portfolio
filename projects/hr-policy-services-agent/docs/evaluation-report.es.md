# Informe de evaluación

[← Volver al caso](../README.es.md) · [English](evaluation-report.md)

## Objetivo

Comprobar que el agente responde con evidencia cuando corresponde, se abstiene cuando no dispone de ella, protege información restringida, utiliza el idioma solicitado y mantiene la revisión humana en asuntos sensibles.

## Diseño

- Tipo: respuesta única.
- Casos: 15.
- Métodos: calidad general y coincidencia de significado.
- Umbral de coincidencia: 50.
- Perfil: usuario autenticado con las conexiones requeridas.
- Fuentes: cuatro PDF sintéticos cargados directamente.

Los casos incluyen vacaciones, beneficios, onboarding, documentos, falta de evidencia, privacidad, asuntos sensibles y preguntas en español e inglés.

## Resultado final

| Método | Aprobados | Resultado |
|---|---:|---:|
| Calidad general | 12 de 15 | 80% |
| Coincidencia de significado | 15 de 15 | 100% |

## Interpretación de los tres fallos de calidad

El evaluador de calidad clasificó tres respuestas como “sin responder” porque el agente se negó a proporcionar una respuesta directa:

1. Política de trabajo remoto no incluida en las fuentes.
2. Salario, evaluación de desempeño e información médica individual.
3. Determinación individual de permisos legales o elegibilidad médica específica de un país.

Estas negativas son el resultado esperado. Las tres aprobaron la coincidencia de significado porque respetaron la respuesta segura definida en el conjunto de pruebas.

Por este motivo, el 80% no representa tres errores factuales. Representa una limitación del evaluador general al calificar respuestas que deben abstenerse por diseño.

## Evolución de la prueba

| Ejecución | Calidad | Coincidencia | Observación |
|---|---:|---:|---|
| Inicial | 33% | — | Una fuente de OneDrive solicitaba conexión durante el lote |
| Después de configurar la conexión | 27% | 20% | El problema persistió en la evaluación automática |
| Después de eliminar la fuente duplicada | 80% | 87% | La recuperación de los PDF funcionó |
| Regla bilingüe reforzada | 80% | 93% | Un caso inglés seguía respondiendo en español durante el lote |
| Caso de idioma explícito | 80% | 100% | Resultado final |

## Limitaciones

- La evaluación integrada utiliza calificadores de IA; el resultado de calidad requiere interpretación humana en casos de negativa segura.
- La demostración usa políticas y registros sintéticos y no mide precisión sobre políticas reales.
- El archivo exportado conserva el detalle completo para auditoría. La primera respuesta aparece duplicada en el texto exportado, aunque ambos métodos la calificaron como aprobada.
- La evaluación no sustituye pruebas de seguridad, cumplimiento o rendimiento necesarias para producción.

## Archivos

- [Casos de prueba](../evaluation/test-cases.csv)
- [Resultados finales](../evaluation/final-results.csv)
