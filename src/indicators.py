"""
Indicators — výpočet technických indikátorov z OHLCV dát.
"""


def price_change_pct(klines: list[dict], period_minutes: int) -> float:
    """
    Percentuálna zmena ceny za posledných `period_minutes` minút.
    Predpokladá 1m sviečky.
    Kladné = rast, záporné = pokles.
    """
    if len(klines) < period_minutes:
        raise ValueError(f"Nedostatok dát: potrebujem {period_minutes} sviečok, mám {len(klines)}")
    price_now = klines[-1]["close"]
    price_then = klines[-period_minutes]["close"]
    return (price_now - price_then) / price_then * 100


def volume_ratio(klines: list[dict], avg_period_hours: int) -> float:
    """
    Pomer aktuálneho objemu k priemeru za posledných `avg_period_hours` hodín.
    Výsledok 4.0 = aktuálny objem je 4x väčší ako priemer.
    Predpokladá 1m sviečky.
    """
    avg_candles = avg_period_hours * 60
    if len(klines) < avg_candles + 1:
        raise ValueError(f"Nedostatok dát pre volume ratio")
    current_volume = klines[-1]["volume"]
    historical = klines[-(avg_candles + 1):-1]
    avg_volume = sum(c["volume"] for c in historical) / len(historical)
    if avg_volume == 0:
        return 0.0
    return current_volume / avg_volume


def rsi(klines: list[dict], period: int = 14) -> float:
    """
    Relative Strength Index (RSI) podľa Wilderovej metódy.
    """
    closes = [c["close"] for c in klines]
    if len(closes) < period + 1:
        raise ValueError(f"Nedostatok dát pre RSI: potrebujem aspoň {period + 1} sviečok")

    deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gains = [d if d > 0 else 0.0 for d in deltas]
    losses = [-d if d < 0 else 0.0 for d in deltas]

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    for i in range(period, len(deltas)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))
