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
    
    # Data Security and Privacy
    try:
        with open("app/texts/data_security_and_privacy.md", "r", encoding="utf-8") as f:
            st.markdown(f.read())
    except Exception as e:
        st.error(f"Could not load data security text: {e}")

    st.markdown("---")
    "Terms of Usage"
    try:
        with open("app/texts/terms_of_usage.md", "r", encoding="utf-8") as f:
            st.markdown(f.read())
    except Exception as e:
        st.error(f"Could not load terms of usage text: {e}")