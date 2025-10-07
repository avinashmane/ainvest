import streamlit as st
from lib import curr

def show_quote(quote):
    st.markdown(f"""
* {quote.get("exchange")} {quote.get("currency")} {quote.get("timezone")}
* day Range: {curr(quote.get("dayLow"))} <-> {curr(quote.get("dayHigh"))} 
* Last/Close: {curr(quote.get("lastPrice"))} / {curr(quote.get("previousClose"))}
    """)