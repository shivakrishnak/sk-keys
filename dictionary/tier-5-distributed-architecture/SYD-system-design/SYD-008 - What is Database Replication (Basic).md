---
id: SYD-008
title: What is Database Replication (Basic)
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★☆☆
depends_on: SYD-005
used_by: SYD-073
related: SYD-007
tags:
  - database
  - foundational
  - mental-model
  - distributed
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 8
permalink: /system-design/what-is-database-replication-basic/
---

# SYD-008 - What is Database Replication (Basic)

⚡ TL;DR - Database replication copies data from one
server to others so reads scale independently of writes
and failures do not lose data.

| #008            | Category: System Design       | Difficulty: ★☆☆ |
| :-------------- | :---------------------------- | :-------------- |
| **Depends on:** | What is Scalability           |                 |
| **Used by:**    | Cache Invalidation Strategies |                 |
| **Related:**    | What is a Message Queue       |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Your application has one database. It handles all
reads and writes. As traffic grows, read queries -
user profile fetches, search results, dashboard loads

- compete with write queries for database CPU,
  connections, and I/O. A slow analytical report query
  starves the transaction path. A hardware failure on
  the single server means total data loss. Your business
  has a single point of failure with no recovery path.

**THE BREAKING POINT:**
Read-heavy applications (news sites, social media,
product catalogs) see 90%+ of their database traffic
as reads. That read traffic has nowhere to go but
the one overloaded primary. Queries queue. Deadlines
are missed. Availability drops to whatever uptime
the single server's hardware provides.

**THE INVENTION MOMENT:**
"This is exactly why database replication was created"

- copy the data to additional servers so reads can be
  distributed and the primary can focus on writes.

**EVOLUTION:**
Early replication was manual (dump and restore).
MySQL introduced binary log replication (circa 1995)
for asynchronous primary-replica streaming. PostgreSQL
added streaming replication in 9.0 (2010). Modern
distributed databases (CockroachDB, Spanner) use
consensus-based replication (Raft, Paxos) for
synchronous multi-master operation with global
consistency.

---

### 📘 Textbook Definition

**Database replication** is the process of
maintaining copies of the same database on multiple
servers. In primary-replica (formerly master-slave)
replication, one server (the primary) accepts writes;
changes are propagated to one or more replica servers
that accept reads. Replication can be synchronous
(primary waits for replica acknowledgement before
committing) or asynchronous (primary commits
immediately and propagates to replicas in background).
The primary trade-off is between data consistency and
write latency.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Database replication makes identical copies of your
data on multiple servers so reads can be shared.

**One analogy:**

> A textbook publisher prints one master copy and
> distributes thousands of identical copies to
> libraries worldwide. Students read from their local
> library copy. When the publisher updates the book,
> new editions propagate to all libraries.
> The printing press is the primary; libraries are
> replicas.

**One insight:**
Replication solves two problems simultaneously:
read scalability (distribute queries across replicas)
and durability (if the primary fails, a replica can
be promoted). A single database server with no
replicas is not production-grade for any service
where data matters.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Writes must be serialized (one canonical order).
2. All replicas must eventually reflect all writes.
3. Reads can tolerate slightly stale data (in most
   business contexts).

**DERIVED DESIGN:**
Since writes must be ordered and there is one canonical
source of truth (the primary), replicas are fed a
stream of changes from the primary's write-ahead log
(WAL) or binary log. Replicas apply changes in the
same order, eventually converging to the same state.

For reads, the system routes them to replicas. The
replica may be slightly behind the primary (replication
lag), so reads may return data that is a few
milliseconds to seconds old.

**THE TRADE-OFFS:**
**Gain:** Read throughput scales linearly with replica
count. Write failures on replicas do not block the
primary. A hardware failure on one node does not lose
data.

**Cost:** Replication lag creates read-your-writes
consistency problems. Failover requires detecting
primary failure and promoting a replica (takes 30-120
seconds typically). Synchronous replication eliminates
lag but adds write latency equal to the network round
trip to the farthest replica.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** In a distributed system, you cannot
have zero replication lag with zero write overhead.
The CAP theorem forces a choice.

**Accidental:** Failover automation, replica lag
monitoring, and connection routing are accidental
complexity handled by proxy layers (ProxySQL,
pgBouncer, AWS RDS Multi-AZ).

---

### 🧪 Thought Experiment

**SETUP:**
A news website has 1 million readers and 100 editors.
The database has 10,000 reads per second and 10
writes per second. Ratio: 1000:1 reads to writes.

**WHAT HAPPENS WITHOUT REPLICATION:**
All 10,000 reads/second hit the primary alongside
the 10 writes. The primary is at 90% CPU on reads.
Slow read queries block write transactions. An editor's
article publish takes 10 seconds instead of 10ms.
Reader experience degrades. One server hosts the
entire article archive with no backup.

**WHAT HAPPENS WITH REPLICATION:**
5 read replicas are added. Each handles 2,000
reads/second. The primary handles only 10 writes
and coordinates replication. CPU drops to 20%.
Write latency returns to sub-millisecond. If the
primary fails, one replica is promoted in 60 seconds.
All article data is preserved on 5 servers.

**THE INSIGHT:**
Replication disaggregates read and write workloads.
In any read-heavy system, this is the highest
leverage database scaling technique.

---

### 🧠 Mental Model / Analogy

> Think of a government issuing a new law. There is
> one official legislature (the primary) where the
> law originates. Copies are printed and sent to every
> courthouse (replicas) in the country. Citizens can
> read the law at their local courthouse. When the law
> is amended, the change is printed and sent to all
> courthouses. There is a short delay between the
> amendment and all courthouses receiving the update.

Mapping:

- "Legislature" → primary database server
- "Courthouse" → read replica
- "Law text" → database row data
- "Amendment" → write / UPDATE transaction
- "Printing and distributing" → replication stream
- "Short delay" → replication lag

**Where this analogy breaks down:** Courthouses do not
elect a new legislature if the current one is destroyed.
In database replication, a replica can be promoted to
primary via automated failover - the analogy misses
the durability and high-availability aspect.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Replication means keeping copies of your database
on multiple servers. If one breaks, the others keep
working. Readers can use any copy.

**Level 2 - How to use it (junior developer):**
Configure your application to use a write connection
string (primary) for INSERTs/UPDATEs and a read
connection string (replica load balancer) for SELECTs.
Most ORM frameworks support this natively
(`django` `DATABASES['replica']`, Spring's
`@Transactional(readOnly=true)`).

**Level 3 - How it works (mid-level engineer):**
The primary writes changes to a binary log (MySQL) or
write-ahead log (PostgreSQL). Replica I/O threads
stream these logs and replay them in order. Replication
lag is measured as the time between a commit on the
primary and the same commit appearing on a replica.
Typical asynchronous lag: 10ms-5s depending on load
and network.

**Level 4 - Why it was designed this way (senior/staff):**
Asynchronous replication was chosen over synchronous
because it does not add write latency. The trade-off
is acknowledged potential data loss: if the primary
fails mid-replication, recently committed data that
hasn't propagated is lost. Synchronous replication
(PostgreSQL `synchronous_commit = on`) eliminates this
but adds 1-5ms of write latency per replica in the
sync group. Semi-synchronous (at least one replica
confirms) is a common middle ground.

**Level 5 - Mastery (distinguished engineer):**
Replication lag is not a constant - it spikes during
write bursts and large transactions. A 4-hour
ALTER TABLE on the primary creates a 4-hour lag on
replicas because DDL is serialized in the replication
stream. This is a production trap: developers assume
replicas are "a few seconds behind" but during
schema migrations they are hours behind. Staff
engineers schedule large DDL during low-traffic
windows and monitor replica lag continuously. They
also understand that "read from replica" breaks the
"read your own writes" guarantee - a user who writes
data and immediately reads it may see the pre-write
state if their read hits a lagging replica.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────┐
│   PRIMARY-REPLICA REPLICATION           │
│                                         │
│  Application                            │
│  ┌────────┐   ┌─────────────────────┐  │
│  │ WRITE  │──▶│  Primary DB         │  │
│  └────────┘   │  [Binary Log/WAL]   │  │
│               └──────────┬──────────┘  │
│                           │ stream      │
│               ┌───────────┴──────────┐ │
│               │                      │ │
│          ┌────▼─────┐  ┌─────────┐   │ │
│          │ Replica 1│  │Replica 2│   │ │
│          └────┬─────┘  └────┬────┘   │ │
│               │              │        │ │
│  ┌────────┐   └──────────────┘        │ │
│  │  READ  │──▶  Read Load Balancer    │ │
│  └────────┘                           │ │
└─────────────────────────────────────────┘
```

**Step 1 - Write to Primary:**
The application sends a write to the primary.
The primary executes the transaction and writes it
to the binary log / WAL.

**Step 2 - Log Streaming:**
The replica's I/O thread connects to the primary
and streams new log entries. The relay log stores
them locally on the replica.

**Step 3 - Log Apply:**
The replica's SQL thread reads the relay log and
executes the same operations against the replica's
data files, producing an identical copy.

**Step 4 - Read Routing:**
Application reads are routed to the read load
balancer (or ProxySQL) which distributes them
across all replicas. Health checks remove lagging
or failed replicas automatically.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
App write → Primary DB
  → WAL entry created
  → Replica streams WAL
      ← YOU ARE HERE (replication stream)
  → Replica applies entry
  → App read → Load Balancer
  → Replica responds with data
```

**FAILURE PATH:**

```
Primary DB fails
  → Health check detects failure (30s)
  → Replica with lowest lag promoted
  → DNS / proxy updated to point to new primary
  → Application reconnects (connection retry)
  → Old primary recovered as replica later
```

**WHAT CHANGES AT SCALE:**
At 10x read load, add more replicas. At 100x writes,
replication lag spikes - consider sharding or
multi-primary. At 1000x, synchronous replication
across data centers requires consensus protocols
(Raft) and latency measured in cross-AZ RTT.

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Read/Write routing**

```java
// BAD - all queries hit the primary
// Replicas exist but are unused
@Service
public class UserService {
    @Autowired
    private DataSource primaryDataSource;

    public User findUser(Long id) {
        // Unnecessary primary hit for a read
        return jdbcTemplate.queryForObject(
            "SELECT * FROM users WHERE id = ?",
            new Object[]{id},
            userRowMapper
        );
    }
}
```

```java
// GOOD - reads routed to replica
// Spring's AbstractRoutingDataSource pattern
@Configuration
public class DataSourceConfig {
    @Bean
    public DataSource routingDataSource(
        DataSource primary,
        DataSource replica
    ) {
        Map<Object, Object> sources = new HashMap<>();
        sources.put("PRIMARY", primary);
        sources.put("REPLICA", replica);
        RoutingDataSource routing =
            new RoutingDataSource();
        routing.setTargetDataSources(sources);
        routing.setDefaultTargetDataSource(primary);
        return routing;
    }
}

// Use @Transactional(readOnly = true) to route
// to replica automatically
@Transactional(readOnly = true)
public User findUser(Long id) {
    return userRepository.findById(id)
        .orElseThrow();
}
```

**Example 2 - Monitoring replication lag**

```sql
-- PostgreSQL: check replication lag
SELECT
  client_addr,
  state,
  sent_lsn,
  write_lsn,
  flush_lsn,
  replay_lsn,
  (sent_lsn - replay_lsn) AS lag_bytes
FROM pg_stat_replication;

-- MySQL: check slave status
SHOW REPLICA STATUS\G
-- Look at: Seconds_Behind_Source
-- > 30 = warning, > 300 = critical
```

---

### ⚖️ Comparison Table

| Mode                  | Write Latency | Data Loss Risk  | Complexity | Best For                 |
| --------------------- | ------------- | --------------- | ---------- | ------------------------ |
| **Async replication** | Low           | Seconds of data | Low        | Read-heavy, tolerate lag |
| Sync replication      | +RTT overhead | Zero            | Medium     | Durability critical      |
| Semi-sync (1 replica) | +1 RTT        | Near-zero       | Medium     | Balance of both          |
| Multi-master          | Variable      | Conflict risk   | High       | Geo-distributed writes   |

**How to choose:** Async replication is the default
for read scaling. Use semi-sync or sync when the
business cannot tolerate any data loss (financial,
healthcare). Multi-master only when geographic write
distribution is required.

---

### ⚠️ Common Misconceptions

| Misconception                                        | Reality                                                                                                                                   |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Replicas are always in sync with the primary         | Asynchronous replicas lag by milliseconds to seconds under normal load, and minutes to hours during large transactions.                   |
| Adding more replicas is always safe                  | Each replica creates replication load on the primary. Beyond 5-10 replicas, use a cascading replica (replica of a replica).               |
| Failover is instant                                  | Automatic failover detection takes 30-120 seconds. Applications must handle connection failures with retry logic.                         |
| Read from replica is equivalent to read from primary | Replication lag means replicas may not reflect recent writes - "read your own writes" breaks unless you route your own writes to primary. |
| Replication provides backup                          | Replication is not backup. If you DELETE FROM users accidentally, the DELETE replicates to all replicas within seconds.                   |

---

### 🚨 Failure Modes & Diagnosis

**Replication Lag Spike During Large Transaction**

**Symptom:**
Replica lag jumps from 0ms to 30+ minutes. Read
queries on replicas return stale data. Monitoring
alerts fire.

**Root Cause:**
A large transaction (ALTER TABLE, bulk UPDATE, large
import) runs on the primary. It appears as a single
log entry that the replica must apply serially,
blocking all subsequent replication during its
execution.

**Diagnostic Command / Tool:**

```sql
-- PostgreSQL: find long-running replica queries
SELECT pid, now() - pg_stat_activity.query_start
    AS duration, query, state
FROM pg_stat_activity
WHERE state != 'idle'
  AND query_start < now() - interval '1 minute';
```

**Fix:**
For schema migrations, use online schema change tools
(pt-online-schema-change, gh-ost) that avoid table
locks and minimize replication lag.

**Prevention:**
Schedule large DDL during off-peak hours. Monitor lag
continuously. Set lag alert threshold at 30 seconds.

---

**Read-Your-Writes Inconsistency**

**Symptom:**
A user updates their display name, refreshes the page,
and sees the old name. The updated name appears after
a few seconds. Intermittent, hard to reproduce.

**Root Cause:**
The write went to the primary. The subsequent read
was routed to a replica that had not yet received the
replication update.

**Diagnostic Command / Tool:**

```sql
-- PostgreSQL: check replica lag for your replica
SELECT now() - pg_last_xact_replay_timestamp()
    AS replication_lag;
```

**Fix:**
For operations that require read-your-writes (user
profile updates, shopping cart), route reads to the
primary for the 1-2 seconds after a write, or use
sticky sessions to the primary for that user's
session window.

**Prevention:**
At application design time, identify which read paths
require read-your-writes consistency and explicitly
route them to primary. Do not default all reads to
replicas without this analysis.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `What is Scalability` - replication is the primary
  mechanism for scaling database read throughput
- `Database Transactions` - understanding ACID
  properties clarifies why replication lag exists
  and what consistency guarantees apply

**Builds On This (learn these next):**

- `Cache Invalidation Strategies` - caches and
  replicas both serve stale reads; their invalidation
  patterns share the same core problem
- `Database Sharding` - the next scaling step when
  write throughput exceeds what a single primary
  can handle

**Alternatives / Comparisons:**

- `Database Sharding` - horizontal partitioning of
  data rather than copying; scales writes, not reads
- `CQRS` - application-level read model separation
  that serves a similar purpose to read replicas

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Maintaining identical copies of a DB on  │
│              │ multiple servers for scale and durability │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ One DB server is a bottleneck for reads  │
│ SOLVES       │ and a single point of failure            │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Read replicas let you scale reads linearly│
│              │ while writes stay on a single primary     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Read traffic dwarfs write traffic;        │
│              │ database durability is required           │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Write-heavy workloads; all reads must be  │
│              │ immediately consistent after writes       │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Using replication as backup - a DELETE    │
│              │ replicates to all replicas immediately    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Read scale + durability vs replication    │
│              │ lag and read-your-writes complexity       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Many readers, one writer - replicas are  │
│              │  the cheapest read scaling available."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Sharding → CQRS → Distributed Databases  │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Replicas scale reads; the primary handles writes.
2. Async replication has lag - replicas are never
   perfectly up to date with the primary.
3. Replication is not backup - data corruption
   replicates everywhere instantly.

**Interview one-liner:**
"Database replication copies the write-ahead log from
a primary to read replicas. It scales read throughput
linearly with replica count and provides durability
through redundancy. The catch is replication lag -
replicas may be slightly behind the primary, which
breaks read-your-writes consistency if you route
reads to replicas without compensating."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Separate read and write concerns." Any system with
a high read-to-write ratio benefits from having
dedicated read infrastructure. This principle appears
in CQRS at the application level, CDN at the network
level, and CPU caches at the hardware level.

**Where else this pattern appears:**

- CQRS pattern - separate read and write data models
  at the application code level
- CDN edge caches - replicate static content to read
  nodes close to users
- DNS TTL - cached DNS records are the IP of your
  server "as of N seconds ago"

**Industry applications:**

- Social media feeds - read replicas serve billions
  of feed reads while the primary handles post writes
- Banking reporting - analytical read replicas take
  complex reports off the transactional primary

---

### 💡 The Surprising Truth

Replication is not just for scale - the biggest
hidden benefit is cross-region disaster recovery.
Many engineers think "replicas = read performance."
But a synchronous replica in a different data center
means your data survives a complete regional outage.
AWS Multi-AZ RDS, for example, keeps a synchronous
replica in a different Availability Zone specifically
for this purpose, with automatic failover in 30-60
seconds - not for performance, but for survival.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. [EXPLAIN] Explain replication lag and the
   read-your-writes problem to a junior developer
   using only an analogy.
2. [DEBUG] Given Seconds_Behind_Source = 1800 in
   MySQL `SHOW REPLICA STATUS`, identify the likely
   cause and immediate diagnostic steps.
3. [DECIDE] Given a checkout flow where the user
   must see their own just-placed order immediately,
   decide which DB connection to use and why.
4. [BUILD] Configure Spring Boot to route
   `@Transactional(readOnly = true)` methods to a
   replica using `AbstractRoutingDataSource`.
5. [EXTEND] Design a replica topology for a system
   with 5 geographic regions, high read load in all
   regions, and write-anywhere requirements.

---

### 🧠 Think About This Before We Continue

**Q1.** Your e-commerce checkout reads the user's
cart from a replica. The user just added an item.
The replica is 2 seconds behind. The user checks out
and the cart is missing the last item. What are two
architectural approaches to prevent this, and what
are their costs?
_Hint: Consider routing strategies and the trade-off
between consistency and read scalability._

**Q2.** You have 10 read replicas and replication
lag is 500ms at normal load. During a marketing
campaign, write volume triples and lag jumps to
30 seconds. Why does more writes cause more replica
lag, and what can you do at the infrastructure level?
_Hint: Think about how the replication stream is
applied on the replica - is it parallel or serial?_

**Q3.** [HANDS-ON] Set up a PostgreSQL streaming
replica locally using Docker. Write a script that
measures replication lag every second. Then run
a 100,000-row INSERT on the primary and observe how
lag evolves. What does the lag curve tell you about
replica apply throughput?
_Hint: Use `pg_stat_replication.replay_lsn` on the
primary to compute lag in bytes and seconds._

---

### 🎯 Interview Deep-Dive

**Q1: What is the difference between synchronous
and asynchronous database replication, and when
would you choose each?**
_Why they ask:_ Tests understanding of the
consistency-latency trade-off in replication.
_Strong answer includes:_

- Async: primary commits immediately, replicates in
  background. Low write latency, potential data loss
  on primary failure.
- Sync: primary waits for replica ACK. Zero data loss,
  but write latency increases by network RTT.
- Choose sync for financial data, healthcare records.
  Choose async for general web apps where eventual
  consistency is acceptable.

**Q2: A user submits a form, gets a success message,
and then immediately sees their old data on the next
page load. What is the likely cause and fix?**
_Why they ask:_ Tests production experience with
replication lag and read-your-writes.
_Strong answer includes:_

- Classic read-your-writes failure: write to primary,
  read routed to lagging replica.
- Fix: route reads to primary for a time window after
  a write, or use "sticky" primary routing for user
  sessions that just wrote data.
- Longer-term: use cache-aside with explicit write to
  cache on update so the next read hits cache, not
  replica.

**Q3: Replication is not backup. Explain why and what
the actual backup strategy should be.**
_Why they ask:_ Tests awareness of a common dangerous
misconception.
_Strong answer includes:_

- A DELETE on the primary replicates to all replicas
  within seconds - all copies are affected.
- Actual backup: point-in-time recovery (PITR) using
  WAL archives to an S3-compatible store.
- Test restores regularly - a backup never tested is
  not a backup.
