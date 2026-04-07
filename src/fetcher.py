"""
Fetcher — sťahuje OHLCV dáta z Binance public API (bez API kľúča).
"""
import requests
from datetime import datetime


BINANCE_BASE = "https://api.binance.com/api/v3"


def get_klines(symbol: str, interval: str, limit: int) -> list[dict]:
    """Vráti posledných `limit` sviečok pre daný symbol a interval."""
    url = f"{BINANCE_BASE}/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    raw = resp.json()
    return [
        {
            "open_time": r[0],
            "open": float(r[1]),
            "high": float(r[2]),
            "low": float(r[3]),
            "close": float(r[4]),
            "volume": float(r[5]),
        }
        for r in raw
    ]


def get_current_price(symbol: str) -> float:
    url = f"{BINANCE_BASE}/ticker/price"
    resp = requests.get(url, params={"symbol": symbol}, timeout=10)
    resp.raise_for_status()
    return float(resp.json()["price"])
