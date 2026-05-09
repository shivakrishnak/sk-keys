---
id: DST-025
title: Replication Strategies
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-006, DST-008
used_by: DST-026, DST-027
related: DST-026, DST-028, DST-009, DST-010
tags:
  - distributed
  - replication
  - reliability
  - consistency
  - deep-dive
status: complete
version: 1
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 25
permalink: /distributed-systems/replication-strategies/
---

# DST-025 - Replication Strategies

⚡ TL;DR - Replication strategies define how writes propagate to multiple nodes: single-leader (one sequencer, strong consistency), multi-leader (conflict resolution required), or leaderless (quorum writes, eventual consistency) — each trading off consistency, availability, and complexity.

| Metadata        |                                    |     |
| :-------------- | :--------------------------------- | :-- |
| **Depends on:** | DST-006, DST-008                   |     |
| **Used by:**    | DST-026, DST-027                   |     |
| **Related:**    | DST-026, DST-028, DST-009, DST-010 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A database runs on a single server. One server means: (1) a single point of failure — server crash = system down; (2) a single throughput ceiling — all reads and writes to one disk and CPU; (3) a single geographic location — high latency for remote users. The single server is the simplest architecture and the most fragile.

**THE BREAKING POINT:**
You add a second server for redundancy. Now: how does a write on Server A get to Server B? When? What if the network drops between A and B during a write? What if both servers accept writes and a conflict occurs? The answers to these questions define your replication strategy — and the wrong answer means data loss, data corruption, or system unavailability.

**THE INVENTION MOMENT:**
RDBMS replication began in the 1980s with simple log shipping (Oracle redo logs, Sybase replication). The Internet era (1990s-2000s) drove requirements for global distribution, high availability, and write scaling that single-leader replication couldn't satisfy. Amazon's Dynamo paper (2007) formalized leaderless replication with W+R>N quorums. Google's Spanner (2012) used Paxos-based synchronous replication for external consistency. The space of replication strategies is now a core component of distributed systems design.

**EVOLUTION:**
1980s: Log shipping (synchronous and asynchronous). 1990s: Statement-based replication. 2004: MySQL binary log (row-based replication). 2007: Dynamo leaderless replication with quorums. 2007: CouchDB multi-master replication with MVCC conflict detection. 2012: Spanner synchronous Paxos replication. 2013: Raft-based replication (etcd, CockroachDB). Today: hybrid strategies with configurable consistency levels per operation (Cassandra, MongoDB).

---

### 📘 Textbook Definition

**Replication strategies** are the protocols by which a distributed system propagates writes from their origin to all replicas, maintaining durability, consistency, and availability according to defined trade-offs. The three primary strategies: (1) **Single-leader (primary-replica):** all writes route to one leader; the leader replicates to followers either synchronously (waits for follower ACK) or asynchronously (doesn't wait). (2) **Multi-leader (multi-master):** multiple nodes accept writes; conflicts resolved by last-write-wins, application logic, or CRDTs. (3) **Leaderless (Dynamo-style):** writes sent to all (or N nearest) replicas; acknowledged when W replicas ACK; reads from R replicas with W+R>N guaranteeing overlap with at least one up-to-date replica. Additionally: **chain replication** routes writes through a chain of nodes, with the tail acknowledging to the client; **synchronous replication** waits for all replicas before acknowledging; **asynchronous replication** acknowledges after local write only.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Replication strategy determines who accepts writes, who propagates them, and what consistency guarantee is made to clients — before a single line of application code.

> Replication strategy is like deciding how news spreads in an organization. Single-leader: one editor approves all stories; reporters can only publish via the editor. Multi-leader: multiple regional editors approve stories independently; central office reconciles conflicts. Leaderless: reporters publish simultaneously to multiple bulletin boards; a story is "official" when enough bulletin boards confirm it.

**One insight:** The fundamental replication trade-off: synchronous replication = strong consistency but write latency = slowest replica's latency. Asynchronous = fast writes but data loss risk on leader failure. Leaderless with quorums = tunable consistency/availability, but reads can return stale data if W+R = N+1 but replicas are slow to sync.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Durability requires replication:** A write acknowledged only to one node is lost if that node fails before replication. Minimum durability: write acknowledged only after persisted to at least f+1 nodes (for f failure tolerance).
2. **Consistency requires ordering:** Multiple replicas accepting writes independently will diverge unless they use a total order protocol (consensus) or conflict resolution. No replication strategy achieves strong consistency without a sequencer (leader) or consensus.
3. **W+R>N guarantees overlap:** In leaderless with N replicas, writing to W and reading from R ensures at least one node is in both sets (W+R>N). If W nodes had the latest write: at least one read node has it.
4. **Replication lag is unavoidable in async:** Asynchronous replication means followers are always behind the leader by some amount. This lag is the consistency gap.

**DERIVED DESIGN:**
The choice of replication strategy is determined by the answers to three questions: (1) Can all writes go through a single node? (No: multi-leader or leaderless). (2) Is write durability more important than write latency? (Yes: synchronous replication). (3) Can clients tolerate reading stale data? (Yes: async replication with follower reads).

**THE TRADE-OFFS:**
**Gain:** More replicas = better fault tolerance, read throughput, geographic distribution.
**Cost:** More replicas = more replication overhead (network, disk), more potential for consistency violations, more complex failure modes.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** The CAP theorem constrains what's possible: strong consistency and full availability cannot both be guaranteed under network partition. Every replication strategy is a specific position on the consistency-availability spectrum.
**Accidental:** Configuration complexity (MySQL binlog format, replication filters, Cassandra consistency levels per operation) — these are implementation details, not fundamental requirements.

---

### 🧪 Thought Experiment

**SETUP:** Social network. Users worldwide. Each user has a profile. Profile writes are infrequent but reads are very frequent. Which replication strategy?

**OPTION A: Single-leader, async:**
Leader in US-East. Write latency for EU users: 100ms (transatlantic round-trip to leader). Read latency: 5ms (local EU replica). Stale reads: up to 100ms replication lag — acceptable for profile data. Risk: leader failure = write unavailability during election (~500ms).

**OPTION B: Multi-leader:**
Leader per region (US-East, EU-West). EU write latency: 5ms. US write latency: 5ms. BUT: user updates profile in EU and US simultaneously (two devices) → conflict. Profile fields: name, bio, avatar. LWW (last-write-wins): loses one update. Application merge: concatenate bios? Show both? Conflict resolution is non-trivial for structured profile data.

**OPTION C: Leaderless (Cassandra-style):**
W=2, R=2, N=3. Write to 2/3 replicas: durability with 1 failure tolerance. Read from 2/3 replicas: returns newest value (read repair on stale). Write latency: < 10ms (nearest 2 replicas). Read latency: < 10ms. Stale reads: possible if W+R = N (not N+1) — use W=2, R=2 with N=3 (2+2>3: safe).

**THE INSIGHT:** For profile data (infrequent writes, frequent reads, acceptable stale latency): single-leader async is simplest and safest. For shopping cart (multi-device, need all items even under partition): leaderless with LWW or CRDT merge. For financial transactions (no stale data, no conflicts): single-leader sync or consensus-based replication.

---

### 🧠 Mental Model / Analogy

> Replication strategy is like a news agency's editorial workflow. Single-leader: one central editor-in-chief (leader) approves and publishes all articles; correspondents (followers) republish. Multi-leader: regional editors approve articles independently; a central desk reconciles conflicting regional reports. Leaderless: correspondents publish directly to multiple wire services; a report is "confirmed" when enough services carry it.

**Mapping:**

- **Editor-in-chief** → single leader (primary)
- **Correspondents re-publishing** → async follower replication
- **Regional editors** → multi-leader nodes
- **Conflicting regional reports** → write conflicts requiring resolution
- **Wire service quorum** → W+R>N quorum confirmation

Where this analogy breaks down: news agencies accept "conflicting reports" as natural — distributed databases must converge to a single truth.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When your database has multiple servers, replication is how writes on one server get to the others. The main choice: does one server handle all writes (single-leader), or can multiple servers handle writes (multi-leader or leaderless)? Each choice has trade-offs for reliability, consistency, and performance.

**Level 2 - How to use it (junior developer):**
MySQL primary-replica setup: `CHANGE MASTER TO MASTER_HOST='primary', MASTER_LOG_FILE='mysql-bin.000001', MASTER_LOG_POS=4`. Replica reads the primary's binary log and replays events. For read scaling: route SELECT to replica, INSERT/UPDATE/DELETE to primary. Monitor: `SHOW SLAVE STATUS` for `Seconds_Behind_Master` — alert if > 30 seconds. For MongoDB: replica sets with `w: majority` for durable writes, `readPreference: secondary` for read scaling.

**Level 3 - How it works (mid-level engineer):**
Single-leader (MySQL binlog): On primary, every committed transaction is written to binary log (statement-based or row-based). Replica maintains an I/O thread (reads binlog from primary) and a SQL thread (replays events to local storage). Replication is semi-synchronous: primary can wait for at least one replica to acknowledge binlog receipt (not apply) before confirming to client. This prevents the "data loss window" of fully-async but doesn't guarantee replication to disk. Leaderless (Cassandra): write coordinator sends to N replicas asynchronously. W replicas acknowledge → client success. Background: anti-entropy (Merkle tree comparison) reconciles replicas periodically. Hinted handoff: write coordinator stores write on a proxy node when target replica is down; delivers when replica recovers.

**Level 4 - Why it was designed this way (senior/staff):**
Dynamo's leaderless design (Amazon, 2007) was a deliberate response to the limitations of single-leader replication for a shopping cart service. Amazon's internal SLA required that adding to a shopping cart ALWAYS succeed — even if 2 of 5 replicas are down. Single-leader can't satisfy this during leader election. Leaderless with W=1 can: any single replica accepts the write. The cost: reads might return stale carts. Amazon's solution: let conflicting carts merge (CRDT-style: union of all items). The principle: choose the replication strategy based on the application's specific availability and consistency requirements, not a single global choice. This is why Cassandra exposes consistency level per operation: `QUORUM`, `ONE`, `ALL`, `LOCAL_QUORUM` — allowing per-operation trade-offs.

**Expert Thinking Cues:**

- "How much data can I lose on leader failure?" → `Seconds_Behind_Master` × write rate = potential data loss window for async replication.
- "Why is Cassandra's QUORUM not always consistent?" → With N=3, W=QUORUM(2), R=QUORUM(2): W+R=4>3 → at least 1 overlap. But if a node is slow (hinted handoff): its data may not be in the quorum until delivered. Use `ALL` for strict consistency.
- "Can I use leaderless for financial transactions?" → Only if you can implement conflict resolution (CRDTs, OCC). Most financial systems use single-leader sync for simplicity and correctness.
- "What is chain replication good for?" → High-throughput object storage (HDFS replication, S3). Write goes head→middle→tail. Read from tail only (tail has all committed writes). Throughput: pipelined. Tail failure: reconfigure chain. Head failure: new head picks up from log.

---

### ⚙️ How It Works (Mechanism)

**Single-leader replication (PostgreSQL WAL streaming):**

```
Primary (P):          Standby (S):
WAL Writer            WAL Receiver

1. Client writes → Primary
2. Primary: write to WAL (fsync)
3. Primary: apply to storage
4. Primary: ACK to client (async)
   OR: wait for walreceiver ACK (sync)
5. WAL Sender streams WAL to S
6. S WAL Receiver: writes WAL locally
7. S WAL Applier: applies WAL to storage
   (Lag: S.replay_lsn < P.flush_lsn)
```

**Leaderless replication (Dynamo/Cassandra quorum):**

```
Client → Coordinator:
  Write(key=K, value=V, W=2, N=3)

Coordinator:
  hash(K) → target replicas: [R1, R2, R3]
  send Write(K, V, timestamp) → R1, R2, R3 (async)
  wait for W=2 ACKs
  → client success

Read(key=K, R=2, N=3):
  send Read(K) → R1, R2, R3 (async)
  wait for R=2 responses
  return newest (by timestamp)
  if R1.ts > R2.ts: read repair R2 (async)
  W+R=4 > N=3: at least 1 overlap guaranteed
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (single-leader async replication — MySQL):**

```
Client      Primary (P)   Replica1 (R1)  Replica2 (R2)
  │              │               │               │
  │──UPDATE─────▶│               │               │
  │              │ write to WAL  │               │
  │              │ apply to DB   │               │
  │◀──success───│               │               │
  │              │──binlog─────▶│               │
  │              │               │ apply UPDATE  │
  │              │──binlog────────────────────▶│
  │              │               │          apply UPDATE
  │              ← YOU ARE HERE               │
  │              │ (R1 lag: maybe 5ms)        │
  │              │ (R2 lag: maybe 50ms)       │
  │──SELECT──────────────────▶│ (routed to R1)
  │◀──stale data? ────────────│ (if lag > 5ms: YES)
```

**FAILURE PATH (primary failure, async replication):**
Primary crashes after ACKing to client but before binlog sent to replicas. Replicas promote R1 as new primary (via external coordinator, e.g., Orchestrator, MHA). R1's binlog position < P's last committed position. Missing writes = data loss. Recovery: check binlog on crashed primary (if disk accessible), apply missing events to R1. If disk gone: data loss is permanent.

**WHAT CHANGES AT SCALE:**
At 100,000 writes/second: single-leader replication creates binlog volume of several GB/hour. Replicas must keep up or replication lag grows unboundedly. Scale options: (1) row-based vs. statement-based binlog (row-based = larger but safer); (2) parallel replication (MySQL 5.7+: multiple SQL threads per schema); (3) partial replication (replicate only certain tables to certain replicas). Monitor: `SHOW REPLICA STATUS\G` for `Seconds_Behind_Source`. Production alert threshold: > 10 seconds for most OLTP.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Multi-leader replication conflicts: two leaders accept writes to the same key concurrently. Conflict detection: compare timestamps (LWW — last-write-wins). Risk: clock skew causes incorrect winner. Alternative: vector clocks (detect conflict → application decides). CRDT-based: increment a counter on each leader; merge = max(). Conflict-free for commutative operations (counters, sets). Leaderless: W+R>N guarantees reading the newest version — but "newest" depends on system timestamps (NTP skew) or vector clocks (causally newest).

---

### 💻 Code Example

**BAD - Reading from async replica without handling replication lag:**

```java
// Writes to primary, reads from replica
// WITHOUT checking replication lag
public class UserProfileService {
    private final DataSource primary; // writes
    private final DataSource replica; // reads

    public void updateProfile(String userId, String bio) {
        // Write to primary — OK
        jdbcTemplate(primary).update(
            "UPDATE profiles SET bio=? WHERE id=?",
            bio, userId
        );
    }

    public Profile getProfile(String userId) {
        // Read from replica — PROBLEM:
        // If replica is 5 seconds behind:
        // user updates profile and immediately refreshes
        // → sees OLD profile (stale read)
        return jdbcTemplate(replica).queryForObject(
            "SELECT * FROM profiles WHERE id=?",
            userId
        );
    }
    // No replication lag check → confusing UX
}
```

**GOOD - Read-your-writes consistency with replication lag awareness:**

```java
public class UserProfileService {
    private final DataSource primary;
    private final DataSource replica;
    // Track last write position per user session
    private final Cache<String, Long> userWritePositions;

    public long updateProfile(String userId, String bio) {
        long binlogPos = jdbcTemplate(primary)
            .queryForObject(
                "SELECT @@GLOBAL.gtid_executed",
                Long.class
            );
        jdbcTemplate(primary).update(
            "UPDATE profiles SET bio=? WHERE id=?",
            bio, userId
        );
        long afterPos = jdbcTemplate(primary)
            .queryForObject(
                "SELECT @@GLOBAL.gtid_executed",
                Long.class
            );
        // Track: user made a write at this position
        userWritePositions.put(userId, afterPos);
        return afterPos;
    }

    public Profile getProfile(
        String userId, String sessionId
    ) {
        Long lastWritePos =
            userWritePositions.getIfPresent(userId);
        if (lastWritePos != null) {
            // User recently wrote: ensure replica
            // has caught up to that position
            long replicaPos = jdbcTemplate(replica)
                .queryForObject(
                    "SELECT @@GLOBAL.gtid_executed",
                    Long.class
                );
            if (replicaPos < lastWritePos) {
                // Replica hasn't caught up:
                // read from primary for this user
                return jdbcTemplate(primary).queryForObject(
                    "SELECT * FROM profiles WHERE id=?",
                    userId
                );
            }
        }
        // Safe to read from replica
        return jdbcTemplate(replica).queryForObject(
            "SELECT * FROM profiles WHERE id=?",
            userId
        );
    }
}
```

**Cassandra quorum write (leaderless, tunable consistency):**

```java
import com.datastax.oss.driver.api.core.CqlSession;
import com.datastax.oss.driver.api.core.cql.*;
import com.datastax.oss.driver.api.core.DefaultConsistencyLevel;

public class CassandraProfileStore {
    private final CqlSession session;

    public void writeProfile(String userId, String bio) {
        // QUORUM write: W=2 for N=3 → survives 1 failure
        // AND readable immediately after with QUORUM read
        PreparedStatement stmt = session.prepare(
            "UPDATE profiles SET bio=? WHERE user_id=?"
        );
        BoundStatement bound = stmt.bind(bio, userId)
            .setConsistencyLevel(
                DefaultConsistencyLevel.QUORUM // W=2/3
            );
        session.execute(bound);
    }

    public String readProfile(String userId) {
        // QUORUM read: R=2 for N=3
        // W+R=4>3: at least 1 overlap → linearizable!
        PreparedStatement stmt = session.prepare(
            "SELECT bio FROM profiles WHERE user_id=?"
        );
        BoundStatement bound = stmt.bind(userId)
            .setConsistencyLevel(
                DefaultConsistencyLevel.QUORUM // R=2/3
            );
        Row row = session.execute(bound).one();
        return row != null ? row.getString("bio") : null;
    }
}
```

**How to test / verify correctness:**

```bash
# Test MySQL replication lag:
# On replica:
SHOW REPLICA STATUS\G
# Check: Seconds_Behind_Source (0 = in sync)
# Replica_IO_Running: Yes
# Replica_SQL_Running: Yes

# Test Cassandra consistency:
# Write with QUORUM, read with QUORUM:
cqlsh -e "CONSISTENCY QUORUM;
  UPDATE profiles SET bio='test' WHERE user_id='u1';
  SELECT bio FROM profiles WHERE user_id='u1';"
# Should return 'test' immediately (no stale read)

# Simulate replica failure (Cassandra):
nodetool disablehandoff  # disable hinted handoff
# Kill one Cassandra node
# Write with QUORUM (W=2 of 3): should succeed (2 up)
# Read with ALL (R=3): should fail (1 node down)
# Read with QUORUM (R=2): should succeed
```

---

### ⚖️ Comparison Table

| Strategy            | Consistency               | Write scalability       | Conflict handling | Best for                       |
| :------------------ | :------------------------ | :---------------------- | :---------------- | :----------------------------- |
| Single-leader sync  | Linearizable              | Low (leader bottleneck) | No conflicts      | Financial, OLTP                |
| Single-leader async | Read-your-writes          | Medium                  | No conflicts      | Web apps, profiles             |
| Multi-leader        | Eventual (with conflicts) | High                    | LWW / CRDT / app  | Multi-datacenter, offline      |
| Leaderless (W+R>N)  | Eventual / tunable        | High                    | LWW / read repair | High availability, low latency |
| Chain replication   | Strong                    | High throughput         | No conflicts      | Object storage, HDFS           |

---

### 🔁 Flow / Lifecycle

**Replication lifecycle (single-leader, follower join):**

```
1. INITIAL SYNC
   Follower requests snapshot from leader
   Leader: LOCK TABLES (brief), create snapshot,
           note binlog position at snapshot time
   Follower: apply snapshot
   Leader: UNLOCK TABLES

2. CATCH-UP REPLICATION
   Follower: replay leader's binlog from snapshot
             position to current position
   Monitor: Seconds_Behind_Source decreasing

3. STEADY STATE
   Follower: continuously replaying new binlog events
             from leader (close to real-time)
   Alert: Seconds_Behind_Source > threshold

4. FAILURE RECOVERY
   Leader fails → external coordinator detects (health check)
   Most-up-to-date follower promoted to leader
   Other followers: point to new leader
   Application: redirect writes to new leader

5. DECOMMISSION
   Drain replication: wait for Seconds_Behind_Source=0
   Remove follower from replica pool
   Stop follower
```

---

### ⚠️ Common Misconceptions

| Misconception                                  | Reality                                                                                                                                                                                                                                                                |
| :--------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Async replication is safe for financial data" | Async replication means the primary can acknowledge a committed transaction BEFORE it reaches any replica. Leader failure = potential data loss. Financial systems must use synchronous replication or Raft-based consensus with majority quorum.                      |
| "W+R>N always gives linearizable reads"        | W+R>N guarantees you'll read from at least one node that has the latest write. But if that node uses system timestamps for "latest" (LWW) and clocks are skewed: you may still get stale data. True linearizability requires vector clocks or Paxos/Raft coordination. |
| "Multi-leader replication avoids split-brain"  | Multi-leader makes split-brain WORSE — multiple leaders by design. Conflict resolution must be implemented. LWW is dangerous (clock skew). CRDT-based merge is correct for limited data types only.                                                                    |
| "More replicas always improves read latency"   | More replicas improve READ AVAILABILITY (fewer requests to each). But if consistency level = ALL (read from all replicas), latency = slowest replica. Adding slow replicas with ALL consistency makes reads slower.                                                    |
| "Replication lag is always small"              | Replication lag depends on write rate, network bandwidth, and follower CPU/disk speed. Under heavy load: lag can grow to minutes or hours. High-frequency writes + slow network link = unbounded lag without back-pressure mechanisms.                                 |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Replication Lag Spike Causes Read-After-Write Violations**

**Symptom:** After writing a record, users immediately reading it see the old version. Customer complaints: "I just updated my address but the confirmation page still shows the old one." Application team says "we route writes to primary and reads to replica."
**Root Cause:** Async replication lag between primary and replica. User writes to primary (immediately consistent), reads routed to replica (5-30 second lag). User's own write isn't visible on the replica yet.
**Diagnostic:**

```bash
# Check MySQL replication lag (run on replica):
mysql -u root -p -e "SHOW REPLICA STATUS\G" | \
  grep "Seconds_Behind_Source"
# High lag: diagnose with:
mysql -u root -p -e \
  "SHOW PROCESSLIST\G" | grep "system user"
# "Waiting for dependent transaction to commit"
# = parallel replication bottleneck
```

**Fix:**
BAD: Routing all reads to replica without session-based read-your-writes tracking.
GOOD: After write, route subsequent reads for the same session to primary (for 1-5 seconds), OR use MySQL GTID-based read-your-writes (send GTID with read request to replica; replica waits until it applies that GTID).
**Prevention:** Monitor `Seconds_Behind_Source`. Define application-level read-after-write requirements. Configure read routing strategy accordingly.

**Failure Mode 2: Leaderless Quorum Stale Read from Sloppy Quorum**

**Symptom:** Cassandra cluster with N=3, W=QUORUM(2), R=QUORUM(2). After a node failure and recovery, reads return stale data — the OLD value even after a QUORUM write.
**Root Cause:** Hinted handoff. During node failure: coordinator stored the write as a "hint" on a proxy node (not the target replica). After target replica recovered: hint NOT yet delivered. Read goes to 2 nodes: the recovered (stale) replica and one other node (has new write). Newer write wins — BUT: if the delivered hint was lost (hint store corruption): recovered replica permanently stale.
**Diagnostic:**

```bash
# Check Cassandra hint delivery:
nodetool tpstats | grep -i hint
# If HintsInProgress > 0 for a long time: hints stuck
# Check hint delivery:
nodetool describecluster
# If a node shows "status: Normal" but hints pending:
# Run: nodetool compact -- system hints
```

**Fix:**
BAD: Relying on hinted handoff for durability during extended node outages (> `max_hint_window_in_ms`, default 3 hours).
GOOD: After node recovery: run `nodetool repair` to reconcile all data between replicas using Merkle tree anti-entropy. Ensure repair runs regularly (weekly at minimum) to prevent long-term stale reads.
**Prevention:** Schedule regular `nodetool repair` (Cassandra Reaper automates this). Monitor hint queue length. Alert if pending hints exceed a threshold.

**Failure Mode 3: Security - Replication Credentials in Plaintext Config**

**Symptom:** Security audit finds MySQL replica configuration with replication user password stored in plaintext in `my.cnf` or in `SHOW REPLICA STATUS` output (visible to all users with SUPER privilege).
**Root Cause:** Traditional MySQL replication uses `CHANGE MASTER TO MASTER_PASSWORD='plaintext'` — this password is stored in `mysql.slave_master_info` (visible) and written to `relay-log.info` files on disk.
**Diagnostic:**

```bash
# Check if replication password is visible:
mysql -u root -p -e \
  "SELECT * FROM mysql.slave_master_info\G" | \
  grep -i "user_password"
# If plaintext password appears: security violation
# Check if replication uses SSL:
mysql -u root -p -e "SHOW REPLICA STATUS\G" | \
  grep "Master_SSL_Allowed"
# If "Master_SSL_Allowed: No": unencrypted replication
```

**Fix:**
BAD: `CHANGE MASTER TO MASTER_USER='repl', MASTER_PASSWORD='plaintext'`
GOOD: Use MySQL replication with SSL and credential rotation:

```sql
CHANGE REPLICATION SOURCE TO
  SOURCE_HOST='primary',
  SOURCE_USER='repl',
  SOURCE_PASSWORD='rotated_password',
  SOURCE_SSL=1,
  SOURCE_SSL_CA='/etc/mysql/ca.pem',
  SOURCE_SSL_CERT='/etc/mysql/client.pem',
  SOURCE_SSL_KEY='/etc/mysql/client-key.pem',
  GET_SOURCE_PUBLIC_KEY=1;
```

**Prevention:** Use MySQL's `MASTER_PUBLIC_KEY_PATH` with RSA key pairs instead of passwords for replication authentication. Enable `require_secure_transport=ON` on primary to enforce SSL for all replication connections.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-006 - CAP Theorem (replication strategy is a specific CAP trade-off)
- DST-008 - Consistency Models (each replication strategy produces a specific consistency model)

**Builds On This (learn these next):**

- DST-026 - Log Replication (the mechanism used in single-leader replication)
- DST-027 - State Machine Replication (consensus-based replication for strong consistency)

**Alternatives / Comparisons:**

- DST-028 - Quorum (mathematical basis for leaderless replication guarantees)
- DST-009 - Eventual Consistency (the consistency model produced by async replication)
- DST-010 - Strong Consistency (the consistency model produced by sync replication)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Protocol for propagating writes|
|                  | across multiple replicas       |
+------------------+--------------------------------+
| PROBLEM SOLVED   | Single server: SPOF + no scale |
|                  | Multi-server: how to sync?     |
+------------------+--------------------------------+
| KEY INSIGHT      | Sync=safe but slow; Async=fast |
|                  | but lossy; Quorum=tunable      |
+------------------+--------------------------------+
| USE WHEN         | Any system needing fault       |
|                  | tolerance or read scaling      |
+------------------+--------------------------------+
| AVOID WHEN       | Single-node is sufficient      |
|                  | (simpler, no replication bugs) |
+------------------+--------------------------------+
| TRADE-OFF        | Consistency vs. availability   |
|                  | vs. write latency (CAP)        |
+------------------+--------------------------------+
| ONE-LINER        | Who writes where, wait for     |
|                  | how many ACKs, read from who?  |
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-026 Log Replication,       |
|                  | DST-028 Quorum                 |
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. Single-leader: simple, no conflicts, leader is bottleneck. Multi-leader: write anywhere, requires conflict resolution. Leaderless: quorum writes (W+R>N), tunable consistency, no single failure point.
2. Async replication = potential data loss on leader failure (commits acknowledged before replication). Sync replication = no data loss, but write latency = slowest replica.
3. W+R>N guarantees quorum read overlap — but only if W and R are measured consistently across the same N replicas and timestamps are trustworthy.

**Interview one-liner:**
"The three primary replication strategies are: single-leader (all writes through one node, replicated to followers — simple, consistent, limited by leader throughput), multi-leader (multiple nodes accept writes — conflict resolution required via LWW or CRDTs), and leaderless (writes to W of N replicas, reads from R of N with W+R>N guaranteeing overlap with the latest write — tunable consistency and availability without a single leader bottleneck)."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Every system that maintains state across multiple nodes must answer: who is the source of truth, how does truth propagate, and what happens when propagation fails? The answer defines your consistency, availability, and durability guarantees. These three questions — ownership, propagation, failure behavior — appear in every distributed state management problem: database replication, cache invalidation, CDN content distribution, microservice saga state, event sourcing. Before choosing a database, understand its replication strategy and verify it matches your application's consistency requirements.

**Where else this pattern appears:**

- **CDN content distribution (push vs. pull):** Push replication (origin actively pushes content to edge caches) maps to single-leader eager replication. Pull replication (edge caches fetch from origin on cache miss) maps to lazy/async replication with hinted handoff equivalent (edge serves stale until origin responds). CDN cache invalidation is the leaderless read-repair equivalent: invalidate all edges (W=N) for strong consistency, or let stale content expire (W=1, async) for availability.
- **Event sourcing and CQRS:** An event store is a single-leader append-only log (the "write model"). Projections (the "read models") are async followers. Projection lag = replication lag. Replay from event log = follower catch-up after failure. The CQRS pattern is single-leader async replication applied to domain objects — the write model is the leader, read models are asynchronous followers with eventual consistency.
- **DNS replication:** DNS root servers use a single-leader-like authoritative model (authoritative NS record is the "leader"). Secondary nameservers pull zone transfers periodically (async replication with configurable TTL = acceptable replication lag). DNS TTL is the explicit acknowledgment of stale reads — clients cache DNS answers for TTL seconds, accepting eventual consistency for the read benefit of cached resolution.

---

### 💡 The Surprising Truth

The Amazon Dynamo paper (2007) — which introduced the leaderless, quorum-based replication strategy now used by Cassandra, Riak, and DynamoDB — was not primarily about databases. Dynamo was designed for Amazon's shopping cart. The paper's core observation was: "shopping cart consistency is not required." Amazon's product team explicitly decided that it was better for a customer to see an empty shopping cart (stale read) than to fail to add an item to their cart (unavailability). This means: the foundational paper for eventually-consistent distributed databases was justified not by technical theory but by a business decision about user experience. The right consistency model for your system is determined by the specific failure scenario your users find LEAST tolerable — empty cart vs. no cart at all. Every replication strategy debate ultimately reduces to this: what failure mode is acceptable to your users? The surprising truth: the most theoretically sophisticated distributed systems are designed around product management decisions, not computer science principles.

---

### 🧠 Think About This Before We Continue

**Q1 (C - Design Trade-off):** Single-leader async replication is common for MySQL web applications. A company switches from async to semi-synchronous replication (at least 1 replica ACKs before primary ACKs client). Write latency increases from 2ms to 15ms. The team argues this is unacceptable. What specific application scenarios actually REQUIRE the 13ms of additional latency, and for what scenarios is async replication genuinely safe?
_Hint:_ Semi-synchronous is required when: the PRIMARY crashing after client ACK would cause user-visible data loss (financial transaction, user account creation, order placement). Async is acceptable when: the data can be reconstructed from a different authoritative source (cache data, denormalized counts), or the user-visible impact of losing 1 second of writes is acceptable (activity feeds, analytics events, non-critical profile updates). Can you identify which tables in your application need semi-sync and which are safe with async?

**Q2 (D - Root Cause):** A Cassandra cluster is experiencing "ghost reads" — read requests return data that was deleted minutes ago. The cluster uses W=QUORUM, R=QUORUM, N=3. Compaction is running. No recent node failures. What is the most likely cause, and how does Cassandra's tombstone mechanism interact with quorum reads to produce ghost reads?
_Hint:_ Cassandra marks deletes with tombstones (not immediate removal). A quorum read returns the newest version by timestamp. If tombstones are not yet propagated to all replicas — and a read quorum happens to query two replicas without the tombstone — the read may return the "old" (not-yet-deleted) data. What happens when `gc_grace_seconds` expires and compaction removes tombstones from some replicas but not others? Is this a quorum violation or expected Cassandra behavior?

**Q3 (A - System Interaction):** A multi-leader (multi-master) setup has two MySQL nodes (M1, M2) in a master-master configuration. A developer runs: `INSERT INTO orders(id) VALUES(1)` on M1 and simultaneously `INSERT INTO orders(id) VALUES(1)` on M2. Both succeed locally. What happens when replication catches up, and how does MySQL handle the duplicate key conflict in a multi-master setup?
_Hint:_ MySQL multi-master replication does NOT automatically resolve duplicate key conflicts. When M1's INSERT replicates to M2 (or vice versa), the replica encounters a duplicate key error and by default STOPS replication (SQL thread crashes). The conflict must be manually resolved: `SET GLOBAL SQL_SLAVE_SKIP_COUNTER=1; START SLAVE;` skips the conflicting event. What does this mean for multi-master MySQL setups without application-level conflict prevention? What specific design patterns prevent duplicate key conflicts in MySQL multi-master?
