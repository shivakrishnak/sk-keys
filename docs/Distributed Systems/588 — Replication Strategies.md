---
layout: default
title: "Replication Strategies"
parent: "Distributed Systems"
nav_order: 588
permalink: /distributed-systems/replication-strategies/
number: "588"
category: Distributed Systems
difficulty: ★★★
depends_on: "Leader Election, Consistency Models"
used_by: "MySQL, PostgreSQL, Kafka, Cassandra"
tags: #advanced, #distributed, #replication, #consistency, #durability
---

# 588 — Replication Strategies

`#advanced` `#distributed` `#replication` `#consistency` `#durability`

⚡ TL;DR — **Replication Strategies** are the policies (synchronous, asynchronous, semi-sync, multi-master) defining when a write is "done" — determining the consistency vs. latency vs. availability trade-off in distributed data stores.

| #588            | Category: Distributed Systems       | Difficulty: ★★★ |
| :-------------- | :---------------------------------- | :-------------- |
| **Depends on:** | Leader Election, Consistency Models |                 |
| **Used by:**    | MySQL, PostgreSQL, Kafka, Cassandra |                 |

---

### 📘 Textbook Definition

**Replication Strategies** are policies that determine how data written to one node is propagated to replica nodes and when a write is acknowledged as complete. The four primary strategies: **Synchronous replication** — primary waits for ALL replicas to ACK before responding to client (strong consistency, high write latency, reduced availability); **Asynchronous replication** — primary ACKs client immediately, replicates in background (low latency, risk of data loss on primary failure); **Semi-synchronous replication** — primary waits for at least one replica to ACK (balances latency and durability — at most 1 transaction lost on failover); **Multi-master/Multi-primary replication** — multiple nodes accept writes concurrently, conflicts resolved via last-write-wins, CRDTs, or application logic (highest availability, eventual consistency, conflict risk). Additional dimensions: **Statement-based replication** (replicate SQL statements — non-deterministic functions unsafe), **Row-based replication** (replicate actual row changes — safe, verbose), **Mixed replication**. **Quorum-based replication** (Cassandra, DynamoDB): write acknowledged when W nodes confirm; read from R nodes; consistency iff W + R > N. Replication lag: asynchronous replicas always behind primary; applications reading from replicas may see stale data.

---

### 🟢 Simple Definition (Easy)

Replication strategy: when you write data to the "primary" database, how does it get to the "backup" databases, and when does the system say "write successful"? Synchronous: system waits for all backups to confirm → very safe, slow. Asynchronous: system immediately says OK, sends to backups later → fast, but backup might miss recent writes if primary crashes. Semi-synchronous: middle ground — at least one backup must confirm.

---

### 🔵 Simple Definition (Elaborated)

Real trade-off: a primary DB in us-east, replica in eu-west (80ms RTT). Synchronous: every write waits 160ms+ (round-trip to replica + ACK). Users notice. Asynchronous: writes return in <1ms (no waiting), but if primary crashes, the last 80ms of writes are lost — replica doesn't have them. Semi-sync: waits for the eu-west replica to ACK (160ms for that write) but if eu-west is down, falls back to async. Quorum: Cassandra W=2, R=2, N=3 — at most 1 replica can have stale data; reader always gets at least one up-to-date value.

---

### 🔩 First Principles Explanation

**All four strategies with failure scenarios:**

```
SYNCHRONOUS REPLICATION:

  Write flow:
    Client → Primary: "INSERT INTO orders VALUES (1001, 'user_a', 99.99)"
    Primary: writes to local log.
    Primary → Replica1: "Replicate this write."
    Primary → Replica2: "Replicate this write."
    Wait... wait... wait...
    Replica1 → Primary: ACK.
    Replica2 → Primary: ACK.
    Primary → Client: "Write successful."

  Latency: write_latency = primary_write_time + max(replica1_RTT, replica2_RTT) + replica_write_time.
    Same DC (1ms RTT): ~2-3ms per write. Acceptable.
    Cross-region (80ms RTT): ~160ms per write. Unacceptable for most apps.

  Failure scenarios:
    Replica1 CRASHES during write:
      Primary: waiting for Replica1 ACK indefinitely.
      Options:
        a) Primary times out → returns error to client (write fails). Availability impact.
        b) Primary waits until Replica1 recovers (may be minutes/hours). Blocked.
        c) Primary continues with remaining replicas if quorum satisfied (Raft approach).

      With Raft (quorum-based synchronous): N=5 cluster, W=3 (majority).
        Primary waits for 3 ACKs (including itself): if 1 replica down, 4 remaining → still gets 3.
        One failure tolerated without availability impact. Two failures: primary stops (safety).

  Data loss on failover: ZERO. All replicas have all committed data.
  Use when: financial transactions, configuration data, anything where 0 data loss is required.

ASYNCHRONOUS REPLICATION:

  Write flow:
    Client → Primary: "INSERT INTO orders VALUES (1001, 'user_a', 99.99)"
    Primary: writes to local log.
    Primary → Client: "Write successful." ← IMMEDIATELY (before replica ACK)
    [Background] Primary → Replica1: "Replicate this write."
    [Background] Primary → Replica2: "Replicate this write."
    Replicas apply write asynchronously (100ms - minutes later, depending on load).

  Replication lag: the delay between primary write and replica having the write.
    Typical: 100ms - 10 seconds under normal load.
    Under primary load spike: can grow to minutes.

  Failure scenario — PRIMARY CRASHES:
    Primary has written [tx1, tx2, tx3] but only tx1 has replicated to Replica1.
    tx2, tx3: LOST. Replica1 promoted to primary.
    Applications see data from tx1 but never tx2 or tx3.

    Real-world example: MySQL async replication, primary has 5 seconds of unreplicated writes.
    Primary crashes. Replica promoted. 5 seconds of orders missing. Customers charged but no order.

  Replication lag reading:
    Client writes: update balance to $100 (primary).
    Client reads: balance = $50 (replica, hasn't received update yet).
    Client sees stale data. This is "read-your-writes" violation.

    Fix: route reads to primary, OR wait for replication lag on replica.
    MySQL: SELECT WAIT_FOR_EXECUTED_GTID_SET('<gtid>', 5) — wait for replica to catch up before read.

  Use when: analytics replicas (reads can be slightly stale), geo-replication for disaster recovery
            (acceptable to lose seconds of data if regional DC fails).

SEMI-SYNCHRONOUS REPLICATION:

  Write flow:
    Client → Primary: write.
    Primary: writes locally.
    Primary → ALL replicas: "Replicate."
    Primary waits for AT LEAST ONE replica to ACK.
    Primary → Client: "Write successful."
    Other replicas: continue replicating asynchronously.

  Guarantee: on primary failure, AT MOST 1 transaction lost.
    Why 1?: the primary has committed transaction T. At least 1 replica confirmed T.
    Replica1 has T. Even if Replica2 doesn't: Replica1 promoted → T not lost.

  Failover: must promote a replica that ACKed the latest transaction.
    MySQL: GTID-based auto-failover (MHA, Orchestrator) — promotes replica with highest GTID.

  Latency: primary waits for the FASTEST replica's ACK.
    Same DC replica: minimal latency impact.
    Cross-region: wait for nearest replica → acceptable compromise.

  Degradation: if ALL replicas are slow/unavailable → MySQL times out → falls back to async.
    This is a safety hole! Semi-sync can silently degrade to async under replica failure.

  Use when: MySQL production setups with RPO > 0 but < last-transaction.
            "We can't lose more than 1 write."

QUORUM-BASED REPLICATION (Cassandra, DynamoDB, Riak):

  Parameters:
    N = replication factor (copies of data)
    W = write quorum (number of replicas that must ACK write)
    R = read quorum (number of replicas that must respond to read)

  Consistency iff W + R > N:
    At least (W + R - N) replicas have both the latest write AND are included in the read.
    These "overlap" replicas return the latest value.

  Example: N=3, W=2, R=2:
    Write: ACK from 2 of 3 replicas → "written."
    Read: query 2 of 3 replicas, take latest value (by timestamp or version).
    Overlap: at least 1 replica has both latest write and is queried → consistent.

  Tuning options:
    W=1, R=1: max performance, no consistency (any single replica accepts/serves).
    W=3, R=1: all replicas write, 1 read → consistent (but write throughput limited).
    W=1, R=3: 1 replica writes, all 3 queried → consistent but write bottleneck.
    W=2, R=2, N=3: balanced — tolerates 1 replica failure for both reads and writes.
    W=N, R=1: all writes synchronous → equivalent to synchronous replication.

  Last-Write-Wins (LWW): conflicting writes resolved by timestamp.
    Problem: clock skew → arbitrary conflict resolution (later clock wins, not later write).
    Cassandra: uses coordinator-assigned timestamps. Clients can set explicit timestamps.

  Hinted Handoff (Cassandra failover):
    Node B is down. Write (key, value) goes to A and C (quorum W=2 met).
    A: "I'll hold a 'hint' for B — deliver when B recovers."
    B recovers: A delivers hint → B gets the write.
    Anti-entropy repair: periodic Merkle tree comparison between replicas to find divergence.

MULTI-MASTER (MULTI-PRIMARY) REPLICATION:

  All nodes accept writes. Conflicts possible.

  Use case: MySQL multi-master cluster across DCs.
    DC-east: master writes US data.
    DC-west: master writes EU data.
    Both replicate bidirectionally.

  Conflict: both DCs update same row simultaneously.
    Row A: user_id=1, email='a@old.com'.
    DC-east: UPDATE email='a@new1.com'.
    DC-west: UPDATE email='a@new2.com'.
    Replication delay: each DC ACKs its local write, replicates to other.

  Conflict resolution options:
    Last-Write-Wins (LWW): highest timestamp wins (a@new1.com or a@new2.com — arbitrary).
    Application-defined merge: application provides merge function (e.g., union of tags).
    Conflict detection + rejection: reject second write (optimistic concurrency control).
    CRDT: data structure that merges automatically (e.g., grow-only counter, OR-Set).

  Use when: geo-distributed systems where cross-DC write latency is unacceptable.
            Accept eventual consistency + conflict resolution complexity.

COMPARISON TABLE:

  Strategy         | Latency  | Data Loss Risk    | Availability | Complexity
  ─────────────────┼──────────┼───────────────────┼──────────────┼───────────
  Synchronous      | High     | None (0 loss)     | Lower        | Low
  Asynchronous     | Low      | High (seconds)    | Highest      | Low
  Semi-Synchronous | Medium   | Low (≤1 tx)       | High         | Medium
  Quorum (W+R>N)   | Medium   | Low (tunable)     | High         | Medium
  Multi-Master     | Low      | Conflict risk     | Highest      | High
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT replication strategies (only raw replication):

- No systematic way to trade off consistency vs. latency
- Engineers copy-paste replication setups without understanding failure modes
- Silent data loss: async replication with failover, no one notices missing writes

WITH replication strategies:
→ Explicit consistency contract: W/R quorum, sync/async — know exactly what's guaranteed
→ Tunable trade-offs: change W, R, N to match RPO/RTO requirements
→ Informed architecture: choose semi-sync for MySQL, quorum for Cassandra, based on use case

---

### 🧠 Mental Model / Analogy

> A bank vault with N safety deposit boxes. Synchronous: open your box AND N backup vaults confirm they have a copy before the clerk says "stored." Asynchronous: clerk says "stored" immediately, couriers take copies to backup vaults later. Semi-sync: at least ONE backup vault confirms before the clerk says "stored" — others can catch up. Quorum: write to W of N vaults; read from R of N — overlap guarantees at least one vault has the latest deposit.

"Safety deposit boxes" = replica nodes
"Clerk saying stored" = primary acknowledging write to client
"Couriers to backup vaults" = async replication
"W of N vaults must confirm" = write quorum

---

### ⚙️ How It Works (Mechanism)

**MySQL replication modes:**

```sql
-- CHECK current replication mode:
SHOW VARIABLES LIKE 'rpl_semi_sync%';
-- rpl_semi_sync_master_enabled = ON/OFF
-- rpl_semi_sync_master_wait_for_slave_count = 1 (wait for 1 replica minimum)
-- rpl_semi_sync_master_timeout = 10000 (ms timeout before falling back to async)

-- ENABLE semi-synchronous replication:
SET GLOBAL rpl_semi_sync_master_enabled = ON;
SET GLOBAL rpl_semi_sync_master_wait_for_slave_count = 1; -- Wait for 1 replica
SET GLOBAL rpl_semi_sync_master_timeout = 1000; -- 1 second timeout, then fall back to async

-- CHECK replication lag on replicas:
SHOW SLAVE STATUS\G
-- Seconds_Behind_Master: 0 (up to date), 5 (5 seconds behind), etc.
-- Exec_Master_Log_Pos: position in primary's binlog that replica has applied.

-- GTID-based replication (MySQL 5.6+):
-- Every transaction gets a globally unique ID: server_uuid:transaction_number
-- Example: 3E11FA47-71CA-11E1-9E33-C80AA9429562:1-37

-- On replica: wait until specific GTID applied (ensure read-your-writes):
SELECT WAIT_FOR_EXECUTED_GTID_SET('3E11FA47-71CA-11E1-9E33-C80AA9429562:37', 5);
-- Returns: 0 (GTID applied within 5s), 1 (timeout)
-- Use after write on primary, before read on replica.

-- MONITOR replication lag:
SELECT
    MEMBER_HOST,
    MEMBER_STATE,
    COUNT_TRANSACTIONS_IN_QUEUE,
    COUNT_TRANSACTIONS_CHECKED,
    COUNT_CONFLICTS_DETECTED
FROM performance_schema.replication_group_member_stats;
```

---

### 🔄 How It Connects (Mini-Map)

```
Consistency Models (what guarantees: eventual, strong, linearisable)
        │
        ▼
Replication Strategies ◄──── (you are here)
(HOW data is replicated and WHEN write is "done")
        │
        ├── Log Replication (Raft's mechanism: append entries to replicated log)
        ├── Quorum (W + R > N: the math behind consistent quorum reads)
        └── Conflict Resolution Strategies (multi-master: what to do when replicas diverge)
```

---

### 💻 Code Example

**Cassandra quorum-based replication (W=2, R=2, N=3):**

```java
import com.datastax.oss.driver.api.core.CqlSession;
import com.datastax.oss.driver.api.core.ConsistencyLevel;
import com.datastax.oss.driver.api.core.cql.*;

public class CassandraQuorumExample {

    private final CqlSession session;

    // WRITE with QUORUM consistency (W=2 of N=3 must ACK):
    public void writeUserProfile(String userId, String email) {
        PreparedStatement write = session.prepare(
            "UPDATE user_profiles SET email = ? WHERE user_id = ?"
        );
        BoundStatement statement = write.bind(email, userId)
            .setConsistencyLevel(ConsistencyLevel.QUORUM); // W=2 of 3 replicas

        session.execute(statement);
        // Returns only when 2 of 3 replicas have the write.
        // 1 replica can be down → still succeeds.
        // At most 1 replica has stale data → safe with QUORUM reads.
    }

    // READ with QUORUM consistency (R=2 of N=3 must respond):
    public String readUserProfile(String userId) {
        PreparedStatement read = session.prepare(
            "SELECT email FROM user_profiles WHERE user_id = ?"
        );
        BoundStatement statement = read.bind(userId)
            .setConsistencyLevel(ConsistencyLevel.QUORUM); // R=2 of 3 replicas

        Row row = session.execute(statement).one();
        // Queries 2 of 3 replicas. Takes the value with highest timestamp.
        // Since W=2, R=2, N=3 → W+R=4 > N=3 → always sees latest write.
        return row != null ? row.getString("email") : null;
    }

    // For eventual consistency (max performance, may serve stale):
    public String readEventually(String userId) {
        PreparedStatement read = session.prepare(
            "SELECT email FROM user_profiles WHERE user_id = ?"
        );
        BoundStatement statement = read.bind(userId)
            .setConsistencyLevel(ConsistencyLevel.ONE); // R=1: any replica
        // Fast but may return stale data if replica hasn't synced yet.
        Row row = session.execute(statement).one();
        return row != null ? row.getString("email") : null;
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| --------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Asynchronous replication means data is replicated slowly  | Asynchronous means the primary doesn't WAIT for replication. The actual replication can be near-instant (milliseconds). The "lag" depends on network and replica load. MySQL async replication on the same LAN: typically < 1ms lag under normal load. The risk is not slowness but: during the millisecond before replication completes, if the primary crashes, those writes are lost                                                        |
| Quorum reads always return the latest write               | Quorum reads return the latest write IF W + R > N. If you set W=1, R=1, N=3: no quorum overlap → stale reads possible even with "quorum". Also: Cassandra's quorum reads use timestamps for conflict resolution. If two writes happen with the same timestamp (clock skew), the winning value is arbitrary. Always use monotonic timestamps or explicit version vectors for true latest-write semantics                                        |
| Semi-synchronous replication guarantees no data loss      | Semi-sync guarantees at most 1 transaction lost. If the primary ACKs a transaction to the client, at least 1 replica has it — on failover, promote that replica. BUT: MySQL semi-sync silently degrades to async if the replica ACK times out (configurable timeout, default 10 seconds). During that window: zero replicas confirmed, and if the primary crashes — the transaction is lost. Production must monitor for semi-sync degradation |
| Multi-master replication enables horizontal write scaling | Multi-master enables writes at multiple DCs (reduce latency for geographically distributed users), NOT higher aggregate write throughput. Each master must replicate all writes from all other masters. Total replication work increases with masters. For throughput: shard write traffic (Vitess, CitusDB, CockroachDB) — different nodes own different partitions                                                                           |

---

### 🔥 Pitfalls in Production

**Async replication with read-from-replica causing stale reads:**

```
PROBLEM: e-commerce checkout.
  Client writes order (primary). Client redirected to order-confirmation page.
  Order-confirmation page: reads order (replica). Replica is 200ms behind.
  Order-confirmation page: "No order found" → user calls support.

  This happens in production frequently with async replicas behind a load balancer.

BAD: Reads after writes load-balanced across primary and replicas without lag awareness:
  // Service layer — reads from any DB node (round-robin):
  @Transactional(readOnly = true)
  public Order getOrder(String orderId) {
      return orderRepository.findById(orderId)  // May hit stale replica
          .orElseThrow(() -> new OrderNotFoundException(orderId));
  }

  // Write route:
  @Transactional
  public Order createOrder(OrderRequest req) {
      Order order = orderRepository.save(new Order(req));
      return order;  // Written to primary.
      // But subsequent reads may hit replica with 200ms lag.
  }

FIX 1: STICKY SESSIONS — route user to primary for short window after write:
  @Transactional
  public Order createOrder(OrderRequest req, HttpSession session) {
      Order order = orderRepository.save(new Order(req));
      // Tell this user's session: read from primary for next 500ms.
      session.setAttribute("read_primary_until", System.currentTimeMillis() + 500);
      return order;
  }

  @Transactional(readOnly = true)
  public Order getOrder(String orderId, HttpSession session) {
      Long readPrimaryUntil = (Long) session.getAttribute("read_primary_until");
      boolean readFromPrimary = readPrimaryUntil != null &&
                                System.currentTimeMillis() < readPrimaryUntil;
      DataSource ds = readFromPrimary ? primaryDataSource : replicaDataSource;
      // ... route to appropriate DS
  }

FIX 2: GTID WAIT — replica catches up before serving read-your-writes:
  @Transactional
  public String createOrderAndGetGTID(OrderRequest req) {
      Order order = orderRepository.save(new Order(req));
      // Get current GTID from primary:
      String gtid = jdbcTemplate.queryForObject(
          "SELECT @@gtid_executed", String.class
      );
      return gtid; // Return GTID to client.
  }

  @Transactional(readOnly = true)  // On replica connection
  public Order getOrderConsistent(String orderId, String afterGtid) {
      // Wait for replica to apply GTID before serving read:
      jdbcTemplate.queryForObject(
          "SELECT WAIT_FOR_EXECUTED_GTID_SET(?, 5)", Integer.class, afterGtid
      );
      return orderRepository.findById(orderId).orElseThrow(...);
  }
```

---

### 🔗 Related Keywords

- `Log Replication` — Raft's mechanism for implementing synchronous quorum-based replication
- `Quorum` — the W + R > N mathematics of consistent distributed reads
- `Consistency Models` — what guarantees replications strategies provide (eventual, strong, etc.)
- `Conflict Resolution Strategies` — how multi-master replication handles diverging replicas
- `Hinted Handoff` — Cassandra's mechanism for delivering writes to temporarily unavailable nodes

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Synchronous=0 loss/high latency;         │
│              │ Async=low latency/data loss risk;        │
│              │ Quorum=tunable via W+R>N                 │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Sync: financial data (0 RPO).            │
│              │ Async: analytics replicas. Semi-sync:    │
│              │ MySQL production. Quorum: Cassandra.     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Sync cross-region (160ms+ latency).      │
│              │ Async for primary user data (data loss   │
│              │ on failover catastrophic for business)   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "How many vaults must confirm before     │
│              │  the clerk says 'stored'?"               │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Log Replication → Quorum → Conflict      │
│              │ Resolution → Consistency Models          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a MySQL cluster: 1 primary, 2 replicas, semi-synchronous replication with wait_for_slave_count=1 and timeout=10000ms. The single replica that was ACKing writes goes offline at 2:00 PM. What happens to writes between 2:00 PM and when the DBA notices? What is the RPO (Recovery Point Objective) in the worst case? How does this change if you set wait_for_slave_count=2?

**Q2.** Cassandra cluster: N=5, W=3, R=3. An engineer suggests reducing W to 1 to improve write throughput during a flash sale. After the flash sale, the engineer resets W=3. During the W=1 period, 10,000 writes went to only 1 replica each (other 4 replicas missed them). After restoring W=3, a user reads a key that was written during W=1 period. What does R=3 return? What does Cassandra's read-repair mechanism do? How does anti-entropy repair ensure eventual consistency?
