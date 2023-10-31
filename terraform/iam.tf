# Create IAM user for data engineer
resource "aws_iam_user" "data_engineer_iam_user" {
    name = join("-", [var.project, var.data_engineer_iam_user])
}

# Create a key-pair access for data engineer user
resource "aws_iam_access_key" "data_engineer_iam_user_access_key" {
    user = aws_iam_user.data_engineer_iam_user.name
}

# Create IAM policy for interacting with S3. Delete, List, Put objects into S3
resource "aws_iam_policy" "data_loader_iam_policy" {
  name = join("-", [var.project, var.data_loader_iam_policy])

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

# Create data-loader role
resource "aws_iam_role" "data_loader_role" {
  name = join("-", [var.project, var.data_loader_iam_role])
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:user/${aws_iam_user.data_engineer_iam_user.name}"
        }
      }
    ]
  })
}

# Attach data-loader policy to data-loader role
resource "aws_iam_role_policy_attachment" "data_loader_attachment" {
  policy_arn = aws_iam_policy.data_loader_iam_policy.arn
  role       = aws_iam_role.data_loader_role.name
}