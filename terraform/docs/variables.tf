variable "aws_region" {
  description = "AWS region. Keep us-east-1 — CloudFront requires its ACM certificate there."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Short name used to prefix all resources (matches the main stack)."
  type        = string
  default     = "anote-ai"
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "production"
}

variable "domain_name" {
  description = "Public hostname for the docs site."
  type        = string
  default     = "docs.ourogen.ai"
}

variable "hosted_zone_name" {
  description = "Existing Route 53 public hosted zone that domain_name lives in."
  type        = string
  default     = "ourogen.ai"
}

variable "price_class" {
  description = "CloudFront price class. PriceClass_100 (North America + Europe edges) is the cheapest."
  type        = string
  default     = "PriceClass_100"
}

variable "deploy_role_name" {
  description = "Optional: name (not ARN) of the IAM role GitHub Actions assumes (secrets.AWS_ROLE_ARN). If set, it is granted permission to upload to the docs bucket and invalidate the docs distribution."
  type        = string
  default     = ""
}
