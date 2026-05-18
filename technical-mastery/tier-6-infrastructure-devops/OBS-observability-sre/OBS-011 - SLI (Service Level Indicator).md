---
id: OBS-011
title: "SLI (Service Level Indicator)"
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★☆☆
depends_on: OBS-005, OBS-006
used_by: OBS-012, OBS-013, OBS-020
related: OBS-005, OBS-012, OBS-009
tags:
  - observability
  - reliability
  - foundational
  - first-principles
  - sre
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Mastery"
nav_order: 11
permalink: /technical-mastery/obs/sli-service-level-indicator/
---

⚡ TL;DR - An SLI is the specific metric you choose to
measure whether your service is meeting its reliability
promise to users - the single number that says "are
users experiencing good service right now?"

| #011            | Category: Observability & SRE              | Difficulty: ★☆☆ |
| :-------------- | :----------------------------------------- | :-------------- |
| **Depends on:** | SRE What It Is, Metrics Types              |                 |
| **Used by:**    | SLO, SLA, Error Budget                     |                 |
| **Related:**    | SRE What It Is, SLO, Alerting Fundamentals |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A team says their payment service is "highly available."
But what does that mean? Is it measured? Is it a gut
feeling from the on-call engineer who did not get paged
last week? When an incident occurs and management asks
"how reliable was the service this quarter?", the team
answers: "We think it was fine. We did not have many
incidents." This is not engineering - it is impression.
The service reliability is unmeasured, cannot be
compared to previous quarters, cannot be tracked over
time, and cannot be used to make decisions about
feature vs reliability investment.

**THE INVENTION MOMENT:**
Google's SRE practice formalised the SLI as the answer:
choose one specific, measurable, time-based ratio that
represents user experience. Not "how do we feel about
reliability" but "what fraction of requests, in the
last 30 days, were served successfully?" That number
is objective, comparable, and actionable.

---

### 📘 Textbook Definition

**A Service Level Indicator (SLI)** is a carefully
defined quantitative measure of some aspect of the
level of service being provided. It is always expressed
as a ratio: the fraction of events that were "good"
relative to total events, measured over a time window.

**SLI formula:**

```
SLI = (count of good events) / (count of total events)
```

**Standard SLI types by service class:**

- **Request-based services:** success ratio, latency
  ratio (fraction of requests faster than threshold)
- **Data pipelines:** freshness (fraction of data
  within age threshold), correctness (fraction of
  records without errors)
- **Storage systems:** durability (fraction of written
  data that can be read back), availability
- **Batch jobs:** completion ratio, timeliness

---

### ⏱️ Understand It in 30 Seconds

**One line:**
An SLI is the number that tells you whether users are
receiving good service - expressed as a ratio so it
can be compared and trended over time.

> Think of a teacher grading an exam. The raw score
> ("correct: 87") is not as useful as the ratio ("87/100
> = 87%"). The ratio can be compared across exams of
> different lengths, trended over time, and set a
> target against ("pass if >= 70%"). An SLI is the
> reliability equivalent: not "we had 3 errors today"
> (raw count, meaningless without context) but "99.97%
> of requests succeeded" (ratio, immediately comparable
> to yesterday's 99.99%).

**One insight:**
SLIs are ratios, not counts, not averages. This is the
most common mistake: teams define an SLI as "error
count" (a counter metric) or "average latency" (an
average, which hides outliers). A proper SLI is the
fraction of events that meet the "good" threshold.

---

### 🔩 First Principles Explanation

**WHY RATIOS, NOT ABSOLUTES:**
An absolute count of 100 errors means nothing without
the denominator. 100 errors out of 100 requests = 100%
failure rate (catastrophe). 100 errors out of 1,000,000
requests = 0.01% failure rate (within SLO). A ratio
normalises for traffic volume and makes the metric
comparable across time periods.

**WHY USER-VISIBLE, NOT SYSTEM-INTERNAL:**
A CPU at 95% utilisation is an internal system metric.
Users do not experience CPU. They experience:

- "Did my request succeed?" (availability SLI)
- "How long did my request take?" (latency SLI)
- "Was the data I received correct?" (correctness SLI)
  Internal metrics (CPU, memory, disk) are causes;
  SLIs are symptoms. SLIs measure what users notice.

**THE LATENCY SLI FORMULATION:**
Rather than "average latency" (which hides outliers),
a latency SLI is:

```
Latency SLI = fraction of requests that complete
              in under T milliseconds

Example: fraction of checkouts completing < 500ms
= count(checkout_duration < 500ms)
  / count(checkout_duration total)
```

This is the "latency ratio" - using a histogram metric
with `histogram_quantile()` in Prometheus.

**TRADE-OFFS:**

**Gain:** objective, measurable, comparable, trackable.
SLI makes reliability a first-class engineering metric.

**Cost:** choosing the right SLI requires understanding
what users actually care about. A poor SLI choice (one
that does not correlate with user experience) produces
a metric that is green when users are suffering.

---

### 🧪 Thought Experiment

**SETUP:**
Two checkout services. Service A tracks "is the server
up?" (binary availability). Service B tracks "what
fraction of checkout requests return HTTP 2xx within
500ms?"

**WHAT HAPPENS:**
Service A's health check returns 200 OK. SLI = 100%.
Users are actually experiencing 3% checkout failures
because a payment dependency is returning 500 errors.
The health check does not call the payment dependency.
The SLI appears healthy while users suffer.

Service B's SLI measures actual checkout success:
`sum(rate(checkout_total{status=~"2.."}[5m]))
/ sum(rate(checkout_total[5m]))` = 97%.
The SLI immediately reflects the payment dependency
failure. It degrades at the same moment users notice.

**THE INSIGHT:**
An SLI must measure the user-facing behaviour directly,
not a proxy that might diverge from user experience.
Health checks measure "is the process alive?"; SLIs
measure "are users being served well?"

---

### 🧠 Mental Model / Analogy

> A restaurant uses two reliability measures. The first:
> "is the kitchen open?" (binary - yes/no). The second:
> "what fraction of orders were delivered correctly and
> within 20 minutes?" The first measure could be 100%
> while customers wait 90 minutes for cold food. The
> second measure directly reflects customer experience.
> The SLI is always the second type.

The SLI design question is always: "What number, if it
degraded, would cause customers to notice and complain?"
For a search engine: query success rate and P99 latency.
For a payment service: transaction success rate and
P99 time to payment confirmation. For a streaming
service: fraction of playback starts within 2 seconds.

**Where this breaks down:** Some user-visible behaviours
are hard to instrument. "Was the recommendation relevant?"
is user experience that cannot be directly measured by
a server-side SLI. These require synthetic monitoring,
user satisfaction surveys, or proxy metrics (click-through
rate on recommendations).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone):**
An SLI is a number that measures how well your service
is performing from the user's perspective. For example,
"what percentage of login attempts succeeded?"

**Level 2 - How to use it (junior developer):**
Pick one metric that best represents user experience for
your service. Express it as a ratio: good events /
total events. For an API: HTTP 2xx responses / total
responses. Implement it as a PromQL query over your
existing counter metrics.

**Level 3 - How it works (mid-level):**
SLIs are typically computed from Prometheus counter
metrics using `rate()` queries. The ratio is computed
over a sliding time window (5m for alerting, 30d for
SLO compliance). For latency SLIs, use histogram buckets
to compute the fraction of requests within the threshold.

**Level 4 - Why it matters (senior/staff):**
The hard part of SLI design is choosing what to measure.
Three criteria: (1) it must correlate strongly with
user satisfaction - if this metric is green, users are
happy; if it degrades, users notice; (2) it must be
measurable continuously from server-side instrumentation;
(3) it must be aggregatable across service instances.
The common trap: designing an SLI that measures something
easy to measure (server uptime) rather than something
that correlates with user experience (request success).

**Level 5 - Mastery (distinguished engineer):**
At scale, SLI granularity becomes important. A single
SLI for the entire checkout service may hide regional
failures (US is healthy, EU is degraded). Multi-
dimensional SLIs (broken down by `region`, `user_tier`,
`payment_method`) provide more actionable signal but
require more careful aggregation. The rule: the SLO
must be defined at the same granularity as the SLI.
A 99.9% SLO measured globally may hide a 95% SLI in
one region where high-value customers are located.
Staff engineers also understand that SLIs should be
defined before instrumentation, not after - the SLI
definition drives which metrics to collect.

---

### ⚙️ How It Works (Mechanism)

**SLI COMPUTATION PIPELINE:**

```
[Application instruments request handling]
  counter: checkout_requests_total{status="2xx"}
  counter: checkout_requests_total{status="5xx"}
  histogram: checkout_duration_seconds
        ↓
[Prometheus scrapes every 15s]
  Stores time series with labels
        ↓
[SLI computed via PromQL]
  Availability SLI (5-min window for alerting):
    sum(rate(checkout_requests_total{
      status=~"2.."}[5m]))
    / sum(rate(checkout_requests_total[5m]))

  Latency SLI (fraction < 500ms, 5-min window):
    sum(rate(checkout_duration_seconds_bucket{
      le="0.5"}[5m]))
    / sum(rate(checkout_duration_seconds_count[5m]))
        ↓
[SLO evaluation]
  Availability SLI >= 0.999 → within SLO
  Availability SLI < 0.999 → SLO violated
```

**STANDARD SLI TEMPLATES:**

```promql
# Availability SLI (request-response service)
sum(rate(http_requests_total{status=~"2.."}[window]))
/ sum(rate(http_requests_total[window]))

# Latency SLI (fraction under threshold T)
sum(rate(http_duration_seconds_bucket{le="T"}[window]))
/ sum(rate(http_duration_seconds_count[window]))

# Freshness SLI (data pipeline)
# fraction of pipeline runs completing within 1 hour
count_over_time(
  pipeline_last_success_age_seconds{job="etl"}[24h]
  < 3600)
/ count_over_time(
  pipeline_last_success_age_seconds{job="etl"}[24h])
```

---

### 🔄 The Complete Picture - End-to-End Flow

**SLI IN THE SRE WORKFLOW:**

```
[Service design phase]
  Team answers: "What does good service mean to users?"
  → Availability: >99.9% of checkouts return 2xx
  → Latency: >99% of checkouts complete < 500ms
        ↓
[Instrumentation phase]
  Add counters + histogram to application code
  Verify metrics appear in Prometheus
        ↓
[SLI validation]
  Run PromQL queries in Grafana
  Confirm SLI reflects actual user experience
  [SRE team ← YOU ARE HERE: setting up SLI]
  Verify: degrade the dependency artificially
  Check: does SLI drop immediately?
        ↓
[SLO definition phase]
  SLO = target threshold for SLI (e.g., >= 0.999)
  Error budget = 1 - SLO = 0.001 per month
        ↓
[Continuous measurement]
  SLI measured continuously
  Alert when burn rate exceeds threshold
  Report SLO compliance monthly
```

---

### 💻 Code Example

**Example 1 - BAD: SLI as a health check (wrong):**

```java
// BAD: health check SLI - returns UP even when
// downstream dependencies are failing.
// Users can be receiving errors while this returns 100%.
@GetMapping("/health")
public ResponseEntity<String> health() {
    return ResponseEntity.ok("UP");
    // This always returns UP unless the process dies.
    // It does not measure actual request success rate.
}
```

**Example 2 - GOOD: SLI from actual request metrics:**

```java
// GOOD: SLI measured from real request outcomes.
// Automatically reflects actual user experience.
import io.prometheus.client.Counter;

static final Counter requests = Counter.build()
    .name("checkout_requests_total")
    .labelNames("status_class") // "2xx", "4xx", "5xx"
    .help("Checkout HTTP requests by status class")
    .register();

@PostMapping("/checkout")
public ResponseEntity<CheckoutResult> checkout(
        @RequestBody CheckoutRequest req) {
    try {
        CheckoutResult result = checkoutService.process(req);
        requests.labels("2xx").inc();
        return ResponseEntity.ok(result);
    } catch (UserError e) {
        requests.labels("4xx").inc();  // user error, not SLI
        throw e;
    } catch (Exception e) {
        requests.labels("5xx").inc();  // server error = bad SLI
        throw e;
    }
}

// SLI PromQL (exclude 4xx - user errors, not our fault):
// sum(rate(checkout_requests_total{status_class="2xx"}[5m]))
// / sum(rate(checkout_requests_total{
//     status_class=~"2xx|5xx"}[5m]))
```

**Example 3 - Latency SLI with histogram:**

```java
// Latency SLI: fraction of checkouts < 500ms
static final Histogram duration = Histogram.build()
    .name("checkout_duration_seconds")
    .buckets(0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0)
    //                   ^ SLO threshold: 500ms
    .register();

// PromQL for latency SLI (fraction under 500ms):
// sum(rate(checkout_duration_seconds_bucket{
//   le="0.5"}[5m]))
// / sum(rate(checkout_duration_seconds_count[5m]))
```

---

### ⚖️ Comparison Table

| SLI type         | Metric used                | Good event definition      | Service class        |
| ---------------- | -------------------------- | -------------------------- | -------------------- |
| **Availability** | HTTP status counter        | Status 2xx (or non-5xx)    | Request-response API |
| **Latency**      | Request duration histogram | Duration < threshold (P99) | Request-response API |
| **Freshness**    | Pipeline age gauge         | Data age < threshold       | Data pipeline        |
| **Correctness**  | Validation counter         | Passed validation          | Data pipeline        |
| **Durability**   | Write/read ratio           | Successful read-back       | Storage              |
| **Coverage**     | Records processed ratio    | Records without errors     | Batch job            |

**Common SLI mistakes:**

| Wrong SLI                   | Right SLI                        | Why                                      |
| --------------------------- | -------------------------------- | ---------------------------------------- |
| Average latency             | Fraction of requests < threshold | Average hides long tail                  |
| Error count                 | Error ratio (count / total)      | Count is meaningless without denominator |
| Health check up/down        | Request success ratio            | Health check does not test full path     |
| Infrastructure metric (CPU) | Request outcome                  | CPU is a cause, not a symptom            |

---

### ⚠️ Common Misconceptions

| Misconception                             | Reality                                                                                                                                                                                          |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "Average response time is a good SLI"     | Averages mask outliers. A 250ms average can coexist with a 5-second P99. The latency SLI should be a ratio: fraction of requests completing within the threshold.                                |
| "SLI = uptime percentage"                 | Uptime (binary up/down) is the crudest possible SLI. It misses partial failures, slow responses, and correctness errors. Use request success ratio instead.                                      |
| "More SLIs are better"                    | One or two well-chosen SLIs per service is sufficient. A checkout service needs an availability SLI and a latency SLI. Adding more SLIs dilutes focus and creates conflicting signals.           |
| "4xx errors should count against the SLI" | 4xx errors represent user mistakes (bad request, not found, unauthorised). They are not caused by your service misbehaving. Exclude 4xx from the SLI denominator - count only 5xx and successes. |
| "SLI is the same as SLO"                  | SLI is the measurement. SLO is the target. The SLI is "current success rate = 99.93%". The SLO is "target success rate >= 99.9%".                                                                |

---

### 🚨 Failure Modes & Diagnosis

**SLI does not reflect the actual user-visible failure**

**Symptom:**
The SLI dashboard shows 99.98% availability. Users are
reporting that 10% of checkouts silently fail - the
request returns 200 OK but no payment is processed
and no confirmation email is sent. The SLI appears
healthy; the service is broken.

**Root Cause:**
The SLI measures HTTP response code (2xx = good event).
The checkout handler catches all exceptions internally
and returns 200 OK even when the payment processing
fails. The HTTP success code does not reflect whether
the business transaction succeeded.

**Diagnostic Command:**

```bash
# Check if HTTP 200 responses contain error signals
# in the response body or downstream metric
grep "payment_failed" /var/log/checkout.log | wc -l
# Compare to HTTP 200 count in same window
```

**Fix:**
Define the SLI based on business outcome, not HTTP code:

```promql
# BETTER: count only confirmations sent (business outcome)
rate(checkout_payment_confirmed_total[5m])
/ rate(checkout_requests_total[5m])
```

**Prevention:**
Validate SLI definitions with synthetic load tests that
simulate partial failures. Verify that a simulated
payment failure causes the SLI to degrade.

---

**SLI computed from the wrong time window**

**Symptom:**
The SLI alert fires during a 2-minute incident but
the SLO compliance dashboard shows 99.97% for the month.
Post-mortem finds the monthly SLI calculation used a
5-minute rate window in the monthly query, masking
the actual monthly compliance.

**Root Cause:**
The 30-day SLO compliance query used `rate(...[5m])`,
which computes a per-second rate over 5-minute windows
and averages those rates over the 30-day display range.
The correct query for monthly compliance needs the
total count over the full 30-day window.

**Fix:**

```promql
# WRONG: 30-day SLO compliance with rate window
avg_over_time(
  sum(rate(errors[5m]))
  / sum(rate(requests[5m]))
  [30d:5m]
)

# CORRECT: total counts over full 30-day window
sum(increase(errors[30d]))
/ sum(increase(requests[30d]))
```

**Prevention:**
Test SLI computation at both short windows (for alerting)
and long windows (for SLO compliance). Compare results
manually against known incident windows.

---

**Excluding the wrong requests from SLI denominator**

**Symptom:**
SLO compliance shows 99.95% for the month. A quarterly
review finds that the SLI query excluded all requests
from non-authenticated users (unauthenticated 401 errors
were counted as "user error" and excluded). 30% of total
traffic is unauthenticated. The actual reliability seen
by all users is lower than measured.

**Root Cause:**
The SLI query excluded 4xx responses. However, 401
errors caused by an expired authentication service
are server-side failures, not user errors. Excluding
them masks a real reliability failure.

**Fix:**
Carefully define which 4xx codes represent genuine user
errors. Only exclude: 400 (bad request, user malformed
input), 404 (not found, user requested non-existent
resource). Include 401, 403, 429 in "bad events" if
they are caused by your service's own authentication
system failing.

**Prevention:**
Document the SLI exclusion policy. Review with the
product team: does a 401 response represent a user
failure or a service failure? The answer depends on
whether authentication is owned by this service.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `SRE What It Is` - SLIs are the core measurement tool
  of SRE practice; understanding the SRE philosophy
  explains why SLIs must measure user experience
- `Metrics Types (Counter, Gauge, Histogram)` - SLIs are
  computed from Prometheus counter and histogram metrics

**Builds On This (learn these next):**

- `SLO (Service Level Objective)` - the SLO is the target
  threshold applied to the SLI measurement
- `Error Budget` - the error budget is derived from the
  gap between SLO target and current SLI
- `Alerting Fundamentals` - SLO burn rate alerts are
  computed from the SLI measurement

**Alternatives / Comparisons:**

- `Health Checks` - binary up/down checks that are
  a much cruder proxy for service reliability than SLIs
- `Synthetic Monitoring` - probes that simulate user
  journeys and measure outcomes - used alongside SLIs
  when server-side metrics cannot fully capture user
  experience (e.g., client-side rendering performance)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ DEFINITION   │ Ratio: good_events / total_events        │
│              │ Measures user-visible service quality    │
├──────────────┼──────────────────────────────────────────┤
│ AVAILABILITY │ sum(rate(requests{status=~"2.."}[w]))    │
│ SLI          │ / sum(rate(requests[w]))                 │
├──────────────┼──────────────────────────────────────────┤
│ LATENCY SLI  │ sum(rate(duration_bucket{le="T"}[w]))    │
│              │ / sum(rate(duration_count[w]))           │
├──────────────┼──────────────────────────────────────────┤
│ EXCLUDE 4xx? │ Yes for 400, 404. No for 401, 503 (yours)│
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ avg(latency) as SLI - hides P99 outliers │
│              │ error_count as SLI - meaningless without │
│              │ denominator                              │
├──────────────┼──────────────────────────────────────────┤
│ GOOD SLI     │ Degrades immediately when users notice   │
│              │ problems. Healthy when users are fine.   │
├──────────────┼──────────────────────────────────────────┤
│ SLI vs SLO   │ SLI = the measurement                    │
│              │ SLO = the target for that measurement    │
├──────────────┼──────────────────────────────────────────┤
│ VALIDATE     │ Inject failures in staging. Verify SLI   │
│              │ degrades proportionally.                 │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ SLO definition → Error Budget → Alerting │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Measure outcomes, not activities. A sales team measures
"revenue closed" (outcome), not "calls made" (activity).
An SLI measures "requests successfully served" (outcome),
not "server uptime" (activity). The outcome metric
directly represents value delivered; the activity metric
is at best a proxy. This principle applies everywhere:
measuring "features shipped" vs "users achieving their
goal", "tests run" vs "defect escape rate", "deploys
per day" vs "MTTR".

---

### 💡 The Surprising Truth

The most counterintuitive SLI insight: the SLI for
a service should be defined by the users' experience,
not the service operator's experience. Operators care
about server health (CPU, memory). Users care about
request success and speed. The hardest part of SLI
design is not the PromQL - it is the conversation where
you ask "what does a user actually notice if our service
degrades?" and resist the temptation to answer with
infrastructure metrics that are easy to measure but
disconnected from user experience.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[EXPLAIN]** Explain why average latency is not a
   valid SLI and demonstrate the correct latency SLI
   formulation using a Prometheus histogram query.
2. **[DEBUG]** Given a scenario where SLI shows 99.98%
   but users report frequent failures, identify three
   ways the SLI definition could be wrong and write the
   PromQL fix for each.
3. **[DECIDE]** For a payment API, define two SLIs
   (availability and latency), specify the exact PromQL
   expressions, justify which 4xx codes to include vs
   exclude, and explain how to validate the SLI correctly
   reflects user experience.
4. **[BUILD]** Add SLI instrumentation to a Spring Boot
   checkout service: counter metrics with status_class
   labels, a duration histogram with SLO-aware bucket
   boundaries, and the recording rules that pre-compute
   the 5-minute SLI for use in dashboards and alerts.
5. **[EXTEND]** Design a multi-dimensional SLI for a
   global service that can reveal regional failures:
   define the label dimensions, write the PromQL for
   global SLI and per-region SLI, and describe how to
   set region-specific SLOs.

---

### 🧠 Think About This Before We Continue

**Q1.** Your checkout service handles three types of
requests: authenticated users (90% of traffic), guest
users (8%), and API integrations (2%). A production
incident causes 100% failure for API integrations but
0% failure for the other two groups. Your current SLI
measures overall success rate. Calculate the SLI value
during this incident. Would the SLO breach alert fire
if the SLO threshold is 99.9%? What does this reveal
about single-aggregate SLIs for heterogeneous traffic?
_Hint: 2% traffic x 100% failure = 2% of total requests
failing. 98% success rate. Yes, alert fires. But the
signal is diluted: API clients are experiencing complete
outage while the SLI shows 98%. Consider: should API
integrations have their own SLI and SLO?_

**Q2.** You are asked to define an SLI for a data
ingestion pipeline that processes events from IoT
sensors. The pipeline must: (1) process all events
within 60 seconds of receipt, (2) not drop any events,
(3) produce correct output (no data corruption). For
each requirement, define the SLI: what metric to
measure, how to express it as a ratio, and what
instrumentation you need in the pipeline code.
_Hint: (1) Freshness SLI = fraction of events with
processing_lag < 60s (needs event timestamp and
processing completion timestamp). (2) Completeness
SLI = events processed / events received (needs
ingestion counter and completion counter). (3)
Correctness SLI = validated events / total events
processed (needs validation step with counter)._

**Q3 (TYPE G):** You are the SRE lead for an e-commerce
platform with 50 microservices. Each service currently
has no SLI instrumentation. You have 1 engineer-month
to establish SLI coverage for the most critical services.
Design the prioritisation strategy: how do you determine
which services to instrument first, what SLIs to define
for each tier, how to avoid defining too many SLIs, and
what "done" looks like after the engineer-month. Include
the criteria for measuring success of this SLI rollout.
\*Hint: Prioritise by user impact and blast radius. The
checkout critical path (checkout → payment → inventory)
gets SLIs first. Define two SLIs per service (availability

- latency). Skip infrastructure-only services. Done =
  top 10 services have verified SLIs, SLOs are set, and
  at least one SLO breach has been simulated and detected
  within the new system.\*

---

### 🎯 Interview Deep-Dive

**Q1: "What is an SLI and how is it different from a
regular metric?"**
_Why they ask:_ Tests whether the candidate understands
the precision of SLI design, not just the acronym.
_Strong answer includes:_

- A metric is any measured value (CPU: 75%, request
  count: 1,234). A metric by itself is not an SLI.
- An SLI is a specific metric formulated as a ratio
  (good events / total events) over a time window,
  chosen specifically because it represents user
  experience.
- Key distinctions: SLI is always a ratio (not absolute),
  always user-visible (not internal system health),
  always time-bounded (measured over a window)
- Example: `requests_total` is a metric.
  `success_rate = rate(success[5m]) / rate(total[5m])`
  is an SLI.

**Q2: "How would you define an SLI for a checkout API?
Walk me through the PromQL."**
_Why they ask:_ Tests practical implementation, not
just conceptual understanding.
_Strong answer includes:_

- Start with the user question: "Did my checkout succeed
  and was it fast?"
- Availability SLI: `sum(rate(checkout_requests_total{
status=~"2.."}[5m])) / sum(rate(
checkout_requests_total{status!~"4.."}[5m]))`
- Latency SLI: `sum(rate(checkout_duration_seconds_bucket
{le="0.5"}[5m])) / sum(rate(
checkout_duration_seconds_count[5m]))`
- Note the exclusion of 4xx from the availability
  denominator: user errors (400, 404) are not the
  service's reliability failures
- Mention: histogram buckets must include the SLO
  threshold (0.5s) as a bucket boundary for accuracy

**Q3: "Your SLI shows 99.95% availability but users are
filing support tickets saying checkout is broken.
What are the possible explanations?"**
_Why they ask:_ Tests ability to question metric validity
and diagnose measurement failures - critical skill.
_Strong answer includes:_

- The SLI definition is wrong: service returns 200 OK
  even when payment fails (business failure masked by
  HTTP success)
- The SLI excludes a subset of users experiencing the
  issue (authenticated users are fine, guest users fail,
  but guest traffic is excluded from SLI)
- The incident is too short to move the monthly SLI
  below the threshold (5 minutes of 100% failures in
  a 30-day window barely moves the aggregate)
- Client-side failures not captured server-side (network
  timeouts, client-side JavaScript errors not reflected
  in server metrics)
- The SLI measures the wrong endpoint (health check
  endpoint is healthy; checkout endpoint is broken)
