# app.py
import os
import streamlit as st
from dotenv import load_dotenv
import time
from pprint import pformat
from typing import Iterator # Added for type hinting

# Agno Imports
from agno.agent import Agent, RunOutput # Added for type hinting
from agno.team import Team
from lib.model import model
from lib.database import db

from agents.search import search_agent
# from app.crawler import crawler_agent
# from app.email import email_agent
# from app.github import github_agent
# from app.hackernews import hackernews_agent
# from app.youtube import youtube_agent

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

# --- Agent Definitions ---
# Define specialized agents
from agents.general import general_agent
from agents.search import search_agent
from agents.yfinance import yfinance_agent

# --- Team Initialization (in Session State) ---
def initialize_team():
    """Initializes or re-initializes the investment team."""
    return Team(
        name="InvestmentAssistantTeam",
        role="coordinate",
        model=model,
        db=db,
        members=[
            search_agent,
            # crawler_agent,
            # youtube_agent,
            # email_agent,
            # github_agent,
            # hackernews_agent,
            yfinance_agent,
            general_agent
        ],
        description="Coordinates specialists to handle investment inquiry tasks.",
        instructions=[
            "Analyze the query and assign tasks to specialists.",
            "Delegate based on task type:",
            "- Web searches: InternetSearcher",
            # "- URL content: WebCrawler",
            # "- YouTube videos: YouTubeAnalyst",
            # "- Emails: EmailAssistant",
            # "- GitHub queries: GitHubResearcher",
            # "- Hacker News: HackerNewsMonitor",
            "- Finance new, Stock quote, Share information: yfinance"
            "- General or synthesis: GeneralAssistant",
            "Synthesize responses into a cohesive answer.",
            "Cite sources and maintain clarity.",
            "Always check previous conversations in memory before responding.",
            "When asked about previous information or to recall something mentioned before, refer to your memory of past interactions.",
            "Use all relevant information from memory when answering follow-up questions."
        ],
        # success_criteria="The user's query has been thoroughly answered with information from all relevant specialists.",
        enable_agentic_memory=True,      # Coordinator maintains context
        share_member_interactions=True, # Members see previous member interactions in context
        show_members_responses=False,     # Don't show raw member responses in final output
        markdown=True,
        # show_tool_calls=False,            # Don't show raw tool calls in final output
        
        add_history_to_context=True,         # Pass history between coordinator/members
        num_history_runs=5 # Limit history passed
    )

if "team" not in st.session_state:
    st.session_state.team = initialize_team()


# --- Streamlit UI ---
st.title("🤑 Investment Assistant Team")
st.markdown("""
This team coordinates specialists to assist with:
- 🔍 Web searches
- 📈 Stock Market
- 🧠 General queries and synthesis
""")
# - 🌐 Website content extraction
# - 📺 YouTube video analysis
# - 📧 Email drafting/sending
# - 💻 GitHub repository exploration
# - 📰 Hacker News trends

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
user_query = st.chat_input("Ask the investment team anything...")

if user_query:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_query)

    # Display team response (Streaming)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            # Use stream=True for the team run
            response_stream: RunOutput = st.session_state.team.run(user_query, stream=True) # Ensure type hint Iterator[RunResponse]

            for chunk in response_stream:
                # Check if content is present and a string
                if chunk.content and isinstance(chunk.content, str):
                    full_response += chunk.content
                    message_placeholder.markdown(full_response + "▌") # Add cursor effect
            message_placeholder.markdown(full_response) # Final response without cursor

            # Update memory debug information for display
            if hasattr(st.session_state.team, 'memory') and hasattr(st.session_state.team.memory, 'messages'):
                try:
                    # Extract only role and content safely
                    st.session_state.memory_dump = [
                        {"role": m.role if hasattr(m, 'role') else 'unknown',
                         "content": m.content if hasattr(m, 'content') else str(m)}
                        for m in st.session_state.team.memory.messages
                    ]
                except Exception as e:
                    st.session_state.memory_dump = f"Error accessing memory messages: {str(e)}"
            else:
                st.session_state.memory_dump = "Team memory object or messages not found/accessible."

            # Add the final assistant response to Streamlit's chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.exception(e) # Show full traceback in Streamlit console for debugging
            error_message = f"An error occurred: {str(e)}\n\nPlease check your API keys and tool configurations. Try rephrasing your query."
            st.error(error_message)
            message_placeholder.markdown(f"⚠️ {error_message}")
            # Add error message to history for context
            st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})

# --- Sidebar ---
with st.sidebar:
    st.title("Team Settings")

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
