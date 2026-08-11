"""
lib/api_client.py
-----------------
Thin HTTP client for the ainvest FastAPI server.

All yfinance and Firestore calls in the Streamlit front-end go through this
module so the back-end can be replaced or scaled independently.

Usage
-----
    from lib.api_client import api

    quote  = api.get_quote("INFY.NS")
    rows   = api.get_pvt_pf("user@example.com")
"""

from __future__ import annotations

from typing import Any

import requests

from lib.config import API_BASE_URL as _BASE


class _ApiError(RuntimeError):
    """Raised when the API returns a non-2xx response."""


def _get(path: str, **params) -> Any:
    url = f"{_BASE}{path}"
    r = requests.get(url, params=params, timeout=30)
    if not r.ok:
        raise _ApiError(f"GET {path} → {r.status_code}: {r.text}")
    return r.json()


def _put(path: str, json: Any) -> Any:
    url = f"{_BASE}{path}"
    r = requests.put(url, json=json, timeout=30)
    if not r.ok:
        raise _ApiError(f"PUT {path} → {r.status_code}: {r.text}")
    return r.json()


def _post(path: str, json: Any) -> Any:
    url = f"{_BASE}{path}"
    r = requests.post(url, json=json, timeout=30)
    if not r.ok:
        raise _ApiError(f"POST {path} → {r.status_code}: {r.text}")
    return r.json()


# ── Quotes ────────────────────────────────────────────────────────────────────

def get_quote(ticker: str) -> dict[str, Any]:
    """Return live quote dict for *ticker* (60-second server-side cache)."""
    return _get(f"/quotes/{ticker}")


def get_history(ticker: str, period: str = "1y") -> list[dict[str, Any]]:
    """Return OHLCV history rows for *ticker*."""
    return _get(f"/quotes/{ticker}/history", period=period)


def search_tickers(query: str, exchanges: list[str] | None = None) -> list[dict[str, Any]]:
    """Search / lookup tickers by keyword."""
    return _post("/quotes/search", json={"query": query, "exchanges": exchanges or ["BSE", "NSI"]})


# ── Public portfolio (GSheets) ────────────────────────────────────────────────

def get_portfolio_gsheet(url: str = "", named_range: str = "") -> list[dict[str, Any]]:
    params: dict[str, str] = {}
    if url:
        params["url"] = url
    if named_range:
        params["named_range"] = named_range
    return _get("/portfolio", **params)


# ── User profile ──────────────────────────────────────────────────────────────

def get_profile(email: str) -> dict[str, Any]:
    return _get(f"/users/{email}/profile")


def update_profile(email: str, **fields) -> dict[str, Any]:
    return _put(f"/users/{email}/profile", json=fields)


# ── Transactions ──────────────────────────────────────────────────────────────

def list_transactions(email: str) -> list[dict[str, Any]]:
    return _get(f"/users/{email}/transactions")


def add_transaction(email: str, ticker: str, quantity: int,
                    price: float, amount: float) -> dict[str, Any]:
    return _post(f"/users/{email}/transactions",
                 json={"ticker": ticker, "quantity": quantity,
                       "price": price, "amount": amount})


# ── Game portfolio ────────────────────────────────────────────────────────────

def get_game_portfolio(email: str) -> list[dict[str, Any]]:
    return _get(f"/users/{email}/portfolio")


# ── Private portfolio ─────────────────────────────────────────────────────────

def get_pvt_pf(email: str) -> list[dict[str, Any]]:
    """Load saved private portfolio rows from Firestore."""
    return _get(f"/users/{email}/pvt_pf")


def save_pvt_pf(email: str, rows: list[dict[str, Any]]) -> int:
    """Persist *rows* to Firestore; returns the number of rows saved."""
    result = _put(f"/users/{email}/pvt_pf", json=rows)
    return result.get("saved", 0)


def get_pvt_pf_gsheet(email: str) -> list[dict[str, Any]]:
    """Read private portfolio live from the user's linked Google Sheet."""
    return _get(f"/users/{email}/pvt_pf/gsheet")


# ── Leaderboard ───────────────────────────────────────────────────────────────

def list_users() -> list[dict[str, Any]]:
    """Return all users with portfolio values for the leaderboard."""
    return _get("/users")
