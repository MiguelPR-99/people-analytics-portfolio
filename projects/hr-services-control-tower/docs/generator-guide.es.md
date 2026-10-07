# Guía sencilla — generador de datos

## ¿Qué hace?

El generador crea de forma automática los casos ficticios de HR Services, sus eventos, encuestas, snapshots de backlog y tablas de referencia. Siempre que se use la misma semilla, producirá exactamente el mismo dataset.

No utiliza información real y no necesita descargar librerías adicionales.

## Requisito

Tener instalado **Python 3** en Windows.

Para comprobarlo, abre PowerShell y escribe:

```powershell
py -3 --version
```

Si aparece una versión como `Python 3.12`, puedes continuar.

## Ejecución normal

Desde la carpeta `hr-services-control-tower`, ejecuta:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_generator.ps1
```

La ejecución completa puede tardar algunos segundos. Al finalizar debe aparecer el mensaje `Generacion terminada correctamente`.

## ¿Dónde quedan los archivos?

```text
data/
├─ raw/          Archivos que simulan exportaciones originales
├─ processed/    Tablas limpias de referencia
└─ manifest.json Resumen, cantidades, controles y huellas de los archivos
```

## Volver a generar los datos

Si la carpeta `data` ya contiene una generación previa, el programa se detendrá para no reemplazarla accidentalmente. Para regenerar conscientemente los mismos archivos:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_generator.ps1 -Force
```

`-Force` solamente reemplaza las carpetas generadas `data/raw`, `data/processed` y el archivo `data/manifest.json`.

## Prueba rápida opcional

Para aprender el flujo con solo 500 casos:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_generator.ps1 -CaseCount 500 -Force
```

Después vuelve a ejecutar la versión completa con `-CaseCount 9000 -Force` antes de construir Power BI.

## Semilla

La semilla predeterminada es `20260824`. Es el número que controla la parte aleatoria. Mantenerla permite que otra persona reproduzca exactamente los mismos resultados.

No cambies la semilla para la versión oficial del portafolio.

