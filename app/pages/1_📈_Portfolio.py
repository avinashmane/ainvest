import streamlit as st
from page_common import state
from components.profile import show_profile
import pandas as pd
from lib import dict2md_table, curr
import locale

locale.setlocale(locale.LC_ALL, '')  

state=st.session_state


#----- UI ----
from components.sidebar import sidebar
from components.login import is_logged_in, please_register
with st.sidebar:
    sidebar()

if is_logged_in():
    st.title(f"Portfolio ")
    st.write(f"### Account: {state.user.email if state.get('proxy_login') else st.user.name}")
    st.header(f"Balances") 

    with st.spinner(text="Getting your holdings", show_time=True):
        try:
            portfolio=state.user.get_portfolio()
            pf_value=portfolio['value'].sum()
        except:
            pf_value=0

        st.write(dict2md_table({
            'Cash': curr(state.user.cash_balance),
            'Portfolio': curr(pf_value),
            'Total': curr(pf_value+state.user.cash_balance),
        },["Balance","Amount"]))

        st.subheader("Portfolio")
        st.write(portfolio)

        st.page_link("pages/2_↔️_Transactions.py", label="Click here to Buy/Sell", icon="↔️")

else:
    please_register()