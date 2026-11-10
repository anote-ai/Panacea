terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Separate state from the main ../ stack, so applying this root only ever
  # touches the docs site. Configure via `terraform init -backend-config=...`:
  #   bucket = "<your terraform state bucket>"
  #   key    = "docs/terraform.tfstate"
  #   region = "us-east-1"
  backend "s3" {}
}

# us-east-1 is required: CloudFront only accepts ACM certificates from there.
provider "aws" {
  region = var.aws_region
}
