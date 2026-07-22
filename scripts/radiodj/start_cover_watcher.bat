@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "WATCH_SCRIPT=%SCRIPT_DIR%watch_and_upload_cover.ps1"

if not exist "%WATCH_SCRIPT%" (
    echo [cover-watch] Missing script: %WATCH_SCRIPT%
    exit /b 1
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%WATCH_SCRIPT%"
exit /b %ERRORLEVEL%
