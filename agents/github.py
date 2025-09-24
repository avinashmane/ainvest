from app import model


from agno.agent import Agent
from agno.tools.github import GithubTools


github_agent = Agent(
    name="GitHubResearcher",
    model=model,
    tools=[GithubTools(access_token=GITHUB_ACCESS_TOKEN)], # Pass required args
    add_history_to_messages=True,
    num_history_responses=3,
    description="Explores GitHub repositories.",
    instructions=[
        "Search repositories or list pull requests based on user query.",
        "Include repository URLs and summarize findings concisely."
    ],
    markdown=True,
    exponential_backoff=True,
    add_datetime_to_instructions=True
)