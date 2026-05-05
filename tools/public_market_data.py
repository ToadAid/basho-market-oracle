"""Public market-data adapters for Bashō Market Oracle.

These adapters are intentionally wallet-free. They let analysis, paper trading,
and token-risk review work without Trust Agentic Wallet, private keys, or any
custody/execution module.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import requests

DEXSCREENER_BASE_URL = "https://api.dexscreener.com/latest/dex"


def _public_market_data_enabled() -> bool:
    return os.getenv("PUBLIC_MARKET_DATA_ENABLED", "true").lower() == "true"


def _request_json(url: str, *, timeout: int = 12) -> Optional[Dict[str, Any]]:
    if not _public_market_data_enabled():
        return None

    try:
        response = requests.get(url, timeout=timeout, headers={"Accept": "application/json"})
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _normalize_chain(chain: str) -> str:
    c = (chain or "").strip().lower()
    aliases = {
        "eth": "ethereum",
        "ethereum": "ethereum",
        "base": "base",
        "sol": "solana",
        "solana": "solana",
        "bsc": "bsc",
        "bnb": "bsc",
        "polygon": "polygon",
        "matic": "polygon",
        "arbitrum": "arbitrum",
        "arb": "arbitrum",
        "optimism": "optimism",
        "op": "optimism",
        "avax": "avalanche",
        "avalanche": "avalanche",
    }
    return aliases.get(c, c or "ethereum")


def _best_pair(pairs: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not pairs:
        return None

    def score(pair: Dict[str, Any]) -> float:
        liquidity = pair.get("liquidity") or {}
        volume = pair.get("volume") or {}
        try:
            liq = float(liquidity.get("usd") or 0)
        except Exception:
            liq = 0.0
        try:
            vol = float(volume.get("h24") or 0)
        except Exception:
            vol = 0.0
        return liq + (vol * 0.25)

    return sorted(pairs, key=score, reverse=True)[0]


def fetch_token_pairs(token_address: str, chain: str = "ethereum") -> List[Dict[str, Any]]:
    """Fetch DEX pairs for a token address from DexScreener."""
    chain_id = _normalize_chain(chain)
    token = (token_address or "").strip()
    if not token:
        return []

    data = _request_json(f"{DEXSCREENER_BASE_URL}/tokens/{token}")
    pairs = data.get("pairs") if isinstance(data, dict) else None
    if not isinstance(pairs, list):
        return []

    same_chain = [p for p in pairs if str(p.get("chainId", "")).lower() == chain_id]
    return same_chain or pairs


def search_tokens(query: str, chain: str = "ethereum", limit: int = 10) -> List[Dict[str, Any]]:
    """Search public DEX token/pair data without wallet dependencies."""
    q = (query or "").strip()
    if not q:
        return []

    chain_id = _normalize_chain(chain)
    data = _request_json(f"{DEXSCREENER_BASE_URL}/search?q={q}")
    pairs = data.get("pairs") if isinstance(data, dict) else None
    if not isinstance(pairs, list):
        return []

    same_chain = [p for p in pairs if str(p.get("chainId", "")).lower() == chain_id]
    ranked = same_chain or pairs
    ranked = sorted(ranked, key=lambda p: float(((p.get("liquidity") or {}).get("usd") or 0)), reverse=True)
    return ranked[:limit]


def get_token_price(token: str, chain: str = "ethereum") -> Optional[Dict[str, Any]]:
    """Return best-effort public price data for a token address or symbol.

    Address input uses DexScreener token pairs. Symbol/name input uses the public
    search endpoint and selects the highest-liquidity matching pair.
    """
    token = (token or "").strip()
    if not token:
        return None

    is_evm_address = token.lower().startswith("0x") and len(token) == 42
    pairs = fetch_token_pairs(token, chain) if is_evm_address else search_tokens(token, chain, limit=10)
    pair = _best_pair(pairs)
    if not pair:
        return None

    base_token = pair.get("baseToken") or {}
    quote_token = pair.get("quoteToken") or {}
    return {
        "source": "dexscreener",
        "chain": pair.get("chainId") or _normalize_chain(chain),
        "dex": pair.get("dexId"),
        "pair_address": pair.get("pairAddress"),
        "url": pair.get("url"),
        "token_address": base_token.get("address"),
        "symbol": base_token.get("symbol"),
        "name": base_token.get("name"),
        "quote_symbol": quote_token.get("symbol"),
        "price": float(pair.get("priceUsd") or 0.0),
        "priceUsd": pair.get("priceUsd"),
        "liquidity_usd": (pair.get("liquidity") or {}).get("usd"),
        "volume_h24": (pair.get("volume") or {}).get("h24"),
        "price_change_h24": (pair.get("priceChange") or {}).get("h24"),
        "fdv": pair.get("fdv"),
        "market_cap": pair.get("marketCap"),
        "pair_created_at": pair.get("pairCreatedAt"),
        "raw_pair": pair,
    }


class PublicMarketDataClient:
    """Wallet-free market-data client used by public-safe analysis tools."""

    def get_price(self, token: str, chain: str = "ethereum") -> Dict[str, Any]:
        result = get_token_price(token, chain=chain)
        return result or {"source": "dexscreener", "chain": chain, "token": token, "price": 0.0, "error": "not_found"}

    def search_token(self, query: str, chain: str = "ethereum", limit: int = 10) -> List[Dict[str, Any]]:
        return search_tokens(query, chain=chain, limit=limit)

    def get_token_info(self, token: str, chain: str = "ethereum") -> Dict[str, Any]:
        return self.get_price(token, chain=chain)

    def get_prices_batch(self, tokens: List[str], chain: str = "ethereum") -> Dict[str, float]:
        prices: Dict[str, float] = {}
        for token in tokens:
            data = self.get_price(token, chain=chain)
            try:
                prices[token] = float(data.get("price") or data.get("priceUsd") or 0.0)
            except Exception:
                prices[token] = 0.0
        return prices


def public_price_json(token: str, chain: str = "ethereum") -> str:
    """Convenience JSON string for tool fallback output."""
    data = get_token_price(token, chain=chain)
    if not data:
        return json.dumps({"source": "dexscreener", "chain": chain, "token": token, "error": "not_found"}, indent=2)
    return json.dumps(data, indent=2)
