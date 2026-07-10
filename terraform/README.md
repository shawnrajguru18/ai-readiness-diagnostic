# Terraform Infrastructure for AI Readiness Diagnostic

Infrastructure as Code using Terraform to manage AWS resources for the AI Readiness Diagnostic application.

## Architecture

```
ECR (Docker images)
  ↓
ECS Fargate (containerized app)
  ├→ DynamoDB (session state)
  ├→ Bedrock (Claude API)
  └→ CloudWatch (logs)
```

## Prerequisites

1. **Terraform** (>= 1.0): [Install](https://www.terraform.io/downloads)
2. **AWS CLI v2**: [Install](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
3. **AWS credentials** configured: `aws configure` or SSO
4. **Docker** (to build and push images to ECR)

## Quick Start

### 1. Configure Variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
```

**Key variables:**
- `aws_region` — Target AWS region (default: us-east-1)
- `app_name` — Application name for resources
- `container_image` — Docker image URL (ECR repository)
- `task_cpu` / `task_memory` — ECS task sizing

### 2. Initialize Terraform

```bash
terraform init
```

This downloads the AWS provider and sets up the backend.

### 3. Plan Infrastructure

```bash
terraform plan -out=tfplan
```

Review the resources that will be created.

### 4. Apply Infrastructure

```bash
terraform apply tfplan
```

This creates:
- ECR repository
- ECS cluster + service
- DynamoDB table
- IAM roles
- CloudWatch log group
- Security groups

**Output:** Note the `ecr_repository_url` for pushing Docker images.

### 5. Push Docker Image

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and push from repo root
docker build -t ai-readiness-diagnostic .
docker tag ai-readiness-diagnostic:latest <ecr-url>:latest
docker push <ecr-url>:latest
```

Update `container_image` in `terraform.tfvars` and run `terraform apply` again.

## Teardown

Destroy all infrastructure:

```bash
terraform destroy
```

This deletes:
- ECS service and cluster
- DynamoDB table
- ECR repository
- IAM roles
- CloudWatch logs
- Security groups

## State Management

Terraform stores state in `terraform.tfstate` (local) or a remote backend.

**To use remote state** (recommended for teams), add a backend:

```bash
# Create S3 bucket for state
aws s3 mb s3://ai-readiness-tfstate-<account-id>

# Add to main.tf:
terraform {
  backend "s3" {
    bucket = "ai-readiness-tfstate-<account-id>"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}

# Migrate state
terraform init
```

## Useful Commands

```bash
# Check syntax
terraform fmt -check .

# Validate configuration
terraform validate

# Show current resources
terraform show

# Output resource attributes
terraform output

# Refresh state
terraform refresh

# Target specific resource
terraform apply -target=aws_ecs_service.app
```

## Cost Estimation

```bash
terraform plan -out=tfplan
# View estimated costs (if using Infracost or similar)
```

**Approximate monthly costs** (us-east-1):
- **ECS Fargate** (1024 CPU, 2048 MB): ~$11/month
- **DynamoDB** (on-demand): $0.25 per million reads + $1.25 per million writes
- **ECR**: ~$0.10/month (storage)
- **CloudWatch**: ~$0.50/month (logs)
- **Total**: ~$12-15/month

## Autoscaling

Enable autoscaling in `terraform.tfvars`:

```hcl
enable_autoscaling = true
min_capacity       = 1
max_capacity       = 3
```

This adds CPU-based autoscaling (target: 70% CPU utilization).

## Customization

### Change Task Size

Edit `terraform.tfvars`:
```hcl
task_cpu    = 2048  # Valid: 256, 512, 1024, 2048, 4096
task_memory = 4096  # Must be compatible with CPU
```

Run `terraform apply`.

### Add Environment Variables

Edit `ecs.tf` in the container definition:
```hcl
environment = [
  {
    name  = "MY_VAR"
    value = "my_value"
  }
]
```

### Scheduled Shutdown (Save Costs)

Add to `ecs.tf`:
```hcl
resource "aws_autoscaling_schedule" "scale_down" {
  scheduled_action_name  = "scale-down-evening"
  min_capacity           = 0
  max_capacity           = 0
  desired_capacity       = 0
  recurrence             = "0 18 * * MON-FRI"  # 6 PM weekdays
  service_namespace      = "ecs"
}

resource "aws_autoscaling_schedule" "scale_up" {
  scheduled_action_name  = "scale-up-morning"
  desired_capacity       = 1
  recurrence             = "0 8 * * MON-FRI"   # 8 AM weekdays
  service_namespace      = "ecs"
}
```

## Troubleshooting

**ECS tasks failing to start:**
```bash
# Check logs
aws logs tail /ecs/ai-readiness-diagnostic --follow --region us-east-1
```

**Permission denied errors:**
Ensure your AWS IAM user has permissions for EC2, ECS, DynamoDB, IAM, CloudWatch, ECR.

**ECR image not found:**
Push the image to ECR first, then update `container_image` in `terraform.tfvars`.

## Documentation

- [AWS Provider Docs](https://registry.terraform.io/providers/hashicorp/aws/latest)
- [Terraform Best Practices](https://www.terraform.io/docs/language/values/locals)
- [ECS Fargate Pricing](https://aws.amazon.com/fargate/pricing/)
