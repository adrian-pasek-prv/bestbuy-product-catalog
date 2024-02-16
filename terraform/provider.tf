terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    snowflake = {
      source  = "Snowflake-Labs/snowflake"
      version = "~> 0.85.0"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project = var.project
    }
  }
}

# Configure the Snowflake Provider
provider "snowflake" {
  role = "INFRA_ADMIN"
}

# Extract info about AWS account
data "aws_caller_identity" "current" {}
