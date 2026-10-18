@echo off
setlocal
set "AZURE_CONFIG_DIR=D:\PBI-Agentic\azure-config"
if not exist "%AZURE_CONFIG_DIR%" mkdir "%AZURE_CONFIG_DIR%"
"D:\PBI-Agentic\azure-cli\bin\az.cmd" %*
exit /b %ERRORLEVEL%
