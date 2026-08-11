"""
server/routers/quotes.py
------------------------
yfinance endpoints — live quotes, ticker search, price history,
options chains, upgrades/downgrades, institutional holders,
analyst targets, and news.

Single-ticker routes
--------------------
GET /api/quotes/{ticker}                    Live quote fields
GET /api/quotes/{ticker}/info               Full yfinance .info dict
GET /api/quotes/{ticker}/history            OHLCV price history
GET /api/quotes/{ticker}/options            Available option expiry dates
GET /api/quotes/{ticker}/options/{yyyymmdd} Calls + puts for a specific expiry
GET /api/quotes/{ticker}/upgrades_downgrades
GET /api/quotes/{ticker}/institutional_holders
GET /api/quotes/{ticker}/analysts           Analyst price targets

Multi-ticker routes  (comma-separated tickers, e.g. AAPL,MSFT)
--------------------
GET /api/quotes/{tickers}/history           Multi-ticker price history
GET /api/quotes/{tickers}/news              Latest news items

POST /api/quotes/search
    Body: { "query": "Reliance", "exchanges": ["BSE", "NSI"] }
"""

from __future__ import annotations

from datetime import date
from typing import Any

import yfinance as yf
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from lib.ticker import Ticker

router = APIRouter(prefix="/api/quotes", tags=["quotes"])

# ── TTL-cached quote fetch (60 s) ─────────────────────────────────────────────
# Delegates to lib.ticker.Ticker which owns the cache.


def _fetch_quote(ticker: str) -> dict[str, Any]:
    """Thin wrapper kept for backwards compatibility (tests mock this name)."""
    return Ticker(ticker).quote()


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/{ticker}", summary="Live quote for a single ticker")
def get_quote(ticker: str) -> dict[str, Any]:
    try:
        return _fetch_quote(ticker)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/{ticker}/info", summary="Full yfinance .info dict for a single ticker")
async def get_info(ticker: str) -> dict[str, Any]:
    try:
        return yf.Ticker(ticker).info
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


# ── History ───────────────────────────────────────────────────────────────────

@router.get("/{ticker}/history", summary="OHLCV price history (single ticker)")
def get_history(
    ticker: str,
    period: str = "1y",
    interval: str = "1d",
    start: date | None = None,
    end: date | None = None,
) -> list[dict[str, Any]]:
    """
    Returns OHLCV records for *ticker*.
    Query params mirror yfinance: period, interval, start (YYYY-MM-DD), end (YYYY-MM-DD).
    """
    try:
        t = yf.Ticker(ticker)
        df = t.history(period=period, interval=interval, start=start, end=end, repair=True)
        df = df.reset_index()
        df["Date"] = df["Date"].astype(str)
        return df[["Date", "Open", "High", "Low", "Close", "Volume"]].to_dict(orient="records")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/{tickers}/history/multi", summary="Price history for multiple comma-separated tickers")
async def get_history_multi(
    tickers: str,
    price_type: str = "Close",
    period: str = "1mo",
    interval: str = "1d",
    start: date | None = None,
    end: date | None = None,
) -> dict[str, Any]:
    """
    Returns a dict keyed by ticker with lists of {date, value} pairs.
    *tickers* is a comma-separated string, e.g. ``AAPL,MSFT,RELIANCE.NS``.
    *price_type* is one of: Open, High, Low, Close, Volume, Dividends, Stock Splits.
    """
    try:
        data = yf.Tickers(tickers=tickers).history(
            period=period, interval=interval, start=start, end=end, repair=True
        )
        # Drop columns that contain any NaN
        data = data.loc[:, ~data.apply(lambda col: col.hasnans, axis=0)]
        data.index = data.index.astype(str)
        col_data = data[price_type] if price_type in data.columns else data
        return col_data.to_dict()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


# ── Options ───────────────────────────────────────────────────────────────────

@router.get("/{ticker}/options", summary="Available option expiry dates")
async def get_options(ticker: str) -> list[str]:
    try:
        return list(yf.Ticker(ticker).options)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/{ticker}/options/{yyyymmdd}", summary="Calls and puts for a specific expiry")
async def get_option_chain(ticker: str, yyyymmdd: str) -> dict[str, Any]:
    try:
        t = yf.Ticker(ticker)
        chain = t.option_chain(yyyymmdd)
        ret: dict[str, Any] = {}
        for side in ("calls", "puts"):
            df = getattr(chain, side).copy()
            df["lastTradeDate"] = df["lastTradeDate"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            ret[side] = df.to_dict(orient="records")
        return ret
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


# ── Analyst / holder data ─────────────────────────────────────────────────────

@router.get("/{ticker}/upgrades_downgrades", summary="Upgrades and downgrades history")
async def get_upgrades_downgrades(ticker: str) -> dict[str, Any]:
    try:
        return yf.Ticker(ticker).upgrades_downgrades.T.to_dict()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/{ticker}/institutional_holders", summary="Institutional holders")
async def get_institutional_holders(ticker: str) -> dict[str, Any]:
    try:
        return yf.Ticker(ticker).institutional_holders.T.to_dict()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/{ticker}/analysts", summary="Analyst price targets")
async def get_analysts(ticker: str) -> Any:
    try:
        return yf.Ticker(ticker).analyst_price_targets
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


# ── News ──────────────────────────────────────────────────────────────────────

@router.get("/{tickers}/news", summary="Latest news for one or more comma-separated tickers")
async def get_news(tickers: str) -> Any:
    try:
        return yf.Tickers(tickers=tickers).news()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


# ── Search ────────────────────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    query: str
    exchanges: list[str] = ["BSE", "NSI"]


@router.post("/search", summary="Search / lookup tickers")
def search_tickers(req: SearchRequest) -> list[dict[str, Any]]:
    try:
        result = yf.Search(
            req.query,
            max_results=30,
            recommended=30,
            news_count=0,
            enable_fuzzy_query=True,
        ).all
        if "quotes" not in result:
            return []
        return [
            q for q in result["quotes"]
            if q.get("isYahooFinance") and q.get("exchange") in req.exchanges
        ]
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
