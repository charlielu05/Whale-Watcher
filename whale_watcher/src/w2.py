
import boto3
from typing import List
import re 


def return_ecr_client(region_name='ap-southeast-2')->boto3.client:
    # boto3 configuration
    session = boto3.session.Session(region_name=region_name)

    return session.client("ecr")

def return_lambda_client(region_name='ap-southeast-2')->boto3.client:
    # boto3 configuration
    session = boto3.session.Session(region_name=region_name)

    return session.client("lambda")

def get_image_scan_findings(ecr_client:boto3.client, 
                            repository_name:str,
                            image_digest:str, 
                            image_tag:str)->dict:
    
    return  ecr_client.describe_image_scan_findings(
        repositoryName = repository_name,
        imageId = {
            'imageDigest' : image_digest,
            'imageTag' : image_tag
        }
    )

def get_severity_counts_from_scan(image_scan_findings:dict)->dict:
    
    return image_scan_findings.get('imageScanFindings').get('findingSeverityCounts')

def parse_imageid(functions_details:dict):
    # given functions code details containing ImageUri and ResolvedImageUri
    # parse out the repository name, imageTag and imageDigest
    temp_list = []
    
    for details_dict in functions_details:
        for key, val in details_dict.items():
            temp_list.append({key : 
                                {'image_digest': val.get('ResolvedImageUri'),
                                 'image_tag': val.get('ImageUri')
                                }
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
    
    # regex string
    regex_image_tag = ':.+'
    regex_image_sha = ':.+'
    
    image_scan_finding:dict = get_image_scan_findings(ecr_client, 
                                                      REPOSITORY_NAME,
                                                      IMAGE_DIGEST,
                                                      IMAGE_TAG)

    severity_counts = get_severity_counts_from_scan(image_scan_finding)

    lambda_functions:dict = get_lambda_functions(lambda_client)
    
    functions_name:List[str] = get_list_functions_name(lambda_functions)
    
    functions_code_details = get_lambda_image(lambda_client, functions_name)
    
    image_digest_and_tag = parse_imageid(functions_code_details)
    