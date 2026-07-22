param(
    [string]$UploadUrl = "http://192.168.1.178:8080/upload",
    [string]$ApiKey = "pirate2024",
    [string]$CoverFile = "C:\RadioDJ\current_cover.jpg",
    [int]$IntervalSeconds = 5
)

$ErrorActionPreference = "Stop"

Write-Host "[cover-watch] Watching: $CoverFile"
Write-Host "[cover-watch] Upload URL: $UploadUrl"
Write-Host "[cover-watch] Interval: ${IntervalSeconds}s"

$lastHash = $null

while ($true) {
    try {
        if (Test-Path -LiteralPath $CoverFile) {
            $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $CoverFile).Hash

            if ($hash -ne $lastHash) {
                Write-Host "[cover-watch] Change detected. Uploading..."

                $curlArgs = @(
                    "-sS",
                    "-X", "POST",
                    "$UploadUrl",
                    "-H", "X-Api-Key: $ApiKey",
                    "-F", "file=@$CoverFile"
                )

                & curl.exe @curlArgs
                if ($LASTEXITCODE -eq 0) {
                    $lastHash = $hash
                    Write-Host "[cover-watch] Upload successful."
                }
                else {
                    Write-Warning "[cover-watch] Upload failed (exit code $LASTEXITCODE)."
                }
            }
        }
        else {
            Write-Host "[cover-watch] Waiting for file: $CoverFile"
        }
    }
    catch {
        Write-Warning "[cover-watch] Error: $($_.Exception.Message)"
    }

    Start-Sleep -Seconds $IntervalSeconds
}
