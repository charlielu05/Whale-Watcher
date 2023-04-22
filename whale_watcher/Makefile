SHELL := /bin/bash

start-api:
	. .ww/bin/activate
	cd ./src
	uvicorn w2:app --reload
	
python-env:
	python -m venv .ww 
	. .ww/bin/activate 
	pip-compile ./src/requirements.in
	pip install --upgrade pip 
	pip install -r ./src/requirements.txt

python-test:
	. .ww/bin/activate
	python -m pytest

start-local-dynamodb:
	docker-compose up -d

stop-local-dynamodb:
	docker-compose down

python-dev: start-local-dynamodb
	. .ww/bin/activate
	python -i ./src/ww.py

llm-dev: 
	source .env.sh
	. .ww/bin/activate
	python -i ./src/llm.py

.PHONY: *
.ONESHELL:
.SILENT: