# Métricas y reglas de cálculo

[← Volver al caso](../README.md) · [English](metric-dictionary.en.md)

## Población y contexto

Los cálculos parten de evaluaciones sintéticas. Salvo que se indique otra cosa, los porcentajes usan como base a los empleados evaluados dentro de los filtros activos. Los conteos se realizan por `EmployeeID` distinto.

El periodo, el departamento y los demás filtros pueden cambiar tanto el resultado como su referencia. Al comparar dos vistas, primero hay que comprobar que representan la misma población y el mismo periodo.

## Evaluaciones y matriz 9-box

| Concepto | Regla |
|---|---|
| Performance | Nivel de desempeño asignado en la evaluación: Low, Moderate o High |
| Potential | Nivel de potencial asignado en la evaluación: Low, Moderate o High |
| Posición 9-box | Celda que corresponde a la combinación de desempeño y potencial |
| Future Leader | Desempeño alto y potencial alto |
| Under Performer | Desempeño bajo y potencial bajo |
| Future Leader % | Empleados distintos en esa celda / empleados distintos evaluados |
| Under Performer % | Empleados distintos en esa celda / empleados distintos evaluados |

El reporte recibe estas valoraciones; no calcula el desempeño ni predice el potencial a partir de otros atributos. *Future Leader* y *Under Performer* son etiquetas del ejercicio para combinaciones concretas, no definiciones permanentes de una persona.

## Movimiento entre evaluaciones

Se compara el periodo seleccionado con la evaluación inmediatamente anterior disponible.

| Clasificación del reporte | Regla |
|---|---|
| Improved | Sube el desempeño o el potencial, sin que baje el otro |
| Stable | Se mantiene la misma posición en la matriz |
| Declined | Baja el desempeño o el potencial, sin que suba el otro |
| Mixed | Desempeño y potencial cambian en direcciones opuestas |
| Conteo de transiciones | Empleados distintos para cada combinación de posición anterior y actual |

La primera evaluación disponible no tiene una comparación previa y devuelve una clasificación vacía. La ausencia de comparación no significa estabilidad.

Por ejemplo, pasar de desempeño moderado y potencial alto a desempeño alto y potencial moderado es un movimiento mixto. El orden de las etiquetas 9-box no se interpreta como una escala única de mejora.

En el ejemplo de 2025 a 2026, las clasificaciones son 66% Stable, 18% Improved, 14% Declined y 2% Mixed. Describen cambios en las evaluaciones registradas, sin demostrar sus causas ni cambios objetivos en la capacidad de las personas.

## Calibración entre managers

| Métrica | Regla |
|---|---|
| Promedio del manager | Promedio del puntaje de desempeño o potencial de sus empleados evaluados, con los filtros activos |
| Referencia de la población seleccionada | Promedio correspondiente para el conjunto de managers que conservan los filtros del reporte |
| Performance gap | Promedio de desempeño del manager − promedio de desempeño de la población seleccionada |
| Potential gap | Promedio de potencial del manager − promedio de potencial de la población seleccionada |
| Señal de calibración | Valor absoluto de cualquiera de los dos gaps ≥ 0.25 puntos **y** al menos cinco empleados evaluados por manager |

Un gap positivo indica un promedio superior al de referencia; uno negativo indica un promedio inferior. El tamaño de las burbujas representa empleados evaluados. Los gaps se expresan en puntos del puntaje, no en porcentajes.

El umbral de 0.25 y el mínimo de cinco empleados son reglas elegidas para el ejercicio. No son estándares universales, pruebas de significancia ni controles suficientes frente a grupos pequeños. No se ha establecido su validez estadística.

Las diferencias pueden orientar una conversación sobre criterios, evidencia o composición de los equipos. No demuestran sesgo, discriminación ni calidad de la gestión. Estar dentro del rango tampoco acredita que los criterios se hayan aplicado correctamente.

La captura de calibración usa **2024**: tres de ocho managers cumplen la regla en esa selección. Ese ejemplo pertenece a otro periodo que la comparación de movimiento 2025–2026.

## Talent Balance por departamento

**Talent Balance = Future Leader % − Under Performer %.**

Es una diferencia en **puntos porcentuales**. Un valor positivo indica una mayor proporción en Future Leader; uno negativo, una mayor proporción en Under Performer. El indicador resume esas dos celdas y deja fuera las otras siete.

En Customer Success, para 2026, hay seis empleados: ninguno en Future Leader y tres en Under Performer. El cálculo es **0% − 50% = −50 puntos porcentuales**. Una sola persona representa aproximadamente 16.7 puntos porcentuales en un grupo de ese tamaño.

La captura conserva el formato porcentual y un titular sobre *talent risk* y *pipeline strength*. Esas expresiones no deben leerse como riesgo predictivo, probabilidad de salida, calidad global del talento o preparación demostrada para el liderazgo. Tampoco justifican por sí solas un ranking de departamentos ni decisiones individuales.
