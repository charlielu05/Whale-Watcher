terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = ">= 2.12"
    }
    random = {
      source  = "hashicorp/random"
      version = ">= 2.0"
    }
  }
  backend "s3" {
    region  = "ap-southeast-2"
    encrypt = "true"
    bucket = "terraform-states-clu"
    key = "chronicler/test_lambda"
  }
}