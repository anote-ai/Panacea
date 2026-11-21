# Ourogen Docs

MkDocs Material site published at **https://docs.ourogen.ai**.

## Develop

```bash
pip install -r requirements.txt
mkdocs serve          # http://127.0.0.1:8000
mkdocs build --strict # what CI and the deploy run
```

## Deploy

`.github/workflows/deploy-docs.yml` runs on every push to `main` that touches `packages/docs/**`
(or manually from **Actions → Deploy Docs → Run workflow**). It builds with `--strict`, syncs
`site/` to S3, invalidates CloudFront, then checks that the home page and a nested page return 200.

It skips with a warning until these repository variables are set:

| Variable | Value |
|---|---|
| `S3_BUCKET_DOCS` | `ourogen-docs` |
| `CLOUDFRONT_DISTRIBUTION_ID_DOCS` | `EK3EHTUQSOFMW` |

`AWS_REGION` and the `AWS_ROLE_ARN` secret are shared with the main deploy workflow.

## AWS setup (done by hand in the console, us-east-1)

| Piece | Setting |
|---|---|
| S3 bucket `ourogen-docs` | Private (Block all public access on); readable only by CloudFront via Origin Access Control |
| ACM certificate | `docs.ourogen.ai`, DNS-validated in the `ourogen.ai` Route 53 zone |
| CloudFront distribution `EK3EHTUQSOFMW` | Origin = the bucket with OAC; alternate domain `docs.ourogen.ai`; default root object `index.html`; 404 → `/404.html` (status 404); HTTP → HTTPS |
| CloudFront Function `docs-index-rewrite` | Viewer request. MkDocs pages live at `/section/page/`, and S3 doesn't resolve folder indexes, so this maps them to `index.html` (code below) |
| Route 53 | `docs` A/AAAA alias → the distribution |
| IAM | `github-panacea-role` may `s3:ListBucket`/`PutObject`/`DeleteObject`/`GetObject` on the bucket and `cloudfront:CreateInvalidation` on the distribution |

```js
function handler(event) {
  var request = event.request;
  var uri = request.uri;
  if (uri.endsWith("/")) {
    request.uri = uri + "index.html";
  } else if (uri.lastIndexOf(".") <= uri.lastIndexOf("/")) {
    request.uri = uri + "/index.html";
  }
  return request;
}
```

If nested pages return 403 while the home page works, the function isn't attached to the
distribution's default behavior as a viewer-request function.
