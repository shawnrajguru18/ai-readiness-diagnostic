# AWS Deprovisioning Plan: AI Readiness Diagnostic MVP

**Project:** DXC AI Readiness Diagnostic MVP  
**AWS Account:** 023138541872  
**Region:** us-east-1  
**Environment:** Test/Production Deployment  
**Date:** 2026-07-10  
**Method:** Terraform Destroy (Primary) + Safe Verification Checklist

---

## Executive Summary

This document outlines a **safe, reversible deprovisioning plan** using **Terraform destroy** to tear down AWS resources created by the Infrastructure-as-Code deployment. Terraform automatically handles dependency ordering and sequencing.

**Primary Method:** `terraform destroy` from `/terraform` directory
- Automatically handles resource dependency graph
- Respects creation order in reverse
- State file tracking ensures consistency
- Safer than manual AWS CLI deletion

**Scope:** All resources created by the Terraform IaC deployment:
- ECS Cluster + Service + Task Definition
- ECR Repository (with images)
- DynamoDB Table (with historical data)
- CloudWatch Logs
- IAM Roles & Policies
- Security Group
- Network configuration

**NOT included in scope:**
- Default VPC (shared AWS infrastructure - Terraform doesn't manage it)
- Default subnets (shared AWS infrastructure - Terraform doesn't manage it)
- Any manually created resources outside Terraform

---

## 1. Pre-Destruction Inventory

### 1.1 AWS Resources to be Deleted

| Resource Type | Resource Name | ID/ARN | Notes |
|---|---|---|---|
| **ECS Cluster** | ai-readiness-cluster | (discovered) | Contains running service |
| **ECS Service** | ai-readiness-diagnostic | (discovered) | Currently active, must be scaled to 0 |
| **ECS Task Definition** | ai-readiness-diagnostic | (discovered) | Latest revision, can have multiple |
| **CloudWatch Log Group** | /ecs/ai-readiness-diagnostic | (discovered) | 7-day retention policy |
| **DynamoDB Table** | ai-readiness-sessions | (discovered) | On-demand billing, has PITR enabled |
| **ECR Repository** | ai-readiness-diagnostic | (discovered) | Contains Docker images |
| **ECR Lifecycle Policy** | (auto-managed) | (discovered) | Attached to ECR repo |
| **Security Group** | ai-readiness-diagnostic-ecs-tasks | sg-094e244f45432489d | Only custom SG created |
| **IAM Role (Task)** | ai-readiness-diagnostic-task-role | (discovered) | Contains policies for DynamoDB, Bedrock |
| **IAM Role (Execution)** | ai-readiness-diagnostic-execution-role | (discovered) | Contains ECR pull permissions |
| **IAM Policies** | (5 inline policies) | (discovered) | Attached to above roles |

### 1.2 Current Resource Counts

**Before Deprovisioning:**
- ECS Clusters: 1
- ECS Services: 1
- ECS Task Definitions: ~5-10 (historical revisions)
- ECS Running Tasks: 1
- CloudWatch Log Groups: 1
- DynamoDB Tables: 1
- ECR Repositories: 1
- ECR Images: ~10-20 (depends on deployment history)
- Security Groups: 1 (custom)
- IAM Roles: 2
- IAM Inline Policies: 5

**After Deprovisioning:**
- All above: 0

---

## 2. Terraform Destroy Dependency Handling

**How Terraform Manages Destruction:**

Terraform automatically determines the correct deletion order by analyzing the resource dependency graph. Resources are deleted in **reverse dependency order**:

```
Terraform State Graph (used for reverse deletion):

aws_ecs_service.app
    ├─ depends_on: aws_ecs_task_definition.app
    ├─ depends_on: aws_security_group.ecs_tasks
    ├─ depends_on: aws_iam_role_policy.task_role_dynamodb
    └─ depends_on: aws_iam_role_policy.task_role_bedrock

aws_ecs_task_definition.app
    ├─ depends_on: aws_iam_role.execution_role
    └─ depends_on: aws_iam_role.task_role

aws_dynamodb_table.sessions
    └─ referenced_by: aws_iam_role_policy.task_role_dynamodb

aws_iam_role.task_role
    ├─ depends_on: aws_iam_role_policy.task_role_dynamodb
    └─ depends_on: aws_iam_role_policy.task_role_bedrock
```

**Destruction Order (automatically handled by Terraform):**

```
1. ECS Service (depends on everything below)
   └─ releases: Security Group ENI, IAM task role binding

2. ECS Task Definition (depends on IAM roles)
   └─ deregisters all revisions

3. ECS Cluster (depends on service)
   └─ becomes empty after service deleted

4. CloudWatch Log Group (independent)
   └─ can be deleted in parallel

5. DynamoDB Table (independent)
   └─ triggers PITR backup (35-day retention)

6. ECR Repository (independent)
   └─ must be empty before deletion

7. Security Group (depends on ECS tasks detaching)
   └─ deleted after all ENIs released

8. IAM Role Policies (inline policies)
   └─ automatically deleted with roles

9. IAM Roles (task & execution)
   └─ final cleanup

**No manual sequencing needed** — Terraform handles all of this automatically.
```

---

## 3. Quick Start: Terraform Destroy

### Prerequisites

```bash
# Verify you are in the correct directory
cd terraform/

# Verify AWS credentials are set
aws sts get-caller-identity

# Verify Terraform is initialized
terraform init

# Verify Terraform state is valid
terraform validate
terraform state list  # Should show ~15 resources
```

### Quick Destroy (5 minutes)

**For environments where you're confident no production data exists:**

```bash
cd terraform/

# Single command with auto-approval
terraform destroy -auto-approve

# Or with interactive prompts (recommended):
terraform destroy
# Review the plan, type 'yes' to confirm
```

**That's it.** Terraform handles everything else automatically.

### Step-by-Step Destroy (Recommended)

Follow the checklist below, then run:

```bash
cd terraform/

# 1. Review what will be deleted
terraform plan -destroy

# 2. Create backup (see section 4 below)
# 3. Run pre-destroy checklist (see section 5 below)

# 4. Execute destroy
terraform destroy

# 5. Verify results (see section 6 below)
```

---

## 4. Pre-Destruction Checklist

### 4.1 Data Backup & Verification (SAFE - No Deletion)

**Goal:** Ensure no data loss and verify test-only resources

```bash
# Export entire DynamoDB table to JSON file
aws dynamodb scan \
  --table-name ai-readiness-sessions \
  --region us-east-1 \
  --output json > ai-readiness-sessions-backup-$(date +%Y%m%d).json

# Verify backup
du -h ai-readiness-sessions-backup-*.json
jq '.Items | length' ai-readiness-sessions-backup-*.json

# Check if data is test-only (should see fixture names)
jq '.Items[0:5]' ai-readiness-sessions-backup-*.json
```

**Expected Output:**
- JSON file with all session records (should be < 1 MB for test data)
- Item count: ~3-10 test fixtures (MeridianFS, NorthernCare, AurelianTech)
- NO production customer data

**Verification Checklist:**
- [ ] Backup file created successfully
- [ ] DynamoDB contains ONLY test fixtures
- [ ] No production credentials in data
- [ ] No customer PII or sensitive data

#### Export CloudWatch Logs

```bash
# Export logs to local file for archival
aws logs tail /ecs/ai-readiness-diagnostic \
  --region us-east-1 \
  --follow=false \
  --no-newline > cloudwatch-logs-$(date +%Y%m%d).txt

# Verify export
du -h cloudwatch-logs-*.txt
head -20 cloudwatch-logs-*.txt
```

**Expected Output:**
- Log file with 7 days of logs (size depends on traffic)
- Logs show only test requests/container startup
- No sensitive credentials in logs

#### Verify Terraform State

```bash
cd terraform/

# Verify state file exists and is valid
terraform validate
echo "Expected resources in state:"
terraform state list | wc -l
# Should be ~15 resources

# Dry run: see exactly what will be destroyed
terraform plan -destroy
```

**Verification Checklist:**
- [ ] terraform validate passes with no errors
- [ ] ~15 resources shown in `terraform state list`
- [ ] No state file lock (.terraform.lock.hcl issues)
- [ ] Terraform plan shows all resources for destruction
- [ ] Backups created (DynamoDB JSON, logs, state file)

---

## 4. Cost Impact Analysis

### 4.1 Before Deprovisioning (Monthly Costs)

| Resource | Monthly Cost | Notes |
|---|---|---|
| **ECS Fargate** | ~$15-30 | 1 task × 1024 CPU × 2048 MB × 730 hours |
| **DynamoDB** | ~$5-10 | On-demand, pay-per-request (test usage) |
| **ECR Storage** | ~$2-5 | ~1-2 GB of images at $0.10/GB-month |
| **CloudWatch Logs** | ~$1-3 | 7-day retention, ~100MB/day ingestion |
| **CloudWatch Container Insights** | ~$5 | Per-cluster monitoring |
| **NAT Gateway** | ~$32 | 1 × $0.045/hour + data transfer |
| **Data Transfer** | ~$2-5 | Minimal for test |
| **VPC Endpoints** | $0 | Using default VPC (no extra costs) |
| **Total** | **~$62-88/month** | **Estimated** |

### 4.2 After Deprovisioning (Monthly Costs)

| Resource | Monthly Cost | Notes |
|---|---|---|
| **All Deleted Resources** | $0 | Complete removal |
| **Total** | **$0** | Full cost recovery |

### 4.3 Cost Recovery Timeline

- **Immediate (Day 0):** $0 costs as soon as resources are deleted
- **No Refunds:** AWS does not refund proportional costs for deleted resources mid-month
- **Benefit:** Resources deleted on 2026-07-10 will not incur charges for remainder of month (already billed)
- **Next Billing Cycle:** July 11 onwards shows $0 charges for these resources

**Example:**
- If $60/month deployment runs for 10 days, cost is ~$20
- Deleting on day 10 does NOT refund the $20
- Days 11-31 will show $0 costs
- Next month (August onwards) shows $0 if not redeployed

---

## 5. Post-Destroy Verification

### 5.1 Verify Terraform Destroy Completed

```bash
cd terraform/

# Check state file is empty
terraform state list
# Should return: (empty - no resources)

# Double-check: list state resources
terraform state list 2>&1 | wc -l
# Should be 0

# View state file to confirm
cat terraform.tfstate | jq '.resources | length'
# Should be 0
```

### 5.2 Verify AWS Resources Deleted

```bash
# ECS Cluster
aws ecs describe-clusters \
  --clusters ai-readiness-cluster \
  --region us-east-1 \
  --query 'clusters[?status==`ACTIVE`]'
# Expected: Empty list []

# DynamoDB Table
aws dynamodb describe-table \
  --table-name ai-readiness-sessions \
  --region us-east-1 2>&1 | grep -i "ResourceNotFoundException"
# Expected: ResourceNotFoundException

# ECR Repository
aws ecr describe-repositories \
  --repository-names ai-readiness-diagnostic \
  --region us-east-1 2>&1 | grep -i "RepositoryNotFoundException"
# Expected: RepositoryNotFoundException

# CloudWatch Log Group
aws logs describe-log-groups \
  --log-group-name-prefix "/ecs/ai-readiness-diagnostic" \
  --region us-east-1 \
  --query 'logGroups'
# Expected: Empty list []
```

### 5.3 Verify IAM Roles Deleted

```bash
# Task Role
aws iam get-role \
  --role-name ai-readiness-diagnostic-task-role 2>&1 | grep -i "NoSuchEntity"
# Expected: NoSuchEntity

# Execution Role
aws iam get-role \
  --role-name ai-readiness-diagnostic-execution-role 2>&1 | grep -i "NoSuchEntity"
# Expected: NoSuchEntity
```

**Verification Checklist:**
- [ ] terraform state list returns 0 resources
- [ ] ECS cluster not found or INACTIVE
- [ ] DynamoDB table reports ResourceNotFoundException
- [ ] ECR repository reports RepositoryNotFoundException
- [ ] CloudWatch log group not found
- [ ] IAM roles report NoSuchEntity
- [ ] AWS billing shows $0 for these resources (next cycle)

---

## 6. Rollback & Recovery Procedures

### 6.1 Immediate Rollback (Before State Cleanup)

**If you need to undo the destruction before step 4.2:**

```bash
cd terraform/

# Terraform stores a backup: terraform.tfstate.backup
# If it still exists, you can restore
cp terraform.tfstate.backup terraform.tfstate

# Re-apply to restore all resources
terraform init
terraform apply -auto-approve

# All AWS resources will be recreated with same configuration
```

**Timeline:** Rollback works until you delete the `terraform.tfstate.backup` file.

### 6.2 Recovery from DynamoDB Backup (Within 35 Days)

**If you deleted DynamoDB but need to recover the data:**

```bash
# Using PITR (Point-in-Time Recovery)
aws dynamodb restore-table-to-point-in-time \
  --source-table-name ai-readiness-sessions \
  --target-table-name ai-readiness-sessions-recovered \
  --restore-date-time $(date -d "1 hour ago" -u +"%Y-%m-%dT%H:%M:%S.000Z") \
  --region us-east-1

# Verify recovery
aws dynamodb describe-table \
  --table-name ai-readiness-sessions-recovered \
  --region us-east-1
```

**Note:** PITR automatically enabled on creation; data retained for 35 days.

### 6.3 Recovery from Exported Backup

**Using the JSON backup created in pre-destroy phase:**

```bash
# Recreate the table
terraform apply -target=aws_dynamodb_table.sessions -auto-approve

# Import data from JSON backup
aws dynamodb batch-write-item \
  --request-items file://ai-readiness-sessions-backup-*.json \
  --region us-east-1
```

---

## 7. Safety Checklist

### Pre-Destroy Checklist

- [ ] **Backups Created:** 
  - DynamoDB exported to JSON file
  - CloudWatch logs exported to text file
  - Terraform state file backed up locally
- [ ] **Data Verified:** DynamoDB contains ONLY test fixtures
  - MeridianFS
  - NorthernCare
  - AurelianTech
  - No production data
- [ ] **No Sensitive Data:**
  - No AWS credentials in logs
  - No API keys in config
  - No customer PII
- [ ] **Terraform Validation:**
  - `terraform validate` passes
  - `terraform state list` shows ~15 resources
  - `terraform plan -destroy` completes without errors
- [ ] **External Dependencies:** No other systems depend on this deployment
- [ ] **DNS/URLs:** No DNS records pointing to test IP
- [ ] **Git Committed:** All current work committed to main branch
- [ ] **AWS Credentials:** Verified correct account (023138541872) and region (us-east-1)

### During Destroy Checklist

- [ ] **Review Terraform Plan:** Read output of `terraform plan -destroy`
- [ ] **Confirm Destruction:** Type 'yes' when prompted by `terraform destroy`
- [ ] **Monitor Process:** Watch for completion (usually 2-5 minutes)
- [ ] **Check for Errors:** Review any warnings (some are expected)
- [ ] **Record Timestamp:** Note when destroy completes

### Post-Destroy Checklist

- [ ] **Verify State:** `terraform state list` returns empty
- [ ] **Verify AWS Console:** Check resources are deleted
  - ECS Cluster gone
  - DynamoDB table gone
  - ECR repo gone
  - Log group gone
  - IAM roles gone
  - Security group gone
- [ ] **Backup State Files:** Store `terraform.tfstate.backup*` safely
- [ ] **Clean Up Backups:** Move backup directory to archive location
- [ ] **Git Commit:** Record deprovisioning in git history
  ```bash
  git add -A
  git commit -m "Deprovisioning: Terraform destroy completed for test deployment"
  git push origin main
  ```
- [ ] **Alert Monitoring:** Disable any CloudWatch alarms for deleted resources
- [ ] **Cost Verification:** Confirm next billing cycle shows $0 for these resources

---

## 8. Troubleshooting Terraform Destroy

### Issue: ECR Repository Won't Delete

**Error:** "RepositoryNotEmptyException"

**Solution:**
```bash
# Force delete all images first
aws ecr batch-delete-image \
  --repository-name ai-readiness-diagnostic \
  --image-ids imageTag=latest \
  --region us-east-1

# Then retry terraform destroy
terraform destroy -auto-approve
```

### Issue: Security Group Won't Delete

**Error:** "InvalidGroup.InUse"

**Cause:** ENIs still attached from ECS tasks

**Solution:**
```bash
# Wait longer for task termination
sleep 30

# Then retry
terraform destroy -auto-approve

# Or manually detach and retry:
aws ec2 describe-network-interfaces \
  --filters "Name=group-id,Values=sg-094e244f45432489d" \
  --region us-east-1
```

### Issue: IAM Role Won't Delete

**Error:** "DeleteConflict: You cannot delete a role that has inline policies"

**Solution:**
```bash
# Terraform should handle this automatically
# If stuck, check what policies are attached:
aws iam list-role-policies \
  --role-name ai-readiness-diagnostic-task-role

# If they exist, manually delete:
aws iam delete-role-policy \
  --role-name ai-readiness-diagnostic-task-role \
  --policy-name <policy-name>
```

### Issue: State File Lock

**Error:** "Error acquiring the state lock"

**Solution:**
```bash
cd terraform/

# Check for lock file
ls -la .terraform.tfstate.lock

# Remove lock (use with caution)
rm .terraform.tfstate.lock

# Re-initialize
terraform init

# Retry destroy
terraform destroy
```

### Nuclear Option: Force Clean State

**Only use if nothing else works:**

```bash
cd terraform/

# Save current state
cp terraform.tfstate terraform.tfstate.manual-backup

# Remove all resources from state (doesn't delete AWS resources)
terraform state list | xargs -I {} terraform state rm {}

# Verify state is empty
terraform state list

# Resources still exist in AWS - delete them manually if needed
# See AWS Console or use AWS CLI commands
```

---

## 9. Estimated Timeline

| Step | Task | Duration | Notes |
|---|---|---|---|
| **1** | Create backups (DynamoDB, logs) | 2-3 min | Concurrent operations |
| **2** | Verify Terraform state | 1 min | Quick validation |
| **3** | Run `terraform plan -destroy` | 1-2 min | Review plan output |
| **4** | Run `terraform destroy` | 2-5 min | Wait for completion |
| **5** | Verify AWS cleanup | 2-3 min | Check all resources gone |
| **6** | Clean up state files | 1 min | Local operations |
| **7** | Git commit | 1 min | Record changes |
| **Total** | **Complete deprovisioning** | **10-15 minutes** | Conservative estimate |

---

## 10. Appendix: Resource Mapping

### Terraform Resources → AWS Resources

| Terraform Resource | AWS Resource | Deletion Order |
|---|---|---|
| `aws_ecs_cluster.main` | ECS Cluster: ai-readiness-cluster | 3 |
| `aws_ecs_service.app` | ECS Service: ai-readiness-diagnostic | 1 (first) |
| `aws_ecs_task_definition.app` | ECS Task Definition: ai-readiness-diagnostic | 2 |
| `aws_cloudwatch_log_group.ecs` | Log Group: /ecs/ai-readiness-diagnostic | 4 |
| `aws_dynamodb_table.sessions` | DynamoDB Table: ai-readiness-sessions | 5 |
| `aws_ecr_repository.app` | ECR Repo: ai-readiness-diagnostic | 6 |
| `aws_ecr_lifecycle_policy.app` | ECR Lifecycle Policy | (with repo) |
| `aws_security_group.ecs_tasks` | Security Group: ai-readiness-diagnostic-ecs-tasks | 7 |
| `aws_iam_role.task_role` | IAM Role: ai-readiness-diagnostic-task-role | 8 |
| `aws_iam_role.execution_role` | IAM Role: ai-readiness-diagnostic-execution-role | 9 |
| `aws_iam_role_policy.*` | IAM Inline Policies (4 total) | (with roles) |
| `aws_iam_role_policy_attachment.*` | Attached Managed Policies | (with roles) |

**Note:** Terraform automatically handles deletion in reverse dependency order.

### Deletion Dependencies (Handled by Terraform)

```
aws_ecs_service.app (depends on all below)
  ├─ aws_iam_role_policy.task_role_dynamodb
  ├─ aws_iam_role_policy.task_role_bedrock
  ├─ aws_ecs_task_definition.app
  └─ aws_security_group.ecs_tasks

aws_ecs_task_definition.app (depends on)
  ├─ aws_iam_role.execution_role
  └─ aws_iam_role.task_role

aws_security_group.ecs_tasks (depends on)
  └─ (no internal dependencies)

aws_iam_role.task_role (depends on)
  ├─ aws_iam_role_policy.task_role_dynamodb
  └─ aws_iam_role_policy.task_role_bedrock

aws_dynamodb_table.sessions (referenced by)
  └─ aws_iam_role_policy.task_role_dynamodb
```

### Cost Savings Summary

**Before Deprovisioning:**
- ECS Fargate: ~$15-25/month
- DynamoDB: ~$5-10/month
- ECR Storage: ~$2-5/month
- CloudWatch: ~$1-3/month (logs + Container Insights)
- NAT Gateway: ~$32/month (if using NAT)
- Data Transfer: ~$2-5/month
- **Total: ~$60-88/month**

**After Deprovisioning:**
- **Total: $0/month**

**Payback Timeline:**
- **Day 0:** Deprovisioning complete, no charges for remaining month
- **Day 31:** First billing cycle shows $0 for deleted resources
- **Annual savings:** ~$720-1,056 if not redeployed

---

## 11. Next Steps After Deprovisioning

### If You Need to Redeploy

```bash
# Terraform state is backed up, so full redeploy is simple
cd terraform/

# Restore state if needed (from backup)
# cp terraform.tfstate.backup.* terraform.tfstate

# Redeploy
terraform init
terraform apply -auto-approve
```

### Archival

```bash
# Preserve the backup for historical records
mkdir -p archive/deprovisioning-2026-07-10
cp ai-readiness-sessions-backup-*.json archive/deprovisioning-2026-07-10/
cp cloudwatch-logs-*.txt archive/deprovisioning-2026-07-10/
cp terraform-state-backup*.tar.gz archive/deprovisioning-2026-07-10/

# Commit to git
git add archive/
git commit -m "Archive: Deprovisioning backups from 2026-07-10"
```

### Documentation

- **This file:** DEPROVISIONING_PLAN.md
- **Checklist:** pre_destroy_checklist.txt
- **Verification:** post_destroy_validation.txt
- **Script:** destroy_terraform.sh

---

## Contact & Support

**Questions about Terraform:**
- See CLAUDE.md for codebase documentation
- Terraform configs: `/terraform` directory

**Data Recovery (DynamoDB):**
- 35-day PITR window automatically enabled
- JSON backup: `ai-readiness-sessions-backup-*.json`

**Cost Questions:**
- AWS Billing Console: Check account 023138541872
- Expected: $0 charges for deleted resources in next cycle

---

**Document Version:** 2.0 (Terraform-focused)  
**Last Updated:** 2026-07-10  
**Author:** Claude Agent  
**Status:** Ready for Execution - Use `terraform destroy` as primary method
