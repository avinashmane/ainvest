from lib.model import model
from lib.database import db
from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools


search_agent = Agent(
    name="InternetSearcher",
    model=model,
    db=db,
    tools=[DuckDuckGoTools(enable_search=True, enable_news=False)],
    add_history_to_context=True,
    num_history_runs=3, # Limit history passed to agent
    description="Expert at finding information online.",
    instructions=[
        "Use duckduckgo_search for web queries.",
        "Cite sources with URLs.",
        "Focus on recent, reliable information."
    ],
    add_datetime_to_context=True, # Add time context
    markdown=True,
    exponential_backoff=True # Add robustness
)