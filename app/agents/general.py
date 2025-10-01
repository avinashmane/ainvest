from lib.model import model
from lib.database import db
from agno.agent import Agent
from agno.tools.visualization import VisualizationTools

# Generalist Agent (No KB in this version)
general_agent = Agent(
    name="GeneralAssistant",
    model=model,
    db=db,
    add_history_to_context=True,
    tools=[VisualizationTools()],
    num_history_runs=5, # Can access slightly more history
    description="Handles general queries and synthesizes information from specialists.",
    instructions=[
        "Answer general questions or combine specialist inputs.",
        "return the file name for the chart/graph/plots generated in the expected result",
        "Produce charts for stock price or key stats by default in area mode.",
        "If a query doesn't fit other specialists, attempt to answer directly.",
        "Maintain a professional tone."
    ],
    markdown=True,
    exponential_backoff=True
)