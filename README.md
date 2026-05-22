# 📁 File Sharing Bot

A Telegram bot that stores files in a private DB channel and shares them via encoded links.  
Built with **Pyrogram** · **MongoDB** · **aiohttp** — deployable on **Render** in minutes.

---

## ✨ Features

| Feature | Details |
|---|---|
| File sharing | Admin sends file → bot returns a shareable `t.me` link |
| Batch links | Generate one link for a range of channel messages |
| Force-subscribe | Require users to join a channel before accessing files |
| Auto-delete | Files auto-delete after a configurable time |
| Protect content | Prevent users from forwarding files |
| Broadcast | Send a message to all bot users |
| Web keep-alive | Built-in aiohttp server — no extra pinger needed on Render |

---

## 🚀 Deploy on Render

### Step 1 — Prerequisites

Before deploying, you need:

1. **Telegram Bot Token** — create a bot via [@BotFather](https://t.me/BotFather)
2. **API ID & API Hash** — from [my.telegram.org](https://my.telegram.org)
3. **DB Channel** — a private Telegram channel; add your bot as **Admin**
4. **MongoDB URI** — free cluster at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)

### Step 2 — Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/file-sharing-bot.git
git push -u origin main
```

### Step 3 — Create a Render Web Service

1. Go to [render.com](https://render.com) → **New → Web Service**
2. Connect your GitHub repo
3. Set:
   - **Environment**: `Docker`
   - **Dockerfile path**: `./Dockerfile`
   - **Plan**: Free (or Starter for always-on)

### Step 4 — Set Environment Variables

In Render → your service → **Environment**, add:

| Variable | Required | Description |
|---|---|---|
| `TG_BOT_TOKEN` | ✅ | Bot token from @BotFather |
| `APP_ID` | ✅ | Telegram API ID |
| `API_HASH` | ✅ | Telegram API Hash |
| `CHANNEL_ID` | ✅ | DB Channel ID (e.g. `-100xxxxxxxxx`) |
| `OWNER_ID` | ✅ | Your Telegram user ID |
| `DATABASE_URL` | ✅ | MongoDB connection string |
| `DATABASE_NAME` | ❌ | Default: `filesharexbot` |
| `ADMINS` | ❌ | Extra admin IDs (space-separated) |
| `FORCE_SUB_CHANNEL` | ❌ | Channel ID for force-sub (0 = off) |
| `PROTECT_CONTENT` | ❌ | `True` to block forwarding |
| `DISABLE_CHANNEL_BUTTON` | ❌ | `True` to hide Share button |
| `AUTO_DELETE_TIME` | ❌ | Seconds before auto-delete (0 = off) |
| `CUSTOM_CAPTION` | ❌ | Override file caption |
| `START_PIC` | ❌ | Image URL for /start message |

### Step 5 — Deploy!

Click **Deploy** — Render builds the Docker image and starts the bot.  
Check **Logs** to confirm: `Bot @yourbot is running!`

---

## 🤖 Bot Commands

| Command | Who | Description |
|---|---|---|
| `/start` | Everyone | Show welcome message or retrieve files |
| `/stats` | Admin | Show bot uptime |
| `/users` | Admin | Count registered users |
| `/broadcast` | Admin | Broadcast a message (reply to use) |
| `/genlink` | Admin | Generate link for one DB-channel message |
| `/batch` | Admin | Generate link for a range of messages |

---

## 📤 How to Share Files

1. Send any file to the bot (as admin)
2. The bot copies it to the DB channel and replies with a `t.me` link
3. Share that link — users click it, bot sends them the file

For batches, use `/batch` and forward the first + last messages of the range.

---

## 🛠 Local Development

```bash
git clone https://github.com/YOUR_USERNAME/file-sharing-bot.git
cd file-sharing-bot
pip install -r requirements.txt
cp .env.example .env   # fill in your values
python3 main.py
```

---

## 📂 Project Structure

```
├── main.py               # Entry point
├── bot.py                # Bot client class
├── config.py             # All config from env vars
├── helper_func.py        # Encode/decode, file fetching, auto-delete
├── database/
│   └── database.py       # MongoDB user CRUD
├── plugins/
│   ├── __init__.py       # aiohttp web server factory
│   ├── route.py          # Health-check endpoint (GET /)
│   ├── start.py          # /start, /users, /broadcast
│   ├── channel_post.py   # Auto-link on channel post + admin upload
│   ├── link_generator.py # /genlink and /batch
│   ├── cbb.py            # Callback query handler
│   └── useless.py        # /stats + catch-all DM reply
├── Dockerfile
├── render.yaml           # Render deploy config
└── .env.example
```

---

## 📝 License

MIT — feel free to fork and customise.
