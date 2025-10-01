import streamlit as st
from pydash import capitalize
def show_profile():
    if 'profile' in st.session_state:
        table="|Profile||\n|--|--|"
        for k,v in st.session_state.profile.items():
            table+=f"\n| {capitalize(k)} | **{v}** |"
        st.write(table)