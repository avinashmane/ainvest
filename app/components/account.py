import streamlit as st
from textwrap import dedent, shorten
from lib import curr

def show_portfolio(df):
    
    df=df.sort_values('total',ascending=False).reset_index(drop=True).fillna('')

    for i,x in df.iterrows():
        with st.container(horizontal=True,):
            name = x.get('name')  or x.id.split("@")[0]
            st.header(f"{i+1}")
            with st.container(width=250):
                st.write(dedent(f"""
                    ## :yellow[{curr(x.total,0)}]
                    #### {name} 
                    """))
            st.write(dedent(f"""
                    | Total| {curr(x.total)} |
                    |-|-:|
                    |Cash|{curr(x.cash_balance)} |
                    |Portfolio| {curr(x.portfolio)} |
                    """))
        st.divider()    
    # alternate(df)

    

def show_transactions(df):
    df=df.sort_values('date',ascending=False).reset_index(drop=True).fillna('')
    
    if rows:=len(df)>10:
        if st.button('More/Less'):
            rows=10

    for i,x in df.iloc[:rows].iterrows():
        with st.container(horizontal=True,):
            name = x.get('name')  or x.id.split("@")[0]
            st.header(f"{i+1}")
            with st.container(width=250):
                st.write(dedent(f"""
                    ## :yellow[{curr(x.total,0)}]
                    #### {name} 
                    """))
            st.write(dedent(f"""
                    | Total| {curr(x.total)} |
                    |-|-:|
                    |Cash|{curr(x.cash_balance)} |
                    |Portfolio| {curr(x.portfolio)} |
                    """))
        st.divider()    
