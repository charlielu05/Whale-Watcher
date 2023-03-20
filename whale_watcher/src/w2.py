
import boto3
from typing import List,Callable
import re 
from functools import partial
from dataclasses import dataclass

@dataclass
class ImageDetails:
    repoName: str
    imageDigest: str
    imageTag: str

@dataclass
class AppDetails:
    applicationType: str
    applicationName: str
    
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
    
def get_image_scan_findings(ecr_client:boto3.client, 
                            image_detail:ImageDetails)->dict:
    # get the ECR scan result for a single repository
    return  ecr_client.describe_image_scan_findings(
        repositoryName = image_detail.repoName,
        imageId = {
            'imageDigest' : image_detail.imageDigest,
            'imageTag' : image_detail.imageTag
        }
    )

def get_severity_counts_from_scan(image_scan_findings:dict)->dict:
    return image_scan_findings.get('imageScanFindings').get('findingSeverityCounts')

def get_severity_counts_from_image_details(ecr_client, image_details:ImageDetails)->dict:
    # given the repository_detail, get the severity count for that image
    return {image_details.repoName: get_severity_counts_from_scan(get_image_scan_findings(ecr_client, image_details))}
    
def regex_filter(string_chars:str, regex_pattern:str):
    return re.search(regex_pattern, string_chars).group()
 
def parse_imageid(functions_details:dict, 
                  tag_regex_function:Callable, 
                  repo_name_regex_function:Callable,
                  sha_regex_function:Callable):
    # given functions code details containing ImageUri and ResolvedImageUri
    # parse out the repository name, imageTag and imageDigest
    temp_list = []
    
    for function_details in functions_details:
        for key, val in function_details.items():
            temp_list.append({key: 
                                ImageDetails(repoName = repo_name_regex_function(val.get('ImageUri')),
                                             imageDigest = sha_regex_function(val.get('ResolvedImageUri')),
                                             imageTag = tag_regex_function(val.get('ImageUri')) 
                                             )
                            })
    
    return temp_list

def get_lambda_functions(lambda_client:boto3.client)->dict:
    return lambda_client.list_functions()

def get_list_functions_name(lambda_functions:dict)->List[str]:
    return [function.get('FunctionName')
            for function
            in lambda_functions.get('Functions')]
    
def get_lambda_image(lambda_client:boto3.client, 
                     lambda_functions:List[str])->dict:
    return [{function_name: lambda_client.get_function(
                                                    FunctionName = function_name).get('Code')}
            for function_name
            in lambda_functions]
    
if __name__ == "__main__":
    ecr_client = return_ecr_client()
    lambda_client = return_lambda_client()
    REPOSITORY_NAME = 'bitnami/jupyterhub'
    IMAGE_TAG = '3.1.1-debian-11-r11'
    IMAGE_DIGEST = 'sha256:4af0b7dd95312ccf1ab4e50465dcf870c1de9e99ae8ff40026eba2397bd45d9e'
    TEST_LAMBDA_NAME = 'flying-dogfish-lambda-from-container-image'
    
    image_detail = ImageDetails(repoName = REPOSITORY_NAME,
                                imageTag = IMAGE_TAG,
                                imageDigest =  IMAGE_DIGEST)
    # regex string
    regex_image_tag = '(?<=:).*'
    regex_image_sha = '(?<=@).*'
    regex_image_repo = '(?<=\/)(.*?)(?=\:)'
    
    image_scan_finding:dict = get_image_scan_findings(ecr_client, 
                                                      image_detail)

    severity_counts = get_severity_counts_from_scan(image_scan_finding)

    lambda_functions:dict = get_lambda_functions(lambda_client)
    
    functions_name:List[str] = get_list_functions_name(lambda_functions)
    
    functions_code_details = get_lambda_image(lambda_client, functions_name)
    
    # set regex function partially and pass to parse function
    tag_regex_filter = partial(regex_filter, regex_pattern = regex_image_tag)
    sha_regex_filter = partial(regex_filter, regex_pattern = regex_image_sha)
    repo_name_regex_filter = partial(regex_filter, regex_pattern = regex_image_repo)
    
    images_digest_and_tag = parse_imageid(functions_code_details, 
                                         tag_regex_filter,
                                         repo_name_regex_filter,
                                         sha_regex_filter)
    
    # severity count from image details
    # TODO: fix dict value unpacking into the function
    images_severity_count = [get_severity_counts_from_image_details(ecr_client, list(image.values())[0])
                             for image
                             in images_digest_and_tag]
                             