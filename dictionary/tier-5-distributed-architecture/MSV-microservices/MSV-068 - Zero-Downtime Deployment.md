---
id: MSV-068
title: Zero-Downtime Deployment
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★★
depends_on: MSV-067, MSV-020, MSV-069
used_by: MSV-067
related: MSV-067, MSV-069, MSV-020, MSV-010, MSV-063, MSV-078
tags:
  - microservices
  - devops
  - deep-dive
  - deployment
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 68
permalink: /microservices/zero-downtime-deployment/
---

# MSV-068 - Zero-Downtime Deployment

⚡ TL;DR - Zero-Downtime Deployment: deploy a new
service version with NO period where the service
is unavailable. Kubernetes enables this natively
with Rolling Update (replaces pods one by one).
Requirements: service must support multiple
versions running simultaneously (backward-compatible
DB migrations, no breaking API changes), graceful
shutdown (finish in-flight requests before pod
terminates), and Kubernetes readiness probes (new
pod only receives traffic after it's fully started).
Strategies: rolling update, blue/green, canary.
Common pitfall: DB migration that drops a column
used by old pods = downtime during rolling update.

| #068 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Canary Deployment, Service Mesh, Graceful Shutdown | |
| **Used by:** | Canary Deployment | |
| **Related:** | Canary Deployment, Graceful Shutdown, Service Mesh, Service Discovery, Cross-Cutting Concerns, Service Mesh Traffic Management | |

---

### 🔥 The Problem This Solves

**DEPLOYMENT MAINTENANCE WINDOWS ARE EXPENSIVE:**
Old deployment approach: stop old version, deploy
new version, start new version. Window: 2-5 minutes
of downtime. For high-traffic services: 2 minutes
at 1000 RPS = 120,000 failed requests. For SLAs
that promise 99.9% uptime: 2-minute downtime per
deployment = only 43 deployments/year within SLA.
Modern teams deploy 10x/day. Zero-downtime deployment:
eliminate the maintenance window entirely.

---

### 📘 Textbook Definition

**Zero-Downtime Deployment (ZDD)** is a deployment
technique where software updates are applied to
production systems without any period where the
service is unavailable to users. Kubernetes
implements ZDD through **Rolling Update**: pods
running the old version are terminated one-by-one
while new pods start up. At any point during the
rollout: some pods run old version, some run new.
Service is continuously available. Key components:
(1) **Rolling Update Strategy** - Kubernetes
Deployment `maxUnavailable: 0`, `maxSurge: 1`
(or more); (2) **Readiness Probe** - new pod only
receives traffic after passing the probe; prevents
routing traffic to not-yet-ready pods; (3) **Graceful
Shutdown** - old pod receives SIGTERM, finishes
in-flight requests before exiting; (4) **Backward-
Compatible Database Migrations** - new and old
versions run simultaneously; DB schema must be
compatible with both. Strategies: Rolling Update
(one-by-one pod replacement), Blue/Green (two
complete environments, instant traffic switch),
Canary (small percentage traffic to new version).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Zero-downtime deployment: update service while
it's running. New pods start before old pods stop.
Requires: readiness probes, graceful shutdown,
backward-compatible DB migrations.

**One analogy:**
> Replacing airplane engines mid-flight. Impossible?
With modern aircraft: no. You can replace one
> engine while others run (Kubernetes rolling update).
> The plane (service) never stops flying. Key
> requirement: the plane must be able to fly with
> any combination of old and new engines during
> the transition (backward-compatible DB schema;
> old and new code can coexist). The plane doesn't
> land (no maintenance window). Passengers never
> notice (zero downtime).

**One insight:**
Zero-downtime deployment is primarily a DISCIPLINE
problem, not a technology problem. Kubernetes rolling
updates work automatically. The hard part: making
your application ready for it. DB migrations that
run before deployment? They will break old pods
still running during rolling update. API changes
that remove a field? Old consumers fail while
new version rolls out. Zero-downtime deployment
requires: expand/contract migrations, backward-
compatible API changes, and graceful shutdown.
These are team discipline requirements.

---

### 🔩 First Principles Explanation

**KUBERNETES ROLLING UPDATE MECHANISM:**

```
BEFORE UPDATE: 3 pods running v1.4
  pod-1: v1.4 (RUNNING)
  pod-2: v1.4 (RUNNING)
  pod-3: v1.4 (RUNNING)
  Traffic: all 3 pods receiving requests

ROLLING UPDATE START: maxSurge=1, maxUnavailable=0
  Step 1: Start pod-4 (v2.0)
    pod-4: v2.0 (STARTING)
    Readiness probe: fails (pod not ready yet)
    Traffic: still only pods 1,2,3
  
  Step 2: pod-4 readiness probe passes
    pod-4: v2.0 (READY)
    Traffic: pods 1,2,3,4 (4 pods, mix of versions)
  
  Step 3: Kubernetes terminates pod-1
    pod-1: receives SIGTERM
    pod-1: finishes in-flight requests (graceful shutdown)
    pod-1: exits after 30s max
    Traffic: pods 2,3,4 (3 pods, 2 old + 1 new)
  
  Step 4: Start pod-5 (v2.0), same cycle
  Step 5: Terminate pod-2 (graceful shutdown)
  Step 6: Start pod-6 (v2.0), terminate pod-3
  
AFTER UPDATE: 3 pods running v2.0
  pod-4: v2.0 (RUNNING)
  pod-5: v2.0 (RUNNING)
  pod-6: v2.0 (RUNNING)
  Traffic: all 3 pods
  Downtime: ZERO (traffic always available)
```

**EXPAND/CONTRACT PATTERN FOR DB MIGRATIONS:**

```
PROBLEM: Rename column 'customer_email' -> 'email'
Naive approach: ALTER TABLE orders RENAME COLUMN
  customer_email TO email
Running during rolling update:
  v1.4 pods: SELECT customer_email FROM orders -> ERROR
  v2.0 pods: SELECT email FROM orders -> OK
  Result: v1.4 pods fail during the rolling update
  Downtime: for v1.4 pods until they are terminated

EXPAND/CONTRACT PATTERN (3 deployments):
  DEPLOYMENT 1 (expand):
    ALTER TABLE orders ADD COLUMN email VARCHAR(255);
    UPDATE orders SET email = customer_email;
    Application code: writes to BOTH customer_email
    AND email
    Both v1.4 and v2.0 compatible: v1.4 uses
    customer_email; v2.0 uses both
  
  DEPLOYMENT 2 (contract):
    Application code: reads from email;
    writes to email only
    customer_email column: no longer written
  
  DEPLOYMENT 3 (cleanup):
    ALTER TABLE orders DROP COLUMN customer_email;
    Only after ALL v1.4 pods are gone
    Safe: no pods use customer_email anymore

Result: column renamed over 3 deployments;
        ZERO downtime throughout
```

---

### 🧪 Thought Experiment

**ZDD FAILURE: READINESS PROBE NOT CONFIGURED**

```
SCENARIO: Rolling update without readiness probe
  
  Step 1: Kubernetes starts new pod (v2.0)
  v2.0: Spring Boot starting up...
        Loading application context...
        Connecting to database...
        Starting Kafka consumers...
        Server started on port 8080
        [startup time: 25 seconds]
  
  Without readiness probe:
  Kubernetes: sees container started (port bound)
  After default 10s: marks pod READY
  Traffic: routed to pod (pod is in Ready state)
  But: Spring Boot application still starting!
  Requests: arrive at pod before app is ready
  Result: 503 Service Unavailable or NullPointerException
  Downtime: 15 seconds of errors per pod (25s startup
            - 10s Kubernetes wait = 15s of bad traffic)
  3 pods rolled: 45 seconds total of errors
  
  WITH readiness probe:
  /actuator/health/readiness: returns 503 until
    Spring Boot fully started (all beans initialized,
    DB connection verified, Kafka consumer started)
  Returns 200: only when fully ready
  Kubernetes: only routes traffic after 200 response
  Rolling update: zero errors during startup window
```

---

### 🧠 Mental Model / Analogy

> Zero-downtime deployment is like highway lane
> resurfacing. Old approach: close the highway
> (maintenance window); resurface; reopen. Modern
> approach: close one lane at a time; resurface;
> reopen; move to next lane. Traffic keeps moving
> (zero downtime). Requirements: must have multiple
> lanes (multiple pods/replicas), traffic must be
> able to use any lane (stateless, no session affinity
> that breaks on pod termination), and the resurfacing
> must complete before traffic can return to the
> lane (readiness probe before traffic routing).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Deploy new software without the service going
down. New pods start before old pods stop. Users
never see an outage.

**Level 2 - Kubernetes basics (junior developer):**
Spring Boot: add `spring-boot-starter-actuator`.
Configure readiness probe: `/actuator/health/
readiness`. Add liveness probe: `/actuator/health/
liveness`. Deployment spec: `maxUnavailable: 0`,
`maxSurge: 1`. Add `terminationGracePeriodSeconds:
60`. This is enough for basic ZDD in Kubernetes.

**Level 3 - DB migration discipline (mid-level):**
Expand/contract pattern for every schema change.
Rule: migrations run in production BEFORE the new
code is deployed (old code must still work). So:
migrations must be backward-compatible with old
code. Adding column: backward-compatible (old code
ignores it). Dropping column: NOT backward-compatible
(old code tries to read it). Renaming column: NOT
backward-compatible. Changing column type: NOT
backward-compatible. Every ZDD-breaking migration
needs expand/contract.

**Level 4 - API backward compatibility (senior):**
Rolling update: old and new API versions run
simultaneously. If API consumers are also being
rolled: old consumers talk to new provider, new
consumers talk to old provider. All 4 combinations
must work. API versioning: `/api/v1/orders` (old)
and `/api/v2/orders` (new) coexist during rollout.
Deprecation policy: maintain old API version for
N deployments after new version. Consumer-Driven
Contract Tests (Pact) guarantee backward compatibility.

**Level 5 - ZDD at 100+ replicas (principal):**
At high replica counts: rolling update takes time
(100 replicas, 1 at a time = 100 pod restarts).
Solution: `maxSurge: 25`, `maxUnavailable: 0` -
start 25 new pods simultaneously; terminate 25
old pods after all 25 are ready. Speed: 4 batches
for 100 pods. But: 125 pods during rollout
(resource spike). PodDisruptionBudget: ensure
minimum available pods during voluntary disruptions
(deployments, node drains). Blue/Green as alternative
for highest-traffic services: instant cutover
(no rolling update period), but requires double
resources.

---

### ⚙️ How It Works (Mechanism)

```yaml
# KUBERNETES DEPLOYMENT: zero-downtime configuration
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0   # No pods removed until
                          # replacement is ready
      maxSurge: 1         # Add 1 extra pod during
                          # rollout (temporary)
  template:
    spec:
      # Graceful shutdown: 60s for in-flight requests
      terminationGracePeriodSeconds: 60
      containers:
      - name: order-service
        image: order-service:2.1.0
        ports:
        - containerPort: 8080
        
        # Readiness probe: only route traffic
        # when application is fully started
        readinessProbe:
          httpGet:
            path: /actuator/health/readiness
            port: 8080
          initialDelaySeconds: 10  # wait 10s before first check
          periodSeconds: 5         # check every 5s
          failureThreshold: 3      # 3 failures -> not ready
        
        # Liveness probe: restart if truly broken
        livenessProbe:
          httpGet:
            path: /actuator/health/liveness
            port: 8080
          initialDelaySeconds: 30  # longer: wait for startup
          periodSeconds: 10
          failureThreshold: 3
        
        lifecycle:
          # Ensure K8s stops routing traffic BEFORE
          # the pod receives SIGTERM (avoids race condition)
          preStop:
            exec:
              command: ["sleep", "5"]
---
# PodDisruptionBudget: maintain minimum availability
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: order-service-pdb
spec:
  minAvailable: 2  # Always have at least 2 pods
  selector:
    matchLabels:
      app: order-service
  # During rolling update: K8s respects this
  # (maxUnavailable: 0 in Deployment already ensures this)
  # This PDB also applies during: node drain, cluster
  # upgrades, voluntary disruptions
```

```java
// SPRING BOOT: graceful shutdown configuration
// application.yaml
spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s  # Wait 30s for
    # in-flight requests to complete before shutdown
server:
  shutdown: graceful  # Enable graceful shutdown

// What happens:
// 1. SIGTERM received
// 2. Spring: stops accepting new requests
// 3. Spring: waits for in-flight requests (max 30s)
// 4. Spring: context closes, beans destroyed
// 5. Process exits

// If in-flight requests take > 30s: forced shutdown
// Typical: 30s is sufficient for HTTP services
// Long-running jobs: need a longer timeout or
// separate graceful shutdown mechanism
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
COMPLETE ZDD DEPLOYMENT CHECKLIST:

BEFORE DEPLOYMENT:
  [ ] DB migration is backward-compatible
      (expand/contract; old code still works)
  [ ] API changes are backward-compatible
      (no removed fields; new fields are optional)
  [ ] Readiness probe configured (/actuator/health/readiness)
  [ ] Liveness probe configured (/actuator/health/liveness)
  [ ] Graceful shutdown configured (spring.lifecycle...)
  [ ] terminationGracePeriodSeconds >= request timeout
  [ ] PodDisruptionBudget in place
  [ ] maxUnavailable: 0 in Deployment strategy

DURING DEPLOYMENT (automated, no action needed):
  Kubernetes: start new pod
  New pod: Spring Boot starts, readiness probe fails
  Readiness probe: passes -> pod added to load balancer
  Old pod: SIGTERM -> preStop sleep -> SIGTERM app
  App: graceful shutdown (finish in-flight requests)
  Old pod: exits -> removed from load balancer
  Repeat for each pod

AFTER DEPLOYMENT:
  [ ] Verify: all pods running new version
      kubectl rollout status deployment/order-service
  [ ] Verify: error rate unchanged
  [ ] Verify: p99 latency unchanged
  [ ] If issues: kubectl rollout undo deployment/order-service
                 (instant rollback to previous version)
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: blocking migration vs expand/contract**

```sql
-- BAD: blocking migration run before deployment
-- (old pods still running; will fail immediately)
ALTER TABLE orders RENAME COLUMN
  customer_email TO email;
-- old pods (v1.4):
--   SELECT customer_email FROM orders
--   ERROR: column "customer_email" does not exist
-- Rolling update: 5 minutes of failures on old pods
-- Downtime: NOT zero
```

```sql
-- GOOD: expand/contract migration (3 steps)

-- STEP 1 (deployment N): expand
ALTER TABLE orders ADD COLUMN email VARCHAR(255);
UPDATE orders SET email = customer_email
  WHERE email IS NULL;
-- App v2.0: writes BOTH customer_email AND email
-- App v1.4 (old): still works (reads customer_email)

-- STEP 2 (deployment N+1): migrate
-- App v2.1: reads from email; writes to email only
-- customer_email still in DB but not written

-- STEP 3 (deployment N+2): contract
ALTER TABLE orders DROP COLUMN customer_email;
-- Safe: no application reads customer_email anymore
-- Zero downtime throughout all 3 deployments
```

---

### ⚖️ Comparison Table

| Strategy | Downtime | Resource Need | Rollback Speed | Complexity |
|---|---|---|---|---|
| **Big-bang** | 2-5 min | Normal | Minutes | Low |
| **Rolling Update** | Zero | +1 pod (maxSurge) | Minutes | Low |
| **Blue/Green** | Zero | 2x normal | Instant | Medium |
| **Canary** | Zero | +canary pods | Instant | High |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Rolling update automatically means zero downtime | Rolling update is the mechanism. Zero downtime requires: (1) readiness probes (new pod only gets traffic when ready), (2) graceful shutdown (old pod finishes in-flight requests), (3) backward-compatible DB migrations (old and new code run simultaneously). Without ALL THREE: rolling update can cause downtime. The most common cause: DB migration that drops/renames a column used by old pods still running during rollout. |
| terminationGracePeriodSeconds is sufficient for graceful shutdown | `terminationGracePeriodSeconds` is the HARD LIMIT Kubernetes enforces. The APPLICATION must implement graceful shutdown WITHIN that time. Spring Boot `server.shutdown=graceful` + `timeout-per-shutdown-phase=30s`: Spring stops accepting requests, waits for in-flight requests (up to 30s), then shuts down. If `terminationGracePeriodSeconds: 60` but Spring's timeout is not configured: Spring shuts down immediately (default). Both must be configured and aligned. |
| Blue/green deployment is always better than rolling update | Blue/green requires 2x resources (both environments running simultaneously). For cost-sensitive environments: significant overhead. Blue/green benefit: instant rollback (DNS switch) vs rolling update rollback (minutes). For most services: rolling update with proper configuration is sufficient. Blue/green is justified for: high-revenue services where rollback speed matters most, or services that cannot run multiple versions simultaneously (e.g., stateful services with strict schema requirements). |

---

### 🚨 Failure Modes & Diagnosis

**Pods restarting during deployment: readiness/liveness misconfiguration**

**Symptom:**
During rolling update: new pods start, then
immediately get killed and restarted. Deployment
never completes. `kubectl rollout status`: stuck.
`kubectl get pods`: new pods in CrashLoopBackOff
or repeatedly Terminating.

**Root Cause (most common):**
Liveness probe: `initialDelaySeconds: 10` (too short
for 25-second Spring Boot startup). Spring Boot:
still starting at 10s. Liveness probe: fails 3
times (at 10s, 20s, 30s). Kubernetes: kills pod
as "unhealthy" (liveness failure = restart). New
pod starts, same cycle. CrashLoopBackOff.

**Diagnosis:**
```bash
# Check events for pod:
kubectl describe pod order-service-new-pod-xyz
# Look for: "Liveness probe failed"
# Check: initialDelaySeconds vs actual startup time

# Check startup time:
kubectl logs order-service-new-pod-xyz
# Look for: "Started OrderServiceApplication in Xs"
# If X > initialDelaySeconds: liveness probe too aggressive
```

**Fix:**
```yaml
livenessProbe:
  httpGet:
    path: /actuator/health/liveness
    port: 8080
  initialDelaySeconds: 60  # > startup time (30s)
  periodSeconds: 10
  failureThreshold: 3
readinessProbe:
  httpGet:
    path: /actuator/health/readiness
    port: 8080
  initialDelaySeconds: 10  # Check frequently for startup
  periodSeconds: 5
  failureThreshold: 6  # 30 seconds to become ready
```

---

### 🔗 Related Keywords

**Enables ZDD:**
- `Graceful Shutdown` - how pods terminate without
  dropping in-flight requests
- `Canary Deployment` - progressive delivery as
  an alternative to rolling update

**Infrastructure:**
- `Service Mesh Traffic Management` - Istio/Linkerd
  enable fine-grained traffic control during ZDD

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ REQUIRES     │ Readiness probe + graceful shutdown +     │
│              │ backward-compatible DB migrations         │
├──────────────┼───────────────────────────────────────────┤
│ K8S CONFIG   │ maxUnavailable:0, maxSurge:1, PDB,       │
│              │ terminationGracePeriodSeconds: 60         │
├──────────────┼───────────────────────────────────────────┤
│ DB PATTERN   │ Expand/contract: add->migrate->drop       │
│              │ Never drop/rename in single migration     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Rolling update + readiness probe +       │
│              │  graceful shutdown + expand/contract"     │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Three requirements for true ZDD: readiness probe
   (traffic only after ready), graceful shutdown
   (finish in-flight requests), backward-compatible
   DB migrations (old and new run simultaneously).
2. Kubernetes config: `maxUnavailable: 0`,
   `maxSurge: 1`, `terminationGracePeriodSeconds: 60`.
3. DB migration rule: never DROP or RENAME a column
   in a single migration during rolling update. Use
   expand/contract (3 deployments).

**Interview one-liner:**
"Zero-Downtime Deployment with Kubernetes Rolling
Update requires three elements: (1) Readiness probe
(/actuator/health/readiness) - pod only receives
traffic when fully ready; (2) Graceful shutdown
(spring.lifecycle.timeout-per-shutdown-phase=30s +
terminationGracePeriodSeconds: 60) - old pod finishes
in-flight requests before exiting; (3) Backward-
compatible DB migrations - use expand/contract: add
new column first (backward-compat), then drop old
column only after all old pods are gone. Without
all three: rolling update = downtime."

---

### 💡 The Surprising Truth

The preStop hook is the most underused (and most
necessary) ZDD configuration. Without it: Kubernetes
sends SIGTERM to the pod AND simultaneously removes
it from the Service endpoints. But these two events
happen concurrently: kube-proxy takes up to 5
seconds to update iptables rules across nodes.
During those 5 seconds: new requests are STILL
routed to the pod that has already received SIGTERM
(and started shutting down). Solution:
```yaml
lifecycle:
  preStop:
    exec:
      command: ["sleep", "5"]
```
This makes the pod wait 5 seconds before starting
shutdown, giving kube-proxy time to update routing.
Without this: up to 5 seconds of connection refused
errors per pod during rolling update. With this:
true zero downtime.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **CONFIGURE** Write a complete Kubernetes
   Deployment manifest for ZDD: rolling update
   strategy, readiness/liveness probes (correct
   timing for 25s Spring Boot startup), graceful
   shutdown via preStop hook, PodDisruptionBudget.
2. **DB MIGRATION** Given a schema change (rename
   orders.customer_email to orders.email): write
   all 3 Flyway/Liquibase migration scripts and
   the application code changes for each deployment.
   Verify: old and new code both work at each step.
3. **DIAGNOSE** Given: rolling update stuck, new
   pods in CrashLoopBackOff. Walk through: kubectl
   describe pod, check liveness probe configuration,
   check startup time, fix the probe timing.
4. **BLUE/GREEN** Explain when to choose blue/green
   over rolling update: what trade-offs justify
   the 2x resource cost, and what deployment
   scenarios make rolling update insufficient?
5. **PRESSTOP** Explain the preStop sleep race
   condition: why it causes errors, what the
   solution is, and why 5 seconds is usually
   sufficient.

---

### 🧠 Think About This Before We Continue

**Q1.** Your order-service has a DB migration that
needs to add a new payment_method_token field (NOT
NULL with a default) and remove an old
credit_card_hash field that has PCI-DSS implications.
Design the complete expand/contract migration across
3 deployments. For each deployment: write the SQL
migration AND the application code changes needed.

**Q2.** You run `kubectl rollout status deployment/
order-service` during a deployment and it's been
stuck for 10 minutes. The deployment should take
< 2 minutes. Walk through your diagnostic process:
what kubectl commands do you run, what do you
look for in the output, and what are the 5 most
common causes of a stuck rolling update?

**Q3.** Your team is debating: "For our highest-
revenue payment-service (500,000 USD/hour), should
we use rolling update or blue/green deployment?"
Present the analysis: what are the risks of each
approach, what is the cost difference (extra
infrastructure for blue/green), and what is your
recommendation based on the revenue-at-risk
calculation?