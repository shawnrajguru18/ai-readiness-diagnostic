# Remediation Roadmap: Critical Vulnerabilities

**Generated:** 2026-07-10  
**Status:** Evaluation Suite Complete — Ready for Testing & Remediation  
**Target Completion:** 2026-07-24 (2 weeks)

---

## Executive Summary

**22 critical vulnerabilities** identified across 4 severity tiers. Remediation requires **~60-80 hours** of development effort. **6 vulnerabilities block production deployment** (marked P0).

| Tier | Count | Blockers | Est. Effort | Priority |
|------|-------|----------|-------------|----------|
| **Tier 1** | 6 | 4 | 20-24h | **P0** |
| **Tier 2** | 5 | 2 | 20-28h | **P0-P1** |
| **Tier 3** | 5 | 0 | 12-18h | **P1-P2** |
| **Tier 4** | 1 | 0 | 2-3h | **P3** |
| **Total** | **22** | **6** | **60-80h** | - |

---

## PHASE 1: CRITICAL BLOCKERS (Week 1)

### Sprint 1a: Security Foundation (Days 1-2)

**Goal:** Fix path traversal and prompt injection — enables safe development.

#### 1. Fix Path Traversal (Test 1.2) — 2-4 hours
**Files:** `app/content.py:32-33`

```python
# BEFORE (vulnerable):
def load_fixture(name: str) -> dict:
    return yaml.safe_load((FIXTURE_DIR / f"{name}.yaml").read_text())

# AFTER (fixed):
def load_fixture(name: str) -> dict:
    # Validate name: alphanumeric + underscore only
    if not re.match(r'^[a-zA-Z0-9_]+$', name):
        raise ValueError(f"Invalid fixture name: {name}")
    
    path = (FIXTURE_DIR / f"{name}.yaml").resolve()
    
    # Ensure path is within FIXTURE_DIR
    if not str(path).startswith(str(FIXTURE_DIR.resolve())):
        raise ValueError(f"Path traversal attempt: {name}")
    
    if not path.exists():
        raise FileNotFoundError(f"Fixture not found: {name}")
    
    return yaml.safe_load(path.read_text(encoding="utf-8"))
```

**Test:** `pytest tests/test_evaluation_suite.py::TestPathTraversal -v`

**Verification:**
```bash
# Should reject traversal attempts
curl "http://localhost:8000/api/fixture/../../etc/passwd" # → 400
curl "http://localhost:8000/api/fixture/meridianfs" # → 200 (valid)
```

---

#### 2. Add Input Sanitization (Test 1.1) — 4-6 hours
**Files:** `app/models.py`, `app/agents/__init__.py`

Create sanitization function:
```python
# app/utils/sanitization.py (new file)
import re

def sanitize_for_prompt(text: str, max_length: int = 500) -> str:
    """
    Sanitize user input before embedding in LLM prompts.
    - Remove control characters
    - Escape special sequences
    - Limit length
    """
    if not isinstance(text, str):
        return ""
    
    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f]', '', text)
    
    # Remove newlines and tabs
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    
    # Collapse multiple spaces
    text = re.sub(r' +', ' ', text).strip()
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    return text
```

Update models:
```python
# app/models.py
from app.utils.sanitization import sanitize_for_prompt

class Submission(BaseModel):
    prospect_name: str = ""
    prospect_role: str = ""
    prospect_email: str = ""
    company_name_raw: str = ""
    
    @field_validator('prospect_name', 'prospect_role', 'company_name_raw')
    def sanitize_fields(cls, v):
        return sanitize_for_prompt(v, max_length=500)
```

**Test:** `pytest tests/test_evaluation_suite.py::TestPromptInjection -v`

---

### Sprint 1b: HTTP Headers & CORS (Days 3-4)

#### 3. Fix PDF Header Injection (Test 1.3) — 1-2 hours
**Files:** `app/api.py:170-172, 177-179`

```python
# BEFORE (vulnerable):
fname = f"AI-Readiness-Scorecard-{rec['scorecard']['company_name']}.pdf"
return Response(content=pdf, media_type="application/pdf",
                headers={"Content-Disposition": f'inline; filename="{fname}"'})

# AFTER (fixed):
def sanitize_filename(name: str, max_length: int = 100) -> str:
    """Sanitize filename: remove dangerous characters."""
    # Remove control characters
    name = re.sub(r'[\x00-\x1f\x7f\r\n]', '', name)
    
    # Remove/replace filesystem-unsafe characters
    name = re.sub(r'[/:*?"<>|\\]', '-', name)
    
    # Limit length
    if len(name) > max_length:
        name = name[:max_length]
    
    return name.strip()

fname = f"AI-Readiness-Scorecard-{sanitize_filename(rec['scorecard']['company_name'])}.pdf"
return Response(
    content=pdf,
    media_type="application/pdf",
    headers={"Content-Disposition": f'attachment; filename="{fname}"'}
)
```

**Test:** `pytest tests/test_evaluation_suite.py::TestHeaderInjection -v`

---

#### 4. Fix CORS Misconfiguration (Test 1.4) — 1-2 hours
**Files:** `app/api.py:37`

```python
# BEFORE (vulnerable):
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# AFTER (fixed):
import os
from fastapi.middleware.cors import CORSMiddleware

# Read allowed origins from environment or config
ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "https://app.example.com").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
```

**Configuration:** Add to `.env` or `app/config.py`:
```python
CORS_ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "https://app.example.com,https://review.example.com"
)
```

**Test:** `pytest tests/test_evaluation_suite.py::TestCORSMisconfiguration -v`

---

### Sprint 1c: Input Validation (Days 5-7)

#### 5. Add Email Validation (Test 1.5) — 2-4 hours
**Files:** `app/models.py:42`

```python
# app/models.py
from pydantic import field_validator, EmailStr
from email_validator import validate_email, EmailNotValidError

class Submission(BaseModel):
    prospect_email: str = ""
    
    @field_validator('prospect_email')
    def validate_email_field(cls, v):
        if not v:
            return v  # Allow empty
        
        try:
            # Validate email format and normalize
            valid = validate_email(v)
            return valid.email
        except EmailNotValidError as e:
            raise ValueError(f"Invalid email: {str(e)}")
```

**Install dependency:**
```bash
pip install email-validator
```

**Test:** `pytest tests/test_evaluation_suite.py::TestEmailValidation -v`

---

#### 6. Add URL Validation (Test 1.6) — 2-4 hours
**Files:** `app/models.py:44`

```python
# app/models.py
from urllib.parse import urlparse
from pydantic import field_validator, HttpUrl
import ipaddress

BLOCKED_IP_RANGES = [
    ipaddress.ip_network("127.0.0.0/8"),      # Loopback
    ipaddress.ip_network("10.0.0.0/8"),       # Private
    ipaddress.ip_network("172.16.0.0/12"),    # Private
    ipaddress.ip_network("192.168.0.0/16"),   # Private
    ipaddress.ip_network("169.254.0.0/16"),   # Link-local
]

class Submission(BaseModel):
    company_website: str = ""
    
    @field_validator('company_website')
    def validate_url(cls, v):
        if not v:
            return v
        
        try:
            parsed = urlparse(v)
            
            # Must have http or https scheme
            if parsed.scheme not in ("http", "https"):
                raise ValueError(f"URL scheme must be http or https, got {parsed.scheme}")
            
            # Must have hostname
            if not parsed.netloc:
                raise ValueError("URL must include a domain name")
            
            # Check for blocked IPs (SSRF prevention)
            hostname = parsed.hostname
            if hostname:
                if hostname.lower() in ("localhost", "127.0.0.1"):
                    raise ValueError("Localhost URLs not allowed")
                
                try:
                    ip = ipaddress.ip_address(hostname)
                    for blocked_range in BLOCKED_IP_RANGES:
                        if ip in blocked_range:
                            raise ValueError(f"URL points to blocked IP range: {ip}")
                except ValueError as e:
                    if "does not appear to be" not in str(e):
                        raise  # Re-raise if it's our validation error
            
            # Limit length
            if len(v) > 2048:
                raise ValueError("URL must be less than 2048 characters")
            
            return v
        
        except Exception as e:
            raise ValueError(f"Invalid URL: {str(e)}")
```

**Install dependency:**
```bash
pip install httpx
```

**Test:** `pytest tests/test_evaluation_suite.py::TestURLValidation -v`

---

## PHASE 2: DATA INTEGRITY (Week 1-2)

### Sprint 2a: DynamoDB Locking (Days 8-10)

#### 7. Fix DynamoDB Race Condition (Test 2.1) — 8-12 hours
**Files:** `app/store.py:87-88, 96-106`

Add optimistic locking:

```python
# app/store.py
from typing import Optional
import uuid

class _DynamoStore:
    def put(self, rec: dict[str, Any]) -> None:
        """Put with optimistic locking."""
        # Add version/etag if not present
        if "version" not in rec:
            rec["version"] = str(uuid.uuid4())
        
        # Use conditional write
        json_doc = _rec_to_json(rec)
        
        try:
            self._table.put_item(
                Item={"id": rec["id"], "doc": json_doc, "version": rec["version"]},
                ConditionExpression="attribute_not_exists(id) OR #v = :old_version",
                ExpressionAttributeNames={"#v": "version"},
                ExpressionAttributeValues={":old_version": rec.get("old_version")}
            )
        except self._table.meta.client.exceptions.ConditionalCheckFailedException:
            raise RuntimeError(f"Concurrent modification detected for {rec['id']}")
    
    def save(self, rec: dict[str, Any]) -> None:
        """Save with version check."""
        old_version = rec.get("version")
        rec["version"] = str(uuid.uuid4())
        rec["old_version"] = old_version
        
        try:
            self.put(rec)
        except RuntimeError:
            raise ValueError("Record was modified by another process")
```

**Test:** `pytest tests/test_evaluation_suite.py::TestDynamoDBRaceCondition -v`

---

#### 8. Fix Review Decision Race (Test 2.2) — 6-8 hours
**Files:** `app/api.py:150-160`

```python
# BEFORE (vulnerable):
@app.post("/api/review/{sid}/decision")
def review_decision(sid: str, req: DecisionRequest):
    rec = store.get(sid)  # Read
    if not rec:
        raise HTTPException(404, "Not found")
    
    rec["status"] = "approved_for_delivery" if req.decision == "approved" else ...
    rec["partner_note"] = req.note
    store.save(rec)  # Write (race condition between read and write)
    return {"id": sid, "status": rec["status"]}

# AFTER (fixed with optimistic locking):
@app.post("/api/review/{sid}/decision")
def review_decision(sid: str, req: DecisionRequest):
    rec = store.get(sid)
    if not rec:
        raise HTTPException(404, "Not found")
    
    # Save original version for conflict detection
    original_version = rec.get("version")
    
    rec["status"] = "approved_for_delivery" if req.decision == "approved" else "sent_back_for_reprocessing"
    rec["partner_note"] = req.note
    rec["decision_timestamp"] = datetime.now(timezone.utc).isoformat()
    rec["decided_by"] = "partner_reviewer"  # Add audit trail
    
    try:
        store.save(rec)
        
        # Log decision for audit
        logger.info(f"Decision on {sid}: {req.decision} by {req.note}")
        
        return {"id": sid, "status": rec["status"]}
    
    except ValueError as e:
        # Version conflict: another reviewer modified this
        raise HTTPException(409, "Record was modified by another reviewer. Please refresh and try again.")
```

**Test:** `pytest tests/test_evaluation_suite.py::TestReviewDecisionRace -v`

---

### Sprint 2b: Numeric Consistency (Days 11-12)

#### 9. Fix Banker's Rounding (Test 2.3) — 2-4 hours
**Files:** `app/scoring.py:90, 104`

```python
# app/scoring.py
from decimal import Decimal, ROUND_HALF_UP

def round_half_up(value: float) -> int:
    """Consistent rounding: always round 0.5 up."""
    return int(Decimal(str(value)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))

def score_dimensions(responses: list[QuestionResponse]) -> list[DimensionScore]:
    # ... existing code ...
    
    for dim in DIMENSION_IDS:
        # ... existing logic ...
        
        # Use consistent rounding instead of round()
        score = round_half_up(weighted_sum / weight_total) if weight_total > 0 else 0
        
        # ... rest of code ...

def overall_score(dimensions: list[DimensionScore]) -> int:
    # ... existing code ...
    return round_half_up(num / den) if den else 0
```

**Test:** `pytest tests/test_evaluation_suite.py::TestBankersRounding -v`

---

#### 10. Fix Type Consistency in Scoring (Test 2.4) — 2-3 hours
**Files:** `app/content.py`, `app/models.py`

Add validation when loading question pool:

```python
# app/content.py
def load_question_pool() -> dict:
    data = yaml.safe_load((CONTENT_DIR / "question_pool.yaml").read_text())
    
    # Validate type consistency
    for question in data.get("questions", []):
        if question["type"] == "scale_1_5":
            for anchor in question.get("scale_anchors", []):
                # Ensure all scores are integers
                anchor["score"] = int(anchor["score"])
                anchor["value"] = int(anchor["value"])
    
    return data
```

**Test:** `pytest tests/test_evaluation_suite.py::TestTypeConsistency -v`

---

## PHASE 3: RESILIENCE & ERROR HANDLING (Week 2)

### Sprint 3a: Exception Handling (Days 13-14)

#### 11. Fix Bare Exception Clauses (Test 3.1) — 3-5 hours
**Files:** `app/agents/__init__.py:58-59, 115-116`

```python
# BEFORE:
except Exception as e:
    logger.warning(f"[A2] LLM failed, falling back: {e}")

# AFTER:
except (APIStatusError, ValidationError, TimeoutError, ConnectionError) as e:
    logger.warning(f"[A2] LLM failed ({type(e).__name__}), falling back: {e}")
    # Handle expected failures by falling back
except Exception as e:
    # Unexpected error — log fully and re-raise
    logger.exception(f"[A2] Unexpected error (re-raising): {e}")
    raise
```

Create exception hierarchy:

```python
# app/llm_errors.py
from anthropic import (
    APIStatusError,
    APIConnectionError,
    APITimeoutError,
    RateLimitError
)

EXPECTED_LLM_ERRORS = (
    APIStatusError,
    APIConnectionError,
    APITimeoutError,
    RateLimitError,
    ValidationError,
)
```

**Test:** `pytest tests/test_evaluation_suite.py::TestBareExceptions -v`

---

### Sprint 3b: Resilience Features (Days 15-16)

#### 12. Add Rate Limit Handling (Test 3.2) — 4-6 hours
**Files:** `app/llm.py`, `app/config.py`

```python
# app/llm.py
import asyncio
from anthropic import RateLimitError
from typing import TypeVar

T = TypeVar("T", bound=BaseModel)

def _retry_with_backoff(func, max_retries=3):
    """Decorator for retrying with exponential backoff."""
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except RateLimitError as e:
                if attempt == max_retries - 1:
                    # Last attempt failed, return error
                    logger.error(f"Rate limit exceeded after {max_retries} attempts")
                    raise
                
                # Extract retry-after header
                retry_after = 1
                if hasattr(e, 'response') and e.response:
                    retry_after = int(e.response.headers.get("Retry-After", 1))
                
                # Exponential backoff with jitter
                wait_time = retry_after * (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"Rate limited. Retrying in {wait_time:.1f}s (attempt {attempt+1}/{max_retries})")
                
                time.sleep(wait_time)
        
    return wrapper

@_retry_with_backoff
def complete_text(
    system: str,
    messages: Sequence[dict[str, Any]],
    *,
    model: str | None = None,
    effort: str | None = None,
    thinking: bool = True,
    max_tokens: int = 4000,
) -> str:
    """Generate free text with rate limit handling."""
    kwargs: dict[str, Any] = dict(
        model=model or settings.default_model,
        max_tokens=max_tokens,
        system=system,
        messages=list(messages),
        timeout=settings.llm_timeout,  # Add timeout
    )
    resp = _client.messages.create(**kwargs)
    return "".join(b.text for b in resp.content if b.type == "text").strip()
```

**Test:** `pytest tests/test_evaluation_suite.py::TestRateLimitHandling -v`

---

#### 13. Add LLM Timeouts (Test 3.3) — 2-4 hours
**Files:** `app/llm.py`, `app/config.py`

```python
# app/config.py
class Settings(BaseSettings):
    llm_timeout: float = 60.0  # seconds
    llm_max_retries: int = 3

# app/llm.py
from anthropic import APITimeoutError

def complete_text(...) -> str:
    """..."""
    kwargs = dict(
        ...,
        timeout=settings.llm_timeout,  # Set timeout
    )
    
    try:
        resp = _client.messages.create(**kwargs)
        return "".join(b.text for b in resp.content if b.type == "text").strip()
    
    except APITimeoutError:
        logger.warning("LLM call timed out, falling back to deterministic")
        raise  # Let caller handle with fallback
```

**Test:** `pytest tests/test_evaluation_suite.py::TestLLMTimeouts -v`

---

#### 14. Add JSON Error Handling (Test 3.4) — 2-3 hours
**Files:** `app/store.py:45-55`

```python
# app/store.py
def _rec_from_json(blob: str) -> dict[str, Any]:
    """Deserialize record with error handling."""
    try:
        d = json.loads(blob)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in record: {e}")
        raise ValueError(f"Corrupted record: {str(e)}")
    
    try:
        sess = d.get("session")
        return {
            "id": d["id"],
            "session": Session.model_validate(sess) if sess is not None else None,
            "scorecard": d["scorecard"],
            "created_at": d["created_at"],
            "status": d["status"],
            "partner_note": d.get("partner_note", ""),
        }
    except (KeyError, ValidationError) as e:
        logger.error(f"Invalid record structure: {e}")
        raise ValueError(f"Corrupted record: {str(e)}")
```

**Test:** `pytest tests/test_evaluation_suite.py::TestJSONDeserialization -v`

---

## PHASE 4: DATA VALIDATION (Week 2)

### Sprint 4: Input Length Constraints (Day 17)

#### 15. Add Length Constraints (Test 4.1) — 1-2 hours
**Files:** `app/models.py`

```python
# app/models.py
from pydantic import Field

class Submission(BaseModel):
    prospect_name: str = Field(default="", max_length=200)
    prospect_role: str = Field(default="", max_length=200)
    prospect_email: str = Field(default="", max_length=254)
    company_name_raw: str = Field(default="", max_length=500)
    company_website: str = Field(default="", max_length=2048)
    industry_label: str = Field(default="", max_length=100)
    hq_country: str = Field(default="", max_length=50)

class QuestionResponse(BaseModel):
    question_id: str
    text: Optional[str] = Field(default=None, max_length=5000)
    option_id: Optional[str] = Field(default=None, max_length=100)
    option_ids: list[str] = Field(default_factory=list)
    scale_value: Optional[int] = None
```

**Test:** `pytest tests/test_evaluation_suite.py::TestLengthConstraints -v`

---

## TESTING & VERIFICATION

### Run Complete Test Suite

```bash
# Install test dependencies
pip install pytest pytest-asyncio hypothesis

# Run all vulnerability tests
pytest tests/test_evaluation_suite.py -v --tb=short

# Run by tier
pytest tests/test_evaluation_suite.py -k "Test" -v --tb=short  # Tier 1
pytest tests/test_evaluation_suite.py -k "Test2" -v             # Tier 2
pytest tests/test_evaluation_suite.py -k "Test3" -v             # Tier 3
pytest tests/test_evaluation_suite.py -k "Test4" -v             # Tier 4

# Run with coverage
pytest tests/test_evaluation_suite.py --cov=app --cov-report=html

# Run integration tests
pytest tests/test_evaluation_suite.py::TestEndToEndAssessmentFlow -v
```

### Manual Testing Checklist

Before release, verify:

- [ ] Path traversal attempts are rejected (e.g., `../`, `..\\`)
- [ ] Prompt injection payloads don't influence LLM output
- [ ] PDF filenames don't contain newlines/control chars
- [ ] CORS allows only configured origins
- [ ] Email validation rejects invalid formats
- [ ] URL validation blocks internal IPs
- [ ] Concurrent operations don't lose data
- [ ] Rate-limited API calls retry with backoff
- [ ] Timeout errors don't block forever
- [ ] Scoring rounding is consistent (50.5 → 51)
- [ ] Input length limits are enforced

---

## DEPLOYMENT CHECKLIST

### Pre-Deployment

- [ ] All 22 test cases pass
- [ ] No new test failures
- [ ] Coverage maintained above 80%
- [ ] Security review approved
- [ ] Peer code review completed
- [ ] Performance impact assessed (should be minimal)

### Deployment

1. **Staging:** Deploy to staging environment, run full test suite
2. **Monitoring:** Enable error logging and rate limit alerts
3. **Production:** Blue-green deployment with rollback plan

### Post-Deployment

- [ ] Monitor error rates for first 24h
- [ ] Verify no new exceptions in logs
- [ ] Confirm CORS works as expected
- [ ] Check DynamoDB consistency lag (< 1s)
- [ ] Monitor LLM timeout/retry rates

---

## Configuration Examples

### Environment Variables

```bash
# .env or deployment config
CORS_ALLOWED_ORIGINS="https://app.example.com,https://review.example.com"
LLM_TIMEOUT=60
LLM_MAX_RETRIES=3
AIDIAG_DDB_TABLE=assessments  # DynamoDB table name
```

### Docker Configuration

```dockerfile
# Dockerfile (add validation)
RUN pip install email-validator validators

ENV CORS_ALLOWED_ORIGINS="https://app.example.com"
ENV LLM_TIMEOUT=60
```

---

## Knowledge Transfer

### Documentation

1. **Security Playbook:** `docs/SECURITY.md`
   - Input validation rules
   - Error handling patterns
   - Rate limit behavior

2. **Architecture Decision Record:** `docs/ADR-001-security-fixes.md`
   - Why each fix was chosen
   - Tradeoffs considered
   - Future improvements

### Team Training

- [ ] Security review session (1h)
- [ ] Test execution walkthrough (1h)
- [ ] Troubleshooting guide (30m)

---

## Success Criteria

**All must be true:**

1. ✅ All 22 tests implemented and passing
2. ✅ 6 P0 blockers fixed and verified
3. ✅ No regressions in existing functionality
4. ✅ Performance impact < 5% on critical paths
5. ✅ Security review board approval
6. ✅ Documentation complete
7. ✅ Team trained on changes

---

## Timeline Summary

| Phase | Sprints | Duration | Effort |
|-------|---------|----------|--------|
| **Phase 1** | 1a, 1b, 1c | Days 1-7 | 20-24h |
| **Phase 2** | 2a, 2b | Days 8-12 | 20-28h |
| **Phase 3** | 3a, 3b | Days 13-16 | 12-18h |
| **Phase 4** | 4 | Day 17 | 2-3h |
| **Testing** | - | Days 18-20 | 8-10h |
| **Deployment** | - | Days 21-22 | 4-6h |
| **Monitoring** | - | Ongoing | - |
| **Total** | - | **~4 weeks** | **~60-80h** |

**Go/No-Go Decision:** End of Day 20

---

## Contact & Support

- **Security Lead:** [Assign owner]
- **Architecture Review:** [Assign reviewer]
- **Testing Lead:** [Assign QA]
- **DevOps:** [Assign deployment owner]

Escalation email: [security-team@company.com]

---

**Document Version:** 1.0  
**Last Updated:** 2026-07-10  
**Next Review:** 2026-07-24
