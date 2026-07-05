output "web_cloudfront_domain_name" {
  value = aws_cloudfront_distribution.web.domain_name
}

output "cookbook_cloudfront_domain_name" {
  value = aws_cloudfront_distribution.cookbook.domain_name
}

output "web_s3_bucket" {
  value = aws_s3_bucket.web.bucket
}

output "cookbook_s3_bucket" {
  value = aws_s3_bucket.cookbook.bucket
}

output "backend_instance_id" {
  value = data.aws_instance.backend.id
}

output "backend_public_dns" {
  value = data.aws_instance.backend.public_dns
}

output "origin_verify_header_value" {
  description = "Set this as the value the Flask backend expects on X-Panacea-Origin-Verify"
  value       = random_password.origin_verify.result
  sensitive   = true
}

output "route53_name_servers" {
  description = "If manage_route53_zone = true, point GoDaddy's nameservers (Domain Settings > Nameservers > Custom) at these"
  value       = var.manage_route53_zone ? aws_route53_zone.this[0].name_servers : []
}

output "manual_dns_records" {
  description = "If manage_route53_zone = false, create these records in GoDaddy's DNS panel by hand"
  value = var.manage_route53_zone ? tomap({}) : tomap({
    "${var.domain_name}"                                 = "ALIAS/ANAME (or A via GoDaddy's flattening) -> ${aws_cloudfront_distribution.web.domain_name}"
    "${var.cookbook_subdomain}.${var.domain_name}"        = "CNAME -> ${aws_cloudfront_distribution.cookbook.domain_name}"
    "ACM validation (see `aws acm describe-certificate`)" = "CNAME records from aws_acm_certificate.site.domain_validation_options"
  })
}
