import streamlit as st
from datetime import datetime
from textwrap import dedent
from lib.yf import lookup_tickers,get_quote
from components.quote import show_quote
from page_common import init_state
from lib.user import User

state=st.session_state

#--- code ----
@st.dialog("Select the ticker")
def lookup_shares():
    t=st.text_input("Search for shares/funds")
    quotes = lookup_tickers(state['profile'],t)
    selected_ticker= st.selectbox("Ticker", options=[f"{i} - {q["symbol"]} - {q["shortname"]} ({q["exchDisp"]} {q["typeDisp"]})"
                            for i,q in enumerate(quotes)])
    if st.button("Submit"):
        state.ticker = selected_ticker.split("-")[1].strip()
        st.rerun()

#----- UI ----
from components.sidebar import sidebar
from components.login import is_logged_in, please_login
with st.sidebar:
    sidebar()

if is_logged_in():

    st.title(f"Transactions")

    cash_bal=getattr(state.user,"cash_balance",-0.01)
    currency=state.get('profile',{}).get('currency','-')
    st.write(dedent(f"""
                    ## {st.user.given_name}, 
                    #### are you ready ?
                    * Date: {datetime.now()}
                    * Cash: {cash_bal:0,.2f} {currency}
    """))

    with st.container(horizontal=True):
        if st.button('Click here to Buy or Sell'):
            ticker= lookup_shares()
        if st.button('Cancel'):
                state.ticker=None            

    if 'ticker' in state and state.ticker:    

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

        with st.spinner(text="Getting your transactions", show_time=True):    
            txs=state.user.list_transactions().sort_values('date')
            st.write(txs)
else:
    please_login()