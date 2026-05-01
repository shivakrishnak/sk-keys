---
layout: default
title: "PACELC"
parent: "Distributed Systems"
nav_order: 572
permalink: /distributed-systems/pacelc/
number: "572"
category: Distributed Systems
difficulty: ★★★
depends_on: "CAP Theorem"
used_by: "Consistency Models, Database Selection"
tags: #advanced, #distributed, #consistency, #latency, #theory
---

# 572 — PACELC

`#advanced` `#distributed` `#consistency` `#latency` `#theory`

⚡ TL;DR — **PACELC** extends CAP by adding a crucial insight: even without a partition (the normal case), distributed systems must trade off between **L**atency and **C**onsistency — faster writes (async replication) = lower latency but weaker consistency; slower writes (sync replication) = stronger consistency but higher latency.

| #572            | Category: Distributed Systems          | Difficulty: ★★★ |
| :-------------- | :------------------------------------- | :-------------- |
| **Depends on:** | CAP Theorem                            |                 |
| **Used by:**    | Consistency Models, Database Selection |                 |

---

### 📘 Textbook Definition

**PACELC** (Daniel Abadi, 2012) is a theoretical framework that extends the CAP theorem to address the latency/consistency trade-off that exists in distributed systems even during normal (non-partition) operation. The theorem states: if a **P**artition occurs, choose between **A**vailability and **C**onsistency (the CAP choice); **E**lse (during normal operation), choose between **L**atency and **C**onsistency. PACELC acknowledges that high consistency (synchronous replication — all replicas must acknowledge before responding to client) adds write latency equal to the round-trip to the slowest replica. Databases are classified as PA/EL (low latency, weak consistency), PC/EC (high consistency, higher latency), or mixed (PC/EL: CP during partition, low latency during normal operation — e.g., optimistic locking). PACELC better captures the engineering reality than CAP alone, since most production traffic occurs outside of partition events.

---

### 🟢 Simple Definition (Easy)

PACELC: CAP covers partition scenarios (rare). PACELC adds the everyday trade-off: "Even when everything is fine, do you want fast responses (async replication, might be slightly stale) or accurate data (sync replication, slower)?" Writing to a bank account: synchronous replication waits for 3 nodes to confirm → 30ms extra latency. Asynchronous: responds immediately → 1ms latency, but if master crashes before replication → data lost. Most databases let you choose.

---

### 🔵 Simple Definition (Elaborated)

PACELC decision matrix for a database with 3 replicas: Synchronous replication (EC: consistent, higher latency) — write waits for all 3 replicas to acknowledge. Latency = max(3 replica write times) = 30ms if furthest replica is 30ms away. But: crash before sync = no data loss. Asynchronous replication (EL: low latency, weaker consistency) — write acknowledged after local write only. Latency = 1ms. But: 30ms replication window = if master crashes, up to 30ms of writes lost. Real systems like DynamoDB offer this as a per-request choice: `ConsistentRead=true` (EC, higher cost) or `ConsistentRead=false` (EL, cheaper, faster, default).

---

### 🔩 First Principles Explanation

**PACELC classifications and latency-consistency analysis:**

```
PACELC CLASSIFICATION MATRIX:

  During Partition (P→A or P→C):
    PA: Serve requests with potentially stale data (Cassandra, DynamoDB default)
    PC: Refuse requests to maintain consistency (ZooKeeper, HBase)

  Else/During Normal Operation (E→L or E→C):
    EL: Respond immediately, replicate async (low latency, weaker consistency)
    EC: Wait for replicas to confirm, then respond (higher latency, strong consistency)

  Database classifications:
  ┌───────────────┬──────────┬──────────────────────────────────────────┐
  │ Database      │ PACELC   │ Notes                                    │
  ├───────────────┼──────────┼──────────────────────────────────────────┤
  │ DynamoDB      │ PA/EL    │ Partition→Available; Normal→Low Latency  │
  │ Cassandra     │ PA/EL    │ Eventual consistency by default           │
  │ MongoDB       │ PA/EC    │ Partition→Available; Normal→wait replicas│
  │ MySQL (async) │ PC/EL    │ Partition→Consistent; Normal→async rep   │
  │ MySQL (sync)  │ PC/EC    │ Both: consistent + higher latency        │
  │ DynamoDB *    │ PC/EL    │ Strong reads = CP; Normal→async writes   │
  │ Spanner       │ PC/EC    │ TrueTime for global consistency + higher │
  │ ZooKeeper     │ PC/EC    │ Sequential consistency, higher latency   │
  │ Dynamo paper  │ PA/EL    │ Amazon's shopping cart: availability > C │
  └───────────────┴──────────┴──────────────────────────────────────────┘
  * DynamoDB strongly consistent reads = PC/EL mode

LATENCY-CONSISTENCY TRADE-OFF (the E side):

  Setup: 3-replica PostgreSQL cluster.
  Primary in London, Replica 1 in Frankfurt (10ms RTT), Replica 2 in NY (80ms RTT).

  synchronous_commit = on (EC mode):
    Write: primary writes WAL → waits for at least 1 replica to flush WAL.
    Minimum latency: primary write + 10ms (Frankfurt RTT) = ~12ms per write.

  synchronous_commit = remote_apply (strict EC):
    Write: waits for replica to APPLY changes (not just flush WAL).
    Latency: includes replica apply time → ~15-20ms per write.
    Benefit: replica is immediately queryable with fresh data.

  synchronous_commit = off (EL mode):
    Write: primary writes WAL buffer → responds immediately → replicates async.
    Latency: ~1-2ms per write (no replica roundtrip).
    Risk: up to wal_writer_delay (200ms) of data loss on primary crash.

  synchronous_standby_names (mixed):
    Synchronous for one replica (Frankfurt: 10ms).
    Async for NY replica (80ms RTT → not in critical path).
    Latency: ~12ms. Durability: 2 copies synced.
    Use: fast primary-region writes + geo-replicated async for read scale.

PACELC AND TUNABLE CONSISTENCY:

  Many distributed databases offer "tunable consistency":
  User selects the CAP/PACELC position per operation.

  Cassandra consistency levels:
    ONE (EL): accept write/read from any 1 replica → fast, may be stale
    QUORUM (EC, quasi): majority (N/2+1) must agree → slower, fresh
    ALL (strict EC): all replicas must agree → slowest, freshest

  DynamoDB:
    ConsistentRead=false (EL): uses eventually consistent read model → cheap + fast
    ConsistentRead=true (EC): guarantees reading latest write → 2× read capacity units

  The trade-off is not just theoretical — it has a dollar cost:
    DynamoDB strongly consistent reads = 2× the capacity unit cost of eventually consistent reads.
    This is the literal price of consistency.

PRACTICAL EXAMPLES:

  SHOPPING CART (PA/EL — Amazon Dynamo):
    Business requirement: cart must always be addable to (availability > consistency)
    Partition: show cart with last-known contents. Let user keep adding.
    Conflict on heal: merge both carts (union of items) — "always add, never lose items"
    This is the design choice Amazon documented in the Dynamo paper.

  BANK LEDGER (PC/EC — PostgreSQL synchronous):
    Business requirement: money must never appear or disappear incorrectly
    Partition: refuse to process transactions on isolated node
    Normal operation: synchronous replication → every write confirmed by replica before ACK
    Latency cost: 10-30ms per transaction → acceptable for financial integrity

  DNS (PA/EL — extreme availability):
    Business requirement: DNS must always resolve (even if stale)
    TTL = 300 seconds (5 minutes of staleness acceptable)
    Partition: serve cached DNS records (stale by minutes) → available
    Never refuse to resolve → AP system.
    Change propagation: eventually consistent (minutes to hours for global propagation).

WRITE PATH LATENCY MODEL:

  Synchronous (EC) write latency = max(local_write, max(replica_write_times))
  Asynchronous (EL) write latency = local_write only

  For a multi-region setup (US, EU, APAC):
  EC write: waits for APAC acknowledgment → 200ms RTT → 200ms per write → unacceptable

  Solution: synchronous with REGIONAL replica only, async for other regions:
    EC with US-East replica (5ms RTT) → 6ms write latency
    Async to EU and APAC replicas → no latency impact, eventual consistency cross-region

  This is AWS Aurora's "read replicas" model:
    Synchronous replication: within same region (EC within region)
    Asynchronous: cross-region replicas (EL across regions)
    PACELC: PC within partition (refuses isolated region) / EC within region, EL cross-region
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT PACELC:

- CAP only covers partition scenarios (rare)
- Engineers miss the everyday latency/consistency trade-off
- Misconfigured databases: async replication everywhere for "performance" → data loss risk

WITH PACELC:
→ Complete picture: CAP (partition behavior) + latency/consistency (normal operation)
→ Informed configuration: synchronous for critical data, async for high-throughput non-critical
→ Cost awareness: consistency has a measurable latency and dollar cost

---

### 🧠 Mental Model / Analogy

> A bank with multiple branches. CAP governs phone outages (partitions — rare). PACELC governs everyday operations: (E) when everything works, do branches call headquarters to confirm every transaction (EC: accurate but slow) or process locally and sync later (EL: fast but briefly divergent)? High-value transactions (wire transfers): call HQ and wait (EC, high latency, certain accuracy). ATM cash dispensals: process locally, sync overnight (EL, fast, occasional small discrepancies corrected next morning). PACELC maps each transaction type to the right trade-off.

"Phone outages" = network partitions (CAP applies)
"Everything works normally" = E in PACELC (else — normal operation)
"Call HQ and wait" = EC (synchronous replication — higher latency, strong consistency)
"Process locally, sync later" = EL (async replication — low latency, eventual consistency)
"Wire transfers = call HQ; ATM = local processing" = different operations can use different modes

---

### ⚙️ How It Works (Mechanism)

**PostgreSQL: configuring PACELC position:**

```sql
-- EC mode (normal operation): wait for replica before ACKing client
-- Higher latency, guaranteed consistency:
ALTER SYSTEM SET synchronous_commit = 'remote_apply';
-- or per-transaction:
SET synchronous_commit = 'remote_apply';
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;  -- waits for replica to apply change → 10-30ms latency

-- EL mode (normal operation): respond immediately, replicate async
-- Lower latency, potential data loss of last 200ms on crash:
SET synchronous_commit = 'off';
BEGIN;
INSERT INTO page_views (page_id, user_id, ts) VALUES (1, 2, NOW());
COMMIT;  -- returns immediately → ~1ms latency, acceptable for analytics

-- EC with quorum (wait for N replicas):
-- Require acknowledgment from at least 2 standbys:
ALTER SYSTEM SET synchronous_standby_names = 'ANY 2 (standby1, standby2, standby3)';
-- Write latency = 2nd-fastest replica's RTT (not the slowest)
-- 2 of 3 confirms: one replica can be slow without penalizing every write
```

---

### 🔄 How It Connects (Mini-Map)

```
CAP Theorem (partition behavior)
        │
        ▼
PACELC ◄──── (you are here)
(adds: normal-operation latency vs consistency trade-off)
        │
        ├── Consistency Models (the spectrum of C in PACELC)
        ├── Replication Strategies (sync EC vs async EL)
        └── Database Selection (classify each DB by PACELC position)
```

---

### 💻 Code Example

**Cassandra tunable consistency per operation:**

```java
@Repository
public class UserRepository {

    private final CqlSession session;

    // PACELC PA/EL: fast non-critical reads (eventual consistency):
    public Optional<User> findUserForDisplay(UUID userId) {
        Statement stmt = QueryBuilder.selectFrom("users")
            .all()
            .whereColumn("user_id").isEqualTo(literal(userId))
            .build()
            .setConsistencyLevel(ConsistencyLevel.ONE);  // EL: any 1 replica

        // Fast (1-2ms), may return data up to seconds old
        // Acceptable for: profile views, activity feeds
        ResultSet result = session.execute(stmt);
        return Optional.ofNullable(result.one()).map(this::map);
    }

    // PACELC PA/EC: strong consistency for financial operations:
    public BigDecimal getAccountBalance(UUID accountId) {
        Statement stmt = QueryBuilder.selectFrom("accounts")
            .column("balance")
            .whereColumn("account_id").isEqualTo(literal(accountId))
            .build()
            .setConsistencyLevel(ConsistencyLevel.QUORUM);  // EC: N/2+1 must agree

        // Slower (5-10ms), but guaranteed to return latest committed balance
        // Required for: payment processing, balance display
        ResultSet result = session.execute(stmt);
        Row row = result.one();
        return row != null ? row.getBigDecimal("balance") : BigDecimal.ZERO;
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| --------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PACELC replaces CAP                                 | PACELC extends CAP by adding the Else (E) clause for normal operation. CAP is still valid for partition scenarios. PACELC gives a more complete picture because it addresses both partition AND normal operation trade-offs. Most real-world problems are in the E (else) dimension — the latency/consistency trade-off during normal operation                                                                                                |
| Low latency always means eventual consistency       | Low latency during normal operation (EL) means async replication, which risks losing data on primary crash. But you can have LOW LATENCY + CONSISTENCY within a single region if your replicas are nearby. A primary and replica in the same datacenter (1ms RTT) can do synchronous replication with only 1ms extra latency. The latency penalty for EC scales with geographic distance, not with the synchronous replication protocol itself |
| PA/EL systems are always worse than PC/EC           | It depends entirely on the use case. DNS (PA/EL) is one of the most critical pieces of internet infrastructure — its availability guarantee is more important than having perfectly fresh records. A bank ledger must be PC/EC. Neither is "better" — the classification must match the business requirements                                                                                                                                  |
| PACELC requires explicitly choosing between C and L | Many modern systems offer tunable consistency: you select the trade-off per operation, not per system. DynamoDB, Cassandra, MongoDB all support this. The PACELC "classification" of such systems is better described as "tunable between EL and EC" — the system itself doesn't force a single choice                                                                                                                                         |

---

### 🔥 Pitfalls in Production

**Async replication gap causes data loss on failover:**

```
PROBLEM: Primary crashes with 200ms async replication lag → committed writes lost

  Setup:
    MySQL primary (async replication, synchronous_commit=off = EL mode).
    Replica 1 in same AZ (50ms replication lag on average).
    Writes per second: 10,000 (analytics events — EL chosen for low latency).

  Failure:
    Primary: hardware failure at 14:23:45.000.
    Replication lag at crash: 150ms (replica 50ms behind primary).

  Data loss:
    Last 150ms of writes: NOT on replica. They were in primary WAL buffer (unflushed).
    Writes lost: 10,000 × 0.15 = ~1,500 analytics events.

  For analytics: 1,500 lost events → acceptable (PA/EL choice was intentional).
  For financial: 1,500 lost transactions → catastrophic (should have been PC/EC).

BAD: Using EL mode for financial writes:
  -- MySQL: async replication for all writes
  SET @@SESSION.innodb_flush_log_at_trx_commit = 0;  -- EL: no sync I/O
  -- 200ms exposure window → data loss on crash

FIX: SEMI-SYNCHRONOUS REPLICATION (EC within region):
  -- MySQL semi-sync: wait for at least 1 replica to acknowledge before COMMIT:
  SET @@GLOBAL.rpl_semi_sync_master_enabled = 1;
  SET @@GLOBAL.rpl_semi_sync_master_timeout = 1000;  -- 1s timeout → fallback to async on timeout

  -- Latency: +10ms (same-AZ replica RTT) → acceptable for financial transactions
  -- Data loss window: 0ms (at least 1 replica always has the write before COMMIT)

  -- Per-table choice: financial tables = EC, analytics tables = EL:
  -- Use separate databases with different replication settings per data criticality.
```

---

### 🔗 Related Keywords

- `CAP Theorem` — PACELC's foundation: partition behavior (PA or PC)
- `Consistency Models` — the spectrum of "C" in PACELC (linearisability to eventual)
- `Replication Strategies` — synchronous (EC) vs asynchronous (EL) replication
- `Write-Ahead Logging` — mechanism for durability in EC systems

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ P→A or C (CAP during partition); Else→    │
│              │ L or C (latency vs consistency, always)   │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Selecting replication mode; understanding │
│              │ trade-offs beyond partition scenarios     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ EL mode for financial writes (200ms       │
│              │ replication gap = potential data loss)    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Wire transfers call HQ; ATM withdrawals  │
│              │  process locally and sync overnight."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Consistency Models → Replication Strategies│
│              │ → Synchronous Commit Configuration        │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A fintech startup is building a payment processing system. Their database architect says: "We'll use PostgreSQL with asynchronous replication for low latency on writes. If the primary crashes, we'll failover to the replica — it'll only be behind by a few hundred milliseconds of transactions." The CTO disagrees. Who is right, and why? What specific PostgreSQL configuration would you recommend, and what is the latency cost of that recommendation? Use PACELC terminology to frame your answer.

**Q2.** Google Spanner uses "TrueTime" (GPS-synchronized clocks) to achieve both strong consistency (EC) and low latency at global scale. The claim is it breaks the PACELC trade-off. Is this true? How does TrueTime reduce the latency cost of synchronous global replication? What is the minimum latency Spanner can achieve for a globally replicated write (e.g., data replicated across US, EU, and APAC), and why is this latency floor fundamental (hint: speed of light)?
