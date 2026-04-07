"""
Evaluator — vyhodnocuje podmienky alertu na základe stiahnutých dát.
"""
import logging
from src.fetcher import get_klines
from src.indicators import price_change_pct, volume_ratio, rsi

logger = logging.getLogger(__name__)

# Koľko 1m sviečok sťahujeme (max potreba: 24h*60 + buffer)
KLINES_LIMIT = 1500


def evaluate_alert(alert: dict) -> tuple[bool, list[str]]:
    """
    Vyhodnotí všetky podmienky alertu.
    Vráti (True, [popis splnených podmienok]) ak sú všetky splnené,
    inak (False, []).
    """
    coin = alert["coin"]
    conditions = alert["conditions"]

    try:
        klines = get_klines(coin, "1m", KLINES_LIMIT)
    except Exception as e:
        logger.error(f"[{coin}] Chyba pri sťahovaní dát: {e}")
        return False, []

    results = []
    for cond in conditions:
        matched, description = _check_condition(cond, klines, coin)
        if not matched:
            return False, []
        results.append(description)

    return True, results


def _check_condition(cond: dict, klines: list[dict], coin: str) -> tuple[bool, str]:
    ctype = cond["type"]

    if ctype == "price_change":
        period = cond["period_minutes"]
        threshold = cond["threshold_pct"]
        try:
            change = price_change_pct(klines, period)
        except ValueError as e:
            logger.warning(f"[{coin}] price_change: {e}")
            return False, ""
        if threshold >= 0:
            matched = change >= threshold
            sign = "+"
        else:
            matched = change <= threshold
            sign = ""
        desc = f"Cena {sign}{change:.2f}% za {period} minút (prah: {sign}{threshold}%)"
        return matched, desc

    elif ctype == "volume_spike":
        multiplier = cond["multiplier"]
        avg_hours = cond["avg_period_hours"]
        try:
            ratio = volume_ratio(klines, avg_hours)
        except ValueError as e:
            logger.warning(f"[{coin}] volume_spike: {e}")
            return False, ""
        matched = ratio >= multiplier
        desc = f"Objem {ratio:.1f}x priemer za {avg_hours}h (prah: {multiplier}x)"
        return matched, desc

    elif ctype == "rsi":
        period = cond.get("period", 14)
        try:
            rsi_val = rsi(klines, period)
        except ValueError as e:
            logger.warning(f"[{coin}] rsi: {e}")
            return False, ""
        if "above" in cond:
            matched = rsi_val >= cond["above"]
            desc = f"RSI({period}) = {rsi_val:.1f} (prah: nad {cond['above']})"
        elif "below" in cond:
            matched = rsi_val <= cond["below"]
            desc = f"RSI({period}) = {rsi_val:.1f} (prah: pod {cond['below']})"
        else:
            return False, ""
        return matched, desc

    else:
        logger.warning(f"Neznámy typ podmienky: {ctype}")
        return False, ""
