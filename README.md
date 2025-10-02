# AINVEST


# Host
# AINVEST

AINVEST (Investment Assistant) is a Streamlit-based web app that provides an AI-powered assistant and a simple investment game. The app integrates several helper agents (using Agno) and uses Google Firestore for persistence in places. It includes UI components (login, profile, sidebar, quote) and small analytics charts.

Hosts / Demos
----------------
- https://ainvest.streamlit.app
- https://ainvest-1008690560612.us-central1.run.app/
- https://ainvest.forthe.life

Key features
------------
- Streamlit UI with multi-page layout under `app/`
- Agent-based tooling under `agents/` (Agno integrations)
- Firestore integration (via `google-cloud-firestore`) for persistence
- Uses `yfinance` and plotting libraries for financial data and charts

Quick start
-----------
Prerequisites

- Python 3.12+
- pip (or a virtual environment tool)

Install dependencies (recommended inside a virtualenv):

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

Run the Streamlit app locally:

```bash
streamlit run app/Home.py
```

Or use the small runner in `main.py` (this expects an Agent OS available in the environment):

```bash
python main.py
```

Environment variables
---------------------
Create a `.env` file in the project root or set environment variables in your shell. The app checks for at least the following key:

- `GOOGLE_API_KEY` — required for some features

Other optional keys the project references (configure as needed):

- `OPENROUTER_API_KEY`, `EMAIL_FROM`, `EMAIL_TO`, `GITHUB_ACCESS_TOKEN`, `RESEND_API_KEY`

Project layout
--------------

- `app/` — Streamlit pages and components (main UI, pages, components, and lib helpers)
- `agents/` — bot/agent modules and integrations (Agno tools, yfinance helpers, email, github, etc.)
- `charts/` — static chart images used in the UI
- `lib/` — small helper libraries (database, models, yf wrappers)
- `tests/` — unit tests for core library functions

Development
-----------
- Run tests with pytest (inside the venv):

```bash
pytest -q
```

- Linting and type checks can be added with your preferred tools (ruff, mypy, black).

Contributing
------------
Open issues and pull requests are welcome. Keep changes small, and add tests for new functionality when possible.

License
-------
This project currently does not specify a license in the repo. Add a `LICENSE` file if you want to make the license explicit.

Contact
-------
For questions, open an issue in the repository.
