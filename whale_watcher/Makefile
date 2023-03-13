SHELL := /bin/bash

python-env:
	python -m venv venv 
	source ./venv/bin/activate 
	pip-compile ./src/requirements.in
	pip install --upgrade pip 
	pip install -r ./src/requirements.txt

python-run: python-env
	. venv/bin/activate
	python ./sync.py

.PHONY: *
.ONESHELL:
.SILENT: