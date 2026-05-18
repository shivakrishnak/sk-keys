---
id: DST-017
title: Leader-Follower Replication
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★☆☆
depends_on: DST-008, DST-012, DST-014
used_by: DST-026, DST-027, DST-046
related: DST-012, DST-014, DST-026, DST-046
tags:
  - distributed
  - data
  - replication
  - foundational
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 17
permalink: /technical-mastery/distributed-systems/leader-follower-replication/
---

⚡ TL;DR - Leader-follower replication designates one node
as the leader that accepts all writes and propagates them
to followers; it eliminates write conflicts by design but
creates a write throughput ceiling and a recovery challenge
when the leader fails.

---

### 📋 Entry Metadata

| #017 | Category: Distributed Systems | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Node, Replication, Consistency | |
| **Used by:** | Replication Lag, Read and Write Quorums, Raft Consensus | |
| **Related:** | Replication, Consistency, Replication Lag, Raft | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Two nodes each accept writes to the same record. Node A
receives "set X=10." Node B receives "set X=20" at the
same millisecond. Both writes are committed locally.
Both nodes replicate their version to each other.
Which write wins? There is no systematic answer without
conflict resolution logic. Every write to shared state is
a potential conflict.

**THE CORE INSIGHT:**
Conflicts arise when multiple nodes can write to the same
data simultaneously. The simplest way to eliminate conflicts:
designate exactly one node as the authority for writes.
All writes go through the leader. The leader determines the
canonical order of all writes. Followers apply writes in
the exact order the leader saw them. No conflicts are possible
by design.

---

### 📘 Textbook Definition

**Leader-follower replication** (also: master-slave,
primary-replica, single-leader replication) is a replication
topology where one designated node - the **leader** (primary)
- is the only node that accepts write operations. The leader
maintains a **replication log** (WAL in PostgreSQL, binlog
in MySQL) that records every write in the order it was
applied. **Followers** (replicas, secondaries) subscribe
to this log and apply writes in the same order, eventually
reaching an identical state as the leader. Read requests
can be served by either the leader (strong consistency) or
followers (eventual consistency with possible replication lag).
If the leader fails, one follower is promoted to become
the new leader through an election process.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
One node handles all writes; the rest copy everything it does.

**One analogy:**
> A company's primary database is the CEO. The CEO makes
> all decisions (writes) and sends memos (replication log
> entries) to all branch offices (followers). Branch offices
> can answer questions from their local copies of company
> records (reads), but all policy changes go through the CEO.
> If the CEO is unavailable, the branch offices elect a
> successor from among themselves.

**One insight:**
Leader-follower is the most common replication strategy
because its trade-offs are well-understood and predictable.
The leader is the single source of truth. Followers are
consistent copies with possible lag. The design decision
is: which operations require the source of truth (leader
reads), and which can tolerate lag (follower reads)?

---

### 🔩 First Principles Explanation

**THE REPLICATION LOG:**

Every write committed by the leader is recorded in an
ordered log entry. The log records: the log sequence number
(LSN), the operation type (INSERT/UPDATE/DELETE), the
affected rows, and the new values. Followers stream this
log from the leader and apply each entry in sequence.

```
Leader Replication Log:
┌──────────────────────────────────────────────────────┐
│ LSN  │ Operation │ Table  │ Key  │ New Value          │
├──────┼───────────┼────────┼──────┼───────────────────┤
│ 1001 │ INSERT    │ users  │ id=1 │ {name:'Alice'}    │
│ 1002 │ UPDATE    │ users  │ id=1 │ {email:'a@b.com'} │
│ 1003 │ INSERT    │ orders │ id=5 │ {user:1, amt:100} │
│ 1004 │ DELETE    │ users  │ id=2 │ -                 │
└──────────────────────────────────────────────────────┘

Follower A: applied up to LSN 1003 (1 entry behind)
Follower B: applied up to LSN 1001 (3 entries behind)
Follower B replication lag: higher (network issue?)
```

**SYNCHRONOUS vs ASYNCHRONOUS REPLICATION:**

```
SYNCHRONOUS (durability guarantee):
  Leader → Write to disk
  Leader → Send to follower
  Follower → Write to disk
  Follower → ACK
  Leader → ACK to client

  Write is NOT acknowledged until at least one follower
  has persisted it. If leader crashes after ACK,
  follower has the data.
  Cost: write latency includes follower network RTT.

ASYNCHRONOUS (performance optimized):
  Leader → Write to disk
  Leader → ACK to client     (immediately)
  Leader → Send to follower  (background)
  Follower → Write to disk

  Write acknowledged before follower has the data.
  If leader crashes before replication:
    Data is lost for any writes not yet replicated.
  Cost: none (fire-and-forget replication).

SEMI-SYNCHRONOUS (common default):
  Leader → Wait for exactly ONE synchronous follower
  Leader → Other followers async
  Balance: at least 1 durable follower, reasonable latency.
```

**FAILOVER CHALLENGE:**

When the leader fails, one follower must be promoted:
1. Detect leader failure (timeout, no heartbeats)
2. Elect a new leader (vote among followers, choose
   the one with the most up-to-date log)
3. Update routing so writes go to new leader
4. Reconfigure followers to follow new leader

Complications:
- The new leader may not have all data if using async
  replication. The old leader's un-replicated writes are
  lost or conflict.
- The old leader may come back online after a brief network
  partition, believing it is still the leader (split-brain).
- Fencing tokens or epoch numbers are required to prevent
  the old leader from accepting writes after demotion.

---

### 🧠 Mental Model / Analogy

> Leader-follower replication is like a database version
> of a version control system's main branch. The leader
> is the authoritative main branch. Followers are read-only
> mirrors. Only maintainers (the leader) can merge code
> (accept writes). All mirrors (followers) pull from main
> (replicate). If main is temporarily unavailable, a
> maintainer from a mirror is promoted.

**Mapping:**
- "Main branch" - leader node
- "Read-only mirrors" - followers
- "Merge to main" - write to leader
- "Mirror pulls from main" - follower replication
- "Promote a maintainer" - leader failover/election

**Where the analogy breaks down:** Git merges are explicit,
human-managed events. Replication is continuous, automatic,
and millisecond-level. Failover is automatic (in well-configured
systems) without human involvement.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
One node (the leader) handles all database writes.
All other nodes (followers) copy the writes from the leader.
Reads can come from any node. If the leader crashes, a
follower takes over.

**Level 2 - How to use it (junior developer):**
In PostgreSQL: configure one server as primary, others as
standby (streaming replication). Your application connection
string uses the primary for writes (INSERT, UPDATE, DELETE)
and the standby for reads (SELECT). PgBouncer or a connection
proxy handles the routing.

**Level 3 - How it works (mid-level engineer):**
The leader writes every change to its WAL (Write-Ahead Log)
before applying it. Followers connect to the leader and
stream the WAL continuously. Each follower tracks how far
it has applied the WAL (the "replication position"). Lag
is measured as the difference between the leader's current
WAL position and the follower's applied position. Large lag
means the follower is serving stale data.

**Level 4 - Why it was designed this way (senior/staff):**
Log-based replication was adopted over statement-based
replication because statement replication is non-deterministic:
`INSERT INTO orders SELECT * FROM pending WHERE created < NOW()`
executed at different times produces different results.
Log-based replication records the actual row changes, not
the statement. Given the same log, every follower reaches
the same state - deterministic and exactly reproducible.

**Level 5 - Mastery (distinguished engineer):**
The split-brain problem during failover is the hardest
practical challenge in leader-follower replication. When the
leader becomes unreachable, followers elect a new leader.
If the old leader was merely partitioned (not crashed),
it continues to believe it is the leader and may accept
writes. Two leaders now accept writes simultaneously:
split-brain. The solution requires fencing: the new leader
receives a higher epoch number (term in Raft). Any write
from the old leader must be rejected by the storage layer
if it carries a lower epoch. PostgreSQL uses "pg_replication_slots"
and connection-level authorization to prevent old leaders
from connecting. etcd and Consul use lease-based leadership
that automatically expires.

---

### ⚙️ Mechanism - How Leader-Follower Works

**WAL STREAMING (PostgreSQL):**

```
┌──────────────────────────────────────────────────────┐
│  LEADER (Primary)                                    │
│                                                      │
│  1. Transaction committed to WAL                     │
│     WAL: {lsn:5000, xid:1042, changes:[...]}        │
│                                                      │
│  2. WAL sender process reads WAL segment             │
│  3. Sends WAL records to each connected follower     │
│                                                      │
│            ───────── WAL stream ──────────>          │
│                                                      │
│  FOLLOWER (Standby)                                  │
│                                                      │
│  4. WAL receiver process receives WAL records       │
│  5. Writes to follower's WAL                        │
│  6. Startup process applies WAL to data files        │
│  7. Updates pg_last_wal_replay_lsn() pointer        │
│                                                      │
│  REPLICATION LAG:                                    │
│  leader_lsn - follower_replay_lsn                   │
│  (in bytes of WAL; divide by ~100 to estimate rows) │
└──────────────────────────────────────────────────────┘
```

**FAILOVER SEQUENCE:**

```
t=0: Leader stops responding (crash or partition)
t=3s: Followers' heartbeat timeout fires
t=3s: Followers start election
t=4s: Follower with highest LSN wins election
t=4s: New leader starts accepting writes
t=4s: pgBouncer/HAProxy routes writes to new leader
t=5s: Other followers reconfigure to follow new leader
t=6s: Old leader comes back; sees new epoch number;
      becomes a follower; requests missing WAL from
      new leader; syncs state
Total failover time: ~4-6 seconds
```

---

### 💻 Code Example

**Replication-Aware Connection Routing (Wrong vs Right)**

```python
# BAD: Same connection for reads and writes
db_url = "postgresql://user:pass@db:5432/app"
engine = create_engine(db_url)

def update_user_email(user_id: int, email: str) -> None:
    with engine.connect() as conn:
        conn.execute(
            text("UPDATE users SET email=:email WHERE id=:id"),
            {"email": email, "id": user_id}
        )
        conn.commit()
        # If db_url points to replica: this FAILS
        # Replicas reject writes in PostgreSQL
        # Common mistake: replica is faster (closer to app)
        # so developer points db_url at replica by default
```

```python
# GOOD: Separate connections for reads and writes
from sqlalchemy import create_engine, text, event
from contextlib import contextmanager

# Writes always go to primary
primary = create_engine(
    "postgresql://user:pass@primary:5432/app",
    pool_size=10
)

# Reads can go to replica (accepts replication lag)
replica = create_engine(
    "postgresql://user:pass@replica:5432/app",
    pool_size=20  # more read connections
)

@contextmanager
def read_session():
    """Use for non-critical reads (may be slightly stale)"""
    with replica.connect() as conn:
        yield conn

@contextmanager
def write_session():
    """Use for all writes and reads requiring latest data"""
    with primary.connect() as conn:
        yield conn

# Usage:
def update_user_email(user_id: int, email: str) -> None:
    with write_session() as conn:
        conn.execute(
            text("UPDATE users SET email=:e WHERE id=:id"),
            {"e": email, "id": user_id}
        )
        conn.commit()

def get_user_profile(user_id: int) -> dict:
    # Non-critical read: replica is fine
    with read_session() as conn:
        return conn.execute(
            text("SELECT * FROM users WHERE id=:id"),
            {"id": user_id}
        ).mappings().one()

def get_account_balance(user_id: int) -> Decimal:
    # Critical read: must be from primary
    with write_session() as conn:
        return conn.execute(
            text("SELECT balance FROM accounts WHERE id=:id"),
            {"id": user_id}
        ).scalar()
```

**Detecting Split-Brain (Production)**

```bash
# Check for two PostgreSQL nodes both believing they are primary:
for host in primary-1 primary-2; do
    echo "$host: $(psql -h $host -c 'SELECT pg_is_in_recovery()')"
done

# Expected output:
#   primary-1: f  (false = not in recovery = is primary)
#   primary-2: t  (true = is a follower)

# DANGER - split-brain output:
#   primary-1: f
#   primary-2: f  ← TWO PRIMARIES: split-brain detected

# Immediate action: kill the older primary
# Identify the older primary by WAL LSN:
psql -h primary-1 -c "SELECT pg_current_wal_lsn()"
psql -h primary-2 -c "SELECT pg_current_wal_lsn()"
# The one with LOWER LSN has less data: demote it
```

---

### ⚖️ Comparison Table

| Aspect | Leader-Follower | Multi-Leader | Leaderless |
|---|---|---|---|
| **Write conflicts** | Impossible (one writer) | Possible (conflict resolution needed) | Possible (quorum managed) |
| **Write throughput** | Limited to leader | Scales with leaders | Scales with N |
| **Read scaling** | Good (any follower) | Good | Good |
| **Consistency** | Strong on leader reads | Eventually consistent | Tunable |
| **Complexity** | Low | High | Medium |
| **Best for** | Most databases, OLTP | Multi-region writes | High-availability stores |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Followers can serve the latest data" | Asynchronous followers may serve data that is seconds or minutes old (replication lag). Only the leader or synchronous followers have the latest committed data. |
| "Failover is instant" | Failover requires: detecting failure (timeout), electing a new leader, updating routing. Typically 10-60 seconds even with automation. Design for this window. |
| "The old leader's data is always correct" | After a failover, the old leader may have committed writes that no follower received. If the old leader rejoins as a follower, these un-replicated writes must be discarded. Data loss for acknowledged writes is possible with async replication. |
| "Read from follower is safe if lag is low" | Low lag at query time does not guarantee the specific record you are reading is current. An important record could have been updated 1 second ago and is in the lag window. Critical reads should always go to the leader. |

---

### 🚨 Failure Modes & Diagnosis

**Write to Leader, Read Stale from Follower**

**Symptom:** User updates their shipping address. The order
confirmation email shows the old address. Support confirms
the database has the new address. The email service read
from a replica.

**Root Cause:** Email service read from a follower 200ms
behind the leader. The address update had not yet been
replicated when the email service read it.

**Diagnosis:**
```sql
-- Check replication lag on PostgreSQL:
SELECT
    application_name,
    client_addr,
    state,
    replay_lag,
    pg_size_pretty(
        pg_wal_lsn_diff(
            sent_lsn,
            replay_lsn
        )
    ) as lag_bytes
FROM pg_stat_replication;

-- If lag > 100ms at time of incident: this is the cause.
```

**Fix:** Route reads for "immediately after write" scenarios
to the leader. Implement session-level read-your-writes
by tracking the write LSN and waiting for replica to catch
up, or always routing post-write reads to the leader.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Node` - The units playing leader/follower roles
- `Replication` - The general concept
- `Consistency` - The property affected by replication lag

**Builds On This (learn these next):**
- `Replication Lag` - Deep dive into follower lag:
  measurement, causes, and mitigation
- `Read and Write Quorums` - How quorum replication achieves
  stronger consistency guarantees

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ One leader writes; followers copy        │
├──────────────┼──────────────────────────────────────────┤
│ KEY BENEFIT  │ No write conflicts - single writer,      │
│              │ single source of truth                   │
├──────────────┼──────────────────────────────────────────┤
│ KEY COST     │ Leader = write bottleneck                │
│              │ Followers = possible replication lag     │
├──────────────┼──────────────────────────────────────────┤
│ SYNC REPLIC. │ No data loss on leader failure;          │
│              │ Higher write latency                     │
├──────────────┼──────────────────────────────────────────┤
│ ASYNC REPLIC.│ Low write latency;                       │
│              │ Possible data loss on leader failure     │
├──────────────┼──────────────────────────────────────────┤
│ FAILOVER     │ ~10-60 seconds; requires election,       │
│              │ routing update, follower reconfiguration │
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ Reading from follower after a write      │
│              │ without replication lag awareness        │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Simple consistency: one writer, many    │
│              │  readers, careful with lag."             │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Replication Lag → Read-Your-Writes       │
│              │ Consistency → Raft Consensus             │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Designating a single authoritative source of truth for
any shared mutable state eliminates consistency conflicts
at the cost of availability of that authority. This pattern
appears in: single-leader databases (one primary), Git
(one main branch), event sourcing (one event stream), and
microservices (one service owns a domain's data). The
trade-off is always the same: single-authority = no conflicts
but bottleneck; distributed authority = scales but requires
conflict resolution.

---

### 💡 The Surprising Truth

MySQL's semi-synchronous replication (introduced in 2007)
was designed to prevent data loss by requiring at least one
replica to acknowledge before the leader commits. In practice,
at Google scale, the 100ms or more latency penalty of waiting
for a remote replica was unacceptable. Google's solution
(Spanner) uses atomic clocks and GPS receivers to achieve
global clock synchronization within 7ms, allowing a 14ms
read-write delay that guarantees global ordering without
waiting for quorum messages. The insight: when network
latency is the bottleneck for consistency, eliminating
the need for coordination messages (by knowing the global
time precisely enough) achieves consistency without
the traditional latency cost. Clock uncertainty is the
real enemy of distributed consistency.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. [CONFIGURE] Set up PostgreSQL streaming replication
   with a synchronous standby, verify the standby is in
   sync, and simulate a failover.
2. [DEBUG] A service writes a record and immediately
   reads it back. The read returns the old value. Diagnose
   whether this is a replication lag issue, and implement
   a fix using read-your-writes consistency.
3. [EXPLAIN] The difference between synchronous and
   asynchronous replication, including what guarantees
   each provides on leader failure, and the latency
   implications.
4. [DESIGN] Design the failover procedure for a PostgreSQL
   leader with two async followers. Include: failure detection,
   election criteria, routing update, old leader handling.
5. [PREVENT] Describe the split-brain scenario and implement
   at least one mechanism (fencing token, lease, epoch) to
   prevent two nodes from simultaneously accepting writes.
