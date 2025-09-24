import streamlit as st
from pprint import pformat
import os
import time

def sidebar(initialize_team):
    st.title("Team Settings")
    tabs=st.tabs(['Settings','About'],width='stretch')
    with tabs[0]:
        # Memory debug section
        if st.checkbox("Show Team Memory Contents", value=False):
            st.subheader("Team Memory Contents (Debug)")
            if "memory_dump" in st.session_state:
                try:
                    # Use pformat for potentially complex structures
                    memory_str = pformat(st.session_state.memory_dump, indent=2, width=80)
                    st.code(memory_str, language="python")
                except Exception as format_e:
                    st.warning(f"Could not format memory dump: {format_e}")
                    st.json(st.session_state.memory_dump) # Fallback to json
            else:
                st.info("No memory contents to display yet. Interact with the team first.")

        st.markdown(f"**Session ID**: `{st.session_state.team_session_id}`")
        st.markdown(f"**Model**: {os.getenv("MODEL")}")

        # Memory information
        st.subheader("Team Memory")
        st.markdown("This team remembers conversations within this browser session. Clearing the chat resets the memory.")

        # Clear chat button
        if st.button("Clear Chat & Reset Team"):
            st.session_state.messages = []
            st.session_state.team_session_id = f"streamlit-team-session-{int(time.time())}" # New ID for clarity
            st.session_state.team = initialize_team() # Re-initialize the team to reset its state
            if "memory_dump" in st.session_state:
                del st.session_state.memory_dump # Clear the dump
            st.rerun()
        
        #--- Log ---
        with st.container(width=300):
            flds="event content".split()
            for i,e in enumerate(st.session_state.log) :
                try: st.write(f"{i:2d}: "+" : ".join([getattr(e,f) for f in flds]))
                except: pass

    with tabs[1]:
        st.title("About")
        st.markdown("""
        **How it works**:
        - The team coordinator analyzes your query.
        - Tasks are delegated to specialists (Searcher, YahooFinance, General).
        - Responses are synthesized into a final answer.
        - Team memory retains context within this session.

        **Example queries**:
        - "What are the latest AI breakthroughs?"
        - "Crawl agno.com and summarize the homepage."
        - "Summarize the YouTube video: https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        - "Draft an email to contact@example.com introducing our research services."
        - "Find popular AI repositories on GitHub created in the last month."
        - "What's trending on Hacker News today?"
        - "What was the first question I asked you?" (tests memory)
        """)
