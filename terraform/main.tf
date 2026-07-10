terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Local values for consistent naming
locals {
  app_name = var.app_name
  environment = var.environment
  tags = {
    Environment = local.environment
    Application = local.app_name
    ManagedBy   = "Terraform"
  }
}
