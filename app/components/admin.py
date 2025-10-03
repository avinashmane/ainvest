import streamlit as st
import pandas as pd
from pydash import omit
from lib.user import User, default_profile, Accounts
from copy import copy

def admin():
        
    st.subheader('Admin')
    def cb(x=None):
        # print(x)
        pass

    def update_selected_row(selection):

        if len(selection['rows']):
            row=users.iloc[selection['rows'][0]]
            id=row['id']
            profile=omit(row,'id')
            cash_balance=st.number_input("Cash Balance",
                                         value=profile['cash_balance'] if profile['cash_balance']>0 else 1_00_00_000) #'cash_balance' in profile
            profile.update(default_profile)
            profile['cash_balance']=cash_balance
            st.write(f"Email: {id}", profile, )

            if st.button("save"):
                with st.spinner():
                    user=User(row['id'])
                    st.write(user.update(**profile))
                    st.rerun()
        pass

    with st.spinner():
        users=Accounts.list_users()
        ret=st.dataframe(users,
                        on_select=cb, 
                        selection_mode="single-row",
                        hide_index =True,
                    )
        # st.write(ret)
        update_selected_row(ret['selection'])