FROM docker.io/bitnami/jupyterhub:3.1.1-debian-11-r11

# Install the function's dependencies using file requirements.txt
# from your project folder

# Copy function code
COPY ./app/handler.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "handler.handler" ] 