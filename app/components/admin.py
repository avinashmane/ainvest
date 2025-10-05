import streamlit as st
import pandas as pd
from pydash import omit
from lib.user import User, default_profile, Accounts
from copy import copy

state=st.session_state

def admin():
        
    st.subheader('Admin')
    def cb(x=None):
        print(x)
        pass

    def call_menu(email):
        if email is None: exit
        menu=st.selectbox('Action',["Update","Imitate",'Delete'])
        st.write(email)
        if len(sel_users:=users.loc[users['id'] == email]):
            row=sel_users.iloc[0,:]
            if menu=='Update':
                update_selected_row(row)
            elif menu=='Imitate':
                if st.button(f'Really change to {email}?'):
                    state.email=email
                    state.user=User(email)
                    state.profile=state.user.get_profile()
                    print(state)             
                    print(state.user.__dict__)             
                    st.rerun()
            else:
                st.write("Not implemented")

    def update_selected_selection(selection):
        if len(selection['rows']):
            return update_selected_row(users.iloc[selection['rows'][0]])

    def update_selected_row(row):
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

    @st.cache_data
    def get_users():
        return Accounts.list_users()

    with st.spinner():
        users=get_users()
        sel_email=st.selectbox('Email',index =None,options=users.id.to_list())
        
        call_menu(sel_email)
    