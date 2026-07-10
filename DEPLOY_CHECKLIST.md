# Deployment Checklist

**AI Diagnostic MVP - Pre/Post Deployment Validation**

**Version:** 1.0  
**Last Updated:** 2026-07-10

---

## Pre-Deployment Checklist

All items must be completed before deploying to staging or production.

### Code Quality & Testing

- [ ] **All TIER 1 Security Tests Pass**
  ```bash
  make test-eval-t1
  ```
  - [ ] Prompt injection tests pass
  - [ ] Path traversal tests pass
  - [ ] Header injection tests pass
  - [ ] CORS misconfiguration tests pass
  - [ ] Email validation tests pass
  - [ ] URL validation tests pass

- [ ] **All TIER 2 Data Integrity Tests Pass**
  ```bash
  make test-eval-t2
  ```
  - [ ] Race condition (DynamoDB) tests pass
  - [ ] Review decision race condition tests pass
  - [ ] Banker's rounding tests pass
  - [ ] Type mismatch tests pass
  - [ ] Eventual consistency tests pass

- [ ] **Unit Tests Pass**
  ```bash
  make test-unit
  ```

- [ ] **Code Coverage >= 80%**
  ```bash
  make coverage
  ```
  Coverage report: `htmlcov/index.html`

- [ ] **Code Formatting Correct**
  ```bash
  make format-check
  ```
  All code formatted with Black (line length 120)

- [ ] **Imports Properly Sorted**
  isort has sorted all imports (Black compatible profile)

- [ ] **Linting Passes**
  ```bash
  make lint
  ```
  No critical flake8 or pylint issues

- [ ] **Type Checking Passes**
  ```bash
  make type-check
  ```
  mypy analysis complete (warnings OK, errors critical)

- [ ] **Complexity Within Limits**
  ```bash
  make complexity
  ```
  Cyclomatic complexity <= 10, maintainability index >= 70

### Security Validation

- [ ] **No Bandit Security Issues**
  ```bash
  bandit -r app/ -ll
  ```
  No HIGH or CRITICAL severity issues

- [ ] **No Known CVEs in Dependencies**
  ```bash
  pip-audit --desc
  ```
  All dependencies up-to-date, no known vulnerabilities

- [ ] **No Hardcoded Secrets**
  ```bash
  make secrets-check
  ```
  - [ ] No API keys (api_key=, API_KEY=)
  - [ ] No AWS credentials (AKIA*, aws_secret*)
  - [ ] No Stripe keys (sk_*)
  - [ ] No private keys (.pem, .key)

- [ ] **No Unverified Commits**
  - Commit messages are clear and descriptive
  - All commits signed or verified

### Repository State

- [ ] **No Uncommitted Changes**
  ```bash
  git status
  ```
  Working tree is clean

- [ ] **All Changes Committed**
  - [ ] Code changes pushed
  - [ ] Configuration updates committed
  - [ ] Documentation updated
  - [ ] Version bumped

- [ ] **Branch Up-to-Date with Main**
  ```bash
  git log origin/main..HEAD  # Should show release commits only
  ```

- [ ] **CHANGELOG Updated**
  - [ ] Document all features added
  - [ ] Document all bugs fixed
  - [ ] Document breaking changes (if any)
  - [ ] Include ticket references (JIRA, GitHub)

- [ ] **Version Bumped (Semantic Versioning)**
  - [ ] Major version (X.0.0) for breaking changes
  - [ ] Minor version (x.Y.0) for new features
  - [ ] Patch version (x.y.Z) for bug fixes
  - [ ] Example: v1.2.3

### Infrastructure Validation

- [ ] **Terraform Configuration Valid**
  ```bash
  make terraform-validate
  ```

- [ ] **Terraform Formatted Correctly**
  ```bash
  make terraform-format
  ```

- [ ] **No Infrastructure Security Issues (tfsec)**
  ```bash
  tfsec terraform/
  ```
  No HIGH or CRITICAL severity findings

- [ ] **Terraform Plan Reviewed**
  ```bash
  make terraform-plan
  ```
  - [ ] Review tfplan output
  - [ ] Understand all resource changes
  - [ ] Approve additions/modifications/deletions

### Docker & Container Validation

- [ ] **Docker Image Builds Successfully**
  ```bash
  make docker-build
  ```

- [ ] **Docker Image Scans Clean**
  ```bash
  docker run --rm aquasec/trivy image ai-diagnostic-mvp:latest
  ```
  No CRITICAL or HIGH severity vulnerabilities

- [ ] **Base Image is Up-to-Date**
  - Using `python:3.11-slim` or later
  - No security patches pending

- [ ] **Docker Image Size Reasonable**
  ```bash
  docker images | grep ai-diagnostic-mvp
  ```
  Should be < 500MB (with dependencies)

### Environment & Secrets

- [ ] **AWS Credentials Configured**
  ```bash
  aws sts get-caller-identity
  ```
  Should show current AWS account

- [ ] **Environment Variables Set**
  - [ ] AIDIAG_* environment variables configured
  - [ ] Bedrock region set (us-east-1, us-west-2, etc.)
  - [ ] DynamoDB table name set (if applicable)

- [ ] **Secrets Loaded in Deployment Pipeline**
  - [ ] API keys in GitHub Secrets (if needed)
  - [ ] AWS credentials in IAM role/temporary credentials
  - [ ] No secrets in code or config files

### Documentation

- [ ] **README.md Current**
  - [ ] Installation instructions accurate
  - [ ] Running instructions clear
  - [ ] Deployment instructions documented

- [ ] **API Documentation Generated**
  - [ ] FastAPI docs available at `/docs`
  - [ ] OpenAPI spec available at `/openapi.json`

- [ ] **Runbook Created**
  - [ ] How to deploy
  - [ ] How to rollback
  - [ ] How to monitor
  - [ ] Common troubleshooting steps

### Performance & Load Testing

- [ ] **Latency Tests Pass**
  - Fixture endpoint: < 100ms
  - Assess endpoint: < 500ms (baseline)

- [ ] **Memory Tests Pass**
  - Peak memory for 10 requests: < 100MB

- [ ] **Concurrency Tests Pass**
  - Handles 5+ concurrent requests

- [ ] **Load Testing Completed (Optional)**
  - Tested with expected peak load
  - No memory leaks detected
  - Response times acceptable under load

### Final Review

- [ ] **Code Review Approved**
  - At least one other developer approved
  - All comments addressed
  - No "changes requested" from reviewers

- [ ] **Security Review Completed**
  - Run through OWASP Top 10
  - Checked for: injection, auth, data exposure, XXE, broken access control, misconfig
  - All critical issues resolved

- [ ] **Architecture Review (if applicable)**
  - Changes don't violate design patterns
  - Scalability considered
  - Performance implications understood

- [ ] **Team Sign-Off**
  - [ ] Tech lead approved
  - [ ] Security team approved (for security changes)
  - [ ] DevOps approved (for infrastructure changes)

---

## Deployment Steps

### 1. Create Release

```bash
# Ensure on latest main
git checkout main
git pull origin main

# Create release branch
git checkout -b release/v1.2.3

# Update version
echo "1.2.3" > VERSION
# Or in pyproject.toml:
# version = "1.2.3"

# Update CHANGELOG.md
# Add section like:
# ## [1.2.3] - 2026-07-10
# ### Added
# - New feature X
# ### Fixed
# - Bug fix Y

git add VERSION CHANGELOG.md
git commit -m "chore: Bump version to 1.2.3"
git push origin release/v1.2.3
```

### 2. Create Pull Request

```bash
# GitHub: Create PR from release/v1.2.3 → main
# Title: "chore: Release v1.2.3"
# Description: Link to CHANGELOG section
```

### 3. Wait for CI Checks

- All GitHub Actions must pass
- Code review approval required
- No conflicts with main

### 4. Deploy to Staging

```bash
# After PR merged to main
git checkout main
git pull origin main

# Deploy to staging environment
terraform -chdir=terraform apply -var-file=staging.tfvars

# Or via GitHub Actions (if automated):
# Push tag: git tag v1.2.3 && git push origin v1.2.3
```

### 5. Smoke Test in Staging

- [ ] Application starts without errors
- [ ] API endpoints respond
- [ ] Database connectivity works
- [ ] External services (Bedrock) accessible
- [ ] Create test assessment, verify output
- [ ] Check logs for errors

### 6. Deploy to Production

```bash
# After staging validation
terraform -chdir=terraform apply -var-file=production.tfvars

# Or trigger via release workflow
```

---

## Post-Deployment Validation

### Immediate Checks (< 5 minutes)

- [ ] **Application is Running**
  ```bash
  curl https://api.example.com/api/health
  ```
  Should return 200 OK

- [ ] **No Error Logs**
  ```bash
  # Check CloudWatch Logs
  aws logs tail /aws/ecs/ai-diagnostic-mvp --follow --since 1m
  ```
  No ERROR level entries

- [ ] **API is Responsive**
  ```bash
  curl https://api.example.com/api/fixture/meridianfs -v
  ```
  Should return 200 with valid JSON

- [ ] **Database Connected**
  - DynamoDB table accessible
  - Items can be read/written
  - Replication healthy (if multi-region)

### Functional Tests (5-30 minutes)

- [ ] **Assessment Creation Works**
  - POST /api/assess with valid payload
  - Response includes ID and scorecard
  - Response time acceptable

- [ ] **Fixture Endpoint Works**
  - GET /api/fixture/meridianfs
  - Returns expected JSON structure
  - No errors in logs

- [ ] **Review Queue Works**
  - GET /api/review/queue
  - Returns list of pending reviews
  - No stale data

- [ ] **PDF Generation Works**
  - GET /api/scorecard/{id}/pdf
  - Returns valid PDF file
  - File is readable

- [ ] **External Services Working**
  - Bedrock inference working
  - API rate limits not exceeded
  - Response quality acceptable

### Monitoring & Alerts (Ongoing)

- [ ] **CloudWatch Dashboards Show Normal Metrics**
  - API response times
  - Error rate (should be < 1%)
  - DynamoDB throughput
  - Lambda cold start rate

- [ ] **Logging is Working**
  - All requests logged
  - Errors captured with context
  - Performance metrics recorded

- [ ] **Alerts Configured**
  - High error rate alert
  - High latency alert
  - DynamoDB throttling alert
  - Bedrock rate limit alert

### Data Integrity Check (First Hour)

- [ ] **Recent Assessments Visible**
  - New assessments appear in queue
  - No "missing" assessments
  - Scores calculated correctly

- [ ] **Historical Data Intact**
  - Previous assessments still accessible
  - No data corruption
  - Backups up-to-date

### Security Check (First Hour)

- [ ] **No Unexpected Network Connections**
  - Only expected egress to AWS services
  - No data exfiltration

- [ ] **Access Logs Review**
  - No suspicious access patterns
  - No failed login attempts
  - IP allowlist working (if configured)

- [ ] **Secrets Not Exposed**
  - API keys not in logs
  - No sensitive data in responses
  - Error messages don't expose internals

### Performance Baseline (First 24 Hours)

- [ ] **Response Times Normal**
  - Fixture endpoint: ~50ms (< 100ms limit)
  - Assess endpoint: varies by LLM speed
  - No p95 latency spikes

- [ ] **Memory Stable**
  - No memory leaks
  - Container memory usage stable
  - No OOM kills

- [ ] **Throughput Acceptable**
  - Can handle expected request rate
  - No timeout errors
  - No queue backlog

---

## Rollback Procedure

If deployment has critical issues:

### Immediate Actions

1. **Alert Team**
   - Notify in Slack #deployments
   - Page on-call engineer if production

2. **Assess Severity**
   - Is application completely down? (Critical - roll back now)
   - Is functionality partially broken? (High - investigate first)
   - Is performance degraded? (Medium - monitor and assess)

### Rollback Steps

**Option 1: Terraform Rollback** (if infrastructure changed)

```bash
# Get previous state
terraform -chdir=terraform show -json | jq

# Revert to previous version tag
git checkout v1.2.2

# Re-apply Terraform with previous version
terraform -chdir=terraform apply

# Verify
curl https://api.example.com/api/health
```

**Option 2: Git Revert** (safest for small changes)

```bash
# Find commit to revert
git log --oneline | head -5

# Revert specific commit
git revert <commit-hash>
git push origin main

# CI/CD will re-deploy previous version
```

**Option 3: Blue-Green Rollback** (if using blue-green deployment)

```bash
# Switch traffic back to previous version
aws elbv2 modify-listener \
  --listener-arn <green-listener> \
  --default-actions Type=forward,TargetGroupArn=<blue-tg>

# Or via GitHub Actions: trigger "Deploy to Staging" with previous tag
```

### Post-Rollback

1. **Verify Rollback Success**
   - Application responding normally
   - No error logs
   - Previous functionality working

2. **Root Cause Analysis**
   - What caused the failure?
   - Could it have been caught by pre-deployment checks?
   - Update quality gates if necessary

3. **Fix the Issue**
   - Create fix branch: `git checkout -b fix/deployment-issue`
   - Apply fix, test locally
   - Create PR with detailed explanation

4. **Document Incident**
   - Post-mortem meeting
   - Update runbook if needed
   - Improve automation to prevent recurrence

---

## Common Deployment Issues & Fixes

### Issue: "Application starts but API returns 500"

**Diagnosis:**
```bash
aws logs tail /aws/ecs/ai-diagnostic-mvp --since 1m
```

**Common Causes & Fixes:**
- [ ] Missing environment variable → Add to CloudFormation/ECS task definition
- [ ] Database connection failed → Check security group, VPC routing
- [ ] Bedrock credentials invalid → Verify IAM role has bedrock:InvokeModel permission
- [ ] Configuration parsing error → Check YAML/JSON syntax in config files

### Issue: "DynamoDB ConditionalCheckFailedException"

**Cause:** Race condition detected (good!)  
**Fix:** App should retry - check app logs  
**Escalate if:** Happens frequently (indicates higher load than expected)

### Issue: "API response time > 5 seconds"

**Cause:** Likely LLM inference slow  
**Check:** AWS Bedrock metrics for throttling  
**Fix:** None needed if under expected load; scale if load increased

### Issue: "Docker image missing from ECR"

**Cause:** Build failed or push didn't complete  
**Fix:**
```bash
# Rebuild and push
docker build -t ai-diagnostic-mvp:v1.2.3 .
docker tag ai-diagnostic-mvp:v1.2.3 <account>.dkr.ecr.<region>.amazonaws.com/ai-diagnostic-mvp:v1.2.3
docker push <account>.dkr.ecr.<region>.amazonaws.com/ai-diagnostic-mvp:v1.2.3
```

### Issue: "Terraform plan shows unexpected deletions"

**Cause:** State inconsistency or configuration drift  
**Fix:**
```bash
# Review plan carefully
terraform -chdir=terraform plan -out=tfplan

# Only apply if confident
terraform -chdir=terraform apply tfplan

# If uncertain, contact DevOps
```

---

## Environment-Specific Checklists

### Development Environment

Skip items:
- [ ] Code review approval (optional)
- [ ] Security review (optional)
- [ ] Changelog update (optional)
- [ ] Performance baseline (optional)

### Staging Environment

Include all items above.

### Production Environment

Include all items above, plus:

- [ ] **Disaster Recovery Plan Reviewed**
  - Backup/restore procedure tested
  - RTO/RPO acceptable
  - Team trained on recovery

- [ ] **Incident Response Procedures Updated**
  - Escalation contacts updated
  - On-call schedule configured
  - Runbooks current

- [ ] **Monitoring & Alerting Complete**
  - All dashboards set up
  - All alerts configured and tested
  - Alert thresholds tuned

- [ ] **Documentation Complete**
  - Architecture diagrams updated
  - Runbook finalized
  - Team trained on changes

---

## Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Developer | ________________ | ________ | ________ |
| Tech Lead | ________________ | ________ | ________ |
| Security | ________________ | ________ | ________ |
| DevOps | ________________ | ________ | ________ |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-07-10 | Initial checklist |

## Related Documents

- [CI_CD_PIPELINE.md](CI_CD_PIPELINE.md) — Full pipeline documentation
- [EVALUATION_SUITE.md](EVALUATION_SUITE.md) — Vulnerability tests
- [README.md](README.md) — Project overview
- `.github/workflows/` — Automated checks
