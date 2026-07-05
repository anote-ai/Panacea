# Static hosting for the Panacea web app and the developer cookbook/docs
# site. Both buckets are private — CloudFront reaches them only via OAC.

resource "aws_s3_bucket" "web" {
  bucket = "${var.project_name}-${var.environment}-web"
}

resource "aws_s3_bucket_public_access_block" "web" {
  bucket                  = aws_s3_bucket.web.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_policy" "web" {
  bucket = aws_s3_bucket.web.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "cloudfront.amazonaws.com" }
      Action    = "s3:GetObject"
      Resource  = "${aws_s3_bucket.web.arn}/*"
      Condition = {
        StringEquals = {
          "AWS:SourceArn" = aws_cloudfront_distribution.web.arn
        }
      }
    }]
  })
}

resource "aws_s3_bucket" "cookbook" {
  bucket = "${var.project_name}-${var.environment}-cookbook"
}

resource "aws_s3_bucket_public_access_block" "cookbook" {
  bucket                  = aws_s3_bucket.cookbook.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_policy" "cookbook" {
  bucket = aws_s3_bucket.cookbook.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "cloudfront.amazonaws.com" }
      Action    = "s3:GetObject"
      Resource  = "${aws_s3_bucket.cookbook.arn}/*"
      Condition = {
        StringEquals = {
          "AWS:SourceArn" = aws_cloudfront_distribution.cookbook.arn
        }
      }
    }]
  })
}
