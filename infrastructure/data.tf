data "aws_iam_user" "this" {
  user_name = var.smtp_user
}