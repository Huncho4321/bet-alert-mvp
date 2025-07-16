
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
    # send_discord_message("✅ Betting bot is live and running.")
    while True:
        now = datetime.now().strftime('%I:%M:%S %p')
        print(f"[✓] Starting search cycle at {now}...", flush=True)

        # Simulate checking live games (fake number)
        total_games_checked = 17  # ← Just a placeholder; real code will replace this
        print(f"[→] Checked {total_games_checked} live games.", flush=True)

        # Simulate 1 fake bet signal to test the flow
        fake_bet = {
            "sport": "NBA",
            "matchup": "Lakers vs Warriors",
            "market": "Moneyline",
            "pick": "Lakers",
            "odds": "-115",
            "units": "1u",
            "confidence": "Strong",
            "note": "Example signal for testing"
        }

        print(f"[💡] Found bet: {fake_bet}", flush=True)
        send_discord_message(
            f"💡 **{fake_bet['sport']} - {fake_bet['matchup']}**\n"
            f"📈 **{fake_bet['market']}**: {fake_bet['pick']} at {fake_bet['odds']}\n"
            f"📊 **Confidence**: {fake_bet['confidence']} | {fake_bet['units']}\n"
            f"📝 {fake_bet['note']}"
        )

        # Sleep for interval
        print(f"[…] Sleeping for {SEARCH_INTERVAL_MINUTES} minutes...\n", flush=True)
        time.sleep(SEARCH_INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    main_loop()
