# app.py
import os
import streamlit as st
from dotenv import load_dotenv
import time
from rich import print
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
    st.session_state.log = []


# --- Sidebar ---
import yaml
from textwrap import dedent
from components.sidebar import sidebar
with st.sidebar:
    sidebar(initialize_team)

# --- Streamlit UI ---
st.title("🤑 Investment Assistant Team")
with st.container(horizontal=True):
    samples=yaml.safe_load(dedent("""
    - Latest news on Microsoft along with negative sentiment italics in markdown
    - Get me current price of Reliance
    - 5 day chart for Reliance
    """))
    for s in samples: st.code(s) 


# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Handle user input
user_query = st.chat_input("Ask the investment team anything...")

if user_query:
    print(user_query)
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

            for i,run_event in enumerate(response_stream):
                # Check if content is present and a string
                # print(f"{i}> ",run_event)
                if run_event.content and isinstance(run_event.content, str):
                    if run_event.event in ['RunContent','TeamRun-Content']:
                        full_response += run_event.content
                        message_placeholder.markdown(full_response + "▌") # Add cursor effect
                    else:
                        if hasattr(st.session_state,'log'): st.session_state.log.append(run_event)
                        else: st.session_state.log=[run_event]

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


