---
id: MSV-030
title: SLA and SLO in Microservices
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★☆
depends_on: MSV-008, MSV-009, MSV-002
used_by: MSV-044, MSV-066
related: MSV-008, MSV-009, MSV-044, MSV-065, MSV-066
tags:
  - microservices
  - reliability
  - intermediate
  - observability
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Mastery"
nav_order: 30
permalink: /technical-mastery/microservices/sla-and-slo-in-microservices/
---

⚡ TL;DR - SLA (Service Level Agreement) is the external
contract with customers defining minimum acceptable service
levels and penalties for breach. SLO (Service Level
Objective) is the internal target that must be exceeded
to maintain the SLA. SLI (Service Level Indicator) is
the metric measured. In microservices: each service
defines SLOs; the product SLA is derived from the weakest
service in the call chain. Error budgets (derived from
SLOs) govern when to deploy vs when to stabilise.

| #030 | Category: Microservices | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Health Check Patterns, Readiness and Liveness Probes, Microservices Architecture | |
| **Used by:** | Circuit Breaker, Chaos Engineering | |
| **Related:** | Health Check Patterns, Readiness and Liveness Probes, Circuit Breaker, OpenTelemetry in Microservices, Chaos Engineering | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT SLOs:**
Team deploys a new feature on Friday. On Saturday, latency
spikes. Oncall engineer is alerted: "p99 latency is high".
High vs what baseline? Is this a problem? How urgent?
The alert threshold was set by guessing 6 months ago.
No one can articulate whether the system is meeting
user expectations.

In a microservices system: 12 services, each contributing
latency. When the product is slow, which service is
the bottleneck? Without per-service SLOs and error
budgets, the answer requires manual investigation.

**THE SOLUTION:**
SLOs define explicit reliability targets. Error budgets
(1 - SLO target) quantify how much unreliability is
acceptable. When the error budget is being consumed
too fast: engineering focus shifts to reliability.
When the budget is healthy: new features can be deployed.
SLOs transform reliability from a vague aspiration to
an engineering decision framework.

---

### 📘 Textbook Definition

**Service Level Indicator (SLI):** A quantitative measure
of a service characteristic. Common SLIs: availability
(% of successful requests), latency (% of requests under
X ms), throughput (requests per second), error rate
(% of failed requests). SLIs are measured from the
consumer's perspective, not the server's.

**Service Level Objective (SLO):** A target value for
an SLI over a time window. Example: 99.9% of requests
served under 200ms over a rolling 28-day window.
SLOs are internal commitments; they are stricter than
the SLA to provide a buffer.

**Service Level Agreement (SLA):** An external contract
between service provider and customer. Defines minimum
service levels and consequences of breach (refunds,
credits). SLA < SLO (SLA is what you promise externally;
SLO is what you aim for internally).

**Error Budget:** (1 - SLO) * total requests in the
window. How many failures/slow requests are acceptable
before the SLO is breached. Example: 99.9% SLO over
28 days = 0.1% error budget = 40.3 minutes of total
downtime allowed.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
SLO = what you're trying to achieve; SLA = what you
promise customers; SLI = how you measure; error budget =
how much badness you have left before you've broken your SLO.

**One analogy:**
> Speed camera analogy. SLA: speed limit = 70 mph
> (external rule, penalty if exceeded). SLO: your
> personal target = 65 mph (internal target, buffer).
> SLI: speedometer reading (the actual measurement).
> Error budget: if you're allowed 60 seconds above 65
> mph per trip and you've used 50 seconds, you have 10
> seconds left (slow down or you'll breach your SLO).

**One insight:**
The error budget is the key concept. It converts SLOs
from abstract targets into engineering decisions:
"Our 99.9% SLO gives us 43 minutes of error budget this
month. We've used 30 minutes. We have 13 minutes left.
Should we deploy the risky database migration this Friday?"
The answer becomes quantitative, not political.

---

### 🔩 First Principles Explanation

**SLI TAXONOMY FOR MICROSERVICES:**

```
AVAILABILITY SLI:
  Definition: successful_requests / total_requests
  Successful: HTTP 200-499 (excluding 5xx and timeouts)
  Window: rolling 28 days
  Example SLO: 99.9% availability
  Error budget: 0.1% = 43.8 minutes/month
  Measurement: API Gateway access logs, Prometheus

LATENCY SLI:
  Definition: % of requests < threshold
  Common thresholds: p99 < 200ms, p99.9 < 1000ms
  Window: rolling 28 days
  Example SLO: 99% of requests under 200ms
  Error budget: 1% of requests can be slow
  Measurement: histogram metric with le (less than) buckets
  Prometheus: histogram_quantile(0.99, ...)

ERROR RATE SLI:
  Definition: 1 - (error_requests / total_requests)
  Errors: HTTP 5xx, application-level errors
  Example SLO: error rate < 0.1%
  Measurement: counter metric with status_code label

SATURATION SLI:
  Definition: % of resource capacity used
  Examples: CPU < 70%, memory < 80%, queue depth < 10K
  Leading indicator: saturation predicts future issues
  Measurement: Kubernetes resource metrics
```

**ERROR BUDGET MATH:**

```
SLO: 99.9% availability over 28 days

Total minutes in 28 days:
  28 * 24 * 60 = 40,320 minutes

Allowed downtime (error budget):
  40,320 * 0.001 = 40.32 minutes

Weekly error budget:
  40.32 / 4 = 10.08 minutes/week

If service had 15 minutes of downtime this week:
  Error budget remaining this month:
  40.32 - 15 = 25.32 minutes
  (but 10.08 was the week's budget, so over-budget)
  Remaining weeks have 8.44 minutes total

DECISION: slow down deployments, focus on reliability
```

---

### 🧪 Thought Experiment

**CASCADING SLO IN CALL CHAIN:**

```
User Journey: checkout
  Browser -> API Gateway -> Order Service
                         -> Payment Service
                         -> Inventory Service

Each service SLO: 99.9% availability

Combined availability (independent failures):
  0.999 * 0.999 * 0.999 = 0.997 = 99.7%

User-facing SLA can be at most 99.7%
(product SLA = weakest chain link compounded)

IMPLICATION:
  If the product SLA is 99.9%, each service must be
  much higher (e.g., 99.97% per service for 3 services
  to achieve 99.91% combined: 0.9997^3 = 0.9991)

EVEN WORSE WITH DEPENDENCIES:
  If each service calls a database AND a cache:
  Order Service: 99.9% * DB 99.9% * Cache 99.95%
               = 99.75% effective availability
```

---

### 🧠 Mental Model / Analogy

> Error budget is like a maintenance window budget.
> Each week you have X hours to spend on changes that
> carry risk (deployments, schema migrations, config
> changes). If you've already had unexpected downtime,
> your budget is reduced. If your budget is exhausted,
> you stop making risky changes until reliability is
> restored. If your budget is healthy, you can move
> fast. The error budget makes reliability a shared
> engineering responsibility, not just an ops problem.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
SLO is the target: "our service should be available
99.9% of the time". SLI is the measurement: "we
measured 99.85% last month". SLA is the customer
contract: "we guarantee 99% availability or you get
credits". Error budget: "we can afford 43 minutes of
downtime this month before we miss our SLO".

**Level 2 - How to use it (junior developer):**
In a Spring Boot microservice: instrument with Micrometer.
`Counter` for requests and errors. `Timer` for latency.
Expose `/actuator/prometheus`. Configure Prometheus to
scrape. Build a Grafana dashboard with SLO target lines.
Set up alerts when error budget burn rate is high.

**Level 3 - How it works (mid-level engineer):**
Key Prometheus queries for SLO monitoring:
```
# Availability SLI (last 28 days)
sum(rate(http_requests_total{status!~"5.."}[28d]))
/
sum(rate(http_requests_total[28d]))

# Error budget remaining
1 - (
  1 - sum(rate(http_requests_total{status!~"5.."}[28d]))
      / sum(rate(http_requests_total[28d]))
) / (1 - 0.999)  # SLO = 99.9%
```

**Level 4 - Why it was designed this way (senior/staff):**
SLOs solve the "reliability vs feature velocity" tension.
Without error budgets: reliability is a qualitative
argument ("we should stabilise before releasing more
features"). With error budgets: it's quantitative
("our 28-day error budget is 0% remaining; deploying
this feature risks SLA breach; we should defer
deployment"). Error budget policies define: when to
freeze deployments (budget < 10%), when to do reliability
work (budget exhausted), when to conduct game days
(budget healthy). The error budget converts SRE
principles into engineering team process.

**Level 5 - Mastery (distinguished engineer):**
Multi-window, multi-burn-rate alerting (from Google
SRE Workbook): alert when error budget is being consumed
too fast on multiple time windows simultaneously. A
fast burn on a 1-hour window AND a 6-hour window
indicates an active major incident. A slow burn on
a 3-day window without a fast burn indicates a subtle
degradation. Alert at multiple burn rates to distinguish
incidents from gradual degradation. This avoids both
missed incidents (if only long window) and alert fatigue
(if only short window). The two-window alert rule:
page only when both a fast window (1h) AND a slow window
(6h) are both burning at rates that will exhaust the
28-day budget.

---

### ⚙️ How It Works (Mechanism)

**MICROMETER SLI INSTRUMENTATION:**

```java
@RestController
public class OrderController {

    private final MeterRegistry meterRegistry;
    private final Counter requestCounter;
    private final Counter errorCounter;
    private final Timer latencyTimer;

    public OrderController(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        this.requestCounter = Counter.builder(
            "http_requests_total")
            .description("Total HTTP requests")
            .register(meterRegistry);
        this.errorCounter = Counter.builder(
            "http_errors_total")
            .description("Total HTTP 5xx errors")
            .register(meterRegistry);
        this.latencyTimer = Timer.builder(
            "http_request_duration_seconds")
            .publishPercentiles(0.5, 0.95, 0.99)
            .register(meterRegistry);
    }

    @GetMapping("/orders/{id}")
    public ResponseEntity<OrderDTO> getOrder(
            @PathVariable Long id) {
        requestCounter.increment();
        return latencyTimer.record(() -> {
            try {
                return ResponseEntity.ok(
                    orderService.findById(id));
            } catch (Exception e) {
                errorCounter.increment();
                throw e;
            }
        });
    }
}
// Spring Boot Actuator + Micrometer + Prometheus:
// auto-exports http_server_requests_seconds histogram
// which can be used for SLI queries without custom code
```

---

### 🔄 The Complete Picture - End-to-End Flow

**SLO DEFINITION AND MONITORING SETUP:**

```
1. DEFINE SLOs (team decision):
   - Availability: 99.9% over 28-day rolling window
   - Latency: p99 < 300ms over 28-day window
   - Error rate: < 0.1%

2. MEASURE SLIs (Prometheus + Spring Boot Actuator):
   http_server_requests_seconds_count (total requests)
   http_server_requests_seconds_bucket (latency histogram)
   Status code labels: {status="5xx"}

3. CALCULATE ERROR BUDGET:
   Available minutes = 28 * 24 * 60 = 40,320
   Error budget = 40.32 minutes/month

4. ALERTING (burn rate alerts):
   Fast burn (1h): burn rate > 14x -> page
   (consuming 1h budget in 5 minutes)
   Slow burn (6h): burn rate > 6x -> ticket

5. ERROR BUDGET POLICY:
   Budget > 50%: normal deployment cadence
   Budget 10-50%: caution; review risk of each deploy
   Budget < 10%: feature freeze; reliability work only
   Budget 0%: incident; all hands on reliability

6. MONTHLY REVIEW:
   Was SLO met? Yes: retrospective on reliability wins.
   No: incident review, reliability work prioritised.
   Share SLO dashboards with stakeholders.
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: vanity metrics vs SLI**

```java
// BAD: measuring from server perspective (not user)
// "Server was up" != "user requests succeeded"
if (serverHealth.isUp()) {
    uptimeCounter++;  // server reported as up
    // but requests may still be timing out
    // or returning 503 while health check passes
}

// BAD: measuring 5xx only (misses timeouts)
// timeouts = worst user experience but not 5xx
if (response.status() >= 500) {
    errorCounter++;
}
```

```java
// GOOD: SLI measured from user perspective
// Spring Boot Actuator + Micrometer exports this automatically:
// http_server_requests_seconds_count{status="200",...}
// Availability SLI query (Prometheus):
String availabilitySLI = """
    sum(rate(
        http_server_requests_seconds_count{
            status!~"5..",
            uri!~"/actuator.*"
        }[28d]
    ))
    /
    sum(rate(
        http_server_requests_seconds_count{
            uri!~"/actuator.*"
        }[28d]
    ))
    """;
// Excludes actuator (internal), counts timeouts as errors
// (503 status after K8s timeout)
```

---

### ⚖️ Comparison Table

| Concept | Who it's for | What it is | Example |
|---|---|---|---|
| **SLI** | Engineers | Measured metric | 99.85% of requests succeeded |
| **SLO** | Internal team | Target | 99.9% availability |
| **SLA** | Customers/legal | External contract | 99% availability, refund if breached |
| **Error budget** | Eng + product | Allowed unreliability | 40 minutes downtime/month |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| 99.99% ("four nines") SLO is always better | Higher SLO = smaller error budget = less flexibility to deploy and change. 99.99% gives 4.38 minutes/month of error budget. Any slow deployment or minor incident exhausts it. Many teams that chase high SLOs end up with deployment fear and slow velocity. Set SLOs to match actual user expectations, not vanity targets. |
| SLA == SLO | SLA is the external customer contract (lower target, with penalties). SLO is the internal engineering target (higher target, buffer above SLA). SLA breach = contractual consequence. SLO breach = internal alert and engineering response. Always: SLA < SLO. |
| Error budget means accepting downtime | Error budget acknowledges that 100% reliability is impossible and pretending otherwise is dishonest. The budget is not a target to consume; it's a quantification of acceptable risk. Ideally, you don't consume it; but if you do, you know exactly how much you've consumed. |

---

### 🚨 Failure Modes & Diagnosis

**Error budget consumed by non-user-impacting events**

**Symptom:**
SLO dashboard shows availability dropped to 99.3% (below
99.9% target). Team investigates: no user complaints,
no incidents in the last month. Error budget shows 60%
consumed in one week.

**Root Cause:**
SLI measurement includes health check endpoints
(`/actuator/health`) which returned 503 during a
Kubernetes rolling deploy for 5 minutes (probes failed
before new pods were ready). These are not user-visible
failures but are included in the SLI denominator.

**Diagnostic:**
```bash
# Check what URLs are included in the SLI
promtool query series \
  'http_server_requests_seconds_count'
# Look at uri label values - are /actuator/* included?

# Check time of error spike
promtool query range \
  'sum by (uri, status) (rate(
     http_server_requests_seconds_count[5m]))' \
  --start=2024-01-15T10:00:00Z \
  --end=2024-01-15T11:00:00Z
# Shows: /actuator/health returned 503 at 10:30
```

**Fix:**
1. Exclude health check paths from SLI:
   `uri!~"/actuator.*"` in SLI queries
2. Exclude synthetic monitor requests if any
3. Distinguish user-visible errors from infrastructure
   chatter in SLI definition
4. Review error budget policy: health check failures
   during rolling deploy are expected; exclude them

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Health Check Patterns` - health checks provide
  the raw availability signal for SLIs
- `Readiness and Liveness Probes` - Kubernetes probes
  contribute to availability SLI measurement

**Builds On This:**
- `Circuit Breaker` - circuit breakers protect service
  SLOs by failing fast when a downstream dependency
  is degraded
- `Chaos Engineering` - validates SLO targets by
  intentionally introducing failures

**Observability:**
- `OpenTelemetry in Microservices` - the metrics layer
  that powers SLI measurement

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ HIERARCHY    │ SLA (external) < SLO (internal target)   │
│              │ SLI = the measured metric                │
├──────────────┼──────────────────────────────────────────┤
│ ERROR BUDGET │ 99.9% SLO over 28 days                  │
│              │ = 40 minutes allowed downtime            │
├──────────────┼──────────────────────────────────────────┤
│ DECISION     │ Budget > 50%: deploy freely             │
│              │ Budget < 10%: feature freeze            │
│              │ Budget 0%: all hands on reliability     │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "SLO = internal target; error budget =   │
│              │  allowed unreliability; drives decisions"│
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Circuit Breaker → Chaos Engineering     │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. SLA = external customer contract; SLO = internal
   target (stricter than SLA to provide buffer);
   SLI = measured metric; error budget = allowed failures.
2. 99.9% SLO over 28 days = ~40 minutes of allowed
   downtime. When budget is near exhaustion: freeze
   deployments and focus on reliability.
3. SLIs must be measured from the user's perspective,
   not the server's. Exclude health checks and internal
   paths from availability SLI.

**Interview one-liner:**
"SLI measures service quality (request success rate).
SLO is the internal target (99.9% availability). SLA
is the external contract (99% availability, with credits
if breached). Error budget = 1 - SLO = how much
unreliability is acceptable. For 99.9% SLO over 28 days:
~40 minutes of downtime budget. Error budget drives
engineering decisions: budget healthy = deploy; budget
exhausted = reliability work only."

---

### 💡 The Surprising Truth

The most common SLO mistake is setting availability
SLOs at the server level ("is the process running?")
instead of the user level ("are user requests succeeding?").
A service can be "available" (process running, health
check green) while users experience errors. Example:
circuit breaker is open (service is up, health check
passes) but all requests return 503 (users experiencing
100% error rate). An availability SLI based on health
checks will show 100% availability. An availability SLI
based on actual request success rate will show 0%.
Always measure SLIs from the user-facing traffic.
Health checks are for Kubernetes infrastructure; SLIs
are for reliability engineering.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **DEFINE** Write SLO definitions for a microservice:
SLI formula, target percentage, measurement window,
what counts as a success vs failure.
2. **CALCULATE** Given an SLO and time window, calculate
the error budget in minutes. Given current consumption
rate, project whether the budget will be exhausted.
3. **IMPLEMENT** Set up Prometheus queries for availability
and latency SLIs using `http_server_requests_seconds`
metrics from Spring Boot Actuator.
4. **ALERT** Configure multi-window burn-rate alerts:
page on fast burn (1h window, 14x burn rate), ticket
on slow burn (6h window, 6x burn rate).
5. **GOVERN** Define an error budget policy that specifies
deployment decisions based on budget remaining percentage.

---

### 🧠 Think About This Before We Continue

**Q1.** You have a microservices system where the product
SLA is 99.9% availability. The system has 5 services
in the critical path. What SLO must each service maintain,
assuming independent failure, to achieve the product
SLA with a comfortable margin?

**Q2.** Your team is debating whether to set the SLO at
99.9% or 99.99%. You're releasing multiple features
per week. What are the engineering implications of
choosing 99.99%? How does the error budget change,
and how does that affect deployment frequency?

**Q3.** Your availability SLO is 99.9% but the service
is actually performing at 99.95% - well within budget.
A product manager argues this means you can reduce
reliability work. A reliability engineer argues you
should raise the SLO to 99.95% to "challenge the team".
Who is right, and what factors should drive the decision
to revise an SLO?