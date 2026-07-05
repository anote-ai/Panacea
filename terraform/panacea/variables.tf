variable "aws_region" {
  description = "AWS region the existing Private Chatbot EC2 instance lives in"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment name (production, staging)"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Short name used to prefix all resources"
  type        = string
  default     = "panacea"
}

# ── Existing compute (reused, not created) ──────────────────────────────────
# Panacea reuses the existing Private Chatbot EC2 instance instead of
# standing up new ECS/Fargate/RDS resources, which is what keeps this stack
# inside the ≤$100/month budget target. Terraform only *reads* this instance
# (via a data source) and adds a security group rule to it — it never
# creates or replaces the instance itself.
variable "ec2_instance_name_tag" {
  description = "Value of the Name tag on the existing Private Chatbot EC2 instance to deploy Panacea's backend onto"
  type        = string
  default     = "private-chatbot"
}

variable "backend_port" {
  description = "Port the Panacea backend container listens on on the EC2 instance"
  type        = number
  default     = 5000
}

# ── Domain ───────────────────────────────────────────────────────────────────
variable "domain_name" {
  description = "New domain purchased on GoDaddy for Panacea (e.g. usepanacea.dev)"
  type        = string
}

variable "cookbook_subdomain" {
  description = "Subdomain the developer cookbook/docs site is served from"
  type        = string
  default     = "cookbook"
}

variable "manage_route53_zone" {
  description = <<-EOT
    If true, Terraform creates a Route 53 hosted zone and all DNS records for
    var.domain_name, and you point GoDaddy's nameservers at Route 53
    (Domain Settings > Nameservers > Custom, using the zone's `name_servers`
    output). If false, GoDaddy stays authoritative for DNS and you manually
    create the CNAME/ACM-validation records Terraform prints in the
    `manual_dns_records` output.
  EOT
  type        = bool
  default     = true
}

# ── S3 / CloudFront ──────────────────────────────────────────────────────────
variable "web_index_document" {
  type    = string
  default = "index.html"
}
