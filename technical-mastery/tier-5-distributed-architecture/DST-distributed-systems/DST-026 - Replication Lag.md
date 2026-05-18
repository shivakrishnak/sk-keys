---
id: DST-026
title: Replication Lag
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-012, DST-017
used_by: DST-028, DST-038
related: DST-012, DST-014, DST-017, DST-027
tags:
  - distributed
  - replication
  - consistency
  - operational
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 26
permalink: /technical-mastery/distributed-systems/replication-lag/
---

⚡ TL;DR - Replication lag is the delay between a write
being applied on the leader and appearing on a follower;
it causes stale reads and read-your-own-writes violations
silently with no error, making it one of the most
operationally dangerous consistency problems in production
distributed systems.

---

### 📋 Entry Metadata

| #026 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Replication, Leader-Follower Replication | |
| **Used by:** | Eventual Consistency, Distributed Cache | |
| **Related:** | Replication, Consistency, Leader-Follower, Read and Write Quorums | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A user updates their profile picture. The application
writes to the primary database, then immediately redirects
to their profile page. The profile page reads from a
read replica. The replica has 200ms of lag. The user
sees their old picture. They upload it again. Now there
are duplicate writes. The user reports a bug: "the app
loses my photo." There is no bug in the write path - there
is unacknowledged replication lag on the read path.

Another scenario: an e-commerce site uses read replicas
for inventory checks. A product has 1 unit left. Two users
simultaneously check inventory (via replica) and both see
1 unit. Both add to cart. Both check out. The inventory
check uses the replica (lagged); the actual decrement uses
the primary. Result: oversell by 1 unit. Replication lag
silently corrupted the business logic.

**THE CORE INSIGHT:**
Replication lag violates user expectations without raising
any error. All queries return data - it is just not the
most recent data. Application code that does not account
for this will produce subtle correctness bugs that are
very difficult to reproduce (they depend on timing).

---

### 📘 Textbook Definition

**Replication lag** is the difference between the most
recent write position on a leader (primary) and the
position up to which a follower (replica) has applied
writes. It is typically measured in bytes (how far behind
the follower is in the replication log) or in seconds
(how old the latest data on the follower is).

In MySQL/PostgreSQL terms: lag is the difference between
`primary_lsn` (Log Sequence Number on primary) and
`replay_lsn` (LSN applied on replica). In Kafka terms:
lag is the difference between the partition's end offset
and the consumer group's committed offset.

Lag arises from asynchronous replication: the leader
acknowledges the write to the client immediately, then
replicates to followers in the background.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The replica is always a few milliseconds (or seconds)
behind the primary; any read from the replica during
that window returns data as it existed before the
latest write.

**Normal vs problematic:**
```
NORMAL lag: <10ms
  - Acceptable for most read-heavy workloads
  - Analytics queries, dashboard reads

PROBLEMATIC lag: >100ms - seconds
  - After large transactions (ALTER TABLE, bulk import)
  - High write load exceeding replica apply speed
  - Network issues between primary and replica
  - Long-running queries on replica blocking apply
```

**The silent contract:**
```
Primary:  write accepted, acknowledged to client
Replica:  write queued, not yet applied

Client:   sees ACK from primary (success!)
          reads from replica (sees old state!)
          client experience: data lost / wrong
```

---

### 🔩 First Principles Explanation

**WHY LAG EXISTS:**

Leader-follower replication is asynchronous by default.
The sequence:

```
1. Client → Leader: WRITE (user_id=1, name="Alice")
2. Leader: writes to disk, updates WAL/binlog
3. Leader → Client: ACK (success, version=42)
   ↑ Client reads from replica here - sees version 41
4. Leader → Replica: sends WAL entry (async, background)
5. Replica: receives entry, applies to local state
6. Replica: now at version 42
   ↑ Client reads from replica here - sees version 42
```

The window between step 3 and step 6 is the lag window.
During this window, any read from the replica returns
the state from before the write.

**THREE TYPES OF REPLICATION LAG:**

```
┌─────────────────────────────────────────────────────────┐
│ 1. WRITE LAG (most common)                              │
│    Large transactions: single WAL entry applied after   │
│    entire transaction commits on primary                │
│    Fix: break large transactions into smaller ones      │
│                                                         │
│ 2. APPLY LAG                                            │
│    Replica receives log but can't apply fast enough     │
│    Cause: replica CPU/IO overloaded (from read queries) │
│    Fix: dedicated replicas for reads vs standby         │
│                                                         │
│ 3. NETWORK LAG                                          │
│    Log bytes in transit between primary and replica     │
│    Cause: slow/congested network                        │
│    Fix: co-locate primary and replica, or use compressio│
└─────────────────────────────────────────────────────────┘
```

**CONSISTENCY VIOLATIONS FROM LAG:**

| Violation | Description |
|---|---|
| Read-your-writes | User writes to primary, reads own write from replica, sees old value |
| Monotonic reads | User reads v2 from replica-A, then reads v1 from replica-B |
| Consistent prefix reads | Reads see causally-related writes out of order |

---

### 🧠 Mental Model / Analogy

> A stock ticker on a financial news website has a
> "15-minute delay" disclaimer. The market is live
> (primary), but your screen shows prices as they were
> 15 minutes ago (replica with 15-minute lag). If you
> try to trade based on the delayed price, you will get
> the current market price (the actual trade goes to
> the primary), not the one on your screen. In a database,
> there is no disclaimer. The application must know
> which operations require real-time data and route
> them to the primary.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is:**
When you write to a database, the replica (backup)
may not immediately have the new data. For a few
milliseconds (or longer), reads from the replica
return old data. This is called replication lag.

**Level 2 - How to detect it:**
```sql
-- PostgreSQL: check replica lag in bytes and seconds
SELECT
  client_addr,
  state,
  sent_lsn - replay_lsn AS lag_bytes,
  now() - pg_last_xact_replay_timestamp()
    AS replay_delay
FROM pg_stat_replication;

-- MySQL: check lag in seconds
SHOW REPLICA STATUS\G
-- Look for: Seconds_Behind_Source: 3
-- 0 = in sync, >0 = lagging by N seconds
```

**Level 3 - How to mitigate it:**

Route critical reads to the primary. Use sticky sessions
to ensure a user's reads go to the same node that served
their recent write. Implement read-your-writes: if the
user just wrote, wait for the replica to catch up before
reading, or read from primary.

**Level 4 - Why it's a harder problem than it looks:**
Replication lag is non-uniform. Different replicas have
different lag. The application cannot easily know the
lag of the replica it is about to query (since checking
lag is itself a database query). Solutions that work at
small scale (read all critical queries from primary)
create write bottlenecks at large scale. Causal
consistency (track the version you last read and
guarantee future reads are at least as fresh) solves
this but requires distributed state.

**Level 5 - Production war stories:**
GitHub experienced a production outage in 2012 where
replication lag combined with a cache invalidation
pattern caused user data to appear missing. During
failover, the new primary was a former replica with
lag - it was behind the previous primary at the time
of failure. Writes from the last seconds before failure
that had not been replicated were lost. This is called
a replication lag-induced data loss event - distinct
from hardware failure. The fix: use synchronous
replication for the primary-secondary relationship
and asynchronous for read replicas. Write to at least
one synchronous replica before acknowledging.

---

### ⚙️ Mechanism - Inside the Replication Log

**PostgreSQL WAL-based replication:**

```
PRIMARY                         REPLICA
  │                               │
  │ 1. BEGIN transaction          │
  │ 2. INSERT INTO orders(...)    │
  │ 3. COMMIT                     │
  │    → WAL record written       │
  │    → WAL shipped via          │
  │      replication slot         │
  │                            ─────
  │ 4. ACK to client              │ 5. Receive WAL
  │    (write is done)            │ 6. Apply WAL record
  │                               │ 7. Update replay_lsn
  │                               │
  │← gap = replication lag ──────→│
```

**Key metrics for monitoring:**

```bash
# PostgreSQL: lag in bytes:
SELECT
  pg_wal_lsn_diff(
    pg_current_wal_lsn(),
    replay_lsn
  ) AS lag_bytes
FROM pg_stat_replication;

# PostgreSQL: lag in human time:
SELECT extract(epoch from
  now() - pg_last_xact_replay_timestamp()
) AS lag_seconds
FROM pg_stat_replication;

# Alert threshold: lag_bytes > 100MB or lag_seconds > 30
```

---

### 💻 Code Example

**Read-Your-Writes: Wrong vs Right**

```python
# BAD: write to primary, immediately read from replica
# Violates read-your-writes consistency

class UserService:
    def __init__(self):
        self.primary = db.connect(host="primary")
        self.replica = db.connect(host="replica")

    def update_profile(self, user_id: int, name: str):
        self.primary.execute(
            "UPDATE users SET name=%s WHERE id=%s",
            (name, user_id)
        )

    def get_profile(self, user_id: int) -> dict:
        # BUG: reads from replica, may not see the write!
        return self.replica.fetchone(
            "SELECT * FROM users WHERE id=%s", (user_id,)
        )

# Failure: user updates name, page refreshes,
# sees old name. User believes update failed.
```

```python
# GOOD: route reads to primary after recent writes
import time

class UserService:
    def __init__(self):
        self.primary = db.connect(host="primary")
        self.replica = db.connect(host="replica")
        # Track when user last wrote (per-user, per-session)
        self._last_write: dict[int, float] = {}

    def update_profile(self, user_id: int, name: str):
        self.primary.execute(
            "UPDATE users SET name=%s WHERE id=%s",
            (name, user_id)
        )
        # Record that this user just wrote
        self._last_write[user_id] = time.time()

    def get_profile(
        self,
        user_id: int
    ) -> dict:
        # If user wrote recently (within 5s): use primary
        recent_write = self._last_write.get(user_id, 0)
        if time.time() - recent_write < 5.0:
            return self.primary.fetchone(
                "SELECT * FROM users WHERE id=%s",
                (user_id,)
            )
        # Otherwise: safe to use replica
        return self.replica.fetchone(
            "SELECT * FROM users WHERE id=%s",
            (user_id,)
        )
```

**Monitoring Replication Lag**

```python
# Production alert: lag exceeds SLO
import psycopg2

def check_replication_lag(conn_primary):
    """
    Returns replication lag in seconds for each replica.
    Alert if any replica is > 30 seconds behind.
    """
    rows = conn_primary.execute("""
        SELECT
            client_addr,
            extract(epoch from
              now() - pg_last_xact_replay_timestamp()
            ) AS lag_seconds,
            pg_wal_lsn_diff(
              pg_current_wal_lsn(),
              replay_lsn
            ) AS lag_bytes
        FROM pg_stat_replication
    """).fetchall()

    for replica_addr, lag_secs, lag_bytes in rows:
        if lag_secs > 30:
            alert(
                f"REPLICATION LAG: {replica_addr} "
                f"is {lag_secs:.1f}s behind "
                f"({lag_bytes / 1024 / 1024:.1f}MB)"
            )
    return rows
```

---

### ⚖️ Comparison Table

| Strategy | Prevents Stale Reads? | Write Throughput | Latency Cost | Complexity |
|---|---|---|---|---|
| **Read from primary** | Yes | Limited (all reads on primary) | None | Low |
| **Read-your-writes (timer)** | Yes (after write) | High | Small (timer check) | Medium |
| **Synchronous replication** | Yes | Lower (wait for replica ACK) | +round trip to replica | Medium |
| **Quorum reads (W+R>N)** | Yes | Moderate | +1 replica read | High |
| **Accept stale reads** | No | Highest | Lowest | Lowest |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Replication lag is only milliseconds, it doesn't matter" | After a bulk import (ALTER TABLE, large ETL), lag can be minutes. Plan for worst case, not average. |
| "I can check the lag before each read to decide where to route" | Checking lag is itself a database query that adds latency. It also doesn't guarantee the lag won't increase between check and read. |
| "Synchronous replication eliminates lag" | Synchronous replication ensures the replica is in sync at commit time. The replica can still lag if the primary crashes between syncs. |
| "Read replicas are just for scale" | Read replicas are also for fault tolerance. But lag means they are not a perfect copy and failover to them may lose data. |

---

### 🚨 Failure Modes & Diagnosis

**High Replication Lag Causing Incorrect Business Logic**

**Symptoms:**
- "Inventory shows available but order fails at checkout"
- "User reports just-uploaded data disappeared"
- `Seconds_Behind_Source` in MySQL monitoring > 10 seconds
- Spike in lag metrics after batch job or migration

**Root Cause Pattern:**
Large transaction on primary creates a single WAL entry
that the replica must apply atomically. During the
apply window (seconds to minutes), all reads from the
replica see the state before the transaction.

**Diagnosis:**
```bash
# PostgreSQL: identify large transactions causing lag:
SELECT
    pid,
    now() - xact_start AS duration,
    state,
    query
FROM pg_stat_activity
WHERE state = 'active'
  AND xact_start < now() - interval '1 minute'
ORDER BY duration DESC;

# MySQL: show running queries > 60s on replica:
SHOW PROCESSLIST;
# Look for: Time > 60, Command: Query, State: applying binlog

# PostgreSQL: lag for all replicas:
SELECT
    application_name,
    state,
    sent_lsn,
    replay_lsn,
    (sent_lsn - replay_lsn) AS byte_lag
FROM pg_stat_replication;
```

**Fixes:**
1. Break bulk operations into smaller batches with `pg_sleep`
2. Route critical reads to primary until lag drops below threshold
3. Use synchronous replication for standby (not all read replicas)
4. Dedicated replicas for heavy analytics (isolated from write path)

---

### 🔗 Related Keywords

**Prerequisites:**
- `Replication` (DST-012), `Leader-Follower Replication` (DST-017)

**Builds On This:**
- `Eventual Consistency / BASE Properties` (DST-028)
- `Read and Write Quorums` (DST-027)
- `Distributed Cache` (DST-038)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ DEFINITION   │ Delay from write on primary to visible   │
│              │ on replica (bytes or seconds behind)     │
├──────────────┼──────────────────────────────────────────┤
│ SILENT RISK  │ No errors - just stale data returned     │
├──────────────┼──────────────────────────────────────────┤
│ DETECT       │ pg_stat_replication.lag_bytes            │
│              │ MySQL: Seconds_Behind_Source             │
├──────────────┼──────────────────────────────────────────┤
│ MITIGATION   │ Read critical ops from primary           │
│              │ Track writes per user, route accordingly │
│              │ Sync replication for standby             │
├──────────────┼──────────────────────────────────────────┤
│ CAUSES       │ Large transactions, heavy replica reads, │
│              │ network bandwidth, async by default      │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Replicas are always slightly in the past│
│              │  design reads around that contract."     │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

Every asynchronous system has lag. Message queues have
consumer lag. CDNs have cache invalidation delay. Browser
caches have stale CSS. Event streams have processing
delay. The pattern is universal: the consumer is always
a bounded distance behind the producer. The engineering
discipline is: know your lag SLO (how much is acceptable),
monitor it continuously, and design read paths that
account for it explicitly rather than hoping lag will
always be below a threshold.

---

### 💡 The Surprising Truth

PostgreSQL's `hot_standby_feedback` parameter, when enabled,
causes the replica to tell the primary about active queries
on the replica. The primary then delays vacuuming rows
that are visible to those queries. This prevents "snapshot
too old" errors on the replica - but at a cost: the primary
accumulates table bloat and cannot vacuum data that
long-running replica queries are holding open. A single
analytics query running for 6 hours on a replica can cause
table bloat of hundreds of GB on the primary. This is
one of the most counterintuitive failure modes in
PostgreSQL replication: a read query on a replica causing
disk exhaustion on the primary.

---

### ✅ Mastery Checklist

1. [MEASURE] Query `pg_stat_replication` or MySQL's
   `SHOW REPLICA STATUS` and interpret the lag values.
2. [IMPLEMENT] Add read-your-writes logic to a service
   that writes to primary and reads from replica.
3. [DEBUG] Given a lag spike to 3 minutes after a batch
   job, identify which specific query caused it and
   propose a fix.
4. [DESIGN] For an e-commerce inventory system, specify
   which read queries must go to primary and which can
   go to replica, with justification.
5. [EXPLAIN] Why synchronous replication for the standby
   (failover target) is different from synchronous
   replication for all read replicas.
