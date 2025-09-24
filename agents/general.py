from lib.model import model

from agno.agent import Agent

# Generalist Agent (No KB in this version)
general_agent = Agent(
    name="GeneralAssistant",
    model=model,
    add_history_to_context=True,
    num_history_runs=5, # Can access slightly more history
    description="Handles general queries and synthesizes information from specialists.",
    instructions=[
        "Answer general questions or combine specialist inputs.",
        "If specialists provide information, synthesize it clearly.",
        "If a query doesn't fit other specialists, attempt to answer directly.",
        "Maintain a professional tone."
    ],
    markdown=True,
    exponential_backoff=True
)