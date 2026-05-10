---
id: DST-047
title: Strong Consistency
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-022, DST-035, DST-040
used_by: DST-038, DST-008, DST-043
related: DST-022, DST-034, DST-035, DST-023, DST-040
tags:
  - distributed
  - consistency
  - deep-dive
  - advanced
  - foundational
  - production
status: complete
version: 2
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 24
permalink: /distributed-systems/strong-consistency/
---

# DST-036 - Strong Consistency

⚡ TL;DR - Strong consistency (linearizability) guarantees every read reflects the most recent write across all replicas, making a distributed system appear as a single correct copy at the cost of coordination overhead on every operation.

| Metadata        |                                             |     |
| :-------------- | :------------------------------------------ | :-- |
| **Depends on:** | DST-022, DST-035, DST-040                   |     |
| **Used by:**    | DST-038, DST-008, DST-043                   |     |
| **Related:**    | DST-022, DST-034, DST-035, DST-023, DST-040 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A distributed ledger system processes $10M per day. The team chose "high availability" and used an eventually consistent database. One morning, a trade settlement reads Account A balance as $500,000 (stale replica). The actual balance (on primary) is $200,000 — a $300,000 withdrawal happened 200ms ago and hasn't propagated yet. The trade is booked. The account is now $100,000 overdrawn. The replication lag that was a "minor technical detail" became a nine-figure risk event.

**THE BREAKING POINT:**
Two microservices coordinate: `InventoryService` decrements stock to 0; `OrderService` reads stock level to validate the order. Both services use the same eventually consistent database. The read happens 100ms after the write, during a replication lag spike. `OrderService` sees stock = 1. Order accepted. Stock is actually 0. 10,000 orders placed for 9,000 units. The team discovers that "we're API-consistent" and "we're data-consistent" are not the same claim.

**THE INVENTION MOMENT:**
Maurice Herlihy and Jeannette Wing formalized linearizability in their 1990 paper "Linearizability: A Correctness Condition for Concurrent Objects." They defined it as: each operation appears to take effect instantaneously at some point between its invocation and its response. This gave engineers a precise, testable definition of "strong consistency" that could be reasoned about and verified.

**EVOLUTION:**
1990: Linearizability defined (Herlihy-Wing). 1998-2005: Paxos becomes the consensus algorithm for strong consistency in distributed systems (Chubby, ZooKeeper). 2012: Spanner achieves global linearizability using TrueTime. 2013: CockroachDB, FoundationDB ship linearizability as a primary feature. 2017-2020: Cloud providers add strongly consistent options (DynamoDB strongly consistent reads, Cosmos DB Strong consistency level, Cloud Bigtable strong consistency mode).

---

### 📘 Textbook Definition

**Strong consistency** (linearizability or external consistency) is the strictest consistency guarantee for a distributed data store. It ensures: (1) every read returns the value of the most recent write that completed before the read began; (2) operations appear to take effect atomically at a single point in time between their invocation and response; (3) the observable behavior of the system is identical to a single-copy, single-threaded execution. Strong consistency requires coordination among replicas — typically through consensus protocols (Paxos, Raft) or leader-based read protocols — at the cost of increased latency and reduced availability under partition (per CAP theorem).

---

### ⏱️ Understand It in 30 Seconds

**One line:** Strong consistency makes a distributed system behave like a single server — any read, from any node, at any time, returns the most recent write.

> Imagine a bank with 100 branches. Strong consistency is the policy: before any teller can tell you your balance, they call HQ and get the live, real-time number — regardless of which branch you walk into. No teller uses yesterday's printout. Every query goes to the single source of truth.

**One insight:** Strong consistency is not about being slow — it's about coordination. The cost is the network round-trip to a leader or quorum. Within a single datacenter, that's 1-5ms. The question is not "can we afford strong consistency?" but "where does correctness matter enough to pay the coordination cost?"

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. In any valid execution, operations appear in a total order.
2. That total order is consistent with real-time ordering: if op A completes before op B begins, A precedes B in the order.
3. Each read returns the value of the most recent write in that total order.
4. These invariants require that at least one node has authoritative state before any read can proceed.

**DERIVED DESIGN:**
Strong consistency requires either:
(a) **Single-leader reads**: All reads served by the leader node, which has the latest committed state. (ZooKeeper, etcd, Raft leader reads)
(b) **Quorum reads**: Read from a quorum (majority) of replicas; with quorum writes, read quorum always overlaps write quorum, so at least one node has latest value. (Cassandra QUORUM, Dynamo QUORUM)
(c) **Commit-wait (Spanner)**: After commit, wait for clock uncertainty bound `2ε` before returning. Ensures no future read on any node can return a lower timestamp.

**THE TRADE-OFFS:**
**Gain:** Correctness guarantees that enable sequential reasoning. Application code can treat the distributed system as a single variable — no stale-read handling required.
**Cost:** Every operation requires network coordination. Under partition (CAP), the system must refuse operations (become unavailable) or violate consistency. Leader is a throughput bottleneck for writes.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Coordinating distributed nodes takes network round-trips. This latency is irreducible — the speed of light constrains cross-region synchronization.
**Accidental:** Many strong consistency implementations add unnecessary overhead (2PC for all operations, global locks) when per-key linearizability via single-leader would suffice.

---

### 🧪 Thought Experiment

**SETUP:** A distributed lock service. Two servers (S1, S2) compete for a lock protecting a critical section. The lock is stored in a distributed database.

**WITHOUT STRONG CONSISTENCY:**
S1 reads the lock: `lock = null`. S2 reads the lock: `lock = null` (from a replica with replication lag). S1 writes: `lock = S1`. S2 writes: `lock = S2` (doesn't see S1's write yet). Both S1 and S2 believe they hold the lock. Both enter the critical section simultaneously. The critical section is violated. Data corruption.

**WITH STRONG CONSISTENCY:**
S1 reads: `lock = null` (from leader). S1 writes: `lock = S1` (via Compare-And-Set, goes through Raft). Raft replicates to majority; write committed. S2 reads: `lock = S1` (leader serves latest committed value). S2 waits. S1 finishes; writes `lock = null`. S2 retries, acquires lock. No simultaneous access. Critical section safe.

**THE INSIGHT:** Distributed locks are only correct with strong consistency. Any distributed coordination primitive (leader election, distributed counters, distributed mutexes) requires linearizability. This is why etcd and ZooKeeper exist: they provide the linearizable foundation everything else can build on.

---

### 🧠 Mental Model / Analogy

> Strong consistency is the policy of a Supreme Court: every ruling is authoritative, applies everywhere simultaneously, and no lower court can contradict it. The "most recent ruling" is always the law, everywhere, immediately after it's issued.

**Mapping:**

- **Supreme Court ruling** → committed write
- **Lower courts** → replicas
- **"The law"** → consistent data state
- **Asking any court what the law is** → read from any node
- **All courts give the same answer** → linearizability guarantee
- **Deliberation delay** → consensus/quorum coordination latency

Where this analogy breaks down: courts have geographic jurisdiction separation; in a distributed system, the consistency requirement applies globally, regardless of which datacenter the client contacts.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Strong consistency means: if you just updated your bank balance and immediately check it, you always see the updated value — even if millions of people are checking their balances simultaneously from around the world. No stale numbers. No "it'll be updated in a few seconds." The update is immediately visible everywhere.

**Level 2 - How to use it (junior developer):**
Choose a strongly consistent database for data where reading stale values is incorrect: account balances, inventory counts, distributed locks, leader election, session state. In practice: etcd, CockroachDB, Spanner, DynamoDB with `ConsistentRead: true`, ZooKeeper. For these systems, no special coding is needed — the database guarantees it. The cost is paid in latency and reduced throughput.

**Level 3 - How it works (mid-level engineer):**
Strong consistency requires consensus before any read or write is acknowledged. Common implementation (Raft leader reads): all writes go through the leader; leader handles all reads directly (no stale replica reads). The leader has the latest committed log entry; any read from the leader returns the committed value. An alternative (Spanner commit-wait): a write completes only after the commit timestamp is guaranteed to be in the past (using TrueTime) — ensures no clock skew can produce a causality violation in future reads.

**Level 4 - Why it was designed this way (senior/staff):**
Herlihy-Wing's key insight: linearizability is _compositional_. If object A is linearizable and object B is linearizable, any system built from A and B is also linearizable. This composability is why linearizability is the standard for distributed systems building blocks. Sequential consistency is NOT compositional — you can't reason about a system of sequential-consistent components the same way. This is why etcd, ZooKeeper, and Chubby commit to linearizability: they're foundations that other systems build on, and composability is essential. The cost is that linearizability is also the most expensive model — it requires O(n) messages per operation for Paxos/Raft, where n is the cluster size.

**Expert Thinking Cues:**

- "Does this operation require a compare-and-swap?" → If yes, you need linearizability.
- "Is this a distributed lock, leader election, or barrier?" → Linearizable store required.
- "What's the P99 write latency from your leader to quorum?" → This is your minimum strong consistency write latency.
- "Are you reading from a follower?" → Then you don't have strong consistency, regardless of what the docs say.

---

### ⚙️ How It Works (Mechanism)

**Leader-based strong consistency (Raft, etcd):**

1. All writes go to the leader via Raft log replication.
2. Leader proposes log entry, replicates to majority of followers.
3. Once majority ACK, leader commits and returns to client.
4. All reads go to the leader (bypassing followers entirely).
5. Leader always has the latest committed state → reads are always fresh.

**Quorum-based (Dynamo-style with QUORUM R+W>N):**

- Write to W=2 nodes (out of N=3), Read from R=2 nodes.
- R+W=4 > N=3 → read and write quorums always share at least 1 node.
- That shared node has the latest write → read is strongly consistent.
- CAVEAT: Cassandra QUORUM is NOT linearizable in the Herlihy-Wing sense — concurrent writes can still create ordering violations without LWTs.

**TrueTime / Commit-wait (Spanner):**

1. Write committed with timestamp T.
2. Spanner waits `2ε` (where ε = max clock uncertainty, ~7ms globally).
3. After wait, timestamp T is guaranteed to be in the past everywhere.
4. Any future read anywhere will have a clock ≥ T → sees this write.
5. Achieves linearizability without synchronous cross-datacenter replication ACKs.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (etcd linear read):**

```
Client
  │
  ├── Write("balance", 500) ──▶ etcd Leader
  │                                   │
  │                          Raft log append
  │                           ├──▶ Follower 1 ACK
  │                           └──▶ Follower 2 ACK
  │                          commit → return OK
  │
  ├── Read("balance") ──────▶ etcd Leader
  │                                   │
  │                          Return 500 (latest commit)
  │                                   │
  ▼                           ← YOU ARE HERE
  Client sees 500 (linearizable)
```

**FAILURE PATH (leader partition):**

```
Network partition separates leader from majority.
Leader can no longer commit new log entries.
New leader elected from majority partition.
Writes to old leader: timeout / rejected.
Reads from old leader: may be stale (leader detects via
  heartbeat timeout, stops serving linearizable reads).
Result: writes fail (unavailable) → CAP: CP behavior.
```

**WHAT CHANGES AT SCALE:**
Leader becomes a write throughput bottleneck at ~50k writes/sec for etcd. Sharding by key space distributes leadership: each shard has its own leader. Cross-shard strong consistency requires distributed transactions (2PC over Raft, as in Spanner or CockroachDB). At global scale, cross-region linearizability requires commit-wait (10-30ms added per transaction).

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Two concurrent writes to the same key under linearizability: the system serializes them via the Raft leader. The second write sees the result of the first (regardless of network delivery order). No silent data loss. No last-write-wins. The ordering is deterministic and observable. This is why distributed mutual exclusion (distributed locks) is only safe on linearizable stores.

---

### 💻 Code Example

**BAD - Using eventually consistent read for distributed lock:**

```java
// Using Redis with default (eventually consistent) behavior
// Two instances race for a lock
public boolean acquireLock(String lockKey, String holder) {
    // Non-atomic: read then write
    String current = redis.get(lockKey); // may be stale
    if (current == null) {
        redis.set(lockKey, holder);       // race condition!
        return true;
    }
    return false;
}
// Two instances can both see null and both acquire lock
// → critical section violated
```

**GOOD - Using atomic Compare-And-Set for linearizable lock:**

```java
// Redis SET NX EX: atomic, linearizable on single-node Redis
// Or use etcd for distributed linearizable CAS

// Redis single-node linearizable (not distributed):
public boolean acquireLock(
    String lockKey,
    String holder,
    long ttlMs
) {
    // SET key value NX PX ms — atomic on Redis
    Boolean acquired = redis.set(
        lockKey, holder,
        SetArgs.Builder.nx().px(ttlMs)
    );
    return Boolean.TRUE.equals(acquired);
}

// etcd linearizable distributed lock (truly distributed):
public boolean acquireDistributedLock(
    Client etcdClient,
    String lockPath,
    String holder
) throws ExecutionException, InterruptedException {
    Lock lockClient = etcdClient.getLockClient();
    // etcd lock: linearizable, fencing-token-aware
    LockResponse response = lockClient
        .lock(ByteSequence.from(lockPath, UTF_8))
        .get();
    // response.getKey() is the fencing token
    return response != null;
}
```

**How to test / verify correctness:**

```bash
# Jepsen: run linearizability test against your cluster
# https://github.com/jepsen-io/jepsen
# Specific tests for etcd, ZooKeeper, Cassandra available

# Quick sanity: write then immediately read from a follower
# If strongly consistent: follower must redirect to leader or
# serve committed value. If it serves a stale value: not linearizable.

# etcd: force linearizable read:
etcdctl get mykey --consistency=l  # l=linearizable, s=serializable
```

---

### ⚖️ Comparison Table

| Property                     | Strong (Linearizable)            | Sequential           | Causal                 | Eventual                   |
| :--------------------------- | :------------------------------- | :------------------- | :--------------------- | :------------------------- |
| Reads see latest write       | Always                           | Maybe (no real-time) | Causally related only  | Eventually                 |
| Coordination cost            | High (consensus)                 | Medium (sequencer)   | Low (vector clocks)    | None                       |
| Availability under partition | Low (refuse ops)                 | Low-Medium           | High                   | Highest                    |
| Write latency                | +consensus RTT                   | +sequencer RTT       | Low                    | Lowest                     |
| Application complexity       | Low (simple reads)               | Medium               | High (track causality) | High (conflict resolution) |
| Use case                     | Locks, balances, leader election | Shared memory models | Social feeds, comments | Counters, analytics, DNS   |

---

### ⚠️ Common Misconceptions

| Misconception                                                  | Reality                                                                                                                                                                                                                                                                          |
| :------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "QUORUM reads/writes in Cassandra give strong consistency"     | Cassandra QUORUM guarantees that read and write quorums overlap, but WITHOUT Lightweight Transactions (Paxos), concurrent writes can still produce non-linearizable histories. Jepsen confirmed this empirically.                                                                |
| "Strong consistency means slow databases"                      | etcd handles 10k+ linearizable writes/sec. CockroachDB handles hundreds of thousands of linearizable ops/sec across clusters. "Strong" describes correctness, not performance.                                                                                                   |
| "We don't need strong consistency because we use transactions" | ACID transactions provide isolation and atomicity, but not linearizability across distributed nodes by default. Two services in separate databases are NOT strongly consistent even if each service uses transactions internally.                                                |
| "Strong consistency is only for financial applications"        | Distributed leader election, configuration management, service discovery, distributed locks — all require strong consistency. Most modern infrastructure (etcd, ZooKeeper, Consul) provides strong consistency for exactly this reason.                                          |
| "Reading from primary gives strong consistency in MySQL"       | MySQL replication is asynchronous by default. Reading from primary avoids stale replica reads, but if primary failover occurs during a transaction, you can still see non-linearizable behavior. Synchronous replication (AFTER_SYNC binlog) is required for strong consistency. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Leader Bottleneck Causing Write Saturation**

**Symptom:** Write throughput plateaus at ~5k/sec despite adding more nodes. Adding nodes makes it worse (more Raft replication overhead). P99 write latency climbs from 5ms to 500ms under load.
**Root Cause:** Single leader serializes all writes. Raft replication adds per-write network round-trip to quorum. As cluster grows, quorum size grows, increasing per-write latency.
**Diagnostic:**

```bash
# etcd metrics:
curl http://etcd-leader:2381/metrics | grep etcd_disk_wal_fsync
# Look for high fsync latency:
curl http://etcd-leader:2381/metrics | grep -E "etcd_network|etcd_server_proposals"
# CockroachDB:
SHOW RANGES FROM TABLE mytable;
# Check if hot ranges are all on one node
```

**Fix:**
BAD: Adding more Raft replicas to improve write throughput.
GOOD: Shard data across multiple Raft groups (CockroachDB ranges, etcd namespaces). Apply strong consistency only where needed; use eventual for bulk data.
**Prevention:** Design data model to minimize hot key contention. Use sharding from day one for high-write workloads needing strong consistency.

**Failure Mode 2: Stale Leader Serving Reads After Partition**

**Symptom:** After a network partition, clients connected to the old leader read stale data. New leader elected; old leader doesn't know it's deposed. Old leader continues serving reads for ~5 seconds (election timeout).
**Root Cause:** Old leader hasn't received heartbeats, but hasn't yet timed out and stepped down. During this window, it serves reads that are no longer authoritative.
**Diagnostic:**

```bash
# etcd: check leader identity from all nodes:
for host in etcd1 etcd2 etcd3; do
  echo "$host: $(etcdctl --endpoints=$host:2379 endpoint status)"
done
# Look for two nodes claiming leadership simultaneously
```

**Fix:**
BAD: Using etcd's default serializable reads (allows stale reads from non-leader).
GOOD: Use `--consistency=l` (linearizable reads in etcd), which verifies leadership before serving the read.
**Prevention:** Always use linearizable reads (`--consistency=l` in etcd, `linearizable=true` in CockroachDB) for correctness-critical paths. Accept the extra RTT.

**Failure Mode 3: Security - Confused Deputy via Stale Auth Token**

**Symptom:** A service account's permissions are elevated at time T. Between T and T+5s (replication lag), a second service reads the permission cache. The second service sees the pre-elevation permissions and refuses the operation. Alternatively: permissions are REVOKED at T, but for 5s the service sees the elevated permissions and allows unauthorized operations.
**Root Cause:** Permission store uses eventually consistent reads. Auth service caches permissions with TTL matching the replication lag window. An adversary who can time their request within the revocation window can exploit the gap.
**Diagnostic:**

```bash
# Check if auth service uses consistent reads:
grep -r "ConsistentRead\|QUORUM\|linearizable" auth-service/
# Check permission cache TTL:
grep -r "permissionCacheTTL\|cache.ttl" auth-service/
```

**Fix:**
BAD: Permission reads with eventual consistency and 30s TTL.
GOOD: Permission reads with strong consistency (no caching, or zero-TTL cache with linearizable read-through). For revocation specifically: use a separate "deny list" stored in a linearizable system (etcd), checked on every auth.
**Prevention:** Classify auth and permission data as requiring strong consistency. Non-negotiable security requirement.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-022 - CAP Theorem (why strong consistency has availability cost)
- DST-035 - Consistency Models (strong consistency in the broader spectrum)
- DST-040 - Consensus Algorithms (the mechanism behind strong consistency)

**Builds On This (learn these next):**

- DST-038 - Distributed Transactions (strong consistency across multiple resources)
- DST-008 - Leader Election (requires strong consistency to be safe)
- DST-043 - Distributed Locking (linearizability is required for correctness)

**Alternatives / Comparisons:**

- DST-023 - Eventual Consistency (the trade-off: lower coordination, weaker guarantees)
- DST-037 - Causal Consistency (middle ground: causal ordering without full coordination)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Linearizability: reads always  |
|                  | see the most recent write      |
+------------------+--------------------------------+
| PROBLEM SOLVED   | Stale reads causing correctness|
|                  | failures in critical systems   |
+------------------+--------------------------------+
| KEY INSIGHT      | Requires coordination; trades  |
|                  | latency for correctness        |
+------------------+--------------------------------+
| USE WHEN         | Locks, balances, leader elec., |
|                  | config, distributed counters   |
+------------------+--------------------------------+
| AVOID WHEN       | High-throughput analytics,     |
|                  | social feeds, counters, DNS    |
+------------------+--------------------------------+
| TRADE-OFF        | Correctness vs. latency and    |
|                  | availability under partition   |
+------------------+--------------------------------+
| ONE-LINER        | Behaves like single-server:    |
|                  | any read = most recent write   |
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-040 Consensus Algorithms,  |
|                  | DST-043 Distributed Locking    |
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. Linearizability = every read returns the most recent committed write; operations appear atomic in real time.
2. Requires consensus (Raft/Paxos) or leader-based reads — not just quorum (Cassandra QUORUM is NOT linearizable without LWTs).
3. Under partition (CAP), strongly consistent systems choose correctness over availability — they refuse operations rather than risk stale responses.

**Interview one-liner:**
"Strong consistency (linearizability) makes a distributed system behave like a single node — any read from any node always returns the most recent write, achieved through consensus protocols or leader reads, at the cost of coordination latency and availability under network partition."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
The cost of strong consistency is coordination; the cost of weak consistency is correctness bugs. The engineering decision is not "which is cheaper" but "what is the worst-case impact of a stale read in this specific context?" Apply strong consistency precisely where stale reads cause system failures or security violations — not as a blanket policy, and not by accident through default database configuration.

**Where else this pattern appears:**

- **Distributed version control (Git):** A `git push --force` after `git pull` is an attempt at strong consistency (you must have the latest state before overwriting). Without it, lost updates (force push over someone else's work) occur — exactly the lost-update failure of eventually consistent stores.
- **Hardware cache coherence (MESI protocol):** CPUs implement strong consistency within a machine through cache coherence protocols. Every core sees a coherent view of memory. This is the hardware analog of linearizability — and it's why single-machine programs don't need to think about stale reads.
- **2-Phase Commit (2PC):** Distributed transactions achieve strong consistency across multiple resources by making all participants agree before any commits. The coordinator is the "Raft leader" analog. The cost is blocking on coordinator failure — same CAP trade-off at the transaction layer.

---

### 💡 The Surprising Truth

Most databases that claim "strong consistency" or "CP" do not provide linearizability. Jepsen tests (2013-present) have found consistency violations in MongoDB, Cassandra, Redis Sentinel, and others — systems widely marketed as "strongly consistent" or "CP." The distinction is subtle: a system can be "CP in CAP" (refuses writes during partition) while still allowing stale reads from followers during normal operation. True linearizability requires that EVERY read go through a consensus round or a verified leader. The databases that actually provide linearizability as a hard guarantee (with proof, not just marketing): etcd, ZooKeeper (with `sync()`), Spanner, CockroachDB, and FoundationDB. For every other database, check the Jepsen analysis before assuming strong consistency.

---

### 🧠 Think About This Before We Continue

**Q1 (C - Design Trade-off):** A distributed rate limiter must ensure no more than 1,000 requests/second per user across 50 API server instances. Two options: (A) strongly consistent counter in etcd, (B) eventually consistent sharded counter where each API server tracks its own shard and lazily synchronises. Under what traffic pattern does option B catastrophically fail, and under what traffic pattern does option A become a bottleneck? Is there a hybrid that avoids both failure modes?
_Hint:_ Option B fails when all traffic for one user concentrates on one API server for a burst. Option A fails when 1,000 concurrent rate-limit checks hit etcd simultaneously. What does "token bucket with eventual consistency" look like?

**Q2 (D - Root Cause):** A team uses Cassandra with `ConsistencyLevel.QUORUM` for both reads and writes (N=3, W=2, R=2). They believe this gives strong consistency. A Jepsen test reveals linearizability violations. What is the mechanism by which QUORUM on Cassandra violates linearizability even though R+W > N guarantees quorum overlap?
_Hint:_ QUORUM overlap guarantees that at least one node in the read quorum has the latest write. But what happens if two concurrent writes are committed at the same wall-clock time on different nodes? Does Cassandra use a consensus protocol to serialize concurrent writes, or does it use Last-Write-Wins?

**Q3 (B - Scale):** Google Spanner achieves global strong consistency across datacenters using TrueTime. TrueTime provides a clock uncertainty bound of ±ε (approximately 7ms). Spanner's commit-wait adds 2ε to every transaction. If ε grows from 7ms to 100ms (e.g., GPS signal lost, atomic clock drift), what happens to Spanner's correctness and performance? Does it fail safe or fail open?
_Hint:_ Spanner's correctness guarantee depends on the uncertainty bound being accurate. If the actual uncertainty exceeds ε, the commit-wait is insufficient. Consider: does Spanner fail by returning incorrect data, or by refusing transactions? What instrumentation exists to detect GPS/clock anomalies?
