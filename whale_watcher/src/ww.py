from fastapi import FastAPI
from data_models.image_repos.ecr import Ecr
from data_models.resources.aws_lambda import awsLambdaService

app = FastAPI()
                  
@app.get('/')
def main():
    pass

if __name__ == "__main__":
    ecr = Ecr(region='ap-southeast-2')
    ecr_repos = ecr.return_ecr_repos() 
    ecr_images ={repo.repoName : repo.return_images()
                for repo
                in ecr_repos}
    # findings for specific ecr image
    findings = ecr_images.get('bitnami/jupyterhub')[0].get_image_scan_findings()
    
    # look through applications (lambda)
    aws_lambda = awsLambdaService(region='ap-southeast-2')
    lambda_functions = aws_lambda.return_lambda_functions()
    
    