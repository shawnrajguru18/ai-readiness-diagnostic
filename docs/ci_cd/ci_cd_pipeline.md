# CI/CD Pipeline Documentation

**AI Diagnostic MVP - Comprehensive Continuous Integration & Continuous Deployment**

**Version:** 1.0  
**Last Updated:** 2026-07-10  
**Purpose:** Prevent regressions of 87+ discovered vulnerabilities and bugs through automated testing, quality gates, and security scanning.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Pipeline Stages](#pipeline-stages)
3. [Quality Gates & Thresholds](#quality-gates--thresholds)
4. [Local Development Setup](#local-development-setup)
5. [Running Tests Locally](#running-tests-locally)
6. [Running Security Checks Locally](#running-security-checks-locally)
7. [GitHub Actions Workflows](#github-actions-workflows)
8. [Deployment Workflow](#deployment-workflow)
9. [Troubleshooting](#troubleshooting)
10. [Common CI Failures & Fixes](#common-ci-failures--fixes)
11. [Adding New Tests](#adding-new-tests)
12. [Tuning Quality Gates](#tuning-quality-gates)
13. [Monitoring & Alerts](#monitoring--alerts)

---

## Architecture Overview

The CI/CD pipeline implements a "shift-left" approach where:
- **Developers** run tests locally before pushing (pre-commit hooks)
- **Pull Requests** trigger automated tests and quality checks
- **Main branch** requires all checks to pass before merging
- **Deployment** is gated by comprehensive pre-deployment validation

### Pipeline Flow

```
Developer Push
    ↓
Pre-commit Hooks (Local)
    ↓
GitHub Actions Triggered
    ├─ Test Suite (Evaluation + Unit Tests)
    ├─ Security Scanning (SAST + Dependencies + Secrets)
    ├─ Code Quality (Linting + Formatting + Complexity)
    ├─ Performance Testing (Latency + Memory + Concurrency)
    └─ Deployment Validation (Terraform + Docker)
    ↓
Quality Gates Check
    ├─ TIER 1 (Security) - MUST PASS (Fail build if fail)
    ├─ TIER 2 (Data Integrity) - MUST PASS (Fail build if fail)
    ├─ TIER 3 (Resilience) - WARN if fail (Don't fail build)
    └─ TIER 4 (Validation) - WARN if fail (Don't fail build)
    ↓
Merge to Main (if all gates pass)
    ↓
Deploy to Staging/Production
```

---

## Pipeline Stages

### 1. Test Suite (test.yml)

**Purpose:** Run all tests and verification suite to catch regressions.

**Triggers:**
- Push to `main` or `develop` branches
- All pull requests

**What it does:**
- Runs unit tests (smoke tests, store tests)
- Runs TIER 1 security tests (prompt injection, path traversal, headers, CORS, email, URL)
- Runs TIER 2 data integrity tests (race conditions, rounding, type mismatches, eventual consistency)
- Runs TIER 3 resilience tests (exception handling, rate limits, timeouts, error masking)
- Runs TIER 4 validation tests (data validation)
- Generates coverage report (target: 80%+)
- Uploads to Codecov for tracking

**Success Criteria:**
- All unit tests pass
- TIER 1 tests pass (critical - fails build)
- TIER 2 tests pass (high - fails build)
- TIER 3 & TIER 4 may fail with warnings
- Coverage >= 80%

**Python Versions Tested:** 3.11, 3.12

---

### 2. Security Scanning (security.yml)

**Purpose:** Detect vulnerabilities in code, dependencies, and secrets.

**Triggers:**
- Push to `main` or `develop` branches
- All pull requests
- Daily schedule (2 AM UTC)

**Tools Used:**

#### Bandit (SAST)
- Scans Python code for security issues
- Checks for: hardcoded secrets, insecure functions, SQL injection patterns
- Fail Build if: HIGH or CRITICAL severity found

#### Semgrep
- Pattern-based vulnerability detection
- Rulesets: OWASP Top Ten, Security Audit, Python Best Practices
- Fails Build: No (informational)

#### pip-audit (Dependency Scanning)
- Scans Python dependencies for known CVEs
- Checks against NVD (National Vulnerability Database)
- Fails Build: Yes (0 known vulnerabilities allowed)

#### TruffleHog (Secrets Detection)
- Scans git history for hardcoded secrets
- Detects: API keys, AWS credentials, private keys, tokens
- Fails Build: Yes if verified secrets found

#### Pattern-Based Secret Detection
- Regex patterns for common credential formats
- Checks for: API_KEY=, sk_*, AKIA* patterns
- Fails Build: Yes

#### CodeQL
- GitHub's advanced static analysis
- Detects: code injection, buffer overflow, logic errors
- Fails Build: No (informational)

---

### 3. Code Quality (quality.yml)

**Purpose:** Maintain code quality, readability, and consistency.

**Triggers:**
- Push to `main` or `develop` branches
- All pull requests

**Tools Used:**

#### Black (Code Formatting)
- Enforces consistent code formatting
- Max line length: 120 characters
- Fails Build: Yes

#### isort (Import Sorting)
- Sorts imports consistently
- Profile: black-compatible
- Fails Build: Yes

#### flake8 (Linting)
- Checks for style violations, unused imports, undefined names
- Max line length: 120
- Ignores: E203 (whitespace before ':'), W503 (line break before binary operator)
- Plugins: bugbear, comprehensions, docstrings
- Fails Build: No (warning only)

#### pylint (Code Analysis)
- Deeper code analysis for maintainability
- Disabled: too-many-arguments, missing-docstring
- Target: Score >= 7.0
- Fails Build: No (warning only)

#### mypy (Type Checking)
- Verifies type hints and catches type mismatches
- Ignores missing imports (external libraries often don't have stubs)
- Fails Build: No (informational)

#### Radon (Complexity Analysis)
- Cyclomatic Complexity: Max 10 per function
- Maintainability Index: Min 70
- Fails Build: No (informational)

#### Vulture (Dead Code Detection)
- Finds unused code, variables, functions
- Min confidence: 80%
- Fails Build: No (informational)

---

### 4. Performance Testing (performance.yml)

**Purpose:** Ensure response times, memory usage, and concurrency don't regress.

**Triggers:**
- Push to `main` or `develop` branches
- All pull requests
- Nightly schedule (3 AM UTC)

**What it tests:**

#### Latency Tests
- Fixture endpoint: < 100ms
- Assess endpoint: < 500ms (baseline, LLM-dependent)
- Uses pytest-benchmark for measuring

#### Memory Usage Tests
- Peak memory for 10 concurrent fixture requests: < 100MB
- Uses tracemalloc to measure

#### Concurrent Request Handling
- Should handle 5+ concurrent requests without crashes
- Tests race condition detection

#### Load Testing (Optional)
- Locust script template for manual load testing
- Can be run against staging environment
- Not automated (requires running app server)

---

### 5. Deployment Validation (deploy.yml)

**Purpose:** Validate infrastructure and deployment readiness.

**Triggers:**
- Push to `main` with changes in `terraform/`, `Dockerfile`, or deploy.yml
- Pull requests with same file changes

**What it validates:**

#### Terraform Validation
- `terraform fmt -check`: Code is properly formatted
- `terraform validate`: Syntax and structure are valid
- Fails Build: Yes

#### tfsec (Infrastructure Security)
- Scans Terraform for security misconfigurations
- Checks: CORS, encryption, IAM, logging, etc.
- Severity: HIGH or CRITICAL fails build
- Fails Build: Yes

#### Docker Image Build
- Builds Docker image without pushing
- Verifies Dockerfile is valid
- Fails Build: Yes

#### Trivy (Container Scanning)
- Scans Docker image for vulnerabilities
- Severity: CRITICAL or HIGH fails build
- Fails Build: Yes

#### Pre-Deployment Checklist
- All tests passing (Tiers 1 & 2)
- Code coverage >= 80%
- No uncommitted changes
- Changelog updated (recommended)
- Version bumped (recommended)

---

## Quality Gates & Thresholds

See `quality-gates.json` for the authoritative configuration.

### Summary of Critical Gates

| Check | Threshold | Fail Build | Description |
|-------|-----------|-----------|-------------|
| TIER 1 Security Tests | Pass | YES | Prompt injection, path traversal, headers, CORS, validation |
| TIER 2 Data Integrity Tests | Pass | YES | Race conditions, rounding, type mismatches, consistency |
| Code Coverage | >= 80% | NO | Warn if below 80% |
| Black Formatting | Pass | YES | Code must be formatted |
| isort Imports | Pass | YES | Imports must be sorted |
| Bandit (SAST) | No HIGH/CRITICAL | YES | No security issues in code |
| pip-audit | No CVEs | YES | No known vulnerabilities in dependencies |
| Secrets Detection | None found | YES | No hardcoded secrets |
| Terraform Validate | Pass | YES | Infrastructure code must be valid |
| tfsec | No HIGH/CRITICAL | YES | No infrastructure security issues |
| Docker Build | Success | YES | Docker image must build |
| Trivy Scan | No CRITICAL | YES | No critical container vulnerabilities |

---

## Local Development Setup

### Prerequisites

- Python 3.11+ (tested on 3.11, 3.12)
- git
- Docker (optional, for container testing)
- Terraform (optional, for infrastructure changes)

### Installation

```bash
# Clone repository
git clone https://github.com/your-org/ai-diagnostic-mvp.git
cd ai-diagnostic-mvp

# Install dependencies and setup pre-commit hooks
make install

# Or manually:
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov
pip install black isort flake8 pylint mypy radon vulture
pip install bandit pip-audit
pip install pre-commit
pre-commit install
```

### Environment Setup

```bash
# Create .env file (if needed for local development)
cp .env.example .env

# If using DynamoDB locally:
# export AIDIAG_DDB_TABLE=ai-diagnostic-local
# docker run -d -p 8000:8000 amazon/dynamodb-local
```

---

## Running Tests Locally

### All Tests

```bash
# Run all tests (unit + evaluation suite)
make test

# Or directly with pytest:
pytest tests/ -v
```

### Unit Tests Only

```bash
make test-unit

# Or:
pytest tests/test_smoke.py tests/test_store.py -v
```

### Evaluation Suite (All Tiers)

```bash
make test-eval

# Or:
pytest tests/test_evaluation_suite.py -v
```

### Specific Vulnerability Tiers

```bash
# TIER 1 (Critical Security) - MUST FIX
make test-eval-t1

# TIER 2 (Data Integrity) - MUST FIX
make test-eval-t2

# TIER 3 (Resilience) - SHOULD FIX
make test-eval-t3

# TIER 4 (Validation) - SHOULD FIX
make test-eval-t4
```

### Coverage Report

```bash
make coverage

# Then open htmlcov/index.html in browser
```

### With Output

```bash
# Verbose output
pytest tests/ -v

# Show print statements
pytest tests/ -v -s

# Stop on first failure
pytest tests/ -x

# Run only tests matching pattern
pytest tests/ -k "prompt_injection" -v

# Show slowest 10 tests
pytest tests/ --durations=10
```

---

## Running Security Checks Locally

### Full Security Suite

```bash
make security-check
```

### Individual Checks

```bash
# Bandit (Python SAST)
bandit -r app/ -ll

# Semgrep
semgrep --config=p/python --config=p/security-audit app/

# Dependency vulnerabilities
pip-audit --desc

# Hardcoded secrets (pattern-based)
grep -r "api[_-]?key\s*[:=]" app/ || echo "No obvious API keys"
grep -r "sk_[a-zA-Z0-9]*" app/ || echo "No Stripe keys"
```

---

## GitHub Actions Workflows

All workflows are in `.github/workflows/` directory.

### test.yml

**When:** Every push and PR  
**Duration:** ~5-15 minutes  
**Matrix:** Python 3.11, 3.12

Runs all tests across Python versions.

### security.yml

**When:** Every push, PR, and daily at 2 AM UTC  
**Duration:** ~10-20 minutes  

Comprehensive security scanning including SAST, dependency checks, secrets detection.

### quality.yml

**When:** Every push and PR  
**Duration:** ~5-10 minutes  

Code formatting, linting, type checking, complexity analysis.

### performance.yml

**When:** Every push, PR, and nightly at 3 AM UTC  
**Duration:** ~10-15 minutes  

Latency, memory, and concurrency tests with benchmarking.

### deploy.yml

**When:** Push to main with infrastructure/deployment changes  
**Duration:** ~5-10 minutes  

Terraform validation, security scanning, Docker build, pre-deployment checklist.

---

## Deployment Workflow

### Prerequisites for Deployment

Before deploying, ensure:

1. **All Tier 1 & 2 Tests Pass**
   ```bash
   make test-eval-t1
   make test-eval-t2
   ```

2. **Coverage >= 80%**
   ```bash
   make coverage
   ```

3. **Code Quality Passed**
   ```bash
   make quality
   ```

4. **Security Checks Passed**
   ```bash
   make security-check
   ```

5. **Terraform Validated**
   ```bash
   make terraform-validate
   ```

6. **Docker Builds**
   ```bash
   make docker-build
   ```

7. **No Uncommitted Changes**
   ```bash
   git status
   ```

### Deployment Steps

1. **Create Release Branch**
   ```bash
   git checkout -b release/v1.2.0
   ```

2. **Update Version**
   - Update version in `VERSION` file or `pyproject.toml`
   - Update `CHANGELOG.md` with changes

3. **Commit & Push**
   ```bash
   git add VERSION CHANGELOG.md
   git commit -m "Bump version to 1.2.0"
   git push origin release/v1.2.0
   ```

4. **Create Pull Request**
   - All CI checks must pass
   - Requires code review approval
   - Merge to main triggers deployment

5. **Monitor Deployment**
   - Check health endpoint
   - Monitor logs for errors
   - Verify functionality in environment

### Rollback Procedure

If deployment fails:

```bash
# Revert to previous version
git revert <commit-hash>
git push origin main

# Or rollback via Terraform
cd terraform
terraform plan -destroy
terraform apply -destroy
terraform apply  # Re-apply previous version
```

---

## Troubleshooting

### Pre-commit Hooks Issues

**Problem:** Pre-commit hooks fail/slow

**Solution:**
```bash
# Skip pre-commit temporarily (not recommended)
git commit --no-verify

# Update pre-commit
pre-commit autoupdate

# Run on all files to find issues
pre-commit run --all-files

# Clean cache
pre-commit clean
```

### Test Failures

**Problem:** Tests fail locally but pass in CI (or vice versa)

**Solutions:**
- Check Python version: `python --version`
- Clear cache: `make clean && pytest tests/ --cache-clear`
- Check environment: `env | grep AIDIAG`
- Run with verbose output: `pytest -v -s`

### Coverage Below 80%

**Problem:** Coverage not meeting 80% threshold

**Solutions:**
```bash
# Generate coverage report
make coverage

# View coverage report
open htmlcov/index.html

# Write tests for uncovered code
# Then re-run: pytest tests/ --cov=app --cov-report=html
```

### Bandit or Security Scanner False Positives

**Problem:** Security scan flags safe code

**Solutions:**
```bash
# Bandit: Add noqa comment
code_that_is_safe()  # nosec

# Semgrep: Create semgrep.yml with exclusions
# See: https://semgrep.dev/docs/ignoring-files-folders-code/
```

### Docker Build Failures

**Problem:** Docker image fails to build

**Solutions:**
```bash
# Check Dockerfile syntax
docker build --dry-run .

# Build with verbose output
docker build --progress=plain .

# Check dependencies
pip install -r requirements.txt
```

### Terraform Validation Failures

**Problem:** Terraform plan fails

**Solutions:**
```bash
# Format Terraform files
make terraform-format

# Check syntax
cd terraform && terraform init -backend=false && terraform validate

# Validate against actual AWS account
cd terraform && terraform init && terraform validate
```

---

## Common CI Failures & Fixes

### 1. Formatting Failure (Black)

**Error:**
```
reformatted app/api.py
would reformat app/agents/__init__.py
```

**Fix:**
```bash
make format
git add app/
git commit -m "Format code with black"
```

### 2. Import Ordering (isort)

**Error:**
```
ERROR: isort would have modified app/models.py
```

**Fix:**
```bash
make format
# isort --profile black app/ tests/
```

### 3. Type Errors (mypy)

**Error:**
```
app/scoring.py:45: error: Argument 1 to "round" has incompatible type "Optional[float]"; expected "float"
```

**Fix:**
```python
# Add type guard
if score is not None:
    result = round(score)
```

### 4. Security: Hardcoded Secret

**Error:**
```
bandit found: Probable hardcoded password assignment
```

**Fix:**
```python
# Move to environment variable
api_key = os.getenv("ANTHROPIC_API_KEY")
```

### 5. Dependency Vulnerability

**Error:**
```
pip-audit: Found vulnerability in package X version Y (CVE-2024-XXXXX)
```

**Fix:**
```bash
# Update dependency
pip install -U package_name
pip freeze > requirements.txt
git commit -m "Update package_name to fix CVE-2024-XXXXX"
```

### 6. Coverage Below 80%

**Error:**
```
Coverage: 75% (target: 80%)
```

**Fix:**
```bash
# Check uncovered lines
pytest tests/ --cov=app --cov-report=term-missing

# Write tests for uncovered code
# Add to tests/test_*.py
```

### 7. Terraform Validation Failed

**Error:**
```
Error: Invalid or missing required argument
```

**Fix:**
```bash
cd terraform
terraform fmt -recursive
terraform validate
```

### 8. Docker Build Failure

**Error:**
```
failed to build image: permission denied
```

**Fix:**
```bash
# Check Dockerfile
docker build --progress=plain .

# May need to rebuild base image
docker pull python:3.11-slim
```

### 9. Rate Limit on pip-audit

**Error:**
```
Connection timeout checking for vulnerabilities
```

**Fix:**
```bash
# Retry with delay
sleep 30 && pip-audit --desc

# Or run locally instead of CI
make deps-audit
```

---

## Adding New Tests

### Adding Test to Evaluation Suite

1. **Identify Vulnerability**
   - What is the security/data/resilience issue?
   - Where is it in the code?
   - What TIER (1-4)?

2. **Create Test Class**
   ```python
   # Add to tests/test_evaluation_suite.py
   class TestMyNewVulnerability:
       """Test: Description of vulnerability"""

       def test_vulnerability_detected(self):
           """Test that vulnerability can be detected."""
           # Arrange: Set up test conditions
           vulnerable_code = VulnerableClass()

           # Act: Execute code that triggers vulnerability
           result = vulnerable_code.dangerous_operation()

           # Assert: Verify vulnerability exists
           assert result.has_issue is True
   ```

3. **Create Fix Test**
   ```python
       def test_vulnerability_fixed(self):
           """Test that fix prevents vulnerability."""
           # Same test, but with fixed code
           fixed_code = FixedClass()
           result = fixed_code.safe_operation()
           assert result.has_issue is False
   ```

4. **Run Test**
   ```bash
   pytest tests/test_evaluation_suite.py::TestMyNewVulnerability -v
   ```

### Adding Unit Test

```bash
# Create test file
touch tests/test_myfeature.py

# Add tests
cat > tests/test_myfeature.py << 'EOF'
import pytest
from app.mymodule import my_function

def test_my_function_happy_path():
    """Test normal operation."""
    result = my_function(valid_input)
    assert result == expected_output

def test_my_function_edge_case():
    """Test edge case."""
    result = my_function(edge_input)
    assert result == edge_output

def test_my_function_error():
    """Test error handling."""
    with pytest.raises(ValueError):
        my_function(invalid_input)
EOF

# Run
pytest tests/test_myfeature.py -v
```

---

## Tuning Quality Gates

### Adjusting Coverage Threshold

Edit `quality-gates.json`:
```json
"coverage": {
  "minimum": 85,  // Changed from 80
  "target": 95,   // Changed from 90
}
```

### Disabling a Quality Check

In relevant workflow file (e.g., `.github/workflows/quality.yml`):

```yaml
- name: Run flake8
  run: |
    flake8 app/ || true  # Don't fail build
  continue-on-error: true  # Ignore failures
```

### Changing Line Length

Multiple places:

1. **Black** - `.github/workflows/quality.yml`
   ```yaml
   black --check app/ tests/ --line-length=100
   ```

2. **isort** - `.pre-commit-config.yaml`
   ```yaml
   - repo: https://github.com/pycqa/isort
     args: ['--line-length=100']
   ```

3. **flake8** - `.github/workflows/quality.yml` & `Makefile`
   ```bash
   flake8 app/ --max-line-length=100
   ```

### Enabling More Strict Checks

```bash
# Enable type checking to fail build
# In .github/workflows/quality.yml, change:
continue-on-error: false
```

---

## Monitoring & Alerts

### GitHub Status Checks

Each pull request shows status:
- ✓ Test Suite — Unit + Evaluation tests
- ✓ Security Scanning — SAST + Deps + Secrets
- ✓ Code Quality — Linting + Formatting + Types
- ✓ Performance Tests — Latency + Memory + Concurrency
- ✓ Deploy Validation — Terraform + Docker

Merge is blocked until all checks pass (for main branch).

### Codecov Coverage Tracking

Coverage reports are uploaded to Codecov (if configured). Track trends:
```
https://codecov.io/gh/your-org/ai-diagnostic-mvp
```

### Build Status Dashboard

View all workflow runs:
```
GitHub → Actions → select workflow → view runs
```

### Slack Notifications (Optional)

Add to workflow:
```yaml
- name: Slack notification on failure
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "Build failed in ${{ github.repository }}",
        "blocks": [{"type": "section", "text": {"type": "mrkdwn", "text": "Build <${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|failed>"}}]
      }
```

---

## Summary

This CI/CD pipeline provides:

✓ **Automated Testing**: Catch regressions of 22 vulnerability tests across 4 tiers  
✓ **Security Scanning**: SAST, dependency audits, secrets detection  
✓ **Code Quality**: Formatting, linting, type checking, complexity analysis  
✓ **Performance Validation**: Latency, memory, and concurrency checks  
✓ **Infrastructure Validation**: Terraform + Docker security scanning  
✓ **Pre-Commit Hooks**: Local checks before pushing  
✓ **Deployment Gates**: Pre/post-deployment checklists  

**Result**: Reliable, secure deployments with confidence in code quality.

For questions or issues, see [TROUBLESHOOTING](#troubleshooting) or check individual workflow files in `.github/workflows/`.
