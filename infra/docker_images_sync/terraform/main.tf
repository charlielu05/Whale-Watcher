locals {
    input = yamldecode(file("../image-list.yml"))
}

resource "aws_ecr_repository" "image_repo" {
    for_each = local.input
    name = each.value["destination"]
    force_delete = true
}