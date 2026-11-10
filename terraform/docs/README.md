# Terraform — docs.ourogen.ai

Hosts the MkDocs site in `packages/docs` at **https://docs.ourogen.ai**, using the
same pattern as the web frontend in `../cloudfront.tf`: a private S3 bucket that
only CloudFront can read (Origin Access Control), behind a CloudFront distribution.

This is a **standalone Terraform root with its own state**, separate from `../`.
Applying it only creates or changes the docs resources below. It never touches the
backend, RDS, ECS, or the web frontend.

## What it creates

| Resource | Notes |
|---|---|
| S3 bucket `anote-ai-production-docs` | Private, with all public access blocked |
| CloudFront distribution | `PriceClass_100` (cheapest), HTTPS only, HTTP/2 and HTTP/3, gzip/brotli |
| CloudFront Function | Rewrites `/guide/` to `/guide/index.html` (MkDocs pretty URLs) |
| ACM certificate for `docs.ourogen.ai` | Free, validated by DNS in the existing `ourogen.ai` zone |
| Route 53 `A` + `AAAA` alias records | `docs.ourogen.ai` pointing at CloudFront |
| *(optional)* inline IAM policy on the GitHub deploy role | Only when `deploy_role_name` is set |

It looks up the existing `ourogen.ai` hosted zone and does **not** create a new one.

## Expected cost

Roughly **$0.10–$1/month** at docs-site traffic:

- S3: about 40 MB stored, about $0.001/month, plus a few cents of requests per deploy.
- CloudFront: the always-free tier covers 1 TB transfer and 10M requests a month.
- CloudFront Function: the first 2M invocations a month are free.
- ACM certificate: free. Route 53: alias records to CloudFront are free to query,
  and the hosted zone already exists, so it adds nothing.
- Cache invalidations: each deploy invalidates `/*`, which counts as one path.
  The first 1,000 paths a month are free.

## One-time setup

```bash
cd terraform/docs
terraform init \
  -backend-config="bucket=<your terraform state bucket>" \
  -backend-config="key=docs/terraform.tfstate" \
  -backend-config="region=us-east-1"

# Optional: also grant the GitHub Actions deploy role (the role behind the
# AWS_ROLE_ARN secret) permission to publish. Pass its *name*, not its ARN.
terraform apply -var deploy_role_name=<github-deploy-role-name>
```

The first apply takes about 5–10 minutes, mostly ACM validation and the CloudFront rollout.

Then, in GitHub, go to **Settings → Secrets and variables → Actions → Variables** in
the `production` environment or at repository level, and add:

| Variable | Value |
|---|---|
| `S3_BUCKET_DOCS` | `terraform output -raw docs_s3_bucket_name` |
| `CLOUDFRONT_DISTRIBUTION_ID_DOCS` | `terraform output -raw docs_cloudfront_distribution_id` |

`AWS_REGION` and the `AWS_ROLE_ARN` secret are reused from the existing deploy workflow.

Finally, run **Actions → Deploy Docs → Run workflow** once, or push any change under
`packages/docs/`. Until the two variables are set, the workflow skips with a
warning instead of failing.

## Ongoing deploys

`.github/workflows/deploy-docs.yml` runs on pushes to `main` that touch
`packages/docs/**`. It builds with `mkdocs build --strict`, syncs to S3, and
invalidates CloudFront. HTML, the sitemap, and the search index are served with
`no-cache` so edits appear right away. Other assets are cached for a day.

## If you skip `deploy_role_name`

Attach an equivalent policy to the deploy role by hand: `s3:ListBucket` on the
bucket, `s3:PutObject`/`s3:DeleteObject`/`s3:GetObject` on `bucket/*`, and
`cloudfront:CreateInvalidation` on the docs distribution.

## Re-enabling the landing page links

The links to `docs.ourogen.ai` on the Ourogen landing page (Navbar, Footer,
Manifesto page, and the product-page CTAs in `landingPageData.js`) are commented
out until this is live. Uncomment them after the first successful docs deploy.
