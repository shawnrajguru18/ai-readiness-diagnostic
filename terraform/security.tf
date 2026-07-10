# Use provided VPC or default VPC
locals {
  vpc_id = var.vpc_id != "" ? var.vpc_id : data.aws_vpc.default[0].id
}

data "aws_vpc" "default" {
  count   = var.vpc_id != "" ? 0 : 1
  default = true
}

# Security group for ECS tasks
resource "aws_security_group" "ecs_tasks" {
  name        = "${local.app_name}-ecs-tasks"
  description = "Allow inbound traffic to ECS tasks"
  vpc_id      = local.vpc_id

  ingress {
    from_port   = var.container_port
    to_port     = var.container_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.tags
}
