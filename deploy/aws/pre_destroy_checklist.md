# Pre-Destroy Checklist

**Complete this before running any teardown.**
Converted from `pre_destroy_checklist.txt` (2026-07-10) without changing the checks.

| | |
|---|---|
| AWS account | `023138541872` |
| Region | `us-east-1` |
| Teardown script | `deploy/aws/destroy_terraform.sh` |
| Afterwards | `bash deploy/aws/post_destroy_validation.sh`, then `post_destroy_validation.md` |

> **Two provisioning paths, two sets of resource names.** `deploy/aws/config.sh` creates
> `ai-readiness-cluster` and `ai-readiness-sessions`; `terraform/` creates
> `ai-readiness-diagnostic-cluster` and `ai-readiness-diagnostic-sessions`. Establish which path
> created the live resources **before** you destroy, or a `terraform destroy` will report success
> while the real resources keep running. Section 2.3 covers this.

---

## 1. Backup and verification

- [ ] **1.1 Export DynamoDB data**
      ```bash
      aws dynamodb scan --table-name ai-readiness-sessions --region us-east-1 \
        --output json > ai-readiness-sessions-backup-$(date +%Y%m%d).json
      ```
      Verify: `du -h ai-readiness-sessions-backup-*.json`

- [ ] **1.2 Export CloudWatch logs**
      ```bash
      aws logs tail /ecs/ai-readiness-diagnostic --region us-east-1 --follow=false \
        > cloudwatch-logs-$(date +%Y%m%d).txt
      ```
      Verify: `wc -l cloudwatch-logs-*.txt`

- [ ] **1.3 Back up Terraform state**
      ```bash
      cd terraform && cp terraform.tfstate terraform.tfstate.backup.$(date +%Y%m%d)
      ```
      Verify: `ls -la terraform/terraform.tfstate.backup.*`

- [ ] **1.4 Confirm the data is test-only** — ⚠️ **STOP if you see production or customer data.**
      ```bash
      jq '.Items[0:5] | map(.id.S)' ai-readiness-sessions-backup-*.json
      ```
      Expected: only test fixture IDs — MeridianFS, NorthernCare, AurelianTech.

- [ ] **1.5 Confirm no credentials in the log export** — ⚠️ **STOP if credentials are exposed.**
      ```bash
      grep -i "password\|secret\|key\|credential" cloudwatch-logs-*.txt
      ```
      Expected: no results, or application logs only.

## 2. Terraform validation

- [ ] **2.1 Configuration is valid**
      `cd terraform && terraform validate` → *Success! The configuration is valid.*

- [ ] **2.2 State resource count**
      `cd terraform && terraform state list | wc -l` → expect ~15.
      Actual count: `______`

- [ ] **2.3 List what will be destroyed — and confirm it is what is actually deployed**
      ```bash
      cd terraform && terraform state list
      ```
      Cross-check against the live resources. If state lists
      `ai-readiness-diagnostic-sessions` but the running table is `ai-readiness-sessions`, the
      resources were created by `deploy/aws/` and Terraform will not remove them — use
      `deploy/aws/03-teardown.sh` instead, or import them first.
      Resources found: `______`

- [ ] **2.4 Review the destroy plan (dry run)**
      ```bash
      cd terraform && terraform plan -destroy -out=destroy.tfplan
      ```
      Confirm the destruction targets match expectations.

- [ ] **2.5 Sanity-check the Terraform files**
      `ls -la terraform/*.tf` → expect `main.tf`, `ecs.tf`, `dynamodb.tf`, `ecr.tf`, `iam.tf`,
      `security.tf`.

## 3. AWS account verification

- [ ] **3.1 Credentials point at the right account** — ⚠️ **STOP if the account is not
      `023138541872`.**
      ```bash
      aws sts get-caller-identity
      ```

- [ ] **3.2 Region is `us-east-1`** — ⚠️ **STOP if wrong.**
      `aws configure get region`

- [ ] **3.3 The expected resources currently exist**
      Confirm in the console or CLI: ECS cluster, ECS service, DynamoDB table, ECR repository,
      CloudWatch log group. Note the exact names you find — this is the check that resolves 2.3.

- [ ] **3.4 No production URL or DNS points at the test IP** — ⚠️ **STOP if a test IP is hardcoded
      in production config.**
      ```bash
      grep -r "54.236.26.147\|54.209.53.225" . \
        --include="*.py" --include="*.js" --include="*.yaml" --include="*.md"
      ```

## 4. Git and documentation

- [ ] **4.1 All work committed** — ⚠️ **STOP if there are uncommitted changes.** `git status`
- [ ] **4.2 Recent commits reviewed** — `git log --oneline | head -5`
- [ ] **4.3 Remote is correct** — `git remote -v`
- [ ] **4.4 This checklist is saved** — it is, in git.

## 5. External dependencies

- [ ] **5.1 Nothing else depends on the test endpoint.** Does any other application reference
      `http://54.236.26.147:8080`? If yes, update it first.
- [ ] **5.2 No load balancer targets this service**
      `aws elbv2 describe-target-groups --region us-east-1 | grep ai-readiness` → expect nothing.
- [ ] **5.3 No CloudWatch alarms reference these resources**
      `aws cloudwatch describe-alarms --alarm-names "ai-readiness*" --region us-east-1`

---

## Sign-off

All pre-destroy checks completed: **[ ] YES**

| | |
|---|---|
| Date and time | |
| Verified by | |
| Team lead (if required) | |

Notes:

---

## Then proceed

1. `bash deploy/aws/destroy_terraform.sh` — or `cd terraform && terraform destroy`
2. Type `yes` when prompted.
3. Watch for errors.
4. `bash deploy/aws/post_destroy_validation.sh` — automated verification.
5. Work through [post_destroy_validation.md](post_destroy_validation.md) for the manual steps.
