import streamlit as st
from box import Box
from lib.user import User

import locale
locale.setlocale(locale.LC_ALL, '')  

state=st.session_state

def init_state(f,default=[]):
    if not f in st.session_state: 
        print(f"init {f}")
        st.session_state[f]=default
    return st.session_state[f]

user={}

def init_page(): 
    init_state('profile',{})
    if st.user.is_logged_in:
        user=init_state('user',User(st.user.email))
        st.session_state.profile =Box(user.get_profile())
    else:
        user=User(None)
        st.session_state.profile =Box()
    print(f"st.session_state.profile {st.session_state.profile}")

    # for transactions
    init_state('ticker',None)
    init_state('quote',Box())

init_page()

with st.sidebar:
    # st.write(st.session_state)
    # from app.components.login import show_login
    # show_login()
    if st.user.is_logged_in:
        st.page_link("./Home.py",label="Login here")
