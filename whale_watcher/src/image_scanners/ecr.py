# AWS ECR specific data models and implementations
from dataclasses import dataclass
from ww_data_models import *
from typing import List
import boto3

@dataclass
class ECR_Findings:
    name: str
    description: str

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

def return_ecr_client(region_name='ap-southeast-2')->boto3.client:
    # boto3 configuration
    session = boto3.session.Session(region_name=region_name)

    return session.client("ecr")

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