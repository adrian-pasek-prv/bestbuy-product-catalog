# Create IAM user for ingestion
resource "aws_iam_user" "ingestion_iam_user" {
    name = var.ingestion_iam_user
}
output "ingestion_iam_user" {
  value = aws_iam_user.ingestion_iam_user.arn
}


# Create a key-pair access for ingestion user
resource "aws_iam_access_key" "ingestion_iam_user_access_key" {
    user = aws_iam_user.ingestion_iam_user.name
}
output "ingestion_iam_user_access_key" {
  value = aws_iam_access_key.ingestion_iam_user_access_key.id
}
output "ingestion_iam_user_secret_key" {
  value = aws_iam_access_key.ingestion_iam_user_access_key.secret
  sensitive = true
}


# Create IAM policy for ingestion. Delete, List, Put objects into S3
resource "aws_iam_policy" "ingestion_iam_policy" {
  name        = var.ingestion_iam_policy

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "s3:ListBucket",
          "s3:GetBucketLocation",
        ],
        Effect   = "Allow",
        Resource = aws_s3_bucket.s3_bucket.arn,
      },
      {
        Action = [
          "s3:PutObject",
          "s3:DeleteObject",
        ],
        Effect   = "Allow",
        Resource = "${aws_s3_bucket.s3_bucket.arn}/*",
      },
    ],
  })
}


# Attach the IAM policy to the IAM user
resource "aws_iam_user_policy_attachment" "ingestion_policy_attachment" {
  user       = aws_iam_user.ingestion_iam_user.name
  policy_arn = aws_iam_policy.ingestion_iam_policy.arn
}