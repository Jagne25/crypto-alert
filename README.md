# Smart Alert Engine

Telegram notification tool for crypto traders. Monitors cryptocurrencies and sends you a message only when **multiple conditions trigger at the same time**.

**Example:**
- BTC jumps +3% in 15 minutes
- AND volume is 4x higher than normal
- AND RSI is above 70

All three at once → you get a message. Only one or two → silence.

## How it works

```
main.py runs
    ↓
Every 60 seconds checks config/alerts.yaml
    ↓
For each alert (BTC, ETH, SOL...)
    ↓
Downloads data from Binance (no API key needed)
    ↓
Calculates indicators (RSI, price change, volume)
    ↓
Are ALL conditions met?
    ↓
YES → sends Telegram message
NO  → silent, waits for next cycle
```

## Setup

**1. Clone the repository**
```bash
git clone https://github.com/Jagne25/crypto-alert.git
cd crypto-alert
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Create a `.env` file with your Telegram credentials**
```
BOT_TOKEN=your_telegram_bot_token
CHAT_ID=your_telegram_chat_id
```

> Get your bot token from [@BotFather](https://t.me/BotFather) and chat ID from [@userinfobot](https://t.me/userinfobot) — both are free.

**4. Configure your alerts in `config/alerts.yaml`**

```yaml
alerts:
  - name: "BTC Pump"
    coin: "BTCUSDT"
    conditions:
      - type: price_change
        period_minutes: 15
        threshold_pct: 3.0
      - type: volume_spike
        multiplier: 4.0
        avg_period_hours: 24
      - type: rsi
        period: 14
        above: 70
```

**5. Run**
```bash
python main.py
```

## Supported condition types

| Type | Description | Parameters |
|------|-------------|------------|
| `price_change` | % price change over N minutes | `period_minutes`, `threshold_pct` |
| `volume_spike` | Current volume vs average | `multiplier`, `avg_period_hours` |
| `rsi` | Relative Strength Index | `period`, `above` or `below` |

## Project structure

```
crypto_alert/
├── config/
│   └── alerts.yaml    # your alert rules
├── src/
│   ├── fetcher.py     # downloads data from Binance
│   ├── indicators.py  # calculates RSI, price change, volume
│   ├── evaluator.py   # AND logic — all conditions must pass
│   └── notifier.py    # sends Telegram messages
├── main.py            # main loop
└── requirements.txt
```
