import requests
import time
import datetime
import os

# ENV variables
ACTION_API_KEY = os.getenv("ACTION_API_KEY")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
BANKROLL = float(os.getenv("BANKROLL", 100))

# Limits
MAX_ML_ODDS = -120
MAX_SPREAD_TOTAL_DIFF = 0.1
MAX_ODDS_DIFF = 20  # in cents

# Track previously alerted events
sent_signals = set()

def get_action_data():
    url = "https://api.actionnetwork.com/web/v1/scoreboard/live"
    headers = {"Authorization": f"Bearer {ACTION_API_KEY}"}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        return r.json().get("events", [])
    except Exception as e:
        print(f"❌ Error fetching Action data: {e}")
        return []

def format_units(odds):
    risk_unit = 1  # base unit
    if odds > 0:
        win_amt = risk_unit * odds / 100
    else:
        win_amt = risk_unit / abs(odds) * 100
    real_bet = BANKROLL * 0.01  # 1% of bankroll
    return f"{round(real_bet, 2)} units"

def send_to_discord(title, odds, market_type, line, pace_score, url):
    msg = {
        "content": f"**{title}**\n"
                   f"> {market_type} | {line} | {odds} odds\n"
                   f"> 📈 Pace: {pace_score}\n"
                   f"> 💰 Bet: {format_units(odds)} (max odds: {MAX_ML_ODDS})\n"
                   f"> 🔗 {url}\n"
                   f"_Max ML odds: -120 | Spreads/totals must match exactly | ML must be within 20¢_\n"
    }
    try:
        r = requests.post(DISCORD_WEBHOOK, json=msg, timeout=10)
        r.raise_for_status()
        print(f"✅ Sent: {title} ({market_type} @ {odds})")
    except Exception as e:
        print(f"❌ Discord error: {e}")

def should_alert(game_id, market_type):
    key = f"{game_id}_{market_type}"
    if key in sent_signals:
        return False
    sent_signals.add(key)
    return True

def scan_games():
    events = get_action_data()
    print(f"🟢 [{datetime.datetime.now().strftime('%I:%M:%S %p')}] Checking {len(events)} live games...")
    
    for game in events:
        game_id = game.get("event_id")
        league = game.get("league", {}).get("display_name", "")
        title = game.get("name", "")
        url = game.get("links", {}).get("web", {}).get("href", "")
        pace = game.get("pace_score", 0)

        for market in game.get("markets", []):
            if market.get("period") != "live":
                continue

            market_type = market.get("label", "").lower()
            odds = market.get("moneyline", {}).get("price", 0)
            line = market.get("line", "")

            if market_type == "ml" and odds >= MAX_ML_ODDS:
                if should_alert(game_id, market_type):
                    send_to_discord(title, odds, "Moneyline", line, pace, url)
            elif market_type in ["spread", "total"]:
                try:
                    if abs(float(line)) <= MAX_SPREAD_TOTAL_DIFF and abs(odds) <= abs(MAX_ML_ODDS):
                        if should_alert(game_id, market_type):
                            send_to_discord(title, odds, market_type.title(), line, pace, url)
                except:
                    continue

# LOOP: Every 5 minutes
if __name__ == "__main__":
    while True:
        print(f"🔄 [{datetime.datetime.now().strftime('%I:%M:%S %p')}] Starting scan cycle...")
        scan_games()
        print(f"⏳ Waiting 5 minutes before next cycle...\n")
        time.sleep(300)
