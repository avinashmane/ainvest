import streamlit as st
import pandas as pd
from page_common import state
from components.sidebar import sidebar
from components.login import is_logged_in, please_register
from components.pvt_pf import show_pvt_profile, save_pvt_pf, show_pvt_pf

ALLOWED_USER = "avinashmane"

with st.sidebar:
    sidebar()

if not is_logged_in():
    please_register()
    st.stop()

if not state.user.email.startswith(ALLOWED_USER):
    st.error("You do not have access to this page.")
    st.stop()

# ── Load from Firestore once per session ──────────────────────────────────────
if not hasattr(state.user, "pvt_pf"):
    with st.spinner("Loading saved portfolio…"):
        state.user.pvt_pf = state.user.load_pvt_portfolio()

tab_pf, tab_setup, tab3 = st.tabs(["PF", "Setup", "Owl"])

# ── Tab: Portfolio ─────────────────────────────────────────────────────────────
with tab_pf:
    st.header("💼 Private Portfolio")
    st.write(f"### Account: {state.user.email}")

    if state.user.pvt_pf.empty:
        st.info("No portfolio data saved yet. Use the **Setup** tab to load from Google Sheets and save.")
    else:
        show_pvt_pf(state.user.pvt_pf)

# ── Tab: Setup (load from GSheets → preview → save to Firestore) ───────────────
with tab_setup:
    # Show settings form + Load button; returns the staged df (or empty)
    df = show_pvt_profile()

    # If something was loaded, preview it and stage it on user object
    save_pvt_pf(df)

    # Save to Firestore only when user explicitly clicks
    pvt_pf = getattr(state.user, "pvt_pf", pd.DataFrame())
    if st.button("💾 Save to Firestore", disabled=pvt_pf.empty):
        try:
            n = state.user.save_pvt_portfolio(pvt_pf)
            st.success(f"Saved {n} rows to Firestore.")
        except Exception as exc:
            st.error(f"Save failed: {exc}")

# ── Tab: Owl ───────────────────────────────────────────────────────────────────
with tab3:
    st.header("An owl")
