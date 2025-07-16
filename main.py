
import os
import requests

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
BANKROLL = float(os.getenv("BANKROLL", 100))

def send_alert(message):
    requests.post(DISCORD_WEBHOOK_URL, json={"content": message})

def main():
    send_alert(f"🧠 MVP Betting Bot is Live | Bankroll: ${BANKROLL}")

if __name__ == "__main__":
    main()
