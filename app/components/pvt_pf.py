import streamlit as st
from lib.user import PVT_PF_SAVE_COLS
import pandas as pd
state = st.session_state


def show_pvt_profile():
    """Show the GSheets settings form and a 'Load from GSheets' button.

    Stores the loaded DataFrame in ``state.pvt_pf_staged`` so it survives
    reruns.  Returns the staged DataFrame (or an empty one if not yet loaded).
    """
    st.write("# Private portfolio")
    user = state.user

    # Ensure profile is loaded
    if not user.profile:
        user.get_profile()

    url = user.profile.get("pvt_sheet_url", "")
    named_range = user.profile.get("pvt_named_range", "PF") or "PF"

    # ── Settings form ──────────────────────────────────────────────────────────
    with st.expander("⚙️ Private sheet settings", expanded=not url):
        with st.form("pvt_sheet_form"):
            new_url = st.text_input(
                "Google Sheet URL",
                value=url,
                placeholder="https://docs.google.com/spreadsheets/d/…",
            )
            new_range = st.text_input(
                "Named range",
                value=named_range,
                placeholder="PF",
            )
            if st.form_submit_button("Save settings"):
                user.update(pvt_sheet_url=new_url, pvt_named_range=new_range)
                user.profile["pvt_sheet_url"] = new_url
                user.profile["pvt_named_range"] = new_range
                st.success("Settings saved.")
                st.rerun()

    # ── Load button ────────────────────────────────────────────────────────────
    if not url:
        st.info("Add a Google Sheet URL above to load your private portfolio.")
        return pd.DataFrame()

    if st.button("🔄 Load from GSheets"):
        df = load_pvt_pf(user, url)
        state.pvt_pf_staged = df

    return state.get("pvt_pf_staged", pd.DataFrame())


def save_pvt_pf(df: pd.DataFrame):
    """Preview the GSheets-loaded *df* and stage it in ``state.user.pvt_pf``.

    Does NOT write to Firestore — that is done by the explicit Save button on
    the page so the user can review first.
    """
    if df.empty:
        return

    present = [c for c in PVT_PF_SAVE_COLS if c in df.columns]
    missing = [c for c in PVT_PF_SAVE_COLS if c not in df.columns]

    st.subheader("Loaded from Google Sheets — preview")
    st.caption(
        f"Columns to save: **{', '.join(present)}**"
        + (f"  •  not found in sheet: {', '.join(missing)}" if missing else "")
    )
    st.dataframe(df[present] if present else df, use_container_width=True, hide_index=True)

    # Stage in user object so the Save button on the page can pick it up
    state.user.pvt_pf = df[present].copy() if present else df.copy()


def show_pvt_pf(df):
    """Render live prices, summary metrics and the styled holdings table for *df*."""
    from lib.api_client import get_quote
    from lib import curr

    # Coerce numeric columns that come back as strings from Firestore
    for col in ["Quantity", "Cost Basis"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # ── Fetch live quotes ─────────────────────────────────────────────────────
    with st.spinner("Fetching live prices…", show_time=True):
        quotes = {}
        for sym in df["Symbol"].dropna().unique():
            quotes[sym] = get_quote(sym)

    def _q(sym, field, default=0.0):
        return quotes.get(sym, {}).get(field) or default

    df["Last Price"]    = df["Symbol"].map(lambda s: _q(s, "lastPrice"))
    df["Prev Close"]    = df["Symbol"].map(lambda s: _q(s, "previousClose"))
    df["Current Value"] = df["Quantity"] * df["Last Price"]
    df["Daily Gain $"]  = df["Quantity"] * (df["Last Price"] - df["Prev Close"])
    df["Daily Gain %"]  = ((df["Last Price"] - df["Prev Close"])
                           / df["Prev Close"].replace(0, float("nan")) * 100)
    df["Total Gain $"]  = df["Current Value"] - df["Cost Basis"]
    df["Total Gain %"]  = (df["Total Gain $"]
                           / df["Cost Basis"].replace(0, float("nan")) * 100)

    # ── Summary cards ─────────────────────────────────────────────────────────
    total_value      = df["Current Value"].sum()
    total_cost       = df["Cost Basis"].sum()
    total_daily_gain = df["Daily Gain $"].sum()
    total_gain       = df["Total Gain $"].sum()
    daily_gain_pct   = (total_daily_gain / (total_value - total_daily_gain)
                        * 100) if (total_value - total_daily_gain) else 0.0
    total_gain_pct   = total_gain / total_cost * 100 if total_cost else 0.0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Portfolio Value", f"₹{curr(total_value)}")
    col2.metric("Cost Basis",      f"₹{curr(total_cost)}")
    col3.metric(
        "Daily Gain",
        f"₹{curr(total_daily_gain)}",
        f"{total_daily_gain:+.2f}  ({daily_gain_pct:+.2f}%)",
        delta_color="normal",
    )
    col4.metric(
        "Total Gain",
        f"₹{curr(total_gain)}",
        f"{total_gain:+.2f}  ({total_gain_pct:+.2f}%)",
        delta_color="normal",
    )

    # ── Holdings table ────────────────────────────────────────────────────────
    st.subheader("Holdings")

    display_cols = [c for c in [
        "Symbol", "Name", "Account Number",
        "Quantity", "Cost Basis",
        "Last Price", "Current Value",
        "Daily Gain $", "Daily Gain %",
        "Total Gain $", "Total Gain %",
    ] if c in df.columns]

    def _colour(val):
        try:
            return "color: green" if float(val) >= 0 else "color: red"
        except (TypeError, ValueError):
            return ""

    gain_cols = [c for c in ["Daily Gain $", "Daily Gain %", "Total Gain $", "Total Gain %"]
                 if c in df.columns]

    styled = (
        df[display_cols]
        .style
        .applymap(_colour, subset=gain_cols)
        .format({
            "Last Price":    "{:,.2f}",
            "Cost Basis":    "{:,.2f}",
            "Current Value": "{:,.2f}",
            "Daily Gain $":  "{:+,.2f}",
            "Daily Gain %":  "{:+.2f}%",
            "Total Gain $":  "{:+,.2f}",
            "Total Gain %":  "{:+.2f}%",
            "Quantity":      "{:,.4g}",
        }, na_rep="—")
    )

    st.dataframe(styled, use_container_width=True, hide_index=True)
    st.caption("Prices refresh on page reload · 60-second cache per ticker")


def load_pvt_pf(user, url):
    with st.spinner("Loading private portfolio…"):
        try:
            df = user.get_pvt_portfolio_gsheet()
        except Exception as exc:
            st.error(f"Could not read sheet: {exc}")
            return pd.DataFrame()
    return df
