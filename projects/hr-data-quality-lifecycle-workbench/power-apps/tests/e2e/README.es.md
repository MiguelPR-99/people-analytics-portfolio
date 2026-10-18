# Pruebas E2E de Power Apps

Este paquete valida la Generative Page publicada dentro del runtime real de Power Apps. Complementa, no sustituye, las pruebas de componente de `generative-pages/dq-command-center`.

## Preparación única

1. Copiar `.env.example` como `.env`.
2. Conservar la URL del Command Center y reemplazar `DQ_TEST_USER` por la cuenta institucional.
3. Ejecutar `npm install`.
4. Ejecutar `npm run auth`, iniciar sesión en la ventana de Edge y abrir `DQ Command Center Generative`. La ventana se cerrará automáticamente cuando la página haya cargado.

El estado autenticado se almacena localmente en `.auth/state.json` y nunca debe versionarse. El script incluye cookies, `localStorage` e `IndexedDB`; este último es necesario para reutilizar correctamente algunas sesiones institucionales de Microsoft.

## Ejecución

- `npm test`: regresión funcional headless.
- `npm run test:smoke`: regresión funcional de sólo lectura; excluye pruebas visuales y mutantes.
- `npm run test:headed`: la misma regresión mostrando el navegador.
- `npm run test:mutation`: ejecuta únicamente la creación real cuando `DQ_CREATE_CASE_BUSINESS_KEY` está definido.
- `npm run test:visual -- --update-snapshots`: crea o actualiza la línea base visual aprobada.
- `npm run test:visual`: compara la UI publicada contra la línea base.
- `npm run report`: abre el informe HTML.

La creación real es una prueba mutante y se mantiene fuera de la regresión ordinaria. Para ejecutarla una sola vez contra una excepción que todavía no tenga caso:

```powershell
$env:DQ_CREATE_CASE_BUSINESS_KEY = "auto"
npx playwright test --grep "@mutation"
```

Con `auto`, la prueba selecciona la primera excepción publicada que todavía no tenga caso. También se puede indicar una clave concreta. La prueba exige que el botón cree el registro antes de navegar y que la URL operativa contenga el GUID del nuevo caso; la clave alternativa de Dataverse sigue siendo la defensa final contra duplicados.

La sesión institucional puede caducar; cuando aparezca una pantalla de autenticación, ejecutar nuevamente `npm run auth`.

El gate unificado del proyecto está en `scripts/verify_power_platform_phase7.ps1`. Por defecto sólo ejecuta las validaciones locales; `-IncludeE2E`, `-IncludeVisual` y `-MutationBusinessKey` activan explícitamente las capas que requieren el entorno publicado.

Los selectores y acciones compartidos se mantienen en `pages/dq-command-center.page.ts` siguiendo Page Object Model. Los casos de prueba deben consumir ese objeto en lugar de duplicar selectores del shell o de la Generative Page.

## Cobertura inicial

- carga del Command Center sin errores del shell;
- filtros de rango, dominio y severidad;
- excepciones con y sin caso de remediación;
- navegación a la app operativa preservada;
- creación opt-in de un caso completo y navegación al GUID recién creado;
- regresión visual separada de las pruebas funcionales.
