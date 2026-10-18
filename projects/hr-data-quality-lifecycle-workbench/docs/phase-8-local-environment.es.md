# Preparación local — Fase 8 Power BI

## Resultado

El entorno local para desarrollo agentic de Power BI quedó preparado el 17 de octubre de 2026. Las herramientas nuevas se concentran en `D:\PBI-Agentic`; Power BI Desktop ya estaba instalado mediante Microsoft Store en el volumen `Data (D:)` según Configuración de Windows.

Windows puede mostrar una ruta proyectada bajo `C:\Program Files\WindowsApps` al consultar el paquete AppX. Esa ruta forma parte del mecanismo de paquetes y no justifica reinstalar ni mover la aplicación.

## Inventario fijado

| Componente | Versión / revisión | Ubicación |
|---|---|---|
| Power BI Desktop | `2.159.883.0` | Microsoft Store, volumen `D:` |
| Node.js | `25.8.1` | `D:\node.exe` |
| Power BI Report Author CLI | `0.5.0` | `D:\PBI-Agentic\npm` |
| Power BI Modeling MCP | `1.0.0` | `D:\PBI-Agentic\npm` |
| Azure CLI portable | `2.91.0` | `D:\PBI-Agentic\azure-cli` |
| Fabric CLI | `1.7.0` | `D:\PBI-Agentic\python` |
| APM CLI | `0.33.0` | `D:\PBI-Agentic\python` |
| Microsoft Fabric skills | commit `bc42aaf734771bf752c1d7082dd91e5a6ca72b9f` | `D:\PBI-Agentic\fabric-skills` |

Las dos skills instaladas son:

- `semantic-model-authoring` para modelo semántico, relaciones, DAX, TMDL, actualización y despliegue;
- `powerbi-report-cli` para planificación, diseño, PBIR/PBIP, validación, preview y publicación.

Ambas se exponen a Codex mediante junctions en `%USERPROFILE%\.agents\skills`; los archivos reales permanecen en `D:`. APM mantiene `apm.yml` y `apm.lock.yaml` en `D:\PBI-Agentic\fabric-skills`.

## Configuración aplicada

- MCP global `powerbi-modeling` registrado en Codex como proceso `stdio` local:
  - comando: `D:\node.exe`;
  - entrada: `D:\PBI-Agentic\npm\node_modules\@microsoft\powerbi-modeling-mcp\index.js --start`.
- No se registró el MCP hospedado equivalente. Usar simultáneamente ambos introduciría ambigüedad y consumo de contexto innecesario.
- `AZURE_CONFIG_DIR=D:\PBI-Agentic\azure-config`.
- `PBI_AGENTIC_HOME=D:\PBI-Agentic`.
- Se añadieron al `PATH` del usuario:
  - `D:\PBI-Agentic\bin`;
  - `D:\PBI-Agentic\npm\node_modules\.bin`;
  - `D:\PBI-Agentic\python\Scripts`;
  - `D:\PBI-Agentic\azure-cli\bin`.
- Los wrappers `D:\PBI-Agentic\bin\az.cmd` y `fab.cmd` redirigen sus perfiles de ejecución a `D:\PBI-Agentic\azure-config` y `D:\PBI-Agentic\fabric-user` sin cambiar el perfil global de Windows.

Es necesario abrir una terminal nueva para que herede el `PATH` y las variables de usuario.

## Verificaciones ejecutadas

- `powerbi-report-author doctor --pretty`: correcto; Node, AJV y el proveedor de metadatos de 57 visuales y 15 VCO disponibles.
- `az version`: `2.91.0`.
- `fab --version`: `1.7.0`.
- APM: lockfile reproducible, commit fijado y sin drift de archivos.
- Codex: MCP `powerbi-modeling` habilitado y detectado en la sesión.
- Power BI Desktop: paquete `Microsoft.MicrosoftPowerBIDesktop` `2.159.883.0` detectado.

La auditoría APM en modo CI informa una inconsistencia de configuración deliberada: el bundle completo también declara `FabricIQ` y `fabric-sqlendpoint`, pero la instalación usa `--only apm` y registra manualmente solo `powerbi-modeling-mcp`. No es drift ni corrupción; es el alcance mínimo elegido para esta fase.

## Seguridad y límites

- No se guardaron credenciales, tokens, IDs de tenant ni secretos. Los nombres de servidor/base y la URL de entorno son valores de parámetros TMDL necesarios para la actualización local; se anonimizarán antes de publicar el repositorio del portafolio.
- No se realizó `az login`, `fab auth login` ni publicación.
- El usuario confirmó el 17 de octubre de 2026 que revisó la [EULA oficial](https://go.microsoft.com/fwlink/?LinkId=2381247) y autorizó su aceptación; el MCP oficial devolvió confirmación satisfactoria.
- El MCP se conectó a la instancia local de Power BI Desktop y el modelo se persistió como TMDL. Azure/Fabric no mantienen una sesión de despliegue y no se realizó publicación.
- Las credenciales de Fabric SQL y Dataverse se configurarán en Power BI/Fabric, nunca en Git.
- Las carpetas `.pbi` de caché y configuración local están excluidas mediante `.gitignore`.

## Asociación CLI–Desktop

Power BI Desktop expone su automatización mediante un named pipe local. La ruta correcta para abrir y asociar el proyecto es el archivo propietario `power-bi\HRDataQualityScorecard.pbip`; la CLI resuelve desde ahí la carpeta `HRDataQualityScorecard.Report`.

```powershell
.\scripts\invoke-powerbi-report-author.ps1 preview .\power-bi\HRDataQualityScorecard.pbip --host desktop
.\scripts\invoke-powerbi-report-author.ps1 preview .\power-bi\HRDataQualityScorecard.pbip --host desktop --status
```

En un runner aislado, `EPERM` al conectar con `\\.\pipe\pbi-desktop-bridge-*` significa que el proceso no tiene permiso para leer el pipe; no indica una ruta PBIP incorrecta. La apertura, el estado y la captura deben ejecutarse en el mismo contexto de usuario/permisos. El estado validado fue `ready` con la carpeta `.Report` esperada.

## Mantenimiento

1. Ejecutar `scripts/verify_power_bi_phase8.ps1` después de actualizar herramientas o reiniciar la preparación.
2. Actualizar las skills solo mediante APM y revisar el cambio de commit antes de adoptarlo.
3. Mantener una sola instancia del MCP de modelado.
4. Ejecutar `powerbi-report-author validate <ruta.Report>` por cada lote lógico de cambios.
5. Validar visualmente en Desktop y conservar capturas antes de publicar.

## Fuentes oficiales

- [Power BI agentic development](https://learn.microsoft.com/power-bi/developer/agentic/power-bi-agentic-overview)
- [Power BI Authoring MCP](https://learn.microsoft.com/power-bi/developer/mcp/power-bi-authoring-mcp)
- [Power BI Project (PBIP)](https://learn.microsoft.com/power-bi/developer/projects/projects-overview)
- [Microsoft skills for Fabric](https://github.com/microsoft/skills-for-fabric)
- [Fabric CLI](https://learn.microsoft.com/rest/api/fabric/articles/fabric-command-line-interface)
- [Azure CLI portable para Windows](https://learn.microsoft.com/cli/azure/install-azure-cli-windows)
