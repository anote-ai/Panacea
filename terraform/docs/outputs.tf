output "docs_url" {
  value = "https://${var.domain_name}"
}

output "docs_s3_bucket_name" {
  description = "Set as the GitHub Actions variable S3_BUCKET_DOCS."
  value       = aws_s3_bucket.docs.bucket
}

output "docs_cloudfront_distribution_id" {
  description = "Set as the GitHub Actions variable CLOUDFRONT_DISTRIBUTION_ID_DOCS."
  value       = aws_cloudfront_distribution.docs.id
}

output "docs_cloudfront_domain_name" {
  value = aws_cloudfront_distribution.docs.domain_name
}
