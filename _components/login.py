import json
import streamlit as st
from textwrap import dedent

with open(".streamlit/firebase_key.json") as f:
    firebase_key=json.load(f)

# print(firebase_key['client_email'])

def show_login():
    if not st.user.is_logged_in:
        login_screen()
    else:
        st.markdown(f'<img src="{st.user.picture}" style="border-radius:100%" with="100px"/>',
                           unsafe_allow_html=True)
        st.header(f"Welcome {st.user.given_name or st.user.name}!")

        st.button("Log out", on_click=st.logout)

def st_login():
    return st.login(provider='google')

def login_screen():
    st.header("This app is private.")
    st.subheader("Please log in.")
    st.button("Log in with Google", 
              on_click=st_login)