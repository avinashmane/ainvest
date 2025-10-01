import streamlit as st
import pandas as pd
from datetime import datetime
from textwrap import dedent
from lib.yf import lookup_tickers,get_quote
from app.components.quote import show_quote
from app.page_common import init_state
from lib.user import User

state=st.session_state

#--- code ----

# init_state("tickers",[])


@st.dialog("Select the ticker")
def lookup_shares():
    t=st.text_input("Search for shares/funds")
    quotes = lookup_tickers(state['profile'],t)
    selected_ticker= st.selectbox("Ticker", options=[f"{i} - {q["symbol"]} - {q["shortname"]} ({q["exchDisp"]} {q["typeDisp"]})"
                            for i,q in enumerate(quotes)])
    if st.button("Submit"):
        state.ticker = selected_ticker.split("-")[1].strip()
        st.rerun()


#! --- UI ------

if st.user.is_logged_in:

    st.title(f"Welcome {st.user.given_name}")

    st.write(dedent(f"""
                    ## Buy or Sell
                    #### Date: {datetime.now()}
                    #### Cash: {state.user.cash_balance:0,.2f} {state.profile.get('currency')}
    """))

    with st.container(horizontal=True):
        if st.button('Select Ticker Symbol'):
            ticker= lookup_shares()
        if st.button('Cancel'):
                state.ticker=None            

    if state.ticker:    

        st.write(f"## {state.ticker}")
        portfolio=state.user.get_portfolio()
        state['quote']=get_quote(state.ticker)
        show_quote(state['quote'])
        
        try: avl_qty=portfolio.query("ticker==@state.ticker").loc[0,'quantity']
        except: avl_qty=0
        
        st.number_input("Available Quantity", value=avl_qty, disabled=True)
        
        qty=st.number_input("Quantity", value=100, min_value=1)
        price=st.number_input("Price", value=round(state['quote']['lastPrice'],2), min_value=1.0, disabled=True)
        amt=st.number_input("Value", value=round(qty*price,2), min_value=1.0, disabled=True)


        if state['quote']['currency']=='INR':
            with st.container(horizontal=True):
                if st.button("Buy",disabled=state.user.cash_balance<=amt):
                    state.user.add_transaction(state.ticker,
                                               qty,
                                               price,
                                               -amt)
                if st.button("Sell",disabled=avl_qty<=qty):
                    state.user.add_transaction(state.ticker,
                                               -qty,
                                               price,
                                               amt)
        
    else:
        st.subheader("Transactions")
        txs=state.user.list_transactions().sort_values('date')
        st.write(txs)
