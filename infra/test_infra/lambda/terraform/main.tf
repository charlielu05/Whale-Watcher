data "aws_region" "current" {}

data "aws_caller_identity" "this" {}

data "aws_ecr_authorization_token" "token" {}

provider "aws" {
  region = "ap-southeast-2"

  # Make it faster by skipping something
  skip_get_ec2_platforms      = true
  skip_metadata_api_check     = true
  skip_region_validation      = true
  skip_credentials_validation = true
  skip_requesting_account_id  = true
}

module "lambda_function_from_container_image_one"{
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${random_pet.first.id}-lambda-from-container-image"
  description   = "My awesome lambda function from container image"

  create_package = false

  ##################
  # Container Image
  ##################
  image_uri     = "004279011638.dkr.ecr.ap-southeast-2.amazonaws.com/bitnami/jupyterhub:3.1.1-debian-11-r11"
  package_type  = "Image"
  architectures = ["x86_64"]
}

module "lambda_function_from_container_image_two"{
  source = "terraform-aws-modules/lambda/aws"

  function_name = "${random_pet.second.id}-lambda-from-container-image"
  description   = "My awesome lambda function from container image"

  create_package = false

  ##################
  # Container Image
  ##################
  image_uri     = "004279011638.dkr.ecr.ap-southeast-2.amazonaws.com/bitnami/nginx:1.23.3-debian-11-r33"
  package_type  = "Image"
  architectures = ["x86_64"]
}

resource "random_pet" "first" {
  length = 2
}

resource "random_pet" "second" {
  length = 2
}