VENV_BIN=/home/avinash/ainvest/.venv/bin
APP_PATH=/home/avinash/ainvest/app
IMAGE=ainvest
PROJECT_ID=ainvest
REGION=us-central1
SERVICE_NAME=ainvest
IMAGE_NAME=${REGION}-docker.pkg.dev/run-pix/runpix/ainvest
export PYTHONPATH = ${APP_PATH}

.PHONY: frontend, build, d-push, d-deploy



dev: srv

streamlit:
	dotenv run uv run streamlit run app/Home.py --server.headless true
dev_:
	dotenv run sh ./entrypoint.sh 

srv:
	uv run dotenv run uvicorn app.server.main:app \
	--host 0.0.0.0 --port 8080 \
	--reload --log-level debug
	# --workers 2 



ui:
	cd frontend && pnpm dev

ui-build:
	cd frontend && pnpm build	

test:
	dotenv run uv run pytest tests/ -v

test_lib:
	dotenv run uv run pytest tests/lib/ -v

test_server:
	dotenv run uv run pytest tests/server/ -v

test_%:
	dotenv run uv run pytest tests/ -k "$*" -v

build:
	docker build . -t ${IMAGE_NAME}

run_cmd:
	gcloud config set run/region us-central1

run: d-stop d-rm d-run

d-run:
	make d-rm || true ;\
	docker run -it\
		-p 8080:8080 --name ${SERVICE_NAME} \
		--env-file .env_docker --env PYTHONPATH="/app"\
		${IMAGE_NAME} 
# --env PYTHONPATH=".:./app" \

d-run-streamlit:
	docker run \
		-p 8080:8501 --name ${SERVICE_NAME} \
		--env-file .env_docker --env PYTHONPATH="/app"\
		${IMAGE_NAME} 

d-bash:
	docker rm ${SERVICE_NAME}-bash || true ; docker run -it -p 8080:8501 --name ${SERVICE_NAME}-bash \
		--env-file .env_docker --env PYTHONPATH="/app"\
		${IMAGE_NAME} bash

d-stop:
	docker stop ${SERVICE_NAME}

d-rm:
	make d-stop || true ;\
	docker rm ${SERVICE_NAME}	

d-push:
	docker push ${IMAGE_NAME}:latest

d-deploy:
	#to be written #
	@echo gcloud auth login --no-launch-browser
	
	gcloud run deploy ${SERVICE_NAME} --image ${IMAGE_NAME} \
        --cpu=1 \
		--max-instances=10 --memory=512M\
        --min-instances=0\
        --allow-unauthenticated \
        --description="AInvest services"\
		--env-vars-file=./.env_docker.yaml \
        --project="${PROJECT_ID}" \
		--region=${REGION}	

# Update environment variables
d-update:
	gcloud run services update ${SERVICE_NAME} \
		--project="${PROJECT_ID}" \
        --env-vars-file=./.env_docker.yaml \
		--region=${REGION}		

d-full-deploy: 
	make ui-build
	make build
	make d-push
	make d-deploy
