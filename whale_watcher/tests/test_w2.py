from w2 import get_image_scan_findings, ImageDetails
import json
from test_helpers import _create_image_manifest, _create_mock_repo


def test_get_image_scan_findings(ecr_client):
    mock_repo_name = 'test-repo'
    mock_image_tag = 'latest'
    
    name, digest, tag = _create_mock_repo(ecr_client, mock_repo_name, mock_image_tag)
    mock_image = ImageDetails(repoName = name,
                            imageDigest = digest,
                            imageTag = tag) 
    ecr_client.start_image_scan(repositoryName=mock_repo_name, imageId={"imageTag": mock_image_tag})

    # when
    response = get_image_scan_findings(ecr_client, mock_image)

    # then
    assert response["repositoryName"] == mock_repo_name
