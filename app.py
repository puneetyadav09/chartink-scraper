import os
import json
import queue
import threading
import pytz
from datetime import datetime, time as dtime
from flask import Flask, render_template, jsonify, send_file, abort
from apscheduler.schedulers.background import BackgroundScheduler

from scraper import run_scraper, WEBSITES

app = Flask(__name__)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)
EXCEL_FILE = os.path.join(OUTPUT_DIR, "chartink.xlsx")

IST = pytz.timezone("Asia/Kolkata")

# ── Shared state (all clients see same data) ─────────────────────────────────
state = {
    "running": False,
    "progress": 0,       # 0-100
    "current": 0,
    "total": len(WEBSITES),
    "logs": [],          # list of log strings
    "last_file": None,   # path to latest Excel file
    "trigger": None,     # "manual" | "auto"
    "started_at": None,
}
state_lock = threading.Lock()
stop_event = threading.Event()


def _emit_log(msg: str):
    ts = datetime.now(IST).strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    with state_lock:
        state["logs"].append(line)
        # keep last 500 lines
        if len(state["logs"]) > 500:
            state["logs"] = state["logs"][-500:]


def _emit_progress(current: int, total: int):
    with state_lock:
        state["current"] = current
        state["total"] = total
        state["progress"] = int((current / total) * 100) if total else 0


def _stop_flag():
    return stop_event.is_set()


def _scraper_thread(trigger: str):
    with state_lock:
        state["running"] = True
        state["progress"] = 0
        state["current"] = 0
        state["logs"] = []
        state["trigger"] = trigger
        state["started_at"] = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
    stop_event.clear()

    output_file = run_scraper(
        log_fn=_emit_log,
        progress_fn=_emit_progress,
        stop_flag=_stop_flag,
        output_dir=OUTPUT_DIR,
    )

    with state_lock:
        state["running"] = False
        state["progress"] = 100 if output_file else state["progress"]
        if output_file:
            state["last_file"] = output_file


def start_scraper(trigger: str = "manual"):
    with state_lock:
        if state["running"]:
            return False
    t = threading.Thread(target=_scraper_thread, args=(trigger,), daemon=True)
    t.start()
    return True


def stop_scraper():
    with state_lock:
        if not state["running"]:
            return False
    stop_event.set()
    return True


# ── Scheduler for 5 PM Mon-Fri ───────────────────────────────────────────────
def scheduled_job():
    _emit_log("🕔 Auto-trigger: 5:00 PM scheduled run starting...")
    start_scraper(trigger="auto")


scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
scheduler.add_job(
    scheduled_job,
    trigger="cron",
    day_of_week="mon-fri",
    hour=17,
    minute=0,
    id="daily_scrape",
)
scheduler.start()


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html", total=len(WEBSITES))


@app.route("/api/status")
def api_status():
    with state_lock:
        file_exists = os.path.exists(EXCEL_FILE)
        file_label = None
        if file_exists:
            mtime = os.path.getmtime(EXCEL_FILE)
            file_label = datetime.fromtimestamp(mtime, IST).strftime("%Y-%m-%d %H:%M")

        job = scheduler.get_job("daily_scrape")
        next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M %Z") if job and job.next_run_time else "—"

        return jsonify({
            "running": state["running"],
            "progress": state["progress"],
            "current": state["current"],
            "total": state["total"],
            "logs": state["logs"],
            "trigger": state["trigger"],
            "started_at": state["started_at"],
            "has_file": file_exists,
            "file_name": f"chartink_{datetime.now(IST).strftime('%Y-%m-%d')}.xlsx",
            "file_updated": file_label,
            "auto_trigger_enabled": True,
            "next_run": next_run,
        })


@app.route("/api/start", methods=["POST"])
def api_start():
    ok = start_scraper(trigger="manual")
    if ok:
        return jsonify({"status": "started"})
    return jsonify({"status": "already_running"}), 409


@app.route("/api/stop", methods=["POST"])
def api_stop():
    ok = stop_scraper()
    if ok:
        return jsonify({"status": "stopping"})
    return jsonify({"status": "not_running"}), 409


@app.route("/api/download")
def api_download():
    if not os.path.exists(EXCEL_FILE):
        abort(404, "No Excel file available yet.")
    # Download name includes today's date so each download is identifiable
    download_name = f"chartink_{datetime.now(IST).strftime('%Y-%m-%d')}.xlsx"
    return send_file(EXCEL_FILE, as_attachment=True, download_name=download_name)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)