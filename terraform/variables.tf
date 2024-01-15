variable "aws_region" {
  type = string
  default = "eu-central-1"
}

variable "project" {
  type = string
  default = "bestbuy-product-catalog"
}

variable "s3_bucket_name" {
  type = string
  default = "s3_bucket_name"
}

variable "data_engineer_iam_user" {
  type = string
  default = "data-engineer"
}

variable "data_loader_iam_role" {
  type = string
  default = "data-loader"
}

variable "data_loader_iam_policy" {
  type = string
  default = "s3-access-policy"
}