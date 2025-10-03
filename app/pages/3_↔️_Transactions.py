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
    st.write("You can also enter exact symbols founds on https://finance.yahoo.com. e.g. RELIANCE.BO")
    if st.button("Select"):
        state.ticker = selected_ticker.split("-")[1].strip()
        st.rerun()

def list_transactions():
    st.subheader("Transactions")

    with st.spinner(text="Getting your transactions", show_time=True):    
        txs=state.user.list_transactions().sort_values('date')
        st.write(txs)
        st.page_link('pages/1_📈_Portfolio.py', label="Check your 📈 Portflio")

def buy_sell(ticker,qty,price,amt):
    with st.spinner():
        ts  = state.user.add_transaction(ticker,qty,price,amt)
    # st.write(f'Transaction successful at {ts}.  Please check your portfolio')
    return ts

def set_status(btn,x=None):
    state.button[btn]=x

#----- UI ----
from components.sidebar import sidebar
from components.login import is_logged_in, please_register
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
                if st.button("Buy",
                             disabled=state.user.cash_balance<=amt,
                             on_click=set_status, args=['tx','Buy triggered']):
                    ts=buy_sell(state.ticker,qty,price,-amt)
                    set_status('tx',f"{ts} transaction completed")
                if st.button("Sell",
                             disabled=avl_qty<=qty,
                             on_click=set_status, args=['tx','Sell triggered']):
                    ts=buy_sell(state.ticker,-qty,price,amt)
                    set_status('tx',f"{ts} transaction completed")
            if status:=state.button.get('tx'):
                st.write(status)
                if 'completed' in state.button.get('tx'):
                    st.write("Your transaction completed.  Ready for next transaction?")
                    list_transactions()
                # st.page_link("pages/3_↔️_Transactions.py", label="Click here to Buy/Sell", icon="↔️") 
            
                    
        
    else:
        list_transactions()
else:
    please_register()


