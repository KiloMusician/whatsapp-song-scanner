# RadioDJ Album Art Upload Scripts

These scripts push RadioDJ cover art to a LAN upload server.

## Files

- `upload_cover.bat`: one-shot upload (best for RadioDJ track-change event)
- `watch_and_upload_cover.ps1`: watches the cover file and uploads only when it changes
- `watch_and_upload_latest_from_folder.ps1`: watches a folder and uploads the newest image file

## Defaults

- Upload URL: `http://192.168.1.178:8080/upload`
- API key header: `X-Api-Key: pirate2024`
- Cover file: `C:\RadioDJ\current_cover.jpg`

Edit each script if your URL/key/path differs.

## RadioDJ Setup (Event-Based)

1. Set RadioDJ to save cover art:
   - `Settings -> General -> Cover Art -> Save cover to file`
   - `C:\RadioDJ\current_cover.jpg`
2. In `Settings -> Events -> After track change`, run `upload_cover.bat`.

## Timed Watcher Setup

Run in PowerShell when RadioDJ starts:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/radiodj/watch_and_upload_cover.ps1
```

Optional arguments:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/radiodj/watch_and_upload_cover.ps1 `
  -UploadUrl "http://192.168.1.178:8080/upload" `
  -ApiKey "pirate2024" `
  -CoverFile "C:\RadioDJ\current_cover.jpg" `
  -IntervalSeconds 5
```

## Quick Launcher (Option 2)

Use the helper batch file to start the watcher without typing arguments:

```bat
scripts\radiodj\start_cover_watcher.bat
```

If RadioDJ does not expose the "Save cover to file" setting, use the cache-folder watcher launcher:

```bat
scripts\radiodj\start_cover_watcher_radiodj_folder.bat
```

Default watched folder: `C:\RadioDJv2\Images`

## Auto-Start at Login (Option 3)

Install a Windows Scheduled Task for the current user:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/radiodj/install_cover_watcher_task.ps1
```

To remove the task later:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/radiodj/install_cover_watcher_task.ps1 -Remove
```
