import os
import time
import requests
from datetime import datetime

# ENVIRONMENT VARIABLES
API_KEY = os.getenv("API_KEY")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
BANKROLL = float(os.getenv("BANKROLL", 100))
SEARCH_INTERVAL_MINUTES = int(os.getenv("SEARCH_INTERVAL_MINUTES", 5))

# SETTINGS
MAX_ML_ODDS = -140
MAX_SPREAD_TOTAL_ODDS = -110
ALLOWED_LINE_DIFFERENCE = 0  # No range for spreads/totals
UNIT_SIZE = 3  # $3 base per unit
HIGH_CONFIDENCE_UNIT_MULTIPLIER = 2  # Multiplies unit size for strong bets

# TOP LEAGUES ONLY
ALLOWED_LEAGUES = {
    "basketball_nba",
    "basketball_nba_summer_league",
    "basketball_wnba",
    "football_nfl",
    "baseball_mlb",
    "ice_hockey_nhl",
    "soccer_usa_mls",
    "soccer_epl",
    "soccer_uefa_champs_league",
    "tennis_atp",
    "tennis_wta"
}

def send_discord_message(message):
    if not WEBHOOK_URL:
        print("❌ DISCORD_WEBHOOK_URL not set.")
        return
    try:
        requests.post(WEBHOOK_URL, json={"content": message})
        print(f"[→] Sent to Discord: {message}", flush=True)
    except Exception as e:
        print(f"❌ Failed to send message: {e}", flush=True)

def fetch_live_games():
    try:
        response = requests.get(
            "https://api.the-odds-api.com/v4/sports/odds",
            params={"apiKey": API_KEY, "regions": "us", "markets": "h2h,spreads,totals", "oddsFormat": "american", "dateFormat": "iso"},
            timeout=10
        )
        if response.status_code != 200:
            print(f"❌ Odds API error: {response.status_code} - {response.text}", flush=True)
            return []
        games = response.json()
        return [g for g in games if g.get("sport_key") in ALLOWED_LEAGUES]
    except Exception as e:
        print(f"❌ Failed to fetch games: {e}", flush=True)
        return []

def main_loop():
    print(f"[✓] Betting bot started at {datetime.now().strftime('%I:%M:%S %p')}!", flush=True)
    send_discord_message("✅ Betting bot is live and running.")

    while True:
        now = datetime.now().strftime('%I:%M:%S %p')
        print(f"[✓] Starting search cycle at {now}...", flush=True)

        live_games = fetch_live_games()
        print(f"[🔍] Checking {len(live_games)} live games...", flush=True)

        # 🆕 SHOW FIRST 3 GAMES BEING PROCESSED
        for game in live_games[:3]:
            teams = game.get('teams', [])
            commence = game.get('commence_time', 'unknown')
            print(f"[🆔] {game.get('sport_key')} | {teams} | {commence}", flush=True)

        # Placeholder: Simulated fake bet (replace with real logic)
        fake_bet = {
            "sport": "NBA",
            "matchup": "Lakers vs Warriors",
            "market": "Moneyline",
            "pick": "Lakers",
            "odds": "-120",
            "units": "2u ($6)"
        }

        send_discord_message(
            f"✅ **{fake_bet['sport']}** | {fake_bet['matchup']}\n"
            f"**Market:** {fake_bet['market']}\n"
            f"**Pick:** {fake_bet['pick']}\n"
            f"**Odds:** {fake_bet['odds']}\n"
            f"**Units:** {fake_bet['units']}\n"
            f"**Worst ML to accept:** {MAX_ML_ODDS}\n"
            f"**Worst Spread/Total to accept:** {MAX_SPREAD_TOTAL_ODDS} exact line only\n"
            f"📍 Only place if Bovada odds & line match"
        )

        print(f"[…] Sleeping for {SEARCH_INTERVAL_MINUTES} minutes...", flush=True)
        time.sleep(SEARCH_INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    main_loop()
