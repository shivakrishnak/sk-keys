---
id: ATZ-054
title: "Authorization Observability and Policy Tracing"
category: Authorization
tier: tier-2-networking-security
folder: ATZ-authorization
difficulty: ★★★
depends_on: ATZ-031, ATZ-040, ATZ-050, ATZ-051, ATZ-053
used_by: ATZ-055, ATZ-062
related: ATZ-031, ATZ-051, ATZ-053
tags:
  - security
  - authorization
  - observability
  - tracing
  - advanced
status: complete
version: 5
layout: default
parent: "Authorization"
grand_parent: "Technical Mastery"
nav_order: 54
permalink: /technical-mastery/authorization/authorization-observability-and-policy-tracing/
---

⚡ **TL;DR** - Authorization observability means knowing, in
production: how many access decisions are being made per second,
what percentage are denials, which policies triggered which
denials, and whether a specific user was denied access to a
specific resource at a specific time. OPA produces structured
decision logs for every allow/deny. These logs are the audit
trail for compliance, the signal for detecting attacks (unusual
deny rate = policy misconfiguration or ATO attempt), and the
debugging tool when a user reports "I can't access X."

---

### 📊 Entry Metadata

| #054 | Category: Authorization | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | ATZ-031 Audit Logging, ATZ-040 Distributed Authz, ATZ-050 Enterprise Arch, ATZ-051 Central vs Dist, ATZ-053 Policy-as-Code | |
| **Used by:** | ATZ-055, ATZ-062 | |
| **Related:** | ATZ-031 Decision Logging, ATZ-051 Central vs Distributed, ATZ-053 Policy-as-Code | |

---

### 📘 Textbook Definition

Authorization observability encompasses three capabilities:
decision logging (recording every allow/deny decision with full
context for audit and compliance), metrics (quantitative signals:
decisions per second, deny rate, latency percentiles, policy
evaluation errors), and distributed tracing (correlating an
authorization decision with the request that triggered it and
the policy rules that evaluated it). OPA provides built-in
decision logging: every evaluation produces a JSON log entry
with the input, the decision (allow/deny), the policy rules
that fired, the bundle revision, and a timestamp. These logs
are the primary evidence source for security audits (who accessed
what, when) and incident response (what was the policy state
when the breach occurred?).

---

### ⚙️ How It Works (Mechanism)

```
┌────────────────────────────────────────────────────────┐
│         Authorization Observability Stack              │
├────────────────────────────────────────────────────────┤
│                                                        │
│  METRICS (Prometheus / Datadog):                       │
│  authz_decisions_total{result="allow"}                 │
│  authz_decisions_total{result="deny"}                  │
│  authz_decision_latency_ms{p50, p95, p99}              │
│  authz_policy_errors_total (policy eval failures)      │
│  Alert: deny_rate > 5% (baseline 0.5%) = investigate  │
│                                                        │
│  DECISION LOGS (OPA, JSON per decision):               │
│  {                                                     │
│    "decision_id": "uuid",                              │
│    "timestamp": "2024-01-01T10:00:00Z",               │
│    "input": {userId, resource, action, context},       │
│    "result": {"allow": false},                         │
│    "rules": ["authz.allow", "authz.deny_deleted"],     │
│    "bundle_revision": "v1.2.0",                        │
│    "sidecar": "payment-svc-pod-abc123"                 │
│  }                                                     │
│  Ship to: SIEM (Splunk, Elastic)                       │
│                                                        │
│  TRACING (OpenTelemetry):                              │
│  HTTP request trace -> authz decision span             │
│  Trace ID links request to authz decision              │
│  "Why was user 123 denied at 10:05?" ->                │
│  Find trace -> find authz span -> see policy rule      │
│                                                        │
│  AUDIT QUERIES (compliance):                           │
│  "All actions by user X in last 30 days"               │
│  "All admin access in production last week"            │
│  "All denied requests for resource Y"                  │
│  Requires: decision logs shipped to queryable store    │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Examples

**Example - OPA decision log configuration**

```yaml
# OPA configuration: enable decision logging
# Every authorization decision -> log entry
services:
  # Where to ship decision logs
  decision_logs:
    url: https://log-collector.company.com/v1/logs
    credentials:
      bearer:
        token: "${DECISION_LOG_TOKEN}"

decision_logs:
  console: false   # Don't log to stdout (use service)
  service: decision_logs
  # Mask sensitive fields (never log passwords, tokens)
  mask_decision: ["input.request.headers.authorization"]
  # Soft-limit on log batch size before flushing
  upload_size_limit_bytes: 131072
  # Buffer and upload asynchronously
  # (no impact to decision latency)
  buffer_size_limit_bytes: 1048576

# Decision log JSON entry:
# {
#   "labels": {"app": "payment-svc", "env": "prod"},
#   "decision_id": "uuid",
#   "bundles": {"authz": {"revision": "v1.2.0"}},
#   "path": "authz/allow",
#   "input": { userId, resource, action... },
#   "result": false,
#   "requested_by": "payment-svc-pod-123",
#   "timestamp": "2024-01-01T10:00:00Z",
#   "metrics": {"timer_rego_query_eval_ns": 250000}
# }
```

---

*Authorization category: ATZ | Entry: ATZ-054 | v5.0*