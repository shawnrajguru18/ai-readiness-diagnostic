# Deploying to AWS (ECS Express Mode + DynamoDB + Bedrock)

The app ships as a single container (`Dockerfile`, port 8080) running on **ECS Express Mode**
(simplified Fargate, no infrastructure management). Session state persists to **DynamoDB**
(via `app/store.py`), and LLM access goes through **AWS Bedrock** with Claude models
(SigV4 authentication via IAM task role — no API key needed).

```
Docker image ──push──▶ ECR ──pull──▶ ECS Fargate task ┬─▶ DynamoDB (sessions, IAM auth)
                                  (public IP, auto)   └─▶ Bedrock (Claude models, SigV4)
```

## Prerequisites
- **AWS CLI v2**, authenticated to the target account. At DXC this is typically SSO:
  `aws sso login` (or `aws configure sso` the first time).
- **Docker** running locally (needed to build/push the image).
- Permission to create ECR, DynamoDB, ECS, IAM, CloudWatch Logs, and access Bedrock models.
- **jq** installed locally (used to parse JSON in the deploy script).
- Bedrock models (`anthropic.claude-3-5-sonnet-20241022-v2:0`, `anthropic.claude-3-5-haiku-20241022-v1:0`)
  must be enabled in the region (check **Bedrock → Model Access** in the AWS console; models may require
  opt-in per region).
- Default VPC with at least one subnet and security group (AWS creates these automatically in most accounts).
- Run everything from **Git Bash / WSL / Linux / macOS** (the scripts are bash).

## One-time setup
```bash
cd deploy/aws
# optional overrides: export AWS_REGION=us-west-2  APP_NAME=ai-readiness-diagnostic  CLUSTER_NAME=my-cluster
bash 01-bootstrap.sh
```
This creates the ECR repo, the DynamoDB table (`ai-readiness-sessions`, on-demand, PK `id`),
the ECS cluster, and the IAM task role (with Bedrock + DynamoDB permissions). It's **idempotent**.

Credentials are resolved from the ECS task role via SigV4 authentication — no secrets needed.
The default ecsTaskExecutionRole is assumed to exist; if not, create it:
```bash
aws iam create-role --role-name ecsTaskExecutionRole \
  --assume-role-policy-document '{
    "Version":"2012-10-17",
    "Statement":[{"Effect":"Allow","Principal":{"Service":"ecs-tasks.amazonaws.com"},"Action":"sts:AssumeRole"}]
  }'
aws iam attach-role-policy --role-name ecsTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
```

## Deploy (repeat for every release)
```bash
cd deploy/aws
bash 02-deploy.sh
```
Builds the Docker image, pushes to ECR, registers a task definition, creates-or-updates
the ECS service, waits for tasks to stabilize, and prints the public IP:port. The first
deploy takes 2-3 minutes (image pull + container start); subsequent deploys take 1-2 minutes.

## Configuration knobs
All overridable via env vars before running the scripts (see `config.sh`):

| Var | Default | Purpose |
|-----|---------|---------|
| `AWS_REGION` | `us-east-1` | Target region |
| `APP_NAME` | `ai-readiness-diagnostic` | ECR repo + ECS service/task name |
| `CLUSTER_NAME` | `ai-readiness-cluster` | ECS cluster name |
| `DDB_TABLE` | `ai-readiness-sessions` | DynamoDB table (also set as `AIDIAG_DDB_TABLE` env var in tasks) |
| `TASK_CPU` / `TASK_MEMORY` | `1024` / `2048` | CPU units / memory in MB (valid combos: 256/512, 512/1024-3072, 1024/2048-8192, etc.) |
| `TASK_COUNT` | `1` | Desired number of running tasks |

The container flips to DynamoDB **only** when `AIDIAG_DDB_TABLE` is set (the deploy script sets it).
Bedrock access is always on when AWS credentials are present; set `AIDIAG_MODEL_*` env vars to override
model IDs. Locally, with `AIDIAG_DDB_TABLE` unset and no AWS credentials, it uses the in-memory store
and deterministic offline pipeline — no AWS needed.

## Gotchas
- **Bedrock model access:** Models are controlled per-region in the **Bedrock console → Model Access**.
  If models show "No access", click → "Request access" and wait for approval (usually instant, 5 min max).
  If access is denied or not enabled, the app falls back to the deterministic offline pipeline.
- **Default VPC:** The deploy script uses your account's default VPC and security group. If you don't have
  a default VPC, create one in the VPC console or use custom subnets by editing the script.
- **IAM roles:** `ecsTaskExecutionRole` must exist; create it if `01-bootstrap.sh` fails. The task role
  is created by bootstrap and is service-linked (auto-cleanup).
- **DXC account guardrails:** SCPs / permission boundaries may block ECR, ECS, DynamoDB, or Bedrock in
  certain regions. Confirm your region is approved before running `01-bootstrap.sh`.
- **First deploy is slow:** Task pulling the image + starting can take 2-3 minutes. Subsequent deploys
  with the same image size take 1-2 minutes.
- **CloudWatch logs:** The deploy script creates a log group `/ecs/${APP_NAME}`. View logs with
  `aws logs tail /ecs/${APP_NAME} --follow --region ${AWS_REGION}`.
- **DynamoDB item size:** each session is stored as one JSON blob under a 400 KB item limit —
  fine for these scorecards; revisit if sessions ever grow large.

## Teardown
```bash
# Delete ECS service and cluster
aws ecs delete-service --cluster ai-readiness-cluster --service ai-readiness-diagnostic --region us-east-1 --force
aws ecs delete-cluster --cluster ai-readiness-cluster --region us-east-1

# Delete DynamoDB and ECR
aws dynamodb delete-table --table-name ai-readiness-sessions --region us-east-1
aws ecr delete-repository --repository-name ai-readiness-diagnostic --region us-east-1 --force

# Delete IAM task role created by 01-bootstrap.sh
aws iam delete-role-policy --role-name ai-readiness-diagnostic-task-role --policy-name app-permissions
aws iam delete-role --role-name ai-readiness-diagnostic-task-role

# Delete CloudWatch logs
aws logs delete-log-group --log-group-name /ecs/ai-readiness-diagnostic --region us-east-1
```
