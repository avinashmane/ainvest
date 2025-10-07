import streamlit as st
from textwrap import dedent, shorten
from lib import curr
from millify import millify

def show_portfolio(df):
    df=df.sort_values('total',ascending=False).reset_index(drop=True).fillna('')
    
    for i,x in df.iterrows():
        with st.container(horizontal=True):
            st.header(f"{i+1}")
            st.write(dedent(f"""
                    #### {x.id} 
                    #### :yellow[{curr(x.total,0)}]
                    """))
            st.write(dedent(f"""
                    | Total| {curr(x.total)} |
                    |-|-:|
                    |Cash|{curr(x.cash_balance)} |
                    |Portfolio| {curr(x.portfolio)} |
                    """))
        st.divider()    
    # alternate(df)

    

def alternate(df):
    tbl=["|Account | |Balance |",
        "| - | -:| -: |"]
    for i,x in df.iterrows():
        tbl.append( f"|#{i+1} |{x.currency}| {curr(x.total)} |")
        tbl.append( f"|{x.id}|{curr(x.cash_balance)} | {curr(x.portfolio)} |")
    tbl="\n".join(tbl)        
    # print(tbl)
    st.write(tbl)
