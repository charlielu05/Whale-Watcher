from data_models.image_repos.ecr import ecrImage, Ecr, ecrRepo
from functools import reduce
import json
from test_helpers import _create_image_manifest, _create_mock_repo


def test_ecrRepo(ecr_client):
    mock_repo_name = 'test-repo'
    mock_image_tag = 'latest'
    
    response, digest, tag = _create_mock_repo(ecr_client, mock_repo_name, mock_image_tag)

    ecr = Ecr(region='us-east-1')
    ecr_repos = ecr.return_ecr_repos()
    
    assert reduce(lambda x,y: x and y, [isinstance(ecr_repo, ecrRepo)
            for ecr_repo
            in ecr_repos])

def test_ecrImages(ecr_client):
    mock_repo_name = 'test-repo'
    mock_image_tag = 'latest'
    
    response, digest, tag = _create_mock_repo(ecr_client, mock_repo_name, mock_image_tag)
    
    # start test
    ecr = Ecr(region='us-east-1')
    ecr_repos = ecr.return_ecr_repos()
    #ecr_repo_images = ecr_repos[]
    assert ecr_repos[0].repoName == mock_repo_name
    
    ecr_testRepo_images = ecr_repos[0].return_images()
    
    assert reduce(lambda x,y: x and y, [isinstance(ecr_image, ecrImage)
            for ecr_image
            in ecr_testRepo_images])
    
    # mock image scan
    ecr_client.start_image_scan(repositoryName=mock_repo_name, imageId={"imageTag": mock_image_tag})
    
    response =  ecr_testRepo_images[0].get_image_scan_findings()
    
    assert response["repositoryName"] == mock_repo_name
    assert response["imageId"] == {"imageDigest": digest, "imageTag": tag}
    assert response["imageScanStatus"] == {"status": "COMPLETE", "description": "The scan was completed successfully."}

