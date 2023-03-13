output "input" {
    value = local.input
}

output "repo_urls" {
    value = {
        for repo_attributes in aws_ecr_repository.image_repo : repo_attributes.name => repo_attributes.repository_url
    }
}