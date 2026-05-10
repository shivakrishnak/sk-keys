---
id: DST-071
title: Failure Domain Design
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on:
used_by:
related:
tags:
  - dst
  - advanced
  - architecture
  - bestpractice
status: complete
version: 2
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 69
permalink: /distributed-systems/failure-domain-design/
---

# DST-070 - Failure Domain Design

⚡ TL;DR - Failure domain design isolates the blast radius of failures so that a failure in one component cannot cause failures in unrelated components; the goal is to make partial failure the norm rather than total failure.

| DST-070         | Category: Distributed Systems                        | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------- | :-------------- |
| **Depends on:** | DST-012, DST-014, DST-027, DST-009                   |                 |
| **Used by:**    | DST-068                                              |                 |
| **Related:**    | DST-012, DST-014, DST-027, DST-009, DST-019, DST-068 |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A single bug in one service causes a thread pool
exhaustion that cascades to all services on the same
host. A slow dependency causes all callers to queue
until memory is exhausted. One noisy tenant consumes
all shared resources. In the absence of failure domain
design, every failure has the potential to be a total
outage.

**THE BREAKING POINT:**
Amazon's 2011 AWS US-East-1 outage: a configuration
error in the EBS storage service triggered a cascade.
EBS triggered EC2, which triggered RDS. Multiple
unrelated services failed because they shared the same
failure domain. The blast radius was the entire region.
Post-mortem: failure domains must be explicit and
enforced, not implicit.

**THE INVENTION MOMENT:**
Defense-in-depth in security (1990s). Bulkhead pattern
(James Hamilton, 2007: Dynamo paper). Netflix Cell
Architecture (2016): divide traffic into cells; a failure
in one cell affects only cell users, not all users.

**EVOLUTION:**
Modern failure domain design: availability zones (AWS
concept, 2008), regional isolation (2009+), cell
architecture (2016), chaos engineering (Netflix
Simian Army) to verify domain isolation holds under
failure injection.

---

### 📘 Textbook Definition

**Failure domain** is a group of components that share
a common failure mode — if one fails, all in the domain
may fail. **Failure domain design** is the practice of
minimising the failure domain of each component so
that a failure in one domain does not propagate to
other domains. Techniques: bulkhead (separate thread
pools), cell architecture (separate routing), AZ/region
isolation (separate infrastructure), rate limiting
(prevent one tenant from consuming all resources).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Failure domain design limits how much of the system a single failure can destroy — design so failures are always partial, never total.

**One analogy:**

> A ship is divided into watertight compartments (bulkheads).
> If one compartment floods, the others remain sealed.
> Without bulkheads (one open hull), any breach sinks the ship.
> Failure domain design is the software equivalent:
> each service/tenant/cell is a watertight compartment.

**One insight:**
You cannot prevent all failures; you can design so
failures are always contained. The target is not zero
failures but bounded failures: "when this fails, exactly
this much is affected, and no more."

---

### 🔩 First Principles Explanation

**FAILURE DOMAIN LEVELS:**

```
Level 1: Thread pool isolation (bulkhead)
  Problem: slow downstream blocks all 100 threads
  Solution: dedicate 10 threads per downstream service
  If payment-service slow: only 10 threads blocked;
  90 threads still serve other work
  Tool: Resilience4j Bulkhead

Level 2: Process isolation
  Problem: bug in one service OOM-kills the JVM
  Solution: each service runs in its own process/container
  If order-service crashes: payment-service unaffected
  Tool: Kubernetes pods

Level 3: Host/node isolation
  Problem: hardware failure kills all processes on host
  Solution: spread service replicas across multiple nodes
  If node fails: replicas on other nodes continue
  Tool: Kubernetes anti-affinity rules

Level 4: AZ isolation
  Problem: power failure in data centre
  Solution: deploy to 3+ AZs; active-active
  If AZ-1 loses power: AZ-2 and AZ-3 serve traffic
  Tool: AWS multi-AZ deployment

Level 5: Region isolation
  Problem: natural disaster / regional AWS outage
  Solution: multi-region active-active or active-passive
  If us-east-1 goes down: eu-west-1 takes traffic
  Tool: Route53 health-check failover

Level 6: Cell isolation (Netflix/Amazon pattern)
  Problem: blast radius still 1M+ users per region
  Solution: divide users into cells; each cell is
    an independent deployment with its own DB, cache,
    and compute
  If cell A has a bug: only cell A's users affected;
  cells B-Z continue normally
  Tool: Custom routing layer + per-cell deployment
```

**CORE INVARIANTS:**

1. A failure domain boundary is only as strong as its enforcement mechanism.
2. Shared resources (DB, cache, message broker) are shared failure domains.
3. The blast radius is the maximum scope of impact from a single failure.
4. Chaos engineering verifies domain boundaries hold under real failures.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Partial failure is unavoidable; bounded failure domains are required.
**Accidental:** Shared thread pools, shared queues, and shared databases that accidentally merge failure domains.

---

### 🧪 Thought Experiment

**SETUP:**
A payment platform has three services: Order, Payment,
Notification. They share a single HTTP thread pool.

**WITHOUT FAILURE DOMAIN ISOLATION:**

```
Notification service becomes slow (email provider slow)
  -> All 100 HTTP threads blocked on notification
  -> New order requests queue
  -> Queue fills; 503 responses
  -> Payment service also unavailable
  -> Revenue impact: 100% of orders blocked
  -> Root cause: email provider slowness

This is a total outage caused by an email provider.
```

**WITH FAILURE DOMAIN ISOLATION (Bulkhead):**

```
Notification service becomes slow
  -> Notification thread pool (10 threads) fills
  -> Circuit breaker trips on notification service
  -> Order and Payment thread pools (90 threads) unaffected
  -> Orders and payments continue normally
  -> Notifications degraded: fallback to async queue
  -> Revenue impact: 0 (notifications deferred, not lost)
  -> Root cause: email provider slowness (contained)
```

**THE INSIGHT:**
Bulkhead + circuit breaker contain the failure to the
notification domain. The blast radius is bounded by
design, not by luck.

---

### 🧠 Mental Model / Analogy

> Failure domain design is blast radius engineering.
> A nuclear bomb's blast radius is physically bounded
> by the yield. A software failure's blast radius is
> determined by the failure domain design. Without
> design, the blast radius is "the entire system."
> With design, it's "one cell, one tenant, one service."

**Element mapping:**

- Blast radius = failure domain size
- Bomb yield = severity of the initial failure
- Blast walls = bulkheads, circuit breakers, cell boundaries
- Radiation = cascading failures that cross boundaries
- Decontamination = incident response after boundary breach

Where this analogy breaks down: blast radius in software
can be reduced to zero for adjacent systems; physics
doesn't allow this for actual explosives.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When one part of the system breaks, failure domain
design ensures it breaks only that part, not everything
else. Like fire doors: a fire in one room doesn't burn
down the whole building.

**Level 2 - How to use it (junior developer):**
Add Resilience4j bulkhead to every outbound service
call in your application. Configure a separate thread
pool per downstream service. If downstream is slow,
only its pool fills; other services are unaffected.

**Level 3 - How it works (mid-level engineer):**
In Kubernetes: use `PodAntiAffinity` to spread service
replicas across AZs. Use resource limits (`resources.limits`)
to prevent one pod from consuming all node resources.
Use namespace isolation for tenant separation. Each
of these enforces a failure domain boundary at a
different level.

**Level 4 - Why it was designed this way (senior/staff):**
Netflix's cell architecture routes each customer to
a specific "cell" — a completely isolated deployment
stack. A new deployment is first rolled out to one cell
(canary). If it fails, only that cell's users are
affected. This is failure domain design applied to
deployment: the deployment blast radius is bounded by
the cell size before any issue is detected at full scale.

**Expert Thinking Cues:**

- When adding a dependency: ask "what failure domain does this add me to?"
- Shared databases are shared failure domains; connection pool limits are the boundary.
- Chaos engineering validates that boundaries hold; don't assume them.

---

### ⚙️ How It Works (Mechanism)

**Resilience4j bulkhead configuration:**

```java
// Separate thread pool per downstream service
BulkheadConfig paymentBulkhead = BulkheadConfig.custom()
    .maxConcurrentCalls(10)     // max 10 concurrent calls to payment
    .maxWaitDuration(Duration.ofMillis(50)) // queue timeout
    .build();

BulkheadConfig notificationBulkhead = BulkheadConfig.custom()
    .maxConcurrentCalls(5)      // separate pool for notification
    .maxWaitDuration(Duration.ofMillis(50))
    .build();

// If notification is slow: only notificationBulkhead fills
// paymentBulkhead is completely unaffected
Bulkhead paymentBulkhead =
    Bulkhead.of("payment", paymentBulkheadConfig);
Bulkhead notifBulkhead =
    Bulkhead.of("notification", notifBulkheadConfig);

// Usage:
CheckedSupplier<Order> paymentCall =
    Bulkhead.decorateCheckedSupplier(
        paymentBulkhead,
        () -> paymentService.charge(amount)
    );
```

---

### 🔄 The Complete Picture - End-to-End Flow

**Failure propagation with and without domains:**

```
WITHOUT FAILURE DOMAINS:
  Email provider slow
    -> Notification threads blocked
    -> Shared thread pool exhausted
    -> Order service 503
    -> Payment service 503
    -> TOTAL OUTAGE

WITH FAILURE DOMAINS:           <- YOU ARE HERE
  Email provider slow
    -> Notification bulkhead fills (5 threads)
    -> Circuit breaker trips: OPEN
    -> Fallback: async queue for notifications
    -> Order bulkhead: unaffected (10 threads)
    -> Payment bulkhead: unaffected (10 threads)
    -> Order + Payment: FULLY OPERATIONAL
    -> Notifications: DEGRADED (delayed, not lost)
    -> Revenue impact: ZERO
```

---

### ⚖️ Comparison Table

| Isolation Level        | Scope             | Blast Radius Limit | Cost                       |
| ---------------------- | ----------------- | ------------------ | -------------------------- |
| Thread pool (bulkhead) | Per downstream    | Process-level      | Low (Resilience4j config)  |
| Process (container)    | Per service       | Host-level         | Medium (K8s pod)           |
| Host (anti-affinity)   | Per replica group | Zone-level         | Low (K8s scheduling)       |
| AZ                     | Per zone          | Region-level       | Medium (multi-AZ deploy)   |
| Region                 | Per region        | Global-level       | High (multi-region ops)    |
| Cell                   | Per user segment  | Cell-level         | Very High (custom routing) |

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                         |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| "Kubernetes handles failure domains for me"   | K8s handles process isolation; you must configure anti-affinity, resource limits, and bulkheads |
| "Multi-AZ deployment is a failure domain"     | AZ is one level; you still need bulkheads within a service for downstream isolation             |
| "Circuit breaker = failure domain"            | Circuit breaker is one tool; failure domain requires bulkhead + circuit breaker + timeout       |
| "Shared DB is fine if it's replicated"        | Replication improves availability; shared connection pool is still a shared failure domain      |
| "Cell architecture is only for Netflix-scale" | Cell architecture is valuable at any scale where deployment blast radius needs control          |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Thread Pool Exhaustion Cascade**
**Symptom:** Service A healthy; service B slow; service A becomes unavailable.
**Root Cause:** Shared thread pool; B's calls fill the pool.
**Diagnostic:**

```bash
# Thread dump to see blocking threads
kill -3 <pid>  # Java: print thread dump to stdout
# Or: jstack <pid> | grep -A5 "BLOCKED"
# Look for: all threads waiting on same HttpClient
```

**Fix:** Bulkhead per downstream service.

**Mode 2: Noisy Tenant (Multi-Tenant System)**
**Symptom:** Tenant A causes 503s for Tenant B.
**Root Cause:** No per-tenant resource limits; Tenant A consumes all DB connections.
**Fix:** Per-tenant connection pool limits; rate limiting per tenant.

**Mode 3: AZ Failure Cascades to Cross-AZ**
**Symptom:** AZ-1 failure causes AZ-2 also to fail.
**Root Cause:** AZ-2 services have hard dependencies on AZ-1 services (not AZ-local).
**Fix:** All services must be deployable and operational entirely within one AZ.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[DST-012 - Split Brain]]
- [[DST-014 - Failure Modes]]
- [[DST-027 - Circuit Breaker]]
- [[DST-009 - Bulkhead]]

**Builds On This (learn these next):**

- [[DST-068 - Distributed System Architecture Strategy]]

**Alternatives / Comparisons:**

- Chaos engineering (Chaos Monkey) — verifies that failure domain isolation holds under real failures

---

### 📌 Quick Reference Card

```
+-----------------------------------------------------+
| WHAT IT IS      Limiting how much the system a      |
|                 single failure can affect           |
| PROBLEM         One slow service causes total outage|
| IT SOLVES       via cascading failure               |
| KEY INSIGHT     Design for partial failure; bounded |
|                 blast radius; never total outage    |
| USE WHEN        Designing any service with external |
|                 dependencies                       |
| AVOID           Shared thread pools, shared queues |
|                 across different domains            |
| TRADE-OFF       Isolation overhead vs blast radius  |
| ONE-LINER       Bulkheads: bounded blast radius     |
| NEXT EXPLORE    DST-027, DST-009, DST-068, Chaos Eng|
+-----------------------------------------------------+
```

**If you remember only 3 things:**

1. Failure domain = the maximum scope of impact from a single failure; design to minimise it.
2. Bulkhead (separate thread pools per downstream) is the most impactful single change for failure isolation.
3. Shared resources (thread pool, DB connection pool) are shared failure domains; scope them carefully.

**Interview one-liner:**
"Failure domain design limits the blast radius of failures: thread pool bulkheads isolate downstream slowness, AZ isolation contains infrastructure failures, and cell architecture limits deployment blast radius — the goal is always partial failure, never total outage."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Containment before cure: in any system, design for
failure containment before designing for failure
prevention. Prevention is imperfect; containment is
controllable. The blast radius is the variable you
can always control; the failure itself often cannot
be prevented.

**Where else this pattern appears:**

- **Security** — principle of least privilege limits blast radius of compromised credentials
- **Database transactions** — transaction scope limits blast radius of a failed write
- **Feature flags** — rollout to 1% of users limits blast radius of a bad feature

---

### 💡 The Surprising Truth

The SolarWinds 2020 supply chain attack compromised
18,000 organisations despite all having "secure" networks.
But the blast radius varied enormously: organisations
with zero-trust segmentation (each service isolated;
no lateral movement allowed) contained the breach to
one network segment. Organisations with flat internal
networks saw attackers move freely to high-value targets.
Failure domain design (in this case: network segmentation)
directly determined how much damage an attack could cause,
even though the initial breach was identical.

---

### 🧠 Think About This Before We Continue

**Q1 (System Interaction):** A multi-tenant SaaS platform
has 1,000 tenants sharing a single Postgres database
with a shared connection pool of 100 connections.
Tenant X runs a slow analytics query that holds 95
connections for 30 seconds. Describe the failure cascade
for all other tenants, and design the failure domain
isolation that would contain it.

_Hint:_ 95 of 100 connections used by Tenant X. Other tenants
can't acquire connections -> timeout -> 503. Containment:
per-tenant connection limit (e.g., 10 max); PgBouncer
with per-user pool; analytics queries on read replica;
statement timeout for long-running queries.

**Q2 (Scale):** Netflix's cell architecture divides
users into cells. At what user scale does this become
necessary vs AZ-level isolation being sufficient? What
metric drives the decision to implement cell architecture?

_Hint:_ AZ-level isolation: regional outage affects all users
in that region. Cell-level: deployment of bad code affects
only cell users. The driver is not user scale but deployment
blast radius: at what point does a bad deployment affecting
100% of users cause unacceptable business impact? Netflix:
200M users; even 1% cell = 2M users; still worth isolating.

**Q3 (Design Trade-off):** Failure domain isolation
adds operational complexity: more deployment units,
more monitoring targets, more configuration. For a startup
with 3 engineers and 1,000 users, what level of failure
domain isolation is justified? Design a minimal but
effective strategy.

_Hint:_ 3 engineers: AZ isolation too complex to operate.
Minimal effective strategy: (1) bulkhead per downstream
(Resilience4j; add in one afternoon); (2) circuit breaker
for critical downstream; (3) K8s pod isolation (already
there if on K8s). AZ and cell architecture: defer until
team grows or outage requires it.
