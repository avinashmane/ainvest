import streamlit as st
from components.login import is_logged_in
from page_common import state

if is_logged_in():
    if 'avinashmane' in st.user.email:
        state.admin=st.toggle(":blue[Admin mode]") 

if ('admin' in state) and state.admin:
    from components.admin import admin
    admin()
    
else:
    st.header("Information")
    st.subheader("Data Security and Privacy")
    st.subheader("Terms")