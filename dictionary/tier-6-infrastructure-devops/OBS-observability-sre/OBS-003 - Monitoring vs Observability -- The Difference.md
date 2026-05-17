---
id: OBS-003
title: "Monitoring vs Observability -- The Difference"
category: Observability & SRE
tier: tier-6-infrastructure-devops
folder: OBS-observability-sre
difficulty: ★☆☆
depends_on: OBS-001
used_by: OBS-009, OBS-012
related: OBS-001, OBS-002, OBS-004
tags:
  - observability
  - reliability
  - foundational
  - mental-model
  - devops
status: complete
version: 4
layout: default
parent: "Observability & SRE"
grand_parent: "Technical Dictionary"
nav_order: 3
permalink: /obs/monitoring-vs-observability-the-difference/
---

# OBS-003 - Monitoring vs Observability -- The Difference

⚡ TL;DR - Monitoring checks conditions you anticipated;
observability lets you answer questions you did not know you
would need to ask.

| #003            | Category: Observability & SRE                                                                                 | Difficulty: ★☆☆ |
| :-------------- | :------------------------------------------------------------------------------------------------------------ | :-------------- |
| **Depends on:** | What Is Observability and Why It Matters                                                                      |                 |
| **Used by:**    | Alerting Fundamentals, SLO - Service Level Objective                                                          |                 |
| **Related:**    | What Is Observability and Why It Matters, The Three Pillars of Observability, The Observability Ecosystem Map |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Engineering teams conflate monitoring and observability,
treating them as synonyms. They invest in observability
tooling - Datadog, OpenTelemetry, distributed tracing - but
configure it exactly like monitoring: a fixed set of
dashboards for known failure modes, a fixed set of alerts for
known thresholds. When a genuinely novel failure occurs (a new
database query pattern, a third-party API behaving strangely
under a specific traffic shape), the monitoring approach fails
because the failure was never anticipated. The tools are
expensive; the insight is absent.

**THE BREAKING POINT:**
The fundamental limit of monitoring is the known-unknown
boundary. Monitoring answers questions you thought to ask
before an incident. But the most expensive production failures
are unknown unknowns - failure modes no one anticipated. A
monitoring-only organisation discovers these from user
complaints, not proactive detection.

**THE INVENTION MOMENT:**
This is exactly why the distinction between monitoring and
observability was articulated - to help teams recognise that
they need both: monitoring for known failure patterns and
SLO-based alerting, observability for diagnosing the novel
failures that monitoring cannot anticipate.

**EVOLUTION:**
"Monitoring" has been a defined practice since the 1990s -
Nagios (1999) was the canonical tool. Observability entered
software engineering vocabulary around 2017, popularised by
Charity Majors and the honeycomb.io blog. The 2016 Google SRE
book used both terms. By 2020, most observability vendors were
marketing their tools as "modern monitoring" - obscuring the
distinction rather than clarifying it.

---

### 📘 Textbook Definition

**Monitoring** is the practice of collecting and analysing a
predefined set of signals and alerting when those signals cross
predefined thresholds. It answers questions that were
anticipated before the incident.

**Observability** is the property of a system that enables
engineers to answer arbitrary questions about its internal
state from external signals alone, including questions not
anticipated at instrumentation time. It answers questions
that were not anticipated before the incident.

The key distinction: monitoring is reactive to known failure
modes; observability enables diagnosis of unknown failure
modes.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Monitoring tells you when something breaks; observability
tells you why anything breaks, including failures you did
not predict.

> A weather monitoring station measures temperature, humidity,
> and wind speed - all anticipated variables. It alerts when
> temperature drops below freezing. If a new atmospheric
> phenomenon occurs that is not temperature, humidity, or wind,
> the station cannot detect it. An observable weather system
> would let scientists query any raw signal combination to
> discover new phenomena they had not previously measured.

**One insight:**
The difference is not in the tools - it is in the questions
you can ask. Monitoring limits you to the questions you thought
of in advance. Observability lets you ask questions you did
not know you would need until the incident is happening.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Monitoring requires a complete enumeration of possible
   failure modes before deployment - it can only check what
   was anticipated
2. Observability requires no advance knowledge of failure modes
   - raw signals enable arbitrary post-hoc queries
3. Both monitoring and observability are necessary: SLO-based
   alerting (monitoring) plus arbitrary diagnosis (observability)
4. The practical difference: can you ask a question you did
   not pre-build a dashboard for?

**DERIVED DESIGN:**
Monitoring is implemented as: "check if X > threshold, alert
if true." This scales well for known failure patterns and is
cheap to implement. Observability is implemented as: "emit
structured, high-cardinality signals that can be queried in
any combination after the fact." This scales less well for
cost but scales infinitely for question space.

A production system needs both: monitoring for known failure
patterns (fast alerts and rehearsed runbooks) and observability
for novel failures (investigative debugging).

**THE TRADE-OFFS:**
**Monitoring Gain:** Fast alert on known failures. Low storage
cost. Simple mental model. Predictable tooling cost.
**Monitoring Cost:** Blind to unanticipated failures. Alert
fatigue when thresholds are set arbitrarily. Cannot diagnose
beyond pre-configured dimensions.

**Observability Gain:** Can answer any diagnostic question,
including questions about failures never seen before.
**Observability Cost:** Requires structured, high-cardinality
signals (expensive to store). Requires query skill. Does not
replace alerting - you still need monitoring to detect
problems proactively.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** The known-unknown distinction is fundamental.
Some failure modes can be anticipated; others cannot. Any
engineering practice that ignores this is incomplete.
**Accidental:** The conflation of "monitoring tool" and
"observability tool" in vendor marketing. Nagios is a
monitoring tool. Honeycomb is an observability tool. Datadog
can be configured as either.

---

### 🧪 Thought Experiment

**SETUP:**
Two teams run identical microservices. Team A uses monitoring
(threshold-based alerts). Team B uses observability (structured
signals, ad-hoc queries). A new failure mode emerges: a
specific combination of user geography, product category, and
traffic pattern causes a database deadlock. This failure was
never anticipated.

**WHAT HAPPENS WITH MONITORING ONLY (Team A):**
No alert fires initially - deadlocks are not in the threshold
configuration. Users start complaining. Eventually, the error
rate crosses the 2% threshold and an alert fires. The on-call
engineer checks pre-built dashboards: CPU fine, memory fine,
error rate 2.3%. They add more instances. Deadlocks continue.
Root cause identified only after 2 hours of manual database
investigation with `SHOW PROCESSLIST`.

**WHAT HAPPENS WITH OBSERVABILITY (Team B):**
No alert fires initially (same). Users start complaining. But
the engineer queries the trace store by
`status=error AND error.type=DeadlockException`. Every
affected trace shares: `user.region=EU`,
`product.category=electronics`, and high concurrency. They
immediately query the database trace spans for those traces
and see two queries locking each other. Root cause identified
in 12 minutes from signals that existed in the system before
any alert was ever configured.

**THE INSIGHT:**
Monitoring requires pre-enumerating the question. Observability
lets you ask the question after the incident starts. The
failure mode does not need to have been anticipated.

---

### 🧠 Mental Model / Analogy

> A smoke detector (monitoring) alerts you when smoke is
> present - a condition you anticipated and configured it
> to detect. It cannot tell you what is burning, where the
> fire started, or why it spread. A fire investigator
> (observability) arrives and answers arbitrary questions:
> what caused ignition, which path did the fire take, what
> accelerated it? The investigator needs evidence. Without
> evidence collection before the fire, no investigation is
> possible.

Mapping:

- "Smoke detector threshold" - monitoring alert threshold
- "Pre-set condition: smoke present" - anticipated failure mode
- "Fire investigator" - on-call engineer using observability
- "Physical evidence at the scene" - structured system signals
- "Post-hoc investigation questions" - ad-hoc queries against
  observability data

**Where this analogy breaks down:** A fire leaves physical
evidence regardless of preparation. Software systems only
emit the signals they were instrumented to emit. Unlike a
fire scene, you cannot collect evidence that was never
recorded.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Monitoring is a set of rules: "alert if CPU > 80%."
Observability is the ability to ask any question: "why is
this specific user's request slow?" Monitoring checks what
you expected could go wrong; observability handles what you
did not expect.

**Level 2 - How to use it (junior developer):**
Set up monitoring for your SLOs: error rate, latency P99,
and saturation. Set up observability by emitting structured
logs, metrics with business labels, and distributed traces.
Use monitoring for alerting and dashboards. Use observability
when an incident does not match a known pattern.

**Level 3 - How it works (mid-level engineer):**
Monitoring is a whitelist of questions: `IF error_rate > 0.5%
FOR 5 minutes THEN alert`. It is stateful (tracks whether a
condition is active) and generates events (alert fires, alert
resolves). Observability is a capability: structured signals
exist and a query engine lets you explore them. The query is
invented at incident time, not at design time.

**Level 4 - Why it was designed this way (senior/staff):**
Monitoring evolved from simple uptime checks in an era of
monolithic, well-understood systems. Observability emerged
from the complexity of distributed systems where the
cardinality of failure modes is effectively unbounded. Neither
replaces the other: monitoring provides fast alerting for
high-probability failures; observability enables diagnosis
when the alert fires for an unanticipated reason.

**Level 5 - Mastery (distinguished engineer):**
The expert recognises that the monitoring/observability
boundary is also a cultural boundary. Monitoring-only
organisations build runbooks for every known alert and
escalate when none applies. Observability-mature organisations
build engineers who can investigate freely, form hypotheses,
and test them using system signals. The transition requires
both tooling investment and engineering culture change.
The hardest part is not adding Jaeger or OpenTelemetry -
it is teaching engineers to think in hypotheses rather than
runbooks.

**EXPERT THINKING CUES:**

- Red flag: "we have dashboards for everything" - this
  describes monitoring, not observability. Observability is
  the ability to ask questions that no dashboard covers.
- The test: "could you diagnose a failure you have never
  seen before, using only your current signals?" If no,
  you have monitoring but not observability.
- At scale, the most valuable investment is often not
  better alerting (monitoring) but better signal cardinality
  (observability) - the ability to filter any incident to
  a specific code path, user cohort, or feature flag.

---

### ⚙️ How It Works (Mechanism)

**How monitoring works:**

1. Define checks: metrics to poll, thresholds to test,
   health endpoints to probe
2. A monitoring agent polls these at intervals (Nagios,
   Prometheus alerting rules)
3. When a check fails (value crosses threshold), an alert
   event is generated
4. Alert is routed (PagerDuty, Slack) to an on-call engineer
5. Engineer consults runbook: pre-defined steps for this alert

**How observability works:**

1. Instrument code to emit structured, high-cardinality
   signals at all interesting points
2. Collect and store signals in queryable backends
3. During an incident, engineer forms a hypothesis
4. Engineer queries signals ad-hoc to test the hypothesis
5. New hypothesis formed from results - iterative investigation
6. No runbook required - the investigation is data-driven

```
┌─────────────────────────────────────────┐
│  Monitoring vs Observability Workflow   │
├─────────────────────────────────────────┤
│                                         │
│  MONITORING:                            │
│  Define check → Poll → Compare → Alert  │
│  [Known failure mode required]          │
│                                         │
│  OBSERVABILITY:                         │
│  Instrument → Collect → Store → Query  │
│  [Any failure mode diagnosable]         │
│                                         │
│  BEST PRACTICE: USE BOTH               │
│  Monitoring: known-failure alerting    │
│  Observability: unknown-failure debug  │
│                                         │
└─────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (incident response using both):**

```
[Metric alert fires: checkout_errors > 0.5%]
    ↓
[Engineer checks monitoring dashboard]
    ↓
[Known pattern? YES → Follow runbook → Resolve]
    ↓
[Known pattern? NO → Switch to observability]
    ↓
[Query trace store: filter by error type + time window]
    ↓
[Service B ← YOU ARE HERE: identify which spans fail]
    ↓
[Correlate: trace to log to metric - find common attribute]
    ↓
[Root cause identified - fix deployed]
```

**FAILURE PATH (monitoring-only):**
Alert fires. Runbook does not match. Engineer checks all
pre-built dashboards. None show the cause. Incident escalates.
Senior engineer SSHes into server and manually inspects
processes. Root cause found through heroics, not systematic
investigation.

**WHAT CHANGES AT SCALE:**
At scale, the number of novel failure modes grows faster than
the number of runbooks. The monitoring-first approach becomes
a maintenance burden. SLO-based monitoring combined with
observability for investigation becomes the dominant pattern.

---

### 💻 Code Example

**Example 1 - BAD: Monitoring-only alert configuration:**

```yaml
# BAD: fixed threshold alerts
# Cannot diagnose any failure outside these conditions
groups:
  - name: checkout
    rules:
      - alert: CheckoutErrorRateHigh
        expr: rate(checkout_errors_total[5m]) > 0.01
        # Problem: fires for ALL error types equally
        # No ability to investigate WHICH errors or WHY
      - alert: CheckoutLatencyHigh
        expr: checkout_duration_p99 > 1.0
        # Problem: no context about cause of latency
```

**Example 2 - GOOD: SLO-based monitoring + observability:**

```yaml
# GOOD: SLO burn rate alert (monitoring layer)
groups:
  - name: checkout-slo
    rules:
      - alert: CheckoutErrorBudgetBurning
        expr: |
          rate(checkout_errors_total[1h])
            / rate(checkout_requests_total[1h])
            > 5 * (1 - 0.999)
        annotations:
          runbook: "Query traces: status=error, last 1h"
```

```java
// GOOD: low-cardinality labels for monitoring
checkoutErrors.add(1, Attributes.of(
    AttributeKey.stringKey("status"), errorCode,
    AttributeKey.stringKey("region"), region
));

// High-cardinality attributes for observability
// (trace spans - not metric labels)
span.setAttribute("user.cohort",     cohort);
span.setAttribute("feature.flag",    featureFlag);
span.setAttribute("product.category", category);
```

---

### ⚖️ Comparison Table

| Dimension              | Monitoring           | Observability           |
| ---------------------- | -------------------- | ----------------------- |
| **Question type**      | Pre-defined (known)  | Arbitrary (any)         |
| **Alert trigger**      | Threshold breach     | SLO burn rate           |
| **Investigation**      | Runbook-driven       | Hypothesis-driven       |
| **Failure coverage**   | Known modes only     | Any failure mode        |
| **Tooling cost**       | Low-medium           | Medium-high             |
| **Signal cardinality** | Low                  | High                    |
| **Best for**           | SLO tracking, uptime | Novel failure diagnosis |

**How to choose:** You need both. SLO-based monitoring for
alerting. Observability for investigation. They are complements,
not alternatives.

---

### ⚠️ Common Misconceptions

| Misconception                             | Reality                                                                                                                                                                         |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Observability replaces monitoring         | They serve different purposes. Monitoring for fast, reliable SLO alerting. Observability for diagnosing unanticipated failures. Both required.                                  |
| More dashboards equals more observability | Dashboards are a monitoring artefact. Observability is the ability to ask questions that no dashboard covers.                                                                   |
| APM tools provide observability           | APM tools provide application performance monitoring - pre-defined performance metrics. True observability requires high-cardinality, ad-hoc queryable signals.                 |
| Observability is only for large teams     | The principles apply at any scale. A small team benefits from structured logs and basic tracing proportionally to system complexity.                                            |
| Monitoring is obsolete                    | SLO-based alerting is still the industry standard for triggering incident response. Observability without alert thresholds means relying on user complaints to detect problems. |

---

### 🚨 Failure Modes & Diagnosis

**Alert fatigue from threshold-based monitoring**

**Symptom:**
Hundreds of alerts fire weekly, most acknowledged and silenced
without investigation. Engineers stop responding to
low-priority alerts. A real P1 incident fires alongside 300
low-priority alerts and is missed for 2 hours.

**Root Cause:**
Monitoring configured with arbitrary CPU, memory, and latency
thresholds not tied to user-visible impact. Every metric has
an alert. Most are noise.

**Diagnostic Command:**

```bash
# Count alerts by firing frequency (Alertmanager API)
curl -s localhost:9093/api/v2/alerts \
  | jq 'group_by(.labels.alertname)
  | map({
      name: .[0].labels.alertname,
      count: length
    })
  | sort_by(-.count) | .[0:20]'
```

**Fix:**
Replace arbitrary threshold alerts with SLO burn rate alerts.
Every alert must be tied to a user-visible SLO and require
immediate human action.

**Prevention:**
For every alert, ask: "Does this require immediate action?
What is the runbook?" If no runbook exists, the alert should
not page.

---

**Monitoring-only misses novel failure mode**

**Symptom:**
Users report slowness. All monitoring dashboards show green.
No alerts fired. Engineers have no starting point for
investigation.

**Root Cause:**
The failure mode was not anticipated when monitoring was
configured. No threshold covers the affected code path.

**Diagnostic Command:**

```bash
# Without observability, only manual server inspection
# is available - this is the monitoring-only failure state
ssh prod-server-1 "top -b -n 1 | head -20"
# No structured data to answer specific questions
# This is the exact problem observability solves
```

**Fix:**
Add structured signal emission. Then add an SLO-based alert
so future occurrences are detected proactively.

**Prevention:**
Design instrumentation to emit high-cardinality signals
(business attributes, user cohort, feature flags) in
structured logs and trace spans. Even unanticipated failures
can be investigated after the fact.

---

**Exposed monitoring endpoints - security vulnerability**

**Symptom:**
Prometheus `/metrics` endpoint is publicly accessible.
External attackers enumerate internal service names,
hostnames, queue depths, and business metrics. Security
audit finds sensitive operational data exposed.

**Root Cause:**
Monitoring exporters and health check endpoints deployed
without network-level or authentication controls.

**Diagnostic Command:**

```bash
# Test if Prometheus metrics endpoint is publicly exposed
curl -s https://your-public-domain.com/metrics | head -20
# If this returns Prometheus metrics, it is misconfigured

# Check for unauthenticated Spring Boot actuator
curl -s https://your-service.com/actuator/prometheus
```

**Fix:**

```yaml
# Restrict Prometheus scrape to internal monitoring namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-prometheus-scrape
spec:
  podSelector:
    matchLabels: { app: checkout }
  ingress:
    - from:
        - namespaceSelector:
            matchLabels: { name: monitoring }
      ports:
        - port: 9090
          protocol: TCP
```

**Prevention:**
Monitoring endpoints must never be exposed to the public
internet. Use NetworkPolicy in Kubernetes or security groups
in AWS for all observability endpoints.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `What Is Observability and Why It Matters` - understanding
  observability as a concept is required before understanding
  how it differs from monitoring

**Builds On This (learn these next):**

- `Alerting Fundamentals` - how SLO-based alerting bridges
  monitoring and observability for production alert design
- `SLO (Service Level Objective)` - the bridge between
  monitoring thresholds and observability; you monitor burn
  rate against the SLO, then use observability to debug
- `The Observability Ecosystem Map` - the full tool landscape
  for both monitoring and observability approaches

**Alternatives / Comparisons:**

- `The Three Pillars of Observability (Logs, Metrics, Traces)` -
  the three signal types implement observability and are also
  used by monitoring (metrics for alerts)
- `Alerting Anti-Patterns (Alert Fatigue)` - what happens when
  monitoring is misconfigured and observability is absent

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ The distinction between checking known    │
│              │ conditions vs answering any question      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Teams use observability tools configured  │
│ SOLVES       │ as monitoring - missing novel failures    │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Monitoring = anticipated failures.        │
│              │ Observability = unanticipated failures.   │
│              │ Both required.                            │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Monitoring: alerting on SLO burn rate.    │
│              │ Observability: investigating unknown root │
│              │ cause after the alert fires               │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Treating observability as a replacement   │
│              │ for monitoring or vice versa              │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Buying Datadog but configuring only       │
│              │ fixed-threshold alerts - expensive        │
│              │ monitoring, not observability             │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Monitoring: fast/cheap/limited.           │
│              │ Observability: powerful/expensive.        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Monitoring asks your pre-written         │
│              │  questions. Observability lets you        │
│              │  ask the question that matters now."      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ SLO → Alerting Fundamentals → Tracing     │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Monitoring checks pre-defined conditions (known failure
   modes). Observability enables any query (unknown failure
   modes). Neither replaces the other.
2. The test: "could you diagnose a failure you have never
   seen before using only your current signals?" Yes =
   observable. No = monitoring-only.
3. SLO-based alerting is the bridge: alert on burn rate
   (monitoring), then use ad-hoc trace and log queries
   to find root cause (observability).

**Interview one-liner:**
"Monitoring checks conditions you anticipated before an
incident. Observability lets you answer questions you did not
anticipate. In practice: monitoring for SLO-based alerting,
observability for root cause investigation when the alert
fires for an unexpected reason."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Complex systems need both reactive detection (monitoring) and
exploratory diagnosis (observability). Designing only for
anticipated failure modes leaves you blind to novel failures
that are often the most expensive. Designing only for
exploration without detection means relying on users to report
problems before you detect them.

**Where else this pattern appears:**

- **Security operations** - intrusion detection systems
  (monitoring: known attack signatures) vs security
  information and event management (observability: ad-hoc
  forensic investigation). Both required.
- **Medical diagnostics** - routine vital sign monitoring
  (monitoring: predefined parameters) vs differential
  diagnosis (observability: systematic investigation of an
  unknown condition).
- **Financial risk** - value-at-risk models (monitoring:
  known risk scenarios) vs stress testing (observability:
  exploring unknown extreme scenarios).

**Industry applications:**

- **E-commerce SRE** - SLO-based monitoring fires the alert;
  distributed tracing and structured logs answer the
  investigation. Black Friday incidents are diagnosable in
  minutes because both layers are in place.
- **Healthcare IT** - EHR systems use monitoring for known
  system failures and compliance alerts, plus observability
  for diagnosing intermittent data quality issues that never
  match a predefined alert pattern.

---

### 💡 The Surprising Truth

The most dangerous failure mode in modern observability
practice is not lack of tooling - it is conceptual confusion.
Teams that buy Datadog or Honeycomb but configure them exactly
like Nagios (fixed thresholds, fixed dashboards, fixed
runbooks) have paid for observability and received only
expensive monitoring. The tool does not determine the
practice; the engineering culture does. The hardest part of
moving from monitoring to observability is teaching engineers
to think in hypotheses: "I believe the problem is X, here is
how I will query the system to test that belief." That skill
cannot be packaged into a SaaS product.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. **[EXPLAIN]** Describe to a non-technical manager why
   "buying Datadog" does not automatically give the team
   observability, and what additional investment is required.
2. **[DEBUG]** Given a production incident where all monitoring
   dashboards show green but users are complaining, describe
   your first three queries to investigate using observability
   signals.
3. **[DECIDE]** For a new SLO (99.9% checkout success rate),
   design both the monitoring component (what alert fires,
   when) and the observability component (what signals exist
   to investigate when the alert fires).
4. **[BUILD]** Write one Prometheus alerting rule that is
   SLO-based (burn rate) rather than threshold-based, and
   explain why it is better than a fixed `error_rate > 0.5%`
   threshold.
5. **[EXTEND]** Apply the monitoring/observability distinction
   to a CI/CD pipeline. What is the monitoring component?
   What is the observability component? What signals would
   implement both?

---

### 🧠 Think About This Before We Continue

**Q1.** You have a service with SLO-based monitoring and full
distributed tracing. The monitoring fires an alert: P99
latency exceeded 2 seconds for 10 minutes. You open the
traces and see all slow traces are from a single user segment:
free-tier accounts. Paid accounts are unaffected. This
behaviour matches no runbook. Walk through how you would use
observability to determine whether this is a deployment
regression, a resource contention issue between account tiers,
or a data quality issue affecting free-tier records.
_Hint: Think about what attributes would be present on the
slow traces that are absent from fast traces. Which service
hosts the tier-differentiation logic?_

**Q2.** A team argues they can replace their monitoring setup
with a single "golden metric" - a composite score from 0 to
100 representing system health - replacing all individual
alerts. Evaluate this against the monitoring/observability
distinction. What does it get right? What does it
fundamentally misunderstand?
_Hint: Consider what happens when the golden metric score
drops but the composite formula obscures which component
changed. Is this monitoring, observability, or neither?_

**Q3.** Design both monitoring and observability layers for
a real-time fraud detection service processing 1,000
transactions per second. False positive rate (legitimate
transactions flagged as fraud) and false negative rate
(fraud allowed through) are both SLOs. Define: two
SLO-based monitoring alerts and three observability signals
that would help diagnose unexpected changes in either rate.
_Hint: Which signals would let you determine whether a rate
change is caused by a model change, a data drift, or a
system configuration change?_

---

### 🎯 Interview Deep-Dive

**Q1: "What is the difference between monitoring and
observability? Give an example of a failure that monitoring
would miss but observability would catch."**
_Why they ask:_ Tests conceptual depth - whether the candidate
understands the fundamental distinction, not just tool names.
_Strong answer includes:_

- Monitoring checks pre-defined conditions (anticipates failure
  modes); observability enables any query post-hoc
- Example: database deadlock caused by a new feature flag
  combination never anticipated - no threshold exists for it;
  traces show the exact query pair locking each other
- Both are needed: monitoring for fast SLO-based alerting,
  observability for investigation when no runbook matches
- Key test: "could you diagnose this failure without a
  runbook?" Yes = observable; No = monitoring-only

**Q2: "Your team uses Datadog. A senior engineer says,
'We have Datadog, so we have observability.' Do you agree?"**
_Why they ask:_ Tests whether the candidate understands that
observability is a system property, not a tool property.
_Strong answer includes:_

- Datadog is a tool; observability is a property of how the
  system is instrumented
- You can have Datadog and be unobservable if signals are
  unstructured, uncorrelated, or low-cardinality
- The question is: can you ask arbitrary questions? Show me
  all requests for this user in the last hour, correlated to
  traces and logs - can Datadog answer that with your current
  instrumentation?
- Observability requires structured signals, trace IDs in
  logs, high-cardinality trace attributes, and ad-hoc query
  capability - Datadog enables all of these, but only if
  instrumented correctly

**Q3: "When would threshold-based monitoring be correct
over SLO-based monitoring? Give a concrete example."**
_Why they ask:_ Tests whether the candidate knows when simpler
approaches are right, not just when to apply modern SRE
practices.
_Strong answer includes:_

- Threshold-based is appropriate for infrastructure alerts
  where user impact is direct and immediate: disk full at 95%
  will cause service crash within minutes regardless of
  current error budget state
- SLO-based is better for application-layer quality signals
  where user impact is proportional and burn rate matters more
  than instantaneous value
- Example of correct threshold: disk at 95% (file writes will
  fail imminently, action required immediately)
- Counter-example: error rate at 1.2% vs SLO of 99.9% - the
  correct alert is burn rate, because 1.2% sustained for one
  hour burns far more budget than 5% for two minutes

> Entry stub. Generate full content using Master Prompt v3.0.
