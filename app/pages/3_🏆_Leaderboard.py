import streamlit as st
from pydash import omit
from lib.yf import lookup_tickers,get_quote
from page_common import init_state
from lib.user import Accounts
from components.account import show_portfolio
state=st.session_state

#--- code ----


#----- UI ----
from components.sidebar import sidebar

with st.sidebar:
    sidebar()

st.title(f"Leaderboard")

cols="id currency total cash_balance".split()
if True:# always/ st.button('Load'):
    with st.spinner():
        users=Accounts.get_leaderboard()
        # st.dataframe(users)
        show_portfolio(users)

         

    