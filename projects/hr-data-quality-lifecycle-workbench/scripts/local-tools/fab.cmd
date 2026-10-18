@echo off
setlocal
set "USERPROFILE=D:\PBI-Agentic\fabric-user"
if not exist "%USERPROFILE%" mkdir "%USERPROFILE%"
"D:\PBI-Agentic\python\Scripts\fab.exe" %*
exit /b %ERRORLEVEL%
