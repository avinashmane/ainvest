import streamlit as st
from page_common import state
from components.profile import show_profile
import pandas as pd
from lib import dict2md_table
import locale

locale.setlocale(locale.LC_ALL, '')  

state=st.session_state
portfolio=state.user.get_portfolio()
pf_value=portfolio['value'].sum()

#----- UI ----
from components.sidebar import sidebar

with st.sidebar:
    sidebar()

st.title(f"Welcome {st.user.given_name}")

st.header(f"Summary") 
st.write(dict2md_table({
    'Cash': state.user.cash_balance,
    'Portfolio': pf_value,
    'Total': pf_value+state.user.cash_balance,
},["Balance","Amount"]))

st.subheader("Portfolio")
st.write(portfolio)


st.page_link("pages/3_Transactions.py", label="Click here to Buy/Sell", icon="↔️")