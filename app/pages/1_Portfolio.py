import streamlit as st
from app.page_common import state
from app.components.profile import show_profile
import pandas as pd
import locale

locale.setlocale(locale.LC_ALL, '')  

state=st.session_state
portfolio=state.user.get_portfolio()
pf_value=portfolio['value'].sum()
          
st.title(f"Welcome {st.user.given_name}")
st.write(f"""
##### Cash: {state.user.cash_balance:,.2f} 
##### Portfolio: {pf_value:,.2f}
##### Total: {pf_value+state.user.cash_balance:,.2f}
""")

st.header(f"Summary") 
show_profile()
st.subheader("Portfolio")
st.write(portfolio)


st.page_link("pages/3_Transactions.py", label="Click here to Buy/Sell", icon="↔️")