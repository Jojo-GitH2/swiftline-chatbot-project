terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.23.0"
    }
    
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


locals {
  name-prefix = "swiftline"
}

data "aws_caller_identity" "current" {}
