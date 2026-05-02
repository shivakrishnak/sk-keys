---
layout: default
title: "Replication Strategies"
parent: "Distributed Systems"
nav_order: 588
permalink: /distributed-systems/replication-strategies/
number: "0588"
category: Distributed Systems
difficulty: ★★★
depends_on: Distributed Systems, CAP Theorem, Consistency Models, Quorum
used_by: Log Replication, State Machine Replication, Eventual Consistency, Raft
related: Log Replication, Quorum, Strong Consistency, Eventual Consistency, Raft
tags:
  - distributed
  - replication
  - reliability
  - consistency
  - deep-dive
---

# 588 — Replication Strategies

⚡ TL;DR — Replication strategies define how and when data is copied across multiple nodes: synchronous (all must confirm before success), asynchronous (confirm immediately, replicate later), or semi-synchronous (wait for a subset) — each balancing durability, latency, and availability differently.

| #588 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Distributed Systems, CAP Theorem, Consistency Models, Quorum | |
| **Used by:** | Log Replication, State Machine Replication, Eventual Consistency, Raft | |
| **Related:** | Log Replication, Quorum, Strong Consistency, Eventual Consistency, Raft | |

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A database runs on a single machine. When that machine crashes, all data is gone until recovery. RTO (Recovery Time Objective) is hours. Worse, the recovery may be incomplete — some writes since the last backup are lost. For any business with continuous write traffic, single-node storage is simply too fragile.

**THE BREAKING POINT:**
Replication is the answer to durability and availability. But how to replicate is not obvious: replicate synchronously and every write takes 2× the time (waiting for the replica); replicate asynchronously and the replica may lag behind, losing recent writes on primary failure. Every replication strategy is a trade-off along the durability-latency-availability triangle.

---

### 📘 Textbook Definition

**Replication** is the process of maintaining identical copies of data on multiple nodes. Strategies differ in when the write is confirmed to the caller vs. when replicas are updated. **Synchronous replication**: primary waits for all (or a quorum of) replicas to acknowledge before confirming to the client. Zero data loss on failure; highest write latency. **Asynchronous replication**: primary confirms to client immediately; replication happens in background. Lowest write latency; potential data loss (replication lag). **Semi-synchronous** (also: chain replication, quorum writes): primary waits for a subset of replicas (commonly 1 or `N/2+1`). Trade-off between full-sync and async. **Chain Replication**: writes propagate head-to-tail down a chain; reads served from tail; strong consistency; tail failure causes full chain stall. **Quorum Writes+Reads**: `W + R > N` ensures read/write sets overlap — guarantees at least one node has the latest write.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Replication strategies answer: "does the client wait for the backup to confirm?" — either "yes, always" (safe but slow), "no, never" (fast but risky), or "yes, for a majority" (balanced).

**One analogy:**
> Synchronous replication is like filing two copies of a cheque simultaneously — slow, but you're certain both banks have a record. Asynchronous is like filing with one bank first, mailing the copy later — faster, but if the postal van crashes before delivery, one bank's copy is lost. Quorum is like filing with 3 out of 5 branches simultaneously — acceptable for "good enough" durability without full synchronous lag.

**One insight:**
The fundamental tension in replication: increasing durability (more replicas must confirm) always increases write latency (more round-trips). The quorum approach (`W + R > N`) is the principled middle ground — it mathematically guarantees at least one node in any read set has seen the latest write, without requiring ALL nodes to confirm every write.

---

### 🔩 First Principles Explanation

**TYPES OF REPLICATION:**
```
┌────────────────┬────────────────────────────┬─────────┬──────────┐
│ Strategy       │ Description                │ Latency │ Max Loss │
├────────────────┼────────────────────────────┼─────────┼──────────┤
│ Synchronous    │ Wait for ALL replicas       │ High    │ Zero     │
│ (full sync)    │ before confirming           │         │          │
├────────────────┼────────────────────────────┼─────────┼──────────┤
│ Semi-sync      │ Wait for ≥1 replica        │ Medium  │ Limited  │
│ (MySQL default)│ (not all) to ACK           │         │          │
├────────────────┼────────────────────────────┼─────────┼──────────┤
│ Async          │ Confirm immediately;        │ Low     │ Can be   │
│                │ replicate in background     │         │ seconds  │
├────────────────┼────────────────────────────┼─────────┼──────────┤
│ Quorum (W+R>N) │ Wait for W replicas to ACK;│ Medium  │ None*    │
│                │ read from R replicas        │         │ *if W+R>N│
├────────────────┼────────────────────────────┼─────────┼──────────┤
│ Chain          │ Head→...→Tail linear chain;│ High    │ Zero     │
│ Replication    │ read from tail             │         │          │
└────────────────┴────────────────────────────┴─────────┴──────────┘
```

**QUORUM MATHS:**
```
System: N replicas
Writes go to W replicas (write quorum)
Reads from R replicas (read quorum)

Consistency guarantee: W + R > N
  → any write set and read set MUST share at least one replica
  → that shared replica holds the latest write
  → the read will always see the latest write

Examples (N=5):
  W=3, R=3: W+R=6 > 5 ✓  Consistent. High durability, high latency.
  W=5, R=1: W+R=6 > 5 ✓  Consistent. All replicas must ACK writes.
  W=1, R=5: High read cost, very fast writes.
  W=2, R=2: W+R=4 < 5 ✗  NOT consistent. Possible to miss latest write.
  W=3, R=2: W+R=5 = 5 ✗  Borderline — NOT consistent (need STRICT >).
```

**REPLICATION LAG:**
```
Async replication scenario:
  Primary applies write at T=0
  Replica receives write at T=500ms (replication lag)
  
  If primary crashes at T=200ms:
    500ms worth of writes NOT yet replicated = LOST
    Replica promoted to primary with stale state

Monitoring replica lag:
  MySQL: SHOW SLAVE STATUS → Seconds_Behind_Master
  PostgreSQL: pg_stat_replication → write_lag, flush_lag, replay_lag
  Redis: INFO replication → master_repl_offset vs slave_repl_offset
```

**CHAIN REPLICATION:**
```
Write path:  Client → HEAD → N2 → N3 → TAIL → ACK to client
Read path:   Client → TAIL (always consistent: TAIL has all committed writes)

Benefits:
  - Strong consistency without quorum voting (reads always from TAIL)
  - TAIL is the single source of truth for reads
  - HEAD handles write fan-out

Failure recovery:
  - TAIL failure: promote N3 to TAIL (N3 has all TAIL data by chain invariant)
  - HEAD failure: promote N2 to HEAD (lose uncommitted writes at old HEAD)
  - Middle node: bypass — HEAD sends to N3 directly
```

---

### 🧪 Thought Experiment

**ASYNC REPLICATION DATA LOSS QUANTIFICATION:**
MySQL async replica. Primary handles 1,000 writes/second. Replica lag: 500ms.
Primary crashes unexpectedly. At the moment of crash, 500 writes (500ms × 1,000/s)
existed in the primary's binlog but had NOT yet replicated to the replica.

You promote the replica to primary. Those 500 writes are gone. Customers who
made purchases in the last 500ms see no record of them. Their money may have been
charged but the order is gone.

**THE TRADE-OFF:**
With synchronous replication, every one of those 1,000 writes/second would have
waited for the replica ACK (~1-5ms per write over LAN). Throughput drops and
latency doubles. This is the business decision: accept 500ms of potential data
loss (async) or accept 2× write latency (sync).

**SEMI-SYNC ANSWER:**
MySQL semi-synchronous replication waits for ONE replica to ACK before confirming
to the client. Loss window shrinks to zero (for 1-replica failure). Write latency
increases by exactly one network round-trip to the nearest replica. This is why
semi-sync is MySQL's recommended production setting for write-critical workloads.

---

### 🧠 Mental Model / Analogy

> Replication strategy is a durability dial:
>
> ASYNC ←──────────────────────────────── SYNC
> Fast, risky                        Slow, safe
> "Post your backup copy later"  "File with all offices simultaneously"
>
> QUORUM sits in the middle: "file with majority of offices" — fast enough,
> safe enough, mathematically guaranteed to be consistent if W + R > N.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** A single database can lose data if the disk fails. Replication copies data to multiple machines. The question is: does the client wait for the copy to confirm (safe, slow) or does it proceed and copy later (fast, risky)?

**Level 2:** Three main strategies: synchronous (wait for all replicas — zero risk, high latency), asynchronous (confirm immediately — low latency, risk of data loss), and quorum (wait for majority — balanced). Quorum strategy uses the rule `W + R > N` to guarantee reads always see the latest write.

**Level 3:** Quorum writes and reads must be combined correctly: `W + R > N` ensures intersection. Dynamo-style databases let applications configure W and R. For strong consistency: W=majority, R=majority. For high availability with weaker consistency: W=1, R=1 (faster, less durable). Chain replication provides strong consistency with simpler failure analysis: TAIL always has all committed writes; reads from TAIL are guaranteed to be up-to-date.

**Level 4:** At scale, replication strategies interact with leader election and log replication protocols. Raft uses synchronous majority replication for commit acknowledgement (entries committed after N/2+1 ACK) — this is quorum replication with W=N/2+1. Async replication is used for cross-region standbys (zero added latency, accepts RPO > 0). Multi-leader and leaderless replication (Dynamo/Cassandra) use quorum tuning plus conflict resolution (LWW, CRDT, version vectors) because any node can accept writes. The combination of replication factor (N), write quorum (W), and read quorum (R) forms the core knob of Dynamo-style storage system design.

---

### ⚙️ How It Works (Mechanism)

**PostgreSQL Synchronous Replication:**
```sql
-- postgresql.conf:
synchronous_commit = 'on'            -- wait for standby WAL write
synchronous_standby_names = '1 (*)'  -- at least 1 standby must confirm

-- Check replication state:
SELECT client_addr, state, write_lag, flush_lag, replay_lag
FROM pg_stat_replication;
-- write_lag: time from WAL write on primary to standby confirming write
-- flush_lag: time to standby confirming flush to disk
-- replay_lag: time to standby applying (visible in standby queries)
```

**Cassandra Quorum:**
```java
// Write quorum (QUORUM = majority of replicas for that token):
session.execute(
    QueryBuilder.insertInto("users")
               .value("id", uuid)
               .value("name", "Alice")
               .setConsistencyLevel(ConsistencyLevel.QUORUM)
);

// Read quorum (reads from majority — intersection with QUORUM write):
session.execute(
    QueryBuilder.selectFrom("users").all()
               .whereColumn("id").isEqualTo(QueryBuilder.literal(uuid))
               .setConsistencyLevel(ConsistencyLevel.QUORUM)
);
// W=QUORUM + R=QUORUM → consistent reads (sees latest write)
// W=ONE   + R=ONE    → fastest, no consistency guarantee
// W=ALL   + R=ONE    → most durable, slowest writes
```

---

### ⚖️ Comparison Table

| Strategy | Durability | Write Latency | Read Staleness | Use Case |
|---|---|---|---|---|
| Async | RPO > 0 | Lowest | Possible lag | Cross-region backup, analytics replicas |
| Semi-sync (1 ACK) | RPO ≈ 0 | Low-medium | Minimal | MySQL production primary-replica |
| Quorum (W+R>N) | Zero (if W+R>N) | Medium | None (if W+R>N) | Dynamo, Cassandra QUORUM |
| Full Sync (W=N) | Zero | Highest | None | Mission-critical, small N |
| Chain Replication | Zero | High (chain depth) | None (TAIL reads) | CRAQ, distributed log systems |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| More replicas = more consistency | More replicas = more durability. Consistency depends on W+R>N, not replica count alone |
| Async replication is always wrong | For read scaling or cross-region observers, async is correct and sync would add unacceptable latency |
| Quorum guarantees linearisability | Quorum writes/reads guarantee that reads see a value from the latest write, but not necessarily a linearisable order without additional mechanisms (e.g., Raft's ReadIndex protocol) |
| Semi-sync means exactly one follower ACKs | MySQL's semi-sync allows configuring a minimum number of replicas; "semi" refers to "not all" |

---

### 🚨 Failure Modes & Diagnosis

**Replication Lag Spike on Primary Overload**

Symptom: Read replica queries return stale data; lag grows from 0ms to 30s;
reads after writes return old values.

Cause: Primary I/O bound or CPU saturated; replica cannot keep pace with binlog
stream; replication thread falls behind.

Diagnosis:
```sql
-- MySQL:
SHOW REPLICA STATUS\G
-- Seconds_Behind_Source: non-zero = lag
-- If growing: primary write rate > replica apply rate

-- Fix: reduce primary write load, add read replicas for read scaling,
--      or switch to semi-sync (ensures replica stays within one write)
```

---

### 🔗 Related Keywords

- `Log Replication` — the mechanism by which Raft/Paxos implement synchronous majority replication
- `Quorum` — the N/2+1 rule that underlies Raft commitment and Dynamo quorum reads/writes
- `Strong Consistency` — the guarantee achievable with synchronous quorum replication
- `Eventual Consistency` — the model that accepts async replication lag in exchange for availability

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  ASYNC:    fast, RPO > 0 (may lose recent writes)        │
│  SEMI-SYNC: wait for 1 replica, RPO ≈ 0                 │
│  QUORUM:   W + R > N → consistent reads always           │
│  SYNC-ALL: zero loss, highest latency                    │
│                                                          │
│  Key formula: W + R > N for read-after-write consistency │
│  N=5 example: W=3, R=3 → consistent                     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Cassandra cluster has N=5 replicas per token (replication factor 5). You need to guarantee that a write is visible to any read immediately after the client receives a success response (read-after-write consistency). What combination of W and R must you configure? If the cluster loses 2 nodes simultaneously, can your W and R configuration still operate? What is the minimum W+R you could use and still guarantee consistency with 5 nodes and tolerate 1 node failure simultaneously?

**Q2.** MySQL primary with async replication has a replica lag of 200ms. A distributed transaction does: (1) insert order → primary; (2) read order → routed to replica. Is the read guaranteed to see the insert? Design a "read-after-write" pattern that ensures the read is consistent without requiring synchronous replication and without routing all reads to the primary.
