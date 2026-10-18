# Arquitectura de la Generative Page

## Decisión

`DQ Command Center` se construirá como una Generative Page oficial de Power Apps mediante React + TypeScript. La aplicación basada en modelo seguirá siendo el host y el núcleo transaccional; Dataverse seguirá siendo la fuente de verdad. El prototipo Canvas existente queda en espera como respaldo visual y funcional recuperable.

## Límite del cambio

El cambio afecta únicamente al front-end del Command Center. Permanecen sin sustitución:

- las tablas, relaciones y seguridad de Dataverse;
- los formularios, vistas y navegación de la aplicación basada en modelo;
- las reglas de negocio y auditoría ya publicadas;
- la separación entre excepción analítica inmutable y caso operativo editable.

## Componentes

```text
HR Data Quality Workbench — model-driven app
├── DQ Command Center — Generative Page, React + TypeScript
│   ├── dataApi.queryTable y dataApi.createRow sobre Dataverse
│   ├── filtros, KPIs y cola priorizada
│   ├── panel contextual de readiness
│   ├── creación completa del caso cuando todavía no existe
│   └── navegación al caso por GUID en la app basada en modelo
├── formularios y vistas model-driven
├── reglas de negocio y auditoría
└── Dataverse
    ├── DQ Exception Reference — solo lectura funcional
    ├── DQ Remediation Case
    ├── DQ Case Activity
    ├── DQ Case Evidence
    ├── DQ Status
    └── variables de entorno de solución — sólo URL operativa
```

## Principios de implementación

1. Usar únicamente las API soportadas por Generative Pages; no llamar Dataverse mediante credenciales embebidas ni peticiones HTTP ad hoc.
2. Consultar las cinco tablas funcionales y únicamente las dos tablas estándar de configuración necesarias para resolver `DQ Operational App URL`; no enumerar otras variables.
3. Mantener `DQ Exception Reference` como solo lectura.
4. Si no existe caso, crearlo con `dataApi.createRow`, referencias completas, estado `New`, propietario predeterminado del usuario invocador y marcas de SLA/transición antes de abrirlo.
5. Abrir el formulario model-driven existente por GUID para la edición completa del caso.
6. Preservar la dirección visual aprobada `Readiness Rail`: encabezado petrol, franja de salud, tabla dominante y rail contextual.
7. Usar datos sintéticos y mostrarlo explícitamente.
8. Validar accesibilidad, estados de carga, vacío, error y permisos insuficientes antes de publicar.

## Flujo local previsto

1. Autenticar Power Platform CLI contra el entorno objetivo.
2. Identificar la app y los nombres lógicos de las tablas.
3. Generar tipos de Dataverse.
4. Crear `page.tsx`, configuración y estilos locales.
5. Transpilar y verificar el paquete.
6. Subir la Generative Page, agregarla al sitemap y publicar la app.
7. Probar con el usuario conectado y conservar evidencia visual.

## Estrategia de pruebas

La Generative Page utiliza tres niveles complementarios:

1. Pruebas de componente con datos simulados de Dataverse para estados, filtros, filas con y sin caso, payload de creación, errores y navegación.
2. Pruebas end-to-end con Playwright contra la app publicada y una sesión institucional reutilizable. Estas pruebas validan el runtime real de Power Apps, el shell model-driven y la navegación entre ambas aplicaciones.
3. Aceptación visual humana para confirmar jerarquía, legibilidad y fidelidad a la dirección Siemens Energy aprobada.

La implementación E2E sigue los patrones de los Power Platform Playwright Samples de Microsoft: Page Object Model, estado de autenticación reutilizable, esperas basadas en condiciones y selectores accesibles. Las capturas de regresión visual se ejecutarán separadas de las pruebas funcionales para no introducir falsos negativos por datos o marcas de tiempo dinámicas.

No se introduce una Custom API para la creación sencilla del MVP: `dataApi.createRow` es una API soportada y las claves alternativas, reglas y auditoría de Dataverse permanecen activas. Si la creación exige en producción una transacción compuesta, asignación por dominio o calendario laboral corporativo, se migrará a una Custom API o plug-in.

## Riesgos controlados

- Sólo una persona editará la Generative Page a la vez.
- No se publicará código generado sin revisión manual.
- Las operaciones experimentales de conectores o Custom API no forman parte del MVP.
- El cálculo de `Due At` del MVP omite fines de semana; un calendario corporativo con festivos queda como endurecimiento productivo.
- El rol HR Data Steward necesita lectura de las dos tablas estándar de variables de entorno y permisos Create/Append/Append To sobre el caso y sus lookups.
- La reasignación posterior utiliza el comando estándar `Asignar`; debe permanecer visible para roles con privilegio Assign.
- La Canvas Page no se elimina hasta que la Generative Page pase el gate de Fase 6.
