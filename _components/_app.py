# app.py
import os
import streamlit as st
from dotenv import load_dotenv
from rich import print
from typing import Iterator # Added for type hinting
from agents.team import initialize_team

# --- Configuration ---
# Load environment variables from .env file
load_dotenv()

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

# with st.sidebar:
#     sidebar(initialize_team)

# --- Streamlit UI ---
# st.set_page_config(
#     page_title="Hello",
#     page_icon="👋",
# )

st.write("# Welcome to Streamlit! 👋")

st.markdown(
    """
    Streamlit is an open-source app framework built specifically for
    Machine Learning and Data Science projects.
    **👈 Select a demo from the sidebar** to see some examples
    of what Streamlit can do!
    ### Want to learn more?
    - Check out [streamlit.io](https://streamlit.io)
    - Jump into our [documentation](https://docs.streamlit.io)
    - Ask a question in our [community
        forums](https://discuss.streamlit.io)
    ### See more complex demos
    - Use a neural net to [analyze the Udacity Self-driving Car Image
        Dataset](https://github.com/streamlit/demo-self-driving)
    - Explore a [New York City rideshare dataset](https://github.com/streamlit/demo-uber-nyc-pickups)
"""
)