from lib.model import get_model
model=get_model()

from agno.agent import Agent
from agno.tools.hackernews import HackerNewsTools


hackernews_agent = Agent(
    name="HackerNewsMonitor",
    model=model,
    tools=[HackerNewsTools()],
    add_history_to_messages=True,
    num_history_responses=3,
    description="Tracks Hacker News trends.",
    instructions=[
        "Fetch top stories using get_top_hackernews_stories.",
        "Summarize discussions and include story URLs."
    ],
    markdown=True,
    exponential_backoff=True,
    add_datetime_to_instructions=True
)