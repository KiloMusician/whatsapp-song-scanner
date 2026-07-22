@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "WATCH_SCRIPT=%SCRIPT_DIR%watch_and_upload_cover.ps1"
set "VIRTUALDJ_COVER=C:\DJ\current_cover.jpg"

if not exist "%WATCH_SCRIPT%" (
    echo [virtualdj-cover] Missing watcher script: %WATCH_SCRIPT%
    exit /b 1
)

echo [virtualdj-cover] Starting watcher for %VIRTUALDJ_COVER%
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%WATCH_SCRIPT%" -CoverFile "%VIRTUALDJ_COVER%"
exit /b %ERRORLEVEL%
