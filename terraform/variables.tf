variable "aws_region" {
  type = string
  default = "eu-central-1"
}

variable "s3_bucket_name" {
  type = string
  default = "s3_bucket_name"
}

variable "ingestion_iam_user" {
  type = string
  default = "ingestion_iam_user"
}

variable "ingestion_iam_policy" {
  type = string
  default = "ingestion_iam_user"
}