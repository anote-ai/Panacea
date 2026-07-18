# Open the backend port on the existing instance's security group so
# CloudFront can reach it. CloudFront doesn't publish a stable IP range, so
# this has to stay open to 0.0.0.0/0 — pair it with the
# X-Panacea-Origin-Verify custom header check in cloudfront.tf so the
# backend rejects requests that didn't come through CloudFront.
resource "aws_security_group_rule" "backend_from_cloudfront" {
  type              = "ingress"
  from_port         = var.backend_port
  to_port           = var.backend_port
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = data.aws_security_group.backend.id
  description       = "Panacea backend, fronted by CloudFront"
}
