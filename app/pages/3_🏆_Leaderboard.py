import streamlit as st
from pydash import omit
from lib.yf import lookup_tickers,get_quote
from page_common import init_state
from lib.user import Accounts

state=st.session_state

#--- code ----
@st.dialog("Select the ticker")
def lookup_shares():
    t=st.text_input("Search for shares/funds")
    quotes = lookup_tickers(state['profile'],t)
    selected_ticker= st.selectbox("Ticker", options=[f"{i} - {q["symbol"]} - {q["shortname"]} ({q["exchDisp"]} {q["typeDisp"]})"
                            for i,q in enumerate(quotes)])
    st.write("You can also enter exact symbols founds on https://finance.yahoo.com. e.g. RELIANCE.BO")
    if st.button("Select"):
        state.ticker = selected_ticker.split("-")[1].strip()
        st.rerun()

def set_status(btn,x=None):
    state.button[btn]=x

#----- UI ----
from components.sidebar import sidebar

with st.sidebar:
    sidebar()

st.title(f"Leaderboard")

cols="id currency total cash_balance".split()
if st.button('Load'):
    with st.spinner():
        users=Accounts.get_leaderboard()
        st.dataframe(users[cols])

         

    