import streamlit as st
from box import Box
from lib.user import User
from components.login import is_logged_in
# import sys
# if '..' in sys.path: sys.path.append('..')
# print(sys.path)
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
    if is_logged_in():
        user=init_state('user',User(st.user.email))
        st.session_state.profile =Box(user.get_profile())
    else:
        user=User(None)
        st.session_state.profile =Box()
    print("init_page():" , #f"st.session_state.profile {st.session_state.profile}")
        getattr(state,"user","user not defined"))
    # for transactions
    init_state('ticker',None)
    init_state('quote',Box())
        

init_page()

