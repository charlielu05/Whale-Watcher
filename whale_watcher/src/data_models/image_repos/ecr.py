
import boto3
from typing import List
from datetime import datetime
from data_models.ww_data_models import ImageDetail

class ecrImages(ImageDetail):
    createDate: datetime
    imageArn: str
    imageUri: str
    
    @classmethod
    # deserialize the json response from boto ecr describe repositories call
    def from_boto(cls, d:dict):
        image_repos:List[dict[str]] = d.get('repositories')
        
        return [cls(repoName=image.get('repositoryName'),
                    createDate=image.get('createdAt'),
                    imageArn=image.get('repositoryArn'),
                    imageUri=image.get('repositoryUri'))
                for image
                in image_repos]

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
    
    