"""
server/routers/users.py
-----------------------
Firestore user endpoints — profile, game portfolio, private portfolio.

GET    /users/{email}/profile
PUT    /users/{email}/profile          body: dict of fields to merge

GET    /users/{email}/transactions
POST   /users/{email}/transactions     body: TransactionIn

GET    /users/{email}/portfolio        (game portfolio derived from transactions)

GET    /users/{email}/pvt_pf           (saved private portfolio rows)
PUT    /users/{email}/pvt_pf           body: list of row dicts  → saves to Firestore

GET    /users/{email}/pvt_pf/gsheet    (reads live from the user's linked Google Sheet)

GET    /users                          (all users — leaderboard data)
"""

from __future__ import annotations

from typing import Any

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from lib.database import db_client
from lib.portfolio import enrich_pvt_portfolio
from lib.user import User
from lib.config import PVT_PF_SAVE_COLS
from lib import now

router = APIRouter(prefix="/api/users", tags=["users"])


# ── helpers ───────────────────────────────────────────────────────────────────

def _user(email: str) -> User:
    return User(email, db_client=db_client)


# ── Profile ───────────────────────────────────────────────────────────────────

@router.get("/{email}/profile", summary="Get user profile")
def get_profile(email: str) -> dict[str, Any]:
    try:
        return _user(email).get_profile()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.put("/{email}/profile", summary="Update user profile fields")
def update_profile(email: str, fields: dict[str, Any]) -> dict[str, Any]:
    try:
        _user(email).update(**fields)
        return {"updated": list(fields.keys())}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


# ── Transactions ──────────────────────────────────────────────────────────────

@router.get("/{email}/transactions", summary="List transactions")
def list_transactions(email: str) -> list[dict[str, Any]]:
    try:
        df = _user(email).list_transactions()
        return df.to_dict(orient="records")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


class TransactionIn(BaseModel):
    ticker: str
    quantity: int
    price: float
    amount: float


@router.post("/{email}/transactions", summary="Add a transaction")
def add_transaction(email: str, tx: TransactionIn) -> dict[str, Any]:
    try:
        ts = _user(email).add_transaction(tx.ticker, tx.quantity, tx.price, tx.amount)
        return {"timestamp": ts}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# ── Game portfolio (derived from transactions) ────────────────────────────────

@router.get("/{email}/portfolio", summary="Get game portfolio (from transactions + live prices)")
def get_portfolio(email: str) -> list[dict[str, Any]]:
    try:
        df = _user(email).get_portfolio()
        if df.empty:
            return []
        return df.to_dict(orient="records")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


# ── Private portfolio — Firestore ─────────────────────────────────────────────

@router.get("/{email}/pvt_pf", summary="Private portfolio with live prices and gain columns")
def get_pvt_pf(email: str) -> dict[str, Any]:
    """
    Returns saved portfolio rows joined with live yfinance prices plus
    portfolio-level summary totals.  Shape expected by PvtPortfolioView:

        { rows: [...], summary: { totalValue, totalCost, totalDayGain,
                                   totalDayGainPct, totalGain, totalGainPct } }
    """
    try:
        df = _user(email).load_pvt_portfolio()
        if df.empty:
            return {"rows": [], "summary": {}}
        return enrich_pvt_portfolio(df)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc



@router.put("/{email}/pvt_pf", summary="Save private portfolio rows to Firestore")
def save_pvt_pf(email: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    try:
        df = pd.DataFrame(rows)
        n = _user(email).save_pvt_portfolio(df)
        return {"saved": n}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


# ── Private portfolio — Google Sheets (live read) ─────────────────────────────

@router.get("/{email}/pvt_pf/gsheet", summary="Read private portfolio live from Google Sheets")
def get_pvt_pf_gsheet(email: str) -> list[dict[str, Any]]:
    try:
        u = _user(email)
        u.get_profile()          # ensure profile fields (pvt_sheet_url etc.) are loaded
        df = u.get_pvt_portfolio_gsheet()
        return df.to_dict(orient="records")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


# ── All users (leaderboard) ───────────────────────────────────────────────────

@router.get("", summary="List all users with portfolio values (leaderboard)")
def list_users() -> list[dict[str, Any]]:
    try:
        from lib.user import Accounts
        from lib.yf import get_quote as _get_quote

        users_df = Accounts.list_users()
        if users_df.empty:
            return []

        def _pf_value(row):
            try:
                pf = User(row["id"], db_client=db_client).get_portfolio()
                return float(pf["value"].sum()) if not pf.empty else 0.0
            except Exception:
                return 0.0

        users_df["portfolio"] = users_df.apply(_pf_value, axis=1)
        users_df["total"] = users_df["portfolio"] + users_df.get("cash_balance", 0)
        return users_df.fillna("").to_dict(orient="records")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
