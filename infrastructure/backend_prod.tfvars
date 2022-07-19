bucket  = "terraform-states"
key     = "smtp-user.tfstate"
encrypt = true
region  = "us-east-1"
dynamodb_table = "terraform-locks"