# app.py
import os
import streamlit as st
# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()
from page_common import state
import time
from typing import Iterator # Added for type hinting
from agents.team import initialize_team
from components.login import is_logged_in
from components.stock import show_stock
# --- Configuration ---


# Check for essential API keys
# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# EMAIL_FROM = os.getenv("EMAIL_FROM")
# EMAIL_TO = os.getenv("EMAIL_TO") # Default recipient
# GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")
# RESEND_API_KEY = os.getenv("RESEND_API_KEY") # ResendTools requires this

# Simple validation for required keys
required_keys = {
    'GOOGLE_API_KEY': os.getenv("GOOGLE_API_KEY")
    # "OPENROUTER_API_KEY": OPENROUTER_API_KEY,
    # "EMAIL_FROM": EMAIL_FROM,
    # "EMAIL_TO": EMAIL_TO,
    # "GITHUB_ACCESS_TOKEN": GITHUB_ACCESS_TOKEN,
    # "RESEND_API_KEY": RESEND_API_KEY
}

missing_keys = [name for name, key in required_keys.items() if not key]

if missing_keys:
    st.error(f"Missing required environment variables: {', '.join(missing_keys)}. Please set them in your .env file or system environment.")
    st.stop() # Stop execution if keys are missing

# Set Streamlit page configuration
st.set_page_config(
    page_title="Investment Assistant Team",
    page_icon="📈",
    layout="wide"
)

# --- Session State Initialization ---
# Initialize team_session_id for this specific browser session
if "team_session_id" not in st.session_state:
    st.session_state.team_session_id = f"streamlit-team-session-{int(time.time())}"
# Initialize chat message history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "team" not in st.session_state:
    st.session_state.team = initialize_team()



# --- Sidebar ---
from components.sidebar import sidebar

with st.sidebar:
    sidebar()

# --- Streamlit UI ---
st.write("# Welcome to AInvest!")

st.markdown(
    f"""
    AInvest is investing with AI. It is investment game challenge, where you are awarded 1 Crore Rupees and 
    You need to make most money by end of each month, and each year.

    Slow and steady win the race!""")

if is_logged_in():
    with st.container(horizontal=True):
        st.write(f"**{st.user.name}** check your ") 
        st.page_link("pages/1_📈_Portfolio.py", label="portfolio", icon="📈")
else:
    st.write('**👈 Please Login**')

st.markdown(      
    """### Investment Assistant aka AInvest:
    
    This is also AI bot for you to do intelligent conversations on investements, new, statistics 
    and most importantly performs
    
    """)

ticker=st.text_input("Ticker Symbol",value='^NSEI')
show_stock(ticker)