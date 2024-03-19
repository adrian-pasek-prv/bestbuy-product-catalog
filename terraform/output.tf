output "airflow_roles" {
  value = {
    "${aws_iam_role.data_loader_role.name}": {
      "conn_type": "aws",
      "login": aws_iam_access_key.data_engineer_iam_user_access_key.id,
      "password": aws_iam_access_key.data_engineer_iam_user_access_key.secret,
      "extra": {
        "role_arn": aws_iam_role.data_loader_role.arn,
        "region_name": var.aws_region
      },
    },
    # bestbuy api credentials
    "bestbuy-api": {
      "conn_type": "http",
      "host": "https://api.bestbuy.com/v1/",
    },
    "snowflake": {
      "conn_type": "snowflake",
      "login": snowflake_user.data_loader_user.name,
      "extra": {
        "account": "IS64571",
        "region": var.aws_region,
        "database": snowflake_database.snowflake_raw_db.name
        "private_key_file": "config_ext/data_loader_snowflake_user.pem",
      }
    }
  }
  sensitive = true
}

output "airflow_variables" {
  value = {
    "aws_region": var.aws_region,
    "s3_bucket_name": aws_s3_bucket.s3_bucket.id,
    "project": var.project
  }
}