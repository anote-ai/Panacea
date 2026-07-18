locals {
  # Shared secret CloudFront attaches to every request it forwards to the
  # backend. The EC2-hosted Flask app should reject anything missing/wrong
  # here, since the backend port itself has to stay open to 0.0.0.0/0.
  origin_verify_header = "X-Panacea-Origin-Verify"
}

resource "aws_cloudfront_origin_access_control" "web" {
  name                              = "${var.project_name}-web-oac"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_origin_access_control" "cookbook" {
  name                              = "${var.project_name}-cookbook-oac"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# ── Web app distribution ─────────────────────────────────────────────────────
# Default behavior serves the built Vite app from S3; /api, /auth, and
# /health are routed to the existing EC2 instance so the SPA can keep using
# same-origin relative paths in production.
resource "aws_cloudfront_distribution" "web" {
  enabled             = true
  default_root_object = var.web_index_document
  aliases             = [var.domain_name]

  origin {
    domain_name              = aws_s3_bucket.web.bucket_regional_domain_name
    origin_id                = "s3-web"
    origin_access_control_id = aws_cloudfront_origin_access_control.web.id
  }

  origin {
    domain_name = data.aws_instance.backend.public_dns
    origin_id   = "ec2-backend"

    custom_origin_config {
      http_port              = var.backend_port
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }

    custom_header {
      name  = local.origin_verify_header
      value = random_password.origin_verify.result
    }
  }

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "s3-web"
    viewer_protocol_policy = "redirect-to-https"
    compress               = true

    forwarded_values {
      query_string = false
      cookies { forward = "none" }
    }
  }

  dynamic "ordered_cache_behavior" {
    for_each = ["/api/*", "/auth/*", "/health"]
    content {
      path_pattern           = ordered_cache_behavior.value
      allowed_methods        = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
      cached_methods         = ["GET", "HEAD"]
      target_origin_id       = "ec2-backend"
      viewer_protocol_policy = "redirect-to-https"
      min_ttl                = 0
      default_ttl            = 0
      max_ttl                = 0

      forwarded_values {
        query_string = true
        headers      = ["Authorization", "Content-Type"]
        cookies { forward = "all" }
      }
    }
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn = aws_acm_certificate.site.arn
    ssl_support_method  = "sni-only"
  }
}

# ── Cookbook / docs distribution ─────────────────────────────────────────────
resource "aws_cloudfront_distribution" "cookbook" {
  enabled             = true
  default_root_object = var.web_index_document
  aliases             = ["${var.cookbook_subdomain}.${var.domain_name}"]

  origin {
    domain_name              = aws_s3_bucket.cookbook.bucket_regional_domain_name
    origin_id                = "s3-cookbook"
    origin_access_control_id = aws_cloudfront_origin_access_control.cookbook.id
  }

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "s3-cookbook"
    viewer_protocol_policy = "redirect-to-https"
    compress               = true

    forwarded_values {
      query_string = false
      cookies { forward = "none" }
    }
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn = aws_acm_certificate.site.arn
    ssl_support_method  = "sni-only"
  }
}

# Rotated on every `terraform apply` that touches this resource; that's fine
# since it's only there to stop stray direct hits on the EC2 instance's
# public port, not to act as real authentication.
resource "random_password" "origin_verify" {
  length  = 32
  special = false
}
