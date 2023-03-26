from fastapi import FastAPI
import boto3
from typing import List,Callable
import re 
from functools import partial
from pydantic import BaseModel

# regex string
regex_image_tag = '(?<=:).*'
regex_image_sha = '(?<=@).*'
regex_image_repo = '(?<=\/)(.*?)(?=\:)'

app = FastAPI()

class ImageDetail(BaseModel, frozen=True):
    repoName: str
    imageDigest: str
    imageTag: str

class ResourceDetail(BaseModel, frozen=True):
    resourceType: str
    resourceName: str
    resourceArn: str

class AppDetails(BaseModel, frozen=True):
    resourceDetail: ResourceDetail
    imageDetail: ImageDetail
    
def return_ecr_client(region_name='ap-southeast-2')->boto3.client:
    # boto3 configuration
    session = boto3.session.Session(region_name=region_name)

    return session.client("ecr")

def return_lambda_client(region_name='ap-southeast-2')->boto3.client:
    # boto3 configuration
    session = boto3.session.Session(region_name=region_name)

    return session.client("lambda")

def get_image_repos(ecr_client:boto3.client)->List[str]:
    return ecr_client.describe_repositories().get('repositories')

def get_image_scan_findings(image_detail:ImageDetail)->dict:
    ecr_client = return_ecr_client()
    # get the ECR scan result for a single repository
    return  ecr_client.describe_image_scan_findings(
        repositoryName = image_detail.repoName,
        imageId = {
            'imageDigest' : image_detail.imageDigest,
            'imageTag' : image_detail.imageTag
        }
    )
    
def regex_filter(string_chars:str, regex_pattern:str):
    return re.search(regex_pattern, string_chars).group()
 
def construct_app_details(functions_details:dict, 
                  tag_regex_function:Callable, 
                  repo_name_regex_function:Callable,
                  sha_regex_function:Callable):
    # given functions code details containing ImageUri and ResolvedImageUri
    # parse out the repository name, imageTag and imageDigest
    app_list = []
    
    for function_details in functions_details:
        for key, val in function_details.items():
            app_list.append(AppDetails(
                                resourceDetail = key,
                                imageDetail = ImageDetail(
                                                repoName = repo_name_regex_function(val.get('ImageUri')),
                                                imageDigest = sha_regex_function(val.get('ResolvedImageUri')),
                                                imageTag = tag_regex_function(val.get('ImageUri')) 
                                                )
                                )
                            )
    
    return app_list

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

def get_severity_counts_from_scan(image_scan_findings:dict)->dict:
    return image_scan_findings.get('imageScanFindings').get('findingSeverityCounts')

def map_severity(app_detail:AppDetails):
    
    return {app_detail.resourceDetail.resourceArn: get_severity_counts_from_scan(
                    get_image_scan_findings(
                        app_detail.imageDetail
                    )
    )}
    
def get_severity_counts(app_details:List[AppDetails])->dict:
    # given the repository_detail, get the severity count for that image
    return list(map(map_severity, app_details))
    
@app.post('/image/scanFinding/')    
def get_image_scan_findings(image_detail:ImageDetail)->dict:
    # get the ECR scan result for a single repository
    ecr_client = return_ecr_client()
    
    return  ecr_client.describe_image_scan_findings(
        repositoryName = image_detail.repoName,
        imageId = {
            'imageDigest' : image_detail.imageDigest,
            'imageTag' : image_detail.imageTag
        }
    )
    
@app.get("/lambda")
def get_lambda_functions():
    lambda_client = return_lambda_client()
    
    return lambda_client.list_functions()

@app.get('/')
def main():
    lambda_functions = get_lambda_functions()
    lambda_functions_details: List[AppDetails] = get_lambda_app_details(lambda_functions)
    functions_code_details = get_lambda_image(lambda_functions_details)
    
    # set regex function partially and pass to parse function
    tag_regex_filter = partial(regex_filter, regex_pattern = regex_image_tag)
    sha_regex_filter = partial(regex_filter, regex_pattern = regex_image_sha)
    repo_name_regex_filter = partial(regex_filter, regex_pattern = regex_image_repo)
    
    app_details: List["dict[ResourceDetail, ImageDetail]"] = construct_app_details(functions_code_details, 
                                         tag_regex_filter,
                                         repo_name_regex_filter,
                                         sha_regex_filter)
    
    images_severity_counts = get_severity_counts(app_details)
    
    return images_severity_counts

if __name__ == "__main__":
    main()