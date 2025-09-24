from app.app import model


from agno.agent import Agent
from agno.tools.resend import ResendTools


email_agent = Agent(
    name="EmailAssistant",
    model=model,
    tools=[ResendTools(from_email=EMAIL_FROM, api_key=RESEND_API_KEY)], # Pass required args
    add_history_to_messages=True,
    num_history_responses=3,
    description="Sends emails professionally.",
    instructions=[
        "send professional emails based on context or user request.",
        f"Default recipient is {EMAIL_TO}, but use recipient specified in the query if provided.",
        "Include URLs and links clearly.",
        "Ensure the tone is professional and courteous."
    ],
    markdown=True,
    exponential_backoff=True
)