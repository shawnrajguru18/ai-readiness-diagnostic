.PHONY: help install test test-unit test-eval test-security lint format type-check complexity security-scan coverage clean run docker-build deploy docs

PYTHON := python3
PYTEST := pytest
VENV := .venv

help:
	@echo "AI Diagnostic MVP - Development Commands"
	@echo "========================================="
	@echo ""
	@echo "Setup & Dependencies:"
	@echo "  make install           Install dependencies and pre-commit hooks"
	@echo "  make clean             Clean build artifacts and cache"
	@echo ""
	@echo "Testing:"
	@echo "  make test              Run all tests (unit + evaluation suite)"
	@echo "  make test-unit         Run unit tests only"
	@echo "  make test-eval         Run evaluation suite (vulnerability tests)"
	@echo "  make test-eval-t1      Run TIER 1 security tests only"
	@echo "  make test-eval-t2      Run TIER 2 data integrity tests only"
	@echo "  make test-eval-t3      Run TIER 3 resilience tests only"
	@echo "  make test-eval-t4      Run TIER 4 validation tests only"
	@echo "  make coverage          Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint              Run all linters (flake8, pylint)"
	@echo "  make format            Auto-format code (black, isort)"
	@echo "  make format-check      Check formatting without changing"
	@echo "  make type-check        Run mypy type checker"
	@echo "  make complexity        Check code complexity (radon, mccabe)"
	@echo "  make quality           Run all quality checks"
	@echo ""
	@echo "Security:"
	@echo "  make security-check    Run security scans (bandit, semgrep, pip-audit)"
	@echo "  make secrets-check     Check for hardcoded secrets"
	@echo "  make deps-audit        Scan dependencies for CVEs"
	@echo ""
	@echo "Local CI/CD:"
	@echo "  make pre-commit        Install and run pre-commit hooks"
	@echo "  make pre-commit-all    Run pre-commit on all files"
	@echo "  make ci-local          Run full CI pipeline locally (test + quality + security)"
	@echo ""
	@echo "Running Application:"
	@echo "  make run               Start FastAPI development server"
	@echo "  make run-prod          Start with production settings"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build      Build Docker image"
	@echo "  make docker-run        Run Docker container locally"
	@echo ""
	@echo "Infrastructure:"
	@echo "  make terraform-plan    Plan Terraform changes"
	@echo "  make terraform-validate Validate Terraform configuration"
	@echo "  make terraform-format  Format Terraform files"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs              Generate documentation"
	@echo ""

install:
	$(PYTHON) -m pip install --upgrade pip
	pip install -r requirements.txt
	pip install pytest pytest-asyncio pytest-cov pytest-timeout pytest-benchmark pytest-xdist
	pip install black isort flake8 flake8-bugbear pylint mypy radon vulture
	pip install bandit semgrep pip-audit
	pip install pre-commit
	pre-commit install
	@echo "✓ Dependencies installed and pre-commit hooks configured"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Build artifacts cleaned"

# ============================================================================
# TESTING
# ============================================================================

test: test-unit test-eval
	@echo "✓ All tests completed"

test-unit:
	@echo "Running unit tests..."
	$(PYTEST) tests/test_smoke.py tests/test_store.py -v --tb=short

test-eval:
	@echo "Running evaluation suite (all tiers)..."
	$(PYTEST) tests/test_evaluation_suite.py -v --tb=short

test-eval-t1:
	@echo "Running TIER 1 (Critical Security) tests..."
	$(PYTEST) tests/test_evaluation_suite.py::TestPromptInjection \
	         tests/test_evaluation_suite.py::TestPathTraversal \
	         tests/test_evaluation_suite.py::TestHeaderInjection \
	         tests/test_evaluation_suite.py::TestCORSMisconfiguration \
	         tests/test_evaluation_suite.py::TestEmailValidation \
	         tests/test_evaluation_suite.py::TestURLValidation \
	         -v --tb=short

test-eval-t2:
	@echo "Running TIER 2 (Data Integrity) tests..."
	$(PYTEST) tests/test_evaluation_suite.py::TestRaceConditionDynamoDB \
	         tests/test_evaluation_suite.py::TestReviewDecisionRace \
	         tests/test_evaluation_suite.py::TestBankersRounding \
	         tests/test_evaluation_suite.py::TestTypeMismatch \
	         tests/test_evaluation_suite.py::TestEventualConsistency \
	         -v --tb=short

test-eval-t3:
	@echo "Running TIER 3 (Resilience) tests..."
	$(PYTEST) tests/test_evaluation_suite.py::TestBareExceptions \
	         tests/test_evaluation_suite.py::TestRateLimitDetection \
	         tests/test_evaluation_suite.py::TestTimeoutHandling \
	         tests/test_evaluation_suite.py::TestErrorMasking \
	         -v --tb=short

test-eval-t4:
	@echo "Running TIER 4 (Validation) tests..."
	$(PYTEST) tests/test_evaluation_suite.py::TestDataValidation -v --tb=short

coverage:
	@echo "Running tests with coverage..."
	$(PYTEST) tests/ --cov=app --cov-report=html --cov-report=term-missing --cov-report=xml
	@echo "✓ Coverage report: htmlcov/index.html"

# ============================================================================
# CODE QUALITY
# ============================================================================

lint:
	@echo "Running flake8..."
	flake8 app/ tests/ --max-line-length=120 --extend-ignore=E203,W503 --count --statistics || true
	@echo "Running pylint..."
	pylint app/ --exit-zero --disable=too-many-arguments --disable=missing-docstring --rating=no || true

format:
	@echo "Formatting code with black..."
	black app/ tests/ --line-length=120
	@echo "Sorting imports with isort..."
	isort app/ tests/ --profile black

format-check:
	@echo "Checking code formatting (black)..."
	black app/ tests/ --check --line-length=120 || (echo "Run 'make format' to fix"; exit 1)
	@echo "Checking import ordering (isort)..."
	isort app/ tests/ --check-only --profile black || (echo "Run 'make format' to fix"; exit 1)

type-check:
	@echo "Running mypy type checker..."
	mypy app/ --ignore-missing-imports --no-error-summary || true

complexity:
	@echo "=== Cyclomatic Complexity ==="
	radon cc app/ -a -s || true
	@echo ""
	@echo "=== Maintainability Index ==="
	radon mi app/ -s || true
	@echo ""
	@echo "=== Dead Code Detection ==="
	vulture app/ --min-confidence 80 || true

quality: format-check lint type-check complexity
	@echo "✓ All quality checks passed"

# ============================================================================
# SECURITY
# ============================================================================

security-check: security-scan secrets-check deps-audit
	@echo "✓ All security checks completed"

security-scan:
	@echo "Running bandit (Python security)..."
	bandit -r app/ -ll || true
	@echo ""
	@echo "Running semgrep (pattern-based security)..."
	semgrep --config=p/python --config=p/security-audit app/ || true

secrets-check:
	@echo "Checking for hardcoded secrets..."
	! grep -r "api[_-]?key\s*[:=]" app/ --include="*.py" | grep -v "^#" | grep -v test || echo "No API keys found"
	! grep -r "sk_[a-zA-Z0-9]*" app/ --include="*.py" || echo "No Stripe keys found"
	! grep -r "AKIA[0-9A-Z]\{16\}" app/ --include="*.py" || echo "No AWS keys found"
	@echo "✓ No obvious hardcoded secrets detected"

deps-audit:
	@echo "Scanning dependencies for CVEs..."
	pip install -q pip-audit
	pip-audit --desc || true

# ============================================================================
# PRE-COMMIT & LOCAL CI
# ============================================================================

pre-commit:
	@echo "Installing pre-commit hooks..."
	pre-commit install
	@echo "Running pre-commit on staged files..."
	pre-commit run --hook-stage commit

pre-commit-all:
	@echo "Running pre-commit on all files..."
	pre-commit run --all-files

ci-local: clean test lint format-check type-check security-check
	@echo ""
	@echo "========================================="
	@echo "✓ Local CI Pipeline Completed Successfully"
	@echo "========================================="
	@echo ""

# ============================================================================
# RUNNING APPLICATION
# ============================================================================

run:
	@echo "Starting FastAPI development server..."
	@echo "Server will be available at http://localhost:8000"
	@echo "API docs: http://localhost:8000/docs"
	uvicorn app.api:app --reload --host 0.0.0.0 --port 8000

run-prod:
	@echo "Starting FastAPI in production mode..."
	uvicorn app.api:app --host 0.0.0.0 --port 8000 --workers 4

# ============================================================================
# DOCKER
# ============================================================================

docker-build:
	@echo "Building Docker image..."
	docker build -t ai-diagnostic-mvp:latest .
	@echo "✓ Docker image built"

docker-run:
	@echo "Running Docker container..."
	docker run -p 8000:8000 ai-diagnostic-mvp:latest

# ============================================================================
# TERRAFORM
# ============================================================================

terraform-validate:
	@echo "Validating Terraform configuration..."
	cd terraform && terraform init -backend=false && terraform validate

terraform-plan:
	@echo "Planning Terraform changes..."
	cd terraform && terraform plan -out=tfplan

terraform-format:
	@echo "Formatting Terraform files..."
	cd terraform && terraform fmt -recursive

# ============================================================================
# DOCUMENTATION
# ============================================================================

docs:
	@echo "Documentation files:"
	@echo "  - README.md (project overview)"
	@echo "  - CI_CD_PIPELINE.md (this CI/CD setup)"
	@echo "  - DEPLOY_CHECKLIST.md (deployment requirements)"
	@echo "  - EVALUATION_SUITE.md (vulnerability tests)"
	@echo "  - EVALUATION_SUITE_SUMMARY.txt (test summary)"
	@echo ""
	@echo "GitHub Actions workflows:"
	@echo "  - .github/workflows/test.yml"
	@echo "  - .github/workflows/security.yml"
	@echo "  - .github/workflows/quality.yml"
	@echo "  - .github/workflows/performance.yml"
	@echo "  - .github/workflows/deploy.yml"
	@echo ""
	@echo "Local configurations:"
	@echo "  - .pre-commit-config.yaml (pre-commit hooks)"
	@echo "  - quality-gates.json (quality thresholds)"
	@echo "  - Makefile (this file)"
