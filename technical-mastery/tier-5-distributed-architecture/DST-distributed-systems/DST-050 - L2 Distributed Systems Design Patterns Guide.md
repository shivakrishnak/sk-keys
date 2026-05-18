---
id: DST-050
title: "L2 Distributed Systems Design Patterns Guide"
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-041, DST-042, DST-043, DST-044, DST-045, DST-046, DST-047, DST-048, DST-049
used_by: []
related: DST-024, DST-025, DST-040
tags:
  - meta
  - l2
  - design-patterns
  - reference
  - distributed
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 50
permalink: /technical-mastery/distributed-systems/l2-design-patterns-guide/
---

⚡ TL;DR - This META guide consolidates the L2 (★★☆)
distributed systems design patterns into decision
frameworks for system design interviews and production
architecture work; covers when to use Raft vs Paxos,
Saga vs 2PC, CQRS vs traditional, Event Sourcing vs
CRUD, distributed locking vs optimistic locking,
leader election vs stateless design, and how these
patterns compose in production systems.

---

### 📋 Entry Metadata

| #050 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Type:** | META - Design Patterns Reference | |
| **Covers:** | DST-041 through DST-049 (L2 consensus + patterns) | |
| **See Also:** | L1 Guide (DST-024), L2 Interview (DST-040) | |

---

### 🎯 How to Use This Guide

This guide is a decision framework and composition
map. For each pattern covered in DST-041 through
DST-049, it answers:
1. **When to use it** (and when NOT to)
2. **What it costs**
3. **What it requires to be safe**
4. **How it composes with other patterns**

---

### 🗺️ L2 Pattern Landscape

```
CONSENSUS (single value/leader agreement):
  Raft (DST-041) ─────────────────┐
  Paxos (DST-042) ─────────────────┤ Foundation for
                                   │ Leader Election
                                     (DST-046)
                                   │ which enables
                                   │ Distributed Locking
                                     (DST-049)
                                   │ and prevents
                                   └─ Split-Brain (DST-048)
                                      + Fencing Token
                                        (DST-047)

DISTRIBUTED TRANSACTIONS:
  Saga Pattern (DST-043) ──────────┐
  ├─ Choreography                  │ Replaces
  └─ Orchestration                 │ Two-Phase Commit
    (DST-033)
                                   │ across service
                                     boundaries
  CQRS (DST-044) ──────────────────┤
  └─ Event Sourcing (DST-045) ─────┘
       └─ Audit + temporal queries
```

---

### 🧭 Pattern Decision Guide

---

### Consensus: Raft vs Paxos

**Choose Raft when:**
- You need replicated log consensus in a new system
- Understandability and correctness of implementation
  matter more than theoretical optimality
- The system needs a clear leader model
- You want production-ready implementations
  (etcd, CockroachDB, TiKV)

**Choose Paxos when:**
- You are using an existing system built on Paxos
  (Google Chubby, ZooKeeper's ZAB variant)
- You need to understand the theoretical foundations
  of Raft (Raft IS Multi-Paxos with constraints)
- You are in an academic context or building a
  research system

**The real answer:** Use etcd or ZooKeeper. Neither
Raft nor Paxos needs to be implemented from scratch
in production. The choice is which library/service
to use, not which algorithm to code.

```
Raft-based:
  etcd          → Kubernetes, Consul
  CockroachDB   → NewSQL database
  TiKV          → TiDB key-value store

ZAB (Paxos variant):
  ZooKeeper     → Kafka, HBase coordination

Paxos-based:
  Google Chubby → Internal (not public)
  Google Spanner→ External time-based variant
```

---

### Distributed Transactions: Saga vs 2PC

**Choose Saga when:**
- Operations span multiple services (microservices)
- Each service has its own database
- External systems are involved (payment gateway)
- Long-running operations (minutes, not milliseconds)
- Eventual consistency is acceptable

**Choose 2PC when:**
- All operations are in one database (XA transactions)
- You need strong ACID atomicity
- The transaction is short-lived (< 1 second)
- All participants support XA protocol
- Blocking on coordinator failure is acceptable

**The real answer:** In microservices, 2PC is
almost never the right choice. Use Saga.
In single-database operations, use a regular
transaction (not even 2PC).

```
SCENARIO                          CHOICE
-----------------------------------------------------------
Place order (Order+Inventory+Pay) Saga (cross-service)
Transfer between bank accounts    DB transaction (single
  DB)
Multi-database write in monolith  2PC (if same org
  controls both)
Long-running business process     Saga (with orchestrator)
```

---

### Read/Write: CQRS vs Traditional

**Choose CQRS when:**
- Read:write ratio > 10:1
- Different queries need different data shapes
- Read model benefits from non-relational storage
  (Elasticsearch, Redis, Cassandra)
- Complex reporting/analytics needs separate pipeline
- You already emit events for other purposes

**Choose Traditional (shared model) when:**
- CRUD with uniform read/write access patterns
- Low traffic (< 1000 req/s total)
- Consistency is critical (every read must see latest)
- Team is small and cannot afford operational overhead
- Fast iteration is prioritized over scale

```
TRAFFIC    READ:WRITE    CONSISTENCY   → CHOICE
< 1K rps   1:1           Strong        → Traditional
< 1K rps   10:1          Eventual      → Traditional or
  light CQRS
> 10K rps  10:1          Eventual OK   → CQRS
> 10K rps  1:1           Strong        → Traditional +
  read replicas
Any        100:1         Eventual OK   → CQRS +
  specialized read store
```

---

### State Management: Event Sourcing vs CRUD

**Choose Event Sourcing when:**
- Audit trail is a legal or business requirement
- Temporal queries (state at time T) are needed
- Event-driven integration is central to the system
- Debugging complex state transitions is important
- Multiple read models need to be derived from
  the same state changes

**Choose CRUD when:**
- Standard state management is sufficient
- No audit requirements
- Team is not experienced with event sourcing
- Schema evolution of events would be frequent
- Quick iteration is needed

**Warning signs that CRUD is struggling (consider ES):**
- "How did this record get into this state?"
  happens weekly
- Audit tables added as afterthought (messy)
- Multiple downstream systems need event notifications
  from database changes

```
If you need audit: Event Sourcing OR audit log table
If you need replay: Event Sourcing only
If you need simplicity: CRUD + audit log table
If you need all benefits: Event Sourcing (with cost)
```

---

### Coordination: Leader Election vs Stateless

**Choose Leader Election when:**
- Exactly one node must perform a task
- The task cannot be parallelized or de-duplicated
- Examples: scheduled job, Kafka controller, primary DB

**Design stateless (no election needed) when:**
- Every node can handle every request independently
- Requests are idempotent and can be retried anywhere
- Examples: API handlers, stateless microservices

**The real goal:** minimize the need for leader
election by designing stateless. Every stateful
coordination point (leader) is a potential failure
domain. Where possible:
- Use idempotent operations + at-least-once delivery
- Use distributed queues (Kafka) to distribute work
- Use database-based coordination (advisory locks)
  rather than external coordination services

---

### Mutual Exclusion: Distributed Lock vs Optimistic

**Choose Distributed Lock when:**
- Multiple processes could interfere on the same resource
- Side effects are non-idempotent (external API call)
- The operation cannot be safely retried on conflict
- Lock hold time is short (< TTL/10)

**Choose Optimistic Locking when:**
- Conflicts are rare (< 5% of requests)
- The operation is database-centric
- You want to avoid lock contention overhead
- On conflict: retry is acceptable

```python
# OPTIMISTIC LOCKING (database version check):
# No lock needed; detect conflict at write time

UPDATE orders
SET status = 'SHIPPED', version = version + 1
WHERE id = :order_id
  AND version = :expected_version  # Conflict check
-- 0 rows updated → conflict → reload and retry
```

**The often-correct answer:** optimistic locking
for most inventory/status updates; distributed lock
only for external API calls that cannot be retried.

---

### 🔗 Pattern Composition in Production

**Pattern: Distributed Job with Exactly-Once Execution**

```
Problem: 10 pods, nightly report job must run once.

Components:
  1. Leader Election (DST-046): elect one pod as
     job coordinator via etcd CAS lease.
  2. Fencing Token (DST-047): coordinator uses etcd
     revision as token; includes in job record write.
  3. Idempotency (DST-018): job writes include token;
     storage rejects stale (paused) coordinator's write.

Flow:
  → All pods race to acquire etcd lease.
  → One pod wins (token=42).
  → Winner starts job.
  → If winner GC-pauses beyond TTL:
    another pod wins (token=43).
  → Old winner resumes with token=42:
    storage rejects writes (42 < 43).
  → Old winner detects rejection, stops.
```

**Pattern: Multi-Service Order Flow**

```
Problem: Place order across Order+Inventory+Payment.

Components:
  1. Saga Pattern (DST-043): Orchestration-based saga.
  2. Idempotency (DST-018): each step keyed on saga_id.
  3. CQRS (DST-044): separate order query service with
     Elasticsearch read model.
  4. Event Sourcing (DST-045): order lifecycle as
     event log (OrderPlaced, PaymentCharged, Shipped).

Flow:
  → Command: PlaceOrder arrives at Saga Orchestrator.
  → Saga emits events: OrderPlaced, InventoryReserved.
  → If PaymentFailed: compensate (ReleaseInventory,
    OrderCancelled events appended to event store).
  → Read model projector builds order summary view.
  → Events published to Kafka → audit log, analytics.
```

**Pattern: Database Primary Failover**

```
Problem: PostgreSQL primary fails; promote replica safely.

Components:
  1. Heartbeat/Health Check (DST-020): detect failure.
  2. Leader Election (DST-046): Patroni acquires etcd
     leader key before promoting replica.
  3. Split-Brain prevention (DST-048): old primary
     checks etcd lease; if lost, refuses writes.
  4. Fencing Token (DST-047): etcd revision as token;
     Patroni enforces on any write to shared state.

Flow:
  → Primary fails to renew etcd lease (crash/partition).
  → Lease expires after TTL (10s).
  → Replica: etcd key gone → acquires new key (token=101).
  → Replica: promotes self to primary.
  → Old primary recovers: checks etcd → sees token=101 >
    its token=100 → steps down → becomes replica.
```

---

### 📊 Pattern Cost Matrix

| Pattern | Operational Cost | Consistency | Latency Impact | When Worth It |
|---|---|---|---|---|
| Raft/etcd | Medium (infra) | Strong | +1 RTT per write | Always for coordination |
| Saga | High (compensations, DLQ) | Eventual | Multiple steps | Cross-service transactions |
| CQRS | High (two models, sync) | Eventual | Reads fast, writes same | High read:write asymmetry |
| Event Sourcing | Very High (schema evo) | Eventual | Replay overhead | Audit/legal requirement |
| Leader Election | Low-Medium | Strong | Election TTL | Exactly-once execution |
| Distributed Lock | Medium (TTL, fencing) | Strong | Lock wait overhead | Non-idempotent critical section |
| Optimistic Locking | Low | Strong | Retry cost | Low-conflict state updates |

---

### 🚨 Common Anti-Patterns

**Anti-pattern 1: Distributed Lock Without Fencing**

Using Redis SETNX for inventory control with no
fencing token check in the database write. JVM GC
pause causes lock expiry mid-write. Fix: ADD fencing
token to every locked write operation.

**Anti-pattern 2: Saga Without Compensation Tests**

Building a Saga but never testing the failure path.
Compensating transactions written but never exercised
in staging. First test happens in production. Fix:
chaos engineering tests that force step failures.

**Anti-pattern 3: CQRS for Simple CRUD**

Applying CQRS to a low-traffic TODO app because
the architecture guide recommends it. Read model
is always in sync with write model (sync projection).
Two codepaths, double the bugs, no benefit. Fix:
use CQRS only when the pain of a shared model is
felt, not as a default architecture.

**Anti-pattern 4: Event Sourcing Without Snapshots**

10,000 events per order aggregate. Loading any order
requires replaying 10,000 events (O(N)). Query
performance degrades as system ages. Fix: implement
snapshots at N events (N=100-500 is common).

**Anti-pattern 5: Leader Election Without Timeout**

A leader election system with no TTL on the lease.
Leader crashes. No new leader ever elected. The
cluster is permanently leaderless. Fix: always use
TTL-bounded leases; always test leader failure recovery.

---

### ✅ L2 Design Mastery Checklist

**Consensus:**
- [ ] Describe the Raft leader election and log
  replication flow without looking
- [ ] Name three production systems that use Raft
  and two that use Paxos (or ZAB)

**Transactions:**
- [ ] For a cross-service order flow, design a Saga
  with compensation transactions for each step
- [ ] Identify the pivot point in the Saga

**Read/Write Patterns:**
- [ ] Identify the three signals that indicate CQRS
  is worth the complexity
- [ ] Design a CQRS projection pipeline from command
  to read model, including the event bus

**State:**
- [ ] Implement a basic event-sourced aggregate with
  snapshot support
- [ ] List two scenarios where an audit log table
  is better than full Event Sourcing

**Coordination:**
- [ ] Implement leader election using etcd CAS with
  lease renewal
- [ ] Explain why fencing is required even with
  correct leader election

**Locking:**
- [ ] Write a Redis distributed lock with Lua script
  release and fencing token
- [ ] For a given scenario, decide between distributed
  lock and optimistic locking with justification

**Failure Modes:**
- [ ] Describe split-brain, its cause, and three
  prevention mechanisms
- [ ] Explain why a healthy isolated node is more
  dangerous than a crashed one
