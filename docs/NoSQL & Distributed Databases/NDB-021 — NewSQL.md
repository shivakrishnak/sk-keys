---
layout: default
title: "NewSQL"
parent: "NoSQL & Distributed Databases"
nav_order: 21
permalink: /nosql/newsql/
number: "NDB-021"
category: NoSQL & Distributed Databases
difficulty: ★★★
depends_on: Database Sharding, CAP Theorem (DB), ACID
used_by: System Design, Distributed Transactions, Microservices
related: Database Sharding, CAP Theorem (DB), CockroachDB
tags:
  - nosql
  - newsql
  - distributed-sql
  - deep-dive
---

# NDB-021 — NewSQL

⚡ TL;DR — NewSQL databases provide the familiar SQL interface and ACID transactions of relational databases, combined with the horizontal scalability of NoSQL — using distributed consensus, automatic sharding, and globally-distributed architectures to eliminate the "scale vs. consistency" trade-off.

| #460            | Category: NoSQL & Distributed Databases                | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------- | :-------------- |
| **Depends on:** | Database Sharding, CAP Theorem (DB), ACID              |                 |
| **Used by:**    | System Design, Distributed Transactions, Microservices |                 |
| **Related:**    | Database Sharding, CAP Theorem (DB), CockroachDB       |                 |

---

### 🔥 The Problem This Solves

**THE 2000s SCALE PROBLEM:**
Traditional relational DBs (PostgreSQL, MySQL) hit vertical scaling limits. NoSQL solutions (Cassandra, DynamoDB) gave horizontal scale but sacrificed ACID transactions, SQL, and developer familiarity. Teams building fintech, e-commerce, and SaaS had to choose: "Do I want consistent, transactional data, or do I want it to scale?" This was the "NoSQL vs. SQL" era.

**NEWSQL SOLUTION:**
What if you could have both? NewSQL databases internalize the hard distributed systems work (Raft consensus, automatic sharding, distributed MVCC) and expose a standard SQL + ACID interface. The application developer writes SQL with JOINs and transactions — as if on PostgreSQL. The database transparently distributes, replicates, and scales horizontally. Scale-out without abandoning consistency.

---

### 📘 Textbook Definition

**NewSQL** refers to a class of relational database management systems designed to provide the **horizontal scalability** of NoSQL databases while maintaining the **ACID guarantees** and **SQL query interface** of traditional relational databases. Key architectural approaches: **Shared-nothing distributed SQL** (data auto-sharded across nodes; SQL query planner distributes query execution): CockroachDB, TiDB. **Consensus-based replication** (each shard/range uses Raft for automatic leader election and replication): CockroachDB, YugabyteDB. **Globally distributed** with TrueTime / Hybrid Logical Clocks for external consistency: Google Spanner, CockroachDB (HLC). **Cloud-native auto-scaling**: AWS Aurora (separates storage from compute; up to 128TB, multi-AZ), Google AlloyDB, PlanetScale (MySQL-compatible, Vitess-based). NewSQL is not one technology but a generation of databases that solved the distributed systems challenges hidden under the SQL abstraction layer.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
NewSQL says "yes" to all three: SQL queries, ACID transactions, and horizontal scale — by hiding the distributed systems complexity inside the database engine.

**One analogy:**

> Automatic transmission in a car. Manual transmission: you control the gears (NoSQL/manual sharding: you manage distribution yourself). Automatic transmission: the car handles gear selection transparently; you just drive (NewSQL: the database handles sharding/replication; you just write SQL). The experience is the same (pressing the accelerator = writing SQL), but the internals are completely different (and the automatic transmission is far more complex).

- "Manual gear shifting" → manual sharding + NoSQL complexity (Cassandra, Vitess)
- "Automatic transmission" → NewSQL (CockroachDB, Spanner)
- "Same driving experience" → same SQL interface, same ACID semantics
- "Far more complex internals" → Raft consensus, HLC, distributed query planner
- "Car accelerates correctly" → queries work correctly, data is consistent

**One insight:**
NewSQL databases are a bet that **complexity should live in the infrastructure, not in the application**. Manual sharding (Vitess + MySQL) works but requires application-level shard awareness, custom migration tooling, and limits cross-shard transactions. NewSQL pushes all of that complexity into the database — the application sees a single logical database. The cost: less flexibility, higher per-node complexity, sometimes less predictable latency.

---

### 🔩 First Principles Explanation

**COCKROACHDB ARCHITECTURE:**

```
Range-based sharding (automatic):
  Data split into 64MB "ranges" (similar to Bigtable tablets)
  Each range: Raft group of 3-5 replicas
  Raft leader = writes; followers = read with stale read or serve read-only

  Key space: all rows sorted by primary key globally
  Range [a - d]: Raft group on nodes 1, 2, 3
  Range [e - h]: Raft group on nodes 2, 3, 4

  Auto-rebalance: when ranges too full → split + rebalance across nodes
  No manual sharding: CockroachDB does this transparently

Distributed SQL query:
  SELECT o.id, u.name FROM orders o JOIN users u ON o.user_id = u.id
  WHERE o.created_at > '2024-01-01'

  Query planner:
  → orders scan: distributed across order ranges (parallel)
  → users lookup: for each order's user_id → route to user's range
  → Partial results aggregated at gateway node
  → Application receives complete result set

  (vs. Cassandra: impossible — no cross-partition join at DB level)
```

**GOOGLE SPANNER (EXTERNAL CONSISTENCY):**

```
Spanner's insight: if you can agree on "absolute time" (wall clock time),
you can determine the global order of transactions without coordination.

TrueTime API:
  TT.now() returns [earliest, latest] — a time interval, not a point
  Guaranteed: true current time ∈ [earliest, latest]
  Uncertainty: ε ≈ 1-7ms (atomic clocks + GPS receivers in every DC)

  Commit wait: after committing a transaction, wait ε ms before returning
  Why: ensures that no transaction committed "later" in real time
       can have a lower timestamp than ours

  Result: external consistency — if transaction T1 commits before T2
  starts, T1's commit timestamp < T2's commit timestamp (globally)
  This is stronger than serializable: it respects real-world ordering

CockroachDB's HLC (Hybrid Logical Clock) approximates this:
  Each node maintains max(wall_clock, last_seen_HLC)
  HLC includes logical component for sub-millisecond ordering
  Not as strong as TrueTime, but works without special hardware
```

**AURORA: SEPARATING STORAGE FROM COMPUTE:**

```
Traditional MySQL/PostgreSQL: storage and compute on same server
  Problem: scaling compute requires scaling storage (they're linked)
  Failover: must copy all data to new primary (slow)

Amazon Aurora:
  Compute: MySQL/PostgreSQL-compatible engine (can have read replicas)
  Storage: distributed storage layer (6 copies across 3 AZs, always)
            writes to storage cluster (quorum: 4 of 6 ACK required)

  Benefits:
  - Scale read replicas without data copies (all share same storage)
  - Failover: new primary in < 30s (no data copy needed)
  - Storage auto-scales to 128TB
  - Crash recovery: no redo log replay needed (storage layer handles it)

  Aurora vs. CockroachDB:
  Aurora: still single-region primary (cross-region = Aurora Global DB, async)
  CockroachDB: true multi-region, distributed writes globally
  Aurora: near-100% MySQL/PostgreSQL compatibility (easy migration)
  CockroachDB: PostgreSQL-compatible but some dialect differences
```

**PLANETSCALE (VITESS-BASED):**

```
PlanetScale = managed MySQL with Vitess sharding + branching model

  Branching: like Git for databases
    Create a branch of production schema
    Apply schema changes (with non-blocking DDL via gh-ost)
    Test on branch (uses copy-on-write)
    Merge/deploy to production

  Non-blocking DDL: large ALTER TABLE = blocks in MySQL
  Vitess + gh-ost: shadow table approach; no locking during migration

  Trade-off: Vitess sharding → no cross-shard transactions (by design)
  PlanetScale's answer: design for single-shard transactions;
                        use keyspace IDs consistently
```

---

### 🧪 Thought Experiment

**NEWSQL FOR FINTECH: GLOBAL CONSISTENCY VS. LATENCY**

Fintech startup: handles cross-currency transfers. Users in US, EU, Asia. Requirements: transfers must be globally consistent (can't double-spend). Team currently on PostgreSQL (single region, hitting limits).

**OPTION A: CockroachDB multi-region:**
Globally distributed; Raft consensus per range; external consistency via HLC. Cross-region transaction: writes to US user + EU user. Raft leader for US range may be in US; leader for EU range in EU. Cross-region transaction round-trip: 150ms (consensus requires majority of 3 replicas; if replicas are in 3 regions, one RTT = ~150ms for trans-Atlantic). For financial transactions < 1 second: acceptable but not great. Better: configure "leaseholder" for US accounts on US ranges, EU accounts on EU ranges → most transactions are single-region.

**OPTION B: Google Spanner:**
TrueTime-based external consistency. Commit wait (7ms max). Most transactions: 10-20ms latency within a region. Cross-region transactions: 100-200ms. Managed: no ops burden. High cost at scale ($0.90/node-hour × many nodes).

**OPTION C: CockroachDB Follower Reads:**
Trades consistency for latency: read from nearest replica (may be 1.5s stale). Display account balance: acceptable. Validate before transfer: use strong read (goes to Raft leader).

**THE LESSON:**
NewSQL doesn't eliminate latency trade-offs — it makes them explicit and configurable. The choice between NewSQL systems is a choice of: global consistency level, acceptable write latency, geographic distribution model, and operational cost. The "magic" of NewSQL is that you have these choices within the SQL+ACID model rather than having to rebuild consistency guarantees in your application.

---

### 🧠 Mental Model / Analogy

> NewSQL is like a multinational bank that lets you walk into any branch worldwide, withdraw or deposit, and your balance is always correct across all branches — without you needing to know which city the "master ledger" is in. Traditional bank with single HQ: every branch calls headquarters for every transaction (single-primary database). NoSQL approach: each branch manages its own ledger locally, reconciles later (eventual consistency — you might overdraft if the reconciliation hasn't happened). NewSQL: every branch is part of a consensus network — they all agree on the balance before any transaction completes.

- "Walk into any branch" → write to any NewSQL node globally
- "Balance always correct" → ACID consistency across distributed nodes
- "Single HQ" → single-primary traditional DB
- "Branch manages own ledger" → NoSQL eventual consistency
- "Consensus network" → Raft/Paxos-based distributed consensus (CockroachDB, Spanner)

---

### 📶 Gradual Depth — Four Levels

**Level 1:** NewSQL databases give you the best of both worlds: you can write normal SQL with JOINs and transactions (like PostgreSQL), AND the database automatically scales across many servers (like Cassandra). The database handles all the distributed systems complexity; your application just sees a regular database.

**Level 2:** Choose by use case: CockroachDB for truly global write distribution with PostgreSQL compatibility; AWS Aurora for managed, highly available PostgreSQL/MySQL that's easy to migrate to; PlanetScale for MySQL + zero-downtime schema changes + Vitess sharding; Google Spanner for the strongest global consistency (TrueTime) at high cost. Remember: cross-region consensus always adds latency — design data locality to minimize cross-region transactions.

**Level 3:** CockroachDB's distributed transaction protocol: uses a two-phase commit variant with Raft. Phase 1: acquire "write intents" (provisional writes); run Raft for each involved range. Phase 2 (commit): write the transaction record; cleanup intents → committed writes visible. Conflict detection: if two transactions contend, CockroachDB detects the conflict and retries the lower-priority transaction. Retry logic: application must handle `40001` (serialization failure) → use `@Transactional` + retry interceptor in Spring. Follower reads: `SELECT ... AS OF SYSTEM TIME follower_read_timestamp()` → reads from nearest replica, up to 4.8 seconds stale. Used for: reporting queries where stale data is acceptable; dramatically improves latency.

**Level 4:** NewSQL represents the maturation of the "distributed systems in the database" philosophy. The original NoSQL movement (2009-2012) responded to the scaling ceiling of relational databases by sacrificing consistency and SQL. The implicit bet was that "applications can handle consistency." Experience showed: most applications cannot handle consistency correctly — distributed consistency in application code is bug-prone and unmaintainable. NewSQL inverts this: "the database handles distributed consistency; applications get their familiar ACID semantics." This is consistent with the Abstraction Principle: hide complexity behind well-understood interfaces. The remaining trade-offs NewSQL cannot eliminate: (a) physical speed of light (cross-region write latency is bounded by geography, regardless of consistency protocol), (b) the operational complexity of running distributed consensus at scale (more failure modes than a single-server database), (c) some SQL features that assume centralized execution (e.g., sequences, certain window functions) require coordination in distributed execution. For applications that fit within a single region (the vast majority), the operational complexity of CockroachDB/Spanner vs. Aurora/PostgreSQL must be justified by a genuine need for cross-region write distribution.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ COCKROACHDB TRANSACTION ACROSS 2 RANGES              │
├──────────────────────────────────────────────────────┤
│                                                      │
│ BEGIN;                                               │
│ UPDATE accounts SET balance = balance - 100          │
│   WHERE id = 'alice';   -- Range A (Node 1 is leader)│
│ UPDATE accounts SET balance = balance + 100          │
│   WHERE id = 'bob';     -- Range B (Node 3 is leader)│
│ COMMIT;                                              │
│                                                      │
│ [NEWSQL ← YOU ARE HERE: distributed 2PC + Raft]      │
│                                                      │
│ Phase 1: Write intents to Range A + Range B          │
│   Range A: Raft propose → 2 of 3 replicas ACK ✓     │
│   Range B: Raft propose → 2 of 3 replicas ACK ✓     │
│                                                      │
│ Phase 2: Write transaction record (COMMITTED)        │
│   → Range A + B intents resolved → balances visible  │
│                                                      │
│ If conflict: retry with backoff (40001 error)         │
│ Application: must handle retries (Spring @Transactional│
│   + CockroachDB retry interceptor)                   │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**FINANCIAL TRANSFER IN COCKROACHDB:**

```
User: transfer $100 from Alice to Bob
→ Spring service: @Transactional method
→ JPA/JDBC: BEGIN
→ SELECT balance FROM accounts WHERE id='alice' FOR UPDATE  -- lock alice's range
→ SELECT balance FROM accounts WHERE id='bob' FOR UPDATE    -- lock bob's range
→ [NEWSQL ← YOU ARE HERE: distributed lock + consistency]
→ CockroachDB: write intents on both ranges (Raft on each)
→ UPDATE alice: balance - 100
→ UPDATE bob: balance + 100
→ COMMIT → CockroachDB: 2PC over Raft → fully committed
→ If conflict: 40001 thrown → Spring @Retryable → retry
→ Response: transfer successful
→ Both balances updated atomically, durably, consistently
```

---

### ⚖️ Comparison Table

| Database       | Consistency  | Horizontal Scale   | SQL Compat     | Multi-Region Writes | Best For                        |
| -------------- | ------------ | ------------------ | -------------- | ------------------- | ------------------------------- |
| PostgreSQL     | Strong       | Vertical only      | 100%           | ❌ (single primary) | Most OLTP                       |
| CockroachDB    | Serializable | Yes (Raft/ranges)  | ~95% PG        | ✅                  | Global OLTP, fintech            |
| Google Spanner | External     | Yes (tablet/Paxos) | Yes (ANSI SQL) | ✅ (TrueTime)       | Enterprise, highest consistency |
| AWS Aurora     | Strong       | Read replicas      | 100% PG/MySQL  | ❌ (Global = async) | Managed, HA, AWS ecosystem      |
| PlanetScale    | Serializable | Vitess sharding    | MySQL compat   | ❌                  | MySQL at scale, zero-DT DDL     |
| TiDB           | Serializable | Yes (TiKV/Raft)    | MySQL compat   | ✅                  | HTAP (OLTP + OLAP)              |

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                                                                   |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "NewSQL eliminates all distributed system complexity" | It hides it behind the database interface, but cross-region latency, Raft leader elections, and retry logic for serialization failures are still your operational concern                 |
| "CockroachDB is a drop-in replacement for PostgreSQL" | ~95% SQL compatible. Some features differ: sequences, stored procedures, certain window functions, some PostgreSQL-specific types. Test thoroughly before migrating                       |
| "Aurora is a distributed database like CockroachDB"   | Aurora separates compute from storage but still has a single primary writer (per region). It scales reads, not writes. AWS Aurora Global Database provides cross-region reads, not writes |
| "NewSQL always outperforms traditional RDBMS"         | Single-region OLTP on PostgreSQL is typically faster than CockroachDB — fewer network hops (no Raft consensus on localhost). NewSQL wins when you genuinely need distribution             |

---

### 🚨 Failure Modes & Diagnosis

**1. CockroachDB Serialization Failure Storms**

**Symptom:** Application experiences intermittent errors: `ERROR: restart transaction: TransactionRetryWithProtoRefreshError`. Error rate increases under load. Some operations take 10× longer than expected.

**Root Cause:** High contention on a "hot range" — many transactions trying to write to the same range (e.g., all orders writing to the same partition of a high-traffic table). CockroachDB's optimistic concurrency detects conflicts and retries.

**Diagnostic:**

```sql
-- CockroachDB: find hot ranges
SHOW RANGES FROM TABLE orders;
-- Look for ranges with very high lease_holder_locality and leaseholder activity

-- Application: log 40001 errors with query context
-- Metric: cockroachdb_transactions_restarts (Prometheus)
```

**Fix:** Add `@Retryable` with exponential backoff for `40001`. For hot ranges: redesign the primary key to spread writes across ranges (add a hash prefix). For INSERT contention: use `UUID` PKs (random, distributes across all ranges naturally). CockroachDB also has "SELECT FOR UPDATE" that pessimistically locks — trade concurrency for fewer retries on hot rows.

---

### 🔗 Related Keywords

**Prerequisites:** Database Sharding, CAP Theorem (DB), ACID
**Builds On This:** System Design, Distributed Transactions
**Related:** CAP Theorem (DB), CockroachDB, Google Spanner

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ SQL + ACID + horizontal scale             │
│ KEY SYSTEMS  │ CockroachDB, Spanner, Aurora, TiDB        │
│ MECHANISM    │ Raft consensus per range/shard            │
│              │ Distributed 2PC for multi-range txns      │
│ RETRY NEEDED │ Handle 40001 (serialization failures)     │
│ CROSS-REGION │ Adds 100-200ms latency (physical reality) │
│ CHOOSE WHEN  │ Global writes + ACID + SQL required       │
│ ONE-LINER    │ "Distributed systems complexity inside   │
│              │  the database, SQL outside"               │
│ NEXT EXPLORE │ MongoDB Patterns → Redis Data Structures  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C — Design Question) A global SaaS company has: user authentication (must be globally consistent, low latency everywhere), product catalog (reads everywhere, writes from admins only in US), order management (writes in user's region, globally consistent balance checks). Design the database architecture using NewSQL for each service: which specific NewSQL DB, which regions, which consistency level (strong vs. follower reads), and how you'd handle the balance check during order placement to prevent double-charging.

**Q2.** (TYPE F — Comparison Depth) Compare Google Spanner vs. CockroachDB on: (a) consistency model (TrueTime vs. HLC), (b) operational model (fully managed vs. self-hosted/cloud), (c) SQL compatibility (ANSI vs. PostgreSQL wire protocol), (d) pricing model, (e) cross-region write latency characteristics. For a startup with a team of 5 engineers, which would you choose and why? Would that choice change for a 500-engineer company?
