param(
    [string]$UploadUrl = "http://192.168.1.178:8080/upload",
    [string]$ApiKey = "pirate2024",
    [string]$ImageFolder = "C:\RadioDJv2\Images",
    [int]$IntervalSeconds = 5
)

$ErrorActionPreference = "Stop"

Write-Host "[folder-watch] Watching folder: $ImageFolder"
Write-Host "[folder-watch] Upload URL: $UploadUrl"
Write-Host "[folder-watch] Interval: ${IntervalSeconds}s"

$lastUploadedHash = $null
$lastUploadedPath = $null

while ($true) {
    try {
        if (-not (Test-Path -LiteralPath $ImageFolder)) {
            Write-Host "[folder-watch] Waiting for folder: $ImageFolder"
        }
        else {
            $latest = Get-ChildItem -LiteralPath $ImageFolder -File -ErrorAction SilentlyContinue |
                Where-Object { $_.Extension -match '^\.(jpg|jpeg|png|bmp)$' } |
                Sort-Object LastWriteTime -Descending |
                Select-Object -First 1

            if ($null -eq $latest) {
                Write-Host "[folder-watch] No image files found in $ImageFolder"
            }
            else {
                $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $latest.FullName).Hash

                if (($hash -ne $lastUploadedHash) -or ($latest.FullName -ne $lastUploadedPath)) {
                    Write-Host "[folder-watch] New latest image: $($latest.Name). Uploading..."

                    $curlArgs = @(
                        "-sS",
                        "-X", "POST",
                        "$UploadUrl",
                        "-H", "X-Api-Key: $ApiKey",
                        "-F", "file=@$($latest.FullName)"
                    )

                    & curl.exe @curlArgs
                    if ($LASTEXITCODE -eq 0) {
                        $lastUploadedHash = $hash
                        $lastUploadedPath = $latest.FullName
                        Write-Host "[folder-watch] Upload successful: $($latest.FullName)"
                    }
                    else {
                        Write-Warning "[folder-watch] Upload failed (exit code $LASTEXITCODE)."
                    }
                }
            }
        }
    }
    catch {
        Write-Warning "[folder-watch] Error: $($_.Exception.Message)"
    }

    Start-Sleep -Seconds $IntervalSeconds
}
