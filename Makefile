VENV_BIN=/home/avinash/ainvest/.venv/bin
IMAGE=ainvest

dev:
	dotenv run uv run streamlit run app/Home.py --server.headless true
dev_:
	dotenv run ./entrypoint.sh 

test: test_database test_user
	@echo test
test_%:
	$(VENV_BIN)/python -m unittest tests/lib/test_$*.py

build:
	docker build . --tag ${IMAGE}

run: d-stop d-rm d-run

d-run:
	docker run \
		-p 8080:8501 --name ${IMAGE} \
		--env-file .env_docker --env PYTHONPATH="/app"\
		${IMAGE} 
# --env PYTHONPATH=".:./app" \
		
d-stop:
	docker stop ${IMAGE}

d-rm:
	docker rm ${IMAGE}	
