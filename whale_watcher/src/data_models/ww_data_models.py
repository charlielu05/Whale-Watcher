from pydantic import BaseModel

class ImageDetail(BaseModel, frozen=True):
    repoName: str

class ResourceDetail(BaseModel, frozen=True):
    resourceType: str
    resourceName: str
    resourceArn: str

class AppDetails(BaseModel, frozen=True):
    resourceDetail: ResourceDetail
    imageDetail: ImageDetail
    
    