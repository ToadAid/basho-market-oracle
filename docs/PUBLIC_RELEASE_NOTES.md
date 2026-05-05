# Public Release Notes — Bashō Market Oracle

This public package was cleaned for open-source release.

## Removed from public package

- `.claude/` local settings
- private `workspace/` content and ledgers
- local databases, logs, release artifacts, caches, and virtual environments

## Safety gates added

- `LIVE_WALLET_TOOLS_ENABLED=false` by default
- `LIVE_TRADING_ENABLED=false` by default
- `AUTONOMOUS_SCANS_ENABLED=false` by default
- `BASH_TOOLS_ENABLED=false` by default
- `FILE_WRITE_TOOLS_ENABLED=false` by default

## Public positioning

This repo is market risk intelligence and paper trading first. Live execution must remain local, explicit, and human-authorized.

## Wallet-free market data patch

Bashō market analysis now treats Trust Agentic Wallet as optional. Market-data lookups use wallet-free public providers first, so users can scan tokens, review risk, and paper trade without installing or pairing a wallet. Trust/TWAK can still be enabled explicitly as a secondary provider or execution/custody layer.

Default posture:

```text
PUBLIC_MARKET_DATA_ENABLED=true
TRUST_WALLET_MARKET_DATA_ENABLED=false
LIVE_WALLET_TOOLS_ENABLED=false
LIVE_TRADING_ENABLED=false
```

Doctrine: no wallet required to see the weather; wallet required only to sail.
