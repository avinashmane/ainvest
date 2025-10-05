import streamlit as st
from components.login import is_logged_in
from page_common import state

#----- UI ----
from components.sidebar import sidebar

with st.sidebar:
    sidebar()

if is_logged_in():
    if ('avinashmane' in st.user.email) or ( state.profile.get('admin') ):
        state.admin=st.toggle(":blue[Admin mode]") 

if ('admin' in state) and state.admin:
    from components.admin import admin
    admin()
    
else:
    st.header("Information")
    st.subheader("Data Security and Privacy")
    st.subheader("Terms")