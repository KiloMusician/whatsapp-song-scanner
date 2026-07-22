param(
    [string]$TaskName = "RadioDJ-CoverWatcher",
    [switch]$Remove
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$watcherPath = Join-Path $scriptDir "watch_and_upload_cover.ps1"

if ($Remove) {
    $existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($null -ne $existing) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "[task] Removed scheduled task: $TaskName"
    }
    else {
        Write-Host "[task] Scheduled task not found: $TaskName"
    }
    return
}

if (-not (Test-Path -LiteralPath $watcherPath)) {
    throw "Watcher script not found: $watcherPath"
}

$psArgs = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$watcherPath`""
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $psArgs
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

$task = New-ScheduledTask -Action $action -Trigger $trigger -Principal $principal -Settings $settings
Register-ScheduledTask -TaskName $TaskName -InputObject $task -Force | Out-Null

Write-Host "[task] Installed scheduled task: $TaskName"
Write-Host "[task] It will start at login for user $env:USERNAME"
Write-Host "[task] You can start it now with: Start-ScheduledTask -TaskName $TaskName"
