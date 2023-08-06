from typing import List
from data_models.ww_data_models import AppDetails, ResourceDetail
import boto3
from pydantic import BaseModel
from datetime import datetime

class awsLambdaService(BaseModel):
    # base AWS lambda service
    region: str

    @property
    def _return_lambda_client(self)->boto3.client:
        session = boto3.session.Session(region_name=self.region)
        return session.client("lambda")

    @property
    def list_lambda_functions(self):
        return self._return_lambda_client.list_functions().get('Functions')

    def return_lambda_functions(self):
        return [awsLambda(functionName=lambda_function.get('FunctionName'),
                          packageType=lambda_function.get('PackageType'),
                          version=lambda_function.get('Version'),
                          LastModified=lambda_function.get('LastModified'),
                          description=lambda_function.get('Description'),
                          role=lambda_function.get('Role'),
                          functonArn=lambda_function.get('FunctionArn'),
                          region=self.region)
                for lambda_function
                in self.list_lambda_functions]
    
class awsLambda(BaseModel):
    functionName: str
    packageType: str
    version: str
    LastModified: datetime
    description: str
    role: str
    region: str
    functonArn: str

    @property
    def _return_lambda_client(self)->boto3.client:
        session = boto3.session.Session(region_name=self.region)
        return session.client("lambda")
    
    def lambda_code_detail(self)->dict:
        return self._return_lambda_client.get_function(
                FunctionName = self.functionName).get('Code')

    def return_lambda_versions(self):
        pass