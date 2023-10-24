output "airflow_roles" {
  value = {
    "aws-${aws_iam_role.data_loader_role.name}": {
      "conn_type": "aws",
      "login": aws_iam_access_key.data_engineer_iam_user_access_key.id,
      "password": aws_iam_access_key.data_engineer_iam_user_access_key.secret,
      "extra": {
        "role_arn": aws_iam_role.data_loader_role.arn,
        "region_name": var.aws_region
      },
    }
  }
  sensitive = true
}

output "airflow_variables" {
  value = {
    "aws_region": var.aws_region,
    "s3_bucket_name": aws_s3_bucket.s3_bucket.id,
    "environment": var.environment
  }
}