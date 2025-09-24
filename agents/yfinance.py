from lib.model import model
from lib.database import db

from agno.agent import Agent
from agno.tools.yfinance import YFinanceTools


yfinance_agent = Agent(
	name="YFinanceAnalyst",
	model=model,
    db=db,
	tools=[YFinanceTools()],
	add_history_to_context=True,
	num_history_runs=3,
	description="Fetches financial data and summaries using yfinance.",
	instructions=[
		"Use YFinanceAnalyst to retrieve ticker data, historical prices, and basic metrics.",
		"When returning numbers, include the ticker and timeframe used."
	],
	markdown=True,
	exponential_backoff=True
)

