VENV_BIN=/home/avinash/ainvest/.venv/bin
IMAGE=ainvest
SERVICE_NAME=ainvest
IMAGE_NAME=us-central1-docker.pkg.dev/run-pix/runpix/ainvest

dev:
	dotenv run uv run streamlit run app/Home.py --server.headless true
dev_:
	dotenv run ./entrypoint.sh 

test: test_database test_user
	@echo test
test_%:
	$(VENV_BIN)/python -m unittest tests/lib/test_$*.py


build:
	docker build . -t ${IMAGE_NAME}

run_cmd:
	gcloud config set run/region us-central1

run: d-stop d-rm d-run

d-run:
	docker run \
		-p 8080:8501 --name ${SERVICE_NAME} \
		--env-file .env_docker --env PYTHONPATH="/app"\
		${IMAGE_NAME} 
# --env PYTHONPATH=".:./app" \
		
d-stop:
	docker stop ${SERVICE_NAME}

d-rm:
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
        --env-vars-file=./.env \
        --allow-unauthenticated \
        --description="Misc services"\
		--region=us-central1	