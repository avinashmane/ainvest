import streamlit as st

def show_quote(quote):
    st.markdown(f"""
* {quote["exchange"]} {quote["currency"]} {quote["timezone"]}
* day Range: {quote["dayLow"]:.2f} <-> {quote["dayHigh"]:.2f} 
* Last/Close: {quote["lastPrice"]:.2f} / {quote["previousClose"]:.2f}
    """)