# Define external ID that is needed to establish a trust relationship betweeen Snowflake and AWS
locals {
  external_id = 5122345
  precalculated_snowflake_role_arn = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${aws_iam_role.snowflake_iam_role.name}"
}

# Create IAM user for Snowflake
resource "aws_iam_user" "snowflake_iam_user" {
    name = join("-", [var.project, var.snowflake_iam_user])
}

# Create IAM policy for Snowflake
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

# Create Snowflake role
resource "aws_iam_role" "snowflake_iam_role" {
  name = join("-", [var.project, var.snowflake_iam_role])
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:user/${aws_iam_user.snowflake_iam_user.name}"
        }
        Condition = {
            StringEquals = {
            "sts:ExternalId" = local.external_id
          }
        }
      }
    ]
  })
}

# Attach data-loader policy to data-loader role
resource "aws_iam_role_policy_attachment" "snowflake_policy_attachment" {
  policy_arn = aws_iam_policy.snowflake_iam_policy.arn
  role       = aws_iam_role.snowflake_iam_role.name
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