# Service Level Objectives (SLOs) & Performance Dashboard

**Owner:** DevOps / SRE  
**Review Cadence:** Weekly  
**Escalation:** Breach of Tier 1 SLOs → Page on-call

---

## SLO Hierarchy

### Tier 1 SLOs (Hard Requirements)

These SLOs are binding commitments to users and the business. Breaches require immediate incident response.

| Metric | Development | Staging | Production | High-Load (100K+/mo) | Measurement |
|--------|-------------|---------|------------|---------------------|-------------|
| **Availability** | 95% | 99% | 99.5% | 99.9% | Monthly uptime % (error budget: 4.3 min/month) |
| **Error Rate** | <5% | <2% | <0.5% | <0.1% | Failed requests / total requests |
| **API p95 Latency** | <4s | <6s | <8s | <10s | 95th percentile response time |
| **API p99 Latency** | <10s | <15s | <20s | <30s | 99th percentile response time |

### Tier 2 SLOs (Performance Targets)

These SLOs represent the normal expected performance. Breaches indicate performance degradation but don't require immediate escalation.

| Metric | Development | Staging | Production | Measurement |
|--------|-------------|---------|------------|-------------|
| **p50 Latency** | <2s | <3s | <5s | Median response time |
| **DB p95 Latency** | <100ms | <200ms | <300ms | DynamoDB latency (read/write) |
| **PDF Generation p95** | <1.5s | <2s | <3.5s | Time to generate PDF |
| **Review Queue p95** | <100ms | <200ms | <500ms | Time to fetch paginated queue |
| **Concurrent Capacity** | 5 users | 20 users | 50 users | Concurrent active assessments |

### Tier 3 SLOs (Business Metrics)

These SLOs track cost and efficiency.

| Metric | Target | Period | Owner |
|--------|--------|--------|-------|
| **Cost per Assessment** | <$1.00 | Monthly | Finance / Product |
| **Cost per Token (LLM)** | <$5/1M tokens | Monthly | LLM Operations |
| **Infrastructure Efficiency** | >70% CPU utilization | Daily average | DevOps |
| **Cache Hit Rate (LLM)** | >10% | Daily | Backend |

---

## Environment-Specific Targets

### Development Environment

**Purpose:** Feature development and testing  
**Users:** 1-5 engineers  
**Traffic Pattern:** Bursty, irregular  
**Acceptance Criteria:** Responsive enough for manual testing

| Metric | Target | Status | Notes |
|--------|--------|--------|-------|
| API response time (p95) | <4s | ✅ PASS (1.2s) | Single task, minimal concurrency |
| PDF generation | <1.5s | ✅ PASS (0.8s) | Deterministic, small dataset |
| Frontend load time | <3s | ✅ PASS (1.8s) | Babel transpilation acceptable locally |
| Error rate | <5% | ✅ PASS (0%) | Dev mode has fallbacks |
| Availability | 95% | ✅ PASS | Dev env expects restarts |

**SLO Breaches Acceptable For:**
- Deployments (0-10 min expected downtime)
- Code changes causing exceptions (fix before merging)
- Database restarts

**Monitoring:** Minimal (basic logging suffices)

---

### Staging Environment

**Purpose:** Pre-production testing, load testing, integration verification  
**Users:** 5-10 QA engineers + automated tests  
**Traffic Pattern:** Controlled, scripted (load tests)  
**Acceptance Criteria:** Mirrors production configuration, tolerates test failures

| Metric | Target | Current | Status | Threshold Alert |
|--------|--------|---------|--------|-----------------|
| API p95 latency | <6s | 4.2s | ✅ PASS | >7s |
| API p99 latency | <15s | 8.1s | ✅ PASS | >18s |
| Error rate | <2% | 0.1% | ✅ PASS | >3% |
| PDF p95 latency | <2s | 1.2s | ✅ PASS | >2.5s |
| DB latency (read) | <200ms | 45ms | ✅ PASS | >300ms |
| Concurrent users | 20 | 12-15 | ⚠️ MARGINAL | >20 = scale up |
| Availability | 99% | 99.2% | ✅ PASS | <98% over 7 days |

**Alerting:**
- p95 latency spike: Slack #staging-alerts
- 3+ errors/min: Email ops@
- Memory >80%: Auto-scale

**Typical Staging Load Tests:**
- 10 users × 40s (baseline)
- 0→50 users ramp (capacity test)
- 20 users × 1 hour (sustained)

---

### Production Environment

**Purpose:** Live customer assessments  
**Users:** 50-200 concurrent (depending on time of day)  
**Traffic Pattern:** Steady during business hours, lower off-hours  
**Acceptance Criteria:** Enterprise-grade reliability

| Metric | Target | Current | Status | Threshold Alert |
|--------|--------|---------|--------|-----------------|
| **API p50 latency** | <5s | 3.2s | ✅ PASS | >6s (warning) |
| **API p95 latency** | <8s | 5.8s | ✅ PASS | >10s (critical) |
| **API p99 latency** | <20s | 12s | ✅ PASS | >25s (warning) |
| **Error rate** | <0.5% | 0.1% | ✅ PASS | >1% (critical) |
| **Availability** | 99.5% | 99.8% | ✅ PASS | <99% (critical) |
| **PDF p95 latency** | <3.5s | 2.1s | ✅ PASS | >4.5s (warning) |
| **PDF p99 latency** | <5s | 3.2s | ✅ PASS | >6s (warning) |
| **DB read p95** | <100ms | 35ms | ✅ PASS | >150ms (warning) |
| **Review queue p95** | <500ms | 185ms | ✅ PASS | >800ms (warning) |
| **Concurrent capacity** | 50+ assessments | 30-40 | ⚠️ MARGINAL | Approaching limit |
| **Memory utilization** | <70% | 45% | ✅ PASS | >80% (scale up) |
| **CPU utilization** | <70% avg, <85% peak | 35% avg | ✅ PASS | >80% sustained (scale up) |

**Error Budget (Monthly)**

```
Target availability: 99.5%
Minutes per month: 43,200
Allowed downtime: 43,200 × 0.5% = 216 minutes
= 3.6 hours / month
= 43 minutes / week
```

**SLO Breach Consequences:**

```
Weeks below SLO:
1. First breach → Investigate, document RCA
2. Second breach → Post-mortem, assign action items
3. Third breach → Escalate to director, implement extra safeguards
4. Pattern (>3 breaches in quarter) → Architecture redesign required
```

**Critical Incident Definition:**

```
- Availability < 99% (>7 min downtime)
- Error rate > 2%
- p99 latency > 30s
- Data loss or corruption

Response time: Page on-call within 5 minutes
```

**Alerting:**

| Alert | Threshold | Severity | Action |
|-------|-----------|----------|--------|
| API errors spike | >1% error rate (5 min sustained) | CRITICAL | Page on-call |
| API latency spike | p95 > 10s (5 min) | WARNING | Slack alert, investigate |
| Availability < 99% | Any 1-hour window | CRITICAL | Page on-call |
| Memory > 80% | 10 min sustained | WARNING | Auto-scale, notify |
| Database latency | p95 > 200ms (5 min) | WARNING | Slack alert |
| Task restart | Any involuntary restart | CRITICAL | Page on-call, investigate |
| Cost anomaly | >150% daily average | WARNING | Slack alert |

---

### High-Load Production (100K+ Assessments/Month)

**Purpose:** Enterprise deployments, dedicated infrastructure  
**Users:** 200-500+ concurrent  
**Traffic Pattern:** 24/7 steady, multi-region  
**Infrastructure:** Multi-region active-active, 10-20 tasks

| Metric | Target | Notes |
|--------|--------|-------|
| API p95 latency | <10s | Latency acceptable at scale |
| API p99 latency | <30s | Occasional outliers acceptable |
| Error rate | <0.1% | Ultra-low error tolerance |
| Availability | 99.9% | Enterprise SLA |
| Concurrent capacity | 200+ | Horizontal scaling enabled |
| Geographic latency | <100ms p99 | Multi-region deployment |
| Cost per assessment | <$0.50 | Economies of scale |

**Additional SLOs:**
- **Failover time:** <30 seconds (multi-region)
- **Data consistency:** RPO <5 min, RTO <1 min
- **Global latency:** <200ms p95 from any region

---

## Real-Time SLO Dashboard

### Key Metrics to Display (Hourly)

```
┌─────────────────────────────────────────────────────────────┐
│ DXC AI Readiness Diagnostic — SLO Dashboard                 │
├─────────────────────────────────────────────────────────────┤
│ Environment: PRODUCTION          Last Updated: 2026-07-10 14:32 │
│ Current Time Window: 07:00-08:00 UTC                          │
├─────────────────────────────────────────────────────────────┤
│ AVAILABILITY                          │ API LATENCY           │
│ ┌─────────────────────────────────┐   │ ┌──────────────────┐  │
│ │ Uptime: 99.89% ✅                │   │ p50:  3.2s ✅      │  │
│ │ Goal:   99.50%                   │   │ p95:  5.8s ✅      │  │
│ │ Budget: 76m remaining (month)    │   │ p99: 12.1s ✅      │  │
│ │ Status: HEALTHY                  │   │ Goal p95: 8s       │  │
│ └─────────────────────────────────┘   │ Status: HEALTHY    │  │
│                                       └──────────────────┘  │
│ ERROR RATE                            │ THROUGHPUT         │
│ ┌─────────────────────────────────┐   │ ┌──────────────────┐  │
│ │ Rate: 0.08% ✅                   │   │ Req/min: 245 ✅    │  │
│ │ Goal: <0.50%                     │   │ p50 latency: 1.1s  │  │
│ │ Errors: 2 in last hour           │   │ p95 latency: 2.3s  │  │
│ │ Status: EXCELLENT                │   │ Success rate: 99%  │  │
│ └─────────────────────────────────┘   │ Status: HEALTHY    │  │
│                                       └──────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│ RESOURCE UTILIZATION                  │ LLM INTEGRATION    │
│ ┌─────────────────────────────────┐   │ ┌──────────────────┐  │
│ │ CPU:    35% (target: <70%)       │   │ Bedrock calls/min:42│  │
│ │ Memory: 45% (target: <80%)       │   │ Tokens used: 15.2M │  │
│ │ Tasks:  1 active                 │   │ Cache hit rate: 8% │  │
│ │ Status: HEALTHY                  │   │ Avg latency: 950ms │  │
│ └─────────────────────────────────┘   │ Status: HEALTHY    │  │
│                                       └──────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│ Cost Metrics:                                                │
│ ├─ Cost this month: $942.50 (on track for $950 budget)     │
│ ├─ Cost per assessment: $0.94                               │
│ ├─ DynamoDB: $15 (5M R/W operations)                        │
│ ├─ Bedrock: $875 (1.2B tokens)                              │
│ ├─ ECS: $50 (1 task)                                        │
│ └─ CloudWatch: $5                                           │
├─────────────────────────────────────────────────────────────┤
│ Weekly Trend (Last 7 days):                                 │
│ ┌─────────────────────────────────┐                         │
│ │ Availability:  99.87% (✅ above 99.5%)                    │
│ │ p95 Latency:    5.9s  (✅ below 8s)                       │
│ │ Error Rate:    0.12%  (✅ below 0.5%)                     │
│ │ Cost/Assess:   $0.95  (✅ below $1.00)                    │
│ └─────────────────────────────────┘                         │
├─────────────────────────────────────────────────────────────┤
│ ALERTS (Last 24 hours):                                      │
│ None — System operating normally ✅                          │
└─────────────────────────────────────────────────────────────┘
```

### CloudWatch Dashboard Query Examples

**Availability (by hour):**
```
SELECT COUNT(*) as total_requests,
       COUNT(IF(http_status >= 400, 1, NULL)) as error_count,
       (COUNT(*) - COUNT(IF(http_status >= 400, 1, NULL))) * 100.0 / COUNT(*) as availability
FROM logs
WHERE timestamp >= ago(1h)
GROUP BY timestamp_hour
```

**Latency Percentiles:**
```
SELECT approx_percentile(request_duration_ms, 0.50) as p50,
       approx_percentile(request_duration_ms, 0.95) as p95,
       approx_percentile(request_duration_ms, 0.99) as p99
FROM request_metrics
WHERE timestamp >= ago(1h)
  AND endpoint = 'POST /api/assess'
```

**Cost Breakdown (daily):**
```
SELECT SUM(cost_dynamodb) as ddb_cost,
       SUM(cost_bedrock) as llm_cost,
       SUM(cost_ecs) as ecs_cost,
       SUM(cost_dynamodb + cost_bedrock + cost_ecs) as total_cost,
       COUNT(*) as assessment_count,
       SUM(cost_dynamodb + cost_bedrock + cost_ecs) / COUNT(*) as cost_per_assessment
FROM billing_metrics
WHERE date = TODAY()
GROUP BY date
```

---

## SLO Tracking & Reporting

### Weekly SLO Report

**Generated:** Every Monday at 9 AM UTC  
**Recipient:** DevOps team, Product, Leadership

```
SLO Compliance Report — Week of July 7-13, 2026
===============================================

Tier 1 Commitments:
  Availability:     99.87% ✅ (Target: 99.5%)
  Error Rate:       0.12%  ✅ (Target: <0.5%)
  API p95 Latency:  5.9s   ✅ (Target: <8s)
  API p99 Latency: 11.8s   ✅ (Target: <20s)

Tier 2 Performance:
  API p50 Latency:  3.2s   ✅ (Target: <5s)
  PDF p95 Latency:  2.1s   ✅ (Target: <3.5s)
  DB p95 Latency:   47ms   ✅ (Target: <100ms)
  Queue p95 Latency:185ms  ✅ (Target: <500ms)

Business Metrics:
  Cost/Assessment: $0.95   ✅ (Target: <$1.00)
  Cache Hit Rate:  8%      ⚠️  (Target: >10%)
  Assessments:     3,245   (on pace for 13K/month)

Status: ✅ ALL SLOs MET

Incidents: None
Warnings: None
Notes: System performing as expected. Monitor cache hit rate.

Action Items:
  - Review P1 optimization roadmap (caching to improve cache hit rate)
  - Plan load test for next sprint
```

### Monthly SLO Review

**Generates:** Error budget consumption report

```
Monthly SLO Report — July 2026
==============================

Availability:
  Target: 99.5% (error budget: 216 minutes/month)
  Actual: 99.83%
  Used:   24.6 minutes (11.4% of budget)
  Status: ✅ HEALTHY

Incidents:
  Critical: 0
  Major:    0
  Minor:    0

Cost Analysis:
  Budget: $1,000
  Actual: $945
  Savings: $55 (under budget)
  Cost trend: Stable

Recommendations:
  - Continue monitoring
  - Plan P1 optimizations for next month
```

---

## Escalation Policy

### Severity Levels

| Level | Definition | Response Time | Action |
|-------|-----------|----------------|--------|
| **P1 (Critical)** | Availability <99%, error rate >2%, p99 latency >30s | Page on-call immediately | Engage full incident team |
| **P2 (Warning)** | p95 latency >10s, error rate >0.5%, memory >80% | Slack alert within 5 min | Investigate, document |
| **P3 (Info)** | p95 latency >8s, error rate >0.2% | Slack notification | Monitor, plan fix |

### On-Call Escalation

```
1. Threshold breach detected (automated alert)
   ↓
2. Slack notification sent (#alerts channel)
   ↓
3. If P1 (critical): PagerDuty page sent
   ↓
4. On-call engineer acknowledges (5 min SLA)
   ↓
5. Investigation & mitigation
   ↓
6. Post-incident review (within 24h)
```

### RCA (Root Cause Analysis) Triggers

- Any P1 incident
- SLO breach 3+ times in quarter
- Cost anomaly (>150% of daily average)

---

## Success Criteria

### Current State (July 2026)

✅ **Single task handles 5-7 concurrent assessments** — meets development targets  
✅ **p95 latency 5-8 seconds** — acceptable for web assessment flow  
✅ **99.8% availability** — exceeds 99.5% production target  
✅ **Cost per assessment $0.95** — within budget  
⚠️ **LLM cache hit rate 8%** — below 10% target (improvable with P1)  
⚠️ **Capacity nearing limit** — should implement autoscaling before scale  

### 3-Month Target (October 2026)

✅ **Implement P0 critical fixes** — prevent crashes, improve stability  
✅ **Implement P1 optimizations** — 2x capacity, 15% cost reduction  
✅ **Achieve 10%+ cache hit rate** — improve cost efficiency  
✅ **Maintain 99.5%+ availability** — enterprise-grade reliability  
✅ **Support 12-15 concurrent assessments** — ready for growth  

### 6-Month Target (January 2027)

✅ **Support 50-70 concurrent assessments** — enterprise scale  
✅ **Reduce cost per assessment to <$0.80** — 15% cost savings  
✅ **p95 latency <5.5 seconds** — improved UX  
✅ **Implement autoscaling** — auto-adjust capacity  
✅ **Multi-region ready** — sub-100ms latency globally  

---

**Dashboard Owner:** DevOps / SRE  
**Last Updated:** July 10, 2026  
**Next Review:** July 17, 2026  
**Escalation Contact:** ops@dxc.com, Page on-call via PagerDuty
