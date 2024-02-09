# Break circular dependency and define a precalculated Snowflake role ARN
locals {
  precalculated_snowflake_role_arn = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${join("-", [var.project, var.snowflake_iam_role])}"
}

# Create IAM policy for Snowflake S3 access
resource "aws_iam_policy" "snowflake_iam_policy" {
  name = join("-", [var.project, var.snowflake_iam_policy])

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
              "s3:GetObject",
              "s3:GetObjectVersion"
            ],
            "Resource": "${aws_s3_bucket.s3_bucket.arn}/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:GetBucketLocation"
            ],
            "Resource": aws_s3_bucket.s3_bucket.arn,
            "Condition": {
                "StringLike": {
                    "s3:prefix": [
                        "*"
                    ]
                }
            }
        }
    ]
})
}

# Create storage integration between AWS S3 and Snowflake
resource "snowflake_storage_integration" "snowflake_storage_integration" {
    name = join("-", [var.project, "storage-integration"])
    comment = "Storage integration between AWS S3 and Snowflake"
    type = "EXTERNAL_STAGE"
    enabled = true
    storage_allowed_locations = ["s3://${aws_s3_bucket.s3_bucket.id}/"]
    storage_provider = "S3"
    storage_aws_role_arn = "${local.precalculated_snowflake_role_arn}"
}


# Create Snowflake role based on the results of storage integration
resource "aws_iam_role" "snowflake_iam_role" {
  name = join("-", [var.project, var.snowflake_iam_role])
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          AWS = "${snowflake_storage_integration.snowflake_storage_integration.storage_aws_iam_user_arn}"
        }
        Condition = {
            StringEquals = {
            "sts:ExternalId" = "${snowflake_storage_integration.snowflake_storage_integration.storage_aws_external_id}"
          }
        }
      }
    ]
  })

  depends_on = [snowflake_storage_integration.snowflake_storage_integration]
}

# Attach snowflake_iam_policy to snowflake-iam-role
resource "aws_iam_role_policy_attachment" "snowflake_iam_policy_attachment" {
  policy_arn = aws_iam_policy.snowflake_iam_policy.arn
  role       = aws_iam_role.snowflake_iam_role.name
}





