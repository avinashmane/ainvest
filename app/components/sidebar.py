import streamlit as st
from pprint import pformat
import os
import time
from components.login import show_login
import pandas as pd
from lib import dict2md_table
state=st.session_state
def sidebar():

    st.title("AInvest")

    show_login()

    if 'profile' in st.session_state and len(state.profile):
        st.subheader("Profile")
        st.write(dict2md_table(state.profile))

def sidebar_assistant(initialize_team=None):

    # --- Session State Initialization ---
    # Initialize team_session_id for this specific browser session
    if "team_session_id" not in st.session_state:
        state.team_session_id = f"streamlit-team-session-{int(time.time())}"
    # Initialize chat message history
    if "messages" not in st.session_state:
        state.messages = []

    if "team" not in st.session_state:
        state.team = initialize_team() if initialize_team else {}

    tabs=st.tabs(['Settings','About'],width='stretch')
    
    with tabs[0]:
        # Memory debug section
        if st.checkbox("Show Team Memory Contents", value=False):
            st.subheader("Team Memory Contents (Debug)")
            if "memory_dump" in st.session_state:
                try:
                    # Use pformat for potentially complex structures
                    memory_str = pformat(state.memory_dump, indent=2, width=80)
                    st.code(memory_str, language="python")
                except Exception as format_e:
                    st.warning(f"Could not format memory dump: {format_e}")
                    st.json(state.memory_dump) # Fallback to json
            else:
                st.info("No memory contents to display yet. Interact with the team first.")

        st.markdown(f"**Session ID**: `{state.team_session_id}`")
        st.markdown(f"**Model**: {os.getenv("MODEL")}")

        # Memory information
        st.subheader("Team Memory")
        st.markdown("This team remembers conversations within this browser session. Clearing the chat resets the memory.")

        # Clear chat button
        if st.button("Clear Chat & Reset Team"):
            state.messages = []
            state.team_session_id = f"streamlit-team-session-{int(time.time())}" # New ID for clarity
            state.team = initialize_team() # Re-initialize the team to reset its state
            if "memory_dump" in st.session_state:
                del state.memory_dump # Clear the dump
            st.rerun()
        
        #--- Log ---
        with st.container(width=300):
            flds="event content".split()
            for i,e in enumerate(state.log) :
                try: st.write(f"{i:2d}: "+" : ".join([getattr(e,f) for f in flds]))
                except: pass

    with tabs[1]:
        st.title("About")
        st.markdown("""
        
        * Version 1.0
                    
        **How it works**:
        - The team coordinator analyzes your query.
        - Tasks are delegated to specialists (Searcher, YahooFinance, General).
        - Responses are synthesized into a final answer.
        - Team memory retains context within this session.

        **Example queries**:
        - "What are the latest AI breakthroughs?"
        - "Crawl agno.com and summarize the homepage."
        - "Summarize the YouTube video: https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        - "What was the first question I asked you?" (tests memory)
                    
        """)

