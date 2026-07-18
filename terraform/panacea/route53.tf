# Optional — see the `manage_route53_zone` description in variables.tf.
# When false, this file creates nothing and DNS stays fully on GoDaddy;
# use the `manual_dns_records` output to fill in GoDaddy's DNS panel by hand.

resource "aws_route53_zone" "this" {
  count = var.manage_route53_zone ? 1 : 0
  name  = var.domain_name
}

resource "aws_route53_record" "apex" {
  count   = var.manage_route53_zone ? 1 : 0
  zone_id = aws_route53_zone.this[0].zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.web.domain_name
    zone_id                = aws_cloudfront_distribution.web.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "cookbook" {
  count   = var.manage_route53_zone ? 1 : 0
  zone_id = aws_route53_zone.this[0].zone_id
  name    = "${var.cookbook_subdomain}.${var.domain_name}"
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.cookbook.domain_name
    zone_id                = aws_cloudfront_distribution.cookbook.hosted_zone_id
    evaluate_target_health = false
  }
}
