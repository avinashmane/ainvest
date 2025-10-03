import streamlit as st
import yfinance as yf
import re
from pydash import chunk

def titlize(name):
    ret=re.sub(r'(?<!^)(?=[A-Z])', ' ', name)
    return ret[0].upper()+ret[1:]

def show_stock(ticker):
    t=yf.Ticker(ticker)
    info=t.info
    if not 'shortName' in info:
        st.write("Invalid ticker.... Please check https://finance.yahoo.com")
    else:
        with st.spinner():
            st.subheader(f"{ticker} : Overview")
            cols=[x for x in "shortName currency previousClose open dayLow dayHigh".split() if x in info]
            for chnk in chunk(cols,2):
                st.write
                with st.container(horizontal=True):
                    for f in chnk:
                        st.write(f"{titlize(f):>30} : {info[f]}")
        
        st.subheader( f"{ticker} : Price history")
        altair_chart(t)

            
import altair as alt
import pandas as pd
def altair_chart(ticker_obj):
    period=st.radio("Period", index=1, options=["1mo","1y",'5y','10y'], horizontal=True)

    with st.spinner():
        df_price= ticker_obj.history( period ).reset_index()#['Close']
        close_desc=df_price['Close'].describe(exclude=[0,None])
        st.dataframe({"Close":{  "Open":df_price['Close'].values[0],
                        "Minimum":close_desc['min'],
                      "Maximum":close_desc['max'],
                      }} )

        st.altair_chart(alt.Chart(df_price).mark_line().encode(
            x="Date:T",
            y=alt.Y( "Close:Q").scale(zero=False, 
                        domain=(close_desc['min']*0.99,close_desc['max']*1.01)),
            # color="source:N"
        ))
            