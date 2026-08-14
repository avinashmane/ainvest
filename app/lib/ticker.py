"""
lib/ticker.py
-------------
TTL-cached wrapper around a single yfinance ticker.

Public API
----------
Ticker(symbol)
    .quote()  -> dict[str, Any]   – live quote fields (60 s TTL cache)
    .to_yf_symbol(raw) -> str     – convert a bare ticker to its yfinance form

OptionTicker(raw_symbol)
    .quote()  -> dict[str, Any]
        Accepts two input formats (leading ``"-"`` is stripped first):

        1. OCC symbol  e.g. ``"KMB260717C113"`` or ``"KMB260717C00113000"``
           Format: <ticker><YYMMDD><C|P><strike>
           Strike may be:
             • 8-digit zero-padded integer ×1000 (full OCC): 00113000 → 113.0
             • Plain integer dollars (short form): 113 → 113.0
           Fetches the matching contract row from the options chain for that
           expiry date and returns its live fields plus underlying context.

        2. Underlying-only  e.g. ``"-NIFTY50"`` → ``"NIFTY50"``
           Falls back to nearest-expiry ATM chain summary (original behaviour).

        Fields returned in both cases:
            quoteType        "OPTION"
            underlying       underlying ticker
            underlyingPrice  last price of the underlying
            currency         from underlying quote
            expiry           expiry date string (YYYY-MM-DD)
            optionType       "call" | "put"  (OCC path) or None
            strike           strike price float (OCC path) or None
            contract         matched contract row dict (OCC path) or None
            lastPrice        contract lastPrice (OCC) or ATM mid (underlying)
            expiryDates      all available expiry dates
            calls / puts     full chain for the matched expiry

Module-level helper
-------------------
fetch_quotes(symbols) -> dict[str, dict]
    Fetch quotes for a list of symbols, tolerating per-symbol failures.
"""

from __future__ import annotations

import math
import re
from datetime import date
from typing import Any
import yaml
import yfinance as yf
from cachetools import TTLCache, cached

# OCC option symbol: 1–6 alpha chars, YYMMDD, C/P, 1–8 digit strike
# Handles both full form (00113000) and short form (113)
_OCC_RE = re.compile(r'^([A-Z]{1,6})(\d{2})(\d{2})(\d{2})([CP])(\d{1,8})$')

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


# ── OptionTicker ──────────────────────────────────────────────────────────────

_option_cache: TTLCache = TTLCache(maxsize=256, ttl=300)  # 5-minute TTL


class OptionTicker:
    """Parse and fetch a specific option contract or a nearest-ATM chain.

    Accepts raw symbols with an optional leading ``"-"``.

    OCC path (e.g. ``"KMB260717C113"`` or ``"KMB260717C00113000"``)
    ----------------------------------------------------------------
    Parses underlying / expiry / side / strike from the symbol, fetches
    the option chain for that expiry date, and returns the matching
    contract row together with underlying context.

    Underlying-only path (e.g. ``"NIFTY50"``, ``"-NIFTY50"``)
    -----------------------------------------------------------
    Falls back to nearest-expiry ATM chain summary.
    """

    def __init__(self, raw_symbol: str) -> None:
        # Strip the leading "-" that fetch_quotes adds
        clean = raw_symbol.strip().lstrip("-").strip().upper()
        self._parsed = _OCC_RE.match(clean)
        self._raw = clean

    # ------------------------------------------------------------------
    # OCC symbol parser
    # ------------------------------------------------------------------

    @staticmethod
    def parse_occ(symbol: str) -> dict[str, Any] | None:
        """Parse an OCC option symbol into its components.

        Parameters
        ----------
        symbol:
            e.g. ``"KMB260717C113"`` or ``"KMB260717C00113000"``

        Returns
        -------
        dict with keys ``underlying``, ``expiry`` (YYYY-MM-DD), ``option_type``
        (``"call"`` / ``"put"``), ``strike`` (float) — or ``None`` if the
        symbol does not match the OCC pattern.
        """
        m = _OCC_RE.match(symbol.strip().upper())
        if not m:
            return None
        tkr, yy, mm, dd, cp, strike_raw = m.groups()
        # Full OCC: 8 digits, strike in units of 1/1000. Short form: plain dollars.
        strike = int(strike_raw) / (1000.0 if len(strike_raw) == 8 else 1.0)
        return {
            "underlying":  tkr,
            "expiry":      f"20{yy}-{mm}-{dd}",
            "option_type": "call" if cp == "C" else "put",
            "strike":      strike,
        }

    # ------------------------------------------------------------------
    # Internal cached fetches
    # ------------------------------------------------------------------

    @staticmethod
    def _df_to_records(df: Any) -> list[dict[str, Any]]:
        df = df.copy()
        if "lastTradeDate" in df.columns:
            df["lastTradeDate"] = df["lastTradeDate"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        return [
            {k: (None if isinstance(v, float) and math.isnan(v) else v)
             for k, v in row.items()}
            for row in df.to_dict(orient="records")
        ]

    @staticmethod
    def _underlying_info(underlying: str) -> tuple[float, str | None]:
        """Return (lastPrice, currency) for the underlying ticker."""
        info = yf.Ticker(underlying).info
        price: float = (
            info.get("regularMarketPrice")
            or info.get("currentPrice")
            or info.get("previousClose")
            or 0.0
        )
        return price, info.get("currency")

    @staticmethod
    @cached(cache=_option_cache)
    def _fetch_occ(underlying: str, expiry: str, option_type: str, strike: float) -> dict[str, Any]:
        """Fetch a specific OCC contract row plus underlying and chain context."""
        yft = yf.Ticker(underlying)
        underlying_price, currency = OptionTicker._underlying_info(underlying)
        expiry_dates: list[str] = list(yft.options or [])

        # Find the closest available expiry to the requested date
        # (yfinance expiry strings are "YYYY-MM-DD")
        target = date.fromisoformat(expiry)
        matched_expiry = min(
            expiry_dates,
            key=lambda d: abs((date.fromisoformat(d) - target).days),
        ) if expiry_dates else expiry

        chain = yft.option_chain(matched_expiry)
        # print(underlying, expiry, option_type, strike)
        calls_records = OptionTicker._df_to_records(chain.calls)
        puts_records  = OptionTicker._df_to_records(chain.puts)

        # Find the exact contract by side + strike
        side_records = calls_records if option_type == "call" else puts_records
        contract = next(
            (r for r in side_records if r.get("strike") == strike),
            # Fallback: nearest strike if exact match not found
            min(side_records, key=lambda r: abs((r.get("strike") or 0) - strike))
            if side_records else None,
        )

        last_price: float = (contract or {}).get("lastPrice") or 0.0

        return {
            "quoteType":        "OPTION",
            "underlying":       underlying,
            "underlyingPrice":  underlying_price,
            "currency":         currency,
            "expiry":           matched_expiry,
            "expiryDates":      expiry_dates,
            "optionType":       option_type,
            "strike":           strike,
            "contract":         contract,
            "calls":            calls_records,
            "puts":             puts_records,
            "lastPrice":        last_price,
        }

    @staticmethod
    @cached(cache=_option_cache)
    def _fetch_underlying(underlying: str) -> dict[str, Any]:
        """Nearest-expiry ATM chain summary (no OCC symbol available)."""
        yft = yf.Ticker(underlying)
        underlying_price, currency = OptionTicker._underlying_info(underlying)
        expiry_dates: list[str] = list(yft.options or [])

        if not expiry_dates:
            return {
                "quoteType":       "OPTION",
                "underlying":      underlying,
                "underlyingPrice": underlying_price,
                "currency":        currency,
                "expiry":          None,
                "expiryDates":     [],
                "optionType":      None,
                "strike":          None,
                "contract":        None,
                "calls":           [],
                "puts":            [],
                "lastPrice":       0.0,
            }

        chain = yft.option_chain(expiry_dates[0])
        calls_records = OptionTicker._df_to_records(chain.calls)
        puts_records  = OptionTicker._df_to_records(chain.puts)

        def _atm(records: list[dict[str, Any]]) -> dict[str, Any] | None:
            if not records or underlying_price == 0:
                return None
            return min(records, key=lambda r: abs((r.get("strike") or 0) - underlying_price))

        atm_call = _atm(calls_records)
        atm_put  = _atm(puts_records)
        call_last = (atm_call or {}).get("lastPrice") or 0.0
        put_last  = (atm_put  or {}).get("lastPrice") or 0.0
        last_price = (call_last + put_last) / 2 if (call_last or put_last) else 0.0

        return {
            "quoteType":       "OPTION",
            "underlying":      underlying,
            "underlyingPrice": underlying_price,
            "currency":        currency,
            "expiry":          expiry_dates[0],
            "expiryDates":     expiry_dates,
            "optionType":      None,
            "strike":          None,
            "contract":        atm_call,   # ATM call as representative contract
            "calls":           calls_records,
            "puts":            puts_records,
            "lastPrice":       last_price,
        }

    # ------------------------------------------------------------------

    def quote(self) -> dict[str, Any]:
        """Return the cached option quote dict."""
        if self._parsed:
            parsed = self.parse_occ(self._raw)
            assert parsed is not None
            return self._fetch_occ(
                parsed["underlying"],
                parsed["expiry"],
                parsed["option_type"],
                parsed["strike"],
            )
        # Underlying-only fallback
        return self._fetch_underlying(self._raw)


def fetch_quotes(symbols: list[str]) -> dict[str, dict]:
    """Fetch quotes for *symbols*, tolerating per-symbol failures.

    Each symbol is first resolved via :meth:`Ticker.to_yf_symbol` so bare
    Indian tickers (e.g. ``"INFY"``) are automatically mapped to their
    yfinance form (``"INFY.NS"``).  The result dict is keyed by the *original*
    symbol so callers don't need to know the resolved form.

    Special cases (no yfinance call made):
    - Symbol contains ``"**"``  → ``quoteType`` is forced to ``"CASH"``.
    - Symbol starts with ``"-"`` → ``quoteType`` is forced to ``"OPTION"``.
    """
    result: dict[str, dict] = {}
    for sym in symbols:
        try:
            if "**" in sym:
                result[sym] = {"ticker": sym, "quoteType": "CASH", "lastPrice": 0.0}
                continue
            if sym.strip().startswith("-"):
                result[sym] = OptionTicker(sym).quote()
                continue
            yf_sym = Ticker.to_yf_symbol(sym)
            result[sym] = Ticker(yf_sym).quote()
        except Exception:
            result[sym] = {}
    return result
