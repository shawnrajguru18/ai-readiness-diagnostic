# Terraform Deployment - Switched from Bash to IaC

**Date:** 2026-07-22  
**Status:** ✅ Successfully deployed  
**App URL:** http://13.220.187.193:8080

## Summary

Successfully migrated from Bash script-based deployment to Infrastructure-as-Code (IaC) using Terraform. The application is now fully managed by Terraform, providing better version control, state management, and repeatability.

## What Was Deployed

### Infrastructure (via Terraform)
All AWS resources created through `terraform apply`:

1. **ECR Repository**
   - `ai-readiness-diagnostic`
   - Region: `us-east-1`
   - URL: `023138541872.dkr.ecr.us-east-1.amazonaws.com/ai-readiness-diagnostic`
   - Lifecycle policy: Keep last 5 images

2. **ECS Cluster**
   - Name: `ai-readiness-diagnostic-cluster`
   - Type: ECS (not EC2-backed)
   - Capacity providers: FARGATE

3. **ECS Service**
   - Name: `ai-readiness-diagnostic`
   - Task definition: `ai-readiness-diagnostic`
   - Desired count: 1 task
   - Launch type: FARGATE
   - Public IP: Enabled (auto-assigned)
   - Health check: HTTP GET on port 8080

4. **ECS Task Definition**
   - CPU: 1024 units
   - Memory: 2048 MB
   - Container image: `023138541872.dkr.ecr.us-east-1.amazonaws.com/ai-readiness-diagnostic:latest`
   - Port mapping: 8080 (container) → 8080 (host)
   - Environment variables:
     - `AIDIAG_DDB_TABLE=ai-readiness-diagnostic-sessions` (enables DynamoDB)
     - `AWS_REGION=us-east-1`

5. **DynamoDB Table**
   - Name: `ai-readiness-diagnostic-sessions`
   - Billing mode: On-demand (pay per request)
   - Primary key: `id` (string)
   - Item size limit: 400 KB (suitable for session data)

6. **IAM Roles**
   - **Task Role** (`ai-readiness-diagnostic-task-role`)
     - Permissions: Bedrock (invoke Claude models), DynamoDB (read/write sessions)
   
   - **Execution Role** (`ai-readiness-diagnostic-execution-role`)
     - Permissions: ECR (pull images), CloudWatch (write logs)

7. **CloudWatch Logs**
   - Log group: `/ecs/ai-readiness-diagnostic`
   - Log stream: created per task

8. **Security Group**
   - Name: `ai-readiness-diagnostic-ecs-tasks`
   - Inbound: Allow TCP port 8080 from 0.0.0.0/0
   - Outbound: Allow all traffic

9. **VPC & Networking**
   - VPC: `vpc-0ce6b8e49eae25738` (DXC account default)
   - Subnets: 3 public subnets configured
   - Network interface: `eni-0ac40c389c8ecdcb0`
   - Public IP: `13.220.187.193`

### Application (via Docker)
Docker image built and pushed to ECR:

1. **Image Build**
   - Base image: `python:3.12-slim`
   - Dependencies: Installed from `requirements.txt`
   - Application files: Copied to `/app`
   - Entrypoint: `python -m uvicorn app.api:app --host 0.0.0.0 --port 8080`
   - Health check: `curl http://localhost:8080` every 30 seconds

2. **Image Push**
   - Registry: `023138541872.dkr.ecr.us-east-1.amazonaws.com/ai-readiness-diagnostic:latest`
   - Digest: `sha256:61071f0b73ffac9707a015b6ccc92d3ee32206536ca83f6e7b1b9de609ba32d0`
   - Size: 856 MB
   - Layers: 11 pushed

## Step-by-Step Deployment Process

### Prerequisites
- AWS CLI v2 with MFA authentication
- Docker installed and running
- Terraform installed
- Access to DXC AWS account (023138541872)

### 1. Authentication (MFA Required)

```bash
aws sts get-session-token \
  --duration-seconds 3600 \
  --serial-number arn:aws:iam::023138541872:mfa/AWS-Sandbox-Axis \
  --token-code <6-digit-code>
```

**Output:** 3 credentials
- `AccessKeyId`: ASIAQKYZKEEYG6IWYKEO
- `SecretAccessKey`: l9JYCkFWVs/I7RJ3fG6EAjqlNsqjFdXKMJRAN0w3
- `SessionToken`: (long token string)

Set as environment variables in Bash:
```bash
export AWS_ACCESS_KEY_ID="ASIAQKYZKEEYG6IWYKEO"
export AWS_SECRET_ACCESS_KEY="l9JYCkFWVs/I7RJ3fG6EAjqlNsqjFdXKMJRAN0w3"
export AWS_SESSION_TOKEN="..."
```

### 2. Initialize Terraform

```bash
cd terraform/
terraform init
```

**Output:** Terraform initialized, AWS provider v5.100.0 loaded

### 3. Plan Infrastructure

```bash
terraform plan -out=tfplan
```

**Output:** Plan shows 15 resources to be added:
- 1 ECR repository
- 1 ECS cluster
- 1 ECS service
- 1 ECS task definition
- 1 DynamoDB table
- 2 IAM roles
- 3 IAM policies
- 1 CloudWatch log group
- 1 Security group
- Additional supporting resources

### 4. Apply Infrastructure

```bash
terraform apply tfplan
```

**Process:**
1. Create ECR repository (1s)
2. Create IAM roles (1s)
3. Create CloudWatch log group (1s)
4. Create security group (4s)
5. Create ECS cluster (11s) - waited for cluster stabilization
6. Create DynamoDB table (14s)
7. Create ECS task definition (0s)
8. Register capacity providers (11s)
9. Create ECS service (1s)

**Total time:** ~45 seconds

**Output:** All 15 resources created successfully

### 5. Build Docker Image

```bash
docker build -t ai-readiness-diagnostic .
```

**Process:**
- Base image: `python:3.12-slim`
- Install dependencies: `pip install -r requirements.txt`
- Copy application code
- Export as `docker.io/library/ai-readiness-diagnostic:latest`

**Total time:** ~70 seconds (includes context transfer of ~750 MB)

### 6. Login to ECR

```bash
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 023138541872.dkr.ecr.us-east-1.amazonaws.com
```

**Output:** `Login Succeeded`

### 7. Tag and Push to ECR

```bash
docker tag ai-readiness-diagnostic:latest \
  023138541872.dkr.ecr.us-east-1.amazonaws.com/ai-readiness-diagnostic:latest

docker push 023138541872.dkr.ecr.us-east-1.amazonaws.com/ai-readiness-diagnostic:latest
```

**Process:**
- Push 11 image layers
- Total size: 856 MB
- Digest: `sha256:61071f0b73ffac9707a015b6ccc92d3ee32206536ca83f6e7b1b9de609ba32d0`

**Total time:** ~5 minutes (network dependent)

### 8. ECS Service Auto-Pulls and Starts

Once image is in ECR:
1. ECS service detects new image
2. Pulls image from ECR
3. Launches new task
4. Assigns public IP: `13.220.187.193`
5. Health checks pass
6. Task becomes RUNNING

**Total time:** ~2-3 minutes

## Verification

### Check ECS Service Status

```bash
aws ecs describe-services \
  --cluster ai-readiness-diagnostic-cluster \
  --services ai-readiness-diagnostic \
  --region us-east-1
```

### Check Task Status

```bash
aws ecs list-tasks --cluster ai-readiness-diagnostic-cluster --region us-east-1
aws ecs describe-tasks --cluster ai-readiness-diagnostic-cluster --tasks <task-arn> --region us-east-1
```

### View Logs

```bash
aws logs tail /ecs/ai-readiness-diagnostic --follow --region us-east-1
```

### Access Application

**URL:** http://13.220.187.193:8080

**Endpoints:**
- GET `/` - React UI (5 screens: Landing, Questionnaire, Scorecard, Quick Wins)
- POST `/api/questions` - Get 20-question pool
- POST `/api/assess` - Submit answers, get scoring
- POST `/api/fixture/{name}` - Load demo fixtures (meridianfs, northerncare, aureliantech)

## Key Improvements Over Bash Scripts

| Aspect | Bash Scripts | Terraform |
|--------|-------------|-----------|
| **State Management** | Implicit (query AWS) | Explicit (terraform.tfstate) |
| **Idempotency** | Manual checks | Built-in |
| **Version Control** | Not versioned | Git tracked |
| **Rollback** | Manual cleanup | `terraform destroy` |
| **Team Collaboration** | Difficult | Easy (with remote state) |
| **Infrastructure Docs** | Ad-hoc | Declarative (IaC) |
| **Dependency Tracking** | Manual | Automatic graph |

## Terraform File Structure

```
terraform/
├── main.tf            # Provider configuration
├── variables.tf       # Input variables (region, app_name, etc.)
├── outputs.tf         # Output values (URLs, ARNs, etc.)
├── iam.tf             # IAM roles and policies
├── ecr.tf             # ECR repository and lifecycle
├── ecs.tf             # ECS cluster, service, task definition
├── dynamodb.tf        # DynamoDB table
├── security.tf        # Security groups
├── terraform.tfvars   # Variable values
└── terraform.tfstate  # State file (DO NOT commit)
```

## Important Notes

### MFA Session Token Expiration
- Session tokens expire after 1 hour (3600 seconds)
- If you get "ExpiredToken" error, regenerate token and set env vars again
- Always get fresh 6-digit code from authenticator app (expires every 30s)

### Cost Estimation (Monthly)
- ECS Fargate (1024 CPU, 2048 MB): ~$11/month
- DynamoDB (on-demand): ~$0.25/M reads + $1.25/M writes
- ECR storage: ~$0.10/month
- CloudWatch logs: ~$0.50/month
- **Total:** ~$12-15/month

### Scaling
To increase desired task count:
```bash
# Edit terraform.tfvars: desired_count = 2
terraform apply
```

To enable autoscaling:
```bash
# Edit terraform.tfvars: enable_autoscaling = true
terraform apply
```

### Managing Terraform State

**Current:** Local state file (`terraform.tfstate`)

**For team collaboration (recommended):**
1. Create S3 bucket: `aws s3 mb s3://ai-readiness-tfstate-023138541872`
2. Add to `main.tf`:
```hcl
terraform {
  backend "s3" {
    bucket = "ai-readiness-tfstate-023138541872"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}
```
3. Run: `terraform init`

## Next Steps

1. **Monitor the application:**
   - Watch logs: `aws logs tail /ecs/ai-readiness-diagnostic --follow --region us-east-1`
   - Check health: `curl http://13.220.187.193:8080/api/health` (if endpoint exists)

2. **Test the application:**
   - Navigate to http://13.220.187.193:8080
   - Complete a 20-question assessment
   - Verify scoring, findings, and quick wins

3. **Set up alerts (optional):**
   - CloudWatch alarms for ECS task failures
   - CloudWatch alarms for high error rates in logs

4. **Backup Terraform state:**
   - Commit `.tfstate.backup` to git (optional but recommended)
   - Set up remote state in S3 for production

5. **Document your AWS account:**
   - Add to team wiki: Terraform-managed resources at account 023138541872

## Rollback / Cleanup

To destroy all infrastructure and start fresh:

```bash
terraform destroy
```

**Warning:** This will delete:
- ECS service and cluster
- DynamoDB table
- ECR repository
- IAM roles
- CloudWatch logs

To keep infrastructure but stop tasks:
```bash
aws ecs update-service \
  --cluster ai-readiness-diagnostic-cluster \
  --service ai-readiness-diagnostic \
  --desired-count 0 \
  --region us-east-1
```

## Support / Troubleshooting

**Task fails to start:** Check logs for Bedrock/DynamoDB auth errors
```bash
aws logs tail /ecs/ai-readiness-diagnostic --region us-east-1 | grep -i error
```

**Cannot reach app:** Verify security group allows inbound 8080
```bash
aws ec2 describe-security-groups --group-ids sg-07c758c00004ec6f5 --region us-east-1
```

**MFA token expired:** Regenerate with fresh authenticator code
```bash
aws sts get-session-token --serial-number arn:aws:iam::023138541872:mfa/AWS-Sandbox-Axis --token-code <NEW_CODE>
```

---

**Deployed by:** Claude Haiku 4.5  
**Commit:** 84d300a (Switch to Bedrock inference profiles)  
**Infrastructure:** Terraform v1.0+  
**Application:** Python 3.12, FastAPI, React
