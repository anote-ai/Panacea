# Terraform — Panacea deployment

Provisions the AWS pieces for Panacea (the developer-facing assistant:
web app, VS Code extension, CLI, desktop app, mobile app, cookbook/docs)
**without** standing up new compute. This stack deliberately reuses the
existing Private Chatbot EC2 instance for the backend instead of the
ECS/Fargate/RDS setup in `../` (the original anote-ai stack), so the whole
thing stays inside the ≤$100/month budget target:

| Resource                              | Rough monthly cost |
|----------------------------------------|---------------------|
| EC2 instance                          | $0 marginal — already running/paid for |
| S3 (web + cookbook buckets)           | ~$1–2 at low traffic |
| CloudFront (2 distributions)          | ~$5–15 at low-to-moderate traffic |
| Route 53 hosted zone                  | $0.50/mo + $0.40/million queries |
| ACM certificate                       | free |
| **Total**                              | **well under $100/month** |

It provisions:

- An **S3 + CloudFront** distribution for the web app (`packages/web`),
  with `/api/*`, `/auth/*`, `/health` routed to the existing EC2 instance so
  the SPA can keep using same-origin relative paths, same pattern as `../cloudfront.tf`.
- A second **S3 + CloudFront** distribution for the developer cookbook/docs
  site (`packages/docs`, built with MkDocs), served from `cookbook.<domain>`.
- An **ACM certificate** (us-east-1, DNS-validated) covering the apex domain
  and the cookbook subdomain.
- Either a **Route 53 hosted zone** (if `manage_route53_zone = true`, the
  default) or nothing (if `false`, GoDaddy stays authoritative for DNS —
  see below).
- A **security group rule** opening the backend port on the *existing*
  instance's security group so CloudFront can reach it. Nothing about the
  instance itself is created or replaced — it's looked up via
  `data "aws_instance"` by its `Name` tag (`var.ec2_instance_name_tag`).

## One-time setup

1. Create/reuse an S3 bucket for Terraform state and configure the
   `backend "s3"` block in `versions.tf` with a **key distinct from the
   main anote-ai stack** (e.g. `panacea/terraform.tfstate`), then
   `terraform init`.
2. Set the required variables (via `terraform.tfvars`, gitignored, or
   `TF_VAR_*`):
   ```
   export TF_VAR_domain_name="yournewdomain.com"          # purchased on GoDaddy
   export TF_VAR_ec2_instance_name_tag="private-chatbot"  # match the real Name tag
   ```
3. `terraform plan` / `terraform apply`.

## Connecting the GoDaddy domain

**Option A — Route 53 authoritative (default, `manage_route53_zone = true`)**
1. `terraform apply` creates the hosted zone.
2. Read the `route53_name_servers` output.
3. In GoDaddy: Domain Settings → Nameservers → Custom → paste those 4 values.
4. Everything else (ACM validation, apex/cookbook records) is wired up by
   Terraform automatically once the nameservers propagate.

**Option B — GoDaddy stays authoritative (`manage_route53_zone = false`)**
1. `terraform apply` (this will not create a Route 53 zone or validate the
   cert automatically).
2. Read the `manual_dns_records` output and the ACM console's
   `domain_validation_options` for the exact CNAME records to add.
3. In GoDaddy's DNS panel, add those CNAME records plus a CNAME/ALIAS for
   the apex and cookbook subdomain pointing at the two
   `*_cloudfront_domain_name` outputs (GoDaddy supports CNAME flattening at
   the apex; otherwise use `www` and redirect the apex).
4. Once ACM shows the cert as `ISSUED`, re-run `terraform apply` if the
   CloudFront distributions were created before validation completed.

## After the first apply

- Configure the backend (`packages/backend`) to read
  `origin_verify_header_value` (sensitive output) and reject any request
  missing a matching `X-Panacea-Origin-Verify` header — the backend port has
  to stay open to `0.0.0.0/0` since CloudFront has no stable IP range, so
  this header is the only thing stopping direct hits on the EC2 instance.
- Push the built web app (`packages/web/dist`) to the `web_s3_bucket`
  output and invalidate the `web` CloudFront distribution.
- Push the built docs (`packages/docs/site`, `mkdocs build`) to the
  `cookbook_s3_bucket` output and invalidate the `cookbook` distribution.
- `.github/workflows/deploy-panacea.yml` automates both of the above plus
  the backend redeploy over SSH — see that file and the root `DEPLOYMENT.md`.

## What this does NOT cover

- **VS Code extension, CLI, desktop app**: already handled by
  `.github/workflows/release.yml` (npm / VS Code Marketplace / GitHub
  Releases on `v*` tags) — unrelated to this AWS stack.
- **Mobile app**: not yet wired into CI — needs an EAS (Expo) build/submit
  step once App Store/Play Store credentials exist. Tracked as a TODO in
  the root `DEPLOYMENT.md`.
- **Import of the existing EC2 instance into state**: intentionally left
  out — this stack only reads the instance via a data source and never
  manages its lifecycle, so there's nothing to import.
