from data_models.image_repos.ecr import ecrImages
import json
from test_helpers import _create_image_manifest, _create_mock_repo


def test_ecrimages_from_boto(ecr_client):
    mock_repo_name = 'test-repo'
    mock_image_tag = 'latest'
    
    response, digest, tag = _create_mock_repo(ecr_client, mock_repo_name, mock_image_tag)

    mock_image = ecrImages(repoName = response.get('repository').get('repositoryName'),
                           createDate = response.get('repository').get('createdAt'),
                           imageArn = response.get('repository').get('repositoryArn'),
                           imageUri = response.get('repository').get('repositoryUri')) 
    
    ecr_images = ecrImages.from_boto(ecr_client.describe_repositories())
    
    assert ecr_images == [mock_image]

