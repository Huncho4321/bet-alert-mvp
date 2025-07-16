import os
import time
import requests
from datetime import datetime

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
BANKROLL = float(os.getenv("BANKROLL", 100))
SEARCH_INTERVAL_MINUTES = int(os.getenv("SEARCH_INTERVAL_MINUTES", 5))

def send_discord_message(message):
    if not WEBHOOK_URL:
        print("❌ WEBHOOK_URL not set.")
        return
    try:
        requests.post(WEBHOOK_URL, json={"content": message})
        print(f"[→] Sent to Discord: {message}", flush=True)
    except Exception as e:
        print(f"❌ Failed to send message: {e}", flush=True)

def main_loop():
    print(f"[✓] Betting bot started at {datetime.now().strftime('%I:%M:%S %p')}!", flush=True)
    send_discord_message("✅ Betting bot is live and running.")
    while True:
        now = datetime.now().strftime('%I:%M:%S %p')
        print(f"[✓] Starting search cycle at {now}...", flush=True)

        # Simulate finding 0 profitable bets
        print("[✓] No profitable bets found this cycle.", flush=True)

        # Sleep for interval
        print(f"[…] Sleeping for {SEARCH_INTERVAL_MINUTES} minutes...
", flush=True)
        time.sleep(SEARCH_INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    main_loop()
