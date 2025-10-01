from lib.model import get_model
model=get_model()


from agno.agent import Agent
from agno.tools.crawl4ai import Crawl4aiTools


crawler_agent = Agent(
    name="WebCrawler",
    model=model,
    tools=[Crawl4aiTools(max_length=None)], # Consider setting a sensible max_length
    add_history_to_messages=True,
    num_history_responses=3,
    description="Extracts content from specific websites.",
    instructions=[
        "Use web_crawler to extract content from provided URLs.",
        "Summarize key points and include the URL."
    ],
    markdown=True,
    exponential_backoff=True
)