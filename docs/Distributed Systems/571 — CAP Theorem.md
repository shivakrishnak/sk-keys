---
layout: default
title: "CAP Theorem"
parent: "Distributed Systems"
nav_order: 571
permalink: /distributed-systems/cap-theorem/
number: "0571"
category: Distributed Systems
difficulty: ★★☆
depends_on: Distributed Systems Fundamentals, Consistency, Availability
used_by: Database Design, NoSQL, Distributed Storage
related: PACELC, Consistency Models, Eventual Consistency, BASE
tags:
  - cap-theorem
  - consistency
  - availability
  - partition-tolerance
  - distributed-systems
  - intermediate
---

# 571 — CAP Theorem

⚡ TL;DR — The CAP Theorem states that a distributed system can guarantee at most two of three properties simultaneously: **C**onsistency (every read gets the most recent write), **A**vailability (every request gets a non-error response), and **P**artition tolerance (the system works despite network partitions); since network partitions are inevitable in distributed systems, the real choice is between Consistency and Availability during a partition.

| #571 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Distributed Systems Fundamentals, Consistency, Availability | |
| **Used by:** | Database Design, NoSQL, Distributed Storage | |
| **Related:** | PACELC, Consistency Models, Eventual Consistency, BASE | |

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A distributed database team debates: "Can we have Strong Consistency, 100% Availability,
and work through network failures?" CAP theorem (Eric Brewer, 2000; formally proven by
Gilbert and Lynch, 2002) gives the definitive answer: no. Without this framework, teams
make mutually-contradictory design requirements ("the system MUST always return current
data AND must always respond AND must handle network partitions"). CAP provides a
vocabulary and framework for making explicit trade-offs rather than seeking a
provably impossible combination.

---

### 📘 Textbook Definition

**CAP Theorem** (Brewer's Theorem) states that a distributed data store can provide
at most two of the following three guarantees simultaneously:
- **Consistency (C)**: every read returns the most recent write (or an error)
- **Availability (A)**: every request receives a non-error response (not guaranteed to be the most recent data)
- **Partition Tolerance (P)**: the system operates correctly despite network partitions (arbitrary message loss or delays between nodes)

Since network partitions are inevitable in any real distributed system (networks fail,
packets drop, datacenters disconnect), partition tolerance is not optional — making the
practical trade-off **CP** (consistency during partitions, may be unavailable) versus
**AP** (available during partitions, may return stale data). CP example: Apache ZooKeeper,
HBase, Spanner. AP example: Cassandra, CouchDB, DynamoDB. CA (no partition tolerance):
only possible in a single-node system (not truly distributed).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
During a network partition, you must choose: "answer immediately (possibly stale)" (AP)
or "refuse to answer until consistent" (CP). You cannot be both simultaneously.

**One analogy:**
> CAP is like a bank during a system outage between branches.
> Branch A (London) and Branch B (New York) lose their connection.
> Option CP: refuse all transactions until connection is restored (consistency over availability).
> Option AP: allow transactions at both branches independently — but if you withdraw from
> both simultaneously before reconnection, you've overdrafted (stale data served).
> You cannot be fully consistent AND fully available during a partition.

**One insight:**
"P" (partition tolerance) is NOT a choice — it's a fact of networked systems.
Choosing "CA" means choosing a single-node system. The real decision for distributed
systems is always: "When a partition occurs, do we prefer consistency or availability?"

---

### 🔩 First Principles Explanation

**THE PARTITION SCENARIO:**

```
Normal operation (no partition):
  Node A ←────→ Node B
  Write to A: user.balance = $100
  A replicates to B
  Read from B: user.balance = $100  ← consistent ✓

Network partition (A and B cannot communicate):
  Node A        Node B
  (isolated)    (isolated)
  Write to A: user.balance = $50  (withdrawal)
  B cannot receive this update.

Decision for B when a read arrives:
  CP choice: B refuses to serve reads ("I might be stale") → 503 Service Unavailable
             → Consistent (won't return stale) 
             → NOT Available (returns error)
  
  AP choice: B serves its last known value: $100 (stale)
             → Available (returns a response)
             → NOT Consistent (returns outdated data)

After partition heals: AP systems reconcile (eventual consistency)
                       CP systems resume normal operation
```

**SYSTEM EXAMPLES:**

```
CP Systems (prefer consistency over availability):
  ZooKeeper:  Distributed coordination — must be consistent
              → returns error if quorum lost
  HBase:      Row-level ACID over HDFS → pauses writes during split-brain
  MongoDB:    Default w:majority → waits for majority acknowledgment

AP Systems (prefer availability over consistency):
  Cassandra:  Tunable consistency — default AP
              → always serves reads, reconciles later (LWW or CRDT)
  DynamoDB:   Eventually consistent reads (AP) + strongly consistent reads (CP) option
  CouchDB:    Multi-master replication, conflict resolution application-level

CA (only in single-node / non-partitioned environments):
  Single-node PostgreSQL: not truly distributed, so CA holds
  → Add replication → now a distributed system → P becomes relevant
```

---

### 🧪 Thought Experiment

**SCENARIO:** Shopping cart during a network partition.

```
User's cart is stored in a distributed DB across 2 regions: US-East and EU-West.
Network partition: US-East and EU-West cannot communicate.

CP CHOICE:
  User in US adds item to cart
  US-East cannot confirm with EU-West
  Checkout fails: "Service temporarily unavailable — please try again"
  User: angry but balance is always accurate
  
AP CHOICE:
  User in US adds item to cart → cart updated in US-East
  Simultaneously, in EU-West (family member) removes same item
  Both succeed independently (available!)
  When partition heals: two conflicting cart states must be reconciled
  Amazon's Dynamo paper: "last-writer-wins" or application-level conflict resolution

AMAZON'S DECISION (from Dynamo paper):
  Amazon chose AP for shopping carts: "adding to a cart that is slightly out of date
  is better than not being able to add to the cart at all." Better user experience
  to resolve rare conflicts than to show errors frequently.
```

---

### 🧠 Mental Model / Analogy

> CAP Theorem is like a customer service guarantee during a communication outage.
> Promise 1 (C): "We'll only tell you the current truth." → During outage: silence (unavailable).
> Promise 2 (A): "We'll always answer you." → During outage: possibly outdated answer.  
> Both simultaneously: impossible. You either give an answer (possibly stale) or refuse to answer (unavailable).
> "P" (the network partition) is not a choice — it happens regardless.
> The only choice is HOW you respond when it happens.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** In distributed systems, when the network fails between nodes, you can either be correct (but might not respond) or always respond (but might be slightly wrong). You can't be both perfectly right AND always responsive during a network failure.

**Level 2:** Use CAP to choose your database: if data accuracy is critical (banking, inventory) → CP (reject during partitions). If availability is more important than immediate accuracy (shopping cart, session data, social feeds) → AP (serve possibly stale, reconcile later).

**Level 3:** "Partition tolerance" is not optional — it's the axiom of distributed systems. The formal proof (Gilbert-Lynch 2002) shows that no protocol can be both CA in an asynchronous network with possible failures. PACELC extends CAP by noting: even without partitions, the latency-consistency trade-off exists. Real database configuration: CassandraConsistencyLevel tuning — `ONE` (AP), `QUORUM` (middle ground), `ALL` (effectively CP).

**Level 4:** Brewer later acknowledged that CAP is often misapplied. "CA" isn't a real option for distributed systems. "C" in CAP is linearizability (very specific, strong consistency), not just "consistent" in a generic sense. Kyle Kingsbury's Jepsen testing framework has empirically tested dozens of databases, showing many claim CAP properties they don't deliver under partition testing. PACELC (2012, Daniel Abadi) is considered a more nuanced model: acknowledges that the latency-consistency trade-off exists even in the absence of partitions — the real design space is a multi-dimensional spectrum, not a binary choice.

---

### ⚙️ How It Works (Mechanism)

```
CONSISTENCY LEVELS IN CASSANDRA (tunable CAP):

  Cassandra: AP system by default. Tunable per-operation:

  ONE  → Read from 1 replica. Fast, low latency, may be stale. (AP)
  TWO  → Read from 2 replicas. Higher consistency. Middle ground.
  QUORUM → Read from majority (N/2 + 1 replicas). Strong consistency if:
           Write QUORUM + Read QUORUM > N replicas.
           This gives CP-like consistency.
  ALL  → Read from all N replicas. Max consistency. Any replica unavailable = error (CP).

  Write consistency levels: same options.
  
  Rule for strong consistency:
  W + R > N   (write replicas + read replicas > total replicas)
  Example: N=3 → W=2 + R=2 = 4 > 3 ✓ → Strong consistency via quorum overlap

  Partition scenario with QUORUM:
  N=3, one node in network partition:
  → QUORUM=2 (majority) still available → reads/writes succeed
  → But if 2+ nodes partitioned → QUORUM fails → CP behavior kicks in
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
CAP IN DATABASE SELECTION:

DECISION TREE:
  Is data accuracy on reads critical?
  (banking, inventory, financial ledger, tickets/reservations)
          │
          YES → CP → ZooKeeper, HBase, MongoDB (w:majority), Spanner
          │    Partition: return error, not stale data
          │
          NO → Can serve slightly stale data for availability?
          (shopping cart, user sessions, social feeds, config flags)
                    │
                    YES → AP → Cassandra, DynamoDB, CouchDB
                    │    Partition: always respond, reconcile later
```

---

### 💻 Code Example

```java
// Cassandra consistency level selection (CP vs AP trade-off in code)
@Repository
public class UserRepository {

    private final CqlSession session;

    // AP: Read ONE replica — fast, possibly stale (for non-critical reads)
    public Optional<User> findByIdEventuallyConsistent(UUID userId) {
        SimpleStatement query = QueryBuilder.selectFrom("users")
            .all()
            .whereColumn("id").isEqualTo(QueryBuilder.literal(userId))
            .build()
            .setConsistencyLevel(ConsistencyLevel.ONE);  // ← AP
        return Optional.ofNullable(session.execute(query).one())
            .map(this::toUser);
    }

    // CP: Read QUORUM — consistent, fails if majority unavailable
    public Optional<User> findByIdConsistently(UUID userId) {
        SimpleStatement query = QueryBuilder.selectFrom("users")
            .all()
            .whereColumn("id").isEqualTo(QueryBuilder.literal(userId))
            .build()
            .setConsistencyLevel(ConsistencyLevel.QUORUM);  // ← CP-like
        return Optional.ofNullable(session.execute(query).one())
            .map(this::toUser);
    }

    // Critical: balance operations use QUORUM for strong consistency
    public void updateBalance(UUID userId, BigDecimal newBalance) {
        Statement update = QueryBuilder.update("users")
            .setColumn("balance", QueryBuilder.literal(newBalance))
            .whereColumn("id").isEqualTo(QueryBuilder.literal(userId))
            .build()
            .setConsistencyLevel(ConsistencyLevel.QUORUM);  // ← Ensures majority sees write
        session.execute(update);
    }
}
```

---

### ⚖️ Comparison Table

| System | CAP Type | Partition Behavior | Example Use Case |
|---|---|---|---|
| **ZooKeeper** | CP | Returns error if quorum lost | Distributed consensus, leader election |
| **Cassandra** | AP (tunable) | Returns last-known data | Social feeds, user sessions |
| **HBase** | CP | Pauses for consistency | Time-series analytics |
| **DynamoDB** | AP (default) / CP (strong) | Eventually consistent / consistent read option | Shopping cart (AP) or transactional (CP) |
| **Spanner** | CP | Globally consistent; uses TrueTime | Financial transactions |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| CA is a valid choice for distributed systems | CA is only possible for single-node systems. Any distributed system with network communication faces partitions — P is mandatory |
| CAP "C" means any kind of consistency | CAP "C" specifically means linearizability — the strongest consistency model. Many "consistent" databases don't provide linearizability |
| AP systems are always inconsistent | AP systems are eventually consistent — they converge to the correct state after partition heals. The window of inconsistency can be very small |

---

### 🚨 Failure Modes & Diagnosis

**Treating AP as CP (Data Loss)**

Symptom:
Double-entry in financial system: two withdrawals process simultaneously in separate
data centers during a brief network partition. Account balance goes negative.

Root Cause:
AP Cassandra used for transactional financial data without application-level conflict
detection.

Fix:
```
For financial data: use CP system (SQL with SERIALIZABLE isolation, or Spanner)
OR: use AP with application-level optimistic locking:
    - Check-and-Set (CAS) operation in Cassandra:
      UPDATE accounts SET balance = 500 WHERE id = ? IF balance = 600
      (Compare-And-Swap — lightweight transaction in Cassandra using Paxos)
    → Only one succeeds; other gets "applied: false" → retry
```

---

### 🔗 Related Keywords

- `PACELC` — extends CAP to latency-consistency trade-off during normal operation
- `Consistency Models` — the spectrum from linearizability to eventual consistency
- `BASE` — the AP equivalent of ACID (Basically Available, Soft state, Eventually consistent)
- `Eventual Consistency` — the consistency model chosen by AP systems

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Distributed systems can have at most 2 of│
│              │ Consistency, Availability, Partition Tol │
├──────────────┼───────────────────────────────────────────┤
│ REAL CHOICE  │ P is mandatory (networks fail)           │
│              │ Choose: CP or AP during partitions        │
├──────────────┼───────────────────────────────────────────┤
│ CP EXAMPLES  │ ZooKeeper, HBase, Spanner               │
│ AP EXAMPLES  │ Cassandra, DynamoDB (default), CouchDB   │
├──────────────┼───────────────────────────────────────────┤
│ DECISION     │ Critical accuracy → CP                   │
│              │ High availability → AP + reconciliation  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Partition happens; pick consistent or available"│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** You're designing a distributed inventory system for an e-commerce company selling
limited-edition sneakers (1,000 units, expected 50,000 concurrent buyers on release day).
The two worst outcomes are: (A) overselling (selling 1,200 units you only have 1,000 of),
or (B) under-selling (failing to sell 200 available units due to false "out of stock" errors).
Evaluate both outcomes for the business, classify each as a CP vs AP failure mode,
and make a concrete database architecture recommendation that balances the risk of both —
including whether a brief CP-safe window during the sale flash moment is acceptable.
