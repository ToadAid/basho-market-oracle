"""
Market Data Analyzer Module

Wallet-free market data for analysis and paper trading.

Trust Agentic Wallet is an optional custody/execution layer. Bashō's market
analysis should still work when no wallet is installed, paired, or funded.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import os

from tools.public_market_data import PublicMarketDataClient

try:  # Optional; never required for public market data.
    from tools.trust import TrustWalletAPI
except Exception:  # pragma: no cover - optional dependency path
    TrustWalletAPI = None  # type: ignore


class MarketDataAnalyzer:
    """Market data analyzer for trading strategies.

    The default data source is wallet-free public market data. Trust Wallet can
    be enabled as an optional secondary provider with:

        TRUST_WALLET_MARKET_DATA_ENABLED=true
    """

    def __init__(self, trust_wallet: Optional[Any] = None, public_client: Optional[PublicMarketDataClient] = None):
        self.public_client = public_client or PublicMarketDataClient()
        self.trust_wallet = trust_wallet
        self.use_trust_market_data = os.getenv("TRUST_WALLET_MARKET_DATA_ENABLED", "false").lower() == "true"

        if self.use_trust_market_data and self.trust_wallet is None and TrustWalletAPI is not None:
            try:
                self.trust_wallet = TrustWalletAPI()
            except Exception:
                self.trust_wallet = None

    def get_price(self, token_address: str, chain: str = "base") -> float:
        """Get current token price in USD without requiring a wallet."""
        # Public provider first: no wallet, no keys, no custody required.
        try:
            public_data = self.public_client.get_price(token_address, chain=chain)
            price = public_data.get("price") or public_data.get("priceUsd")
            if price is not None:
                parsed = float(price)
                if parsed > 0:
                    return parsed
        except Exception:
            pass

        # Optional Trust Wallet fallback only when explicitly enabled.
        if self.use_trust_market_data and self.trust_wallet is not None:
            try:
                price_data = self.trust_wallet.get_price(token_address, chain=chain)
                if isinstance(price_data, dict):
                    return float(price_data.get("price", 0.0))
            except Exception:
                pass

        return 0.0

    def get_prices_batch(self, token_addresses: List[str], chain: str = "base") -> Dict[str, float]:
        """Get prices for multiple tokens without requiring a wallet."""
        prices = self.public_client.get_prices_batch(token_addresses, chain=chain)

        missing = [addr for addr in token_addresses if not prices.get(addr)]
        if missing and self.use_trust_market_data and self.trust_wallet is not None:
            try:
                trust_prices = self.trust_wallet.get_prices_batch(missing, chain=chain)
                if isinstance(trust_prices, dict):
                    for k, v in trust_prices.items():
                        prices[k] = float(v) if isinstance(v, (int, float, str)) else 0.0
            except Exception:
                pass

        return prices

    def analyze_token(self, token_address: str, chain: str = "base") -> Dict[str, Any]:
        """Analyze a token with wallet-free public data first."""
        try:
            token_info = self.public_client.get_token_info(token_address, chain)
            price = self.get_price(token_address, chain)

            return {
                "address": token_address,
                "chain": chain,
                "price": price,
                "info": token_info if isinstance(token_info, dict) else {},
                "market_data_source": token_info.get("source", "public") if isinstance(token_info, dict) else "public",
                "wallet_required": False,
                "analyzed_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            return {
                "address": token_address,
                "chain": chain,
                "error": str(e),
                "wallet_required": False,
                "analyzed_at": datetime.now(timezone.utc).isoformat(),
            }

    def get_volume(self, token_address: str, chain: str = "base") -> float:
        try:
            data = self.public_client.get_price(token_address, chain=chain)
            return float(data.get("volume_h24") or 0.0)
        except Exception:
            return 0.0

    def get_liquidity(self, token_address: str, chain: str = "base") -> float:
        try:
            data = self.public_client.get_price(token_address, chain=chain)
            return float(data.get("liquidity_usd") or 0.0)
        except Exception:
            return 0.0

    def calculate_volatility(self, token_address: str, days: int = 7) -> float:
        # Historical volatility needs a historical data provider. Current public
        # release returns a safe unknown value instead of pretending certainty.
        return 0.0

    def get_market_data(self, token_address: str, chain: str = "base") -> Dict[str, Any]:
        return self.analyze_token(token_address, chain)
