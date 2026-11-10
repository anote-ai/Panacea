# Static hosting for the MkDocs site (packages/docs) at docs.ourogen.ai.
# Same pattern as ../cloudfront.tf: a private S3 bucket that only CloudFront
# can read (Origin Access Control), fronted by a CloudFront distribution.

locals {
  name = "${var.project_name}-${var.environment}-docs"
}

data "aws_route53_zone" "main" {
  name         = var.hosted_zone_name
  private_zone = false
}

# ── S3 bucket (private) ──────────────────────────────────────────────────────

resource "aws_s3_bucket" "docs" {
  bucket = local.name
}

resource "aws_s3_bucket_public_access_block" "docs" {
  bucket                  = aws_s3_bucket.docs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "docs" {
  bucket = aws_s3_bucket.docs.id
  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_cloudfront_origin_access_control" "docs" {
  name                              = "${local.name}-oac"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_s3_bucket_policy" "docs" {
  bucket = aws_s3_bucket.docs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "cloudfront.amazonaws.com" }
      Action    = "s3:GetObject"
      Resource  = "${aws_s3_bucket.docs.arn}/*"
      Condition = {
        StringEquals = {
          "AWS:SourceArn" = aws_cloudfront_distribution.docs.arn
        }
      }
    }]
  })

  depends_on = [aws_s3_bucket_public_access_block.docs]
}

# ── TLS certificate (free, DNS-validated in the existing zone) ───────────────

resource "aws_acm_certificate" "docs" {
  domain_name       = var.domain_name
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "docs_cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.docs.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  zone_id         = data.aws_route53_zone.main.zone_id
  name            = each.value.name
  type            = each.value.type
  records         = [each.value.record]
  ttl             = 300
  allow_overwrite = true
}

resource "aws_acm_certificate_validation" "docs" {
  certificate_arn         = aws_acm_certificate.docs.arn
  validation_record_fqdns = [for r in aws_route53_record.docs_cert_validation : r.fqdn]
}

# ── CloudFront ───────────────────────────────────────────────────────────────

# MkDocs emits pretty URLs (/guide/ -> /guide/index.html). S3 REST origins
# don't resolve directory indexes, so rewrite them at the edge. CloudFront
# Functions are free for the first 2M invocations/month.
resource "aws_cloudfront_function" "docs_index" {
  name    = "${local.name}-index-rewrite"
  runtime = "cloudfront-js-2.0"
  comment = "Append index.html to directory-style docs URLs"
  publish = true
  code    = file("${path.module}/index-rewrite.js")
}

data "aws_cloudfront_cache_policy" "caching_optimized" {
  name = "Managed-CachingOptimized"
}

resource "aws_cloudfront_distribution" "docs" {
  enabled             = true
  is_ipv6_enabled     = true
  comment             = "Ourogen docs (${var.domain_name})"
  default_root_object = "index.html"
  aliases             = [var.domain_name]
  price_class         = var.price_class
  http_version        = "http2and3"

  origin {
    domain_name              = aws_s3_bucket.docs.bucket_regional_domain_name
    origin_id                = "s3-docs"
    origin_access_control_id = aws_cloudfront_origin_access_control.docs.id
  }

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "s3-docs"
    viewer_protocol_policy = "redirect-to-https"
    compress               = true
    cache_policy_id        = data.aws_cloudfront_cache_policy.caching_optimized.id

    function_association {
      event_type   = "viewer-request"
      function_arn = aws_cloudfront_function.docs_index.arn
    }
  }

  # Without s3:ListBucket, S3 returns 403 (not 404) for missing keys.
  # Serve MkDocs' own 404 page for both.
  custom_error_response {
    error_code            = 403
    response_code         = 404
    response_page_path    = "/404.html"
    error_caching_min_ttl = 60
  }

  custom_error_response {
    error_code            = 404
    response_code         = 404
    response_page_path    = "/404.html"
    error_caching_min_ttl = 60
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate_validation.docs.certificate_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }
}

# ── DNS ──────────────────────────────────────────────────────────────────────

resource "aws_route53_record" "docs" {
  for_each = toset(["A", "AAAA"])

  zone_id = data.aws_route53_zone.main.zone_id
  name    = var.domain_name
  type    = each.value

  alias {
    name                   = aws_cloudfront_distribution.docs.domain_name
    zone_id                = aws_cloudfront_distribution.docs.hosted_zone_id
    evaluate_target_health = false
  }
}

# ── Optional: let the GitHub Actions deploy role publish the docs ────────────

resource "aws_iam_role_policy" "deploy_docs" {
  count = var.deploy_role_name != "" ? 1 : 0

  name = "${local.name}-deploy"
  role = var.deploy_role_name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = aws_s3_bucket.docs.arn
      },
      {
        Effect   = "Allow"
        Action   = ["s3:PutObject", "s3:DeleteObject", "s3:GetObject"]
        Resource = "${aws_s3_bucket.docs.arn}/*"
      },
      {
        Effect   = "Allow"
        Action   = ["cloudfront:CreateInvalidation"]
        Resource = aws_cloudfront_distribution.docs.arn
      },
    ]
  })
}
