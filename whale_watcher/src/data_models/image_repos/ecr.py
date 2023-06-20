import boto3
from typing import List
from datetime import datetime
from src.data_models.ww_data_models import ImageDetail, ResourceDetail
from pydantic import BaseModel

class ecrImage(ImageDetail):
    imageDigest: str
    imageTag: str
    repoName: str
    
    def get_image_scan_findings(self)->dict:
        # get the ECR scan result for a single repository
        return  self._return_ecr_client().describe_image_scan_findings(
            repositoryName = self.repoName,
            imageId = {
                'imageDigest' : self.imageDigest,
                'imageTag' : self.imageTag
            }
        )

class ecrRepo(BaseModel):
    repoName:str
    createdAt:datetime
    repositoryArn:str
    repositoryUri:str
    
    def return_images(self):
        return [ecrImage(imageDigest=image.get('imageDigest'),
                         imageTag=image.get('imageTag'),
                         repoName=self.repoName)
                for image
                in self.list_repo_images.get('imageIds')]
    
    @property
    def _return_ecr_client(self)->boto3.client:
        session = boto3.session.Session(region_name=self.region)
        return session.client("ecr")
    
    @property
    def list_repo_images(self):
        return self._return_ecr_client.list_images(repositoryName=self.repoName)
    
class Ecr(BaseModel):
    region:str
   
    def return_ecr_repos(self):
        return [ecrRepo(repoName=repo.get('repositoryName'),
                        createdAt=repo.get('createdAt'),
                        repositoryArn=repo.get('repositoryArn'),
                        repositoryUri=repo.get('repositoryUri'))
                for repo
                in self.list_ecr_repos]
    
    @property
    def _return_ecr_client(self)->boto3.client:
        session = boto3.session.Session(region_name=self.region)
        return session.client("ecr")

    @property
    def list_ecr_repos(self)->List[str]:
        return self._return_ecr_client.describe_repositories().get('repositories')

    
    
