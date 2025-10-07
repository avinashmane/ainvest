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

def get_state(f,default=None):
    if f in st.session_state: 
        return st.session_state[f]
    else:
        return default

user={}

def init_page(): 
    init_state('email',None)
    init_state('profile',{})
    if is_logged_in():
        user=init_state('user',User(st.user.email))
        try: profile=user.get_profile()
        except:profile={}
        st.session_state.profile =Box()
    else:
        user=User(None)
        st.session_state.profile =Box()
    print("init_page():" , #f"st.session_state.profile {st.session_state.profile}")
        getattr(state,"user","No state.user. User not logged"))
    # for transactions
    init_state('ticker',None)
    init_state('quote',Box())
    init_state('transaction',Box({'status':''}))
    init_state('log',Box())
    init_state('menu','Logout')

init_page()

