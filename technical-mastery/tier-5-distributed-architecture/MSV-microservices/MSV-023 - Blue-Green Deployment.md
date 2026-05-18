---
id: MSV-023
title: Blue-Green Deployment
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★☆
depends_on: MSV-008, MSV-009, MSV-002
used_by: MSV-067, MSV-068
related: MSV-067, MSV-068, MSV-069, MSV-024, MSV-027
tags:
  - microservices
  - devops
  - intermediate
  - deployment
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Mastery"
nav_order: 23
permalink: /technical-mastery/microservices/blue-green-deployment/
---

⚡ TL;DR - Blue-Green Deployment runs two identical
environments ("blue" = current, "green" = new version).
Traffic switches from blue to green in seconds. Rollback
means switching back: immediate, zero-downtime. It is
the standard pattern for zero-downtime deployments.

| #023 | Category: Microservices | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Health Check Patterns, Readiness and Liveness Probes, Microservices Architecture | |
| **Used by:** | Canary Deployment, Zero-Downtime Deployment | |
| **Related:** | Canary Deployment, Zero-Downtime Deployment, Graceful Shutdown, Feature Flags, Versioning Strategy | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Deployment requires stopping the current version, deploying
the new version, and starting it up. During this window
(typically 1-5 minutes), the service is unavailable.
At 3 AM on a Tuesday: acceptable. On Black Friday at
11 PM: catastrophic.

Even worse: the new version has a bug discovered after
deployment. Rollback means stopping new version, deploying
old version, starting it up - another 1-5 minutes of
downtime. For critical services, every minute of downtime
costs real money.

**THE INVENTION MOMENT:**
Blue-Green Deployment eliminates the unavailability window
entirely. Two identical environments exist simultaneously.
The new version is deployed to the idle environment,
verified, and traffic is switched at the load balancer
(seconds). Rollback: switch traffic back (seconds).
Zero downtime in both directions.

---

### 📘 Textbook Definition

**Blue-Green Deployment** is a release strategy that
maintains two identical production environments:
"Blue" (the current live version) and "Green" (the
new version being deployed). Traffic is served by Blue
while Green is prepared, tested, and verified. When
ready, traffic is switched from Blue to Green at the
load balancer level (or DNS level), making Green the
new live environment. Blue remains idle and serves as
the instant rollback target: if Green has issues,
traffic is switched back to Blue in seconds, with no
redeployment required.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Blue-Green maintains two live environments - current
(blue) and new (green). Switch traffic in seconds.
Rollback = switch back in seconds. Zero downtime.

**One analogy:**
> Painting a bridge without closing it to traffic.
> You build a second bridge (green) next to the first
> (blue). Cars continue using the first bridge while
> the second is built and inspected. Once ready, you
> redirect traffic to the new bridge. If the new bridge
> has a problem: redirect back to the old bridge in
> seconds. The old bridge stays standing until you
> are confident in the new one.

**One insight:**
The key is that "switching traffic" at a load balancer
or Kubernetes service selector takes seconds, while
"deploying and starting a service" takes minutes. Blue-
Green trades the deployment cost (2x infrastructure
at peak) for the benefit of instant switchover and
instant rollback.

---

### 🔩 First Principles Explanation

**BLUE-GREEN MECHANISM:**

```
STATE 1: Blue is live (v1.0)
───────────────────────────────
  Load Balancer ──→  BLUE (v1.0) [live, 100% traffic]
                └──→  GREEN (v1.1) [idle, 0% traffic]

STATE 2: Deploying v1.1 to GREEN
───────────────────────────────
  Deploy v1.1 to GREEN
  Run smoke tests against GREEN (off live traffic)
  Load Balancer ──→  BLUE (v1.0) [live, 100% traffic]
                └──→  GREEN (v1.1) [ready, 0% traffic]

STATE 3: Switch traffic to GREEN (seconds)
───────────────────────────────
  Load Balancer ──→  BLUE (v1.0) [idle, 0% traffic]
                └──→  GREEN (v1.1) [live, 100% traffic]

ROLLBACK (if GREEN has issues, seconds):
───────────────────────────────
  Load Balancer ──→  BLUE (v1.0) [live, 100% traffic]
                └──→  GREEN (v1.1) [idle, 0% traffic]
  ROLLED BACK IN SECONDS - no redeployment
```

**KUBERNETES BLUE-GREEN MECHANISM:**

```yaml
# Service selector switches traffic
apiVersion: v1
kind: Service
metadata:
  name: order-service
spec:
  selector:
    app: order-service
    # Change this label to switch traffic:
    version: blue   # -> change to "green" to switch
  ports:
    - port: 8080

---
# Blue deployment (v1.0)
kind: Deployment
metadata:
  name: order-service-blue
spec:
  selector:
    matchLabels:
      app: order-service
      version: blue  # matches Service selector
---
# Green deployment (v1.1)
kind: Deployment
metadata:
  name: order-service-green
spec:
  selector:
    matchLabels:
      app: order-service
      version: green  # NOT matched by Service yet
# To switch: kubectl patch service order-service
#   -p '{"spec":{"selector":{"version":"green"}}}'
# Takes effect: seconds (Endpoints update)
```

---

### 🧪 Thought Experiment

**BLUE-GREEN WITH DATABASE SCHEMA CHANGES:**

```
THE HARD PROBLEM:
  Order Service v1.0 uses table: orders(id, amount)
  Order Service v1.1 adds column: orders(id, amount,
    customer_tier)
  Both Blue (v1.0) and Green (v1.1) access the same DB

SIMPLE CASE (additive change):
  Add column with DEFAULT
  v1.0: doesn't know about customer_tier (ignores it)
  v1.1: reads and writes customer_tier
  Works: both versions can run simultaneously

HARD CASE (breaking change):
  Rename column: amount -> order_total
  v1.0: reads 'amount' (fails after rename)
  v1.1: reads 'order_total'
  INCOMPATIBLE: cannot run Blue and Green simultaneously
  
  SOLUTION: Expand-Contract (3-phase migration)
  Phase 1: Add 'order_total', keep 'amount' (expand)
    Both v1.0 and new v1.1a can run
  Phase 2: Migrate data, write to both columns
  Phase 3: Remove 'amount' after v1.0 fully removed
    (contract)
  This enables blue-green even for breaking changes
```

---

### 🧠 Mental Model / Analogy

> Blue-Green is like a phone number switchover. Your
> company moves offices. The new office (Green) is set
> up, tested, and fully operational before the move.
> On moving day: call forwarding from old number to new
> office is changed (seconds). If the new office has
> problems: change call forwarding back to old office
> (also seconds). The old office (Blue) stays open for
> one week as a fallback. No customer call is dropped.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Blue-Green keeps two copies of your service running:
the current version and the new version. When the new
version is ready, you flip a switch to send traffic to
it. If something goes wrong, you flip back in seconds.

**Level 2 - How to use it (junior developer):**
In Kubernetes: create Blue and Green Deployments. Keep
one Service that selects by label ("version: blue" or
"version: green"). To deploy: update Green Deployment
with new image, verify health, then `kubectl patch`
the Service to select "version: green".

**Level 3 - How it works (mid-level engineer):**
The switch is a Kubernetes Service label selector update.
Kubernetes control plane updates the Endpoints object
(~1s). kube-proxy on each node updates iptables rules
(~1-3s). All NEW connections route to Green. Existing
long-lived connections (HTTP keep-alive) to Blue drain
naturally over 30-60 seconds. Configure `preStop` hook
or `terminationGracePeriodSeconds` to allow Blue pods
to finish in-flight requests before termination.

**Level 4 - Why it was designed this way (senior/staff):**
Blue-Green's key property is that rollback requires no
artifact retrieval (no pulling old Docker image, no
waiting for pod startup). Blue is already running and
its pods are warm (JVM JIT compiled, connection pools
full). Rollback to Blue is instant. Canary Deployment
is a variation that uses partial traffic switching
(5% to new, 95% to old) for lower-risk validation;
but rollback from a canary still requires removing the
canary instances. Blue-Green is all-or-nothing but
with full instant rollback capability.

**Level 5 - Mastery (distinguished engineer):**
Blue-Green at scale requires database compatibility
strategy. The Expand-Contract pattern: (1) add new
column with backward-compatible default, deploy v1.1
(reads both), (2) run both Blue and Green, (3) remove
old column in v1.2. All three phases are individual
deployments. The entire sequence can take days for
large schemas. This is why "just do blue-green" advice
ignores the schema migration complexity that makes
blue-green hard in practice. For in-flight requests
during switch: Kubernetes graceful termination
(`terminationGracePeriodSeconds=60`) + Spring Boot
`server.shutdown=graceful` drain all in-flight requests
on Blue before pod termination.

---

### ⚙️ How It Works (Mechanism)

**AUTOMATED BLUE-GREEN WITH ARGO ROLLOUTS:**

```yaml
# Argo Rollouts: Blue-Green Rollout spec
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: order-service
spec:
  replicas: 5
  strategy:
    blueGreen:
      # Service receiving production traffic (Blue)
      activeService: order-service-active
      # Service for preview/testing (Green)
      previewService: order-service-preview
      # Auto-promotion after health checks pass
      autoPromotionEnabled: false  # manual approval
      # Keep Blue alive for N seconds after promotion
      scaleDownDelaySeconds: 300
  template:
    spec:
      containers:
        - name: order-service
          image: order-service:v1.1
```

```bash
# Deployment workflow:
# 1. Update image -> Argo creates Green pods
kubectl argo rollouts set image order-service \
  order-service=order-service:v1.1

# 2. Green pods start and pass health checks
# 3. Run smoke tests against preview service
curl http://order-service-preview.svc/health

# 4. Manual promotion: switch traffic to Green
kubectl argo rollouts promote order-service
# Takes 1-3 seconds

# 5. If issues: rollback to Blue (instant)
kubectl argo rollouts abort order-service
# Traffic back to Blue in 1-3 seconds
# Blue pods were kept running (scaleDownDelay=300s)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**COMPLETE BLUE-GREEN PIPELINE:**

```
[1] Trigger: new Docker image pushed

[2] CI Pipeline:
  - Unit + integration tests pass
  - Docker image built, pushed to registry
  - Vulnerability scan passes

[3] CD Pipeline:
  - Deploy new image to GREEN pods
  - Wait for readiness probes on GREEN
  - Run smoke tests against GREEN (preview service)

[4] Approval Gate:
  - Automated: if smoke tests pass -> promote
  - Manual: engineer reviews metrics -> promote

[5] Promotion:
  - Service selector changes (1-3 seconds)
  - GREEN is now live (BLUE idle)
  - Monitor error rate + latency for 10 minutes

[6] Success Path:
  - After 5 minutes healthy: scale down BLUE
  - BLUE kept as rollback for 24 hours
  - Then decommissioned

[7] Failure Path:
  - Error rate spikes: immediate rollback
  - Selector changes back to BLUE (1-3 seconds)
  - BLUE had never stopped (instant)
  - Post-mortem: fix bug in GREEN, repeat from [2]
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: rolling update vs blue-green**

```yaml
# BAD: rolling update - mixed versions during deploy
# Some pods run v1.0, some v1.1 simultaneously
# Client may hit v1.0 then v1.1 inconsistently
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0
# During deployment:
#   3 pods: v1.0, 2 pods: v1.1
# Request 1 -> v1.0 behaviour
# Request 2 -> v1.1 behaviour (different response!)
# For stateful APIs: inconsistent client experience
```

```yaml
# GOOD: blue-green - clean switch, all-or-nothing
# All traffic goes to v1.0 until v1.1 is verified
# Then ALL traffic switches to v1.1 (no mixed state)
strategy:
  blueGreen:
    activeService: order-service-active
    previewService: order-service-preview
    autoPromotionEnabled: false
# During deployment:
#   ALL requests -> v1.0 (BLUE)
#   v1.1 (GREEN) tested in parallel, not live
# After promotion:
#   ALL requests -> v1.1 (GREEN)
# No request ever sees mixed v1.0/v1.1 behaviour
```

---

### ⚖️ Comparison Table

| Strategy | Rollback Time | Cost | Risk | Best For |
|---|---|---|---|---|
| **In-place** | Minutes (redeploy) | Low (1x infra) | High | Dev/staging |
| **Rolling Update** | Minutes (scale down new) | Low (1x infra) | Medium | Stateless, backward-compat APIs |
| **Blue-Green** | Seconds (flip switch) | High (2x infra peak) | Low | Zero-downtime, instant rollback |
| **Canary** | Minutes (remove canary) | Medium (1.1x infra) | Very low | Risk-averse, large-scale systems |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Blue-Green requires 2x permanent infrastructure | Blue-Green requires 2x infra only during the deployment window. After promotion and validation, the old Blue environment is scaled down. In Kubernetes with Argo Rollouts, this is automated. Peak cost = 2x for 5-30 minutes per deployment. |
| Blue-Green handles all database migrations automatically | Blue-Green only handles the application switch. Database schema changes require the Expand-Contract pattern (additive first, remove after old version is gone). This is the most complex part of blue-green in practice. |
| Blue-Green is always better than canary | For small teams with limited monitoring: Blue-Green (simpler, all-or-nothing). For large systems where 1% of traffic hitting a bug means thousands of affected users: Canary (gradual rollout with metrics-based promotion). |

---

### 🚨 Failure Modes & Diagnosis

**In-flight requests lost during traffic switch**

**Symptom:**
After Blue-Green switch, 2% of requests receive
connection reset errors for ~30 seconds after the switch.

**Root Cause:**
Blue pods still have in-flight requests when the Service
selector switches to Green. New connections route to
Green, but existing TCP connections to Blue are still
open. If Blue pods are terminated immediately: in-flight
requests are dropped.

**Fix:**
```yaml
# Spring Boot: graceful shutdown
server.shutdown: graceful
spring.lifecycle.timeout-per-shutdown-phase: 30s
# Waits up to 30s for in-flight requests to complete

# Kubernetes: preStop hook + termination period
lifecycle:
  preStop:
    exec:
      command: ["sleep", "10"]
      # 10s grace for connections to drain
terminationGracePeriodSeconds: 60
# Total: 10s preStop + 30s graceful shutdown + buffer
```

**Diagnostic:**
```bash
# Check for connection reset errors during deploy
kubectl logs -l app=order-service --since=2m | \
  grep -E "connection reset|ECONNRESET"

# Check graceful shutdown is configured
kubectl exec order-service-xxx -- \
  curl -s localhost:8080/actuator/env | \
  jq '.[] | select(.name == "server.shutdown")'
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Health Check Patterns` - Green must pass health
  checks before traffic is switched
- `Readiness and Liveness Probes` - K8s readiness probe
  gates the Blue-Green switch

**Builds On This (learn these next):**
- `Canary Deployment` - partial traffic switch variant:
  send 5% to new version, verify, then promote 100%
- `Zero-Downtime Deployment` - the goal Blue-Green achieves

**Operational:**
- `Graceful Shutdown` - required to drain in-flight requests
  from Blue before pod termination after the switch

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ MECHANISM    │ Service selector label switch (1-3s)     │
│              │ Green = idle until traffic switched      │
├──────────────┼──────────────────────────────────────────┤
│ ROLLBACK     │ Switch selector back to blue (1-3s)      │
│              │ No redeployment - Blue still running     │
├──────────────┼──────────────────────────────────────────┤
│ DB CHALLENGE │ Schema changes: Expand-Contract pattern  │
│              │ Additive change first (backward compat)  │
├──────────────┼──────────────────────────────────────────┤
│ INFRA COST   │ 2x infra peak (for 5-30 min per deploy)  │
│              │ Scale down old env after validation      │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Two envs: flip switch to new, flip back │
│              │  to old in seconds - zero downtime"      │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Canary Deployment → Graceful Shutdown    │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Traffic switch in Kubernetes = label selector change
   (1-3 seconds). Green runs warm alongside Blue before
   the switch.
2. Rollback = switch selector back to Blue (1-3 seconds).
   Blue is still running - no redeployment needed.
3. Database schema changes are the hard part. Use
   Expand-Contract: add new column (backward compat),
   deploy new version, then remove old column.

**Interview one-liner:**
"Blue-Green maintains two identical environments. Current
version (Blue) receives all traffic. New version (Green)
is deployed, health-checked, and smoke-tested against
the preview service. Traffic is switched at the Kubernetes
Service selector (1-3 seconds, zero downtime). Rollback:
switch selector back to Blue (already warm, instant).
Hard part: database schema changes require Expand-Contract
pattern to ensure both versions are database-compatible
during the switch window."

---

### 💡 The Surprising Truth

The most common Blue-Green failure mode is not a bad
deploy - it is a successful deploy followed by an issue
that only manifests under real load. The smoke tests
pass, the switch occurs, and then 20 minutes later,
a memory leak in the new version causes pods to OOMKill.
By this time, the Blue environment has been scaled down
("cleaned up" after 5 minutes of healthy green). Rollback
now requires redeployment of Blue. The lesson: keep Blue
alive for a meaningful observation window (30-60 minutes)
before scaling it down. Configure `scaleDownDelaySeconds:
3600` in Argo Rollouts. The cost of keeping Blue warm
for an hour is much less than an emergency redeployment
at 3 AM.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **IMPLEMENT** Blue-Green Deployment in Kubernetes
   using Service label selectors: two Deployments,
   one Service, label-based switching.
2. **AUTOMATE** Using Argo Rollouts: configure
   autoPromotionEnabled, previewService, scaleDownDelay,
   and rollback trigger.
3. **HANDLE SCHEMA** Given a new deployment that renames
   a database column, design the Expand-Contract 3-phase
   migration that enables Blue-Green compatibility.
4. **DEBUG** Given 2% connection resets after Blue-Green
   switch, identify the root cause (graceful shutdown
   not configured) and implement the fix.
5. **DECIDE** Given a service with stateful sessions
   stored in application memory (not Redis), explain why
   Blue-Green requires session externalisation first.

---

### 🧠 Think About This Before We Continue

**Q1.** Order Service has an in-memory LRU cache of
the 10,000 most popular products (warmed over 30 minutes
at startup). In Blue-Green deployment: Green starts cold
(empty cache). When traffic switches to Green, all
requests miss the cache for 30 minutes, causing 3x load
on the database. Design a strategy to handle this cache
cold-start problem in Blue-Green.

**Q2.** Blue-Green requires both versions (Blue v1.0
and Green v1.1) to be compatible with the same database
schema simultaneously. You need to change the primary
key strategy of the orders table from auto-increment
INT to UUID. Design the Expand-Contract migration
sequence. How many deployments does this require?
What are the risks at each phase?

**Q3.** Compare Blue-Green vs Canary for a payment
service that processes $1M per hour. If the new version
has a bug that causes 2% of payments to fail: (a) with
Blue-Green and a 5-minute observation window, how many
payments fail before rollback? (b) with Canary at 5%
traffic and a 5-minute window, how many fail? (c) which
strategy is more appropriate for this payment service?