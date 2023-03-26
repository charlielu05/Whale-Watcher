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

python-test:
	. venv/bin/activate
	python -m pytest

python-debug:
	. venv/bin/activate
	python -i ./src/w2.py

.PHONY: *
.ONESHELL:
.SILENT: