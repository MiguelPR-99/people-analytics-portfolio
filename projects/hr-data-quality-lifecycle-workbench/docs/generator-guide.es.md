# Guía del generador de datos sintéticos

## Qué produce

El generador crea seis lotes trimestrales para tres fuentes ficticias:

```text
data/
├─ raw/
│  ├─ global_hris/
│  │  └─ snapshot_date=YYYY-MM-DD/workers.csv
│  ├─ local_hr_operations/
│  │  └─ extract_date=YYYY-MM-DD/lifecycle_events.csv
│  └─ organization_master/
│     └─ snapshot_date=YYYY-MM-DD/positions.csv
└─ manifest.json
```

Son 18 archivos CSV en total. El manifiesto registra filas, columnas, tamaño, hash SHA-256, población, anomalías inyectadas, resultados esperados de calidad y comprobaciones de los patrones controlados.

## Requisitos

- Windows con Python 3.
- No requiere paquetes externos.

Verificación rápida:

```powershell
py -3 --version
```

## Ejecución normal

Desde la carpeta del proyecto:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_generator.ps1
```

El generador se detiene si encuentra una carpeta `data/raw` o un `data/manifest.json` existente. Esto evita sobrescribir una versión aprobada por accidente.

## Regeneración consciente

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_generator.ps1 -Force
```

`-Force` sustituye únicamente `data/raw` y `data/manifest.json` dentro de la ruta de salida del proyecto. No modifica documentación, scripts ni otros proyectos.

## Semilla

La versión oficial utiliza `20261012`. Para una prueba con otra semilla:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_generator.ps1 -Seed 12345 -Force
```

La versión final del portafolio debe volver a la semilla oficial antes de validar y publicar.

## Pruebas automatizadas

```powershell
py -3 -m unittest discover -s .\scripts\tests -p "test_*.py" -v
```

Las pruebas comprueban:

- estructura y schema de los 18 CSV;
- hashes y conteos del manifiesto;
- reconciliación de la población;
- presencia de las ocho reglas;
- patrones de reorganización, onboarding e intervención;
- ausencia de campos sensibles prohibidos;
- reproducibilidad con la misma semilla;
- protección contra sobrescritura accidental.

## Uso posterior en Fabric

Cada carpeta con fecha representa un lote independiente. La fecha de la carpeta y el hash del archivo formarán el control incremental. Reprocesar el mismo lote deberá ser idempotente: no puede duplicar Bronze ni los resultados Gold.

Los CSV son entradas raw. No deben corregirse manualmente antes de cargarlos, porque los errores controlados son parte del caso y permiten validar las reglas de calidad.

