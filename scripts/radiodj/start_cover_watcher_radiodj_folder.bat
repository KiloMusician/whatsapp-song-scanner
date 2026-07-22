@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "WATCH_SCRIPT=%SCRIPT_DIR%watch_and_upload_latest_from_folder.ps1"
set "IMAGE_FOLDER=C:\RadioDJv2\Images"

if not exist "%WATCH_SCRIPT%" (
    echo [folder-watch] Missing script: %WATCH_SCRIPT%
    exit /b 1
)

echo [folder-watch] Starting watcher for %IMAGE_FOLDER%
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%WATCH_SCRIPT%" -ImageFolder "%IMAGE_FOLDER%"
exit /b %ERRORLEVEL%
