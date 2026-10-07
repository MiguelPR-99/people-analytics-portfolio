# Guía visual del dashboard

## Dirección

El reporte utiliza una identidad inspirada en los materiales públicos de Siemens Energy: morado profundo, azul, turquesa, fondos claros y composición corporativa limpia. No pretende reproducir ni representar una herramienta interna oficial.

## Paleta funcional

| Uso | Color |
|---|---|
| Encabezado principal | `#3B123C` |
| Serie principal / demanda | `#7A1E6C` |
| Serie secundaria / cierres | `#00A6A6` |
| Información complementaria | `#006B8F` |
| Fondo del lienzo | `#F4F2F5` |
| Superficie de visuales | `#FFFFFF` |
| Texto principal | `#241E26` |
| Texto secundario | `#5F5862` |
| Bordes discretos | `#DDD7DF` |

Los colores verde, ámbar y rojo se reservan para estados que tengan una regla de negocio explícita. No deben utilizarse solo para decorar.

## Executive Overview

### Encabezado

- Franja superior morado profundo `#3B123C`, de 64 a 72 px de alto.
- Título en blanco: `HR Services Control Tower`.
- Subtítulo: `Service delivery performance | Synthetic portfolio case`.
- No usar el logotipo corporativo. El nombre puede aparecer como contexto de la vacante, no como autoría del reporte.

### Filtros

- Colocarlos en una franja clara inmediatamente debajo del encabezado.
- Usar etiquetas breves: `Periodo`, `Ubicación` y `Servicio`.
- Mantener la misma altura y separación entre controles.

### KPI

- Fondo blanco, radio visual discreto y sin sombras fuertes.
- Número en `#241E26` y etiqueta en `#5F5862`.
- Añadir una línea superior de 3 px únicamente como agrupador: morado para demanda, turquesa para servicio y azul para tiempo.
- Usar nombres abreviados para evitar truncamiento: `SLA primera respuesta`, `SLA resolución`, `Resolución promedio (h)` y `FCR`.

### Gráficos

- Demanda: `#7A1E6C`.
- Casos cerrados: `#00A6A6`.
- Barras de backlog: `#006B8F`.
- SLA por servicio: `#7A1E6C` con etiquetas de datos visibles.
- Quitar subtítulos automáticos del tipo `por ServiceGroup` cuando el título ya explique el gráfico.
- Mantener líneas de cuadrícula muy claras y evitar bordes gruesos.

## Pie de página

Usar texto pequeño y discreto:

`Proyecto de portafolio independiente · Datos 100% sintéticos · No afiliado con Siemens Energy`

## Importar el tema

En Power BI Desktop: **Vista > Temas > Examinar temas** y seleccionar `assets/power-bi/siemens-energy-inspired-theme.json`.
