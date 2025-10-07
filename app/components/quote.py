import streamlit as st
from lib import curr
from textwrap import dedent

def show_quote(quote):
    # md=dedent(f"""
    #     * {quote.get("exchange")} {quote.get("currency")} {quote.get("timezone")}
    #     * day Range: {curr(quote.get("dayLow"))} <-> {curr(quote.get("dayHigh"))} 
    #     * Last/Close: {curr(quote.get("lastPrice"))} / {curr(quote.get("previousClose"))}
    #     """)
    def get(x):
        val= quote.get(x,'-')
        return curr(val) if type(val) in [int,float] \
            else val
    
    md=dedent("""
        * {} {} {}
        * Day Range: {} <-> {} 
        * Last/Close: {} / {}
        """).format(get("exchange"),
                   get("currency") ,
                   get("timezone"),
                   get("dayLow"),                       get("dayHigh"),
                   get("lastPrice"),                    get("previousClose")
                   )
    st.markdown(md)
    