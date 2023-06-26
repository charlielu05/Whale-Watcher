from typing import List
from whale_watcher.src.data_models.ww_data_models import AppDetails, ResourceDetail
import boto3
from pydantic import BaseModel

class awsLambdaService(BaseModel):
    pass

class awsLambda(BaseModel):
    pass
    
def return_lambda_client(region_name='ap-southeast-2')->boto3.client:
    # boto3 configuration
    session = boto3.session.Session(region_name=region_name)

    return session.client("lambda")

def get_lambda_app_details(lambda_functions:dict)->List[ResourceDetail]:
    return [ResourceDetail(
                resourceType = 'lambda',
                resourceName = function.get('FunctionName'),
                resourceArn = function.get('FunctionArn')
                )
            for function
            in lambda_functions.get('Functions')]
    
def get_lambda_image(lambda_app_details:List[AppDetails])->dict:
    lambda_client = return_lambda_client()
    
    return [{function_detail: lambda_client.get_function(
                                                    FunctionName = function_detail.resourceName).get('Code')}
            for function_detail
            in lambda_app_details]

def get_lambda_functions():
    lambda_client = return_lambda_client()
    
    return lambda_client.list_functions()

def return_lambda_image_details():
    lambda_functions = get_lambda_functions()
    lambda_functions_details: List[AppDetails] = get_lambda_app_details(lambda_functions)
    functions_code_details = get_lambda_image(lambda_functions_details)
    
    return functions_code_details