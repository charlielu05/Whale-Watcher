import boto3
from typing import List
from datetime import datetime
from data_models.ww_data_models import ImageDetail
from pydantic import BaseModel

class Ecr(BaseModel):
    region:str
   
    def return_ecr_repos(self):
        return [ecrRepo(repoName=repo.get('repositoryName'),
                        createdAt=repo.get('createdAt'),
                        repositoryArn=repo.get('repositoryArn'),
                        repositoryUri=repo.get('repositoryUri'),
                        region=self.region)
                for repo
                in self.list_ecr_repos]
    
    @property
    def _return_ecr_client(self)->boto3.client:
        session = boto3.session.Session(region_name=self.region)
        return session.client("ecr")

    @property
    def list_ecr_repos(self)->List[str]:
        return self._return_ecr_client.describe_repositories().get('repositories')

class ecrRepo(BaseModel):
    repoName: str
    createdAt: datetime
    repositoryArn: str
    repositoryUri: str
    region: str
    
    @property
    def _return_ecr_client(self)->boto3.client:
        session = boto3.session.Session(region_name=self.region)
        return session.client("ecr")
    
    @property
    def list_repo_images(self):
        return self._return_ecr_client.list_images(repositoryName=self.repoName).get('imageIds')
    
    def return_images(self):
        images = {}
        for image in self.list_repo_images:
            images = images | {f"004279011638.dkr.ecr.{self.region}.amazonaws.com/{self.repoName}@{image.get('imageDigest')}":
                    ecrImage(imageDigest=image.get('imageDigest'),
                            imageTag=image.get('imageTag'),
                            repoName=self.repoName,
                            region=self.region)}
        return images
    
class ecrImage(ImageDetail):
    imageDigest: str
    imageTag: str
    repoName: str
    region: str
    
    @property
    def _return_ecr_client(self)->boto3.client:
        session = boto3.session.Session(region_name=self.region)
        return session.client("ecr")
    
    def return_image_finding(self)->dict:
        return self.get_image_scan_finding(ecr_client = self._return_ecr_client,
                                            repository_name = self.repoName,
                                            image_id = {
                                                'imageDigest' : self.imageDigest,
                                                'imageTag' : self.imageTag}
                                            )
    
    @staticmethod
    def get_image_scan_finding(ecr_client, repository_name:str, image_id:dict)->dict:
        # get the ECR scan result for a single repository
        return  ecr_client.describe_image_scan_findings(
                    repositoryName = repository_name,
                    imageId = image_id    
            ).get('imageScanFindings')