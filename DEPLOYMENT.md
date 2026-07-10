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
   `PANACEA_ORIGIN_VERIFY` from step 4, etc). If chat/document persistence
   lands on a MySQL backend (see #259), also set
   `PERSISTENCE_BACKEND=mysql` alongside the `DB_*` vars here.
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
CLI (`packages/cli`, npm) | `release.yml`, on `v*` git tags
TypeScript SDK (`packages/sdk`, npm) | `release.yml`, on `v*` git tags
Python SDK (`packages/sdk-py`, PyPI `anote-sdk`) | `release.yml`, on `v*` git tags
VS Code extension | `release.yml`, on `v*` git tags
Desktop app | `release.yml`, on `v*` git tags, GitHub Releases on `anote-ai/Panacea`
Mobile app | `release.yml`, on `v*` git tags — builds via EAS; **submit is not automatic yet** (see below)

### Release-track (`release.yml`) secrets

- `NPM_TOKEN` — publishes both the CLI and the TypeScript SDK (two separate
  npm packages, one token).
- `PYPI_API_TOKEN` — PyPI API token scoped to the `anote-sdk` project.
- `VSCE_PAT` — VS Code Marketplace personal access token for the `Anote`
  publisher.
- `GITHUB_TOKEN` — provided automatically by Actions; used by
  `electron-forge publish` to create the desktop app's GitHub Release on
  this repo (`anote-ai/Panacea` — `packages/desktop/forge.config.js` was
  previously pointed at the old `Autonomous-Intelligence` repo name, fixed).
- `EXPO_TOKEN` — Expo access token so `eas build` can run non-interactively
  in CI.

**Mobile app remaining action item**: `packages/mobile/eas.json`'s
`submit.production` block is still empty, so `release.yml`'s
`publish-mobile` job only builds the iOS/Android binaries — it does not
submit them to the App Store / Play Store. To turn on auto-submit:
1. Fill in `submit.production.ios` (`appleId`, `ascAppId`, `appleTeamId`)
   and `submit.production.android` (`serviceAccountKeyPath`, or store the
   key as an EAS secret) in `eas.json`, per the
   [EAS submit docs](https://docs.expo.dev/submit/introduction/).
2. Add `--auto-submit` to the `eas build` command in the `publish-mobile`
   job.
This needs your actual Apple Developer / Google Play Console credentials,
which no amount of pipeline scaffolding can substitute for.

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
