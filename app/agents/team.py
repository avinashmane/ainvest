import streamlit as st
from agno.team import Team
from lib.model import model
from lib.database import db
from box import box_from_file
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

@tool(tool_hooks=[logger_hook],)                       # Hook to run before and after execution
def list_transactions(email: str) -> dict:
    """
    Use this function to get the buys sell transaction stocks/assets along with quantity and buy price.
    Amount should be reversed in sign and called cost basis. Total Value amd Gain at bottom.
    Args:
        email: str -> Email of the person

    Returns:
        pd.DataFrame: Returning dataframe.
    """
    pf = User(email).list_transactions()
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
def buy_sell_transaction(email: str, 
                         buy_or_sell: str, 
                         ticker: str, 
                         quantity: int, 
                         price: float, 
                         amount: float) -> str:
    """
    Use this function to buy or sell ticker symbol of share or fund for specific quantity.  
    Price is taken from yfinance tools. Date is always taken from today.

    arg:
    * email: email id of the person buying
    * buy_or_sell: str - Buy or Sell with exact text
    * ticker: str - symbol that can be found on yahoo finance
    * Quantity: int - normally multiple of 100 but allow only a positive number .
    * price: float - has to be lastPrice
    * amount: float -  arithmetic multiplicate of above quantity and price

    Returns:
        str: transaction confirmation (in format oftimestamp) or error message
    """
    user=User(email)
    if price*quantity != amount:
        err='Exception(Quanty {}* price {}!= amount {})'.format(quantity,price,amount)
        print( err )
        return f'Sorry error in transaction {err}'    
    
    if buy_or_sell=='Sell': 
        quantity=-quantity
    
    try:
        ret = user.add_transaction(ticker,quantity,price,price*quantity)
        return ret
    except:
        return 'Sorry functionaliy not yet implemented {}'

@tool(tool_hooks=[logger_hook],)
def get_profile(email) -> dict:
    """
    Use this function to profile for the email, including cash balance.

    Args:
        email: str -> Email of the person

    Returns:
        Profile -> Dict : Exchanges, currency and balances
    """
    profile=User(email).get_profile()
    return profile

# --- Team Initialization (in Session State) ---
# with open() as f:
cfg=box_from_file("app/texts/agent_team_config.yaml")

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
            list_transactions,
            buy_sell_transaction,
            get_profile,
            get_my_email, ],
        description= cfg.description,
        instructions= cfg.instructions,
        # success_criteria="The user's query has been thoroughly answered with information from all relevant specialists.",
        enable_agentic_memory=True,      # Coordinator maintains context
        share_member_interactions=True, # Members see previous member interactions in context
        show_members_responses=False,     # Don't show raw member responses in final output
        markdown=True,
        # show_tool_calls=True,            # Don't show raw tool calls in final output
        
        add_history_to_context=True,         # Pass history between coordinator/members
        num_history_runs=5 # Limit history passed
    )
