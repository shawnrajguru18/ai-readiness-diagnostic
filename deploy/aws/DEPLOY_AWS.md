# Deploying to AWS (App Runner + DynamoDB + Bedrock)

The app ships as a single container (`Dockerfile`, port 8080). Session state persists to
**DynamoDB** (via `app/store.py`), and LLM access goes through **AWS Bedrock** with Claude models
(SigV4 authentication via IAM roles — no API key needed). The container's IAM instance role
grants Bedrock + DynamoDB access; `.dockerignore` excludes `.env`.

```
Docker image ──push──▶ ECR ──pull──▶ App Runner service ┬─▶ DynamoDB (sessions, IAM auth)
                                            (IAM role)   └─▶ Bedrock (Claude models, SigV4)
```

## Prerequisites
- **AWS CLI v2**, authenticated to the target account. At DXC this is typically SSO:
  `aws sso login` (or `aws configure sso` the first time).
- **Docker** running locally (needed to build/push the image).
- Permission to create ECR, DynamoDB, IAM, App Runner, and access Bedrock models.
- Bedrock models (`anthropic.claude-3-5-sonnet-20241022-v2:0`, `anthropic.claude-3-5-haiku-20241022-v1:0`)
  must be enabled in the region (check Bedrock → Model Access in the AWS console; models may require
  opt-in per region).
- Run everything from **Git Bash / WSL / Linux / macOS** (the scripts are bash).

## One-time setup
```bash
cd deploy/aws
# optional overrides: export AWS_REGION=us-west-2  APP_NAME=ai-readiness-diagnostic
bash 01-bootstrap.sh
```
This creates the ECR repo, the DynamoDB table (`ai-readiness-sessions`, on-demand, PK `id`),
and the two IAM roles App Runner needs (with Bedrock + DynamoDB permissions). It's **idempotent**.

Credentials are resolved from the App Runner instance role via SigV4 authentication — no secrets needed.

## Deploy (repeat for every release)
```bash
cd deploy/aws
bash 02-deploy.sh
```
Builds the image, pushes to ECR, creates-or-updates the App Runner service, waits for
`RUNNING`, and prints the HTTPS URL. `AutoDeploymentsEnabled` is on, so pushing a new
`:latest` to ECR also triggers a redeploy.

## Configuration knobs
All overridable via env vars before running the scripts (see `config.sh`):

| Var | Default | Purpose |
|-----|---------|---------|
| `AWS_REGION` | `us-east-1` | Target region (also used by Bedrock client for model access) |
| `APP_NAME` | `ai-readiness-diagnostic` | ECR repo + App Runner service name |
| `DDB_TABLE` | `ai-readiness-sessions` | DynamoDB table (also set as `AIDIAG_DDB_TABLE` in the service) |
| `APP_CPU` / `APP_MEMORY` | `1024` / `2048` | 1 vCPU / 2 GB |

The container flips to DynamoDB **only** when `AIDIAG_DDB_TABLE` is set (the deploy script sets it).
Bedrock access is always on when AWS credentials are present; set `AIDIAG_MODEL_*` env vars to override
model IDs. Locally, with `AIDIAG_DDB_TABLE` unset and no AWS credentials, it uses the in-memory store
and deterministic offline pipeline — no AWS needed.

## Gotchas
- **Bedrock model access:** Models are controlled per-region in the Bedrock console. If models show
  "No access", click → "Request access" and wait for approval (usually instant, but check in 5 min).
  If access is denied or not enabled, the app falls back to the deterministic offline pipeline.
- **IAM permissions:** If `01-bootstrap.sh` fails on IAM role creation, DXC SCPs / permission boundaries
  may block role creation for specific patterns. Work with your AWS account owner to approve the role ARN.
- **DXC account guardrails:** SCPs / permission boundaries may block ECR, App Runner, Bedrock, or DynamoDB
  in certain regions. Confirm your region is approved before running `01-bootstrap.sh`.
- **First deploy is slow:** App Runner provisioning + image pull can take several minutes.
- **DynamoDB item size:** each session is stored as one JSON blob under a 400 KB item limit —
  fine for these scorecards; revisit if sessions ever grow large.

## Teardown
```bash
aws apprunner delete-service --region us-east-1 --service-arn <arn>   # from list-services
aws dynamodb delete-table --table-name ai-readiness-sessions --region us-east-1
aws ecr delete-repository --repository-name ai-readiness-diagnostic --region us-east-1 --force
# then delete the two IAM roles (${APP_NAME}-instance-role and ${APP_NAME}-ecr-access-role) created by 01-bootstrap.sh
aws iam delete-role-policy --role-name ai-readiness-diagnostic-instance-role --policy-name app-permissions
aws iam delete-role --role-name ai-readiness-diagnostic-instance-role
aws iam detach-role-policy --role-name ai-readiness-diagnostic-ecr-access-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess
aws iam delete-role --role-name ai-readiness-diagnostic-ecr-access-role
```
