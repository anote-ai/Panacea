terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  backend "s3" {
    # Configure via `terraform init -backend-config=...` or a backend.hcl file.
    # Use a key distinct from the main anote-ai stack so state never collides:
    #   bucket = "anote-terraform-state"
    #   key    = "panacea/terraform.tfstate"
    #   region = "us-east-1"
  }
}

# CloudFront + ACM certs for CloudFront must be requested in us-east-1
# regardless of where everything else runs, so we alias the provider even
# though the default region is already us-east-1.
provider "aws" {
  region = var.aws_region
}

provider "aws" {
  alias  = "us_east_1"
  region = "us-east-1"
}
