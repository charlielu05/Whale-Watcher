terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
  backend "s3" {
    bucket = "terraform-states-clu"
    key    = "whale_watcher/docker_image_sync"
    region  = "ap-southeast-2"
    encrypt = "true"
  }

}
