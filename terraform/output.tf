output "data_engineer_iam_user" {
  value = aws_iam_user.data_engineer_iam_user.arn
}
output "data_engineer_iam_user_access_key" {
  value = aws_iam_access_key.data_engineer_iam_user_access_key.id
}
output "data_engineer_iam_user_secret_key" {
  value = aws_iam_access_key.data_engineer_iam_user_access_key.secret
  sensitive = true
}