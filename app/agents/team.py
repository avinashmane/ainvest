import streamlit as st
from agno.team import Team
from lib.model import model
from lib.database import db

# --- Agent Definitions ---
# Define specialized agents
from agents.general import general_agent
from agents.search import search_agent
from agents.yfinance import yfinance_agent
from agents.search import search_agent
from lib.user import User
from agno.tools import tool
import pandas as pd
from components.login import is_logged_in, get_logged_email
from typing import Any, Callable, Dict

def logger_hook(function_name: str, function_call: Callable, arguments: Dict[str, Any]):
    """Hook function that wraps the tool execution"""
    print(f"About to call {function_name} with arguments: {arguments}")
    result = function_call(**arguments)
    print(f"Function call completed with result: {result}")
    return result

@tool(
    name="get_portfolio",                # Custom name for the tool (otherwise the function name is used)
    description="to show the portfolio or stocks/assets you hold.",  # Custom description (otherwise the function docstring is used)
    # stop_after_tool_call=True,                      # Return the result immediately after the tool call and stop the agent
    tool_hooks=[logger_hook],                       # Hook to run before and after execution
    # requires_confirmation=True,                     # Requires user confirmation before execution
    # cache_results=True,                             # Enable caching of results
    # cache_dir="/tmp/agno_cache",                    # Custom cache directory
    # cache_ttl=3600                                  # Cache TTL in seconds (1 hour)
)
def get_portfolio(email: str) -> dict:
    """
    Use this function to get the stocks/assets held portfolio along with quantity and buy price.

    Args:
        email: str -> Email of the person

    Returns:
        pd.DataFrame: Returning dataframe.
    """
    pf = User(email).get_portfolio()
    return pf.to_dict()

@tool(tool_hooks=[logger_hook],)
def get_my_email() -> str:
    """
    Use this function to get email id of the logged in person.

    Returns:
        str: Email id
    """
    email=get_logged_email()
    return email

@tool(tool_hooks=[logger_hook],)
def get_profile(email) -> dict:
    """
    Use this function to profile for the email, including cash balance.

    Args:
        email: str -> Email of the person

    Returns:
        Profile -> Dict : Exchanges, currency and balances
    """
    email=User(email).get_profile()
    print(email)
    return email

# --- Team Initialization (in Session State) ---
def initialize_team():
    """Initializes or re-initializes the investment team."""
    st.session_state.log = []

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
        tools=[
            get_portfolio, 
            get_profile,
            get_my_email, ],
        description="Coordinates specialists to handle investment inquiry tasks.",
        instructions=[
            "Analyze the query and assign tasks to specialists.",
            "Delegate based on task type:",
            "- Web searches: InternetSearcher",
            "answer about logged in user, the transactions, portfolio etc."
            # "- URL content: WebCrawler",
            # "- YouTube videos: YouTubeAnalyst",
            # "- Emails: EmailAssistant",
            # "- GitHub queries: GitHubResearcher",
            # "- Hacker News: HackerNewsMonitor",
            "- Finance new, Stock quote, Share information: yfinance"
            "- General or chart: GeneralAssistant",
            "if file path is program starting with charts, please show it as image in the markdown",
            "Positive sentiment to be shown in green and negative with red",
            "Colored text and background colors for text, using the syntax :color[text to be colored] "
            "Show ammouts with 0 digits after deciman, and show thousans separator for all numbers.",
            "Cite sources and maintain clarity.",
            "Always check previous conversations in memory before responding.",
            "total value = value of portfolio holding + cash balance"
            "When asked about previous information or to recall something mentioned before, refer to your memory of past interactions.",
            "Use all relevant information from memory when answering follow-up questions."
        ],
        # success_criteria="The user's query has been thoroughly answered with information from all relevant specialists.",
        enable_agentic_memory=True,      # Coordinator maintains context
        share_member_interactions=True, # Members see previous member interactions in context
        show_members_responses=False,     # Don't show raw member responses in final output
        markdown=True,
        # show_tool_calls=True,            # Don't show raw tool calls in final output
        
        add_history_to_context=True,         # Pass history between coordinator/members
        num_history_runs=5 # Limit history passed
    )
