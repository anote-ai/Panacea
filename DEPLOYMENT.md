# Deployment Guide

This repo now has two deployment tracks:

1. **Legacy manual track** (`anote.ai` / `chat.anote.ai`, the original
   Autonomous Intelligence product) — S3 sync + Elastic Beanstalk, run by
   hand from a developer's terminal. See "Legacy manual deployment" below
   for the existing runbook; it's unchanged.
2. **Panacea track** (this section) — the developer-facing product (web
   app, VS Code extension, CLI, desktop app, mobile app, cookbook/docs) on
   its own domain, deployed automatically via Terraform + GitHub Actions.

Both tracks run in the same AWS account (`730335449740`, `us-east-1`) as
the existing infrastructure — Panacea doesn't need a new account, just new
S3/CloudFront/Route53 resources plus reuse of the existing Private Chatbot
EC2 instance for compute. That reuse (no new RDS/ALB/Fargate) is what keeps
Panacea's AWS bill under the ≤$100/month target — see
`terraform/panacea/README.md` for the line-item breakdown.

## Panacea: one-time setup

1. **Buy the domain** on GoDaddy.
2. **Provision AWS resources**:
   ```bash
   cd terraform/panacea
   terraform init -backend-config="bucket=<state-bucket>" -backend-config="key=panacea/terraform.tfstate"
   export TF_VAR_domain_name="yournewdomain.com"
   export TF_VAR_ec2_instance_name_tag="private-chatbot"  # match the real Name tag on that EC2 instance
   terraform apply
   ```
3. **Connect the domain** — either point GoDaddy's nameservers at the
   `route53_name_servers` output (default), or add the CNAME records from
   `manual_dns_records` by hand if GoDaddy should stay authoritative. Full
   walkthrough in `terraform/panacea/README.md`.
4. **Harden the backend port**: set the `origin_verify_header_value`
   output as an env var the Flask app checks against the
   `X-Panacea-Origin-Verify` request header, rejecting anything else — the
   EC2 security group has to allow the backend port from `0.0.0.0/0` since
   CloudFront has no fixed IP range.
5. **One-time instance setup**: on the EC2 instance, clone this repo and
   create `.env.panacea` (gitignored) with the backend's runtime secrets
   (`JWT_SECRET_KEY`, `ANTHROPIC_API_KEY`, DB connection info for whatever
   MySQL/Redis/Tika the instance already runs for the existing chatbot,
   `PANACEA_ORIGIN_VERIFY` from step 4, etc).
6. **Set GitHub Actions secrets** (repo Settings → Environments →
   `staging`/`production`):
   - `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` (shared with
     the existing `deploy.yml`)
   - `PANACEA_EC2_HOST`, `PANACEA_EC2_USER`, `PANACEA_EC2_SSH_KEY`,
     `PANACEA_EC2_APP_DIR` (path this repo is checked out to on the instance)
   - `PANACEA_S3_WEB_BUCKET`, `PANACEA_CLOUDFRONT_WEB_DISTRIBUTION_ID`
     (from the `web_s3_bucket` / CloudFront `web` distribution outputs)
   - `PANACEA_S3_COOKBOOK_BUCKET`, `PANACEA_CLOUDFRONT_COOKBOOK_DISTRIBUTION_ID`
     (from the `cookbook_s3_bucket` / `cookbook` distribution outputs)

## Panacea: day-to-day deploys

Push to `develop` → `.github/workflows/deploy-panacea.yml` auto-deploys
staging (backend to EC2 over SSH, web app + cookbook to S3/CloudFront).
Production is manual: Actions → "Deploy Panacea" → Run workflow →
`environment: production`.

Component | How it ships
---|---
Web app (`packages/web`) | `deploy-panacea.yml`, on push to `develop`
Backend (`packages/backend`) | `deploy-panacea.yml`, on push to `develop`
Cookbook/docs (`packages/docs`) | `deploy-panacea.yml`, on push to `develop`
CLI, VS Code extension, desktop app | `release.yml`, on `v*` git tags (unchanged, no AWS involved)
Mobile app | **TODO** — no CI yet; needs an EAS (Expo) build/submit step once App Store/Play Store credentials exist

## Legacy manual deployment (anote.ai / chat.anote.ai)

Tutorial reference: [How to deploy a website on AWS with Docker, Flask, React](https://adamraudonis.medium.com/how-to-deploy-a-website-on-aws-with-docker-flask-react-from-scratch-d0845ebd9da4)

### Frontend — AWS S3

Prod URL: `https://anote-frontend.s3.amazonaws.com/index.html`

From the frontend folder:

**Staging**
```bash
export REACT_APP_API_ENDPOINT=https://api.tryanote-staging.com
npm run build
aws s3 sync build/ s3://anote-staging-frontend --acl public-read
```

**Prod**
```bash
REACT_APP_API_ENDPOINT=https://api.anote.ai npm run build && \
for file in ./build/static/js/*.js; do uglifyjs "$file" --compress --mangle -o "$file"; done && \
aws s3 sync build/ s3://anote-product-frontend --acl public-read
```

Chatbot frontend bucket: `anote-chatbot-frontend`.

### Documentation

From `frontend/src/docs`:
```bash
mkdocs build
aws s3 sync site/ s3://anote-product-docs --acl public-read
```

### Backend — AWS ECR + Elastic Beanstalk

Prod EB URL: `http://anote2-env.eba-dzfpabky.us-east-1.elasticbeanstalk.com/`
ECR URL: `730335449740.dkr.ecr.us-east-1.amazonaws.com`

Local run:
```bash
export APP_ENV=local
flask run
```

Make sure `requirements.txt` is up to date. From the server folder:
```bash
docker build -t anote-backend . --platform linux/amd64
docker run -p 5000:5000 anote-backend   # manual smoke test against the React frontend
# local variant: docker run -e IS_PROD=false -e APP_ENV=localdocker -p 5000:5000 anote-backend
docker tag anote-backend:latest 730335449740.dkr.ecr.us-east-1.amazonaws.com/anote-backend:latest
docker push 730335449740.dkr.ecr.us-east-1.amazonaws.com/anote-backend:latest
```

Staging build: `docker build -t anote-backend . --platform linux/amd64 --build-arg IS_PROD=false`

If not logged into AWS/ECR:
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 730335449740.dkr.ecr.us-east-1.amazonaws.com
```

Then from `server/aws_deploy` (contains `Dockerrun.aws.json`, which references
the ECR image):
```bash
eb init   # select Anote2
eb deploy
```

Specific environments:
```bash
eb deploy Anote2-env       # prod
eb deploy Anotestaging-env # staging
```

### Debugging the EB instance

- AWS EB console logs, or SSH: `eb ssh` (`eb ssh --setup` if not configured yet)
- Live errors: `tail -n 20 -f /var/log/eb-docker/containers/eb-current-app/eb-88128321be16-stdouterr.log`
- Out of disk space:
  ```bash
  df -H            # storage available
  lsblk            # partitions on the machine
  sudo growpart /dev/xvda 1
  sudo xfs_growfs -d /
  ```
- Dockerfile build args: `docker build -t anote-backend . --build-arg IS_PROD=false`
- Check a build arg's runtime value: `docker run --rm anote-backend sh -c 'echo $IS_PROD'`

### Outstanding TODO (legacy track)

Set up a CI/CD pipeline that runs tests before deploying, similar to
[this Elastic Beanstalk + CodePipeline walkthrough](https://www.red-gate.com/simple-talk/blogs/deploying-a-nodejs-application-from-github-to-aws-elastic-beanstalk-and-creating-a-ci-cd-aws-codepipeline/).
`packages/backend`'s CI (`ci.yml`) already runs ruff/mypy/pytest with an
80% coverage gate on every push, so most of this is covered for the
monorepo backend — what's still missing is gating the legacy `frontend/`
and `backend/` (non-`packages/`) folders the same way, since `main.yml`
runs their tests but nothing blocks a manual `eb deploy` on failure.
