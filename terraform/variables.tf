variable "aws_region" {
  description = "AWS region to deploy into"
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
  default     = "anote-ai"
}

variable "backend_image_tag" {
  description = "Docker image tag to deploy for the backend (set by CI to the git SHA)"
  type        = string
  default     = "latest"
}

variable "backend_container_port" {
  type    = number
  default = 5000
}

variable "backend_desired_count" {
  type    = number
  default = 2
}

variable "backend_cpu" {
  type    = number
  default = 512
}

variable "backend_memory" {
  type    = number
  default = 1024
}

variable "db_instance_class" {
  type    = string
  default = "db.t3.micro"
}

variable "db_allocated_storage" {
  type    = number
  default = 20
}

variable "db_name" {
  type    = string
  default = "anote"
}

variable "db_username" {
  type    = string
  default = "anote_admin"
}

variable "db_password" {
  description = "Master password for RDS. Pass via TF_VAR_db_password or a tfvars file excluded from git."
  type        = string
  sensitive   = true
}

variable "jwt_secret_key" {
  description = "Flask JWT signing secret."
  type        = string
  sensitive   = true
}

variable "anthropic_api_key" {
  type      = string
  sensitive = true
  default   = ""
}

variable "openai_api_key" {
  type      = string
  sensitive = true
  default   = ""
}

variable "stripe_secret_key" {
  type      = string
  sensitive = true
  default   = ""
}

variable "stripe_webhook_secret" {
  description = "Signing secret for the Stripe webhook endpoint (whsec_...)."
  type        = string
  sensitive   = true
  default     = ""
}

variable "stripe_price_basic" {
  description = "Stripe Price ID for the basic subscription tier."
  type        = string
  default     = ""
}

variable "stripe_price_pro" {
  description = "Stripe Price ID for the pro subscription tier."
  type        = string
  default     = ""
}

variable "stripe_price_enterprise" {
  description = "Stripe Price ID for the enterprise subscription tier."
  type        = string
  default     = ""
}

variable "provider_key_encryption_key" {
  description = "Fernet key encrypting user-supplied LLM provider API keys at rest. Generate with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
  type        = string
  sensitive   = true
  default     = ""
}

variable "ollama_base_url" {
  description = "Base URL for an Ollama server, if the deployment supports local/self-hosted models."
  type        = string
  default     = "http://localhost:11434"
}

variable "google_client_id" {
  description = "Google OAuth client ID for 'Sign in with Google' (not secret — Google itself sends this back in the browser redirect)."
  type        = string
  default     = ""
}

variable "google_client_secret" {
  description = "Google OAuth client secret, used server-side to exchange the auth code for tokens."
  type        = string
  sensitive   = true
  default     = ""
}

variable "google_oauth_redirect_uri" {
  description = "Must exactly match an 'Authorized redirect URI' on the Google OAuth client, e.g. https://<domain>/callback."
  type        = string
  default     = ""
}

variable "frontend_url" {
  description = "Public URL of the web frontend (e.g. https://<cloudfront-domain> or the custom domain) — where the backend redirects the browser after Google login completes."
  type        = string
  default     = ""
}

variable "domain_name" {
  description = "Optional custom domain for the CloudFront distribution (requires an ACM cert in us-east-1). Leave empty to use the default CloudFront domain."
  type        = string
  default     = ""
}

variable "acm_certificate_arn" {
  description = "ACM certificate ARN in us-east-1 for the CloudFront distribution. Required if domain_name is set."
  type        = string
  default     = ""
}
