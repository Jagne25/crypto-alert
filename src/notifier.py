"""
Notifier — odosiela správy cez Telegram Bot API.
"""
import requests
import logging

logger = logging.getLogger(__name__)

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


def send_telegram(bot_token: str, chat_id: str, message: str) -> bool:
    url = TELEGRAM_API.format(token=bot_token)
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Telegram chyba: {e}")
        return False


def format_alert_message(alert_name: str, coin: str, conditions_met: list[str]) -> str:
    lines = [
        f"🚨 *{alert_name}*",
        f"Coin: `{coin}`",
        "",
        "*Splnené podmienky:*",
    ]
    for c in conditions_met:
        lines.append(f"✅ {c}")
    return "\n".join(lines)
