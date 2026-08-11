"""
lib/user.py
-----------
Streamlit-side user model.

All Firestore and yfinance I/O is delegated to the FastAPI server via
lib.api_client.  No direct firebase-admin / yfinance imports here.
"""

from __future__ import annotations

import pandas as pd
from lib import api_client
from lib.config import PVT_PF_SAVE_COLS

# Re-exported so other modules that do `from lib.user import PVT_PF_SAVE_COLS`
# continue to work.
__all__ = ["User", "Accounts", "default_profile", "PVT_PF_SAVE_COLS"]

default_profile = {
    "currency": "INR",
    "cash_balance": 1_00_00_000,
    "exchanges": ["BSE", "NSI"],
    "pvt_sheet_url": "",
    "pvt_named_range": "PF",
}


class User:
    """Streamlit-side user model — delegates all I/O to the FastAPI server."""

    profile: dict = {}
    tx_cols = "ticker amount quantity date price type".split()

    def __init__(self, email: str, db_client=None):
        # db_client kept for backward-compat but ignored on the Streamlit side
        self.email = email
        self.profile = {}

    def __repr__(self):
        return f"<{self.email}>"

    # ── Profile ───────────────────────────────────────────────────────────────

    def get_profile(self) -> dict:
        self.profile = api_client.get_profile(self.email)
        return self.profile

    def create(self) -> dict:
        return api_client.update_profile(self.email, **default_profile)

    def update(self, **kw) -> dict:
        return api_client.update_profile(self.email, **kw)

    # ── Transactions ──────────────────────────────────────────────────────────

    def add_transaction(self, ticker: str, quantity: int,
                        price: float, amount: float) -> str:
        result = api_client.add_transaction(self.email, ticker, quantity, price, amount)
        return result["timestamp"]

    def list_transactions(self) -> pd.DataFrame:
        rows = api_client.list_transactions(self.email)
        if not rows:
            return pd.DataFrame([], columns=self.tx_cols)
        df = pd.DataFrame(rows)
        present = [c for c in self.tx_cols if c in df.columns]
        return df[present]

    # ── Game portfolio ─────────────────────────────────────────────────────────

    def get_portfolio(self) -> pd.DataFrame:
        rows = api_client.get_game_portfolio(self.email)
        return pd.DataFrame(rows) if rows else pd.DataFrame()

    # ── Private portfolio (Firestore) ─────────────────────────────────────────

    def load_pvt_portfolio(self) -> pd.DataFrame:
        rows = api_client.get_pvt_pf(self.email)
        return pd.DataFrame(rows) if rows else pd.DataFrame()

    def save_pvt_portfolio(self, df: pd.DataFrame) -> int:
        present = [c for c in PVT_PF_SAVE_COLS if c in df.columns]
        subset = df[present].copy() if present else df.copy()
        rows = subset.to_dict(orient="records")
        n = api_client.save_pvt_pf(self.email, rows)
        self.pvt_pf = subset
        return n

    # ── Private portfolio (Google Sheets live read) ────────────────────────────

    def get_pvt_portfolio_gsheet(self) -> pd.DataFrame:
        rows = api_client.get_pvt_pf_gsheet(self.email)
        return pd.DataFrame(rows) if rows else pd.DataFrame()

    # ── Cash balance ──────────────────────────────────────────────────────────

    def update_cash_balance(self, start_bal: float = 1_00_00_000,
                            txs=None) -> float:
        if txs is None:
            txs = self.list_transactions()
        cost_basis = -txs.amount.sum()
        cash_balance = start_bal - cost_basis
        if cash_balance != self.cash_balance:
            self.update(cash_balance=cash_balance)
        return cash_balance

    @property
    def cash_balance(self) -> float:
        ret = self.profile.get("cash_balance")
        if ret is not None:
            return ret
        return self.get_profile().get("cash_balance", 0)


class Accounts:

    @staticmethod
    def list_users() -> pd.DataFrame:
        rows = api_client.list_users()
        if not rows:
            return pd.DataFrame([])
        return pd.DataFrame([r for r in rows if "hide" not in r])

    @staticmethod
    def get_leaderboard() -> pd.DataFrame:
        """Return users with portfolio values — computed server-side."""
        return Accounts.list_users()
