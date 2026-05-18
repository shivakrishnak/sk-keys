---
id: OBS-014
title: "Observability Interview Preparation Guide"
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★☆☆
depends_on: OBS-001, OBS-002, OBS-005, OBS-011, OBS-012
used_by:
related: OBS-001, OBS-002, OBS-005, OBS-006, OBS-007, OBS-008
tags:
  - observability
  - reliability
  - sre
  - foundational
  - mental-model
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Mastery"
nav_order: 14
permalink: /technical-mastery/obs/observability-interview-preparation-guide/
---

⚡ TL;DR - Observability interviews test three things:
conceptual precision (SLI vs SLO vs SLA), operational
fluency (how you debug a production incident), and
system design depth (how you build observable systems
from scratch). This guide maps the question types and
what interviewers are actually evaluating.

| #014            | Category: Observability & SRE                            | Difficulty: ★☆☆ |
| :-------------- | :------------------------------------------------------- | :-------------- |
| **Depends on:** | Observability Fundamentals, SRE, SLI, SLO, Three Pillars |                 |
| **Used by:**    | (meta-guide, no downstream keywords)                     |                 |
| **Related:**    | OBS-001, OBS-002, OBS-005, OBS-006, OBS-007, OBS-008     |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A candidate with solid observability knowledge answers
"I've used Datadog and Prometheus in production" and
receives no follow-up offer. Another candidate who
has only read documentation answers confidently:
"I understand the three pillars, I design SLO-based
alerting, and I debug production incidents by starting
with the golden signals." They get the offer. The
difference: not knowledge depth, but the ability to
communicate observability concepts in the precise
language interviewers use.

**THE INTERVIEW MAP:**
Observability interviews at SRE-focused companies
test three distinct capabilities:

1. **Concept precision:** Can you define SLI, SLO, SLA,
   error budget without confusing them?
2. **Operational fluency:** Can you debug a production
   incident from first principles - where do you look,
   what do you check, what tools do you reach for?
3. **System design:** Can you design an observability
   stack for a new service from scratch? What would
   you instrument, what would you alert on, how would
   you structure dashboards?

---

### 📘 Textbook Definition

**Observability** is the ability to infer the internal
state of a system from its external outputs (logs,
metrics, traces). An observable system can be debugged
without modifying the code or deploying new diagnostic
instrumentation.

**The core interview framework - four conceptual areas:**

```
1. Observability Foundations
   What it is, why it matters, three pillars,
   monitoring vs observability distinction

2. SRE and Reliability Measurement
   SLI, SLO, SLA, error budget, burn rate alerting

3. Tooling and Implementation
   Prometheus, Grafana, OpenTelemetry, Jaeger,
   ELK/EFK stack, Datadog, CloudWatch

4. Operations and Incident Response
   On-call processes, runbooks, post-mortems,
   alerting anti-patterns, incident management
```

---

### ⏱️ Understand It in 30 Seconds

**The five questions you must be able to answer cold:**

1. "What is observability?" - The three pillars
   (logs, metrics, traces) and why they are insufficient
   individually. Observability = ability to ask new
   questions without deploying new code.

2. "Explain SLI, SLO, SLA." - SLI is the measurement,
   SLO is the internal target, SLA is the customer
   contract. SLO must be tighter than SLA. SLO drives
   the error budget.

3. "A service has high latency. How do you debug it?"
   - Golden signals (latency, traffic, errors, saturation),
     distributed traces to find the slow span, metrics
     to identify bottleneck, logs to find error context.

4. "Design an observability stack for a new microservice."
   - Structured JSON logs, Prometheus metrics with
     RED pattern, distributed traces via OpenTelemetry,
     SLO-based alerting with burn rate rules.

5. "What is an error budget and how do you use it?"
   - Error budget = (1 - SLO) x window. When budget is
     healthy: deploy freely. When exhausted: freeze + reliability sprint.

---

### 🔩 First Principles Explanation

**THE FOUR INTERVIEW QUESTION ARCHETYPES:**

**Type 1 - Define and Contrast**
Pattern: "What is X? How does it differ from Y?"
What is tested: conceptual precision and mental models.
Examples: "SLI vs SLO vs SLA", "monitoring vs
observability", "metrics vs logs vs traces",
"alert vs alarm vs incident."

Approach: Define X clearly, then state one concrete
difference, then give a practical example. Never
give circular definitions ("an SLO is an objective
for your SL...").

**Type 2 - Walk Me Through**
Pattern: "Walk me through how you would debug..."
What is tested: systematic debugging methodology
and production experience.
Examples: "Walk me through debugging high error rate
on a payment API", "walk me through a P0 incident
response", "walk me through setting up SLOs for
a new service."

Approach: Use a structured framework (start with
the golden signals, narrow to the component, isolate
the change). Name specific tools at each step
(PromQL, distributed trace in Jaeger, log filter in
Kibana). Always end with "and I would write a
post-mortem to prevent recurrence."

**Type 3 - System Design**
Pattern: "Design an observability system for..."
What is tested: ability to design instrument-ation
and alerting from first principles.
Examples: "Design observability for a 50-microservice
payment platform", "how would you set up on-call for
a new service?", "design an SLO monitoring stack."

Approach: Start with the user journey (what are the
critical user actions?), derive SLIs from those
actions, set SLOs, then design the instrumentation
to measure the SLIs, then design the alerting to
fire when SLOs are at risk.

**Type 4 - Tradeoff and Opinion**
Pattern: "What would you do if...?"
What is tested: pragmatism and real-world judgment.
Examples: "Error budget is exhausted but a customer
needs an urgent feature. What do you do?",
"Your team gets paged 20 times/night. What do you
do?", "Should we build or buy our observability stack?"

Approach: State the principle, acknowledge the tension,
give your recommended approach with reasoning.
Avoid "it depends" without following up with specific
decision factors.

---

### 🧪 Thought Experiment

**THE 45-MINUTE INTERVIEW SIMULATION:**

Imagine you have 45 minutes with an SRE interviewer
at a mid-to-large tech company.

**Minutes 1-5:** Conceptual warmup
"Define observability. How is it different from monitoring?"
→ Expected: three pillars, the unknown unknowns framing,
monitoring = alerts on known failure modes, observability =
ability to debug novel failure modes.

**Minutes 5-20:** Operational scenario
"Your checkout service's error rate just spiked to 5%.
Walk me through your debugging process in real time."
→ Expected: check golden signals (errors, latency,
traffic, saturation), look at distributed traces for
the failing requests, check recent deployments, examine
downstream service health, narrow to the root cause.
Strong candidates name specific queries:
`rate(checkout_errors_total[5m]) / rate(checkout_requests_total[5m])`

**Minutes 20-35:** SRE concepts
"Explain error budgets and how you use them operationally."
→ Expected: error_budget = (1 - SLO) x window, three
states (healthy/caution/exhausted), deployment policy
per state, quarterly SLO review.

**Minutes 35-45:** System design
"How would you set up observability for a new payments
microservice? What would you instrument on day 1?"
→ Expected: start with SLI definition (what is 'good'
for this service?), RED pattern metrics, structured
logs with trace IDs, distributed tracing wired to
OpenTelemetry, one SLO-based alert, runbook written
before the first pager.

---

### 🧠 Mental Model / Analogy

> An aircraft cockpit is a masterclass in observability
> design. The critical instruments (altimeter, airspeed,
> attitude indicator) are positioned prominently and
> alert immediately when outside safe ranges - this is
> the golden signals dashboard. The flight data recorder
> captures full state at 64 points/second - this is
> structured logging. The black box enables post-mortem
> analysis of any incident, even previously unknown
> failure modes. The flight plan defines the expected
> flight path - this is the SLO.
>
> A pilot who knows only "the plane is flying or not"
> is like a team with binary uptime monitoring.
> A pilot who can read all the instruments and knows
> which combinations indicate early-stage engine
> trouble - before it becomes a full failure - is
> like an SRE with full observability.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - Interview foundation (junior):**
Know the three pillars. Know that SLI is measurement,
SLO is target, SLA is contract. Know the four golden
signals. Be able to name one tool in each pillar
(Prometheus/Grafana for metrics, ELK for logs,
Jaeger for traces).

**Level 2 - Operational readiness (mid-level):**
Demonstrate debugging methodology: given an error
spike, what sequence of checks do you perform?
Be able to write basic PromQL. Explain error budget
and how it drives deployment decisions.

**Level 3 - SRE practitioner (senior):**
Design SLOs from first principles. Write multi-window
burn rate alerts. Explain distributed tracing context
propagation. Know the tradeoffs: push vs pull metrics,
agent-based vs sidecar observability, sampling strategies
for traces.

**Level 4 - Platform builder (staff):**
Design the observability platform for a 100-service
org. Cardinality management in Prometheus. Retention
strategies for logs at scale. Trace sampling strategy
(head vs tail sampling). Cost of observability vs
business value.

**Level 5 - Cultural leader (principal):**
Build observability culture: SLO review processes,
blameless post-mortem practice, toil reduction through
automation, observability as a development requirement
not a deployment afterthought.

---

### ⚙️ How It Works (Mechanism)

**INTERVIEW EVALUATION RUBRIC:**

Observability interviewers at companies with SRE
practice typically score on these dimensions:

```
[DIMENSION 1: Conceptual Precision]
Does the candidate define terms correctly without
conflating SLI/SLO/SLA or monitoring/observability?
Weak: "SLO is like an SLA but internal"
Strong: "SLO is the target value for an SLI over a
        time window, set tighter than the SLA to
        provide a buffer before contractual breach"

[DIMENSION 2: Production Fluency]
Does the candidate describe real-world usage or
textbook scenarios?
Weak: "I would look at the dashboard"
Strong: "I would check burn rate on the availability
        SLI over the last 1h and 5m windows using
        the multi-window alert pattern. If fast burn
        is > 14.4x, I page the on-call immediately."

[DIMENSION 3: System Design Capability]
Can the candidate design an observable system, not
just use existing tools?
Weak: "I would set up Datadog"
Strong: "I would define the SLIs first - what does
        'good' mean for this service? Then I would
        instrument the application to emit structured
        logs with request IDs, add the RED pattern
        metrics, wire OpenTelemetry traces, and write
        the first SLO alert before we deploy to prod."

[DIMENSION 4: Incident Handling]
Does the candidate understand the human/process side?
Weak: "I would fix the issue and close the ticket"
Strong: "I would page the on-call, start an incident
        bridge, assign roles (IC, comms lead), work
        the technical mitigation, communicate to
        stakeholders at 30-minute intervals, and
        conduct a blameless post-mortem within 5 days."
```

---

### 🔄 The Complete Picture - End-to-End Flow

**OBSERVABILITY SYSTEM DESIGN FRAMEWORK:**
(Use this for "design the observability for X" questions)

```
Step 1: Define user journeys
  "What does a successful user interaction look like?"
  → checkout, login, search, API call

Step 2: Derive SLIs from user journeys
  Each critical action → availability + latency SLI
  → checkout_availability_sli, checkout_p99_sli

Step 3: Set SLO targets
  Based on measured baseline, user research
  → checkout_availability >= 99.9% over 30d
  → checkout_p99_latency <= 500ms 95% of requests

Step 4: Instrument the application
  → Structured JSON logs with request_id, trace_id
  → RED pattern metrics (rate, errors, duration)
  → OpenTelemetry spans for every key operation

Step 5: Set up collection
  → Prometheus scraping app metrics
  → Filebeat/Fluentd shipping logs to Elasticsearch
  → OTel Collector exporting traces to Jaeger/Tempo

Step 6: Build dashboards
  → SLO compliance page (current SLI vs SLO target)
  → Golden signals dashboard (per service)
  → Infrastructure health (CPU, memory, network)

Step 7: Write SLO-based alerts
  → Multi-window burn rate alerts (fast + slow)
  → Page on: 14.4x burn rate 1h + 5m (budget in <1d)
  → Alert on: 6x burn rate 6h + 30m (budget in <3d)

Step 8: Write the runbook BEFORE deploying
  → What does this alert mean?
  → What are the first 3 things to check?
  → Who to escalate to?
  → How to mitigate vs fully resolve?
```

---

### 💻 Code Example

**Example 1 - SLO alert (the interview gold standard):**

```yaml
# Multi-window burn rate SLO alert
# This is the answer to: "write an SLO-based alert"
# DO NOT write simple threshold alerts for SLO interviews
groups:
  - name: checkout-slo
    rules:
      # Fast burn: pager-level (budget consumed in <1 day)
      - alert: CheckoutSLOFastBurn
        expr: |
          (
            (1 - sum(rate(checkout_ok[1h]))
            / sum(rate(checkout_total[1h])))
            / (1 - 0.999)
          ) > 14.4
          and
          (
            (1 - sum(rate(checkout_ok[5m]))
            / sum(rate(checkout_total[5m])))
            / (1 - 0.999)
          ) > 14.4
        labels:
          severity: page
      # Slow burn: ticket-level (budget consumed in <3 days)
      - alert: CheckoutSLOSlowBurn
        expr: |
          (
            (1 - sum(rate(checkout_ok[6h]))
            / sum(rate(checkout_total[6h])))
            / (1 - 0.999)
          ) > 6
          and
          (
            (1 - sum(rate(checkout_ok[30m]))
            / sum(rate(checkout_total[30m])))
            / (1 - 0.999)
          ) > 6
        labels:
          severity: ticket
```

**Example 2 - Structured log (the instrumentation answer):**

```json
// GOOD: structured log - filterable, parseable, joinable
{
  "timestamp": "2024-04-15T14:23:01.234Z",
  "level": "ERROR",
  "service": "checkout-api",
  "trace_id": "a1b2c3d4e5f6a7b8",
  "span_id": "1234567890abcdef",
  "request_id": "req-123-xyz",
  "user_id": "usr-456",
  "action": "process_payment",
  "duration_ms": 2350,
  "status_code": 503,
  "error": "payment-gateway timeout",
  "upstream": "payment-gateway-us-east"
}

// BAD: unstructured log - unfilterable, grep-only
// 2024-04-15 14:23:01 ERROR checkout-api failed to
// process payment for user usr-456 after 2350ms
// Error: payment-gateway timeout
```

**Example 3 - Golden signals PromQL (the debugging answer):**

```promql
# Rate (throughput): requests per second
sum(rate(checkout_requests_total[5m]))

# Errors: error rate as fraction
sum(rate(checkout_requests_total{status=~"5.."}[5m]))
/ sum(rate(checkout_requests_total[5m]))

# Duration: P99 latency
histogram_quantile(0.99,
  rate(checkout_request_duration_seconds_bucket[5m]))

# Saturation: queue depth or pending requests
avg(checkout_queue_depth)
```

---

### ⚖️ Comparison Table

| Question type                            | Weak answer                                              | Strong answer                                                                                                                                                                                                                                                                                                 |
| ---------------------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "What is observability?"                 | "It's being able to see what's happening in your system" | "Observability is the ability to ask new questions about a system's internal state using its external outputs - logs, metrics, traces - without requiring code changes or new instrumentation"                                                                                                                |
| "Explain error budget"                   | "It's how much downtime you're allowed"                  | "Error budget = (1 - SLO) x window. 99.9% SLO over 30 days = 43.2 minutes. It's not 'allowed downtime' - it's a risk budget that governs deployment velocity. When exhausted, deployments freeze."                                                                                                            |
| "Debug a high error rate"                | "I'd check the logs and see what's happening"            | "I'd start with the error rate golden signal over 5m and 1h windows. If it's a sudden spike, I'd correlate with recent deployments via the deployment marker in Grafana. Then I'd pull distributed traces from the error window to identify which span is failing and which upstream dependency is involved." |
| "Design observability for a new service" | "I'd set up Datadog"                                     | "I'd start by defining the SLIs for the service's critical user journeys, then instrument with RED pattern metrics, structured logs with trace IDs, OpenTelemetry spans, write the first SLO-based alert and runbook before first production deployment."                                                     |

---

### ⚠️ Common Misconceptions

| Misconception                           | Reality                                                                                                                                                                                                                                                         |
| --------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Just name the tools you've used"       | Tool names without conceptual depth fail experienced interviewers. Saying "I used Prometheus" is less impressive than explaining WHY you chose Prometheus and what its tradeoffs are vs Datadog for your specific use case.                                     |
| "SRE interviews are only about on-call" | Senior SRE interviews test system design (how you build observable systems), SLO calibration, and reliability culture - not just incident response.                                                                                                             |
| "Observability = monitoring"            | This is a common conflation that immediately signals shallow knowledge to interviewers. Monitoring = alerting on known failure modes. Observability = ability to debug unknown failure modes.                                                                   |
| "Metrics are more important than logs"  | Neither is categorically more important. Metrics are best for detecting and alerting; logs are best for diagnosing root cause after an alert fires; traces are best for understanding distributed system interactions. The three pillars complement each other. |
| "You need to know every tool"           | Deep knowledge of 2-3 tools beats shallow knowledge of 10. Know one metrics system (Prometheus or Datadog), one logging system (ELK or Loki), one tracing system (Jaeger or Zipkin or Tempo) very well.                                                         |

---

### 🚨 Failure Modes & Diagnosis

**Giving textbook definitions without production examples**

**Symptom:**
The candidate correctly defines SLI, SLO, SLA in
sequence but cannot answer "what is an SLO you set
in production and how did you calibrate it?"

**What the interviewer thinks:**
This candidate understands the theory but has not
applied it. For an SRE role, theory without application
is insufficient.

**Fix:**
Prepare 2-3 specific examples:

- An SLO you set (what service, what target, how you
  derived it from user research or measured baseline)
- An error budget policy you enforced (how did the
  team react when the budget was exhausted?)
- An incident you debugged using the three pillars
  (what was the alert, what metric/log/trace helped
  you find the root cause?)

---

**Jumping to tools without defining the problem**

**Symptom:**
Asked "how would you design observability for a new
service?", the candidate immediately starts listing
tools: "I'd use Datadog for metrics, Splunk for logs,
Jaeger for traces..."

**What the interviewer thinks:**
This candidate defaults to tools without asking what
the service needs to observe. They may not have
experience designing observability from first principles.

**Fix:**
Always start with the user journey and SLI definition.
"First I'd ask: what does a successful user interaction
look like? What's the critical path? What would a
user notice if it degraded? Those answers define
the SLIs. Then I'd design the instrumentation to
measure those SLIs. The tool choice follows the
measurement design, not the other way around."

---

**Confusing SLO breach with incident**

**Symptom:**
Asked "what happens when an SLO is breached?",
the candidate says: "We would immediately page on-call
and start the incident response process."

**What the interviewer thinks:**
The candidate conflates SLO burn rate (rate of error
budget consumption) with an active incident. A slow
burn SLO breach may not require immediate paging -
it may require a deployment freeze and reliability
sprint over the coming days.

**Fix:**
Distinguish: a fast burn rate alert (budget depleted
in hours) = page on-call. A slow burn alert (budget
depleted in days) = create a reliability ticket, review
deployments, plan a sprint. An exhausted error budget
= deployment freeze, not necessarily an ongoing incident.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `What Is Observability and Why It Matters` - the
  conceptual foundation for all interview questions
- `The Three Pillars of Observability` - the core
  architectural framework
- `SRE What It Is and Why It Exists` - the cultural
  and organisational context

**Builds On This (learn these next):**

- `SLI` and `SLO` - the reliability measurement system
  that is tested most heavily in senior SRE interviews
- `Prometheus Metrics Collection` - the most commonly
  tested tooling in metrics interviews
- `Alerting Fundamentals` - burn rate alerting is
  a favourite deep-dive topic in SRE interviews

**Alternatives / Comparisons:**

- `Interview Preparation` vs `Production Knowledge` -
  the strongest interview candidates have both. Production
  knowledge without communication skills fails interviews.
  Communication skills without production knowledge
  fails practical coding/debugging exercises.

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ 5 COLD QUESTIONS  │ 1. What is observability?           │
│ YOU MUST ANSWER   │ 2. SLI vs SLO vs SLA                │
│                   │ 3. Debug high latency step-by-step  │
│                   │ 4. Design observability from scratch│
│                   │ 5. Error budget and deployment polic│
├───────────────────┼─────────────────────────────────────┤
│ 4 INTERVIEW       │ 1. Define and contrast              │
│ ARCHETYPES        │ 2. Walk me through                  │
│                   │ 3. System design                    │
│                   │ 4. Tradeoff and opinion             │
├───────────────────┼─────────────────────────────────────┤
│ INSTANT FAIL      │ "I would check the logs/dashboard"  │
│ PHRASES           │ without specific tooling or queries │
│                   │ "Observability = monitoring"        │
│                   │ "SLO = SLA"                         │
├───────────────────┼─────────────────────────────────────┤
│ ALWAYS MENTION    │ Multi-window burn rate alerts       │
│ IN SLO DESIGN     │ Error budget policy (3 states)      │
│                   │ SLO tighter than SLA (buffer)       │
├───────────────────┼─────────────────────────────────────┤
│ DEBUGGING         │ Start: golden signals (LETS)        │
│ SEQUENCE          │ Narrow: distributed traces          │
│                   │ Confirm: logs in error window       │
│                   │ End: post-mortem / runbook update   │
├───────────────────┼─────────────────────────────────────┤
│ NEXT EXPLORE      │ SLI → SLO → Error Budget → Alerting │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Interviewers are not testing your ability to recall
definitions. They are testing whether you have built
mental models under real conditions. Every question
is an invitation to share a concrete example. "In
production, when X happened, I used Y to do Z, and
the result was W" is always stronger than "one would
use Y when X happens." This applies universally:
performance interviews, architecture discussions,
incident retrospectives. Real examples beat abstract
correctness every time.

---

### 💡 The Surprising Truth

The most surprising truth about observability interviews:
the candidates who pass senior SRE interviews at
companies like Google, Netflix, and Stripe are not
necessarily the ones who have used the most tools.
They are the ones who can clearly explain the failure
mode of their current approach and what they would
do differently next time. "We set the SLO too high,
the error budget was always exhausted, the team
stopped trusting it, and we had to reset it after
measuring a real baseline" demonstrates more credibility
than "we ran everything at 99.99% and never had
problems."

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[DEFINE]** Define SLI, SLO, SLA in 30 seconds
   each with no conflation and one concrete example
   per definition.
2. **[DEBUG]** Given a scenario "error rate spiked to
   5% on checkout 10 minutes ago," describe the first
   8 steps of your debugging process with specific
   PromQL queries or log filter syntax at each step.
3. **[DESIGN]** Sketch the full observability design
   for a new payment service in 15 minutes: SLIs,
   SLOs, instrumentation, alerting, runbook structure.
4. **[CRITIQUE]** Given a description of another team's
   observability setup ("we alert on CPU > 80%"), identify
   at least three problems with that approach and
   propose a better design.
5. **[EXPLAIN]** Explain to a non-technical engineering
   manager why the team needs to freeze deployments
   when the error budget is exhausted, using the
   hotel or car warranty analogy.

---

### 🧠 Think About This Before We Continue

**Q1.** An interviewer asks: "You've been on-call for
a year. What's one observability mistake you made,
what went wrong, and what did you change?" This is
a behavioural question about observability experience.
Prepare your answer using this structure: (1) describe
the system, (2) describe the failure mode that was
missed, (3) what the alert gap was, (4) what you added
or changed, (5) what you would have done differently
from day 1.

**Q2.** You are asked to design observability for a
batch job that runs once per night to process 10M
records. The golden signals model (latency, traffic,
errors, saturation) was designed for request-serving
systems. How do you adapt it for a batch system?
What SLIs would you define? What does "availability"
mean for a job that runs once per night?
_Hint: Batch SLIs: job completion SLI (fraction of
nightly runs completing before deadline), correctness
SLI (fraction of records correctly processed),
timeliness SLI (did the job finish before the next
business day began?). "Availability" becomes "did the
job run and complete successfully within the required
window?"_

**Q3 (TYPE G):** You are interviewing for an SRE role
at a company with 50 microservices, no current SLO
framework, and teams who use a mix of CloudWatch,
Datadog, and home-built dashboards. In your final
interview round (technical lead panel), you are asked:
"How would you build an observability culture from
scratch over the next 12 months?" Design the 12-month
plan: what you would do in months 1-3 (foundation),
4-6 (SLO rollout), 7-9 (tooling consolidation), and
10-12 (cultural maturity). Justify each phase's
priorities and expected outcomes.
_Hint: Months 1-3: instrument 3 most critical services,
define SLIs, measure baselines. Don't set SLOs yet -
you need data first. Months 4-6: set SLOs based on
3-month baseline, write error budget policies, train
teams on the framework. Months 7-9: consolidate tooling
(standardise on one metrics stack, one logging stack),
migrate home-built dashboards. Months 10-12: review
first year of SLO data, run quarterly SLO calibration,
introduce blameless post-mortem process._

---

### 🎯 Interview Deep-Dive

**Q1: "What is observability? How is it different
from monitoring?"**
_Why they ask:_ This is the entry-level filter.
Many candidates cannot articulate the distinction.
_Strong answer:_
"Monitoring is the practice of alerting on known
failure modes - you define thresholds on known metrics
and alert when they are breached. Observability is
the ability to ask new questions about system behaviour
without modifying the code or deploying new
instrumentation. An observable system can be debugged
using its existing outputs. The three pillars provide
different lenses: metrics for detection and alerting,
logs for context and diagnosis, traces for understanding
distributed system interactions. Monitoring tells you
something is wrong; observability helps you understand
why."

**Q2: "How would you approach debugging a sudden
latency increase on a microservice?"**
_Why they ask:_ Tests systematic debugging under pressure.
_Strong answer:_
"First I check the four golden signals: error rate
and latency are the most relevant here. I'd look at
the P50, P95, and P99 latency with a PromQL query
like `histogram_quantile(0.99, rate(duration_bucket[5m]))`.
If P99 spiked but P50 is fine, it's likely a tail
latency issue, possibly a specific request type or
downstream dependency. I'd pull distributed traces
for requests in the high-latency percentile and look
for the slow span - which service, which database
query, which external call. If it correlates with
a recent deployment, I'd check the deployment timeline
in Grafana. I'd also check saturation metrics: is
the service CPU-bound, memory-bound, or connection-
pool exhausted? After finding the root cause I'd fix
or roll back, then write a post-mortem with a runbook
update so the next on-call engineer can diagnose
this faster."

**Q3: "Walk me through how you'd set an SLO for
a new API service."**
_Why they ask:_ Tests end-to-end SLO calibration,
a core SRE competency.
_Strong answer:_
"I'd start by defining the SLI: for a request-serving
API, the primary SLI is availability (good requests /
total requests, excluding 4xx). I'd run the service
in production for 30-90 days first without an SLO -
measuring the actual SLI baseline. Then I'd ask the
product team: at what availability level do users
start noticing? This usually comes from UX research
or conversion rate data. The SLO target is set at
the minimum acceptable level - not the aspirational
maximum. If the measured baseline is 99.95% and
users don't notice degradation until below 99.8%,
I'd set the SLO at 99.9% - achievable, meaningful,
with buffer. The SLA is set looser than the SLO -
if SLO is 99.9%, SLA is 99.5%. I'd then write the
error budget policy and multi-window burn rate alerts
before the SLO goes live. Quarterly I'd review:
if the budget is never spent, the SLO may be too
conservative. If it's always exhausted, we need
reliability investment."
