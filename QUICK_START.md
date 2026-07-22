# ⚡ QUICK START GUIDE

**5-Minute Setup for Telegram Song Scanner**

---

## ✅ Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running
- Telegram Bot Token (from @BotFather)
- 5 GB free disk space
- Ports 5000, 3306, 6379 available

---

## 🚀 Installation (5 minutes)

### **Step 1: Configure Environment** (2 min)
```bash
# Copy configuration template
cp .env.example .env

# Edit with your settings
# Choose: Twilio OR Evolution API
nano .env
```

### **Step 2: Start Services** (2 min)
```bash
# Start Docker containers
docker-compose -f docker/docker-compose.yml up -d

# Wait for services to start (should see all running)
docker-compose -f docker/docker-compose.yml ps
```

### **Step 3: Access Dashboard** (1 min)
```bash
# Open in browser
http://localhost:5000
```

---

## 📡 Configure Telegram Bot

### **Setup Telegram Bot (5 minutes)**
1. Go to https://t.me/BotFather
2. Send `/newbot` and follow instructions
3. Get your **Bot Token** (something like `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)
4. Add your bot to a Telegram group as administrator
5. Send `/mybots` to get your bot's info and get the **Chat ID**
6. Add to `.env`:
   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TELEGRAM_CHAT_ID=your_group_chat_id_here
   ```

### **Test Your Bot**
Send a message in your group like:
```
Play Bohemian Rhapsody by Queen
```

The bot should reply with the song match!

---

## 🎯 Configure RadioDJ

### **Method 1: API (if available)**
```env
RADIODJ_API_URL=http://your-radiodj:8080/api
RADIODJ_API_KEY=your_api_key
```

### **Method 2: Direct Database**
```env
RADIODJ_DB_PATH=/path/to/RadioDJ/Database.db
RADIODJ_DEFAULT_PLAYLIST_ID=1
```

---

## 📊 Dashboard Quick Tour

### **Access Dashboard**
```
http://localhost:5000
```

### **What You See**
- **Pending Requests**: Songs awaiting your approval
- **Approve Button**: ✓ Click to queue song to RadioDJ
- **Reject Button**: ✗ Click to skip song
- **Status**: Green = System healthy

### **Workflow**
1. Someone requests a song on Telegram
2. System matches it to MusicBrainz
3. **You see it in Dashboard → Pending**
4. Click ✓ Approve
5. **Song automatically added to RadioDJ**

---

## ✅ Verify Everything Works

```bash
# Check system health
curl http://localhost:5000/api/v1/health

# View pending requests
curl http://localhost:5000/api/v1/requests/pending

# Test approval
curl -X POST http://localhost:5000/api/v1/requests/approve \
  -H "Content-Type: application/json" \
   -d '{"request_id": 1}'
```

### **Run Focused Regression Test**
```powershell
# From the repo root, with the virtual environment active
pytest tests/unit/test_jamendo_to_radiodj.py -v
```

---

## �️ Local Development (Without Docker)

### **Start Telegram Bot**
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Start bot in background with logs
Start-Process -FilePath ".\.venv\Scripts\python.exe" -ArgumentList "-m", "src.telegram_bot" -RedirectStandardOutput "bot_out.log" -RedirectStandardError "bot_err.log" -NoNewWindow

# Or run in foreground (see output directly)
.\.venv\Scripts\python.exe -m src.telegram_bot
```

### **Start Flask API Server**
```powershell
.\.venv\Scripts\python.exe -m src.main
```

### **Monitor Bot Logs**
```powershell
# Watch error log in real-time
Get-Content bot_err.log -Tail 20 -Wait

# View recent output
Get-Content bot_out.log -Tail 30
```

### **Check if Bot is Running**
```powershell
Get-Process python -ErrorAction SilentlyContinue | Select-Object Id, ProcessName
```

### **Stop All Python Processes**
```powershell
Stop-Process -Name python -Force -ErrorAction SilentlyContinue
```

---

## �🐛 Quick Troubleshooting

### **Dashboard won't load**
```bash
docker-compose -f docker/docker-compose.yml restart song-scanner-bot
```

### **Can't connect to Telegram**
```bash
# Check bot token and chat ID in .env
# Verify bot is added to group as admin
# View logs
docker logs whatsapp-song-scanner | tail -20
```

### **RadioDJ not syncing**
```bash
# Verify path/API credentials in .env
# Restart services
docker-compose -f docker/docker-compose.yml restart
```

### **Port already in use**
```bash
# Change port in .env
APP_PORT=5001

# Restart
docker-compose down && docker-compose up -d
```

---

## 📞 Next Steps

- ✅ Open dashboard: http://localhost:5000
- ✅ Test song request via Telegram
- ✅ Approve request in dashboard
- ✅ Verify it appears in RadioDJ
- 📖 See [DEPLOYMENT.md](DEPLOYMENT.md) for advanced config

---

## 🛑 Stop Services

```bash
docker-compose -f docker/docker-compose.yml down
```

---

**That's it! Your system is running.** 🎉

Refer to [DEPLOYMENT.md](DEPLOYMENT.md) for detailed configuration and troubleshooting.
