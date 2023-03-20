SHELL := /bin/bash

start-api:
	. venv/bin/activate
	cd ./src
	uvicorn w2:app --reload
	
python-env:
	python -m venv venv 
	. venv/bin/activate 
	pip-compile ./src/requirements.in
	pip install --upgrade pip 
	pip install -r ./src/requirements.txt

python-run: python-env
	. venv/bin/activate
	python ./sync.py

python-test:
	. venv/bin/activate
	python -m pytest

.PHONY: *
.ONESHELL:
.SILENT: