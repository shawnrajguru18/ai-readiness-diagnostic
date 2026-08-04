# Deploying to AWS (ECS Express Mode + DynamoDB + Bedrock)

The app ships as a single container (`Dockerfile`, port 8080) running on **ECS Express Mode**
(simplified Fargate, no infrastructure management). Session state persists to **DynamoDB**
(via `app/store.py`), and LLM access goes through **AWS Bedrock** with Claude models
(SigV4 authentication via IAM task role — no API key needed).

```
Docker image ──push──▶ ECR ──pull──▶ ECS Fargate task ┬─▶ DynamoDB (sessions, IAM auth)
                                  (public IP, auto)   └─▶ Bedrock (Claude models, SigV4)
```

## What is in this directory

| | |
|---|---|
| **Scripts** | see the table below — both provisioning paths |
| **Runbooks** | [pre_destroy_checklist.md](pre_destroy_checklist.md), [post_destroy_validation.md](post_destroy_validation.md) |
| **Plans and records** | [deprovisioning_plan.md](deprovisioning_plan.md), [terraform_deployment.md](terraform_deployment.md) |
| **IAM** | [iam/forcemfa_policy_v2.json](iam/forcemfa_policy_v2.json) — the force-MFA policy the two `.ps1` scripts assume |

The general pre/post-release checklist is **not** here — it is target-agnostic and lives at
[../../docs/deployment/deploy_checklist.md](../../docs/deployment/deploy_checklist.md).
Everything else is indexed in [../../docs/INDEX.md](../../docs/INDEX.md).

### Scripts

There are **two provisioning paths**, and this directory now holds the scripts for both. Pick a
path and stay on it.

| Script | Path | What it does |
|---|---|---|
| `01-bootstrap.sh` → `02-deploy.sh` → `03-teardown.sh` (config in `config.sh`) | shell | The procedure documented below. |
| `deploy.ps1` | Terraform | Windows: MFA session token, then `terraform apply` on `terraform/`. |
| `push-image.ps1` | Terraform | Windows: MFA session token, push image to ECR, force an ECS redeploy. |
| `destroy_terraform.sh` | Terraform | `terraform destroy` with backups and confirmations. |
| `post_destroy_validation.sh` | **both** | Read-only check that resources are actually gone. Verifies both name sets. |

The two paths **overlap on some resources and diverge on others**, which is what makes mixing them
dangerous:

| Resource | shell (`config.sh`) | Terraform (`app_name`) |
|---|---|---|
| ECR repository | `ai-readiness-diagnostic` | `ai-readiness-diagnostic` — **same** |
| ECS service | `ai-readiness-diagnostic` | `ai-readiness-diagnostic` — **same** |
| IAM task role | `ai-readiness-diagnostic-task-role` | `ai-readiness-diagnostic-task-role` — **same** |
| CloudWatch log group | `/ecs/ai-readiness-diagnostic` | `/ecs/ai-readiness-diagnostic` — **same** |
| ECS **cluster** | `ai-readiness-cluster` | `ai-readiness-diagnostic-cluster` — **differs** |
| DynamoDB **table** | `ai-readiness-sessions` | `ai-readiness-diagnostic-sessions` — **differs** |

Consequences worth knowing before you run anything:

- A teardown script from the wrong path **reports success while deleting nothing** — the cluster and
  table it looks for do not exist under that name. `post_destroy_validation.sh` exists to catch this.
- Running both paths leaves **two clusters and two tables**, with the second table holding assessment
  data nobody is looking at, and both billing.
- Because the ECR repo and IAM role are shared, whichever path runs last **overwrites** them, and
  `push-image.ps1` pushes to that shared repo before redeploying only the Terraform cluster's service.

Before any teardown, work through
[pre_destroy_checklist.md](pre_destroy_checklist.md) —
step 2.3 is the check that establishes which path created the live resources.

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
the ECS cluster, the IAM task role (with Bedrock + DynamoDB permissions), and the execution role
(for ECR pull + CloudWatch logs). It's **idempotent** — safe to re-run.

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
- **DXC account guardrails:** SCPs / permission boundaries may block ECR, ECS, DynamoDB, or Bedrock in
  certain regions. Confirm your region is approved before running `01-bootstrap.sh`.
- **First deploy is slow:** Task pulling the image + starting can take 2-3 minutes. Subsequent deploys
  with the same image size take 1-2 minutes.
- **CloudWatch logs:** The deploy script creates a log group `/ecs/${APP_NAME}`. View logs with
  `aws logs tail /ecs/${APP_NAME} --follow --region ${AWS_REGION}`.
- **DynamoDB item size:** each session is stored as one JSON blob under a 400 KB item limit —
  fine for these scorecards; revisit if sessions ever grow large.

## Teardown

For the shell path, prefer the script — it deletes the set `config.sh` created:

```bash
cd deploy/aws
bash 03-teardown.sh
bash post_destroy_validation.sh   # read-only; confirms nothing survived under either name set
```

For the Terraform path use `bash deploy/aws/destroy_terraform.sh` instead.

The raw commands below are the shell path's teardown expanded, kept for reference:

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
