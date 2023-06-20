from data_models.image_repos.ecr import ecrImage, Ecr, ecrRepo
from functools import reduce
import json
from test_helpers import _create_image_manifest, _create_mock_repo


def test_ecrimages_from_boto(ecr_client):
    mock_repo_name = 'test-repo'
    mock_image_tag = 'latest'
    
    response, digest, tag = _create_mock_repo(ecr_client, mock_repo_name, mock_image_tag)

    ecr = Ecr(region='us-east-1')
    ecr_repos = ecr.return_ecr_repos()
    
    assert reduce(lambda x,y: x and y, [isinstance(ecr_repo, ecrRepo)
            for ecr_repo
            in ecr_repos])
    
    

