import streamlit as st
# from agno.agent import Agent, RunOutput # Added for type hinting
from agno.team import Team
from lib.model import model
from lib.database import db

# --- Agent Definitions ---
# Define specialized agents
from agents.general import general_agent
from agents.search import search_agent
from agents.yfinance import yfinance_agent
from agents.search import search_agent
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
            "- General or chart: GeneralAssistant",
            "if file path is program starting with charts, please show it as image",
            "Positive tentiment to be shown in green and negative with red",
            "Colored text and background colors for text, using the syntax :color[text to be colored] "
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
