# CloudFront requires the certificate to live in us-east-1, hence the
# provider alias regardless of var.aws_region.
resource "aws_acm_certificate" "site" {
  provider                  = aws.us_east_1
  domain_name               = var.domain_name
  subject_alternative_names = ["${var.cookbook_subdomain}.${var.domain_name}"]
  validation_method         = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

# Only auto-validates when Route 53 is authoritative for the zone. With
# external (GoDaddy) DNS, apply the CNAME records from the
# `manual_dns_records` output by hand and the certificate validates itself
# once GoDaddy's DNS propagates.
resource "aws_route53_record" "cert_validation" {
  for_each = var.manage_route53_zone ? {
    for dvo in aws_acm_certificate.site.domain_validation_options : dvo.domain_name => {
      name  = dvo.resource_record_name
      type  = dvo.resource_record_type
      value = dvo.resource_record_value
    }
  } : {}

  zone_id = aws_route53_zone.this[0].zone_id
  name    = each.value.name
  type    = each.value.type
  ttl     = 60
  records = [each.value.value]
}

resource "aws_acm_certificate_validation" "site" {
  count                   = var.manage_route53_zone ? 1 : 0
  provider                = aws.us_east_1
  certificate_arn         = aws_acm_certificate.site.arn
  validation_record_fqdns = [for r in aws_route53_record.cert_validation : r.fqdn]
}
