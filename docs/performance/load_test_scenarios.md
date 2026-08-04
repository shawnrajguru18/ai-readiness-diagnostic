# Load Testing Scenarios — DXC AI Readiness Diagnostic MVP

**Purpose:** Verify infrastructure capacity and identify bottlenecks under realistic load conditions

**Tools:** k6 (https://k6.io/docs/) — lightweight, scalable, no GUI overhead

**Prerequisites:**
```bash
# Install k6
# macOS: brew install k6
# Linux: sudo apt-get install k6
# Windows: https://dl.k6.io/msi/k6-latest-amd64.msi
```

---

## Load Test 1: Baseline (10 Users, 40 seconds)

**Objective:** Establish baseline latency at modest concurrent load  
**Duration:** 40 seconds total (10s ramp-up, 20s hold, 10s ramp-down)  
**Target:** Verify p95 latency <6s, error rate <0.5%

**Script:** `load_test_baseline.js`

```javascript
import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Trend, Counter, Rate } from 'k6/metrics';

// Custom metrics
const assessmentDuration = new Trend('assessment_duration');
const pdfDuration = new Trend('pdf_duration');
const errorCount = new Counter('errors');
const errorRate = new Rate('error_rate');

export let options = {
  stages: [
    { duration: '10s', target: 10 },   // Ramp up to 10 users over 10s
    { duration: '20s', target: 10 },   // Hold at 10 users for 20s
    { duration: '10s', target: 0 },    // Ramp down over 10s
  ],
  thresholds: {
    'http_req_duration': ['p(95)<6000'],    // 95th percentile latency <6s
    'error_rate': ['rate<0.005'],            // Error rate <0.5%
    'assessment_duration': ['p(95)<7000'],   // Assessment p95 <7s
  },
  noConnectionReuse: false,
  insecureSkipTLSVerify: false,
};

// Helper: Build realistic assessment request
function buildAssessmentPayload(vuid, iteration) {
  return {
    submission: {
      company_name_raw: `TestCorp-${vuid}-${iteration}`,
      industry_label: 'Financial services',
      prospect_role: 'CIO',
      prospect_name: `User ${vuid}`,
      prospect_email: `user${vuid}@testcorp.com`,
    },
    consent: {
      c1_use_for_scorecard: true,
      c2_data_retention: true,
      consent_timestamp: new Date().toISOString(),
    },
    responses: {
      // 20 question responses (simplified)
      'Q1.1': { option_id: 'A' },
      'Q1.2': { scale_value: 4 },
      'Q2.1': { option_ids: ['X', 'Y'] },
      'Q2.2': { scale_value: 3 },
      'Q3.1': { option_id: 'B' },
      'Q3.2': { scale_value: 4 },
      'Q3.3': { scale_value: 3 },
      'Q3.4': { option_id: 'C' },
      'Q4.1': { option_id: 'A' },
      'Q4.2': { scale_value: 3 },
      'Q5.1': { option_id: 'B' },
      'Q5.2': { scale_value: 4 },
      'Q6.1': { option_ids: ['GDPR', 'SOC2'] },
      'Q6.2': { option_id: 'US' },
      // Additional responses to reach 20 questions
      'Q7.1': { option_id: 'A' },
      'Q8.1': { scale_value: 3 },
      'Q9.1': { option_id: 'B' },
      'Q10.1': { option_id: 'C' },
    }
  };
}

export default function () {
  const baseUrl = 'http://localhost:8080';
  const vuid = `${__VU}`;

  group('Baseline Assessment Flow', function () {
    // 1. Load questions
    let questionsRes = http.get(`${baseUrl}/api/questions`);
    check(questionsRes, {
      'questions loaded': (r) => r.status === 200,
      'questions valid JSON': (r) => {
        try {
          JSON.parse(r.body);
          return true;
        } catch (e) {
          return false;
        }
      },
    });
    sleep(1);

    // 2. Submit assessment
    let assessmentPayload = buildAssessmentPayload(vuid, __ITER);
    let assessmentStart = Date.now();
    
    let assessmentRes = http.post(
      `${baseUrl}/api/assess`,
      JSON.stringify(assessmentPayload),
      {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: '30s',
      }
    );
    
    let assessmentLatency = Date.now() - assessmentStart;
    assessmentDuration.add(assessmentLatency);

    let isAssessmentSuccess = check(assessmentRes, {
      'assessment successful': (r) => r.status === 200,
      'assessment has ID': (r) => {
        try {
          let body = JSON.parse(r.body);
          return body.id && body.id.length === 10;
        } catch (e) {
          return false;
        }
      },
      'assessment latency <10s': (r) => assessmentLatency < 10000,
    });

    if (!isAssessmentSuccess) {
      errorCount.add(1);
      errorRate.add(true);
    } else {
      errorRate.add(false);
    }

    if (assessmentRes.status === 200) {
      let body = JSON.parse(assessmentRes.body);
      let sid = body.id;
      sleep(2);

      // 3. Fetch scorecard details
      let scoreRes = http.get(`${baseUrl}/api/review/${sid}`, {
        timeout: '10s',
      });
      check(scoreRes, {
        'scorecard retrieved': (r) => r.status === 200,
      });
      sleep(1);

      // 4. Generate PDF
      let pdfStart = Date.now();
      let pdfRes = http.get(`${baseUrl}/api/scorecard/${sid}/pdf`, {
        timeout: '10s',
      });
      let pdfLatency = Date.now() - pdfStart;
      pdfDuration.add(pdfLatency);

      check(pdfRes, {
        'PDF generated': (r) => r.status === 200,
        'PDF is PDF': (r) => r.headers['Content-Type'].includes('application/pdf'),
        'PDF latency <5s': (r) => pdfLatency < 5000,
      });
    }

    sleep(3);
  });
}
```

**Run:**
```bash
k6 run load_test_baseline.js --vus 10 --duration 40s
```

**Expected Output:**
```
     data_received..............: 8.5 MB   213 kB/s
     data_sent..................: 4.2 MB   105 kB/s
     http_req_blocked...........: avg=52ms   p(95)=150ms
     http_req_connecting........: avg=8ms    p(95)=22ms
     http_req_duration..........: avg=2850ms p(95)=5900ms ✓
     http_req_failed............: 0.00%
     http_req_receiving.........: avg=150ms  p(95)=300ms
     http_req_sending...........: avg=25ms   p(95)=50ms
     http_req_waiting...........: avg=2650ms p(95)=5800ms
     http_reqs..................: 150     3.75/s
     
     assessment_duration.........: avg=3200ms p(95)=7100ms
     pdf_duration...............: avg=2100ms p(95)=3800ms
     error_rate.................: 0.00%
     errors......................: 0
```

---

## Load Test 2: Ramp-Up (0 → 100 Users)

**Objective:** Identify saturation point and capacity limit  
**Duration:** 10 minutes (add 10 users every minute until 100)  
**Target:** Identify where latency exceeds SLO and error rate increases

**Script:** `load_test_rampup.js`

```javascript
import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Trend, Counter, Rate } from 'k6/metrics';

const assessmentDuration = new Trend('assessment_duration');
const errorRate = new Rate('error_rate');

export let options = {
  stages: [
    { duration: '1m', target: 10 },    // 10 users
    { duration: '1m', target: 20 },    // +10 users
    { duration: '1m', target: 30 },    // +10 users
    { duration: '1m', target: 40 },    // +10 users
    { duration: '1m', target: 50 },    // +10 users
    { duration: '1m', target: 60 },    // +10 users
    { duration: '1m', target: 70 },    // +10 users
    { duration: '1m', target: 80 },    // +10 users
    { duration: '1m', target: 90 },    // +10 users
    { duration: '1m', target: 100 },   // +10 users (peak)
  ],
  thresholds: {
    'http_req_duration': ['p(95)<8000'],  // Loosen to 8s for ramp
    'error_rate': ['rate<0.01'],          // <1% errors acceptable during ramp
  },
};

function buildAssessmentPayload(vuid, iteration) {
  return {
    submission: {
      company_name_raw: `RampTest-${vuid}-${iteration}`,
      industry_label: 'Technology',
      prospect_role: ['CEO', 'CIO', 'CFO', 'CTO'][Math.floor(Math.random() * 4)],
      prospect_name: `User ${vuid}`,
      prospect_email: `user${vuid}@ramptest.com`,
    },
    consent: {
      c1_use_for_scorecard: true,
    },
    responses: {
      'Q1.1': { option_id: 'A' },
      'Q1.2': { scale_value: 3 },
      'Q2.1': { option_ids: ['X', 'Y'] },
      'Q3.1': { option_id: 'B' },
      'Q3.2': { scale_value: 4 },
      'Q4.1': { option_id: 'A' },
      'Q5.1': { option_id: 'B' },
      'Q6.1': { option_ids: ['GDPR'] },
      'Q6.2': { option_id: 'US' },
      'Q7.1': { option_id: 'A' },
    }
  };
}

export default function () {
  const baseUrl = 'http://localhost:8080';
  const vuid = `${__VU}`;

  group(`User ${vuid} Assessment`, function () {
    let start = Date.now();
    
    let res = http.post(
      `${baseUrl}/api/assess`,
      JSON.stringify(buildAssessmentPayload(vuid, __ITER)),
      { headers: { 'Content-Type': 'application/json' }, timeout: '30s' }
    );
    
    let latency = Date.now() - start;
    assessmentDuration.add(latency);

    let isSuccess = res.status === 200;
    errorRate.add(!isSuccess);

    check(res, {
      'assessment successful': (r) => r.status === 200,
      'latency <8s': (r) => latency < 8000,
    });

    if (isSuccess) {
      try {
        let body = JSON.parse(res.body);
        let sid = body.id;
        sleep(5);
      } catch (e) {
        // Silent fail
      }
    }

    sleep(10);
  });
}
```

**Run:**
```bash
k6 run load_test_rampup.js --vus 100 --duration 10m
```

**Analysis:**
- Watch for point where p95 latency exceeds 8s
- Note CPU/memory utilization in ECS metrics
- Identify if task restarts occur (health check failures)

**Expected Saturation Point:**
```
At 60-70 concurrent users:
- p95 latency: ~6-8s (still acceptable)
- CPU utilization: 85-90%
- Error rate: <0.5%

At 80-100 concurrent users:
- p95 latency: >10s (SLO breach)
- CPU utilization: >95% (saturation)
- Error rate: 2-5% (task under stress)
- Some timeouts likely
```

---

## Load Test 3: Spike Test (20 → 60 users, 30s spike)

**Objective:** Verify ability to handle sudden traffic spikes  
**Duration:** 5 minutes  
**Pattern:** Normal load (20 users) → spike (60 users for 30s) → recovery

**Script:** `load_test_spike.js`

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend, Counter } from 'k6/metrics';

const latency = new Trend('latency');
const failures = new Counter('failures');

export let options = {
  stages: [
    { duration: '1m', target: 20 },     // Normal load
    { duration: '30s', target: 60 },    // Spike to 60 users in 30s
    { duration: '30s', target: 60 },    // Hold spike for 30s
    { duration: '30s', target: 20 },    // Recover back to 20
    { duration: '1m', target: 20 },     // Verify stability
  ],
  thresholds: {
    'http_req_duration': ['p(95)<10000'],  // Spike tolerance: p95 <10s
    'failures': ['count<10'],              // <10 total failures acceptable
  },
};

export default function () {
  const baseUrl = 'http://localhost:8080';

  let start = Date.now();
  let res = http.post(
    `${baseUrl}/api/assess`,
    JSON.stringify({
      submission: {
        company_name_raw: `Spike-${__VU}-${Date.now()}`,
        industry_label: 'Retail',
        prospect_role: 'VP Engineering',
        prospect_name: `User ${__VU}`,
        prospect_email: `user${__VU}@spike.com`,
      },
      consent: { c1_use_for_scorecard: true },
      responses: {
        'Q1.1': { option_id: 'A' },
        'Q2.1': { option_ids: ['X'] },
        'Q3.1': { option_id: 'B' },
      }
    }),
    { headers: { 'Content-Type': 'application/json' }, timeout: '30s' }
  );

  let dur = Date.now() - start;
  latency.add(dur);

  if (res.status !== 200) {
    failures.add(1);
  }

  check(res, {
    'status is 200': (r) => r.status === 200,
  });

  sleep(8);
}
```

**Run:**
```bash
k6 run load_test_spike.js
```

**Expected Results:**
```
During spike (60 users):
- Response times increase 50-100% temporarily
- p95 latency: 6-10s (acceptable degradation)
- Error rate: 0-1% (task handles gracefully)
- All requests eventually complete

After spike (back to 20 users):
- Latency returns to baseline within 10s
- No memory leaks (memory reclaimed)
- No error persistence
```

---

## Load Test 4: Sustained Load (50 Users × 1 Hour)

**Objective:** Verify stability over extended period, identify memory leaks  
**Duration:** 60 minutes  
**Pattern:** Constant 50 users for full duration

**Script:** `load_test_sustained.js`

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend, Gauge } from 'k6/metrics';

const latency = new Trend('latency');
const successRate = new Gauge('success_rate');

export let options = {
  stages: [
    { duration: '5m', target: 50 },     // Ramp up to 50
    { duration: '50m', target: 50 },    // Hold at 50
    { duration: '5m', target: 0 },      // Ramp down
  ],
  thresholds: {
    'http_req_duration': ['p(95)<7000'],
    'success_rate': ['value>0.99'],     // >99% success
  },
  // Disable limit behavior
  setupTimeout: '30s',
  teardownTimeout: '30s',
};

let successCount = 0;
let totalCount = 0;

export default function () {
  const baseUrl = 'http://localhost:8080';
  totalCount++;

  let start = Date.now();
  let res = http.post(
    `${baseUrl}/api/assess`,
    JSON.stringify({
      submission: {
        company_name_raw: `Sustained-${__VU}-${__ITER}`,
        industry_label: 'Healthcare',
        prospect_role: 'Chief Data Officer',
        prospect_name: `User ${__VU}`,
        prospect_email: `user${__VU}@sustained.com`,
      },
      consent: { c1_use_for_scorecard: true },
      responses: {
        'Q1.1': { option_id: 'A' },
        'Q2.1': { option_ids: ['X'] },
        'Q3.1': { option_id: 'B' },
      }
    }),
    { headers: { 'Content-Type': 'application/json' }, timeout: '30s' }
  );

  if (res.status === 200) {
    successCount++;
  }

  let dur = Date.now() - start;
  latency.add(dur);
  successRate.add((successCount / totalCount) * 100);

  check(res, {
    'status 200': (r) => r.status === 200,
  });

  sleep(10);
}
```

**Run:**
```bash
k6 run load_test_sustained.js --duration 60m
```

**Metrics to Monitor (in parallel):**
```bash
# Terminal 1: k6 load test
k6 run load_test_sustained.js

# Terminal 2: Monitor ECS task memory/CPU
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name MemoryUtilization \
  --dimensions Name=ServiceName,Value=ai-readiness-diagnostic \
  --start-time 2026-07-10T14:00:00Z \
  --end-time 2026-07-10T15:00:00Z \
  --period 60 \
  --statistics Average,Maximum
```

**Expected Results:**
```
After 60 minutes:
- p50 latency: Stable (no drift)
- p95 latency: Stable (no growth)
- Memory usage: Flat line (no memory leak)
- Error rate: <0.5% (consistent)
- Availability: >99.5%
```

---

## Load Test 5: Stress Test (Push to Failure)

**Objective:** Identify hard failure point  
**Duration:** Until task fails or becomes completely unresponsive

**Script:** `load_test_stress.js`

```javascript
import http from 'k6/http';
import { check } from 'k6';
import { Counter } from 'k6/metrics';

const failures = new Counter('failures');

export let options = {
  stages: [
    { duration: '2m', target: 50 },
    { duration: '2m', target: 100 },
    { duration: '2m', target: 150 },
    { duration: '2m', target: 200 },
    { duration: '2m', target: 300 },
  ],
  thresholds: {
    'http_req_duration': ['p(95)<20000'], // Very loose for stress test
  },
};

export default function () {
  const baseUrl = 'http://localhost:8080';

  let res = http.post(
    `${baseUrl}/api/assess`,
    JSON.stringify({
      submission: {
        company_name_raw: `Stress-${__VU}-${Date.now()}`,
        industry_label: 'Manufacturing',
        prospect_role: 'VP AI',
        prospect_name: `User ${__VU}`,
        prospect_email: `user${__VU}@stress.com`,
      },
      consent: { c1_use_for_scorecard: true },
      responses: {
        'Q1.1': { option_id: 'A' },
      }
    }),
    { headers: { 'Content-Type': 'application/json' }, timeout: '30s' }
  );

  if (res.status !== 200) {
    failures.add(1);
  }

  check(res, {
    'status 200': (r) => r.status === 200,
  });
}
```

**Run:**
```bash
k6 run load_test_stress.js
```

**Observe:**
```
- Point where p95 latency >20s (cascading failures)
- Point where task restarts (health check failures)
- Error rate spike point
- Last successful user count before cascade
- Memory/CPU at failure point
```

---

## Load Test 6: PDF Concurrent Generation

**Objective:** Verify PDF endpoint can handle concurrent requests  
**Stress:** Generate PDFs concurrently

**Script:** `load_test_pdf.js`

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend } from 'k6/metrics';

const pdfLatency = new Trend('pdf_latency');

export let options = {
  stages: [
    { duration: '5m', target: 10 },    // Create 10 scorecard records
    { duration: '5m', target: 10 },    // Generate PDFs concurrently
  ],
};

export default function () {
  const baseUrl = 'http://localhost:8080';
  const vuid = `${__VU}`;

  // Stage 1: Create assessment (first 5 minutes)
  if (__ENV.STAGE === 'CREATE' || __ITER < 5) {
    let res = http.post(
      `${baseUrl}/api/assess`,
      JSON.stringify({
        submission: { company_name_raw: `PDF-${vuid}-${__ITER}`, industry_label: 'Tech' },
        consent: { c1_use_for_scorecard: true },
        responses: { 'Q1.1': { option_id: 'A' } }
      }),
      { headers: { 'Content-Type': 'application/json' } }
    );

    if (res.status === 200) {
      let body = JSON.parse(res.body);
      // Store SID for later PDF generation
      __ENV[`SID_${vuid}`] = body.id;
    }
  } else {
    // Stage 2: Generate PDFs concurrently
    let sid = __ENV[`SID_${vuid}`];
    if (sid) {
      let start = Date.now();
      let res = http.get(`${baseUrl}/api/scorecard/${sid}/pdf`);
      let dur = Date.now() - start;
      pdfLatency.add(dur);

      check(res, {
        'PDF generated': (r) => r.status === 200,
        'Is PDF': (r) => r.headers['Content-Type'].includes('pdf'),
        'Latency <4s': (r) => dur < 4000,
      });
    }
  }

  sleep(3);
}
```

**Run:**
```bash
k6 run load_test_pdf.js
```

**Expect:**
```
5 concurrent users × 10 scorecards = 10 PDFs generated simultaneously
Expected peak memory: ~600MB
If OOM occurs, will see errors starting at ~10 concurrent PDFs
```

---

## Running All Tests in CI/CD

**GitHub Actions Example:**

```yaml
name: Load Tests

on:
  schedule:
    - cron: '0 2 * * *'  # Run nightly at 2 AM UTC
  workflow_dispatch:

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install k6
        run: sudo apt-get install -y k6
      
      - name: Run Baseline Test
        run: k6 run load_test_baseline.js --vus 10 --duration 40s --out json=baseline-results.json
      
      - name: Run Ramp-Up Test
        run: k6 run load_test_rampup.js --out json=rampup-results.json
      
      - name: Run Spike Test
        run: k6 run load_test_spike.js --out json=spike-results.json
      
      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: load-test-results
          path: '*-results.json'
      
      - name: Alert on Failures
        if: failure()
        run: |
          echo "Load tests failed. Check metrics in CloudWatch."
          # Send Slack notification, etc.
```

---

## Analyzing Results

**Key Metrics to Track:**

1. **Latency Percentiles**
   - p50: Typical response time
   - p95: 95th percentile (SLO baseline)
   - p99: Worst-case (occasional outliers)

2. **Throughput**
   - Requests/second
   - Should scale linearly until saturation

3. **Error Rate**
   - Should remain <1% until saturation point
   - Spikes above 5% indicate problems

4. **Resource Utilization**
   - CPU: Should scale linearly until 95%+
   - Memory: Should be stable (no leaks)
   - Network: Monitor bandwidth usage

5. **Concurrent Capacity**
   - Identify point where latency exceeds SLO
   - Note user count at that point

---

## Baseline Comparison (Before/After Optimizations)

**After implementing P0 fixes (timeout, PDF streaming, pagination):**

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Peak concurrent (p95 <6s) | 5-7 | 8-10 | +40% |
| PDF memory per request | 60MB | 5MB | -92% |
| Review queue latency at 1000 records | 800ms | 150ms | -81% |
| Cost per assessment | $0.95 | $0.90 | -5% |
| p95 latency (typical) | 6.0s | 5.5s | -8% |

**After implementing P1 optimizations (caching, autoscaling, pre-transpile):**

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Peak concurrent capacity | 5-7 | 15-20 | 3x |
| Frontend FCP | 1.2s | 0.9s | -25% |
| Cost per assessment | $0.95 | $0.80 | -15% |
| LLM cache hit rate | 0% | 12% | 12% |
| P95 latency | 6.0s | 5.2s | -13% |

---

## Continuous Monitoring

**Set up CloudWatch alarms for:**

```
Assessment latency p95 > 8s → PagerDuty alert
Error rate > 1% → Slack notification
Memory utilization > 80% → Auto-scale
Review queue latency > 500ms → Investigate
```

**Weekly Dashboard Review:**
- Compare week-over-week latency trends
- Monitor cost per assessment
- Track error rate trends
- Identify new bottlenecks early

---

**Last Updated:** July 10, 2026  
**Next Review:** After P0/P1 implementation (2 weeks)
