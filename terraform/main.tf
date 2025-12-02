terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.23.0"
    }
    # awscc = {
    #   source  = "hashicorp/awscc"
    #   version = "1.65.0"
    # }
  }
}

provider "aws" {
  # Configuration options
  default_tags {
    tags = {
      Assessment = "SolutionsEngineer-candidate-jonah"
      Project    = "Swiftline"
      Created_by = "terraform"
    }
  }
}

# provider "awscc" {
#   # Configuration options
# }

locals {
  name-prefix = "swiftline"
}

data "aws_caller_identity" "current" {}
