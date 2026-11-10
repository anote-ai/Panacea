// CloudFront Function (viewer-request): map MkDocs directory URLs to their
// index.html, since the S3 REST origin doesn't resolve directory indexes.
//   /           -> /index.html   (also covered by default_root_object)
//   /guide/     -> /guide/index.html
//   /guide      -> /guide/index.html
//   /app.js     -> unchanged
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
