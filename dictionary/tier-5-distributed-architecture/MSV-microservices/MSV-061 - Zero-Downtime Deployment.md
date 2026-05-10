---
layout: default
title: "Zero-Downtime Deployment"
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 61
permalink: /microservices/zero-downtime-deployment/
id: MSV-066
category: Microservices
difficulty: ★★★
depends_on: Graceful Shutdown (Microservices), Health Check (Microservices), Backward Compatibility
used_by: Canary Deployment (Microservices), Blue-Green Deployment, Feature Flags (Microservices)
related: Graceful Shutdown (Microservices), Canary Deployment (Microservices), Blue-Green Deployment
tags:
  - microservices
  - deployment
  - operations
  - deep-dive
status: complete
version: 1
---

# MSV-064 - Zero-Downtime Deployment

⚡ TL;DR - Zero-downtime deployment is a deployment strategy that updates a running service without any interruption in availability - users never experience errors or service unavailability during the deployment window.

| #673            | Category: Microservices                                                                     | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------------------ | :-------------- |
| **Depends on:** | Graceful Shutdown (Microservices), Health Check (Microservices), Backward Compatibility     |                 |
| **Used by:**    | Canary Deployment (Microservices), Blue-Green Deployment, Feature Flags (Microservices)     |                 |
| **Related:**    | Graceful Shutdown (Microservices), Canary Deployment (Microservices), Blue-Green Deployment |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your team deploys every Friday night at midnight to minimise impact. A deploy window of 4 hours is scheduled. During this window, users see: "Service temporarily unavailable. We'll be back shortly." This is accepted as normal. Over a year: 52 × 4 hours = 208 hours of downtime = 97.6% uptime. SLA commitments of 99.9% (8.7 hours/year) are impossible to meet.

**THE BREAKING POINT:**
Modern services must support continuous deployment (multiple deploys per day) without scheduled maintenance windows. This requires every deployment to be invisible to users - no downtime, no errors, no degraded experience.

**THE INVENTION MOMENT:**
Zero-downtime deployment is not a single technique - it's the outcome of applying several techniques together: rolling updates (replace pods incrementally); graceful shutdown (drain in-flight requests before pod termination); health checks (only route traffic to ready pods); backward-compatible changes (old and new versions coexist safely).


**EVOLUTION:**
Zero-downtime deployment became an industry goal as continuous delivery (Jez Humble and David Farley, 2010) pushed deployment frequency from monthly to daily to continuous. Traditional maintenance windows became incompatible with 24/7 global services. Rolling updates (Kubernetes' default), blue-green, and canary deployments all emerged as mechanisms for zero-downtime change. The discipline evolved from 'deploy during scheduled maintenance windows' to 'deployment is a daily operation that users should never notice.'
---

### 📘 Textbook Definition

**Zero-downtime deployment** is the practice of updating a service from one version to another without any period during which the service is unavailable or returns errors to clients. It is achieved by the combination of: (1) **rolling update** or **blue-green switching** - gradually replacing old instances with new ones; (2) **graceful shutdown** - old instances drain in-flight requests before terminating; (3) **readiness probes** - new instances only receive traffic after they are confirmed ready; (4) **backward compatibility** - old and new versions of the service and its database schema coexist during the transition period.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Replace old service instances with new ones so smoothly that users never notice a transition.

**One analogy:**

> Replacing the floor tiles in a busy airport terminal, one tile at a time, without closing the terminal. While workers replace one tile, passengers walk around it. When that tile is complete, the next is replaced. The terminal never closes; passengers always have a path.

**One insight:**
Zero-downtime is a system-level property, not a single feature. It requires the application, the deployment pipeline, the infrastructure, and the database migration strategy to all be designed to support simultaneous running of multiple service versions.

---

### 🔩 First Principles Explanation

**THE FOUR PILLARS:**

**Pillar 1 - Rolling Update:**

```
Before: 5 pods running v1 (all serving traffic)
        v1 v1 v1 v1 v1

Step 1: Terminate 1 old pod (gracefully); start 1 new pod (v2)
        Wait: v2 pod passes readiness check
        v1 v1 v1 v1 [v2]

Step 2: Terminate 1 old pod; start 1 new pod
        v1 v1 v1 [v2] [v2]

...until:
Step 5: v2 v2 v2 v2 v2  (deployment complete)
```

**Pillar 2 - Graceful Shutdown:**
When v1 pod is terminated, it: (a) stops accepting new requests; (b) completes all in-flight requests; (c) releases resources; (d) exits. No request is dropped.

**Pillar 3 - Readiness Probes:**
v2 pods only receive traffic after readiness probe passes. The probe checks: application is started, database connections are established, warm-up is complete. Without readiness probes, traffic is sent to v2 pods before they are ready → errors.

**Pillar 4 - Backward Compatibility:**
During rolling update, v1 and v2 pods coexist. They:

- Share the same database → database schema must be compatible with both v1 and v2
- Consume the same Kafka topics → message format must be compatible with both versions
- Call each other's APIs → API changes must be backward-compatible

**THE EXPAND-CONTRACT PATTERN (for database migrations):**

```
Goal: rename column `order_ts` to `created_at`

Naive approach (breaks zero-downtime):
  Deploy migration: ALTER TABLE orders RENAME COLUMN order_ts TO created_at;
  v1 pods (still running): SELECT order_ts → ERROR (column gone)
  RESULT: downtime during migration

Expand-contract approach:
  Phase 1 (expand):
    Migration: ADD COLUMN created_at (copy data from order_ts)
    Deploy v2: writes to BOTH columns; reads from created_at
    v1: reads from order_ts ← still works
    v2: reads from created_at ← works

  Phase 2 (contract - after all v1 pods are gone):
    Migration: DROP COLUMN order_ts
    v2: only uses created_at ← works
```

**THE TRADE-OFFS:**
**Gain:** Service always available; continuous deployment possible; no maintenance windows; SLA commitments achievable.
**Cost:** Database migrations are more complex (expand-contract adds phases); API changes must be backward-compatible; deployment takes longer (rolling update + drain time per pod); configuration and testing overhead; requires robust readiness probes.

---

### 🧪 Thought Experiment

**SETUP:**
Rolling update: 5 pods. During the update, pods 1-3 are v2, pods 4-5 are v1. A request comes in that is load-balanced to pod 3 (v2). v2's new feature writes a new field (`estimatedDelivery`) to the database. Pod 5 (v1) reads the same order record. v1 doesn't know about `estimatedDelivery`. What happens?

**SCENARIO A - v1 uses SELECT \* and maps via ORM:**
ORM sees an unexpected column. Depending on ORM config: (a) ignores it (safe) or (b) throws MappingException (breaks). If (b): every order created by v2 causes errors on v1 pods.

**SCENARIO B - v1 SELECT explicitly lists columns:**
`SELECT id, total, status FROM orders` - `estimatedDelivery` not listed → ignored → no error.

**THE LESSON:**
During zero-downtime deployments, new database columns must be: (a) added as nullable with defaults (so old inserts still work); (b) ignored gracefully by old code (ORM should not fail on unknown columns). The ORM must be configured with `@JsonIgnoreProperties(ignoreUnknown = true)` or equivalent.

---

### 🧠 Mental Model / Analogy

> Zero-downtime deployment is like replacing a bridge while cars are still driving over it. You don't close the bridge (downtime). Instead: you add a parallel lane (new pods start); redirect some traffic to the parallel lane (readiness passes); drain traffic from the old lane (graceful shutdown); remove the old lane (pod terminates). At all times, cars cross the bridge. The old and new lanes must be compatible in width (backward compatibility).

- "Bridge" → service
- "Parallel lane" → new pod version
- "Redirect traffic" → readiness probe passes
- "Drain old lane" → graceful shutdown
- "Lane width must match" → backward compatibility of API/DB schema
- "Cars always cross" → no downtime

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Upgrading your service without stopping it. Users never see a "service down" message. New versions are deployed one pod at a time while the service stays up throughout.

**Level 2 - Kubernetes rolling update (junior developer):**
Kubernetes rolling update is configured via `strategy.rollingUpdate.maxUnavailable` and `maxSurge`. With `maxUnavailable: 0, maxSurge: 1`, Kubernetes starts 1 extra pod (v2) before terminating any old pod (v1). At all times, the full pod count is running. Readiness probe gates the traffic switch.

**Level 3 - Database migration discipline (mid-level engineer):**
The hardest part of zero-downtime is database changes. The rule: never perform a destructive migration (remove/rename column) during a deployment. Use expand-contract: add new column (both old and new code work); deploy new code; verify all pods running new code; then run the contract migration (remove old column). This requires two deployment cycles per breaking schema change - but guarantees zero downtime.

**Level 4 - End-to-end zero-downtime (senior/staff):**
True zero-downtime requires coordination across application, database, and infrastructure changes. Consider: Kubernetes endpoint propagation delay (preStop sleep required); consumer group rebalancing during Kafka consumer restarts (use cooperative incremental rebalance assignor); long-running background jobs (use checkpoint/resume instead of blocking graceful shutdown); circuit breakers opening during rolling update (tune thresholds to tolerate brief elevated error rates from restarting pods); distributed tracing spans spanning pod restarts (propagate trace context to Kafka headers; downstream service resumes the span). Companies like Netflix and Amazon routinely achieve thousands of deployments per day with zero downtime through rigorous application of these patterns.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────────────────────┐
│ Kubernetes Rolling Update - Zero-Downtime Config         │
└─────────────────────────────────────────────────────────┘

spec:
  replicas: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0    # never reduce below 5 ready pods
      maxSurge: 1          # allow up to 6 pods during update

Flow:
  t=0: 5×v1 running (all ready)
  t=1: Start 1×v2 (total: 5v1 + 1v2 = 6 pods, 5 ready)
       Wait: v2 readiness probe passes
  t=2: v2 ready (6 pods, 6 ready)
       Terminate 1×v1 (gracefully: preStop → drain → exit)
       (5 pods: 4v1 + 1v2, all ready)
  t=3: Start 1 more v2 (6 pods: 4v1 + 2v2)
       ...
  t=n: 5×v2 running (all ready)

At all times: ≥ 5 ready pods serving traffic → no downtime
```

---

### 💻 Code Example

**Kubernetes Deployment with zero-downtime configuration:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  replicas: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0 # never go below 5 ready pods
      maxSurge: 1 # allow 6 pods temporarily
  template:
    spec:
      terminationGracePeriodSeconds: 60
      containers:
        - name: order-service
          image: order-service:v2
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 10"]
          readinessProbe:
            httpGet:
              path: /actuator/health/readiness
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 5
            failureThreshold: 3
          livenessProbe:
            httpGet:
              path: /actuator/health/liveness
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
```

**Expand-contract database migration (Flyway):**

```sql
-- V1__expand_add_created_at.sql (Phase 1 - expand)
-- Add new column, keep old column
ALTER TABLE orders
  ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Backfill new column from old column
UPDATE orders SET created_at = order_ts WHERE created_at IS NULL;

-- Both v1 (uses order_ts) and v2 (uses created_at) work simultaneously
-- Deploy v2; verify all pods running v2

-- V2__contract_drop_order_ts.sql (Phase 2 - contract, run AFTER v2 fully deployed)
-- Only run after 100% of pods are on v2
ALTER TABLE orders DROP COLUMN order_ts;
```

---

### ⚖️ Comparison Table

| Deployment Type            | Downtime         | Rollback Speed | Complexity | Concurrent Versions |
| -------------------------- | ---------------- | -------------- | ---------- | ------------------- |
| **Zero-Downtime Rolling**  | None             | Minutes        | Medium     | Yes (briefly)       |
| Blue-Green (zero-downtime) | None             | Instant        | High       | No (switch)         |
| Canary (zero-downtime)     | None             | Seconds        | High       | Yes (deliberate)    |
| Recreate (with downtime)   | Full deploy time | Re-deploy      | Low        | No                  |
| Rolling (without grace)    | Brief per pod    | Minutes        | Low        | Yes                 |

---

### ⚠️ Common Misconceptions

| Misconception                                     | Reality                                                                                                                                     |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Rolling update = zero-downtime automatically      | Rolling update alone is not zero-downtime; requires graceful shutdown + readiness probes + backward-compatible changes                      |
| Database migrations don't affect zero-downtime    | They are the hardest part; destructive migrations during deployment cause downtime                                                          |
| `maxUnavailable: 0` is always correct             | With low replica count (e.g., 1 pod), `maxUnavailable: 0, maxSurge: 1` doubles the pod count briefly; watch resource limits                 |
| Zero-downtime means zero errors during deployment | Brief elevated error rates are possible (circuit breakers, rebalancing); zero-downtime means zero unavailability, not zero transient issues |

---

### 🚨 Failure Modes & Diagnosis

**New Pods Not Ready - Rolling Update Stalls**

**Symptom:** Rolling update starts new pod; readiness probe keeps failing; pod never becomes ready; deployment stalls.

**Root Cause:** Application startup takes longer than `initialDelaySeconds`; or application fails to connect to a dependency during startup.

**Diagnosis:**

```bash
kubectl describe pod <new-pod-name>
# Look for: Readiness probe failed
kubectl logs <new-pod-name>
# Look for: connection refused, timeout, startup error
```

**Fix:** Increase `initialDelaySeconds`; fix dependency connection issue; add startup probe for slow-starting apps.

---

### 🔗 Related Keywords

**Prerequisites:** `Graceful Shutdown (Microservices)`, `Health Check (Microservices)`, `Backward Compatibility`

**Builds On This:** `Canary Deployment (Microservices)`, `Blue-Green Deployment`, `Feature Flags (Microservices)`

**Related Patterns:** `Rolling Update`, `Expand-Contract Pattern`, `Readiness Probe`

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Deploy without any service interruption   │
├──────────────┼───────────────────────────────────────────┤
│ FOUR PILLARS │ Rolling update + Graceful shutdown +       │
│              │ Readiness probes + Backward compatibility │
├──────────────┼───────────────────────────────────────────┤
│ DB PATTERN   │ Expand-contract (never drop column live)  │
├──────────────┼───────────────────────────────────────────┤
│ KEY CONFIG   │ maxUnavailable: 0, maxSurge: 1            │
│              │ preStop: sleep 10                        │
│              │ server.shutdown: graceful                │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Old and new coexist safely while        │
│              │  transition happens invisibly"            │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Zero-downtime deployment requires that old and new versions can run simultaneously during the transition. This constraint applies at every layer: the API must be backward compatible, the database schema must support both versions, and feature behavior must be consistent regardless of which version handles each request. Any layer that violates this makes the deployment not truly zero-downtime.

**Where else this pattern appears:**
- **Expand-Contract database migration:** Old and new schema coexist during the migration window - zero-downtime applied to database schema changes.
- **API versioning:** v1 and v2 coexist during the consumer migration window - zero-downtime applied to API evolution.
- **Kubernetes rolling updates:** Multiple pod versions run simultaneously during a rolling update - the platform-level mechanism for zero-downtime deployments.

---

### 💡 The Surprising Truth

Zero-downtime deployment is harder than teams expect because 'downtime' has multiple definitions. A deployment can have zero HTTP 500 errors (application-level uptime) while still having 5 seconds of elevated P99 latency during pod restarts (user-visible degradation). Teams that claim 'zero downtime' often mean 'no HTTP 500s during deployment' rather than the stricter definition of 'no user-observable degradation in any metric during deployment.' Both definitions matter, but they require different technical controls.
---

### 🧠 Think About This Before We Continue

**Q1.** Your Order Service deployment fails halfway through a rolling update (3 of 5 pods updated to v2; 2 still on v1). The new v2 pods are healthy (readiness passing). But suddenly you discover v2 has a subtle bug in the discount calculation that only affects 10% of orders (a race condition). Kubernetes won't roll back automatically (all pods pass readiness). Describe your rollback strategy and how you'd detect which orders were affected.

*Hint:* Think about the situation: 3 pods on v2 (with the bug), 2 pods on v1 (correct). All pods pass readiness. Kubernetes won't auto-rollback (no readiness failure). Manual rollback: `kubectl rollout undo deployment/order-service` triggers a rolling update back to v1, replacing the 3 v2 pods. Affected orders: query the database for orders created during the v2 window with a discount calculation anomaly (the race condition affects 10% - look for orders with unexpectedly rounded or zero discount amounts created between the v2 deployment and rollback timestamps).

**Q2.** You need to rename an API field: `orderDate` → `createdAt` in the Order Service response. 12 downstream services consume this field. Design the complete zero-downtime strategy for this API change - considering: (a) the Order Service deployment; (b) the 12 downstream service deployments; (c) the transition period where both field names must coexist; (d) cleanup.

*Hint:* Think about what 'rename a field' requires for zero-downtime: the provider must return BOTH `orderDate` AND `createdAt` during the transition (same value, two field names). Deployment sequence: (1) deploy Order Service returning both fields; (2) each of the 12 downstream services migrates to use `createdAt` and deploys; (3) after all 12 consumers are migrated, deploy Order Service returning only `createdAt`; (4) remove the old field from OpenAPI spec. The transition window duration is set by the slowest of the 12 consumer teams to complete their migration.

**Q3 (Design Trade-off):** A new deployment changes the format of a JSON column from `{"discount": 10}` to `{"discount": {"amount": 10, "type": "percentage"}}`. Old pods crash with a parse error when reading new-format data written by new pods. Design the deployment sequence.

*Hint:* Think about what Expand-Contract means for a JSON column format change: (1) Expand: deploy v2 pods that write the new format but ALSO support reading the old format (detect which format on read, handle both versions). At this point, both v1 and v2 pods can read both formats; (2) background job converts all existing data from old format to new format; (3) Contract: once all data is in new format and all pods are v2, remove the old-format reading code. The key: v2 must read both formats before v1 is removed from the cluster.
