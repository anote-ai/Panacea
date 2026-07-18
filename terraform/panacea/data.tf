# The existing Private Chatbot EC2 instance Panacea's backend gets deployed
# onto. Looked up by tag rather than created here — see variables.tf for why.
data "aws_instance" "backend" {
  filter {
    name   = "tag:Name"
    values = [var.ec2_instance_name_tag]
  }

  filter {
    name   = "instance-state-name"
    values = ["running"]
  }
}

# The instance's primary security group, so we can open the backend port to
# CloudFront without touching any of its other existing rules.
data "aws_security_group" "backend" {
  id = data.aws_instance.backend.vpc_security_group_ids[0]
}
