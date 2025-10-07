import streamlit as st
from datetime import datetime
from textwrap import dedent
from lib.yf import lookup_tickers,get_quote
from components.quote import show_quote
from lib import curr
from page_common import get_state
from lib.user import User

state=st.session_state

#--- code ----
@st.dialog("Select the ticker")
def lookup_shares():
    t=st.text_input("Search for shares/funds")
    quotes = lookup_tickers(get_state('profile'),t)
    selected_ticker= st.selectbox("Ticker", options=[f"{q["symbol"]} - {q["shortname"]} ({q["exchDisp"]} {q["typeDisp"]})"
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
    if not 'button' in state:
        state.button={}
    state.button[btn]=x

#----- UI ----
from components.sidebar import sidebar
from components.login import is_logged_in, please_register
with st.sidebar:
    sidebar()

if is_logged_in():

    st.title(f"Transactions")
    st.write(f"### Account: {state.user.email if state.get('proxy_login') else st.user.name}")
    
    cash_bal=getattr(state.user,"cash_balance",-0.01)
    currency=state.get('profile',{}).get('currency','-')
    st.write(dedent(f"""
                    ### are you ready ?
                    * Date: {datetime.now()}
                    * Cash: {curr(cash_bal)} {currency}
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
        if st.button('Check',type="primary"):
            st.write(f"Transaction --> Symbol: {state.ticker}, Quantity: {qty}, Price: {curr(price)},  Total Amount: {curr(amt)}")


        if get_state('quote',{'currency':''})['currency']=='INR':
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
                    # st.write("Your transaction completed.  ")
                    list_transactions()
                # st.page_link("pages/2_↔️_Transactions.py", label="Click here to Buy/Sell", icon="↔️") 
                    if st.button('Ready for next transaction?'):
                        set_status('tx',{})
                        state.ticker=''
                        st.rerun()
                    
        
    else:
        list_transactions()
else:
    please_register()


