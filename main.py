import os
import time
import requests
from datetime import datetime

# ENV VARS
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
BANKROLL = float(os.getenv("BANKROLL", 100))
API_KEY = os.getenv("ODDS_API_KEY")
SEARCH_INTERVAL_MINUTES = int(os.getenv("SEARCH_INTERVAL_MINUTES", 5))

# SETTINGS
MAX_ODDS = -120
MIN_EDGE = 3.0  # in %
MAX_SPREAD_VIG = 0.10  # max 10 cents diff
MAX_TOTAL_VIG = 0.10

def send_discord_message(bet):
    link = f"https://www.bovada.lv/sports"  # generic link; update if you want smarter links
    message = (
        f"📈 **Live Bet Opportunity**\n"
        f"**Sport**: {bet['sport']}\n"
        f"**Matchup**: {bet['matchup']}\n"
        f"**Market**: {bet['market']}\n"
        f"**Pick**: {bet['pick']} ({bet['odds']})\n"
        f"**Units**: {bet['units']} ({bet['dollars']})\n"
        f"**Max Odds**: {MAX_ODDS}\n"
        f"**Requirements**:\n"
        f"> ✅ Line must match Bovada’s\n"
        f"> ✅ Odds must be **{MAX_ODDS}** or better\n"
        f"> ✅ Max spread/total difference = 10 cents\n"
        f"🔗 [Go to Bovada]({link})"
    )
    try:
        requests.post(WEBHOOK_URL, json={"content": message})
        print(f"[→] Sent signal to Discord: {bet['matchup']} - {bet['pick']}", flush=True)
    except Exception as e:
        print(f"❌ Failed to send Discord message: {e}", flush=True)

def get_live_odds():
    url = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?regions=us&markets=h2h,spreads,totals&oddsFormat=american&apiKey={API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ Odds API error: {response.status_code} - {response.text}", flush=True)
            return []
        return response.json()
    except Exception as e:
        print(f"❌ Error fetching odds: {e}", flush=True)
        return []

def calc_implied(odds):
    odds = int(odds)
    return 100 / (abs(odds) + 100) * (100 if odds > 0 else abs(odds))

def process_game(game):
    signals = []
    for bookmaker in game.get("bookmakers", []):
        if bookmaker["key"] != "bovada":
            continue
        markets = bookmaker.get("markets", [])
        for market in markets:
            if market["key"] == "h2h":
                for outcome in market.get("outcomes", []):
                    odds = int(outcome["price"])
                    if odds <= MAX_ODDS:
                        edge = 100 - calc_implied(odds)
                        if edge >= MIN_EDGE:
                            bet = {
                                "sport": game["sport_title"],
                                "matchup": f"{game['home_team']} vs {game['away_team']}",
                                "market": "Moneyline",
                                "pick": outcome["name"],
                                "odds": f"{odds}",
                                "edge": edge,
                                "units": "2u",
                                "dollars": f"${round(BANKROLL * 0.02, 2)}"
                            }
                            signals.append(bet)
            # You can later add logic for spreads/totals here
    return signals

def main_loop():
    print(f"[✓] Betting bot started at {datetime.now().strftime('%I:%M:%S %p')}!", flush=True)
    while True:
        now = datetime.now().strftime('%I:%M:%S %p')
        print(f"[✓] Starting search cycle at {now}...", flush=True)

        games = get_live_odds()
        print(f"[🔍] Checking {len(games)} live games...", flush=True)

        total_signals = 0
        for game in games:
            bets = process_game(game)
            for bet in bets:
                send_discord_message(bet)
                total_signals += 1

        if total_signals == 0:
            print("[✓] No profitable bets found this cycle.", flush=True)

        print(f"[…] Sleeping for {SEARCH_INTERVAL_MINUTES} minutes...\n", flush=True)
        time.sleep(SEARCH_INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    main_loop()
