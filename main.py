import os
import time
import requests
from datetime import datetime

# === Environment Variables ===
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")
BANKROLL = float(os.getenv("BANKROLL", 100))
SEARCH_INTERVAL_MINUTES = int(os.getenv("SEARCH_INTERVAL_MINUTES", 5))

# === Settings ===
ML_MAX_ODDS = -140
SPREAD_TOTAL_MAX_ODDS = -110

# === Supported Sports (Top Leagues Only + NBA Summer League) ===
SPORT_KEYS = [
    "basketball_nba",            # NBA & Summer League
    "baseball_mlb",              # MLB
    "soccer_epl",                # English Premier League
    "soccer_uefa_champs_league",# UEFA CL
    "soccer_laliga",             # La Liga
    "soccer_bundesliga",        # Bundesliga
    "soccer_serie_a",           # Serie A
    "soccer_ligue_one",         # Ligue 1
    "tennis_atp",               # ATP
    "hockey_nhl",               # NHL
    "football_nfl",             # NFL (in season)
    "basketball_wnba",          # WNBA
]

# === Send to Discord ===
def send_discord_message(message):
    if not WEBHOOK_URL:
        print("❌ WEBHOOK_URL not set.")
        return
    try:
        requests.post(WEBHOOK_URL, json={"content": message})
        print(f"[→] Sent to Discord:\n{message}", flush=True)
    except Exception as e:
        print(f"❌ Failed to send message: {e}", flush=True)

# === Odds Filter ===
def is_valid_bet(market, odds):
    try:
        odds = int(odds)
    except:
        return False
    if market == "h2h":
        return odds >= ML_MAX_ODDS
    else:
        return odds >= SPREAD_TOTAL_MAX_ODDS

# === Main Loop ===
def main_loop():
    print(f"[✓] Betting bot started at {datetime.now().strftime('%I:%M:%S %p')}!", flush=True)
    send_discord_message("✅ Betting bot is live and running.")
    while True:
        print(f"[✓] Starting search cycle at {datetime.now().strftime('%I:%M:%S %p')}...", flush=True)
        total_checked = 0
        for sport in SPORT_KEYS:
            url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
            params = {
                "apiKey": ODDS_API_KEY,
                "regions": "us",
                "markets": "h2h,spreads,totals",
                "oddsFormat": "american",
                "dateFormat": "iso",
                "eventStatus": "live"
            }
            try:
                res = requests.get(url, params=params)
                if res.status_code != 200:
                    print(f"❌ Odds API error: {res.status_code} - {res.text}")
                    continue
                data = res.json()
                total_checked += len(data)
                for game in data:
                    teams = game.get("teams", [])
                    if len(teams) != 2:
                        continue
                    home_team = game.get("home_team", "")
                    away_team = teams[0] if teams[0] != home_team else teams[1]
                    matchup = f"{away_team} vs {home_team}"
                    sport_title = game.get("sport_title", sport.upper())

                    for market in game.get("bookmakers", [])[0].get("markets", []):
                        market_key = market.get("key", "")
                        for outcome in market.get("outcomes", []):
                            pick = outcome.get("name", "")
                            odds = outcome.get("price", "")
                            if is_valid_bet(market_key, odds):
                                # Simple stake logic: flat $3 per unit, 2u
                                units = 2
                                amount = round(units * 3)
                                msg = (
                                    f"✅ **{sport_title}** | {matchup}\n"
                                    f"**Market:** {'Moneyline' if market_key == 'h2h' else market_key.capitalize()}\n"
                                    f"**Pick:** {pick}\n"
                                    f"**Odds:** {odds}\n"
                                    f"**Units:** {units}u (${amount})\n"
                                    f"**Worst ML to accept:** {ML_MAX_ODDS if market_key == 'h2h' else '-'}\n"
                                    f"**Worst Spread/Total to accept:** "
                                    f"{SPREAD_TOTAL_MAX_ODDS} exact line only\n"
                                    f"📍 Only place if Bovada odds & line match"
                                )
                                send_discord_message(msg)
                                break  # 1 bet per game max unless strong 2nd appears (handled later)
            except Exception as e:
                print(f"❌ Error fetching odds for {sport}: {e}", flush=True)

        print(f"[🔍] Checked {total_checked} live games this cycle.", flush=True)
        print(f"[…] Sleeping for {SEARCH_INTERVAL_MINUTES} minutes...", flush=True)
        time.sleep(SEARCH_INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    main_loop()
