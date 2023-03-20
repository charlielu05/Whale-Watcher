# from https://github.com/getmoto/moto/blob/master/tests/test_ecr/test_ecr_helpers.py
import hashlib
import random
from w2 import ImageDetails
import json

def _generate_random_sha():
    random_sha = hashlib.sha256(f"{random.randint(0,100)}".encode("utf-8")).hexdigest()
    return f"sha256:{random_sha}"

def _create_image_layers(n):
    layers = []
    for _ in range(n):
        layers.append(
            {
                "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
                "size": random.randint(100, 1000),
                "digest": _generate_random_sha(),
            }
        )
    return layers

def _create_image_digest(layers):
    layer_digests = "".join([layer["digest"] for layer in layers])
    summed_digest = hashlib.sha256(f"{layer_digests}".encode("utf-8")).hexdigest()
    return f"sha256:{summed_digest}"

def _create_image_manifest(image_digest=None):
    layers = _create_image_layers(5)
    if image_digest is None:
        image_digest = _create_image_digest(layers)
    return {
        "schemaVersion": 2,
        "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
        "config": {
            "mediaType": "application/vnd.docker.container.image.v1+json",
            "size": sum([layer["size"] for layer in layers]),
            "digest": image_digest,
        },
        "layers": layers,
    }

def _create_mock_repo(ecr_client, 
                      repo_name:str = 'test-repo', 
                      image_tag:str = 'latest'):
    
    ecr_client.create_repository(repositoryName=repo_name)
    image_digest = ecr_client.put_image(
        repositoryName=repo_name,
        imageManifest=json.dumps(_create_image_manifest()),
        imageTag="latest",
    )["image"]["imageId"]["imageDigest"]
    
    return (repo_name, image_digest, image_tag)
    