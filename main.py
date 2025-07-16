import os
import time
import requests
from datetime import datetime
import random  # Remove this when using real logic

# Environment variables
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
BANKROLL = float(os.getenv("BANKROLL", 100))
API_KEY = os.getenv("ODDS_API_KEY")
SEARCH_INTERVAL_MINUTES = int(os.getenv("SEARCH_INTERVAL_MINUTES", 5))

# Constants
UNIT_SIZE = 3  # $3 per unit
MAX_ODDS_ML = -120
MAX_ODDS_SPREAD_TOTAL = -110
ML_ALLOWED_RANGE = 10  # 10 cent range for ML
COOLDOWN_TRACKER = {}

def send_discord_message(message):
    if not WEBHOOK_URL:
        print("❌ DISCORD_WEBHOOK_URL not set.")
        return
    try:
        requests.post(WEBHOOK_URL, json={"content": message})
        print(f"[→] Sent to Discord: {message}", flush=True)
    except Exception as e:
        print(f"❌ Failed to send message: {e}", flush=True)

def is_valid_bet(bet_type, odds, actual_line, expected_line):
    try:
        odds = int(odds)
    except ValueError:
        return False
    if bet_type == "ML":
        return odds >= (MAX_ODDS_ML - ML_ALLOWED_RANGE) and odds <= MAX_ODDS_ML
    else:
        return odds <= MAX_ODDS_SPREAD_TOTAL and actual_line == expected_line

def format_bet_message(bet):
    units = bet['units']
    dollars = units * UNIT_SIZE
    return (
        f"✅ **{bet['sport']}** | {bet['matchup']}\n"
        f"**Market:** {bet['market']}\n"
        f"**Pick:** {bet['pick']}\n"
        f"**Odds:** {bet['odds']}\n"
        f"**Units:** {units}u (${dollars})\n"
        f"**Worst ML to accept:** -{abs(MAX_ODDS_ML)}\n"
        f"**Worst Spread/Total to accept:** -{abs(MAX_ODDS_SPREAD_TOTAL)} exact line only\n"
        f"📍 Only place if Bovada odds & line match"
    )

def main_loop():
    print(f"[✓] Betting bot started at {datetime.now().strftime('%I:%M:%S %p')}!", flush=True)
    send_discord_message("✅ Betting bot is live and running.")

    while True:
        now = datetime.now().strftime('%I:%M:%S %p')
        print(f"[✓] Starting search cycle at {now}...", flush=True)

        # Placeholder: Replace with real API calls
        live_games = ["Lakers vs Warriors", "Yankees vs Red Sox", "USA vs Mexico"]
        print(f"[🔍] Checking {len(live_games)} live games...", flush=True)

        bets_this_round = 0
        for game in live_games:
            if COOLDOWN_TRACKER.get(game):
                continue

            # Simulate bet
            bet_type = random.choice(["ML", "Spread", "Total"])
            odds = str(random.choice(["-120", "-115", "-110", "-105", "-100", "-125"]))
            if bet_type == "ML" and not is_valid_bet("ML", odds, None, None):
                continue
            if bet_type in ["Spread", "Total"] and not is_valid_bet("Spread", odds, "-3.5", "-3.5"):
                continue

            bet = {
                "sport": "NBA",
                "matchup": game,
                "market": bet_type,
                "pick": "Lakers",
                "odds": odds,
                "units": 2
            }

            msg = format_bet_message(bet)
            send_discord_message(msg)
            COOLDOWN_TRACKER[game] = True
            bets_this_round += 1

        if bets_this_round == 0:
            print("[✓] No profitable bets found this cycle.", flush=True)

        print(f"[…] Sleeping for {SEARCH_INTERVAL_MINUTES} minutes...", flush=True)
        time.sleep(SEARCH_INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    main_loop()
