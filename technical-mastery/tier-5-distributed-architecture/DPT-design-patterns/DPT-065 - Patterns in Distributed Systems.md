---
id: DPT-065
title: Patterns in Distributed Systems
category: Design Patterns
tier: tier-5-distributed-architecture
folder: DPT-design-patterns
difficulty: ★★★
depends_on: DPT-001, DPT-064
used_by: []
related: DPT-052, DPT-053, DPT-054, DPT-055, DPT-057
tags:
  - concept
  - distributed-systems
  - advanced
  - system-design
  - microservices
  - architecture
status: complete
version: 4
layout: default
parent: "Design Patterns"
grand_parent: "Technical Mastery"
nav_order: 65
permalink: /technical-mastery/design-patterns/patterns-in-distributed-systems/
---

⚡ TL;DR - Distributed systems introduce a new class of
problems (partial failure, network unreliability, consistency
across nodes) that require a different pattern vocabulary
from class-level GoF patterns. The distributed pattern
vocabulary addresses consistency, availability, isolation,
and communication guarantees at the service boundary level.

| #65 | Category: Design Patterns | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | DPT-001, DPT-064 | |
| **Used by:** | N/A | |
| **Related:** | DPT-052, DPT-053, DPT-054, DPT-055, DPT-057 | |

---

### 🔥 The Problem This Solves

**THE CLASS-LEVEL PATTERN BLIND SPOT:**
An engineer knows the GoF patterns deeply. They are building
a distributed system. They apply the Observer Pattern
for event notifications. They apply the Command Pattern
for operations. Then the system enters production:

- A payment message is delivered twice (no idempotency)
- An order is created but payment notification is lost
  (no delivery guarantee)
- Service A hangs when Service B is slow (no isolation)
- An order shows "confirmed" but inventory shows "not reserved"
  (consistency violation)

None of these failures are addressed by GoF patterns.
GoF patterns operate within a single process. Distributed
systems failures happen AT THE PROCESS BOUNDARY.

**THE DISTRIBUTED PATTERN GAP:**
A new vocabulary is needed for the class of problems that
only exist in distributed systems: partial failure, eventual
consistency, guaranteed delivery, service isolation.

---

### 📘 Textbook Definition

**Patterns in Distributed Systems** are design patterns
that specifically address the challenges introduced by
multi-process, network-separated components. These patterns
address:

1. **Communication reliability**: How to ensure a message
   is delivered exactly once (or at least once) across
   a network that may drop, duplicate, or reorder messages.

2. **Consistency across services**: How to maintain
   consistent state across services that have separate
   databases and cannot participate in a single transaction.

3. **Failure isolation**: How to prevent a failure in
   one service from propagating to other services or
   to the entire system.

4. **Observability**: How to trace, monitor, and debug
   a request that spans multiple services.

5. **Deployment and migration**: How to evolve a distributed
   system incrementally without taking the entire system
   offline.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Distributed patterns address problems that cannot exist
in a single process: partial failure, delivery guarantees,
cross-service consistency, and failure isolation.

**One analogy:**
> A single office building has one HR system, one payroll
> system, and one floor plan. If the payroll system fails:
> you can rollback the transaction. Nothing is "lost."
>
> A company with 5 offices in 5 countries: the offices
> have separate HR systems, separate payroll systems,
> and communicate over unreliable international phone
> lines. A salary increase approved in New York might
> not reach Tokyo for 2 hours. Or the call drops entirely
> (network failure). Managing state consistency across
> these offices requires a different set of "patterns"
> than managing state within one office building.
>
> Distributed systems = the 5-office company.
> GoF patterns = the one-office building rules.
> Distributed patterns = the rules for 5-office coordination.

---

### 🔩 First Principles Explanation

**THE EIGHT FALLACIES OF DISTRIBUTED COMPUTING:**
(Originally by Peter Deutsch, Sun Microsystems)
Every distributed system must plan for these being false:
1. The network is reliable
2. Latency is zero
3. Bandwidth is infinite
4. The network is secure
5. Topology doesn't change
6. There is one administrator
7. Transport cost is zero
8. The network is homogeneous

Distributed patterns exist specifically because these
fallacies are false. Each pattern addresses one or more:

**Fallacy 1 (network unreliable) → Outbox Pattern:**
Don't rely on a network call to guarantee delivery.
Write to a local database atomically. A relay process
delivers asynchronously.

**Fallacy 1 + 2 (unreliable + latency) → Circuit Breaker:**
When a remote service is unavailable or slow: fail fast
rather than waiting for a timeout that may never come.

**Fallacy 1 (unreliable) → Idempotency Pattern:**
Networks may deliver a message more than once (retry
after timeout without confirmation). The receiving
service must handle duplicates safely.

**THE CONSISTENCY SPECTRUM:**
Distributed systems cannot have all of: Consistency,
Availability, Partition Tolerance (CAP theorem).
Most distributed patterns operate in the eventual
consistency model (choosing Availability + Partition
Tolerance over strong Consistency). Understanding which
pattern provides which consistency model is essential:

| Pattern | Consistency Model |
|---|---|
| Outbox | At-least-once delivery; idempotent consumers required |
| Saga | Eventual consistency across services; compensating transactions |
| CQRS | Read model: eventual consistency (< N ms). Write: strong |
| Circuit Breaker | Availability over consistency during failure |
| Leader Election | Strong consistency for the election; availability tradeoff |

---

### 🧪 Thought Experiment

**DECOMPOSING A DISTRIBUTED ORDER FLOW BY PATTERN:**

Order placed by customer. Multi-service flow:
- Create order in Order DB
- Charge payment in Payment Service
- Reserve inventory in Inventory Service
- Send confirmation email in Notification Service

**WITHOUT DISTRIBUTED PATTERNS:**
All calls are synchronous HTTP. Order creation is a
sequential chain: create → charge → reserve → notify.
Failures: payment fails → order created but not charged
(inconsistent state). Inventory fails → order charged
but not reserved (double loss). No compensation.
Service B slow → Service A threads exhausted (cascading).

**WITH DISTRIBUTED PATTERNS:**

Step 1: Create order + enqueue payment event atomically.
Pattern: **Outbox** → guarantees the event is delivered
even if the process crashes after the DB write.

Step 2: Multi-service coordination.
Pattern: **Saga (choreography)** → each service handles
its step and publishes an event. If any step fails:
compensating events are published to reverse prior steps.

Step 3: Payment service failure isolation.
Pattern: **Circuit Breaker** → if payment is down,
orders are queued rather than hanging the order service.

Step 4: Notification email.
Pattern: **Retry with idempotency** → email may be sent
twice if the notification service crashes between send
and ack. Idempotency key prevents duplicate emails.

Each pattern addresses a specific distributed systems
tension in the flow.

---

### 🧠 Mental Model / Analogy

> Distributed patterns = "postal service rules" model.
> A letter delivery service must plan for:
> - Letters that get lost in transit (Outbox: write locally, relay)
> - Letters delivered twice (Idempotency: deduplicate)
> - Post offices that temporarily close (Circuit Breaker: fail fast)
> - Multi-leg deliveries where one leg fails (Saga: compensate)
> - Reading from branch offices not yet updated (CQRS: eventual consistency)
>
> None of these concerns exist if you hand-deliver a letter
> in the same room (single process). They all exist in a
> postal system (distributed system). Distributed patterns
> are the standard operating procedures of the postal service.

---

### 📶 Gradual Depth - Three Levels

**Level 1 - Core distributed patterns map:**
Six patterns every distributed systems engineer must know:
1. Outbox: atomic write + guaranteed delivery
2. Saga: multi-service transaction with compensation
3. CQRS: read/write separation for independent scaling
4. Circuit Breaker: fail fast on downstream failure
5. Idempotency: safe retry for non-atomic operations
6. Strangler Fig: incremental migration from legacy

**Level 2 - Pattern interaction:**
Patterns compose. Outbox + Idempotency: the Outbox delivers
at-least-once; idempotent consumers handle the duplicates.
Saga + Outbox: each Saga step publishes events through
the Outbox for guaranteed delivery. Circuit Breaker +
Retry: Retry handles transient single failures; Circuit
Breaker handles sustained failures.

**Level 3 - Pattern selection by CAP trade-off:**
Each distributed pattern makes an explicit CAP trade-off.
Choosing a pattern means choosing a consistency model.
CQRS: trades consistency for scalability (read model
is eventually consistent). Saga: trades strong consistency
for availability (no distributed locks). Circuit Breaker:
trades consistency for availability (serves stale data
or degraded response when downstream is down). Understanding
the trade-off embedded in each pattern enables informed
architectural decisions.

---

### ⚙️ How It Works (Mechanism)

```
Distributed Patterns Taxonomy
┌─────────────────────────────────────────────────────────┐
│ CONSISTENCY PATTERNS                                    │
│   Outbox: atomic local write + guaranteed relay         │
│   Saga: distributed tx with compensating transactions   │
│   CQRS: read/write separation with projection model    │
│   Idempotency: safe-to-retry operations                │
│   Two-Phase Commit: synchronous distributed tx (rare)  │
│                                                         │
│ RESILIENCE PATTERNS                                     │
│   Circuit Breaker: fail fast on sustained failure      │
│   Bulkhead: thread/resource isolation by downstream    │
│   Retry+Backoff+Jitter: handle transient failures      │
│   Timeout+Deadline: bound unbounded waits              │
│   Health Check: detect unhealthy instances             │
│                                                         │
│ MIGRATION PATTERNS                                      │
│   Strangler Fig: incremental rewrite alongside legacy  │
│   Anti-Corruption Layer: translate between models      │
│   Branch by Abstraction: behind abstraction interface  │
│                                                         │
│ INFRASTRUCTURE PATTERNS                                 │
│   Sidecar: co-located helper container                 │
│   Ambassador: outbound proxy sidecar                   │
│   Service Mesh: infrastructure-level resilience        │
│   Leader Election: single coordinator in cluster      │
└─────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Selecting patterns for a distributed flow:**

```
ARCHITECTURE DECISION: Payment processing in a
  microservice system

TENSION 1: Order write must atomically trigger payment
  event.
  If the order is written but the event is lost: 
  order exists, payment never starts.
→ PATTERN: Outbox
  Outbox writes order and payment event to the same DB tx.
  Relay delivers the event. Atomicity guaranteed locally.

TENSION 2: Payment → Inventory → Notification must be
  atomic.
  If payment succeeds but inventory fails: inconsistent
    state.
  Cannot use 2PC (three separate services and databases).
→ PATTERN: Saga (choreography)
  Each step publishes success/failure event.
  Failure triggers compensating events (refund payment,
  release inventory reservation).

TENSION 3: Payment service may be slow or unavailable.
  Order service must not block indefinitely.
→ PATTERN: Circuit Breaker + Bulkhead
  CB: fail fast after threshold.
  Bulkhead: payment calls use a separate thread pool;
  slowness does not affect inventory calls.

TENSION 4: Notification email may be delivered twice
  (Outbox at-least-once delivery).
→ PATTERN: Idempotency
  Notification service deduplicates by order ID.
  Idempotency key: orderId + notificationType.

RESULT: Consistent distributed flow with explicit
guarantees and failure modes for each boundary.
```

---

### ⚖️ Distributed Pattern Trade-offs

| Pattern | Guarantees | Trade-off | When to Use |
|---|---|---|---|
| Outbox | At-least-once delivery, atomic write | Relay process, DB polling overhead | Write + notify across service boundary |
| Saga | Multi-service coordination, compensation | Eventual consistency, complex compensation logic | Multi-step business process across services |
| CQRS | Read/write independent scaling | Read model staleness, projection lag | High read/write ratio imbalance |
| Circuit Breaker | Fast failure, resource preservation | False positives, degraded mode behavior | Calls to any external service |
| Idempotency | Safe retry, no duplicate side effects | Deduplication storage, key management | Any at-least-once delivery scenario |
| Strangler Fig | Incremental migration, rollback ability | Long-running parallel operation cost | Legacy migration without big-bang rewrite |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| GoF patterns are sufficient for microservices | GoF patterns operate within a single process. Distributed patterns address cross-process failures (network unreliability, partial failure, delivery guarantees). Both are needed; they address different levels |
| Eventual consistency is a weakness | Eventual consistency is a trade-off, not a failure. It enables higher availability and scalability than strong consistency. The question is: which operations require strong consistency, and which can tolerate eventual consistency? Most operations in e-commerce are safely eventually consistent |
| Circuit Breaker prevents failures | Circuit Breaker prevents CASCADING failures and resource exhaustion. The underlying service is still failing. Circuit Breaker gives it room to recover and prevents the failure from spreading |
| All microservices need all distributed patterns | Apply patterns to the specific tensions that exist. A service that does only reads (no writes across service boundaries) does not need Saga. A service that makes no external calls does not need Circuit Breaker. Pattern selection is tension-driven |

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ CORE 6       │ Outbox / Saga / CQRS / Circuit Breaker / │
│ PATTERNS     │ Idempotency / Strangler Fig              │
├──────────────┼──────────────────────────────────────────┤
│ CONSISTENCY  │ Outbox: at-least-once + Idempotency     │
│              │ Saga: eventual consistency + compensation│
├──────────────┼──────────────────────────────────────────┤
│ RESILIENCE   │ CB + Bulkhead + Retry (+jitter)         │
│              │ = complete resilience strategy           │
├──────────────┼──────────────────────────────────────────┤
│ FALLACIES    │ Plan for: network unreliable, latency    │
│              │ non-zero, messages duplicated            │
├──────────────┼──────────────────────────────────────────┤
│ CAP TRADEOFF │ Most patterns choose AP over C.         │
│              │ Know which consistency model each gives  │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ DPT-066: Pattern Language Theory -      │
│              │ Christopher Alexander                   │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. GoF patterns = within a process. Distributed patterns =
   across process boundaries. Different problem classes
   require different pattern vocabularies. Knowing one
   set does not substitute for the other.
2. The six core distributed patterns: Outbox (delivery
   guarantee), Saga (multi-service consistency), CQRS
   (read/write scaling), Circuit Breaker (failure isolation),
   Idempotency (safe retry), Strangler Fig (migration).
3. Every distributed pattern makes a CAP trade-off. Most
   choose availability + partition tolerance over strong
   consistency. The specific trade-off of each pattern
   must be understood and explicitly accepted in the design.

