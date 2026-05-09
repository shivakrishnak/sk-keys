---
id: SYD-015
title: SLA SLO SLI
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★☆
depends_on:
used_by: SYD-016, SYD-017
related: SYD-016, SYD-017
tags:
  - reliability
  - intermediate
  - architecture
  - observability
status: complete
version: 1
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 15
permalink: /syd/sla-slo-sli/
---

# SYD-015 - SLA SLO SLI

⚡ TL;DR - Three related but distinct commitments: SLA is a business contract promising uptime, SLO is the internal target we aim for (usually higher than SLA), and SLI is the measured actual performance-together they define expectations and guide reliability decisions.

| #690            | Category: System Design                        | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------- | :-------------- |
| **Depends on:** | Monitoring, High Availability, Observability   |                 |
| **Used by:**    | Production Operations, SRE, Service Management |                 |
| **Related:**    | Error Budget, MTTR / MTBF, Observability       |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your API is "up" sometimes. Customers say it's broken. You say it's fine. No agreed definition of "working." Customer escalates. Both parties unhappy. No one knows: how fast should responses be? How often is downtime acceptable? What happens if you miss targets-are there consequences?

**THE BREAKING POINT:**
Without clear commitments and measurements, service reliability becomes a finger-pointing exercise. No accountability, no way to plan capacity, no basis for decisions.

**THE INVENTION MOMENT:**
"This is why SLA/SLO/SLI were created-define what 'reliable' means, commit to targets, and measure reality."

**EVOLUTION:**
SLA as a legal contract predates software engineering - telecommunications companies used SLAs in the 1970s to define service quality commitments. The Google SRE book (2016) transformed SLAs from legal boilerplate into engineering tools: SLOs gave teams internal targets to aim for, SLIs gave them metrics to measure against, and error budgets gave them permission to ship. The framework spread beyond Google to become the standard reliability discipline across the industry. Modern implementations extend the concept to synthetic monitoring (measuring SLIs from the user's perspective), multi-tier SLAs, and SLOs as code (SLO configuration in version control).

---

### 📘 Textbook Definition

- **SLA (Service Level Agreement):** A contractual commitment between a service provider and customer, specifying minimum service availability/performance (e.g., "99.9% uptime") and consequences if missed (credits, penalties, termination).
- **SLO (Service Level Objective):** An internal target set by the service team, usually more stringent than the SLA, providing a buffer. If you commit to 99.9% SLA, you might aim for 99.99% SLO internally.
- **SLI (Service Level Indicator):** The actual measured metric that indicates service performance (e.g., percentage of successful requests, P99 latency). SLI is compared against SLO to determine if targets are being met.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
SLA = contract promise. SLO = our internal goal (harder than SLA). SLI = what we actually measure.

**One analogy:**

> A pizza restaurant guarantees delivery in 30 minutes (SLA-promise to customer). Internally, staff targets 20 minutes (SLO-better than promise, gives buffer). Driver tracks actual time (SLI-what's measured). If actual > 30 min, customer gets refund. If consistently close to 30 min, staff know they need to optimize.

**One insight:**
SLO > SLA > SLI over time. If SLI frequently exceeds SLO, you're burning error budget. If consistently under SLO, you might be over-provisioning (wasting money).

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. A service can't be 100% reliable (bugs exist, hardware fails, network breaks)
2. Perfect reliability is infinitely expensive
3. Customers have acceptable failure rates; we should define and measure them
4. There's a business/reliability tradeoff

**DERIVED DESIGN:**
Start with customer needs (SLA): "99% of requests must succeed, with <500ms latency." This is the contract. Internally, aim higher (SLO): "99.9% success, <100ms latency"-buffer to handle occasional issues without breaching SLA. Measure actual performance (SLI): "During Jan, 99.97% success, P99 latency = 120ms." Compare SLI to SLO. If tracking well, invest elsewhere. If approaching SLA, trigger incident response.

**THE TRADE-OFFS:**
**Gain:** Clarity. Alignment between business and engineering. Data-driven decisions on reliability investment.

**Cost:** SLAs may limit flexibility (can't experiment/deploy during incidents without risking SLA breach). Too-tight SLOs burn resources. Too-loose SLOs mask problems.

---

### 🧪 Thought Experiment

**SETUP:**
A payment API. Customer expects to pay bills without delays. Business promises 99.5% uptime (SLA). Engineering team targets 99.95% (SLO). A month has 2,592,000 seconds (~30 days).

**SLA:** 99.5% = 0.5% downtime allowed = 0.005 × 2,592,000 = 12,960 seconds = ~3.6 hours/month unplanned downtime allowed.

**SLO:** 99.95% = 0.05% downtime = 0.0005 × 2,592,000 = 1,296 seconds = ~21 minutes/month.

**SLI (Actual):**

- Week 1: 99.97% success (good, well above SLO)
- Week 2: 99.94% success (slightly below SLO but well above SLA)
- Week 3: 99.92% success (approaching SLA boundary)
- Week 4: 99.91% success (still above SLA, but trend is bad)

**Month overall:** 99.93% success → above SLA (customer not due refund) but below SLO (team missed internal target, should investigate).

**THE INSIGHT:**
SLA is the floor (contract boundary). SLO is the target (operational boundary). SLI is reality. The delta between SLO and SLA is error budget-how much you can fail before customers complain.

---

### 🧠 Mental Model / Analogy

> An airline promises 95% on-time arrivals (SLA-legal commitment). Internally, they target 98% (SLO-buffer for weather, mechanical issues). A dispatcher tracks actual arrival rates (SLI). If SLI drops below 95%, customers file complaints, lawsuits. If SLI is consistently 96–97%, airline is meeting SLA but might relax operations. If SLI is 99%+, airline might reduce crew/flights (cost saving, still profitable).

- "On-time arrival" → uptime / success rate
- "Promise to customers (95%)" → SLA
- "Internal target (98%)" → SLO
- "Actual rate tracked" → SLI
- "Buffer between promise and target" → error budget
- "Consequences of missing SLA" → refunds, reputation damage

**Where this analogy breaks down:** Software failures are more binary (up/down) than airline lateness (degrees of late). SLI can be multidimensional (latency AND availability), not just one metric.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
The service promises customers it will work 99.9% of the time (SLA). Engineers aim for 99.95% to have buffer (SLO). Every month, they measure how often it actually worked (SLI). If it works less than 99.9%, customers get refunds.

**Level 2 - How to use it (junior developer):**
Your service has SLA = 99% uptime. SLO = 99.5%. Every day, check the SLI dashboard: what's the actual uptime? If SLI < 99% for the month, alert. If SLI consistently < 99.5%, investigate (why are we missing our target?). When deploying, check if it might breach SLA (don't deploy risky changes if you're already close to SLA limit).

**Level 3 - How it works (mid-level engineer):**
Define SLI metrics (e.g., successful_requests / total_requests, P99 latency < 200ms). Emit these metrics continuously (instrumentation). Aggregate into SLI calculation (daily, weekly, monthly). Set SLO thresholds (e.g., success rate > 99.5% for 30 days). Compare: if SLI >= SLO, good. If SLI < SLO but >= SLA, needs investigation. If SLI < SLA, incident (breach, notify customers, trigger response). Calculate error budget: SLA - actual_SLI. Budget is spent-deploy less frequently until it recovers.

**Level 4 - Why it was designed this way (senior/staff):**
SLA/SLO/SLI emerged from SRE (Google). Before SRE, reliability was vague ("make it work"). After, it's quantified ("99.99% success rate, measured hourly"). The hierarchy (SLA > SLO > SLI) makes sense: business defines maximum acceptable failure (SLA), ops targets higher (SLO), and measures reality (SLI). Error budgets from SLA are then spent on deployments, experiments, and maintenance. This aligns engineering incentives with business goals: stay above SLA, aim for SLO, but don't over-invest beyond SLA.

---

### ⚙️ How It Works (Mechanism)

SLA/SLO/SLI operation:

```
DEFINE (Start of Service):
  SLA = 99.5% uptime (contractual promise)
  SLO = 99.9% uptime (internal target, buffer)

  SLI metrics to track:
    - Successful requests / total requests
    - P99 latency < 200ms
    - Error rate < 0.5%

  Error Budget = SLA - SLI = 0.5% = 12,960 seconds/month

MEASURE (Continuous):
  Every request:
    - Is it successful? (yes/no)
    - What's latency? (ms)
    - Aggregate into SLI metrics

  Hourly SLI calculation:
    success_rate = successful_reqs / total_reqs
    p99_latency = percentile(latencies, 99)
    Report to dashboard

  Monthly SLI aggregation:
    monthly_success = avg of hourly SLI values
    Compare to SLO: 99.9%?
      ├─ YES: "On target"
      └─ NO: "Below target, investigate"

DECIDE (Ongoing):
  If SLI >= SLO for consecutive periods:
    "Reliability good, safe to deploy"
    Go ahead with risky changes

  If SLI < SLO but >= SLA:
    "Missing our target but within contract"
    Investigate, but not urgent

  If SLI < SLA:
    "BREACH! Customer refunds trigger"
    Immediate incident response
    "Don't deploy until SLI recovers above SLA"

ERROR BUDGET CONSUMPTION:
  Each second below SLI, error budget spent
  Once budget exhausted, stop risky deployments
  Wait for quiet period to recover budget
```

**In Happy Path:**
SLI consistently > SLO. Team is well within error budget. Deploy confidently. Optimize features.

**When Something Goes Wrong:**
Critical bug deployed. Requests start failing. SLI drops to 97%. Below SLA (99.5% contract). ALERT. Customers calling. Refunds issued. Rollback deployed. SLI recovers to 99.8%. Investigation done. Post-mortem. Deploy testing improved.

---

### 🔄 The Complete Picture - End-to-End Flow

```
Service Request Arrives
    ↓
Handled (success or failure tracked)
    ↓
METRICS EMISSION (YOU ARE HERE)
Request counted toward SLI
    ↓
Hourly Aggregation
    Aggregate 3600 seconds of requests
    ↓
    Calculate: success_rate, latency_p99
    → SLI_hourly

Daily Aggregation
    Aggregate 24 hourly SLI values
    → SLI_daily

Monthly Aggregation
    Aggregate 30 daily SLI values
    → SLI_monthly

Decision Point:
    SLI_monthly >= SLO? (99.9%)
    ├─ YES: "On track"
    └─ NO: "Miss target, why?"

    SLI_monthly >= SLA? (99.5%)
    ├─ YES: "Acceptable to customers"
    └─ NO: "BREACH-refunds owed"
```

**WHAT CHANGES AT SCALE:**
At 10 req/s, SLI calculation is simple. At 1 million req/s, you need distributed metrics collection (push metrics to monitoring backend). At scale, even 0.1% error rate = 1000 failed requests/second. SLI becomes granular (per-endpoint, per-region, per-customer-tier).

---

### 💻 Code Example

SLA/SLO/SLI are operational, but implementation:

**Example 1 - Prometheus Metrics for SLI:**

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
requests_total = Counter(
    'api_requests_total',
    'Total API requests',
    ['endpoint', 'method', 'status']
)

requests_success = Counter(
    'api_requests_success',
    'Successful API requests',
    ['endpoint']
)

request_latency = Histogram(
    'api_request_latency_seconds',
    'API request latency',
    ['endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0]
)

# In request handler:
@app.route('/api/users/<user_id>')
def get_user(user_id):
    start = time.time()
    try:
        user = db.query(f"SELECT * FROM users WHERE id = {user_id}")
        requests_total.labels(
            endpoint='/users',
            method='GET',
            status='200'
        ).inc()
        requests_success.labels(endpoint='/users').inc()
    except Exception as e:
        requests_total.labels(
            endpoint='/users',
            method='GET',
            status='500'
        ).inc()
    finally:
        latency = time.time() - start
        request_latency.labels(endpoint='/users').observe(latency)
```

**Example 2 - Prometheus Query for SLI:**

```promql
# Calculate success rate (SLI)
success_rate = rate(api_requests_success[5m]) / rate(api_requests_total[5m])

# Calculate P99 latency (SLI)
p99_latency = histogram_quantile(0.99, api_request_latency_seconds_bucket)

# Alert if SLI < SLO (99.5%)
alert: SloBreachWarning
  if: success_rate < 0.995
  for: 5m
  annotations:
    summary: "SLI below SLO ({{ $value | humanizePercentage }})"

# Alert if SLI < SLA (99%)
alert: SlaViolation
  if: success_rate < 0.99
  for: 1m
  annotations:
    summary: "CRITICAL: SLA Breach! ({{ $value | humanizePercentage }})"
```

**Example 3 - SLO Definition Document:**

```yaml
# Service: Payment API
sla:
  availability: "99.5%"
  latency_p99: "500ms"
  error_budget: "0.5%"

slo:
  availability: "99.9%"
  latency_p99: "200ms"
  error_budget: "0.1%"

sli:
  metrics:
    - name: "success_rate"
      calculation: "successful_requests / total_requests"
      target: ">= 99.5% (SLA)"

    - name: "latency_p99"
      calculation: "percentile(request_latencies, 99)"
      target: "<= 500ms (SLA)"

  evaluation_window: "30 days (calendar month)"

error_budget:
  monthly_budget: "0.5% = ~21,600 seconds"
  burn_rate:
    - "< 0.5%/day": "OK, deploy anything"
    - "0.5–1%/day": "Caution, no experimental deploys"
    - "> 1%/day": "Freeze, rollback, fix critical issues only"
```

---

### ⚖️ Comparison Table

| Term    | Scope                 | Audience              | Consequence                           | Example                                       |
| ------- | --------------------- | --------------------- | ------------------------------------- | --------------------------------------------- |
| **SLA** | External, contractual | Customers             | Refunds, penalties, termination       | "99% uptime, $100/hour credit if breached"    |
| **SLO** | Internal, operational | Engineering team      | Performance review, budget allocation | "99.5% uptime, don't deploy if trending down" |
| **SLI** | Measured reality      | Operations, analytics | Trending data, alerting, debugging    | "99.73% uptime this month"                    |

**How to choose:** Start with customer needs (SLA). Set SLO at 1–2 standard deviations better (buffer). Measure SLI continuously. Adjust SLO if consistently too loose or too tight.

---

### ⚠️ Common Misconceptions

| Misconception                    | Reality                                                                                             |
| -------------------------------- | --------------------------------------------------------------------------------------------------- |
| "SLA and SLO are the same thing" | No. SLA is contractual; SLO is internal target. SLA is the floor; SLO is the goal (higher).         |
| "100% SLA is possible"           | No. Bugs, hardware failures, network partitions exist. 100% is infinitely expensive and impossible. |
| "SLI is the same as SLA"         | No. SLI is measured actual performance; SLA is the contract. SLI should be compared to SLO/SLA.     |
| "SLA is just uptime percentage"  | Incomplete. SLA includes latency, error rates, availability, and consequences for missing targets.  |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: SLA Breach (Unplanned)**

**Symptom:**
Database crashes. Service becomes unavailable. SLI drops to 98%. Below SLA (99.5%). Breach. Customers call. "Refunds!"

**Root Cause:**
Insufficient redundancy. Database is single point of failure. No failover. Outage exceeds SLA budget.

**Diagnostic Command:**

```bash
# Check SLI trend
curl https://monitoring/api/sli/daily | tail -30

# Check when breach occurred
curl https://monitoring/api/alerts | grep SLA | head -5

# Identify root cause
aws cloudtrail lookup-events | grep database | tail -10
```

**Fix:**
Bad approach: Hope it doesn't happen again.
Good approach: (1) Add database replicas with automatic failover. (2) Increase SLO testing (chaos engineering). (3) Implement circuit breakers to avoid cascading failures. (4) Create error budget policy: if breached, freeze deploys.

**Prevention:**
Design for SLO/SLA targets from start. Include redundancy, failover, and monitoring. Test failure paths (chaos engineering). Maintain visibility into SLI trends.

---

**Failure Mode 2: Burning Error Budget Too Fast**

**Symptom:**
Month started with 0.5% error budget (for 99.5% SLA). Week 1: burned 0.2%. Week 2: burned 0.15%. Trend: will breach SLA by week 3. Team must freeze deployments.

**Root Cause:**
Multiple small issues accumulating. Bad deployment (10% error spike for 1 hour). Network blip (latency spiked 10x). Database slowness (cascaded). Error budget consumed faster than expected.

**Diagnostic Command:**

```bash
# Check burn rate
burn_rate = (SLA - SLI) / remaining_days

# If burn_rate > safe_rate, alert
if burn_rate > (error_budget / 30 days):
    echo "ALERT: Burning error budget faster than linear"
```

**Fix:**
Bad approach: Ignore and hope it levels off.
Good approach: (1) Implement SLO alerts-warn before SLA breach. (2) Freeze experimental deploys. (3) Increase monitoring-find root cause of errors. (4) Prioritize reliability fixes (not features) until budget recovers.

**Prevention:**
Track burn rate continuously. Set burn rate thresholds (e.g., if > 1%/day, escalate). Establish policy: if burn rate unsustainable, pause feature work, focus on reliability.

---

**Failure Mode 3: SLO Too Tight, Team Overwhelmed**

**Symptom:**
SLA = 99% but SLO = 99.99%. Team spends all time firefighting minor latency variations. Can't ship features. Low morale. Customers don't notice the difference between SLA and SLO.

**Root Cause:**
SLO set too ambitious. Gap between SLO and SLA is too small (almost no error budget buffer).

**Diagnostic Command:**

```bash
# Check SLI vs SLO gap
sli = (successful_requests_30days / total_requests_30days)
slo = 0.9999
gap = slo - sli

if gap < 0.0005:
    echo "SLO too tight"
```

**Fix:**
Bad approach: Accept burnout and accept low velocity.
Good approach: (1) Relax SLO closer to SLA (but keep buffer). (2) Focus team on meeting SLA, not SLO. (3) Use SLO-miss-triggered incidents, not SLA-miss-triggered.

**Prevention:**
Set SLO reasonable. Industry: SLA usually 99–99.5%, SLO 99.5–99.99%. Don't exceed 99.99% unless business critically requires it. Review SLO quarterly-if consistently exceeded, tighten SLA (increase value). If consistently missed, loosen SLO (reduce team burden).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-014 - Auto Scaling]] - infrastructure decisions affect achievable SLO

**Builds On This (learn these next):**
- [[SYD-016 - Error Budget]] - derived directly from SLO
- [[SYD-017 - MTTR MTBF]] - complementary operational metrics that affect SLA achievement

**Alternatives / Comparisons:**
- [[SYD-016 - Error Budget]] - error budget is the operational tool derived from SLA/SLO
- [[SYD-017 - MTTR MTBF]] - different but complementary reliability metrics

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS   │ SLA = contract; SLO = target;       │
│              │ SLI = measured; together they       │
│              │ define reliability expectations     │
├──────────────┼────────────────────────────────────────┤
│ PROBLEM IT   │ Without clear targets, no            │
│ SOLVES       │ accountability; can't make           │
│              │ data-driven reliability decisions   │
├──────────────┼────────────────────────────────────────┤
│ KEY INSIGHT  │ SLO > SLA > SLI; difference is       │
│              │ error budget spent on deployments   │
│              │ and experiments                     │
├──────────────┼────────────────────────────────────────┤
│ USE WHEN     │ Any production system; customer-     │
│              │ facing; when refunds/penalties      │
│              │ for downtime                        │
├──────────────┼────────────────────────────────────────┤
│ AVOID WHEN   │ Internal tools; early-stage         │
│              │ products (undefined); prototypes    │
├──────────────┼────────────────────────────────────────┤
│ TRADE-OFF    │ [Alignment, data-driven] vs         │
│              │ [constraints on deployment,         │
│              │ tuning effort]                      │
├──────────────┼────────────────────────────────────────┤
│ ONE-LINER    │ "Promise, aim higher, measure       │
│              │ reality."                           │
├──────────────┼────────────────────────────────────────┤
│ NEXT EXPLORE │ Error Budget → SRE → MTTR/MTBF      │
└──────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Making a commitment explicit forces alignment. An SLA is a commitment to a customer. An SLO is a commitment within the team. The principle - define the target explicitly before measuring - applies everywhere: capacity planning (define threshold before monitoring), performance tuning (define acceptable latency before optimising), and hiring (define success criteria before interviewing). Ambiguous targets produce ambiguous outcomes.

**Where else this pattern appears:**
- **Capacity planning:** A capacity threshold (CPU < 70%) is an internal SLO for infrastructure - you monitor against it and provision to maintain it.
- **Test coverage targets:** A team's 80% coverage target is an SLO for code quality - it creates shared accountability without being a customer-facing commitment.
- **Delivery SLAs:** A product team's commitment to deliver a feature by Q3 is an SLA - with the same structure of measurement, target, and consequence.

---

### 💡 The Surprising Truth

Google's original SRE insight - that 100% availability is the wrong target - was counterintuitive when published. The argument: if your SLA is 99.9% uptime, the remaining 0.1% (43.8 minutes per month) is your error budget - time you are allowed to fail. Using that budget on planned maintenance, risky deploys, or experiments is not a violation; it is rational allocation of allowed failure. The real problem is not the 0.1% downtime - it is teams that design for 100% uptime and are then paralysed when something breaks because they have no framework for accepting planned failure.

---

### 🧠 Think About This Before We Continue

**Q1.** Your service has SLA = 99.5% (monthly), SLO = 99.9%. Monday, you deploy a risky feature that could improve performance 10%. It has a 1% chance of causing 1-hour outage. Do you deploy? How does error budget inform the decision?

*Hint:* Think about what deploying a risky feature means for error budget consumption in the worst case (1% chance of 1-hour outage). Calculate the expected error budget burn and compare to remaining budget - then explore whether expected value calculation captures the risk correctly or whether tail risk matters more.

**Q2.** Your SLI is 99.92% this month - well above SLO (99.9%) and SLA (99.5%). But your P99 latency is 450ms, approaching your SLA limit of 500ms. Should you treat this as all good because uptime is fine, or as a warning sign?

*Hint:* Think about whether your SLA contract covers uptime only or also latency - is the service responding but slowly a breach? Explore whether P99 latency approaching the SLA limit is a leading indicator that your actual SLA metric will be breached in the future.

**Q3 (Design Trade-off):** You're designing SLOs for a new microservice that depends on a third-party payment API with SLA = 99.9%. Your service's customer-facing SLA is 99.95%. Is this achievable, and what architectural changes does it force?

*Hint:* Think about what achievable means when your component's availability ceiling is your dependency's SLA. Explore whether circuit breakers, fallback payment methods, or async payment processing can decouple your availability from the payment API's availability.
