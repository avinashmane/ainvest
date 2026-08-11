import streamlit as st
import re
import pandas as pd
import altair as alt
from pydash import chunk
from lib import api_client


def titlize(name):
    ret = re.sub(r'(?<!^)(?=[A-Z])', ' ', name)
    return ret[0].upper() + ret[1:]


def show_stock(ticker):
    with st.spinner():
        try:
            info = api_client.get_quote(ticker)
        except Exception as exc:
            st.error(f"Could not fetch quote: {exc}")
            return

    if not info.get("name"):
        st.write("Invalid ticker.... Please check https://finance.yahoo.com")
        return

    st.subheader(f"{ticker} : Overview")
    fields = [f for f in "name currency previousClose lastPrice dayLow dayHigh".split()
              if f in info]
    for chnk in chunk(fields, 2):
        with st.container(horizontal=True):
            for f in chnk:
                st.write(f"{titlize(f):>30} : {info[f]}")

    st.subheader(f"{ticker} : Price history")
    _altair_chart(ticker)


def _altair_chart(ticker: str):
    period = st.radio("Period", index=1, options=["1mo", "1y", "5y", "10y"], horizontal=True)

    with st.spinner():
        try:
            rows = api_client.get_history(ticker, period=period)
        except Exception as exc:
            st.error(f"Could not fetch history: {exc}")
            return

        df_price = pd.DataFrame(rows)
        if df_price.empty:
            st.info("No history data available.")
            return

        close_desc = df_price["Close"].describe()
        st.write(
            f"Open:{df_price['Close'].values[0]:,.2f}, "
            f"Minimum: {close_desc['min']:,.2f}, Maximum: {close_desc['max']:,.2f}"
        )

        st.altair_chart(
            alt.Chart(df_price).mark_line().encode(
                x="Date:T",
                y=alt.Y("Close:Q").scale(
                    zero=False,
                    domain=(close_desc["min"] * 0.99, close_desc["max"] * 1.01),
                ),
            )
        )
