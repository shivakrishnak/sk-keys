---
id: DST-075
title: Failure-First Thinking
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
  - mental-model
  - bestpractice
status: draft
version: 1
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 75
permalink: /dst/failure-first-thinking/
---

# DST-075 - Failure-First Thinking

⚡ TL;DR - Failure-first thinking is the discipline of designing distributed systems by starting with failure scenarios rather than the happy path — systems designed failure-first are resilient by construction, not by accident.

| DST-075 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DST-001, DST-002, DST-004, DST-042, DST-043 | |
### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Engineers design the happy path first, then add error
handling as an afterthought. The happy path becomes
the primary mental model; failure handling is patchy
and inconsistent. The system works perfectly in demos
and staging, then fails in production in ways that
could have been anticipated.

**THE BREAKING POINT:**
Knight Capital (2012): a software deployment error
left old trading code active alongside new code. In
45 minutes, the system lost $440M. Post-mortem: no
failure scenario was designed for "partial deployment";
no rollback plan; no circuit breaker. The happy path
was tested; the failure paths were not designed.

**THE INVENTION MOMENT:**
Netflix Chaos Monkey (2011): deliberately injecting
failures into production to force engineers to design
for them. AWS well-architected framework (2015): failure
mode analysis as a first-class design activity. "Failure
Modes and Effects Analysis" (FMEA): a manufacturing
technique applied to software design.

**EVOLUTION:**
Chaos engineering matured: from random instance killing
(Chaos Monkey) to structured game days (GameDay),
to continuous chaos in production (Chaos Mesh, Gremlin).
Failure-first thinking is now a design methodology,
not just a testing technique.

---

### 📘 Textbook Definition

**Failure-first thinking** is a design methodology
where failure scenarios are designed before (or simultaneously
with) the happy path. For each component and dependency:
(1) What are all the ways this can fail? (2) What
happens to users and dependent systems when it fails?
(3) How is the failure detected? (4) How is the impact
contained? (5) How is the system recovered? Failure-first
thinking produces systems where failures are expected,
detectable, and bounded rather than surprising, invisible,
and unbounded.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Design every failure scenario before writing the happy path — systems that expect failure are resilient by construction.

**One analogy:**

> Failure-first thinking is like designing a building
> by starting with earthquake, fire, and flood scenarios
> before designing the lobby. A lobby designed before
> earthquakes is retrofitted with reinforcement; a
> lobby designed after earthquake analysis has the
> reinforcement built into its bones.

**One insight:**
Failure-first does not mean pessimism; it means the
happy path is a special case of the general case. When
your design handles all failure cases, the happy path
is automatically correct. The reverse is not true.

---

### 🔩 First Principles Explanation

**FAILURE-FIRST DESIGN CHECKLIST (per component):**
```
For every service, dependency, and operation:

1. ENUMERATE FAILURE MODES
   - What fails? (service down, slow, returns wrong data)
   - When does it fail? (network partition, overload, bug)
   - How does it fail? (exception, timeout, 5xx, data corruption)

2. IMPACT ANALYSIS
   - What callers are affected?
   - What user operations are blocked?
   - What is the blast radius? (DST-068)

3. DETECTION
   - How do we know it has failed? (health check, alert)
   - How quickly? (detection latency)
   - Can it fail silently? (partial failure with no error)

4. CONTAINMENT
   - Circuit breaker: stop cascading failure
   - Bulkhead: isolate blast radius
   - Timeout: don't wait forever
   - Fallback: what does the user see?

5. RECOVERY
   - How does the service recover? (restart, failover)
   - How long does recovery take? (RTO)
   - What data might be lost? (RPO)
   - Who is notified? (on-call, customers)

6. PREVENTION
   - How do we make this failure less likely?
   - How do we make it less impactful when it does occur?
```

**APPLICATION TO EVERY OUTBOUND CALL:**
```java
// WRONG: happy path first
public Order placeOrder(OrderRequest req) {
    inventory.decrement(req.productId());
    payment.charge(req.userId(), req.amount());
    return orderRepo.save(new Order(req));
}
// Q: what if inventory times out?
// Q: what if payment succeeds but DB write fails?
// Q: what if payment is charged but inventory fails to decrement?
// Not designed. Will fail in production.

// RIGHT: failure-first
// Design: inventory decrement -> payment charge -> order save
// Failure: inventory fail -> abort (no charge yet)
// Failure: payment fail -> restore inventory (compensation)
// Failure: DB fail -> payment charged, order not saved
//   -> idempotency key on order; retry creates same order
// Failure: payment timeout -> query status; retry or compensate
// THEN: write the code that implements these failure designs
```

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Every failure mode exists whether or not it is designed for; designing for it is unavoidable work.
**Accidental:** Discovering failure modes in production rather than at design time.

---

### 🧪 Thought Experiment

**SETUP:**
You are designing a notification service that sends
SMS via a third-party provider.

**HAPPY-PATH-FIRST DESIGN:**
```
notificationService.send(userId, message)
  -> smsProvider.send(phone, message)
  -> return "sent"

What could go wrong?
  (not designed)
  (will be discovered in production)
```

**FAILURE-FIRST DESIGN:**
```
Failure modes:
  1. smsProvider: timeout (network issue)
  2. smsProvider: 429 (rate limited)
  3. smsProvider: 500 (provider outage)
  4. smsProvider: success but delivery failed (SMSC issue)
  5. Phone number invalid
  6. User opted out
  7. Duplicate send (retry caused by caller)

For each:
  1. Timeout -> retry with backoff; max 3 attempts
     -> if all fail: add to retry queue; alert
  2. 429 -> exponential backoff + jitter
  3. 500 -> circuit breaker opens; fallback: email
  4. Success -> delivery receipt via webhook; alert if no receipt in 5min
  5. Invalid number -> log; no retry; notify caller
  6. Opted out -> check preferences DB before calling provider
  7. Duplicate -> idempotency key on send; provider deduplicates

NOW write the code that implements these designs.
The happy path (smsProvider returns 200 + delivery receipt)
is the simplest path through this design.
```

---

### 🧠 Mental Model / Analogy

> Failure-first thinking is the software equivalent of
> a surgeon's pre-operative briefing. Before cutting,
> the team goes through every possible complication:
> allergic reaction, bleeding, equipment failure, patient
> movement. They assign responsibility for each: anaesthesiologist
> handles allergic reaction; nurse handles equipment.
> The surgery then proceeds on the happy path. Surgeons
> who skip briefings have higher complication rates.

**Element mapping:**
- Surgery = distributed operation
- Complication = failure mode
- Briefing = failure-first design session
- Responsibility assignment = circuit breaker / fallback ownership
- Equipment failure = dependency failure

Where this analogy breaks down: surgical complications
are rare; distributed systems failures are routine.
Failure-first is not contingency planning; it's normal
operations planning.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Before building something, list all the ways it can
break and design what happens in each case. Don't
build the happy path and hope failures don't happen.

**Level 2 - How to use it (junior developer):**
For every method that calls an external service: before
writing the implementation, write the failure cases
as comments: `// failure: timeout`, `// failure: 5xx`,
`// failure: partial success`. Then implement handling
for each before implementing the happy path.

**Level 3 - How it works (mid-level engineer):**
Failure mode and effects analysis (FMEA) at design
review: for each component in the system diagram, add
a column for failure modes. Rate each by: probability,
impact, and detectability. Prioritise handling by
risk score (probability × impact / detectability).
Document the design decision for each.

**Level 4 - Why it was designed this way (senior/staff):**
Netflix's chaos engineering matured from reactive
(Chaos Monkey: random failures after deploy) to proactive
(GameDay: planned failure injection before traffic).
The key insight: the real value of chaos engineering
is not finding the failure you inject; it's forcing
engineers to design for failures BEFORE injection.
Chaos engineering is a culture change tool as much
as a testing tool.

**Expert Thinking Cues:**
- Design review question: "What is the failure mode of this service call?"
- Every call without a timeout is a bug waiting to express itself.
- The most dangerous failures are silent: no error, just wrong data.

---

### ⚙️ How It Works (Mechanism)

**FMEA table for a service design:**
```
| Component       | Failure Mode   | Impact  | P | Handling          |
|-----------------|---------------|---------|---|-------------------|
| Payment API     | Timeout        | High    | M | Retry+idempotency |
| Payment API     | 5xx            | High    | L | Circuit breaker   |
| Payment API     | Success/no rcpt| High    | L | Webhook + alert   |
| Inventory DB    | Slow query     | Medium  | M | Query timeout 1s  |
| Inventory DB    | Connection pool| High    | L | Bulkhead          |
| Message broker  | Partition lag  | Low     | H | Consumer lag alert|
| Message broker  | Dead partition | Medium  | L | DLQ + alert       |

P = Probability (H/M/L)
Handling = designed response
```

---

### 🔄 The Complete Picture - End-to-End Flow

**Failure-first design process:**
```
System design kickoff:               <- YOU ARE HERE
  |
Happy path identified:
  -> List all services and dependencies
  |
For each dependency:
  -> Enumerate failure modes
  -> Rate risk (P x impact / detectability)
  -> Design handling for each
  |
For each failure handling:
  -> Circuit breaker config
  -> Bulkhead config
  -> Timeout values
  -> Fallback response
  -> Alert thresholds
  |
Architecture fitness functions:
  -> Automated check: every outbound call has a timeout
  -> Automated check: every service has a circuit breaker
  |
Implementation:
  -> Code written to implement failure designs
  -> Happy path is the simplest case
  |
Chaos engineering:
  -> Inject designed failure modes in staging
  -> Verify handling behaves as designed
```

---

### ⚖️ Comparison Table

| Approach | When Failure Design Happens | Discovery Cost | Resilience Quality |
|---|---|---|---|
| Happy-path-first | After production incident | Very High | Low (patchy) |
| Failure-first | At design time | Low | High (by construction) |
| Chaos engineering | After deployment | Medium | Medium (finding gaps) |
| FMEA at design review | At design review | Low | High (systematic) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Failure-first is pessimistic" | It is realistic: distributed systems fail constantly at scale |
| "Chaos engineering tests failure-first" | Chaos tests that failure handling works; failure-first designs the handling before chaos |
| "Adding retry handles all failures" | Retry without idempotency causes duplicate operations; retry without circuit breaker causes cascading |
| "Happy-path-first, then add resilience" | Resilience added to existing code is always patchier than resilience designed from scratch |
| "Cloud providers handle failures" | Cloud SLA covers availability, not per-call reliability; fallacies of distributed computing apply in the cloud |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Silent Failure (No Error, Wrong Data)**
**Symptom:** Payment processed; inventory not decremented; no error in logs.
**Root Cause:** Inventory service returned 200 with a stale result (DB read replica lag).
**Diagnostic:** Trace the checkout request; check inventory-service span for which replica was read.
**Fix:** Design: inventory decrement must use primary (linearizable write); health check for replica lag.

**Mode 2: Timeout Cascade (Thread Pool Exhaustion)**
**Symptom:** All services degraded simultaneously; thread pools at 100%.
**Root Cause:** One slow dependency; no timeout; threads block; pool exhausts; cascades.
**Fix:** Failure-first design requires: timeout on every outbound call; bulkhead per dependency.

**Mode 3: Incorrect Fallback Causing Silent Data Loss**
**Symptom:** Orders lost during payment outage; fallback returns empty cart.
**Root Cause:** Fallback design said "return empty cart on payment failure"; should have been "queue order for retry."
**Fix:** Revisit fallback design: what should the user experience be? Empty cart was wrong semantically.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[DST-001 - What Is a Distributed System]]
- [[DST-002 - Why Distribution Is Hard]]
- [[DST-004 - The Fallacies of Distributed Computing]]
- [[DST-042 - Circuit Breaker]]
- [[DST-043 - Bulkhead]]

**Builds On This (learn these next):**
- [[DST-068 - Failure Domain Design]]

**Alternatives / Comparisons:**
- Chaos engineering (tests failure-first assumptions after implementation)

---

### 📌 Quick Reference Card

```
+-----------------------------------------------------+
| WHAT IT IS      Design methodology: enumerate all   |
|                 failure modes before happy path     |
| PROBLEM         Failure handling added as           |
| IT SOLVES       afterthought is always incomplete   |
| KEY INSIGHT     Happy path is the easiest case; the |
|                 failure paths need more design work |
| USE WHEN        Every new service or feature design |
| AVOID           "We'll add error handling later"    |
| TRADE-OFF       Upfront design time vs production   |
|                 incident cost                       |
| ONE-LINER       Design failures first; code follows |
| NEXT EXPLORE    DST-068, FMEA, Chaos engineering    |
+-----------------------------------------------------+
```

**If you remember only 3 things:**
1. Every external call has failure modes; design them before implementing the happy path.
2. The most dangerous failures are silent: no error thrown, but wrong data returned or action not taken.
3. FMEA (Failure Mode and Effects Analysis) is the systematic tool: enumerate, rate, design, verify.

**Interview one-liner:**
"Failure-first thinking means enumerating all failure modes before writing a line of happy-path code: timeout, service down, partial success, silent wrong data — for each, design detection, containment, and recovery; then implement the happy path, which is the simplest path through the failure-designed system."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
The happy path is a special case of the failure-tolerant
design. Systems designed for the happy path and retrofitted
for failures are always weaker than systems designed
for all cases from the start. This principle applies
beyond distributed systems: security (assume breach,
design for containment), data migration (assume partial
failure, design rollback), and team process (assume
members leave, design knowledge transfer).

**Where else this pattern appears:**
- **Security design** — threat modelling: enumerate all attacker actions before designing defences
- **Data migrations** — design rollback before executing forward migration
- **Deployment pipelines** — design rollback and canary failure criteria before deploying

---

### 💡 The Surprising Truth

Knight Capital's $440M loss in 45 minutes (2012) was
the direct result of a partial deployment: the new
code was deployed to 7 of 8 servers; the 8th server
ran old code that activated an obsolete feature (SMARS).
The failure mode — partial deployment with mixed code
versions — was not in any failure-first design checklist.
The engineering team had never asked "what happens if
only 7 of 8 servers receive the new deployment?" If
they had applied failure-first thinking to the deployment
process itself (not just the application logic), the
answer would have been: add deployment verification
before enabling traffic to any server.

---

### 🧠 Think About This Before We Continue

**Q1 (Root Cause):** Apply failure-first thinking to
a database migration. A migration adds a new NOT NULL
column to the `orders` table with no default value.
Enumerate all failure modes of this migration if applied
to a live production database with 10M rows and rolling
deployments where old application code must coexist
with the new schema during the rollout window.

*Hint:* Old code doesn't write the new column -> NOT NULL
violation. Migration takes > 30s -> table locked, all
writes blocked. Rollback: column added, hard to remove
if data written. Failure-first design: expand-contract
pattern: (1) add column nullable; (2) deploy code writing
the column; (3) backfill; (4) add NOT NULL constraint.

**Q2 (Scale):** Netflix's Chaos Monkey randomly kills
EC2 instances in production. At what scale does this
benefit outweigh the risk of causing an actual customer-
facing incident from the injected failure? How do they
ensure the chaos doesn't violate their own SLA?

*Hint:* Chaos Monkey is run only in business hours
(engineers available to respond). Designed failures should
have zero customer impact (if failure-first design is
correct). If Chaos Monkey causes an outage: failure-first
design had a gap; fix it. Netflix runs Chaos Monkey
because the cost of a discovered gap (in business hours,
with engineers available) << cost of same gap discovered
during peak traffic.

**Q3 (Design Trade-off):** A team argues that "we don't
need failure-first design for a feature with <0.1%
failure rate." Use expected value to refute or support
this argument. At what failure rate does failure-first
design become unjustified by expected value calculation?

*Hint:* Expected value = probability × impact. 0.1% failure
rate × $1M incident cost = $1,000 expected loss. If
failure-first design costs 8 hours ($800 engineer time),
the expected value is positive even at 0.1% failure rate.
The argument fails for high-impact failures at any failure
rate > 0. Only justified to skip for near-zero impact
failures (cosmetic glitches, non-critical paths).
