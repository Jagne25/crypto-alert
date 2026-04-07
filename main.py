"""
Smart Alert Engine — hlavný vstupný bod.
Spustiť: python main.py
"""
import time
import logging
import yaml
from pathlib import Path
from src.evaluator import evaluate_alert
from src.notifier import send_telegram, format_alert_message

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/engine.log"),
    ],
)
logger = logging.getLogger(__name__)


def load_config(path: str = "config/alerts.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def run_once(config: dict, already_fired: set) -> set:
    """Prejde všetky alerty a odošle notifikácie pre splnené podmienky."""
    tg = config["telegram"]
    for alert in config["alerts"]:
        name = alert["name"]
        coin = alert["coin"]
        logger.info(f"Kontrolujem: [{name}] {coin}")

        triggered, conditions_met = evaluate_alert(alert)

        if triggered:
            if name not in already_fired:
                msg = format_alert_message(name, coin, conditions_met)
                sent = send_telegram(tg["bot_token"], tg["chat_id"], msg)
                if sent:
                    logger.info(f"✅ Alert odoslaný: {name}")
                    already_fired.add(name)
            else:
                logger.info(f"⏭️  Alert už bol odoslaný v tomto cykle: {name}")
        else:
            # Reset — alert môže znovu vystreliť keď podmienky prestanú platiť a znovu začnú
            already_fired.discard(name)

    return already_fired


def main():
    config = load_config()
    interval = config.get("check_interval", 60)
    already_fired: set = set()

    logger.info(f"Smart Alert Engine spustený. Interval: {interval}s")
    logger.info(f"Sledujem {len(config['alerts'])} alertov")

    while True:
        try:
            already_fired = run_once(config, already_fired)
        except Exception as e:
            logger.error(f"Neočakávaná chyba: {e}", exc_info=True)
        time.sleep(interval)


if __name__ == "__main__":
    main()
