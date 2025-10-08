from lib.gsheets import open_url,get_named_range

import streamlit as st

state=st.session_state






def show_pvt():
    st.write("# Private portfolio")
    state.pvt_profile=state.user.profile['pvt']
    # st.write(state.pvt_profile)

    open_pct_pf()

# Open a sheet from a spreadsheet in one go
def open_pct_pf():
    wks=open_url(state.pvt_profile['url'])
    # st.write(wks.worksheets())
    # st.write(wks.list_named_ranges())
    # st.write(wks.named_range)
    state.pvt_profile['portfolio']= get_named_range("stockSumm")
    st.write(state.pvt_profile['portfolio'])
