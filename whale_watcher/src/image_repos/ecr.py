import boto3
from typing import List
from ..ww_data_models import ImageDetail

def return_ecr_client(region_name='ap-southeast-2')->boto3.client:
    # boto3 configuration
    session = boto3.session.Session(region_name=region_name)

    return session.client("ecr")

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