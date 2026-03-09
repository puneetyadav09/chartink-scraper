# Chartink Scraper — Web Dashboard

A Flask-based web application to run Chartink screener scraping from your browser.

## Features
- ▶ **Manual start/stop** button — anyone who visits the page sees the live state
- ⏰ **Auto-trigger at 5:00 PM** (Mon–Fri) — always enabled, cannot be disabled
- 📊 **Live progress bar** synced for all visitors
- 📋 **Real-time log stream** showing backend output
- 📥 **One-click Excel download** of the latest scraped file
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
├── requirements.txt
├── Procfile         # For Render/Heroku deployment
├── render.yaml      # Render platform config
└── runtime.txt      # Python 3.11
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

## Deploy to Render

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

> **Note**: Render's free tier sleeps after inactivity. Use the Starter plan ($7/mo) for always-on operation so the 5 PM auto-trigger works reliably.

---

## How Shared State Works

The Flask server keeps a single in-memory `state` dict protected by a threading lock. Every browser polls `/api/status` every 1.5 seconds. This means:

- User A starts a run → User B opens the page → User B immediately sees the running progress, logs, and progress bar
- If User A leaves → the scrape continues server-side → User B (or anyone) can still see it and download the result

---

## Auto-trigger

APScheduler fires the scraper every **Monday–Friday at 17:00 (5 PM)**. The scheduler starts with the Flask app and cannot be disabled from the UI. If a manual run is already in progress at 5 PM, the auto-trigger is skipped.