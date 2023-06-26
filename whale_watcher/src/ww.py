from fastapi import FastAPI
from databases.db import DynamoDB
from boto3.dynamodb.types import TypeDeserializer
from data_models.image_repos.ecr import Ecr

app = FastAPI()
                  
@app.get('/')
def main():
    pass

if __name__ == "__main__":
    ecr = Ecr(region='ap-southeast-2')
    ecr_repos = ecr.return_ecr_repos()
    
    
    