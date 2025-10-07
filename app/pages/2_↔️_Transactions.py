import streamlit as st
from datetime import datetime
from textwrap import dedent
from lib.yf import lookup_tickers,get_quote
from components.quote import show_quote
from lib import curr
from page_common import get_state, init_state
from lib.user import User
from box import Box

state=st.session_state

#--- code ----

def set_txn_status(x=None):
    print(f'set_txn_status({x}')
    if not 'transaction' in state:
        state.transaction={"status":'ready'}
    state.transaction['status']=x

@st.dialog("Select the ticker")
def ticker_get():
    t=st.text_input("Search for shares/funds")
    quotes = lookup_tickers(get_state('profile'),t)
    selected_ticker= st.selectbox("Ticker", options=[f"{q["symbol"]} - {q["shortname"]} ({q["exchDisp"]} {q["typeDisp"]})"
                            for i,q in enumerate(quotes)])
    st.write("You can also enter exact symbols founds on https://finance.yahoo.com. e.g. RELIANCE.BO")
    if st.button("Select"):
        state.transaction.ticker = selected_ticker.split(" - ")[0].strip()
        set_txn_status('ready')
        st.rerun()

def ticker_clear():
    state.transaction.ticker=None    
    set_txn_status('')     
     
def get_portfolio():
    return state.user.get_portfolio()

def list_transactions():
    st.subheader("Transactions")
    # if st.button('Transactions'):
    with st.spinner(text="Getting your transactions", show_time=True):    
        txs=state.user.list_transactions().sort_values('date')
        st.write(txs)
    st.page_link('pages/1_📈_Portfolio.py', label="Check your 📈 Portflio")    

@st.fragment
def tranasction_check(qty, price, amt):
    pass
def tranasction_buy_sell(ticker,qty,price,amt):
    with st.spinner():
        ts  = state.user.add_transaction(ticker,qty,price,amt)
    # st.write(f'Transaction successful at {ts}.  Please check your portfolio')
    return ts

def transaction_completed():
    st.write(status)
    with st.container(horizontal=False):
        if st.button('Ready for next transaction?'):
            set_txn_status('ready')
            st.rerun()

        if st.button('List transactions?'):
            list_transactions()

def buy_sell_button(tx_type,btn_type,qty,price,amt,condition):
            print("buy_sell_button {} {} {}".format(tx_type,state.transaction.status, condition or ('check' not in status)))
            if st.button(tx_type,  type= btn_type,
                        disabled = condition or ('check' not in state.transaction.status)  ):
                set_txn_status(f'{tx_type} triggered')
                ts=tranasction_buy_sell(state.transaction.ticker,qty,price,amt)
                msg=f"{tx_type} {ts} transaction completed"
                set_txn_status(msg)
                st.toast(msg)
                amt+=avl_qty

#----- UI ----
from components.sidebar import sidebar
from components.login import is_logged_in, please_register
with st.sidebar:
    sidebar()

@st.fragment
def transaction_check():
    with st.container(horizontal=True):
        if st.button('Check',  disabled= 'check' in state.transaction.status):
            set_txn_status('checked')
            st.rerun()
                    
        if st.button('Edit', disabled= 'check' not in state.transaction.status):
            set_txn_status('ready')
            st.rerun()

if is_logged_in():

    st.title(f"Transactions")
    st.write(f"### Account: {state.user.email if state.get('proxy_login') else st.user.name}")
    
    cash_bal=getattr(state.user,"cash_balance",-0.01)
    currency=get_state('profile',{}).get('currency','-')
    init_state('transaction',Box({'status':'', 'ticker':None}))
    status=state.transaction.status
    st.write(dedent(f"""
                    ### are you ready ?
                    * Date: {datetime.now()}
                    * Cash: {curr(cash_bal)} {currency}
                    """))

    with st.container(horizontal=True):
        if st.button('Select stock/fund to Buy or Sell', 
                     type="secondary" if state.transaction.ticker else "primary"):
            set_txn_status('')
            ticker= ticker_get()

        if st.button('Clear'):
                ticker_clear()
                      

    if 'ticker' in state.transaction and state.transaction.ticker:    

        st.write(f"## {state.transaction.ticker}")

        portfolio=get_portfolio()
        state['quote']=get_quote(state.transaction.ticker)
        show_quote(state['quote'])
        
        try: 
            avl_qty= portfolio.query("ticker==@state.transaction.ticker").iloc[0,:]['quantity']
        except: 
            avl_qty= 0
        
        st.number_input("Available Quantity", value=avl_qty, disabled=True)
        
        qty=st.number_input("Quantity", value=100, min_value=1)
        price=st.number_input("Price", value=round(state['quote']['lastPrice'],2), min_value=1.0, disabled=True)

        amt=round(qty*price,2)
        if get_state('quote',{'currency':''})['currency']=='INR':

            # check transaction details
            transaction_check()      
             
            if 'check' in state.transaction.status:
                amt=st.number_input("Value", value=amt, min_value=1.0, disabled=True)

                st.write("Transaction ➡️ Symbol: **{}**, Quantity: **{}**, Price: {},  Total Amount: **{}**"
                            .format(state.transaction.ticker, qty, curr(price), curr(amt)))  

                with st.container(horizontal=True):
                    btn_type= "secondary" if 'check' not in status else "primary"
                    buy_sell_button( "Buy",  btn_type, qty, price, -amt, 
                        state.user.cash_balance< amt)
                    buy_sell_button( "Sell", btn_type, -qty, price, amt, 
                        avl_qty < qty)

            if 'complete' in state.transaction.status:
                transaction_completed()

    else:
        list_transactions()
else:
    please_register()


# st.write(state.transaction)