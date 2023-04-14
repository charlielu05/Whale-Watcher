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

python-debug:
	. .ww/bin/activate
	python -i ./src/w2.py

.PHONY: *
.ONESHELL:
.SILENT: