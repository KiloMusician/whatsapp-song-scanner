@echo off
setlocal

REM Album-art upload settings
set "UPLOAD_URL=http://192.168.1.178:8080/upload"
set "API_KEY=pirate2024"
set "COVER_FILE=C:\RadioDJ\current_cover.jpg"

if not exist "%COVER_FILE%" (
    echo [upload_cover] Cover file not found: %COVER_FILE%
    exit /b 1
)

curl.exe -sS -X POST "%UPLOAD_URL%" -H "X-Api-Key: %API_KEY%" -F "file=@%COVER_FILE%"
if errorlevel 1 (
    echo [upload_cover] Upload failed.
    exit /b 1
)

echo [upload_cover] Upload successful.
exit /b 0
