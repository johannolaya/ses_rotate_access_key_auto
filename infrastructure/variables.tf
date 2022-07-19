variable "aws_region" {
  description = "AWS region for all resources."
  type    = string
}

variable "environment" {
  description = "Environment suffix. i.e dev, qa, stg, prod"
  type = string
}

variable "smtp_user" {
  description = "IAM user to SES"
  type = string
}
