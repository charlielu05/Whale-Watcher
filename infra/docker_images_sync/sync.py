#!/usr/bin/python3
import yaml
import boto3
from typing import List
import json


def return_ecr_client(region_name='ap-southeast-2')->boto3.client:
    # boto3 configuration
    session = boto3.session.Session(region_name=region_name)

    return session.client("ecr")

def return_desired_images(image_list_filepath:str):
    with open(image_list_filepath, 'r') as input:
        image_dict = yaml.safe_load(input)

    # Convert all tag elements to strings
    for image in image_dict:
        tag_list = image_dict[image]["tags"]
        image_dict[image]["tags"] = [str(tag)
                                    for tag in tag_list]

    return image_dict

def filter_desired_image(desired_images_dict:dict)->dict:
    # transform the structure
    return {desired_images_dict.get(image).get('destination') : desired_images_dict.get(image).get('tags')
            for image
            in desired_images_dict
            }

def filter_aws_ecr_repos(aws_ecr_repos:List[dict]):
    # filter boto results and transform data into the same shape as the desired state YAML file
    return {ecr_image.get('repositoryName'): 
                [image_detail.get('imageTag')
                    for image_detail
                    in ecr_image.get('repositoryImageDetails').get('imageIds')] 
            for ecr_image
            in aws_ecr_repos
            }

def filter_aws_ecr_repo_uri(aws_ecr_repos: List[dict]):
    # filter boto results and transform data into same shape as the desired state YAML file
    return {ecr_image.get('repositoryName'): ecr_image.get('repositoryUri')
            for ecr_image
            in aws_ecr_repos
            }

def return_aws_ecr_repos(ecr_client:boto3.client)->dict:
    # get the entire list of ECR repos that exist
    # return a list of dict with the name of the repo and the details of the repo
    aws_ecr_repos = ecr_client.describe_repositories().get('repositories')
    ecr_images_list = [
                        {'repositoryName': ecr_repo.get('repositoryName'),
                        'repositoryImageDetails': ecr_client.list_images(registryId=ecr_repo.get('registryId'),
                                             repositoryName=ecr_repo.get('repositoryName')),
                        'repositoryUri': ecr_repo.get('repositoryUri')
                        }
                      for ecr_repo
                      in aws_ecr_repos]
    
    return ecr_images_list
    
def return_new_images(aws_images: dict, desired_images: dict):
    return {image_name: set(desired_images.get(image_name)).difference(set(aws_images.get(image_name)))
            for image_name
            in desired_images
            }
    
def create_artifactory_ecr_sync_file(desired_images_dict:dict, new_images_dict:dict, aws_ecr_repos_uri: dict)->json:
    temp_json = []

    for repo_name_str, _ in desired_images_dict.items():
        # actual source name
        source_str:str = desired_images_dict.get(repo_name_str)["source"]
        # actual destination name
        destination_str:str = desired_images_dict.get(repo_name_str).get('destination')

        if new_images_dict.get(destination_str):
            temp_json.append(
                {
                    "source": source_str,
                    "destination": destination_str,
                    "destination_url": aws_ecr_repos_uri.get(destination_str),
                    "new_tags": list(new_images_dict.get(destination_str))
                }
            )

    return temp_json

def write_list_to_json_file(list_obj:list):
    with open("temp.json", "w") as temp_file:
         temp_file.write(json.dumps(list_obj, indent=2))

if __name__ == "__main__":

    ecr_client = return_ecr_client()
    desired_images = return_desired_images('./image-list.yml')
    
    aws_ecr_repos_tags = filter_aws_ecr_repos(return_aws_ecr_repos(ecr_client))
    aws_ecr_repos_uris = filter_aws_ecr_repo_uri(return_aws_ecr_repos(ecr_client))
    desired_images_tags = filter_desired_image(desired_images)

    new_images_tags = return_new_images(aws_ecr_repos_tags, desired_images_tags)

    sync_file_obj = create_artifactory_ecr_sync_file(desired_images, 
                                            new_images_tags, 
                                            aws_ecr_repos_uris)
    
    write_list_to_json_file(sync_file_obj)