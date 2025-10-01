from lib.model import get_model
model=get_model()


from agno.agent import Agent
from agno.tools.youtube import YouTubeTools


youtube_agent = Agent(
    name="YouTubeAnalyst",
    model=model,
    tools=[YouTubeTools()],
    add_history_to_messages=True,
    num_history_responses=3,
    description="Analyzes YouTube videos.",
    instructions=[
        "Extract captions and metadata for YouTube URLs.",
        "Summarize key points and include the video URL."
    ],
    markdown=True,
    exponential_backoff=True
)