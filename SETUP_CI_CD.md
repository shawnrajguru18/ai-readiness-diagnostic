# CI/CD Pipeline Setup Guide

**Quick Setup Instructions for AI Diagnostic MVP**

**Time Required:** ~15 minutes for initial setup, ~5 minutes per future commit

---

## TL;DR - Quick Start

```bash
# One-time setup (5 minutes)
make install

# Before every commit (automatic via pre-commit)
git add .
git commit -m "your message"  # Pre-commit hooks run automatically

# Or manually test everything before pushing
make ci-local  # Runs full CI pipeline locally (takes ~2-3 minutes)

# Push to GitHub
git push origin feature-branch
```

---

## Step 1: Initial Setup (One Time)

### 1.1 Install Python Dependencies

```bash
cd /path/to/ai-diagnostic-mvp

# Ensure Python 3.11+
python3 --version  # Should be 3.11.x or 3.12.x

# Install all dependencies
make install

# Or manually:
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov pytest-timeout pytest-benchmark
pip install black isort flake8 flake8-bugbear pylint mypy radon vulture
pip install bandit semgrep pip-audit pre-commit
```

### 1.2 Install Pre-Commit Hooks

```bash
# Automatically installed by "make install" above
# If not, run manually:
pre-commit install

# Verify installation
pre-commit run --all-files  # Run on all files to check for issues
```

### 1.3 Verify Setup

```bash
# Test that everything works
make test-unit          # Should pass
make lint               # Should run without critical errors
make security-check     # Should run all security scans
```

---

## Step 2: Daily Development Workflow

### 2.1 Make Code Changes

```bash
git checkout -b feature/my-feature
# ... write code ...
```

### 2.2 Test Locally

```bash
# Run tests relevant to your changes
make test-unit         # Quick unit tests

# Or more comprehensive
make test              # All tests
make coverage          # With coverage report
```

### 2.3 Format & Lint

```bash
# Auto-format code
make format

# Check for any remaining issues
make lint
```

### 2.4 Security Check (Optional)

```bash
# Quick security scan
make security-check

# Or individual scans
bandit -r app/ -ll      # Python security
pip-audit --desc        # Dependency CVEs
```

### 2.5 Commit Code

```bash
git add .

# Pre-commit hooks run automatically:
git commit -m "feat: Add new feature"

# Pre-commit will:
# 1. Check code formatting (Black)
# 2. Sort imports (isort)
# 3. Check for secrets
# 4. Lint code (flake8)
# 5. Type check (mypy)
# 6. Security check (bandit)

# If issues found, fix and retry:
git add .
git commit -m "feat: Add new feature"
```

### 2.6 Push to Remote

```bash
git push origin feature/my-feature

# GitHub Actions workflows trigger automatically
# Check progress: GitHub → Actions tab
# All checks must pass before merging
```

---

## Step 3: GitHub Actions Checks

Once you push, GitHub automatically runs:

### 3.1 Test Suite (5-15 min)
```
✓ Unit tests (Python 3.11, 3.12)
✓ TIER 1 security tests (MUST PASS)
✓ TIER 2 data integrity tests (MUST PASS)
✓ TIER 3 resilience tests (warn only)
✓ TIER 4 validation tests (warn only)
✓ Coverage report
```

**Status in PR:** "Test Suite (Evaluation + Unit Tests)"

### 3.2 Security Scanning (10-20 min)
```
✓ Bandit (Python SAST)
✓ Semgrep (pattern analysis)
✓ pip-audit (CVE detection)
✓ Secrets detection
✓ CodeQL (advanced analysis)
```

**Status in PR:** "Security Scanning (SAST + Dependencies + Secrets)"

### 3.3 Code Quality (5-10 min)
```
✓ Black formatting check
✓ isort import ordering
✓ flake8 linting
✓ pylint analysis
✓ mypy type checking
✓ Complexity analysis
✓ Dead code detection
```

**Status in PR:** "Code Quality (Linting, Formatting, Complexity)"

### 3.4 Performance Tests (10-15 min)
```
✓ Latency benchmarks
✓ Memory usage tests
✓ Concurrent request handling
```

**Status in PR:** "Performance & Load Testing"

### 3.5 Deployment Validation (5-10 min)
```
✓ Terraform validation
✓ Infrastructure security (tfsec)
✓ Docker build
✓ Container scanning (Trivy)
```

**Status in PR:** "Deploy Validation (Infrastructure & Terraform)"

---

## Common Tasks

### Running Specific Tests

```bash
# All vulnerability tests
make test-eval

# Specific vulnerability tier
make test-eval-t1      # Security (critical)
make test-eval-t2      # Data integrity (critical)
make test-eval-t3      # Resilience (important)
make test-eval-t4      # Validation (nice-to-have)

# Specific test
pytest tests/test_evaluation_suite.py::TestPromptInjection -v

# With output
pytest tests/test_evaluation_suite.py -v -s

# Stop on first failure
pytest tests/ -x
```

### Checking Code Coverage

```bash
# Generate coverage report
make coverage

# View interactive HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov\index.html  # Windows
```

### Running Security Scans

```bash
# All security scans
make security-check

# Individual scans
bandit -r app/          # SAST
pip-audit --desc        # CVE check
grep -r "api_key" app/  # Hardcoded secrets
```

### Formatting Code

```bash
# Auto-fix formatting
make format

# Check without changing
make format-check
```

### Simulating Full CI Locally

```bash
# Run complete CI pipeline locally (takes ~2-3 minutes)
make ci-local

# Or step by step
make clean              # Clean cache
make test              # Run tests
make lint              # Run linters
make format-check      # Check formatting
make type-check        # Type checking
make security-check    # Security scans
```

---

## Troubleshooting

### Issue: Pre-commit hooks fail on commit

**Problem:** Pre-commit finds formatting issues
```
black would reformat app/api.py
isort would reformat app/models.py
```

**Solution:**
```bash
# Auto-fix with make
make format

# Then retry commit
git add .
git commit -m "your message"
```

### Issue: "Permission denied" running make commands

**Solution:**
```bash
# Ensure you have proper permissions
chmod +x Makefile  # Usually not necessary

# Or use python directly
python -m pytest tests/ -v
python -m black --check app/
```

### Issue: Tests fail locally but pass in CI (or vice versa)

**Solutions:**
```bash
# Clear all caches
make clean

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check Python version
python3 --version

# Run with verbose output
pytest tests/ -v -s --tb=long
```

### Issue: Coverage below 80%

```bash
# Check which lines are uncovered
make coverage

# Review htmlcov/index.html for uncovered code

# Write tests for uncovered lines
# Then re-run: make coverage
```

### Issue: "Command not found" for make

**Solution:** Install GNU Make
```bash
# macOS
brew install make

# Ubuntu/Debian
sudo apt-get install make

# Windows (use PowerShell in repo directory)
# Commands also work without make, using python directly
python -m pytest tests/
```

---

## Pre-Commit Hook Details

Pre-commit hooks run **before each commit**. Here's what they check:

1. **File Checks** (~1 sec)
   - Trailing whitespace removed
   - Files end with newline
   - YAML/JSON valid
   - Large files rejected (> 500KB)
   - No merge conflicts

2. **Code Formatting** (~10 sec)
   - Black: Code style consistent
   - isort: Imports sorted alphabetically

3. **Code Analysis** (~20 sec)
   - flake8: Style violations
   - mypy: Type mismatches
   - pydocstyle: Docstring format

4. **Security** (~10 sec)
   - bandit: Hardcoded secrets, unsafe functions
   - detect-secrets: API keys, credentials

5. **Infrastructure** (~5 sec)
   - Terraform formatting & validation
   - YAML linting

**Total time:** ~45 seconds (cached, subsequent runs faster)

### Skipping Pre-Commit (Not Recommended)

```bash
# Skip pre-commit (use sparingly!)
git commit -m "message" --no-verify

# Better: Fix the issues
make format
git add .
git commit -m "message"
```

---

## GitHub Actions Workflow Status

### Checking Workflow Status

1. **In GitHub Web UI:**
   - Go to Pull Request
   - Scroll to "Checks" section
   - See status of all workflows

2. **In Terminal:**
   ```bash
   # View latest workflow run
   gh run list --limit 5
   
   # View specific run
   gh run view <run_id>
   ```

### Workflow Badges (in PR)

- ✓ **Green checkmark**: All checks passed
- ✗ **Red X**: Some checks failed
- ⏱ **Yellow circle**: Checks running
- ⊘ **Gray dash**: Checks skipped

### Common Failures

| Failure | Cause | Fix |
|---------|-------|-----|
| Test Suite fails | TIER 1/2 test fails | Review test output, fix code |
| Security fails | Vulnerability found | Fix security issue, update code |
| Quality fails | Formatting/linting | Run `make format` |
| Performance fails | Latency/memory issue | Optimize code, check for regressions |
| Deploy fails | Terraform/Docker issue | Fix infrastructure code |

### Viewing Workflow Logs

1. **GitHub Web:**
   - PR → Checks → Click workflow name → View logs

2. **Terminal:**
   ```bash
   # Download and view logs
   gh run view <run_id> --log
   ```

---

## Deployment Workflow

Once all checks pass, you can deploy:

### 1. Merge to Main

```bash
# All CI checks must pass
# Requires code review approval (1 reviewer minimum)

# GitHub will merge automatically (or manual button click)
```

### 2. Verify Deployment

```bash
# After merge to main, deployment workflow runs
# Follow: GitHub → Actions → Deployment workflow

# Verify deployment succeeded:
# - All checks passed
# - No errors in logs
# - Application responding
```

### 3. Monitor Production

```bash
# Check CloudWatch logs (if configured)
# Monitor error rate, latency, throughput
# Verify functionality in production environment
```

---

## Reference Commands

### Development

```bash
make help                      # Show all available commands
make install                   # Initial setup
make clean                     # Clean build artifacts
make run                       # Start dev server
```

### Testing

```bash
make test                      # All tests
make test-unit                 # Unit tests only
make test-eval                 # Evaluation suite
make test-eval-t1              # TIER 1 (security)
make test-eval-t2              # TIER 2 (data integrity)
make test-eval-t3              # TIER 3 (resilience)
make test-eval-t4              # TIER 4 (validation)
make coverage                  # Coverage report
```

### Code Quality

```bash
make format                    # Auto-format code
make format-check              # Check without changing
make lint                      # Run all linters
make type-check                # Type checking
make complexity                # Complexity analysis
make quality                   # All quality checks
```

### Security

```bash
make security-check            # All security scans
make secrets-check             # Hardcoded secrets
make deps-audit                # Dependency CVEs
```

### CI/CD

```bash
make pre-commit                # Run pre-commit hooks
make pre-commit-all            # Run on all files
make ci-local                  # Simulate full CI
```

### Infrastructure

```bash
make docker-build              # Build Docker image
make docker-run                # Run Docker container
make terraform-validate        # Terraform validation
make terraform-plan            # Terraform plan
make terraform-format          # Terraform formatting
```

---

## Documentation

- **CI_CD_PIPELINE.md**: Comprehensive pipeline documentation (1000+ lines)
- **DEPLOY_CHECKLIST.md**: Deployment procedures and checklists
- **CI_CD_PIPELINE_SUMMARY.md**: Overview and quick reference
- **Makefile**: `make help` for command reference
- **.github/workflows/**: Individual workflow files with comments

---

## Getting Help

1. **Check documentation:**
   - CI_CD_PIPELINE.md → Troubleshooting section
   - DEPLOY_CHECKLIST.md → Common issues

2. **Check workflow logs:**
   - GitHub Actions → Failed workflow → View logs
   - Look for error messages and stack traces

3. **Run tests locally:**
   - `make test -v` for verbose output
   - `pytest tests/ -v -s` for even more detail

4. **Check Git status:**
   ```bash
   git status
   git log --oneline -10
   git diff
   ```

5. **Ask the team:**
   - Slack #dev-help
   - Create GitHub issue with details

---

## Best Practices

✓ **Do:** Run `make ci-local` before pushing
✓ **Do:** Keep commits small and focused
✓ **Do:** Write tests for new code
✓ **Do:** Review your own PR first

✗ **Don't:** Commit without pre-commit hooks
✗ **Don't:** Push without running local tests
✗ **Don't:** Ignore failed CI checks
✗ **Don't:** Use `--no-verify` to skip pre-commit (unless absolutely necessary)

---

## Summary

1. **Setup:** `make install` (one time)
2. **Daily:** Write code → `make format` → `git commit` (hooks run automatically)
3. **Push:** `git push origin feature-branch`
4. **Verify:** GitHub Actions runs all checks automatically
5. **Merge:** When all checks pass and code reviewed, merge to main
6. **Deploy:** Deployment workflow runs automatically after merge

**Happy coding!** 🚀

For detailed information, see [CI_CD_PIPELINE.md](CI_CD_PIPELINE.md) and [DEPLOY_CHECKLIST.md](DEPLOY_CHECKLIST.md).
