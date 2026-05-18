---
id: SYD-033
title: Read-Heavy vs Write-Heavy Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-005
used_by: ""
related: SYD-005, SYD-008, SYD-031, SYD-032, SYD-034, SYD-035
tags:
  - architecture
  - database
  - scalability
  - design-tradeoff
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 33
permalink: /technical-mastery/syd/read-heavy-vs-write-heavy/
---

⚡ TL;DR - Read-heavy and write-heavy workloads require
fundamentally different system architectures. Read-heavy
systems (typical web apps: 100:1 read-write ratio) scale
reads with caching, CDNs, and read replicas. Write-heavy
systems (logging, metrics, event sourcing) must scale the
write path through sharding, async writes, and write-
optimized storage (LSM trees). Misidentifying your workload
type leads to over-engineering the wrong path and under-
engineering the bottleneck.

| #033 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | CAP Theorem and Consistency Models | |
| **Used by:** | (Fan-Out on Write vs Read) | |
| **Related:** | CAP Theorem, Horizontal Scaling, Sharding, Hot Shard, Denormalization for Scale, Fan-Out on Write vs Read | |

---

### 🔥 The Problem This Solves

**THE WRONG ARCHITECTURE:**
An engineering team builds a news feed service.
They carefully shard the database for write scalability
(5 shards). But the actual write load is 1,000/sec and
read load is 500,000/sec (500:1 ratio). The bottleneck
is never the database writes - it is the read path.
The caching layer was not invested in.

Result: database reads overwhelm all 5 shards despite
light write load. Meanwhile, the sharding complexity
adds operational burden. The team solved the wrong problem.

**THE OPPOSITE MISTAKE:**
A log ingestion pipeline for 10,000 microservices expects
to receive 5 million events per second. The team deploys
PostgreSQL with read replicas, expecting to query the
logs later. The write path immediately saturates the
PostgreSQL primary at ~20K writes/sec. Log events start
dropping. The team added read replicas which don't help
writes. The pipeline is broken.

---

### 📘 Textbook Definition

**Read-heavy system:** A system where reads significantly
outnumber writes (typically >10:1 ratio). The primary
bottleneck is read throughput. Common examples: social
media feeds, product catalog, content delivery, search.

**Write-heavy system:** A system where writes are the
bottleneck or near-equal to reads. The primary challenge
is write throughput and write durability. Common examples:
log ingestion, metrics pipelines, IoT sensor data,
event sourcing, payment ledgers, audit trails.

**Mixed workload:** Many systems have read-heavy primary
paths with write-heavy secondary paths (e.g., an
e-commerce checkout: read-heavy product browsing,
write-heavy order processing). Each path must be
designed independently.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Identify whether your bottleneck is reads or writes.
Then invest architecture in the right path - you cannot
optimize everything equally.

**One analogy:**
> A restaurant:
> - Read-heavy: a takeout restaurant where 100 customers
>   pick up orders while 2 chefs cook. The bottleneck is
>   the counter (order fulfillment, read path). Fix:
>   more counter staff, not more chefs.
> - Write-heavy: a catering company producing 1,000 meals
>   per hour for events. The bottleneck is the kitchen
>   (production, write path). Fix: more chefs and prep
>   stations, not more servers.
>
> A "restaurant architect" who installs more counters at
> the catering company - or more chefs at the takeout
> restaurant - has misdiagnosed the bottleneck.

**One insight:**
Read-heavy solutions (caching, CDN, read replicas) add
stale data risk (cache invalidation). Write-heavy solutions
(async writes, LSM trees, write buffers) add read latency
and eventual consistency. Knowing the workload type prevents
over-applying one set of tradeoffs to the wrong problem.

---

### 🔩 First Principles Explanation

**PROFILING WORKLOAD TYPE:**

```
Key questions to ask:
  1. Reads per second / Writes per second = ratio?
     <5:1   = write-intensive (or mixed)
     5-50:1  = balanced; optimize both
     >50:1  = read-heavy (optimize read path primarily)
     
  2. What does a latency spike trace to?
     Read latency spike → read path is bottleneck
     Write latency spike → write path is bottleneck
     
  3. What is the data access pattern?
     Same data read many times = cacheable read-heavy
     Data written once read never (logging) = write-heavy
     Data written once read once (messages) = stream
     
  4. What is the data size?
     Small/hot dataset = cache-friendly read-heavy
     Append-only large = write-heavy (log/time-series)
```

**READ-HEAVY ARCHITECTURE PATTERNS:**

```
Read-heavy toolkit:
  1. Multi-tier caching:
     CDN → application cache (Redis) → DB read replica
     Cache hit rates of 95%+ reduce DB read load by 20x

  2. Read replicas:
     Primary handles writes; replicas handle reads
     Scales read throughput with replica count
     
  3. Denormalization:
     Pre-join data so reads are single-table queries
     Avoids expensive JOIN operations under load

  4. Read-optimized data structures:
     B-tree indexes (PostgreSQL) for sorted reads
     Covering indexes to avoid table scans

  5. Materialized views:
     Pre-compute aggregations
     Expensive aggregation queries become indexed reads

  6. Fan-out on write:
     Precompute results for each user at write time
     Reads become a simple key-value lookup
```

**WRITE-HEAVY ARCHITECTURE PATTERNS:**

```
Write-heavy toolkit:
  1. Async writes (write buffering):
     Accept write → ACK to client → persist async
     Allows 10x-100x higher write throughput
     Risk: in-flight data lost if crash before persist

  2. Write-ahead log (WAL) + batching:
     Buffer multiple writes, flush as a batch
     Amortizes fsync() cost across many writes
     Used by: Kafka (batch.size, linger.ms)

  3. LSM tree storage (write-optimized):
     Writes go to in-memory memtable (fast)
     Flushed to sorted SSTable files (sequential I/O)
     Background compaction merges SSTables
     Read: check multiple SSTables (slower than B-tree)
     Used by: Cassandra, RocksDB, LevelDB

  4. Sharding:
     Distribute writes across N independent primaries
     Each shard handles 1/N of write load

  5. Event streaming (Kafka):
     Write to Kafka (sequential append, very fast)
     Consumers process at their own pace
     Kafka handles 1M+ writes/sec per broker

  6. CQRS:
     Separate write model from read model
     Write to event log; derive read models async
```

**THE STORAGE ENGINE DECISION:**

```
B-tree (PostgreSQL, MySQL):
  Write: random I/O (update in-place)
  Read: O(log N) with index
  Best for: balanced read/write, strong consistency

LSM tree (Cassandra, RocksDB):
  Write: sequential append to memtable → SSTable
  Read: multiple SSTable lookups (slower than B-tree)
  Best for: write-heavy, high-throughput ingestion

Columnar store (ClickHouse, Parquet):
  Write: buffered batch insert
  Read: column projection (very fast for analytics)
  Best for: write-once read-many, analytical queries
```

---

### 🧪 Thought Experiment

**SCENARIO: Design a "likes" counter system**

Instagram has 500M users. A post can get 10M likes in
an hour (viral post). The team debates the architecture.

**APPROACH A: Read-heavy design (wrong)**
Store likes in a relational table:
  `likes(post_id, user_id, created_at)`
Read: `SELECT COUNT(*) FROM likes WHERE post_id=X`
Write: `INSERT INTO likes VALUES (X, Y, NOW())`

Problem: a viral post gets 10M writes in 1 hour
(2,800 writes/sec peak). The database's write capacity
is saturated. This IS a write-heavy path. Read-heavy
optimization (read replicas, caching) helps reads but
does not fix the write bottleneck.

**APPROACH B: Write-heavy design (correct)**
Accept like events as a Kafka stream (1M writes/sec).
A counter service consumes the stream and increments
a Redis counter: `INCR post:{post_id}:likes`.
Periodic batch job materializes counters to a DB table.

Read: `GET post:{post_id}:likes` from Redis (1μs).
Write: stream to Kafka (async), Redis INCR (1μs).

Result: The write path (Kafka + Redis atomic increment)
handles millions of writes/sec without a B-tree database
bottleneck. The read path (Redis GET) is O(1) with no
database involvement. Both paths independently optimized.

**THE LESSON:**
"Like" writes are write-heavy (volume, frequency).
"Like count" reads are read-heavy (100x more read
frequency than write frequency). The right architecture
treats these as two separate paths: a write-optimized
event stream for the write path, a read-optimized cache
for the read path. CQRS by design.

---

### 🧠 Mental Model / Analogy

> Read vs write heavy is like a library's two jobs:
>
> READ-HEAVY job: Lending books to 10,000 patrons/day.
>   Each book is checked out many times. The bottleneck
>   is the checkout desk. Fix: automated checkout kiosks
>   (caching), more librarians (replicas), books near
>   the exit (CDN).
>
> WRITE-HEAVY job: Cataloging 1,000 new books/day.
>   Each book is cataloged once, rarely read by staff.
>   The bottleneck is the cataloging process. Fix: faster
>   cataloging tools, parallel catalogers (sharding),
>   batch processing (write buffering). Adding checkout
>   kiosks does not help catalogers.
>
> A library doing both jobs needs both architectures,
> each optimized for its own bottleneck.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Some systems are read much more than written (like a
web page). Others are written to constantly (like a
log file). Each type needs a different kind of infrastructure.

**Level 2 - How to use it (junior developer):**
Identify your read/write ratio before designing.
If >10:1 (reads:writes): invest in caching and read
replicas. If <5:1 or write-bound: invest in write
throughput (async writes, LSM storage, sharding).

**Level 3 - How it works (mid-level engineer):**
Profile with real metrics (not assumptions). Measure
read and write QPS in production (or expected from
requirements). Trace latency to identify whether read
or write path is the actual bottleneck. Then apply
the appropriate toolkit.

**Level 4 - Why it was designed this way (senior/staff):**
Storage engines make a fundamental choice: optimize
for reads (B-tree, update-in-place) or writes (LSM,
append-only). This choice cannot be changed without
replacing the storage engine. Choosing Cassandra for
a read-heavy, consistency-critical workload leads to
performance issues (LSM reads are slower). Choosing
PostgreSQL for a 10M-writes/sec time-series pipeline
leads to immediate saturation (B-tree random writes
are expensive). The read/write tradeoff is hardcoded
into the storage layer.

**Level 5 - Mastery (distinguished engineer):**
The deepest insight: CQRS (Command Query Responsibility
Segregation) is the architectural formalization of this
principle. Separate the write model (optimized for
writes) from the read model (optimized for reads).
The write model captures events (append-only, write-
optimized). The read model is derived from events
(materialized views, denormalized, cache-friendly).
This is how systems like Kafka + Elasticsearch are
built: Kafka is the write model (sequential append),
Elasticsearch is the read model (indexed search).
Each optimized for its purpose; neither is a compromise.

---

### ⚙️ How It Works (Mechanism)

**Architecture comparison:**

```
┌──────────────────────────────────────────────────────┐
│ READ-HEAVY ARCHITECTURE                             │
│                                                      │
│  Client ─► CDN ─► Redis cache ─► Read replica      │
│                         │           (x5)            │
│                         │                           │
│                    Cache hit:                       │
│                    99% of reads                     │
│                    never reach DB                   │
│                                                      │
│  Write: Client → Primary DB (low volume)            │
│  Primary → replicates to read replicas              │
│                                                      │
│ READ-HEAVY BOTTLENECK: cache miss rate              │
│ MONITOR: cache hit %, replica replication lag       │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ WRITE-HEAVY ARCHITECTURE                            │
│                                                      │
│  Client → Load balancer → Kafka (append-only)       │
│                               │                     │
│                          Consumers (async)          │
│                               │                     │
│                    ┌──────────┴─────────────┐       │
│                    │ Process & persist       │       │
│                    │ to Cassandra/RocksDB    │       │
│                    │ (LSM tree, write-opt)   │       │
│                    └────────────────────────┘       │
│                                                      │
│ Kafka ACK → client: < 1ms                          │
│ DB persist: async, within seconds                  │
│                                                      │
│ WRITE-HEAVY BOTTLENECK: consumer lag, compaction    │
│ MONITOR: Kafka consumer lag, LSM compaction I/O     │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Read-heavy: user profile with multi-tier cache**
```python
# Read-heavy pattern: user profiles (1000:1 read:write)
# Multi-tier cache reduces DB reads by 99%

from functools import wraps
import redis
import json

r = redis.Redis(host="redis", port=6379)
PROFILE_TTL = 300  # 5 minutes

def get_user_profile(user_id: int) -> dict:
    """
    Read-heavy path: check cache first, fall back to DB.
    Profile is read 1000x more than written.
    """
    # L1: Redis cache check (< 1ms)
    cache_key = f"profile:{user_id}"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    # L2: DB read (only on cache miss: ~1% of reads)
    profile = db.query(
        "SELECT * FROM users WHERE id = %s", [user_id]
    )
    if profile:
        # Populate cache (300s TTL)
        r.setex(cache_key, PROFILE_TTL, json.dumps(profile))
    return profile

def update_user_profile(user_id: int, data: dict):
    """Write path: update DB and invalidate cache."""
    db.execute(
        "UPDATE users SET name=%s WHERE id=%s",
        [data["name"], user_id]
    )
    # Invalidate cache immediately
    # (Next read will repopulate from DB)
    r.delete(f"profile:{user_id}")
```

**Example 2 - Write-heavy: metrics ingestion pipeline**
```python
# Write-heavy pattern: metrics ingestion
# 100,000 metric events/sec; read once for alerts

from kafka import KafkaProducer
import json
import time

producer = KafkaProducer(
    bootstrap_servers=["kafka:9092"],
    # Write optimization: batch for throughput
    batch_size=64 * 1024,     # 64KB batch
    linger_ms=5,              # wait up to 5ms to fill batch
    compression_type="lz4",   # compress for throughput
    acks=1,                   # single broker ACK (fast)
    # acks=all for durability; acks=1 for write throughput
)

def ingest_metric(service: str, metric: str, value: float):
    """
    Write-heavy path: metrics ingestion.
    Do NOT write directly to PostgreSQL (will saturate).
    Write to Kafka; consumers persist to time-series DB.
    """
    event = {
        "service": service,
        "metric": metric,
        "value": value,
        "ts": int(time.time() * 1000)  # milliseconds
    }
    # Async send: returns immediately (< 1ms)
    # Actual disk write happens in Kafka broker
    producer.send(
        "metrics",
        key=f"{service}.{metric}".encode(),
        value=json.dumps(event).encode()
    )

# Consumer writes to ClickHouse (columnar, write-fast)
# Read queries on ClickHouse (column projection, fast for analytics)
```

**Example 3 - BAD vs GOOD: identifying workload type**
```python
# BAD: Read replicas on a write-heavy table
# write_heavy_table: 50,000 inserts/sec, rarely read

# Team adds 5 read replicas thinking it helps
# Result: 5 replicas all struggle to KEEP UP WITH WRITES
# from primary (replication lag). Reads are fine;
# writes are still bottlenecked on the primary.
# 5 replicas made the problem WORSE (more replication lag).

# Diagnosis:
# SELECT * FROM pg_stat_replication;
# → replication lag: 45 seconds and growing

# GOOD: Match the solution to the workload type
# Write-heavy table → don't use read replicas
# Use: Kafka → append-only → RocksDB/Cassandra
# Or: PostgreSQL with partitioning + archival
#     (drop old partitions instead of DELETE)
# 
# Check workload type FIRST:
# SELECT relname, n_tup_ins, n_tup_upd, n_tup_del,
#        seq_scan, idx_scan
# FROM pg_stat_user_tables
# ORDER BY n_tup_ins DESC;
# n_tup_ins >> seq_scan → write-heavy (optimize writes)
# seq_scan >> n_tup_ins → read-heavy (optimize reads)
```

---

### ⚖️ Comparison Table

| Property | Read-Heavy | Write-Heavy | Mixed |
|---|---|---|---|
| **Ratio** | >50:1 reads:writes | <5:1 or write-bound | 5-50:1 |
| **Bottleneck** | Read throughput | Write throughput | Both |
| **Primary fix** | Cache + read replicas | Sharding + async writes | CQRS (separate models) |
| **Storage engine** | B-tree (PostgreSQL) | LSM tree (Cassandra) | Depends on path |
| **Consistency model** | Eventually consistent (caching) | Eventual (async writes) | Configurable per path |
| **Examples** | Social feeds, product catalog | Log ingestion, metrics, IoT | E-commerce, banking |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| All databases need read replicas | Read replicas only help read-heavy workloads. For write-heavy workloads, replicas must process all writes from the primary to stay in sync. Under heavy write load, replicas lag and reads against them return stale data. |
| Caching solves all performance problems | Caching only helps if the same data is read repeatedly (high read:write ratio). For write-heavy data that is barely read, a cache wastes memory and adds invalidation complexity without reducing the write bottleneck. |
| You have to choose one or the other | Most systems have both read-heavy and write-heavy paths. Design each independently. CQRS formalizes this: separate write model (event log) from read model (materialized views). |

---

### 🚨 Failure Modes & Diagnosis

**Applying Read Optimizations to Write-Heavy Path**

**Symptom:**
PostgreSQL primary CPU at 95%, write latency 2 seconds,
with 5 read replicas at 10% CPU. Adding more replicas
does not reduce primary CPU. Replication lag on replicas
grows to 10 minutes.

**Diagnosis:**
```sql
-- Check if writes are the bottleneck:
SELECT sum(n_tup_ins + n_tup_upd + n_tup_del) as writes_per_sec,
       sum(seq_scan + idx_scan) as reads_per_sec
FROM pg_stat_user_tables;

-- If writes_per_sec >> reads_per_sec: write-heavy
-- Read replicas won't help; need write path optimization

-- Check replication lag:
SELECT client_addr, state, 
       pg_wal_lsn_diff(pg_current_wal_lsn(),
                       sent_lsn) as lag_bytes
FROM pg_stat_replication;
-- Growing lag = replicas can't keep up with write volume
```

**Fix:**
Migrate high-volume insert tables from PostgreSQL to
a write-optimized store (Cassandra, Kafka + RocksDB).
Or partition PostgreSQL table by time range with
aggressive archival (drop old partitions weekly rather
than DELETE, which is an expensive write operation).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `CAP Theorem and Consistency Models` - the consistency
  tradeoffs differ by read vs write design choice

**Builds On This (learn these next):**
- `Fan-Out on Write vs Read` - a direct application of
  this distinction to feed system design
- `Denormalization for Scale` - how read-heavy systems
  denormalize to avoid expensive JOINs

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ READ-HEAVY    │ >50:1 reads:writes                      │
│               │ Fix: cache, CDN, read replicas,         │
│               │ denormalization, materialized views     │
├───────────────┼─────────────────────────────────────────┤
│ WRITE-HEAVY   │ <5:1, or writes are the bottleneck      │
│               │ Fix: async writes, Kafka, sharding,     │
│               │ LSM tree storage (Cassandra, RocksDB)   │
├───────────────┼─────────────────────────────────────────┤
│ DIAGNOSE      │ Measure read QPS vs write QPS in prod   │
│               │ Trace latency spikes to read or write pa│
│               │ pg_stat_user_tables: n_tup_ins vs scans │
├───────────────┼─────────────────────────────────────────┤
│ STORAGE       │ Read-heavy: B-tree (PostgreSQL)         │
│               │ Write-heavy: LSM tree (Cassandra, RocksD│
│               │ Analytics: columnar (ClickHouse)        │
├───────────────┼─────────────────────────────────────────┤
│ CQRS          │ Separate write model + read model       │
│               │ Kafka = write model; search/cache = read│
├───────────────┼─────────────────────────────────────────┤
│ ONE-LINER     │ "Profile first. Match architecture to   │
│               │  the actual bottleneck: read or write." │
├───────────────┼─────────────────────────────────────────┤
│ NEXT EXPLORE  │ Fan-Out on Write vs Read → CQRS         │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Read-heavy: cache and read replicas. Write-heavy:
   async writes, Kafka, LSM-tree storage, sharding.
   Applying the wrong toolkit to the wrong workload
   wastes engineering effort and doesn't fix anything.
2. Most systems have both paths. Design them separately.
   CQRS is the formal pattern: separate write model
   (event log) from read model (materialized/cached).
3. Diagnose before designing. Measure actual read/write
   ratio from pg_stat_user_tables or APM. Assumptions
   about workload type are often wrong.

**Interview one-liner:**
"Read-heavy and write-heavy workloads require different
architectures. Read-heavy (>50:1 reads:writes) scales with
caching (Redis, CDN), read replicas, and denormalization.
Write-heavy scales with async writes (Kafka buffering), sharding
(split write load), and write-optimized storage engines (LSM
trees: Cassandra, RocksDB). The common mistake is applying
read optimizations (adding read replicas) to a write-heavy
table - replicas don't reduce primary write load. The correct
approach is to measure the actual read:write ratio, identify
which path is the bottleneck, then apply the appropriate
toolkit. Most real systems use CQRS: a separate write model
(event log, write-optimized) from a read model (materialized
views, cache-optimized), each designed for its purpose."
