VENV_BIN=/home/avinash/ainvest/.venv/bin

dev:
	dotenv run uv run streamlit run app/Home.py --server.headless true
dev_:
	dotenv run uv run streamlit run app.py --server.headless true

test: test_database test_user
	@echo test
test_%:
	$(VENV_BIN)/python -m unittest tests/lib/test_$*.py
