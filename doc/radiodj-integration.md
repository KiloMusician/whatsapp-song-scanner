# RadioDJ Integration

## REST Plugin Endpoint

The RadioDJ REST plugin listens on `http://localhost:7000`. The correct endpoint path is `/opt`:

```
GET http://localhost:7000/opt?auth=<password>&command=<command>&arg=<value>
```

### Commands

| Command | Description | arg |
|---------|-------------|-----|
| `LoadTrackToBottom` | Add song to bottom of queue | Song ID from `songs` table |

### Example

```
GET http://localhost:7000/opt?auth=password&command=LoadTrackToBottom&arg=183
```

Returns `<string>200</string>` on success.

> **Note:** `/SetItem`, `/addtrack`, `/npjson`, `/p`, and `/Status` all return 404. Only `/opt` works with this plugin version.

## Database Fallback

When the REST plugin is unavailable, songs can be added via direct DB insert into the `queuelist` table. The `ETA` column **must** be set to `NOW()` — RadioDJ ignores rows with the default value (`2002-01-01 00:00:01`).

```sql
INSERT INTO queuelist (songID, ETA, duration, artist, associated_artists, title, album)
SELECT ID, NOW(), duration, artist, associated_artists, title, album
FROM songs WHERE ID = ?;
```

RadioDJ loads `queuelist` into memory at startup and does not re-read it while running. A restart is required for DB-inserted rows to appear. The `/opt` API path is preferred because it updates the live in-memory queue immediately.

## Pipeline: Telegram → RadioDJ

1. User sends song request in Telegram group
2. `telegram_bot.py` (polling mode) receives the message
3. Message parsed → MusicBrainz search → fuzzy match (0–100 confidence)
4. Match saved to `song_scanner` DB, request auto-approved if confidence ≥ 90
5. `playlist_manager.add_song_to_playlist()` called:
   - Finds track ID via `find_track_in_library()` (exact title match, then fuzzy LIKE)
   - Tries REST API (`/opt?command=LoadTrackToBottom&arg=<id>`)
   - Falls back to DB insert if API fails
6. Telegram reply sent with match details and queue status

## Album Art Upload (RadioDJ → Icecast PC)

Use this when you want RadioDJ cover art to be pushed to a LAN upload server.

- Upload server: `http://192.168.1.178:8080/upload`
- API header: `X-Api-Key: pirate2024`
- LAN-only setup (no internet exposure)

### Test Upload (Windows)

```bat
curl -X POST "http://192.168.1.178:8080/upload" -H "X-Api-Key: pirate2024" -F "file=@cover.jpg"
```

### Option A: Event-Based Upload (Recommended)

1. In RadioDJ, save cover art to file:
   - `Settings -> General -> Cover Art -> Save cover to file`
   - Path: `C:\RadioDJ\current_cover.jpg`
2. Use `scripts/radiodj/upload_cover.bat` (or copy it beside RadioDJ and edit variables).
3. In RadioDJ: `Settings -> Events -> After track change` and run the batch file.

This uploads exactly once per track change.

### Option B: Timed Watcher Upload

1. Keep the same RadioDJ cover-art file path: `C:\RadioDJ\current_cover.jpg`
2. Run `scripts/radiodj/watch_and_upload_cover.ps1` when RadioDJ starts.
3. Script checks for cover file changes every 5 seconds and uploads only on change.

Example:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/radiodj/watch_and_upload_cover.ps1
```

Use this mode if RadioDJ events are not available or not reliable.

## Key Config (`.env`)

| Variable | Purpose |
|----------|---------|
| `RADIODJ_API_URL` | REST plugin URL (`http://localhost:7000`) |
| `RADIODJ_API_KEY` | Plugin password |
| `RADIODJ_DB_HOST` | MariaDB host (`127.0.0.1`) |
| `RADIODJ_DB_NAME` | Database name (`radiodj2`) |
| `RADIODJ_DB_USER` | DB user (`root`) |
| `RADIODJ_DB_PASS` | DB password |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token |
| `TELEGRAM_CHAT_ID` | Target chat/group ID |

## Bugs Fixed (foolish-fix branch)

- **Wrong endpoint:** Changed `/SetItem` → `/opt` for REST plugin
- **Confidence scale:** `telegram_bot.py` was dividing confidence by 100 before storing, causing values like `1.0` instead of `100.0` — broke auto-approve (threshold 90)
- **Wrong song match:** `find_track_in_library()` now prefers exact title match before fuzzy LIKE
- **Missing ETA:** `queuelist` inserts now set `ETA = NOW()` so RadioDJ recognizes them
