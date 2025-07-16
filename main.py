import os
import time
import requests
from datetime import datetime

API_KEY = os.getenv("ODDS_API_KEY")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
BANKROLL = float(os.getenv("BANKROLL", 100))

MAX_MONEYLINE = -120
MAX_MONEYLINE_SCRAPE = -140
MAX_SPREAD_TOTAL_ODDS = -110
SEARCH_INTERVAL_MINUTES = int(os.getenv("SEARCH_INTERVAL_MINUTES", 5))
UNIT_SIZE = round(BANKROLL * 0.03)  # 3% of bankroll

TOP_LEAGUES = [
    "NBA", "NBA Summer League",
    "WNBA",
    "NFL", "NCAA Football",
    "MLB",
    "NHL",
    "UEFA Champions League", "English Premier League", "La Liga",
    "Serie A", "Bundesliga", "Ligue 1",
    "Copa America", "EURO", "World Cup", "MLS"
]

def send_discord_message(message):
    if not WEBHOOK_URL:
        print("❌ DISCORD_WEBHOOK_URL not set.")
        return
    try:
        requests.post(WEBHOOK_URL, json={"content": message})
        print(f"[→] Sent to Discord: {message}", flush=True)
    except Exception as e:
        print(f"❌ Failed to send message: {e}", flush=True)

def fetch_live_odds():
    url = f"https://api.the-odds-api.com/v4/sports/?apiKey={API_KEY}&regions=us&markets=h2h,spreads,totals&oddsFormat=american&dateFormat=iso"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ Odds API error: {response.status_code} - {response.text}", flush=True)
            return []
        games = response.json()
        return games
    except Exception as e:
        print(f"❌ Failed to fetch odds: {e}", flush=True)
        return []

def analyze_and_signal(games):
    sent_signals = []
    for game in games:
        league = game.get("sport_title", "")
        if league not in TOP_LEAGUES:
            continue

        teams = game.get("home_team", "") + " vs " + game.get("away_team", "")
        markets = game.get("bookmakers", [])

        for book in markets:
            if book["title"].lower() != "bovada":
                continue

            for market in book["markets"]:
                if market["key"] == "h2h":
                    for outcome in market["outcomes"]:
                        team = outcome["name"]
                        odds = int(outcome["price"])
                        if odds <= MAX_MONEYLINE and odds >= MAX_MONEYLINE_SCRAPE:
                            signal = f"✅ **{league}** | {teams}\n**Market:** ML\n**Pick:** {team}\n**Odds:** {odds}\n**Units:** 2u (${UNIT_SIZE})\n**Worst ML to accept:** {MAX_MONEYLINE}\n**Worst Spread/Total to accept:** {MAX_SPREAD_TOTAL_ODDS} exact line only\n📍 Only place if Bovada odds & line match"
                            send_discord_message(signal)
                            sent_signals.append(signal)
                elif market["key"] in ["spreads", "totals"]:
                    for outcome in market["outcomes"]:
                        odds = int(outcome["price"])
                        if odds == MAX_SPREAD_TOTAL_ODDS:
                            signal = f"✅ **{league}** | {teams}\n**Market:** {'Spread' if market['key']=='spreads' else 'Total'}\n**Pick:** {outcome['name']} @ {outcome['point']}\n**Odds:** {odds}\n**Units:** 2u (${UNIT_SIZE})\n**Worst ML to accept:** {MAX_MONEYLINE}\n**Worst Spread/Total to accept:** {MAX_SPREAD_TOTAL_ODDS} exact line only\n📍 Only place if Bovada odds & line match"
                            send_discord_message(signal)
                            sent_signals.append(signal)
    if not sent_signals:
        print("No profitable bets found this cycle.", flush=True)

def main_loop():
    print(f"[✓] Betting bot started at {datetime.now().strftime('%I:%M:%S %p')}!", flush=True)
    send_discord_message("✅ Betting bot is live and running.")
    while True:
        now = datetime.now().strftime('%I:%M:%S %p')
        print(f"[✓] Starting search cycle at {now}...", flush=True)

        games = fetch_live_odds()
        print(f"[🔍] Checking {len(games)} live games...", flush=True)
        analyze_and_signal(games)

        print(f"[…] Sleeping for {SEARCH_INTERVAL_MINUTES} minutes...", flush=True)
        time.sleep(SEARCH_INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    main_loop()
