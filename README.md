---
title: Chartink Scraper
emoji: 📊
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
app_port: 7860
---

# Chartink Scraper — Web Dashboard

A Flask-based web application to run Chartink screener scraping from your browser.

## Features
- ▶ **Manual start/stop** button — anyone who visits the page sees the live state
- ⏰ **Auto-trigger at 5:00 PM IST** (Mon–Fri) — always enabled, accurately timezone-mapped
- ⚡ **Fast-Polling Extraction** — bypasses 15s timeouts for blazing fast scraping (under 5 mins total)
- 📊 **Live progress bar** synced for all visitors
- 📋 **Real-time log stream** fully persistent across tab switches and page reloads
- 📥 **Advanced Excel download** — Dynamically apply filters to the table and download exactly what you see
- 🌐 **Shared state** — if one user starts a run, all visitors see it live

---

## Project Structure

```
chartink-scraper/
├── app.py           # Flask app — routes, scheduler, shared state
├── scraper.py       # Selenium scraper logic (original code, refactored)
├── templates/
│   └── index.html   # Single-page dashboard (pure HTML/CSS/JS)
├── outputs/         # Generated Excel files saved here
├── Dockerfile       # Hugging Face Spaces & Docker configuration
├── requirements.txt # Python dependencies
├── Procfile         # Render/Heroku platform config (Legacy)
└── render.yaml      # Render platform config (Legacy)
```

---

## Local Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Make sure ChromeDriver is installed and in PATH
#    macOS:   brew install chromedriver
#    Ubuntu:  apt install chromium-driver

# 3. Run
python app.py
# Visit http://localhost:5000
```

---

## Deploy to Hugging Face Spaces (Recommended)

1. Create a new **Space** on [Hugging Face](https://huggingface.co/spaces)
2. Choose **Docker** as the Space SDK and select **Blank** template
3. Clone the repo and push this folder's contents to the Hugging Face Space repository
4. The space will automatically build using the existing `Dockerfile` and start the server on port `7860`
5. The `Dockerfile` handles everything including the background installation of Chromium and ChromeDriver.

> **Note**: Free-tier Spaces sleep after 48 hours of inactivity. For the 5 PM auto-trigger to fire flawlessly every day, consider an automatic Space awake script or upgrading to a Pro environment.

---

## Deploy to Render (Legacy)

1. Push this folder to a GitHub repo
2. Go to https://render.com → New → Web Service
3. Connect your GitHub repo
4. Set:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --workers 1 --threads 4 --bind 0.0.0.0:$PORT`
5. Add a **Build Script** to install Chrome:
   ```
   apt-get update && apt-get install -y chromium-driver
   ```
6. Deploy!

---

## How Shared State Works

The Flask server keeps a single in-memory `state` dict protected by a threading lock. Every browser polls `/api/status` every 1.5 seconds. This means:

- User A starts a run → User B opens the page → User B immediately sees the running progress, logs, and progress bar
- If User A leaves → the scrape continues server-side → User B (or anyone) can still see it and download the result

---

## Auto-trigger

APScheduler fires the scraper every **Monday–Friday at 17:00 (5 PM) Indian Standard Time (IST)**. Using the `pytz` library, the timezone is strictly mapped to `Asia/Kolkata` so it executes accurately regardless of where the server is hosted. The scheduler starts with the Flask app and cannot be disabled from the UI. If a manual run is already in progress at 5 PM IST, the auto-trigger is skipped.