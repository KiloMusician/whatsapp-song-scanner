# 🎵 Telegram Song Scanner → MariaDB → RadioDJ

A production-ready system that listens to a Telegram group for song requests, matches them against MusicBrainz using fuzzy matching, stores verified results in MariaDB, and queues approved songs directly into RadioDJ.

## ✨ Features

- **Telegram Bot**: Receives song requests from a Telegram group in natural language
- **Intelligent Song Matching**: MusicBrainz search with fuzzy matching and confidence scoring
- **Fallback APIs**: Spotify and Deezer as secondary match sources
- **MariaDB Storage**: Tracks chats, messages, extracted songs, matches, and request history
- **RadioDJ Integration**: Queues songs via REST API and direct database access
- **Web Dashboard**: Approve or reject pending requests from a browser UI
- **Background Automation**: APScheduler handles scanning and sync automatically
- **Redis Cache**: Rate-limit-safe caching for MusicBrainz API calls
- **Production Ready**: Docker deployment, health checks, structured logging

## 🤖 How It Works

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   Telegram      │───▶│  Message Parser  │───▶│  MusicBrainz     │
│   Group Chat    │    │  (extract song)  │    │  Search          │
└─────────────────┘    └──────────────────┘    └──────────────────┘
                                                        │
┌─────────────────┐    ┌──────────────────┐    ┌───────▼──────────┐
│   RadioDJ       │◀───│  Web Dashboard   │◀───│  Fuzzy Matcher   │
│   Playlist      │    │  Approve/Reject  │    │  + Confidence    │
└─────────────────┘    └──────────────────┘    └──────────────────┘
                                  │
                           ┌──────▼──────┐
                           │   MariaDB   │
                           │   Storage   │
                           └─────────────┘
```

1. Someone sends a message in the Telegram group:
   ```
   Play Bohemian Rhapsody by Queen
   ```
2. The bot extracts the song title and artist, searches MusicBrainz, and returns the best match.
3. The matched song is stored in MariaDB as a pending request.
4. You open the web dashboard and approve it.
5. The song is queued directly into RadioDJ.

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose (app runs on Linux host `xanadu`)
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- RadioDJ running on Windows (REST plugin on port 7000)
- Python 3.11+ (for local development only)

### 1. Configure Environment

```bash
cp .env.example .env
nano .env
```

Key variables:

```env
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_group_chat_id_here

# App database (MariaDB in Docker)
MARIADB_HOST=mariadb
MARIADB_DATABASE=song_scanner
MARIADB_USERNAME=scanner_bot
MARIADB_PASSWORD=changeme

# RadioDJ (Windows PC on local network)
RADIODJ_API_URL=http://192.168.1.x:7000
RADIODJ_API_KEY=password
RADIODJ_DB_HOST=192.168.1.x
RADIODJ_DB_NAME=radiodj2
RADIODJ_DB_USER=root
RADIODJ_DB_PASS=yourpassword

# Redis
REDIS_HOST=redis
```

### 2. Start Services (on Linux host)

```bash
git clone https://github.com/KiloMusician/whatsapp-song-scanner.git
cd whatsapp-song-scanner
docker compose -f docker/docker-compose.yml up -d
```

### 3. Verify

```bash
curl http://localhost:5000/api/v1/health
```

Expected:
```json
{
  "status": "healthy",
  "components": {
    "cache": { "connected": true, "status": "healthy" },
    "radiodj": { "api_available": true, "database_available": true, "status": "healthy" }
  }
}
```

### 4. Open Dashboard

```
http://xanadu:5000
```

## 📡 API Endpoints

### Health & Monitoring

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | System health check |
| `GET` | `/api/v1/metrics` | Application metrics |
| `GET` | `/api/v1/scan/status` | Scanner state and stats |
| `GET` | `/api/v1/radiodj/status` | RadioDJ now-playing and queue |

### Telegram Webhook

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/webhook/telegram` | Receive updates from Telegram |

### Song Requests

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/requests/pending` | List pending requests |
| `GET` | `/api/v1/requests/recent` | Recent requests (all statuses) |
| `POST` | `/api/v1/requests/approve` | Approve and queue to RadioDJ |
| `POST` | `/api/v1/requests/reject` | Reject a request |
| `GET` | `/api/v1/requests/<id>/events` | Queue event timeline |

## ⚙️ Telegram Bot Setup

1. Message [@BotFather](https://t.me/BotFather), send `/newbot`, follow the prompts.
2. Copy the **Bot Token**.
3. Add the bot to your Telegram group as an administrator.
4. Get the **Chat ID** — send a message to the group, then call:
   ```
   https://api.telegram.org/bot<TOKEN>/getUpdates
   ```
   and read `message.chat.id`.
5. Set the webhook:
   ```bash
   curl -F "url=https://your-host/api/v1/webhook/telegram" \
        -F "secret_token=MY_SECRET" \
        https://api.telegram.org/bot<TOKEN>/setWebhook
   ```
6. Add `TELEGRAM_WEBHOOK_SECRET=MY_SECRET` to `.env`.

### Supported Request Patterns

```
Play Bohemian Rhapsody by Queen
I want to hear Blinding Lights by The Weeknd
Can you play Hoe Cakes by MF Doom
request: Daft Punk - Get Lucky
song? Blue (Da Ba Dee)
```

## 🎙️ RadioDJ Integration

RadioDJ runs on a Windows PC on the local network. The bot connects in two ways:

| Method | How | When Used |
|--------|-----|-----------|
| REST API | `GET http://192.168.1.x:7000/opt?command=...&auth=password` | Queueing songs |
| Direct DB | MySQL connection to `radiodj2` on Windows | Validation and fallback |

**Requirements on Windows:**
- RadioDJ REST plugin enabled and running on port 7000
- MariaDB `bind-address=0.0.0.0` in `my.ini` to allow remote connections
- Root user with `%` host permission

## 🗄️ Database Schema

Five core tables in MariaDB:

| Table | Purpose |
|-------|---------|
| `telegram_chats` | Monitored Telegram conversations |
| `chat_messages` | Individual messages |
| `extracted_songs` | Song phrases parsed from messages |
| `matched_songs` | Verified matches from MusicBrainz |
| `song_requests` | Pending/approved/rejected requests for RadioDJ |

## 📁 Project Structure

```
whatsapp-song-scanner/
├── src/
│   ├── main.py                    # Flask app + all API routes
│   ├── dashboard.html             # Web UI (served at /)
│   ├── message_handler.py         # Telegram update processor
│   ├── telegram_bot.py            # Bot polling mode
│   ├── core/
│   │   ├── scheduler.py           # APScheduler jobs
│   │   ├── health_check.py        # Health monitoring
│   │   └── state_manager.py       # App state
│   ├── database/
│   │   ├── models.py              # SQLAlchemy models
│   │   └── operations.py          # CRUD operations
│   ├── text_processing/
│   │   ├── message_parser.py      # Extract song/artist from text
│   │   ├── text_cleaner.py        # Normalize input
│   │   └── keyword_extractor.py
│   ├── music_matching/
│   │   ├── musicbrainz_client.py  # MusicBrainz API
│   │   ├── fuzzy_matcher.py       # Confidence scoring
│   │   ├── song_validator.py      # Match validation
│   │   └── matching_orchestrator.py
│   ├── radiodj_integration/
│   │   ├── radiodj_client.py      # REST API + MySQL client
│   │   ├── playlist_manager.py
│   │   └── sync_service.py
│   └── utils/
│       ├── logger.py
│       ├── cache.py               # Redis wrapper
│       └── rate_limiter.py
├── config/
│   ├── settings.py                # All env var loading
│   ├── database.py
│   └── logging_config.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── tests/
├── requirements.txt
└── .env.example
```

## 🐳 Docker Services

| Service | Port | Purpose |
|---------|------|---------|
| `whatsapp-song-scanner` | 5000 | Flask app + dashboard |
| `scanner-mariadb` | 3306 | App database |
| `scanner-redis` | 6379 | Cache layer |

```bash
# Start
docker compose -f docker/docker-compose.yml up -d

# Rebuild after code changes
docker compose -f docker/docker-compose.yml build song-scanner-bot
docker compose -f docker/docker-compose.yml up -d --force-recreate song-scanner-bot

# Logs
docker logs whatsapp-song-scanner --tail 50 -f

# Stop
docker compose -f docker/docker-compose.yml down
```

## 🛠️ CLI Commands

```bash
# Status
python -m src.cli status

# Sync pending requests to RadioDJ
python -m src.cli sync
python -m src.cli sync --limit=10

# Manage requests
python -m src.cli list-requests
python -m src.cli approve 5
python -m src.cli reject 5 --notes="not available"
```

## 🧪 Testing

```bash
# All tests
pytest -v

# With coverage
pytest --cov=src --cov-report=html

# Specific suites
pytest tests/unit/test_text_processing.py -v
pytest tests/unit/test_fuzzy_matcher.py -v
```

## 📈 Performance & Monitoring

- **APScheduler**: Background scan every 5 min, RadioDJ sync every 2 min
- **Redis**: Caches MusicBrainz results to respect rate limits
- **Prometheus** (optional): `http://localhost:9090`
- **Health endpoint**: `http://xanadu:5000/api/v1/health`

## 🔒 Security

- Store all credentials in `.env` — never commit secrets
- Validate Telegram webhook requests using `X-Telegram-Bot-Api-Secret-Token`
- RadioDJ REST plugin secured with an auth parameter
- Rate limiting on all outbound API calls

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m 'Add my feature'`
4. Push and open a Pull Request

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

## 🙏 Credits

- [MusicBrainz](https://musicbrainz.org/) — open music encyclopedia
- [RadioDJ](http://www.radiodj.ro/) — radio automation software
- [Flask](https://flask.palletsprojects.com/) — web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) — ORM
