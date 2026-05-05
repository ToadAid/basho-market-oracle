# Bashō Market Oracle

Bashō Market Oracle does **not** print money. It reflects market risk, separates signal from noise, supports paper trading, and keeps live execution behind explicit human/operator gates.

This repository is a public-safe release of a market-intelligence agent. It is designed for:

- token and market risk analysis
- narrative separation and community warnings
- technical and macro signal review
- paper trading and strategy testing
- human-authorized signal proposals
- learning from prior paper/live outcomes through a Wisdom Ledger

It is **not** financial advice and it is **not** an autonomous profit machine.

## Safety posture

Default public-release behavior:

```text
LIVE_WALLET_TOOLS_ENABLED=false
LIVE_TRADING_ENABLED=false
AUTONOMOUS_SCANS_ENABLED=false
BASH_TOOLS_ENABLED=false
FILE_WRITE_TOOLS_ENABLED=false
```

Live wallet tools, shell tools, file-writing tools, and scheduled autonomous scans are disabled unless a local operator deliberately enables them in `.env`.

Core doctrine:

```text
No tool prints money.
No signal removes risk.
No execution without authorization.
Paper trading first.
The ledger remembers.
```


## Wallet-free market data

Bashō does **not** require Trust Agentic Wallet for market analysis. The public-safe release uses wallet-free market-data adapters first, currently including public DEX data paths such as DexScreener-style token/pair lookups.

```text
No wallet required to see the weather.
Wallet required only to sail.
```

Trust Agentic Wallet / TWAK is optional and belongs to the custody or execution layer. Use it only when you intentionally enable wallet-aware features locally.

Relevant defaults:

```text
PUBLIC_MARKET_DATA_ENABLED=true
TRUST_WALLET_MARKET_DATA_ENABLED=false
LIVE_WALLET_TOOLS_ENABLED=false
LIVE_TRADING_ENABLED=false
```

## Optional: Trust Agentic Wallet / TWAK

Bashō Market Oracle does **not** require Trust Agentic Wallet / TWAK for market analysis, token risk review, narrative separation, paper trading, or normal proposal-mode usage.

Trust Agentic Wallet belongs to the custody/execution layer. Install and pair it only if you intentionally want to experiment with live wallet-aware actions such as transfers or swaps.

By default, wallet execution remains disabled:

```text
LIVE_WALLET_TOOLS_ENABLED=false
LIVE_TRADING_ENABLED=false
TRUST_WALLET_MARKET_DATA_ENABLED=false
```

### Install / pair checklist

Follow the official Trust Agentic Wallet / TWAK installation instructions for your operating system. After installation, make sure the wallet CLI is on your `PATH`. In Tommy's local setup, the CLI is expected to be available as:

```bash
caw status
```

A healthy paired wallet should return a status response showing the wallet is paired/active. If `caw` is not found, add the installed wallet CLI directory to your shell path, for example:

```bash
export PATH="$HOME/.cobo-agentic-wallet/bin:$PATH"
```

To make that persistent for Bash users:

```bash
echo 'export PATH="$HOME/.cobo-agentic-wallet/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Then verify again:

```bash
caw status
```

### Enabling wallet-aware tools

Only after the wallet is installed, paired, healthy, and connected to a test wallet, you may enable wallet-aware tools locally in `.env`:

```text
LIVE_WALLET_TOOLS_ENABLED=true
LIVE_TRADING_ENABLED=true
```

Use a fresh test wallet first. Do **not** enable live wallet tools on a wallet holding funds you cannot afford to lose.

Important: wallet installation is optional. Market analysis should still work without it.

```text
No wallet required to see the weather.
Wallet required only to sail.
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python agent.py login
python agent.py chat
```

`python agent.py login` is the required first-run setup for choosing and authenticating an LLM provider. Use it before starting the CLI chat or Telegram bot.

Optional dashboard:

```bash
python backend/app.py
```

Set a real `SECRET_KEY` and non-default `DASHBOARD_PASSWORD` before exposing the dashboard beyond localhost.

## Main entrypoints

```bash
python agent.py login     # first-run LLM provider authentication/setup
python agent.py chat      # local CLI chat
python agent.py bot       # Telegram bot, requires TELEGRAM_BOT_TOKEN
python agent.py tui       # optional terminal UI
python backend/app.py     # dashboard/backend
```

## Recommended first release scope

Use this public repo for analysis and paper trading:

- wallet-free market data tools
- technical indicators
- token/security scans
- paper trading
- proposal review
- Wisdom Ledger reflection

Keep private/operator-only systems separate:

- funded wallet execution
- Trust Agentic Wallet / TWAK execution modules unless deliberately enabled
- token transfers
- autonomous background scans that propose trades
- private workspaces and user ledgers
- private lore or operational notes

## Environment

See `.env.example` for placeholders. Never commit `.env`, wallet passwords, API keys, database files, logs, or local workspace files.

## Warning

Crypto assets are volatile. Contract safety does not mean price-entry safety. A token being sellable does not mean it is a good trade. Bashō is a mirror for risk, not a promise of profit.
