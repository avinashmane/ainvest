import json
import streamlit as st
from lib.user import User

# with open(".streamlit/firebase_key.json") as f:
#     firebase_key=json.load(f)

# print(firebase_key['client_email'])

def show_login():
    if not st.user.is_logged_in:
        login_screen()
    else:
        logged_in()

def logged_in():
    st.session_state.user=User(st.user.email)
    st.session_state.user.update(**st.session_state.user.get_profile())
    st.markdown(f'<img src="{st.user.picture}" style="border-radius:100%" with="100px"/>',
                           unsafe_allow_html=True)
    st.header(f"Welcome {st.user.given_name or st.user.name}!")

    st.button("Log out", on_click=st.logout)

def st_login():
    return st.login(provider='google')

def login_screen():
    st.header("This app is needs.")
    st.subheader("Please log in.")
    st.button("Log in with Google", 
              on_click=st_login)
