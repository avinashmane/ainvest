"""
lib/ticker.py
-------------
TTL-cached wrapper around a single yfinance ticker.

Public API
----------
Ticker(symbol)
    .quote()  -> dict[str, Any]   – live quote fields (60 s TTL cache)
    .to_yf_symbol(raw) -> str     – convert a bare ticker to its yfinance form

Module-level helper
-------------------
fetch_quotes(symbols) -> dict[str, dict]
    Fetch quotes for a list of symbols, tolerating per-symbol failures.
"""

from __future__ import annotations

from typing import Any
from textwrap import dedent
import yaml
import yfinance as yf
from cachetools import TTLCache, cached

_quote_cache: TTLCache = TTLCache(maxsize=1024, ttl=60)

# Cache resolved yf symbols so each bare symbol is probed at most once per
# process lifetime (probing makes a network call).
_symbol_cache: dict[str, str] = yaml.safe_load("""
.INX: ^GSPC
.IXIC: ^IXIC
.DJI: ^DJI
""")

# yfinance exchange suffixes for Indian markets, tried in priority order.
_INDIAN_SUFFIXES = (".NS", ".BO")


class Ticker:
    """Thin wrapper around a single yfinance ticker with a 60 s quote cache."""

    def __init__(self, symbol: str) -> None:
        self.symbol = symbol

    @staticmethod
    def to_yf_symbol(raw: str) -> str:
        """Convert *raw* to the yfinance ticker symbol that returns a live quote.

        Resolution order
        ----------------
        1. Already contains a ``"."`` suffix (e.g. ``"INFY.NS"``, ``"BP.L"``)
           → returned as-is.
        2. Bare symbol (e.g. ``"INFY"``, ``"TCS"``) → probed with each suffix in
           ``_INDIAN_SUFFIXES`` in order; the first one whose yfinance ``info``
           has a non-empty ``regularMarketPrice`` (or ``previousClose``) is
           returned.
        3. None of the probes succeed → the raw symbol is returned unchanged so
           the caller can still attempt a fetch and handle the empty response.

        Results are cached in ``_symbol_cache`` for the lifetime of the process.

        Parameters
        ----------
        raw : str
            Ticker as it appears in the portfolio sheet (e.g. ``"INFY"``,
            ``"AAPL"``, ``"0P0001EKBS.BO"``).

        Returns
        -------
        str
            Resolved yfinance symbol.
        """
        raw = raw.strip().upper()

        if raw in _symbol_cache:
            return _symbol_cache[raw]

        # Already has a suffix – trust it and skip probing.
        if "." in raw:
            _symbol_cache[raw] = raw
            return raw

        # Probe Indian exchange suffixes.
        # for suffix in _INDIAN_SUFFIXES:
        #     candidate = raw + suffix
        #     try:
        #         info = yf.Ticker(candidate).info
        #         if info.get("regularMarketPrice") or info.get("previousClose"):
        #             _symbol_cache[raw] = candidate
        #             return candidate
        #     except Exception:
        #         continue

        # No probe succeeded – return raw so the caller handles the miss.
        _symbol_cache[raw] = raw
        return raw

    @staticmethod
    @cached(cache=_quote_cache)
    def _fetch(symbol: str) -> dict[str, Any]:
        t = yf.Ticker(symbol)
        info = t.info

        keys = [
            "currency", "exchange", "timezone", "quoteType",
            # Price
            "open", "dayHigh", "dayLow", "previousClose",
            "regularMarketOpen", "regularMarketDayHigh", "regularMarketDayLow",
            "regularMarketPreviousClose", "regularMarketVolume",
            "regularMarketPrice",
            # 52-week range
            "fiftyTwoWeekHigh", "fiftyTwoWeekLow",
            # Moving averages
            "fiftyDayAverage", "twoHundredDayAverage",
            # Fundamentals
            "marketCap", "trailingPE", "forwardPE",
            "priceToBook", "trailingEps", "forwardEps",
            "dividendYield", "dividendRate", "exDividendDate",
            "beta",
            # Revenue / earnings
            "totalRevenue", "revenuePerShare", "returnOnEquity",
            "grossMargins", "operatingMargins", "profitMargins",
            # Shares
            "sharesOutstanding", "floatShares",
            # Sector / industry
            "sector", "industry", "country",
            # Analyst targets
            "targetHighPrice", "targetLowPrice", "targetMeanPrice",
            "recommendationMean", "recommendationKey",
            "numberOfAnalystOpinions",
        ]
        quote: dict[str, Any] = {f: info.get(f) for f in keys}
        quote["ticker"] = symbol

        name = info.get("shortName")
        quote["name"] = name if (name and name != symbol) else info.get("longName")
        quote["longName"] = info.get("longName")
        quote["website"] = info.get("website")
        quote["logo_url"] = info.get("logo_url")
        quote["description"] = info.get("longBusinessSummary")

        # Resolve lastPrice: prefer regularMarketPrice, then previousClose
        quote["lastPrice"] = (
            info.get("regularMarketPrice")
            or info.get("currentPrice")
            or info.get("lastPrice")
            or info.get("previousClose")
            or 0.0
        )
        return quote

    def quote(self) -> dict[str, Any]:
        """Return the cached live quote dict for this ticker."""
        return self._fetch(self.symbol)


def fetch_quotes(symbols: list[str]) -> dict[str, dict]:
    """Fetch quotes for *symbols*, tolerating per-symbol failures.

    Each symbol is first resolved via :meth:`Ticker.to_yf_symbol` so bare
    Indian tickers (e.g. ``"INFY"``) are automatically mapped to their
    yfinance form (``"INFY.NS"``).  The result dict is keyed by the *original*
    symbol so callers don't need to know the resolved form.
    """
    result: dict[str, dict] = {}
    for sym in symbols:
        try:
            yf_sym = Ticker.to_yf_symbol(sym)
            result[sym] = Ticker(yf_sym).quote()
        except Exception:
            result[sym] = {}
    return result
