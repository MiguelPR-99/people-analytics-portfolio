# Revisión del gate — Fase 6 Power Apps

**Fecha inicial:** 15 de octubre de 2026  
**Revalidación correctiva:** 16 de octubre de 2026  
**Resultado:** PASS

## Arquitectura entregada

- `DQ Command Center Generative`: Generative Page oficial en React + TypeScript.
- aplicación basada en modelo preservada como núcleo transaccional.
- Dataverse preservado como fuente de verdad.
- prototipo Canvas conservado como respaldo; no fue sobrescrito ni eliminado.

## Criterios del gate

| Criterio | Evidencia | Resultado |
|---|---|---|
| Completar el flujo sin editar tablas directamente | Selección de excepción; creación completa mediante `dataApi.createRow`; apertura por GUID en la app operativa | PASS |
| Filtros, estados y validaciones | Matriz de componentes y E2E de rango, dominio y severidad; estado de error de Dataverse contenido dentro de la página | PASS |
| Minimización de información | La cola muestra únicamente atributos operativos necesarios y mantiene la referencia analítica como solo lectura | PASS |
| API soportada y separación transaccional | Lectura mediante `dataApi.queryTable`; creación mediante `dataApi.createRow`; edición posterior delegada al formulario model-driven | PASS |
| Configuración transportable | URL operativa obtenida de `DQ Operational App URL`, sin tenant ni App ID codificados en React | PASS |
| Estabilidad del runtime | Sin error genérico del shell al cargar, filtrar o navegar | PASS |
| Fidelidad visual | Dirección `Readiness Rail` aceptada y línea base visual reproducible | PASS |

## Verificación automatizada

Ejecutada el 15 de octubre de 2026:

- `npm run typecheck`: PASS.
- `npm test` en la Generative Page: 4/4 pruebas de componente.
- `npm test` en `power-apps/tests/e2e`: 4/4 pruebas contra la app publicada.
- `npm run test:visual`: 1/1 comparación visual.

Revalidación del 16 de octubre de 2026:

- `npm run typecheck`: PASS.
- `npm test` en la Generative Page: 5/5 pruebas de componente.
- regresión publicada no mutante: 4/4 PASS.
- prueba publicada y opt-in de creación real: 1/1 PASS; el caso se creó antes de navegar y la URL incluyó su GUID.
- `DQ - Notify Case Assignment`: ejecuciones posteriores a la creación finalizadas correctamente.
- publicación mediante Power Platform CLI: página `d4795a8b-616b-42cf-a84a-5354a58dfa3c`, siete fuentes registradas.

La regresión E2E cubre carga, todos los dominios disponibles, combinación de filtros y navegación hacia la aplicación operativa. La creación es una prueba mutante separada y opt-in para no generar registros durante la regresión ordinaria. La suite utiliza Page Object Model, selectores accesibles y una sesión institucional reutilizable que conserva también `IndexedDB`.

## Corrección del flujo de creación

La primera versión abría un formulario nuevo vacío. Como los identificadores, estado y marcas temporales son campos controlados por sistema, el usuario encontraba campos requeridos bloqueados. La corrección mantiene los candados y cambia la responsabilidad del botón:

1. identifica el estado inicial `New` desde `DQ Status`;
2. crea el caso con referencia, `Exception Instance ID`, `Recurrence Key`, título, propietario predeterminado, `SLA Start At`, `Due At` y `Last Transition At`;
3. conserva la clave alternativa de Dataverse como defensa contra duplicados;
4. abre el registro creado por GUID;
5. contiene el error y cierra la ventana provisional si la creación falla.

## Decisión

La Fase 6 permanece completada después de la revalidación correctiva. El prototipo Canvas permanece como respaldo durante el resto del proyecto. El formulario conserva bloqueados los campos técnicos; la reasignación se realiza mediante el comando estándar `Asignar` y requiere privilegio Assign.
