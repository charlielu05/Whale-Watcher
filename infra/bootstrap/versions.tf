terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
  backend "s3" {
    region  = "ap-southeast-2"
    encrypt = "true"
    bucket = "terraform-states-clu"
    key = "chronicler/bootstrap"
  }
}