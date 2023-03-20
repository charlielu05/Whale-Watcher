SHELL := /bin/bash

aws-public-ecr-login:
	aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws

docker-ecr-login:
	aws ecr get-login-password --region ap-southeast-2 | \
	docker login --username AWS --password-stdin $$(aws sts get-caller-identity | jq -r '.Account').dkr.ecr.ap-southeast-2.amazonaws.com

python-env:
	python -m venv venv 
	. venv/bin/activate ; pip install --upgrade pip ; pip install -r ./requirements.txt

python-run: python-env
	. venv/bin/activate
	python ./sync.py

images-sync: docker-ecr-login python-run
	jq -cr '.[]' temp.json | while read item; do 
	# Add tags
		jq -cr '.new_tags | .[]' <<< "$$item" | while read tag; do 
			img_name="$$(jq -r .destination <<< "$$item")":"$$tag" 
			echo $$img_name 
			tgd_img_src="$$(jq -r .source <<< "$$item")":"$$tag" 
			echo $$tgd_img_src 
			tgd_img_dest="$$(jq -r '.destination_url' <<< "$$item")":"$$tag" 
			echo $$tgd_img_dest 

			docker pull $$tgd_img_src 
			docker tag $$tgd_img_src $$tgd_img_dest 
			docker push $$tgd_img_dest 
		done 
	done

tf-init:
	cd terraform
	terraform init

tf-apply:
	cd terraform
	terraform apply

.PHONY: *
.ONESHELL:
.SILENT: