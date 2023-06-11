import re 
from whale_watcher.src.data_models.ww_data_models import AppDetails, ImageDetail
from typing import Callable
from functools import partial

# regex string
regex_image_tag = '(?<=:).*'
regex_image_sha = '(?<=@).*'
regex_image_repo = '(?<=\/)(.*?)(?=\:)'

def regex_filter(string_chars:str, regex_pattern:str):
    return re.search(regex_pattern, string_chars).group()

# set regex function partially and pass to parse function
tag_regex_filter = partial(regex_filter, regex_pattern = regex_image_tag)
sha_regex_filter = partial(regex_filter, regex_pattern = regex_image_sha)
repo_name_regex_filter = partial(regex_filter, regex_pattern = regex_image_repo)

def construct_app_details(functions_details:dict, 
                  tag_regex_function:Callable, 
                  repo_name_regex_function:Callable,
                  sha_regex_function:Callable):
    # given functions code details containing ImageUri and ResolvedImageUri
    # parse out the repository name, imageTag and imageDigest
    app_list = []
    
    for function_details in functions_details:
        for key, val in function_details.items():
            app_list.append(AppDetails(
                                resourceDetail = key,
                                imageDetail = ImageDetail(
                                                repoName = repo_name_regex_function(val.get('ImageUri')),
                                                imageDigest = sha_regex_function(val.get('ResolvedImageUri')),
                                                imageTag = tag_regex_function(val.get('ImageUri')) 
                                                )
                                )
                            )
    
    return app_list


def get_app_details(image_details:dict):
    return construct_app_details(image_details, 
                                tag_regex_filter,
                                repo_name_regex_filter,
                                sha_regex_filter)