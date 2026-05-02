---
layout: default
title: "PACELC"
parent: "Distributed Systems"
nav_order: 572
permalink: /distributed-systems/pacelc/
number: "0572"
category: Distributed Systems
difficulty: ★★★
depends_on: CAP Theorem, Consistency Models, Latency
used_by: Database Design, Distributed Storage, Cloud Databases
related: CAP Theorem, Consistency Models, Eventual Consistency
tags:
  - pacelc
  - cap-theorem
  - latency-consistency
  - distributed-systems
  - advanced
---

# 572 — PACELC

⚡ TL;DR — PACELC extends the CAP Theorem by acknowledging that even when there is no network partition (normal operations), distributed systems must choose between **Latency (L)** and **Consistency (C)** — specifically: if there's a Partition (P), choose between Availability (A) or Consistency (C); Else (E, normal operation), choose between Latency (L) or Consistency (C).

| #572 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | CAP Theorem, Consistency Models, Latency | |
| **Used by:** | Database Design, Distributed Storage, Cloud Databases | |
| **Related:** | CAP Theorem, Consistency Models, Eventual Consistency | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT CAP EXTENSION:**
The CAP theorem only describes behavior during partitions — but partitions are rare events.
What about the other 99.99% of the time when the network is working fine? Even without
a partition, a distributed database must wait for replication to complete before
acknowledging a write. This waiting = latency. CAP says nothing about this trade-off.
PACELC (Daniel Abadi, 2012) fills the gap: in normal operation, every distributed system
chooses between lower latency (acknowledge early, replicate asynchronously) and stronger
consistency (wait for all replicas, higher latency).

---

### 📘 Textbook Definition

**PACELC** (pronounced "pass-elk") is an extension to the CAP theorem proposed by
Daniel Abadi in 2012. It specifies behavior in TWO scenarios:
- **If Partition (P)**: must choose between Availability (A) or Consistency (C) — like CAP
- **Else (E)** (normal operation, no partition): must choose between Latency (L) or Consistency (C)

Classification: a system is **PA/EL** (partition → available; normal → low latency),
**PC/EC** (partition → consistent; normal → consistent), or hybrid combinations like
**PA/EC** (partition → available; normal → EC consistent with some latency cost).

Examples: DynamoDB = PA/EL (partition: available, normal: low latency with eventual consistency);
Spanner = PC/EC (partition: consistent, normal: consistent via TrueTime but higher latency);
Cassandra = PA/EL by default; with QUORUM = PC/EC-like.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
PACELC adds the latency-consistency dimension to CAP: even when everything works fine,
fast distributed writes trade consistency for latency (async replication vs. sync wait).

**One analogy:**
> PACELC is like a bank's wire transfer policy.
> **During outage (partition):** CP = refuse transfers OR AP = allow but might double-process.
> **During normal operation (no partition):** EC = wait 24 hours for full international clearing (consistent, slow) OR EL = process instantly (fast, but funds aren't globally reconciled for 24 hours).
> Even with no outage, speed vs. accuracy is a real trade-off.

---

### 🔩 First Principles Explanation

**THE LATENCY-CONSISTENCY TRADE-OFF (ELSE BRANCH):**

```
SYNCHRONOUS REPLICATION (EC — Else Consistent):
  Client → Leader → Write to local log
  Leader → Replica1 → ACK
  Leader → Replica2 → ACK
  Leader → ACK to Client (ALL replicas confirmed)
  
  Result: Every read from any replica sees the latest write.
  Latency: round-trip to replicas added to every write.
  Example: Google Spanner waits ~7ms for cross-zone commit.

ASYNCHRONOUS REPLICATION (EL — Else Low Latency):
  Client → Leader → Write to local log
  Leader → ACK to Client immediately (before replication)
  Leader → Replica1 → Replicate (background, 10-50ms later)
  Leader → Replica2 → Replicate (background, 10-50ms later)
  
  Result: Fast ACK to client; replicas briefly lag.
  Read from replica immediately after write: may get stale data.
  Example: MySQL async replication, Cassandra ONE consistency level.

PACELC CLASSIFICATION:
  System       | P→A/C  | E→L/C  | PACELC
  ─────────────┼────────┼────────┼────────────────────────
  DynamoDB     | PA     | EL     | PA/EL  (default)
  Spanner      | PC     | EC     | PC/EC
  Cassandra    | PA     | EL     | PA/EL  (default ONE)
  Cassandra QUORUM | PC | EC    | PC/EC  (with quorum)
  VoltDB       | PC     | EC     | PC/EC
  RIAK         | PA     | EL     | PA/EL
  MongoDB (w:majority) | PC | EC | PC/EC
```

---

### 🧪 Thought Experiment

**SCENARIO:** Multi-region database for a social media feed.

```
User posts a tweet. It's stored in US-East and replicated to EU-West and AP-Southeast.

EL CHOICE (Async replication):
  User tweets → US-East leader ACKs in 5ms → fast response
  EU-West user reads feed 100ms later: tweet not yet visible (lag)
  EU-West user reads 2 seconds later: tweet visible
  → Low latency for writer, brief staleness for readers
  → Acceptable for social feeds: 2-second staleness is imperceptible to users

EC CHOICE (Sync replication):
  User tweets → US-East must wait for EU-West (110ms RTT) + AP-Southeast (200ms RTT)
  User sees "Posted!" after 210ms (round-trip to farthest replica)
  EU-West user reads immediately: tweet visible ✓
  → Consistent, but 210ms vs 5ms write latency — 42× slower
  → Unacceptable for high-volume social applications

TWITTER/META's actual choice: EL for timeline (social feeds)
                               EC for financial transactions within the platform
Each workload gets the right PACELC classification.
```

---

### 🧠 Mental Model / Analogy

> PACELC is like a two-question filter for distributed database decisions.
> Q1 (P branch): "When the network breaks, do you want an error or stale data?"
> Q2 (E branch): "During normal operation, do you want speed or guaranteed freshness?"
> Every distributed database answers both questions. PACELC labels those answers:
> PA/EL = "available during failures, fast normally (may be stale)"
> PC/EC = "consistent during failures, correct normally (will be slower)"

---

### 📶 Gradual Depth — Four Levels

**Level 1:** PACELC says: even without failures, fast databases trade accuracy for speed. Waiting for all copies to confirm = slow but correct. Not waiting = fast but briefly inconsistent.

**Level 2:** Use PACELC to evaluate databases beyond partitions. For read-your-own-writes semantics after an insert: need EC (sync replication) or session consistency. For maximum write throughput with staleness tolerance: EL (async replication).

**Level 3:** Latency components in distributed writes: network RTT between data centers (typically 10–200ms for cross-region), disk write latency (1–10ms local SSD), consensus protocol overhead (Paxos/Raft adds ~1–3 rounds of RTT). Even "async" systems have consistency window: duration between leader write ACK and replica sync. The larger this window, the higher the staleness risk during failure.

**Level 4:** PACELC resolves the "CA vs CP vs AP" confusion from CAP by separating normal-operation trade-offs from failure-mode trade-offs. The critical insight: most of the time, systems aren't in a partition. The EL vs EC trade-off matters more often than the PA vs PC trade-off. Database families: NewSQL (Spanner, CockroachDB) aim for PC/EC using distributed consensus → strong consistency at medium latency cost; traditional NoSQL (Cassandra, DynamoDB) defaults to PA/EL → high availability at cost of temporary inconsistency. The hybrid: tunable consistency (DynamoDB strong consistent reads, Cassandra QUORUM) allows per-operation PA/EL vs PC/EC choice.

---

### ⚙️ How It Works (Mechanism)

```
LATENCY vs CONSISTENCY IN PRACTICE — MYSQL:

  SYNC REPLICATION (EC):
    primary: COMMIT → wait for binlog ACK from replica → return OK
    After commit: replica has the data immediately
    Write latency: primary commit time + network RTT to replica
    
    MySQL: rpl_semi_sync_master_enabled = ON
    → Every write waits for at least 1 replica ACK (EL→EC shift)

  ASYNC REPLICATION (EL — default):
    primary: COMMIT → return OK immediately
    Replica: receives binlog asynchronously, catches up eventually
    
    MySQL async: default configuration
    If primary crashes before replica receives log: data loss (EL risk)
    
  MEASURING THE WINDOW:
    SELECT * FROM performance_schema.replication_applier_status_by_worker;
    → Shows lag between primary and replica
    → EL window = this lag duration
    → If lag = 500ms: reads from replica may be 500ms stale
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
CHOOSING DATABASE BASED ON PACELC:

  Multi-region write-heavy workload (social feed posts):
  → PA/EL: DynamoDB (globally distributed, async replication)
  → Write in ms; brief staleness acceptable
  
  Financial ledger (bank transfers):
  → PC/EC: Spanner or CockroachDB
  → Write takes ~50ms (cross-region consensus); every read is current
  
  Configuration management (rarely written, must be consistent):
  → PC/EC: ZooKeeper or etcd
  → Writes are slow (consensus); reads always correct
  
  User sessions (write frequently, read frequently, slight staleness OK):
  → PA/EL: Cassandra ONE or DynamoDB
  → High performance; session staleness of a few seconds acceptable
```

---

### 💻 Code Example

```java
// DynamoDB — choosing EL vs EC-like per-operation
@Service
public class ProductInventoryService {

    private final DynamoDbClient dynamoDb;

    // EL: Eventually consistent read — fast, may be slightly stale
    public Optional<Product> getProductFast(String productId) {
        GetItemRequest req = GetItemRequest.builder()
            .tableName("products")
            .key(Map.of("id", AttributeValue.fromS(productId)))
            .consistentRead(false)  // ← Eventually consistent (EL — lower latency)
            .build();
        return Optional.ofNullable(dynamoDb.getItem(req).item()).map(this::toProduct);
    }

    // EC-like: Strong consistent read — more latency, guaranteed current data
    public Optional<Product> getProductAccurate(String productId) {
        GetItemRequest req = GetItemRequest.builder()
            .tableName("products")
            .key(Map.of("id", AttributeValue.fromS(productId)))
            .consistentRead(true)   // ← Strongly consistent (EC-like — higher latency)
            .build();
        return Optional.ofNullable(dynamoDb.getItem(req).item()).map(this::toProduct);
    }

    // Inventory check before purchase: use strong consistency
    public boolean checkInventoryForPurchase(String productId, int quantity) {
        Product product = getProductAccurate(productId)  // ← EC — must be current
            .orElseThrow(() -> new ProductNotFoundException(productId));
        return product.getStockCount() >= quantity;
    }

    // Browse product listing: eventual consistency is fine
    public List<Product> getProducts(List<String> ids) {
        // Eventually consistent batch read
        return ids.stream()
            .map(this::getProductFast)  // ← EL — fast browsing
            .filter(Optional::isPresent)
            .map(Optional::get)
            .collect(toList());
    }
}
```

---

### ⚖️ Comparison Table

| System | P → A/C | E → L/C | Notes |
|---|---|---|---|
| **DynamoDB (default)** | PA | EL | Eventually consistent reads/writes |
| **DynamoDB (strong reads)** | PA | EC | EC reads, 2× cost |
| **Cassandra (ONE)** | PA | EL | Fast, possibly stale |
| **Cassandra (QUORUM)** | PC | EC | Consistent, higher latency |
| **Spanner** | PC | EC | TrueTime-backed global consistency |
| **MySQL async replication** | PA | EL | Replica lag = EL window |
| **MySQL semi-sync** | PC | EC | Waits for replica ACK |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| PACELC replaces CAP | PACELC extends CAP — it adds the E (else) branch. CAP remains valid for partition behavior |
| Low latency means low consistency | Only under async replication. Systems like Spanner achieve EC at medium latency via TrueTime — consistency doesn't require extreme latency everywhere |
| The EL choice means unreliable data | EL means TEMPORARILY stale, not wrong. The inconsistency window is bounded by replication lag, typically milliseconds to seconds |

---

### 🚨 Failure Modes & Diagnosis

**Read-Your-Own-Writes Violation (EL System)**

Symptom:
User updates profile picture. Refreshes page. Old picture still showing on first refresh.

Root Cause:
Write went to leader, read routed to stale replica (EL system, within the consistency window).

Diagnosis + Fix:
```java
// Fix: route reads for the same session to the leader or use session consistency
// Option 1: DynamoDB — use strong consistent read for "own profile" reads
dynamoDb.getItem(req.consistentRead(true));  // EC for own-data reads

// Option 2: Route to primary after write (session consistency):
// Cassandra: read from same coordinator node + CL.LOCAL_QUORUM

// Option 3: Cache invalidation on write, read from cache (avoid replica lag problem)
cacheService.invalidate("user:" + userId);
```

---

### 🔗 Related Keywords

- `CAP Theorem` — the foundation PACELC extends
- `Consistency Models` — the spectrum of consistency guarantees
- `Latency` — the performance dimension PACELC adds to CAP
- `Eventual Consistency` — the consistency model of PA/EL systems

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ FORMULA      │ if Partition → A or C                     │
│              │ Else → L (latency) or C (consistency)     │
├──────────────┼───────────────────────────────────────────┤
│ PA/EL        │ Available during partition, fast normally │
│              │ DynamoDB default, Cassandra ONE           │
├──────────────┼───────────────────────────────────────────┤
│ PC/EC        │ Consistent during partition, correct norm │
│              │ Spanner, ZooKeeper, Cassandra QUORUM      │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Normal operations have latency-consistency│
│              │ trade-off too (EL vs EC)                  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "CAP covers failures; PACELC covers all" │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** A system uses DynamoDB (PA/EL) for user account data. An e-commerce company discovers
that when users update their shipping address and then immediately place an order (within
500ms), 0.3% of orders are shipped to the old address (eventual consistency read lag).
The fix seems simple: "use strongly consistent reads for the order placement read."
But the order service makes 8 DynamoDB reads during checkout. Analyze the cost 
(latency, monetary, architectural) of making all 8 reads strongly consistent vs.
making only the shipping address read consistent, and propose a PACELC-aware checkout
architecture that minimizes both the 0.3% staleness error AND the checkout latency impact.
