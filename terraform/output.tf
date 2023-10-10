output "secrets" {
  value = {
    "data-engineer-user": {
      "name": aws_iam_user.data_engineer_iam_user.name,
      "access_key": aws_iam_access_key.data_engineer_iam_user_access_key.id,
      "access_secret": aws_iam_access_key.data_engineer_iam_user_access_key.secret
    }
  }
  sensitive = true
}

output "variables" {
  value = {
    "s3_bucket_name": aws_s3_bucket.s3_bucket.id,
    "data_loader_role_arn": aws_iam_role.data_loader_role.arn
  }
}