import streamlit as st
from page_common import state
from components.profile import show_profile
import pandas as pd
from lib import dict2md_table
import locale

locale.setlocale(locale.LC_ALL, '')  

state=st.session_state


#----- UI ----
from components.sidebar import sidebar
from components.login import is_logged_in, please_register
with st.sidebar:
    sidebar()

if is_logged_in():
    st.title(f"Welcome {st.user.given_name}")

    st.header(f"Summary") 

    with st.spinner(text="Getting your holdings", show_time=True):
        try:
            portfolio=state.user.get_portfolio()
            pf_value=portfolio['value'].sum()
        except:
            pf_value=0

        st.write(dict2md_table({
            'Cash': state.user.cash_balance,
            'Portfolio': pf_value,
            'Total': pf_value+state.user.cash_balance,
        },["Balance","Amount"]))

        st.subheader("Portfolio")
        st.write(portfolio)


        st.page_link("pages/3_Transactions.py", label="Click here to Buy/Sell", icon="↔️")

else:
    please_register()