from fastapi import FastAPI
from data_models.image_repos.ecr import Ecr
from data_models.resources.aws_lambda import awsLambdaService
import boto3 

app = FastAPI()
                  
@app.get('/')
def main():
    pass

REGION = 'ap-southeast-2'

def image_scan_finding(image_uri:str, resolved_image_uri:str):
    session = boto3.session.Session(region_name=REGION).client('ecr')
    # need reponame, imagedigest and image tag

    # return session.describe_image_scan_findings(
    
    # )

if __name__ == "__main__":
    ecr = Ecr(region='ap-southeast-2')
    ecr_repos = ecr.return_ecr_repos() 
    # ecr_images ={repo.return_images()
    #             for repo
    #             in ecr_repos}
    ecr_images = {}
    for repo in ecr_repos:
        ecr_images = ecr_images | repo.return_images()

    # findings for specific ecr image
    # findings = ecr_images.get('bitnami/jupyterhub')[0].return_image_finding()
    
    # look through applications (lambda)
    aws_lambda = awsLambdaService(region='ap-southeast-2')
    lambda_functions = aws_lambda.return_lambda_functions()
    
    # image for specific lambda function
    lambda_detail = lambda_functions[0].lambda_code_detail()

