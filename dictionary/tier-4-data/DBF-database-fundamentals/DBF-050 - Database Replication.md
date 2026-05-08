---
layout: default
title: "Database Replication"
parent: "Database Fundamentals"
grand_parent: "Technical Dictionary"
nav_order: 50
permalink: /databases/database-replication/
id: DBF-050
category: Database Fundamentals
difficulty: ★★★
depends_on: WAL, Transaction, ACID
used_by: Read Replica, Master-Slave Replication, Multi-Master Replication
related: Read Replica, WAL, Distributed Systems
tags:
  - database
  - replication
  - distributed-systems
  - deep-dive
---

# DBF-050 - Database Replication

⚡ TL;DR - Database replication copies data from a primary to one or more replicas using WAL/binlog streaming - enabling high availability (failover), read scaling (replicas handle reads), and geographic distribution - at the cost of replication lag and consistency trade-offs.

| #445            | Category: Database Fundamentals                                  | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------- | :-------------- |
| **Depends on:** | WAL, Transaction, ACID                                           |                 |
| **Used by:**    | Read Replica, Master-Slave Replication, Multi-Master Replication |                 |
| **Related:**    | Read Replica, WAL, Distributed Systems                           |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A single database server. The server fails at 2am. The application is down until the server is recovered, backup restored, and services restarted - potentially hours of downtime. Also: all reads and writes go to one server - under load, the single node becomes the bottleneck.

**THE BREAKING POINT:**
Business requirement: 99.9% availability (8.7 hours downtime/year). A single database server fails once every two years → 8 hours recovery → already breaks SLA. Single point of failure for the most critical component: the data store.

**THE INVENTION MOMENT:**
"Maintain a live copy of the database on another server. If the primary fails, promote the copy to primary and redirect traffic. Recovery time: seconds, not hours."

---

### 📘 Textbook Definition

**Database replication** is the process of continuously copying data changes from one database instance (the **primary** or **master**) to one or more other instances (the **replicas**, **standbys**, or **secondaries**) to maintain synchronized copies. Replication serves three purposes: (1) **High Availability** - if the primary fails, a replica is promoted (failover); (2) **Read Scaling** - read queries directed to replicas, offloading the primary; (3) **Disaster Recovery / Geographic Distribution** - replicas in other data centers or regions. Replication strategies include: **synchronous** (primary waits for replica acknowledgment before committing - zero data loss, higher write latency), **asynchronous** (primary commits without waiting for replica - lower write latency, risk of losing committed data on failover), and **semi-synchronous** (wait for at least one replica).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Replication keeps live copies of the database in sync - for failover, read scaling, and geographic distribution - with a trade-off between data loss risk and write latency.

**One analogy:**

> A primary musician (write database) performs live. Sound engineers (replicas) record every note in real time for broadcast. If the musician collapses (primary fails), the broadcast doesn't stop - a recording is immediately played (replica promoted). The recordings are slightly behind the live performance (replication lag) but essentially the same show.

- "Live performance" → primary database (authoritative)
- "Recording for broadcast" → replication streaming (WAL/binlog)
- "Slight delay" → replication lag
- "Musician collapses" → primary failure
- "Play the recording" → replica promotion (failover)

**One insight:**
Replication lag is always a reality with async replication - you cannot have zero lag AND zero impact on write throughput. The durability vs. performance trade-off: synchronous replication (no data loss on failover) adds network round-trip latency to every write commit. For a cross-region primary with synchronous replication: every write takes 100ms+ (cross-region RTT). Choose the right replication mode based on data loss tolerance.

---

### 🔩 First Principles Explanation

**REPLICATION MODES:**

```
SYNCHRONOUS REPLICATION:
Primary writes WAL → sends to replica → waits for replica ACK
→ Only after ACK: primary commits and returns to client
Guarantee: replica has data when client receives "committed"
Cost: every write adds replica RTT to commit latency

ASYNCHRONOUS REPLICATION:
Primary writes WAL → commits immediately → sends to replica async
→ Client receives "committed" without waiting for replica
Guarantee: none - if primary fails before replica applies: data lost
Cost: none (no added latency)

SEMI-SYNCHRONOUS (MySQL default sync option):
Primary waits for at least ONE replica to acknowledge
→ Guarantees data on at least one other node
→ Compromise: some write latency; no single-node data loss
```

**POSTGRESQL STREAMING REPLICATION:**

```
# Primary: postgresql.conf
wal_level = replica
max_wal_senders = 10
synchronous_commit = on   # sync replication to named standby
# OR
synchronous_commit = off  # async (default) for performance
synchronous_standby_names = 'replica1'  # require ACK from replica1

# Replica: recovery.conf / postgresql.conf (v12+)
primary_conninfo = 'host=primary-db port=5432 user=replication'
hot_standby = on    # allow read-only queries on replica

# Check replication status (on primary):
SELECT application_name, state, sent_lsn, write_lsn,
       flush_lsn, replay_lsn, replay_lag
FROM pg_stat_replication;
```

**WAL SHIPPING VS. STREAMING:**

- **WAL Shipping:** Completed WAL segment files are periodically copied to replica (5 min lag typical). Simpler; less real-time.
- **Streaming Replication:** WAL records streamed continuously as they are written. Near-real-time lag (milliseconds). Standard for production.

**LOGICAL vs. PHYSICAL REPLICATION:**
| | Physical Replication | Logical Replication |
|---|---|---|
| Replicates | Binary page-level changes | Logical row changes (INSERT/UPDATE/DELETE) |
| Replica version | Must match major version | Can differ |
| Selective replication | No (entire instance) | Yes (per table, per schema) |
| Use case | Hot standby, read replicas | Cross-version migration, selective sync |

**REPLICATION TOPOLOGY:**

- **Single primary + N replicas:** Most common. Writes to primary; reads optionally to replicas.
- **Cascading replication:** Primary → replica1 → replica2 (replica2 receives from replica1, reducing primary WAL sender load).
- **Multi-primary (multi-master):** Multiple primaries, each accepting writes. Complex - conflict resolution required.

---

### 🧪 Thought Experiment

**FAILOVER SCENARIO:**

Primary database crashes at 2:00:00 AM.
Async replication: replica was 500ms behind (replication lag).

**WITHOUT AUTOMATED FAILOVER:**

- On-call engineer paged: 5 minutes to wake up.
- Assess: 10 minutes.
- Promote replica: 2 minutes.
- Update DNS/connection strings: 5 minutes.
- Total downtime: ~22 minutes.

**WITH AUTOMATED FAILOVER (Patroni / AWS Multi-AZ):**

- Health check detects primary failure: 30 seconds.
- Automatic replica promotion: 15 seconds.
- DNS/VIP updated: 5 seconds.
- Application reconnects: 5 seconds.
- Total downtime: ~55 seconds.

**DATA LOSS QUESTION:**

- Async replica was 500ms behind → transactions committed to primary in the last 500ms are LOST.
- Sync replication: zero data loss (primary couldn't commit without replica ACK).
- Business decision: 500ms of order data loss acceptable? → Use async. Not acceptable? → Use sync.

---

### 🧠 Mental Model / Analogy

> Replication is like a live satellite TV broadcast with a redundant signal. The studio (primary) broadcasts live. Satellite relay stations (replicas) capture and retransmit the signal. If the studio's main transmitter fails, the relay station's stored signal keeps the broadcast going (failover). The slight delay in the relay (replication lag) means the relay is always a fraction of a second behind the live studio. Synchronous: the studio can't say "we're on air" until the relay confirms it received the signal. Asynchronous: the studio broadcasts immediately; if the transmitter fails in that fraction of a second, that moment is lost from the relay.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Replication makes copies of your database on other servers. If the main one crashes, a copy takes over instantly. It also means multiple servers can handle read queries, improving performance.

**Level 2:** Configure `hot_standby = on` on the replica to serve SELECTs. Monitor `replay_lag` in `pg_stat_replication`. Use Patroni for automatic failover. Choose async (no write latency impact) for read replicas, sync for financial systems that can't lose data.

**Level 3:** PostgreSQL WAL streaming: the primary's WAL sender process streams WAL records to the replica's WAL receiver, which writes to local WAL and signals the startup process to apply. LSN (Log Sequence Number) tracks position. `sent_lsn - replay_lsn = lag bytes`. Replication slots ensure the primary retains WAL until the replica has consumed it - prevents the replica from falling too far behind. Risk: a paused replica with a replication slot causes WAL accumulation on primary, potentially filling disk.

**Level 4:** The trade-off between durability and latency is captured by the **RPO** (Recovery Point Objective - how much data can be lost) vs. **latency SLA**. Synchronous replication achieves RPO=0 at the cost of write latency = RTT to replica. Async achieves minimum write latency at the cost of RPO = replication lag. The CAP theorem frames this: replication lag = the "A" (availability for writes) vs. "C" (consistency of all copies) trade-off under a network partition. Modern databases (CockroachDB, Google Spanner) use Raft/Paxos consensus to guarantee zero data loss without sacrificing availability - but at the cost of geographic write latency (Paxos round-trip between data centers). Replication is one dimension of a larger HA architecture: replication + connection pooling + automated failover + load balancing = complete HA stack.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ ASYNC STREAMING REPLICATION: DATA FLOW               │
├──────────────────────────────────────────────────────┤
│                                                      │
│ PRIMARY                      REPLICA                 │
│ ────────                     ───────                 │
│ Client writes → WAL record   WAL Receiver            │
│ Append to WAL buffer         ← WAL Record (TCP)      │
│ Commit transaction           Write to local WAL      │
│ (no wait for replica)        Startup process applies │
│                              Updates data files      │
│                              Serves SELECT queries   │
│                                                      │
│ pg_stat_replication:                                 │
│  sent_lsn: how far WAL sent to replica               │
│  replay_lsn: how far replica has applied             │
│  replay_lag: time delta between commit and apply     │
│  → lag = replay_lag (target: < 1s for LAN replica)   │
│                                                      │
│ Replication slot:                                    │
│  Primary retains WAL until replica's replay_lsn      │
│  Prevents replica from falling too far behind        │
│  Risk: slot + paused replica → disk fill on primary  │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**FAILOVER FLOW (Patroni):**

```
Primary health check fails (3 consecutive)
→ Patroni/etcd quorum detects primary unavailability
→ [REPLICATION ← YOU ARE HERE: replica has recent data]
→ Replica promoted: pg_promote() called
→ Replica now accepts writes
→ Patroni updates etcd/ZooKeeper with new primary address
→ HAProxy/PgBouncer health check detects new primary
→ Application connections rerouted to new primary
→ Old primary (if recovered) becomes replica of new primary
Total: ~30–60 seconds
```

**WHAT CHANGES AT SCALE:**
Multiple primaries (Multi-Master): each accepts writes; conflict resolution needed (last-write-wins, CRDT, or application logic). Used in: CockroachDB, Cassandra, Galera Cluster (MySQL), Amazon Aurora Global. Geographic distribution: primary in US-East, replica in EU-West, Asia-Pacific - reads served locally (10ms vs. 100ms cross-continent). Writes still go to primary (or nearest in multi-master). AWS RDS Multi-AZ: synchronous replication within the same region - automatic failover, zero data loss on AZ failure. RDS Read Replicas: async, for read scaling.

---

### ⚖️ Comparison Table

| Mode                   | Write Latency   | Data Loss Risk              | Use Case                 |
| ---------------------- | --------------- | --------------------------- | ------------------------ |
| **Async**              | None added      | RPO = lag                   | Read replicas, analytics |
| **Sync (one replica)** | +RTT to replica | Zero (if replica available) | Financial, critical data |
| **Sync quorum**        | +RTT to quorum  | Zero (quorum available)     | Distributed consensus    |
| **Semi-sync (MySQL)**  | +RTT to one     | Zero for that commit        | Balance of perf + safety |

---

### ⚠️ Common Misconceptions

| Misconception                             | Reality                                                                                                                                                                           |
| ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Replication = backup                      | Replication gives you a live copy that applies changes in real time - including accidental DELETEs. A backup is a point-in-time snapshot; replication is not a backup replacement |
| Sync replication prevents all data loss   | Only prevents data loss from primary hardware failure after commit; a bug that DELETEs rows will replicate the DELETE to all replicas simultaneously                              |
| Replication lag doesn't matter for writes | Replication lag matters for reads (stale data) but NOT for writes (which go to primary) - unless you're using sync replication, where lag IS write latency                        |
| Failover is instantaneous                 | Even with Patroni/automated failover: 30–60 seconds minimum for detection, promotion, and connection rerouting                                                                    |

---

### 🚨 Failure Modes & Diagnosis

**1. Replication Slot Disk Fill**

**Symptom:** Primary disk filling unexpectedly; `pg_replication_slots` shows a slot with increasing `lag_bytes`; application may become read-only or crash.

**Root Cause:** A replication slot created for a replica that is paused or disconnected - the primary retains all WAL since the slot's `restart_lsn`, accumulating indefinitely.

**Diagnostic:**

```sql
-- Check replication slots and lag
SELECT slot_name, active, restart_lsn, confirmed_flush_lsn,
       pg_current_wal_lsn() - restart_lsn AS lag_bytes
FROM pg_replication_slots;
-- If lag_bytes >> expected: slot is stale; active=false: replica disconnected
```

**Fix (immediate):** If the replica is permanently gone: `SELECT pg_drop_replication_slot('slot_name')` - WAL can now be cleaned. If replica will return: increase disk, reconnect replica ASAP.

**Prevention:** Set `max_slot_wal_keep_size` (PostgreSQL 13+) to cap WAL retention per slot. Alert on `pg_replication_slots.lag_bytes > 10GB`. Monitor all replication slots and alert on `active = false`.

---

**2. Replica Falling Behind During Write Spike**

**Symptom:** `replay_lag` growing from milliseconds to minutes during peak write traffic; application reads from replica showing increasingly stale data.

**Root Cause:** Replica's apply rate (disk I/O, CPU) can't match primary's write rate.

**Diagnostic:**

```sql
-- Track lag trend over time
SELECT NOW(), application_name, write_lag, flush_lag, replay_lag
FROM pg_stat_replication;
-- If replay_lag increasing monotonically: replica is falling behind
```

**Fix (immediate):** Redirect reads to primary (or another non-lagging replica). Upgrade replica disk I/O (NVMe). Add more replicas to distribute read load. **Fix (long-term):** Reduce primary write rate (better write patterns, batching). Use parallel WAL apply (`max_logical_replication_workers`).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `WAL (Write-Ahead Log)` - replication streams WAL records from primary to replica
- `Transaction` - replication applies changes at transaction granularity
- `ACID` - replication preserves ACID properties on the replica

**Builds On This (learn these next):**

- `Read Replica` - read replicas are the read-scaling use case of replication
- `Master-Slave Replication` - specific topology terminology and patterns
- `Multi-Master Replication` - write-scale topologies with conflict resolution

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PURPOSES     │ High Availability, Read Scaling, DR/Geo   │
├──────────────┼───────────────────────────────────────────┤
│ ASYNC        │ No write latency impact; RPO = lag        │
│ SYNC         │ Zero data loss; adds RTT per write        │
├──────────────┼───────────────────────────────────────────┤
│ MONITOR      │ pg_stat_replication.replay_lag            │
│              │ pg_replication_slots.lag_bytes             │
│              │ Alert: slot inactive; lag growing          │
├──────────────┼───────────────────────────────────────────┤
│ FAILOVER     │ Patroni (PostgreSQL), MHA (MySQL)         │
│              │ AWS Multi-AZ: automatic, same region       │
├──────────────┼───────────────────────────────────────────┤
│ NOT A BACKUP │ Replication ≠ backup - DELETEs replicate  │
│              │ Always maintain separate point-in-time BK │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Live copy for failover and reads -       │
│              │  async is fast but lossy on crash"        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Read Replica → Master-Slave → Multi-Master│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C - Design Question) Design the replication architecture for a global fintech payment system that requires: (a) zero data loss for payment transactions, (b) < 50ms write latency for US-based payments, (c) local read latency < 10ms for EU and APAC users. What replication modes, topologies, and database technologies would you use? What consistency guarantees does each region's users experience?

**Q2.** (TYPE D - Failure Scenario) At 3am, the primary PostgreSQL database's SSD fails suddenly. The async replica has a `replay_lag` of 2 seconds at time of failure. The team promotes the replica to primary. Describe: (a) what data is lost; (b) what the application sees during the failover window; (c) what happens to in-flight transactions that were committed on the primary but not yet applied to the replica; (d) how would synchronous replication have changed this scenario?
