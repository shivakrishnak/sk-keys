---
layout: default
title: "Master-Slave Replication"
parent: "Database Fundamentals"
nav_order: 46
permalink: /databases/master-slave-replication/
number: "DBF-046"
category: Database Fundamentals
difficulty: ★★☆
depends_on: Database Replication, WAL, Read Replica
used_by: Multi-Master Replication, Database Sharding, High Availability
related: Database Replication, Read Replica, Multi-Master Replication
tags:
  - database
  - replication
  - high-availability
  - intermediate
---

# DBF-046 — Master-Slave Replication

⚡ TL;DR — Master-slave (primary-replica) replication is the most common DB HA topology: one primary accepts all writes, one or more replicas receive changes and serve reads — simple, proven, but the single write node is the scaling ceiling.

| #446            | Category: Database Fundamentals                                | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------- | :-------------- |
| **Depends on:** | Database Replication, WAL, Read Replica                        |                 |
| **Used by:**    | Multi-Master Replication, Database Sharding, High Availability |                 |
| **Related:**    | Database Replication, Read Replica, Multi-Master Replication   |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT REPLICATION TOPOLOGY:**
Multiple servers with identical copies of the database, all accepting writes — but no coordination. Server A updates a record; Server B updates the same record simultaneously. Who wins? How does Server A learn about Server B's change? Without a defined topology, you have conflicting writes with no resolution strategy.

**MASTER-SLAVE SOLUTION:**
Define a single authority for writes (master/primary). All writes go there. The master propagates changes to replicas (slaves). No conflicts — there is only one source of truth. Replicas are read-only copies.

**THE REMAINING PROBLEM:**
The master is a single point of write bottleneck. Vertical scaling has limits. And if the master fails, no writes can happen until a slave is promoted.

---

### 📘 Textbook Definition

**Master-slave replication** (also called **primary-replica** or **leader-follower** replication) is a replication topology with exactly **one writable node** (the master/primary/leader) and **one or more read-only nodes** (slaves/replicas/followers). All writes go to the master; the master replicates changes to slaves via WAL streaming (PostgreSQL), binary log (MySQL/binlog), or logical replication. Slaves serve read queries from their continuously updated copy of the data. On master failure, one slave is **promoted** to master (either manually or via automated failover tools like **Patroni** for PostgreSQL, **MHA** for MySQL, or **AWS RDS Multi-AZ** for cloud deployments). This topology is the foundation of most production database HA setups.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
One master writes, multiple slaves read — clear authority, simple consistency, write scale limited to one node.

**One analogy:**

> A newsroom: one editor-in-chief (master) approves and publishes all articles. Junior editors (slaves) have copies of the newspaper — they can answer questions about published articles (read queries) but cannot publish new ones without the editor-in-chief. If the editor-in-chief is unavailable, a deputy editor (slave promotion) takes over.

- "Editor-in-chief" → master database (single write authority)
- "Published articles" → committed data
- "Junior editors with copies" → slave replicas (read-only)
- "Deputy takes over" → slave promotion to master (failover)
- "Newsroom hierarchy" → defined replication topology (no conflicting write authorities)

**One insight:**
The terminology "master/slave" is increasingly replaced by "primary/replica" or "leader/follower" in modern documentation (including PostgreSQL, Kubernetes, and most cloud providers). The concept is identical — the vocabulary shift reflects industry sensitivity to the connotations of the original terms.

---

### 🔩 First Principles Explanation

**TYPICAL TOPOLOGY:**

```
┌─────────────┐          ┌─────────────┐
│   PRIMARY   │ ─WAL──→  │  REPLICA 1  │ (read queries)
│  (Writes)   │ ─WAL──→  │  REPLICA 2  │ (read queries)
│             │          │  REPLICA 3  │ (standby for failover)
└─────────────┘          └─────────────┘
       ↑
All application writes
```

**CASCADING REPLICATION:**

```
PRIMARY → REPLICA 1 → REPLICA 2 → REPLICA 3
(Reduces WAL sender load on primary; REPLICA 1 fans out to others)
```

**MYSQL BINLOG REPLICATION:**

```sql
-- Primary (MySQL): configure binary logging
[mysqld]
server-id = 1
log_bin = /var/log/mysql/mysql-bin.log
binlog_format = ROW  -- recommended: row-level changes (most consistent)
binlog_row_image = FULL  -- log complete row image (before + after)

-- Replica:
server-id = 2
[connect to primary and start replication]
CHANGE MASTER TO
    MASTER_HOST='primary-host',
    MASTER_USER='replication_user',
    MASTER_PASSWORD='secret',
    MASTER_LOG_FILE='mysql-bin.000001',
    MASTER_LOG_POS=4;
START SLAVE;
SHOW SLAVE STATUS\G;  -- check Seconds_Behind_Master, Slave_IO_Running, Slave_SQL_Running
```

**GTID REPLICATION (MySQL/PostgreSQL: recommended):**

```sql
-- GTID (Global Transaction ID): identifies each transaction globally
-- Simplifies failover: new primary tells replicas "continue from GTID X"
-- No need to manually track binlog file + position

-- MySQL:
[mysqld]
gtid_mode = ON
enforce_gtid_consistency = ON
```

**FAILOVER PROCESS:**

```
Primary fails
→ Automated detection (Patroni heartbeat, MHA, AWS health check)
→ Select promotion candidate:
   - Replica with most recent data (highest LSN/GTID)
   - Prefer sync replica (if configured)
→ Promote selected replica:
   PostgreSQL: pg_promote()
   MySQL: STOP SLAVE; RESET MASTER;
→ Update connection routing:
   DNS TTL, HAProxy, PgBouncer, VIP failover
→ Other replicas point to new primary:
   CHANGE REPLICATION SOURCE TO new_primary (MySQL 8+)
   primary_conninfo = 'host=new_primary' (PostgreSQL)
→ Old primary recovered:
   Rejoin as replica (PITR recovery to sync point + replicate forward)
```

**THE TRADE-OFFS:**
**Gain:** Simple topology — no conflicts possible; clear write authority; read scaling via replicas; proven and well-understood failure modes.
**Cost:** Single write bottleneck — write throughput is limited to one server's capacity; write scaling requires sharding or multi-master (both more complex). Failover lag — even automated failover takes 30–60 seconds, causing brief write unavailability.

---

### 🧪 Thought Experiment

**FAILOVER RACE CONDITION (Split-Brain):**
Primary is failing (network issue, not crashed). Two scenarios:

**SCENARIO A — Correct Failover:**

- Primary is genuinely unreachable by all replicas AND all application nodes.
- Failover quorum (Patroni + etcd): 2 of 3 Patroni agents agree primary is dead.
- One replica promoted. Old primary (if it recovers): sees new primary, becomes replica.
- No split-brain: consensus protocol ensures only one primary.

**SCENARIO B — Split-Brain:**

- Network partition: primary can reach some app servers but not Patroni agents.
- Patroni promotes a replica (thinks primary is dead).
- Two primaries: old primary accepting writes from app servers that can still reach it.
- New primary accepting writes from reconnected app servers.
- CONFLICT: both primaries have committed different data.
- Resolution: complex — requires manual reconciliation; one primary's writes discarded.

**PREVENTION:**

- Use consensus protocol (etcd, ZooKeeper) for leader election — requires quorum (majority) to promote.
- "Stonith" (Shoot The Other Node In The Head): primary must be fenced (powered off, disk detached) before replica promotion in quorum-based systems.
- AWS Multi-AZ: AWS infrastructure guarantees single primary; split-brain eliminated by cloud-managed fencing.

---

### 🧠 Mental Model / Analogy

> Master-slave replication is like a master chef with line cooks. The master chef (primary) creates new dishes (writes data). Line cooks (replicas) watch and learn — they have an identical copy of every recipe (data) the master chef has made. Customers can ask line cooks for recipe information (read queries) without bothering the master chef. If the master chef calls in sick (primary failure), the most senior line cook (best replica) becomes the acting head chef (promoted to primary).

- "Master chef creates dishes" → primary accepts writes
- "Line cooks watching and copying" → replicas receiving WAL/binlog
- "Customers asking line cooks" → reads from replicas
- "Master chef sick" → primary failure
- "Senior line cook promoted" → replica promotion/failover
- "Only one head chef at a time" → single-primary guarantee (no split-brain)

---

### 📶 Gradual Depth — Four Levels

**Level 1:** One database accepts all changes (master). Other copies (slaves) automatically stay up-to-date and can answer read questions. If the master fails, the best-updated slave becomes the new master.

**Level 2:** Use a connection pooler (PgBouncer) or HAProxy with a VIP to route writes to primary and reads to replicas. Automate failover with Patroni (PostgreSQL) or ProxySQL (MySQL) + MHA. Monitor `replay_lag` — alert if lag > 30s. Test failover regularly in staging.

**Level 3:** PostgreSQL Patroni: uses DCS (Distributed Configuration Store — etcd, ZooKeeper, Consul) for leader election. Primary acquires a leader lock in etcd (TTL-based). Patroni agents on each node monitor: if primary's lock expires, a replica can acquire the lock and promote. Each Patroni agent also maintains HAProxy config — when the primary changes, HAProxy's backend config updates automatically. Patroni supports "synchronous standby" designation: the configured sync standby must acknowledge every write for the primary to commit — zero data loss on planned or unplanned failover.

**Level 4:** The "master-slave" topology is a specific application of Raft's "single leader" principle: one node is the authority for all writes; all others are followers. Unlike Raft (which uses consensus for every write), traditional master-slave allows asynchronous replication where the master can commit without follower acknowledgment — trading consistency for performance. This is the foundational choice that determines RPO (recovery point objective). Distributed systems like CockroachDB and Google Spanner use consensus-based replication (Raft/Paxos) to achieve zero RPO without sacrificing write availability — at the cost of geographic write latency (multi-region consensus round trips). Master-slave remains the dominant architecture for single-region OLTP databases because: (a) intra-datacenter RTT is < 1ms (sync replication is nearly free), (b) operational simplicity (well-understood failure modes), (c) PostgreSQL and MySQL ecosystems are optimized for it.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ MASTER-SLAVE: PATRONI HA TOPOLOGY                    │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │                  etcd cluster                │   │
│  │           (leader lock + config)             │   │
│  └────────────────────┬─────────────────────────┘   │
│                       │                             │
│  ┌────────────┐  Lock  │  ┌────────────┐            │
│  │  PRIMARY   │◄───────┘  │  REPLICA 1 │            │
│  │  Patroni   │           │  Patroni   │            │
│  │  Postgres  │──WAL──►   │  Postgres  │            │
│  └─────┬──────┘           └────────────┘            │
│        │                                            │
│  ┌─────┴──────────────────────────────────┐        │
│  │     HAProxy / PgBouncer                │        │
│  │  write: → Primary  read: → Replica(s)  │        │
│  └─────┬──────────────────────────────────┘        │
│        │                                            │
│  Application Servers                                │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
Application write → HAProxy → Primary database
Application read → HAProxy → Replica (read-only)
Primary commits → WAL stream → Replica applies
pg_stat_replication.replay_lag: < 100ms (target)
```

**FAILOVER FLOW:**

```
Primary fails (crash, hardware failure)
→ Patroni health checks fail (3× 10s = 30s detection)
→ [MASTER-SLAVE ← YOU ARE HERE: promotion topology]
→ etcd: primary's lock expires (no renewal)
→ Most up-to-date replica acquires lock
→ pg_promote() called on replica
→ Replica is now primary (accepts writes)
→ HAProxy config updated: write pool → new primary
→ Other replicas: primary_conninfo updated → follow new primary
→ Total: ~30-60 seconds
```

---

### ⚖️ Comparison Table

| Topology                     | Write Scale          | Consistency                   | Complexity | Use Case                     |
| ---------------------------- | -------------------- | ----------------------------- | ---------- | ---------------------------- |
| **Master-Slave (1 primary)** | Vertical only        | Strong (single source)        | Low        | Most OLTP applications       |
| **Master + Sync Slave**      | Vertical only        | Zero data loss                | Low-Medium | Financial, critical data     |
| **Cascading Replica**        | Vertical only        | Increasing lag downstream     | Low        | High-replica-count scenarios |
| **Multi-Master**             | Horizontal (limited) | Complex (conflict resolution) | High       | Geo-distributed writes       |
| **Sharding**                 | Horizontal (full)    | Per-shard strong              | Very High  | Extreme write scale          |

---

### ⚠️ Common Misconceptions

| Misconception                                           | Reality                                                                                                                                                                  |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Master-slave replication provides redundancy for writes | It provides failover (a replica CAN become a writer after promotion) but normal operation has only one writer; during failover, writes are unavailable for 30-60 seconds |
| Adding more slaves improves write throughput            | Slaves are read-only; more slaves = more read capacity, not write capacity. Write throughput is bounded by the single primary                                            |
| A slave can be promoted instantly with zero downtime    | Promotion takes 30-60 seconds with automated tools; during this window, writes fail. Zero-downtime write failover requires active-active architecture (multi-master)     |
| All slaves are always up-to-date                        | With async replication, slaves lag behind the primary; the lag can grow to minutes under heavy write load or network congestion                                          |

---

### 🚨 Failure Modes & Diagnosis

**1. Split-Brain: Two Nodes Accepting Writes Simultaneously**

**Symptom:** Application experiencing data inconsistency; conflicting records appear in the database; two database nodes both believe they are primary.

**Root Cause:** Failover happened while old primary was still reachable by some app servers; both nodes accepted writes simultaneously.

**Diagnostic:**

```
Check: which nodes does the application think are primary?
Check: etcd/ZooKeeper leader key — which node holds the leader lock?
Check: `pg_is_in_recovery()` on each node — false = primary
If two nodes return false: split-brain
```

**Fix (immediate):** Fence the old primary immediately (stop PostgreSQL or revoke network access). Choose one primary (the one that was correctly elected by consensus). Restore the other's data to its correct state from the elected primary. This is a manual, painful recovery.

**Prevention:** Use Patroni with etcd — split-brain prevention is built into the consensus protocol. Set `pause` mode for maintenance windows. Ensure `synchronous_standby_names` is set for critical systems (sync replica cannot be promoted unless in sync).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Database Replication` — the overarching mechanism
- `WAL (Write-Ahead Log)` — what is being replicated
- `Read Replica` — the read-scaling benefit of master-slave topology

**Builds On This (learn these next):**

- `Multi-Master Replication` — extending to multiple write nodes
- `Database Sharding` — horizontal write scaling beyond what one primary can handle
- `High Availability` (general patterns)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ TOPOLOGY     │ 1 primary (writes) + N replicas (reads)   │
├──────────────┼───────────────────────────────────────────┤
│ FAILOVER     │ Patroni (PostgreSQL) + etcd               │
│ TOOLS        │ MHA (MySQL), AWS Multi-AZ (cloud-managed) │
├──────────────┼───────────────────────────────────────────┤
│ FAILOVER     │ ~30-60s with automation                   │
│ TIME         │ Minutes without automation                │
├──────────────┼───────────────────────────────────────────┤
│ WRITE LIMIT  │ Bounded by single primary capacity        │
│              │ Vertical scale only; sharding for more    │
├──────────────┼───────────────────────────────────────────┤
│ SPLIT-BRAIN  │ Consensus (etcd) + fencing prevents it    │
│              │ Manual recovery if it occurs              │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "One writer, many readers, proven HA —    │
│              │  write scale ceiling is the trade-off"   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Multi-Master Replication → Sharding       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE D — Failure Scenario) A Patroni-managed PostgreSQL cluster has 1 primary + 2 async replicas. During a network maintenance window, the switch connecting the primary to the Patroni agents' network (but not to the application network) fails. The primary can still serve the application but Patroni agents can't reach it. What happens? Does Patroni promote a replica? Is there a risk of split-brain? How should the cluster be configured to handle this correctly?

**Q2.** (TYPE C — Design Question) You're choosing between: (a) single primary + 3 async replicas in one datacenter, (b) single primary + 1 sync replica + 2 async replicas in one datacenter, (c) primary in US-East + sync replica in US-East + async replica in EU-West. For each: describe the RPO (data loss on primary failure), RTO (time to recover), read capacity, and geographic reach. Which would you choose for a US-based fintech with European expansion plans?
