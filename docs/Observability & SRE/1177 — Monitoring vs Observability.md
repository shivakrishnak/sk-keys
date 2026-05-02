---
layout: default
title: "Monitoring vs Observability"
parent: "Observability & SRE"
nav_order: 1177
permalink: /observability/monitoring-vs-observability/
number: "1177"
category: Observability & SRE
difficulty: ★★☆
depends_on: "Observability, Metrics, Logging"
used_by: "SRE, alerting, incident response, capacity planning"
tags: #observability, #monitoring, #alerting, #sre, #metrics, #dashboards
---

# 1177 — Monitoring vs Observability

`#observability` `#monitoring` `#alerting` `#sre` `#metrics` `#dashboards`

⚡ TL;DR — **Monitoring** watches for known failure conditions (pre-defined thresholds, pre-defined questions). **Observability** enables answering arbitrary questions about system behavior, even ones you didn't anticipate. Monitoring catches known unknowns ("is CPU above 90%?"); observability addresses unknown unknowns ("why was this specific user's request slow in this specific way?"). You need both: monitoring to detect, observability to diagnose.

| #1177           | Category: Observability & SRE                       | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------- | :-------------- |
| **Depends on:** | Observability, Metrics, Logging                     |                 |
| **Used by:**    | SRE, alerting, incident response, capacity planning |                 |

---

### 📘 Textbook Definition

**Monitoring**: the practice of collecting predefined metrics and setting alerts on known thresholds to detect known failure modes. Monitoring answers questions defined before deployment: "Alert if: CPU > 90%, error rate > 1%, disk usage > 80%, latency p99 > 1 second." Monitoring is reactive to known failure patterns — it can only alert on conditions you anticipated. **Observability** (see #1176): the property of a system that allows understanding its internal state from external outputs. Observability enables answering questions NOT defined in advance — exploring the system's behavior interactively during an incident. The distinction: monitoring watches **known unknowns** ("I know this metric might go wrong, and I'll watch it"); observability handles **unknown unknowns** ("I don't know what's wrong yet; I need to explore"). In practice: monitoring detects that something is wrong (alert fires); observability diagnoses WHAT is wrong and WHY. Both are necessary: monitoring without observability means you get paged but can't find the root cause; observability without monitoring means you never know there's a problem until a user calls. The Charity Majors framing (Honeycomb): "Monitoring is asking questions you thought to ask ahead of time. Observability is being able to ask questions you didn't know you'd need to ask."

---

### 🟢 Simple Definition (Easy)

Monitoring: you set up an alert — "page me if error rate is above 1%." You get paged. Monitoring detected the problem. Now what? That's where observability comes in: you open your traces, drill into the failing requests, look at logs, find the slow database query. Observability diagnosed the problem. Monitoring says "something is wrong." Observability says "here's exactly what is wrong and why."

---

### 🔵 Simple Definition (Elaborated)

Think of it as a two-phase incident response:

**Phase 1 — Detection (Monitoring)**:

- You have dashboards with key metrics: error rate, latency, throughput
- You have alerts on thresholds: "p99 > 500ms for 5 minutes → PagerDuty"
- An alert fires. You're paged. You know SOMETHING is wrong.

**Phase 2 — Diagnosis (Observability)**:

- You open your observability tool (Jaeger, Honeycomb, Datadog APM)
- You can query: "Show me all requests in the last 10 minutes where latency > 1s"
- You pick a slow request, see its trace: auth=5ms, cart=8ms, inventory=2,100ms ← slow
- You dig into inventory logs at that timestamp: "query took 2,100ms — missing index"
- Root cause found. You didn't need to redeploy or add new instrumentation.

**The key distinction**: monitoring asks pre-defined questions (defined when you set up the alert). Observability lets you ask new questions on the fly during an incident.

**Complementary tools**:
| Tool | Role | Type |
|---|---|---|
| PagerDuty alerts | "Something is wrong" | Monitoring |
| Grafana dashboards | "What's the trend?" | Monitoring |
| Jaeger trace explorer | "What did this request do?" | Observability |
| Loki log exploration | "What happened at 14:23?" | Observability |
| Honeycomb/Datadog APM | "Why are some requests slow?" | Observability |

---

### 🔩 First Principles Explanation

```yaml
# MONITORING: Prometheus alert rules (pre-defined threshold alerts)
# These are the KNOWN UNKNOWNS: "I anticipate these metrics might go wrong"

groups:
  - name: order-service-alerts
    rules:
      # Know Unknown 1: error rate spike
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m])
          / rate(http_requests_total[5m]) > 0.01
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Error rate is {{ $value | humanizePercentage }}"
          runbook: "https://runbooks.company.com/high-error-rate"

      # Known Unknown 2: latency degradation
      - alert: HighLatency
        expr: histogram_quantile(0.99,
          rate(http_request_duration_seconds_bucket[5m])) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "p99 latency is {{ $value | humanizeDuration }}"

      # Known Unknown 3: service down
      - alert: ServiceDown
        expr: up{job="order-service"} == 0
        for: 1m
        labels:
          severity: critical

      # Known Unknown 4: database connection pool exhaustion
      - alert: DBConnectionPoolNearExhaustion
        expr: hikaricp_connections_active / hikaricp_connections_max > 0.8
        for: 3m
        labels:
          severity: warning
```

```java
// OBSERVABILITY: what enables ad-hoc investigation after an alert fires

// The monitoring alert fires: "HighErrorRate on order-service"
// Now the on-call engineer investigates using observability tooling:

// STEP 1: Grafana dashboard (monitoring → overview)
// → error rate chart shows spike started at 14:23
// → which endpoints? → /orders/checkout → 12% errors
// → what HTTP status? → 504 Gateway Timeout

// STEP 2: Jaeger distributed trace search (observability → exploration)
// Query: service=order-service, status=error, time=14:23-14:35
// → Found 847 failed traces
// → Random sample of a failed trace:
//    order-service  checkout()    1,250ms total
//    ├── auth-service  verify()   11ms  ✓
//    ├── cart-service  getCart()   8ms  ✓
//    └── inventory-service  checkStock()  1,230ms  ← SLOW

// STEP 3: Loki log search (observability → root cause)
// Query: {app="inventory-service"} | json | duration_ms > 1000
// → Found: "SELECT * FROM inventory WHERE product_id IN (...)
//           LIMIT 100 [1,230ms] — seq scan on 8M rows"
// → Root cause: migration at 14:21 accidentally dropped index on product_id

// OBSERVABILITY ENABLED:
// Engineer answered questions NOT defined in advance:
// - "Which service was slow in the request chain?"
// - "What specific database query was slow?"
// - "What event preceded the slowness?"
// None of these were in the monitoring alert definitions.
```

```
MONITORING vs OBSERVABILITY COMPARISON:

                    MONITORING              OBSERVABILITY
  ─────────────────────────────────────────────────────────────────
  Purpose           Detect known failures   Diagnose any failure
  Questions         Pre-defined             Ad-hoc, exploratory
  Failure model     Known unknowns          Unknown unknowns
  Output            Alerts                  Insights
  Interaction       Passive (alerts you)    Active (you query)
  Tools             Prometheus, PagerDuty   Jaeger, Loki, Honeycomb
  When useful       "Something is wrong"    "Find out what/why"

  WHEN BOTH ARE NEEDED:
  ─────────────────────────────────────────────────────────────────
  "Monitoring without observability: you get paged but spend
   2 hours finding the root cause."

  "Observability without monitoring: you can diagnose anything
   but you never know there's a problem until a user calls."

  "With both: paged within 2 minutes, root cause in 10 minutes."
```

---

### ❓ Why Does This Exist (Why Before What)

Early web infrastructure was simpler — monoliths on a handful of servers. Monitoring (CPU, disk, process up/down) was sufficient. With microservices, Kubernetes, and distributed systems, monitoring alone fails: a latency problem might be in 1 of 20 services; a cascade of 5 normal-looking metrics might combine to create an outage. The concept of observability emerged to address what monitoring can't: the ability to understand complex distributed system behavior without having anticipated every possible failure mode in advance.

---

### 🧠 Mental Model / Analogy

> **Monitoring is a smoke detector; observability is a forensics team**: a smoke detector (monitoring) tells you there's a fire — it fires the alarm. But it can't tell you where the fire started, what caused it, or how it spread. The forensics team (observability) arrives after the alarm and reconstructs exactly what happened from all available evidence. You need both: the smoke detector to detect the fire quickly, and the forensics capability to understand and prevent future fires.

---

### 🔄 How It Connects (Mini-Map)

```
System is instrumented with telemetry (logs + metrics + traces)
        │
Monitoring: alert fires ─────────┐
        │                        │
        ▼                        ▼
Monitoring vs Observability ◄── (you are here)
(monitoring detects; observability diagnoses)
        │
        ├── Observability: the broader discipline
        ├── Metrics: primary tool for monitoring dashboards and alerts
        ├── Logging: primary tool for observability investigation
        └── Distributed Tracing: the key observability tool for microservices
```

---

### 💻 Code Example

```yaml
# Grafana dashboard combining monitoring (alerts) and observability (exploration)
# alerting_rules.yml defines the monitoring part
# Grafana explore panel enables the observability part

# MONITORING: Grafana alert from Prometheus metric
apiVersion: 1
groups:
  - orgId: 1
    name: order-service
    folder: production
    rules:
      - title: High Error Rate
        condition: C
        data:
          - refId: A
            expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])
        noDataState: NoData
        for: 2m
        annotations:
          summary: "Error rate {{ $values.A | humanizePercentage }}"
          # Link to Grafana explore for OBSERVABILITY investigation
          investigate: >
            {{grafanaUrl}}/explore?datasource=loki&expr={app="order-service"}|json|level="ERROR"
            &from=now-30m&to=now

# The annotation URL takes the on-call engineer from the monitoring alert
# directly into the observability explore panel — pre-filtered to the
# relevant service and time window. This bridges monitoring → observability.
```

---

### ⚠️ Common Misconceptions

| Misconception                            | Reality                                                                                                                                                                                                                                                                                                                                                            |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Observability replaces monitoring        | Observability is complementary to monitoring, not a replacement. Monitoring provides proactive detection (alerts fire when thresholds are crossed). Observability provides reactive investigation (diagnose after detection). A system with observability but no monitoring means you only find out about problems when users report them. You need both.          |
| More dashboards = better monitoring      | Dashboard sprawl is a common anti-pattern: teams create hundreds of dashboards, no one knows which to look at during an incident. Effective monitoring requires discipline: a few key dashboards (RED method: Rate, Errors, Duration) for each service; alerts on actionable metrics only (if the alert fires and there's nothing to do, it shouldn't alert).      |
| Observability is just structured logging | Observability requires all three pillars: logs, metrics, AND traces. Logs alone can't answer "which service in the call chain was slow?" without traces. Metrics alone can't answer "what did this specific failed request do?" without logs and traces. The power of observability comes from the ability to correlate all three signals using a common trace ID. |

---

### 🔗 Related Keywords

- `Observability` — the broader discipline that enables post-alert diagnosis
- `Metrics` — the primary data source for monitoring dashboards and alerts
- `Logging` — key observability tool for event investigation
- `Distributed Tracing` — key observability tool for request path analysis
- `SRE` — SRE practices define how to do monitoring and observability at scale

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ MONITORING: detects known failure conditions           │
│  → Pre-defined thresholds → Alerts → "Something wrong" │
│  Tools: Prometheus, Grafana alerts, PagerDuty          │
│                                                          │
│ OBSERVABILITY: diagnoses any failure                   │
│  → Ad-hoc queries → Exploration → "Why it's wrong"    │
│  Tools: Jaeger, Honeycomb, Datadog APM, Loki           │
│                                                          │
│ INCIDENT FLOW:                                         │
│  Alert fires (monitoring) → Investigate (observability)│
│                                                          │
│ MONITORING = known unknowns                            │
│ OBSERVABILITY = unknown unknowns                       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The RED method (Rate, Errors, Duration) and the USE method (Utilization, Saturation, Errors) are two frameworks for deciding what to monitor. RED is for services (request-oriented): monitor request rate, error rate, and request duration. USE is for infrastructure (resource-oriented): monitor utilization (% busy), saturation (waiting queue), and errors. Design a monitoring strategy for a checkout service: which RED metrics do you alert on? Which USE metrics do you monitor for the underlying infrastructure (CPU, DB, network)? What are the alerting thresholds, and how do you avoid alert fatigue (too many non-actionable alerts)?

**Q2.** Synthetic monitoring (also called "active monitoring" or "external probing") complements internal observability. Instead of only instrumenting the application, synthetic monitoring runs scripted user journeys against production continuously: "every 5 minutes, try to log in, add an item to cart, and checkout." If the synthetic monitor fails, you detect the outage even before real users are affected (or before your internal metrics catch it). Tools: Datadog Synthetic Tests, Checkly, Pingdom. How does synthetic monitoring complement (not replace) internal observability? What are its blind spots — what can synthetic monitoring NOT detect that internal observability can?
