---
id: SYD-066
title: What is Database Replication (Basic)
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★☆☆
depends_on: ""
used_by: SYD-019, SYD-033
related: SYD-019, SYD-033, SYD-042, SYD-063
tags:
  - fundamentals
  - replication
  - database
  - design
  - beginner
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 66
permalink: /technical-mastery/syd/what-is-database-replication/
---

⚡ TL;DR - Database replication copies data from one
database server (primary) to one or more others
(replicas). Two main purposes: (1) High availability -
if the primary fails, a replica becomes the new primary
(failover). (2) Read scaling - direct read queries to
replicas to reduce load on the primary. The key trade-off:
replication lag. Replicas are slightly behind the primary
(milliseconds to seconds). Reads from a replica may return
stale data. Choose replication for read-heavy systems
where a small amount of staleness is acceptable.

| #066 | Category: System Design | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | (none - foundational concept) | |
| **Related:** | Database Replication (System), Database Internals, Data Partitioning Strategies, What is Scalability | |

---

### 🔥 The Problem This Solves

Your PostgreSQL database is at 90% CPU. Most load is
reads (user profile lookups, product catalog queries).
The primary database handles both reads and writes.
Adding more primary databases is complex (distributed
writes require coordination). The simple solution: add
read replicas. Route reads to replicas, writes to primary.
One primary at 10% write load + three replicas sharing
the read load = 4x read throughput improvement.

---

### 📘 Textbook Definition

**Database replication:** The process of copying and
maintaining database objects (tables, rows) across
multiple database servers in near real-time.

**Primary (master):** The authoritative server that
accepts all write operations (INSERT, UPDATE, DELETE).
Replication flows FROM the primary TO replicas.

**Replica (standby/slave):** A copy of the primary
database. Receives and applies changes from the primary.
Can serve read queries. Cannot accept writes (in
single-leader replication).

**Replication lag:** The delay between a write on the
primary and that change appearing on a replica. Typically
milliseconds on a healthy, fast network. Can grow to
seconds or minutes under heavy write load.

**Synchronous replication:** Primary waits for at least
one replica to confirm the write before acknowledging
success to the client. Zero data loss; higher write latency.

**Asynchronous replication:** Primary acknowledges the
write immediately without waiting for replicas.
Better write performance; risk of data loss if primary
fails before replica receives the change.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Primary handles writes; replicas handle reads.
Replicas lag behind slightly. Adds redundancy and
read throughput.

**One analogy:**
> A head chef and kitchen assistants:
>
> The head chef (primary) makes all decisions and
> creates the official recipe book (data).
> Assistants (replicas) copy the recipe book in
> real time. Customers can ask any assistant for
> a recipe (reads). Only the head chef changes recipes
> (writes). If the head chef is sick: an assistant
> is promoted to head chef (failover). Assistants
> may be a few minutes behind on the latest recipe
> update (replication lag).

**One insight:**
Replication scales reads trivially - add a replica,
add read capacity. But it does NOT scale writes: all
writes still go to one primary. If writes are the
bottleneck, replication alone is not enough - you
need sharding (partitioning). Most systems are read-
heavy (10:1 or 100:1 read-to-write ratio), so
replication solves the most common scalability problem.

---

### 🔩 First Principles Explanation

**HOW REPLICATION WORKS:**
```
Primary → Binary Log (WAL) → Network → Replica

1. Write arrives at primary: INSERT INTO orders(...)
2. Primary writes to its Write-Ahead Log (WAL/binlog)
3. Primary applies change to its data files
4. Primary sends WAL entry to connected replicas
5. Replica receives WAL entry
6. Replica applies the change (replays the write)
7. Replica is now in sync (up to that write)

Asynchronous (default in MySQL, PostgreSQL):
  Primary: step 1-3 done, ACK to client
  Steps 4-7 happen after the client gets success.
  Risk: if primary crashes between step 3 and step 4,
        the write is on primary but never reached replica.
        Failover to replica = that write is LOST.

Synchronous (optional):
  Primary: step 1-4 done
  Wait for at least one replica to confirm step 6
  Then ACK to client.
  Risk: if replica is slow/unreachable = write is blocked.
  Use: when zero data loss is required (financial systems).
```

**READ ROUTING:**
```
Application has a primary connection and a
replica connection pool.

def get_user(user_id):
    # Read: use replica connection
    return replica_db.query(
        "SELECT * FROM users WHERE id = ?", [user_id])

def update_user(user_id, data):
    # Write: ALWAYS use primary
    primary_db.execute(
        "UPDATE users SET ... WHERE id = ?", [user_id])

Load balancer in front of replicas:
  Application → DB Load Balancer → [Replica 1, 2, 3]
  Primary write: application direct to primary.
  
  Tools: ProxySQL (MySQL), PgBouncer + HAProxy
  (PostgreSQL), AWS RDS Proxy.
```

**FAILOVER:**
```
Primary server fails (hardware failure, network, crash).

Manual failover:
  DBA promotes a replica to primary manually.
  Update application config to point to new primary.
  Downtime: minutes to hours.
  
Automatic failover (high availability):
  Monitor: check primary health every N seconds.
  On failure detected: elect new primary (highest
  replication position = least lag).
  Update service discovery / DNS to new primary.
  Other replicas reconfigure to follow new primary.
  Downtime: seconds to < 1 minute.
  
  Tools: Patroni + etcd (PostgreSQL),
         MHA (MySQL), AWS RDS Multi-AZ.
  
Split-brain risk:
  Two nodes both think they are the primary.
  Both accept writes → data diverges.
  Prevented by: quorum-based leader election
  (need majority of nodes to agree on new primary).
```

---

### 🧪 Thought Experiment

**REPLICATION LAG IMPACT**

User: posts a comment (write to primary).
Page: refreshed immediately after posting.
App: reads comments from replica.

Timeline:
  T=0: comment written to primary.
  T=0: user refreshes page. Query → replica.
  T=100ms: replica receives and applies the write.
  
At T=0, the replica doesn't have the new comment.
User sees their own comment missing.
(Read-your-own-writes consistency violation)

Solutions:
1. Read-your-own-writes: after a write, route subsequent
   reads for that user to the primary for 1-2 seconds.
2. Write to primary, then read from primary for same
   request (sticky session for post-write reads).
3. Return the new comment from the write response
   (optimistic update). Display it locally without
   re-fetching from the replica.

This is a real, common bug in apps with read replicas.
Design for it explicitly.

---

### 🧠 Mental Model / Analogy

> Database replication is like a news bureau with one
> editor and multiple reporters:
>
> The editor (primary) approves and publishes all stories.
> Reporters (replicas) copy the newspaper and distribute
> it to readers. Readers can get the newspaper from any
> reporter (reads). Only the editor publishes new stories
> (writes). If the editor is hit by a bus: the senior
> reporter becomes editor (failover). The reporter's
> copy of the newspaper is slightly old (replication lag)
> - it may not have the story published 5 minutes ago.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Database replication makes copies of your database on
multiple servers. If one server fails, another takes over.
Read queries can go to any copy, spreading the load.
The copies may be a tiny bit out of date.

**Level 2 - How to use it (junior developer):**
Use an ORM that supports separate read/write connections.
Configure a primary (writes) and replica pool (reads).
Be aware of replication lag: don't read from replica
immediately after writing critical data.

**Level 3 - How it works (mid-level engineer):**
Primary writes to WAL/binlog. Replicas stream WAL and
replay changes. Replication lag: difference between
primary LSN and replica LSN. Read-your-own-writes:
route user's reads to primary after a write.
Failover: monitor primary, promote replica with lowest
lag. Tools: Patroni (PostgreSQL), AWS RDS Multi-AZ.

**Level 4 - Why it was designed this way (senior/staff):**
Asynchronous replication (default) maximizes write
throughput: the primary does not wait for replicas.
The accepted risk: if the primary fails before the WAL
is sent to replicas, the last few milliseconds of writes
are lost. For most applications, this is acceptable
(a few lost user actions in milliseconds). For financial
systems (bank transfers), synchronous replication to
at least one replica eliminates this risk at the cost
of slightly higher write latency (the write round-trip
includes one network hop to the replica). The choice
is explicit: throughput vs. durability.

**Level 5 - Mastery (distinguished engineer):**
LinkedIn's horizontal scaling of MySQL (2011) was one
of the first large-scale deployments of active-active
multi-leader replication: each shard had two primaries
accepting writes. This eliminated the bottleneck of a
single primary for writes, but introduced conflict
resolution complexity (two simultaneous writes to the
same row). Most systems avoid this complexity by using
single-primary replication and scaling writes through
sharding instead. PostgreSQL's streaming replication
is particularly elegant: it ships exact WAL bytes to
replicas, making replicas bit-for-bit identical to the
primary (physical replication). This is more efficient
than logical replication (shipping SQL statements) but
requires replicas to be on the same PostgreSQL version
and OS architecture.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ PRIMARY-REPLICA REPLICATION                         │
│                                                      │
│ Writes:                                             │
│  Application → Primary DB                         │
│                │ WAL entry                         │
│                ▼                                   │
│           [WAL Stream]                             │
│              │    │    │                           │
│              ▼    ▼    ▼                           │
│         [R1]  [R2]  [R3]  (async, ~1-100ms lag)   │
│                                                      │
│ Reads:                                              │
│  Application → DB Proxy (ProxySQL/PgBouncer)       │
│                → [R1], [R2], [R3] (round-robin)   │
│                                                      │
│ Failover:                                           │
│  Primary health check fails (no heartbeat 30s)     │
│  Patroni/HAProxy detects: primary down            │
│  Elect new primary: replica with highest LSN      │
│  Reconfigure: other replicas follow new primary   │
│  Update DNS: point to new primary                 │
│  Downtime: ~30-60 seconds                         │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Read/write routing in Python**
```python
import psycopg2
from psycopg2 import pool

# Primary: all writes
primary_pool = pool.ThreadedConnectionPool(
    minconn=5, maxconn=50,
    host="primary.db.internal",
    database="myapp", user="app", password="..."
)

# Replica pool: all reads
replica_pool = pool.ThreadedConnectionPool(
    minconn=5, maxconn=100,
    host="replica.db.internal",  # or load balancer
    database="myapp", user="app_readonly", password="..."
)

def get_user(user_id: int) -> dict:
    """Read: use replica (fast, no write pressure on primary)"""
    conn = replica_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, email FROM users "
                "WHERE id = %s",
                (user_id,))
            row = cur.fetchone()
            return {"id": row[0], "name": row[1],
                    "email": row[2]} if row else None
    finally:
        replica_pool.putconn(conn)

def update_user_email(user_id: int, email: str):
    """Write: ALWAYS use primary"""
    conn = primary_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET email = %s "
                "WHERE id = %s",
                (email, user_id))
        conn.commit()
    finally:
        primary_pool.putconn(conn)

# BAD: reading from replica immediately after writing
def update_and_read_bad(user_id: int, email: str) -> dict:
    update_user_email(user_id, email)
    # Read from replica: may still have OLD email
    # due to replication lag (race condition)
    return get_user(user_id)  # Returns stale data!

# GOOD: read-your-own-writes - use primary for post-write read
def update_and_read_good(user_id: int, email: str) -> dict:
    update_user_email(user_id, email)
    # Read from primary to guarantee fresh data
    conn = primary_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, email FROM users "
                "WHERE id = %s", (user_id,))
            row = cur.fetchone()
            return {"id": row[0], "name": row[1],
                    "email": row[2]}
    finally:
        primary_pool.putconn(conn)
```

---

### ⚖️ Comparison Table

| Aspect | No Replication | Async Replication | Sync Replication |
|---|---|---|---|
| **Write throughput** | Baseline | Same as baseline | Slower (waits for replica ACK) |
| **Read scalability** | One server only | N replicas share reads | N replicas share reads |
| **Data loss on failure** | Database crash = data loss | Milliseconds of writes may be lost | Zero data loss |
| **Availability** | Single point of failure | Automatic failover (~30s downtime) | HA, but write blocked if replica unreachable |
| **Complexity** | Low | Medium | High |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Replicas handle both reads and writes | In single-leader replication (the most common), replicas are read-only. All writes must go to the primary. Sending writes to a replica causes errors or (in some configurations) silent data divergence. The connection pool must explicitly route writes to primary and reads to replicas. |
| Replication guarantees data durability | Asynchronous replication does not. If the primary fails before the WAL is sent to the replica, those writes are lost. For durability, use synchronous replication to at least one replica, or use RAID on the primary, or use cloud storage (like AWS EBS Multi-AZ) that guarantees durability independently. |
| Adding more replicas always helps | Beyond a certain point, the primary becomes the bottleneck for sending WAL to replicas. Each replica receives the full WAL stream. With 10 replicas, the primary must send the same data 10 times. Network bandwidth on the primary may become the limiting factor. In practice, 3-5 replicas is typical. For more, use hierarchical replication: a relay server receives WAL from primary and distributes to many replicas. |

---

### 🚨 Failure Modes & Diagnosis

**Replication Lag Spike Causing Stale Reads**

**Symptom:**
Users report seeing old data on the page immediately
after updating it. Support tickets: "I updated my
profile but it still shows the old name."
Monitoring shows replica lag > 5 seconds.

**Root Cause:**
Primary is under heavy write load (bulk import, nightly
job). Replicas cannot keep up. Replication lag grows.
Reads from replicas return data that is 5+ seconds stale.

**Diagnosis:**
```sql
-- PostgreSQL: check replication lag
SELECT client_addr,
       state,
       sent_lsn,
       write_lsn,
       flush_lsn,
       replay_lsn,
       -- Lag in bytes:
       (sent_lsn - replay_lsn)::text AS lag_bytes,
       -- Lag in seconds (if pg_stat_replication):
       extract(epoch from (now() - replay_lag))
           AS lag_seconds
FROM pg_stat_replication;

-- Alert if lag > 5 seconds:
-- Increase max_wal_senders if replication is constrained.
-- Reduce bulk write load during business hours.
-- Add replica with more I/O capacity.
```

**Fix:**
```python
# Application fix: check replica lag before routing
def get_lag_seconds(replica_pool) -> float:
    conn = replica_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT extract(epoch from "
                "  (now() - pg_last_xact_replay_timestamp()))"
            )
            lag = cur.fetchone()[0] or 0
            return float(lag)
    finally:
        replica_pool.putconn(conn)

def get_user_smart(user_id: int) -> dict:
    lag = get_lag_seconds(replica_pool)
    if lag > 2.0:
        # Replica is too stale: use primary
        return get_from_primary(user_id)
    return get_from_replica(user_id)
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- (none - this is a foundational concept entry)

**Builds On This (learn these next):**
- `Database Replication (System)` - detailed strategies:
  single-leader, multi-leader, leaderless; synchronous
  vs. asynchronous; failover mechanics
- `Data Partitioning Strategies` - when replication is
  not enough (writes bottleneck): shard the database
- `What is Scalability` - replication is one tool in
  the broader scalability toolkit

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ CORE IDEA   │ Primary: all writes. Replicas: all reads. │
│             │ WAL streams changes to replicas.         │
├─────────────┼──────────────────────────────────────────┤
  │
│ REPL LAG    │ Typically milliseconds. Can spike to sec. │
│             │ Reads from replica may return stale data. │
├─────────────┼──────────────────────────────────────────┤
  │
│ ASYNC (def) │ Fast writes. Risk: last ms of data lost  │
│             │ if primary fails before replica syncs.   │
├─────────────┼──────────────────────────────────────────┤
  │
│ SYNC        │ Zero data loss. Slower writes (waits for │
│             │ replica ACK). Blocked if replica down.   │
├─────────────┼──────────────────────────────────────────┤
  │
│ FAILOVER    │ Replica with lowest lag → new primary.   │
│             │ Patroni/MHA automates in ~30-60 seconds. │
├─────────────┼──────────────────────────────────────────┤
  │
│ GOTCHA      │ Read-your-own-writes: read from primary  │
│             │ right after writing. Not from replica.   │
├─────────────┼──────────────────────────────────────────┤
  │
│ ONE-LINER   │ "Primary=writes. Replicas=reads.        │
│             │  Watch for lag on post-write reads."    │
├─────────────┼──────────────────────────────────────────┤
  │
│ NEXT        │ CDN Architecture Pattern                  │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. All writes go to the primary. Reads go to replicas.
   This gives you read scalability (add replicas = add
   read capacity) but does NOT scale writes. Scale writes
   requires sharding.
2. Replication lag means replicas may return stale data.
   For "read-your-own-writes" consistency, route reads
   to the primary for the request immediately after a
   write. Do not read your own write from a replica.
3. Asynchronous replication (default): fast writes, risk
   of losing last few milliseconds of writes on primary
   failure. Synchronous: zero data loss, higher write
   latency, blocked if replica is unreachable.

**Interview one-liner:**
"Database replication: primary accepts all writes, replicas serve reads. WAL/binlog
streams changes asynchronously (default: faster writes, risk of losing last ms on
primary failure) or synchronously (zero data loss, slower writes). Read scalability:
add replicas, route reads to them via DB proxy (ProxySQL, PgBouncer). Replication
lag: replicas may be milliseconds to seconds behind. Read-your-own-writes bug: do
not read from replica immediately after writing - use primary for post-write reads.
Failover: Patroni promotes replica with lowest lag to primary (~30-60s downtime)."
