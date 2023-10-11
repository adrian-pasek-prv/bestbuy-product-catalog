output "users" {
  value = {
    "${aws_iam_user.data_engineer_iam_user.name}": {
      "arn": aws_iam_user.data_engineer_iam_user.arn,
      "access_key": aws_iam_access_key.data_engineer_iam_user_access_key.id,
      "access_secret": aws_iam_access_key.data_engineer_iam_user_access_key.secret
    }
  }
  sensitive = true
}

output "variables" {
  value = {
    "aws_region": var.aws_region,
    "s3_bucket_name": aws_s3_bucket.s3_bucket.id,
    "data_loader_role_arn": aws_iam_role.data_loader_role.arn
  }
}