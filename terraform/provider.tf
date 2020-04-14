provider "aws" {
  version = "~> 2.0"
  region  = var.region

  assume_role {
    role_arn     = "arn:aws:iam::312417806451:role/admin"
    session_name = "terraform"
  }
}
