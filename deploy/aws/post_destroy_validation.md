# Post-Destroy Validation

**Run this after a teardown completes.**
Converted from `post_destroy_validation.txt` (2026-07-10) without changing the checks.

Sections 1–3 are now automated. Run:

```bash
bash deploy/aws/post_destroy_validation.sh              # defaults: us-east-1, account 023138541872
bash deploy/aws/post_destroy_validation.sh --region us-west-2 --account 111122223333
```

Exit `0` = every automated check passed. Exit `1` = something survived; the script lists what.
Exit `2` = preflight problem (no `aws` CLI, bad credentials, or wrong account — it refuses to
validate the wrong account, because that would report false success).

The script is **read-only**: describe, list and get calls only.

> The previous version of this document was a prose checklist, but `destroy_terraform.sh` (now `deploy/aws/destroy_terraform.sh`) invoked
> it with `bash post_destroy_validation.txt`. That produced a cascade of shell errors rather than a
> validation run, so the verification step silently never happened. The script now does the work.

---

## What the script checks

**1. Terraform state** — state list is empty; `terraform.tfstate` declares zero resources; no lock
files present.

**2. AWS resources absent** — ECS clusters, DynamoDB tables, ECR repositories, CloudWatch log
groups, IAM task and execution roles, ECS security groups. **Both naming conventions are checked**
(`ai-readiness-*` from `deploy/aws/config.sh` and `ai-readiness-diagnostic-*` from `terraform/`),
because a resource surviving under either name still bills and, in the case of DynamoDB, still holds
assessment data.

**3. Backups present** — the DynamoDB export, CloudWatch log export, and Terraform state backup
produced by [pre_destroy_checklist.md](pre_destroy_checklist.md).

---

## Manual steps the script does not do

### Cost verification

- [ ] **Check the AWS billing console** for account `023138541872` — no new charges for the deleted
      resources. Billing data lags, so this needs revisiting in the next cycle.
- [ ] **Record the saving.** Previous monthly cost ~\$60–88, so ~\$720–1,056 annually.

### Backup archival

- [ ] **Archive the backup files to a secure location.** They contain assessment data — even test
      fixtures should not sit indefinitely in a working directory.
      ```bash
      mkdir -p archive/deprovisioning-$(date +%Y-%m-%d)
      mv ai-readiness-sessions-backup-*.json cloudwatch-logs-*.txt \
         archive/deprovisioning-$(date +%Y-%m-%d)/
      ```
- [ ] **Confirm the archive location is covered by a retention decision.** See
      [../../docs/architecture/workflows_and_data_governance_baseline.md](../../docs/architecture/workflows_and_data_governance_baseline.md)
      §3.2 — retention is still an open item, so this is currently a judgment call.

### Git

Deliberately not automated — a script should not commit or push on your behalf.

- [ ] Working tree is clean apart from the intended deprovisioning change: `git status`
- [ ] Commit: `git add -A && git commit -m "Deprovisioning: teardown completed"`
- [ ] Push: `git push origin <branch>`

---

## Sign-off

All verification checks passed: **[ ] YES**

| | |
|---|---|
| Date and time | |
| Verified by | |
| Script exit code | |

Once this is signed off, deprovisioning is complete. Archive the backups and update
[deprovisioning_plan.md](deprovisioning_plan.md) with the date.
