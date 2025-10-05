import os
import streamlit as st
from lib.user import User
state=st.session_state

def is_logged_in():
    if 'is_logged_in' in st.user:
        if st.user.is_logged_in:
            return True
        else:
            return False
        
def show_login():
    if not is_logged_in():
        login_screen()
    else:
        logged_in()
        call_menu()

def login_set_state(email=None):
        logged_user=getattr(st.user,'email')
        print("Logged,state email >>>",logged_user,email)
        if email:
            state.email=email
        else:
            state.email=logged_user
        state.user=User(state.email)
        state.profile=state.user.get_profile()
        state.proxy_login= state.email != st.user.email
 

def logged_in():

    try:
        login_set_state(state.email if 'email' in state else None)
        state.user.update() #**state.profile    

        if state.get('proxy_login'):
            st.write(f"""Email: {state.email}""")
            st.write(f":red[logged in user: {st.user.email}]")
            if st.button('Reset'):
                login_set_state()
                st.rerun()        
        else:
            st.markdown(f'<img src="{st.user.picture}" style="border-radius:100%" with="80px"/>',
                                unsafe_allow_html=True)
            st.header(f"Welcome {st.user.name}!")
            st.write(f"""Email: {state.email}""")            
    except TypeError:
        register()
    except Exception as e:
        print(f"Error logged_in(): {e!r}")

    

    
    # Hide the deploy button

def st_login(x='login'):
    if x=='logout':
        state.user=None
        state.email=None
        state.profile={}
        return st.logout()
    else:
        return st.login(provider='google')

def login_screen():
    st.subheader("This app is needs a login and it's free.")
    st.button("Log in with Google", 
              on_click=st_login)
    
def register():
    st.write("To receive investment funds:")
    if st.button("Register") and (not 'profile' in state):
        # with st.spinner():
        state.user.create()
        state.profile=state.user.get_profile()
        st.rerun()

def call_menu():
    menu_options=["Logout","Feedback",'Session Trace',"Withdraw", "Delete Account"]
    menu=state.get('menu')
    state.menu=st.selectbox("Menu",options=menu_options,
                            index=menu_options.index(menu) if menu else None)
    
    if menu=="Logout":
        if st.button("Really Log out?"):
            st_login("logout")
    elif menu=='Feedback':
        st.write(f"Write your feedback here {os.getenv('FEEDBACK_URL')}")
    elif menu=='Session Trace':
        st.write(f"st.session_state")
        st.write(st.session_state)
    else:
        st.write('Not implemented.  Please be patient.')
    # st.rerun()

from lib import read_file
def please_register():
    # st.image("app/assets/cheque.avif",
    #          width=300)
    st.write(read_file("app/texts/please_register.md"))
    

