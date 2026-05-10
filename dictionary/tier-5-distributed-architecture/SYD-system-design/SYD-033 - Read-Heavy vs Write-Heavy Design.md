---
id: SYD-033
title: "Read-Heavy vs Write-Heavy Design"
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★☆
depends_on: SYD-003, SYD-004
used_by: SYD-034, SYD-035, SYD-043
related: SYD-034, SYD-035, SYD-007
tags:
  - architecture
  - database
  - performance
  - tradeoff
  - advanced
status: complete
version: 3
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 33
permalink: /syd/read-heavy-vs-write-heavy-design/
---

# SYD-033 - Read-Heavy vs Write-Heavy Design

⚡ TL;DR - The primary system classification that determines database choice, caching strategy, replication topology, and scaling approach before any architecture decision is made.

| SYD-033         | Category: System Design        | Difficulty: ★★☆ |
| :-------------- | :----------------------------- | :-------------- |
| **Depends on:** | SYD-003, SYD-004               |                 |
| **Used by:**    | SYD-034, SYD-035, SYD-043      |                 |
| **Related:**    | SYD-034, SYD-035, SYD-007      |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You pick PostgreSQL, add a Redis cache, and deploy behind a load balancer. Everything seems right. Six months later, your write latency is spiking because the cache adds nothing to write performance. Or your read latency is terrible because you chose a write-optimised database (Cassandra) for a read-heavy social feed. Mismatching your architecture to your actual workload type is one of the most common and expensive system design mistakes.

**THE BREAKING POINT:**
A system optimised for reads performs terribly for writes, and vice versa. The architectural decisions - database type, caching layers, replication topology, storage format (row vs column) - are fundamentally different depending on whether reads or writes dominate. These decisions set the ceiling for the system's ability to scale.

**THE INVENTION MOMENT:**
Database vendors codified this distinction: LSM-tree (Log-Structured Merge) databases like Cassandra and RocksDB optimise for write throughput by sequentially appending to disk. B-tree databases like PostgreSQL optimise for read performance through balanced tree indexes. This fundamental split in storage engine design reflects the read/write trade-off encoded at the hardware level.

**EVOLUTION:**
OLTP (Online Transaction Processing) systems are typically balanced or write-heavy. OLAP (Online Analytical Processing) systems are read-heavy on aggregated historical data. The modern distinction also includes HTAP (Hybrid Transactional/Analytical Processing) databases like TiDB that attempt to serve both workloads, with different internal storage engines per query type.

---

### 📘 Textbook Definition

**Read-heavy design** optimises for throughput and latency of read operations at the cost of write complexity or latency. Common techniques: caching (Redis, CDN), read replicas, denormalization, pre-computation. **Write-heavy design** optimises for write throughput, often at the cost of read performance or consistency. Common techniques: write buffers, append-only logs, LSM-trees, async writes, eventual consistency. The read/write ratio is the first question to answer in any system design.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Identify your read/write ratio first - it determines every major architecture decision downstream.

**One analogy:**
> A library vs a recording studio. A library (read-heavy) has many readers, few writers - optimised for finding and retrieving books fast. A recording studio (write-heavy) has constant recording sessions - optimised for capturing audio reliably with minimal latency. The same building cannot efficiently serve both without dedicated rooms for each purpose.

**One insight:**
Read/write ratio is not fixed - it can change over time (social media posts: write-heavy at upload, read-heavy for years after). Design for the lifetime ratio, not just the upload moment.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Reads and writes contend for the same resources (CPU, disk I/O, network, database connections).
2. Optimising for one typically degrades the other - faster reads often require more work on write paths.
3. Caching amplifies read capacity cheaply; there is no equivalent for write amplification.
4. Read scale is achieved by adding read replicas or cache; write scale requires sharding or partitioning.
5. Consistency requirements constrain both - strong consistency limits both read and write throughput.

**DERIVED DESIGN:**
For read-heavy systems: add caching layers close to the user (CDN, Redis), replicate database for read distribution, denormalize to avoid joins on read path, pre-compute expensive aggregations. For write-heavy systems: batch writes, use append-only storage engines, accept eventual consistency, use LSM-tree databases, separate write and read paths (CQRS).

**THE TRADE-OFFS:**
**Gain (read optimisation):** Low read latency, cache absorption of repeated reads, horizontal read scaling.
**Cost (read optimisation):** Stale cache data, fanout write cost (update cache + DB), complex invalidation logic.
**Gain (write optimisation):** High write throughput, low write latency.
**Cost (write optimisation):** Read latency higher (data not pre-indexed), eventual consistency.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** The physical constraint that writing and reading from the same disk is serial - one must wait for the other.
**Accidental:** Using a single monolithic database for both OLTP and OLAP queries - these can be separated into different stores.

---

### 🧪 Thought Experiment

**SETUP:**
Two systems: System A is a social media post feed (users scroll to read posts, rarely write new ones). System B is an IoT sensor platform (10,000 sensors writing 1 data point/second each = 10,000 writes/second; data is rarely read outside of dashboards).

**WHAT HAPPENS WITHOUT THE CLASSIFICATION:**
Both teams pick PostgreSQL + Redis cache. System A works great (low read latency via cache). System B is overwhelmed - Redis cache adds nothing since writes bypass it, and PostgreSQL with indexes struggles at 10,000 writes/second.

**WHAT HAPPENS WITH THE CLASSIFICATION:**
System A: PostgreSQL with read replicas + aggressive Redis caching + CDN for media = sub-100ms reads at any scale. System B: Cassandra or InfluxDB (write-optimised LSM-tree) for time-series data + no cache on write path + separate read path with aggregation + retention policies for old data.

**THE INSIGHT:**
The same technology stack will be dramatically right or wrong depending on the read/write ratio. Classification drives technology selection, not the other way around.

---

### 🧠 Mental Model / Analogy

> Read/write ratio is like traffic pattern on a road. A one-way street (read-heavy) handles many cars flowing in one direction efficiently - widen the lanes, add more lanes, optimise for flow. A bidirectional road with frequent deliveries (write-heavy) needs different optimisation - loading docks, one-way for heavy trucks, bypass lanes for normal traffic.

**Mapping:**
- Road → database/storage system
- Cars (one direction) → read requests
- Delivery trucks (both directions) → write requests
- Adding lanes → read replicas
- Bypass roads → write-optimised paths (WAL, LSM)
- Traffic signals → transactions and locks

Where this analogy breaks down: road traffic is physical and cannot be cached; database reads can be served from cache, removing them from the road entirely.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Does your app mostly let people view content, or mostly let people create/update content? Mostly viewing = read-heavy. Mostly creating = write-heavy. This one question changes which database you use, whether you need caching, and how you make copies of your data.

**Level 2 - How to use it (junior developer):**
Ask during requirements: "How many reads vs writes per second?" Estimate from user behaviour: 10M DAU × 100 reads/day / 86400 sec ≈ 11,600 reads/sec vs × 2 writes/day ≈ 230 writes/sec = 50:1 read/write ratio. A 50:1 ratio is strongly read-heavy → add aggressive caching and read replicas; write path does not need optimisation.

**Level 3 - How it works (mid-level engineer):**
Different read/write ratios trigger different architectural choices. 100:1+ ratio (social feed, Wikipedia): CDN + distributed cache absorbs >95% of reads; database sees minimal load. 1:1 ratio (transaction systems, order management): no cache benefit; focus on write path reliability, ACID transactions. 1:100+ ratio (IoT, logging, analytics ingestion): write-optimised LSM-tree DB (Cassandra, InfluxDB); separate read path for analytics via batch job or secondary read replica.

**Level 4 - Why it was designed this way (senior/staff):**
The fundamental hardware constraint (CPU, disk, memory) means you cannot simultaneously optimise for reads and writes on the same path without trade-offs. Senior engineers design systems where the read and write paths are separated (CQRS: Command Query Responsibility Segregation), using write-optimised storage for writes and a separately maintained read model for queries. The two models are kept in sync via event streams or change data capture (CDC), accepting a consistency lag.

**Expert Thinking Cues:**
- "Does the read/write ratio change over an entity's lifetime? (write-heavy at creation, read-heavy thereafter)"
- "What are the consequences of reading stale data? (determines cache TTL and consistency requirements)"
- "Should read and write paths be separately optimised (CQRS/event sourcing)?"
- "What is the ratio for the hot path (p99 cases) vs the average?"

---

### ⚙️ How It Works (Mechanism)

```
READ-HEAVY ARCHITECTURE STACK
══════════════════════════════
Client Read Request
    │
    ▼
CDN (cache TTL: 1 min-1 day)
    │ cache miss
    ▼
API Gateway + Load Balancer
    │
    ▼
App Server
    │
    ▼
Redis Cache (TTL: 1-60 min)
    │ cache miss
    ▼
Read Replica (DB)  ← YOU ARE HERE
(multiple replicas absorb reads)

WRITE-HEAVY ARCHITECTURE STACK
═══════════════════════════════
Client Write Request
    │
    ▼
API Gateway + Load Balancer
    │
    ▼
App Server → Write Queue (Kafka)
    │         (decouples write burst)
    ▼
Write-Optimised DB (Cassandra)
  (LSM-tree, sequential disk writes)
    │
    ▼
Async Read Model Update
(CDC or event stream)
    │
    ▼
Read Model (Search/Analytics)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
Identify workload type
    │
    ▼
Estimate reads/sec vs writes/sec  ← YOU ARE HERE
    │
    ▼
Choose primary architecture:
  Read-heavy:  cache + read replicas
  Write-heavy: LSM-DB + async processing
  Mixed:       CQRS pattern
    │
    ▼
Design data model for that workload
    │
    ▼
Select technology stack
```

**FAILURE PATH:**
Wrong classification → wrong technology → performance degradation at scale → expensive migration. A write-heavy system built on B-tree DB with caching has no escape valve when write throughput exceeds B-tree insert capacity.

**WHAT CHANGES AT SCALE:**
At scale, even a 90:10 read/write ratio means the write path can be a bottleneck if absolute write volume is high. At 100M DAU with 10% writing = 100 writes/day = 115 writes/sec average. This is fine for PostgreSQL. At 1B DAU = 1,150 writes/sec. Now write optimisation matters even for a read-heavy system.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Read-heavy systems benefit from cache consistency protocols (cache invalidation, TTL management). Write-heavy systems face write amplification in distributed settings (every write must propagate to replicas, requiring careful consistency model selection).

---

### 💻 Code Example

```java
// BAD: Treating a read-heavy system as write-heavy
// Writing through cache on every user profile view
@Service
public class ProfileService {
    public UserProfile getProfile(Long userId) {
        // Reading from primary DB on every read
        // No cache - treating as if writes matter more
        return userRepository.findById(userId)
            .orElseThrow();
    }
}

// GOOD: Read-heavy optimization with cache-aside
@Service
public class ProfileService {
    @Autowired private RedisTemplate cache;
    @Autowired private UserRepository repo;

    public UserProfile getProfile(Long userId) {
        String key = "profile:" + userId;
        // Try cache first (read-heavy: cache is king)
        UserProfile cached = cache.opsForValue()
            .get(key);
        if (cached != null) return cached;

        UserProfile profile = repo.findById(userId)
            .orElseThrow();
        // Cache for 10 minutes (read-heavy: TTL fine)
        cache.opsForValue()
            .set(key, profile, Duration.ofMinutes(10));
        return profile;
    }

    public void updateProfile(UserProfile p) {
        repo.save(p);
        // Invalidate cache on write (keep it fresh)
        cache.delete("profile:" + p.getId());
    }
}
```

**How to test / verify correctness:**
- Cache effectiveness: load test with repeated reads for same IDs; cache hit rate should be > 80%.
- Write path: confirm writes complete within SLO without cache interaction slowing them down.
- Consistency: update a record and verify cache is invalidated and subsequent reads return new data.

---

### ⚖️ Comparison Table

| Ratio | Architecture | DB Type | Cache | Consistency |
|---|---|---|---|---|
| **100:1 (read-heavy)** | CDN + Redis + replicas | B-tree (PostgreSQL) | Aggressive | Eventual OK |
| **10:1 (moderate read)** | Redis + 1-2 replicas | PostgreSQL/MySQL | Moderate | Mixed |
| **1:1 (balanced)** | Write-ahead cache | PostgreSQL | Write-through | Strong |
| **1:10 (write-heavy)** | Write queue + LSM | Cassandra/RocksDB | None on write | Eventual |
| **1:100+ (IoT/logging)** | Append-only log | InfluxDB/Kafka | None | Eventual |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Add Redis cache for any performance problem" | Cache only helps reads. For write-heavy systems, caching adds no value and can slow writes (cache invalidation overhead). |
| "Read replicas solve all scaling" | Read replicas only help read load. Write load all goes to the primary - replicas help reads, not writes. |
| "OLAP queries can run on the production OLTP DB" | Heavy analytical queries block transactional queries. OLAP needs a separate read-optimised store (data warehouse, Redshift). |
| "Read/write ratio is fixed at launch" | Social media posts are write-heavy at creation (few minutes), then read-heavy for years. Design for the dominant lifetime ratio. |
| "More indexes improve both reads and writes" | Indexes speed reads but slow writes - every write must update all indexes. Too many indexes on a write-heavy table is a common anti-pattern. |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Wrong DB for Write-Heavy Workload**
**Symptom:** Write latency degrades as data grows; B-tree index update cost increases with table size.
**Root Cause:** B-tree database chosen for write-heavy workload; index maintenance overhead dominates.
**Diagnostic:**
```sql
-- PostgreSQL: check index bloat
SELECT tablename, indexname,
  pg_size_pretty(pg_relation_size(indexrelid))
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC;
-- High ratio = index bloat from write-heavy workload
```
**Fix:** Migrate to LSM-tree DB or implement write-buffering with periodic batch index updates.
**Prevention:** At design time, test with realistic write patterns at 10x projected volume.

**Mode 2: Cache Misses on Write-Heavy Path**
**Symptom:** Cache hit rate < 10%; cache overhead is net negative (invalidation > hit savings).
**Root Cause:** Write-heavy data changes too frequently for cached values to be useful.
**Diagnostic:**
```bash
redis-cli info stats | grep keyspace
# Look for keyspace_hits vs keyspace_misses ratio
# < 80% hit rate for a "cached" system = wrong cache strategy
```
**Fix:** Remove caching from frequently-updated entities. Cache only stable, read-heavy data.
**Prevention:** Before adding a cache, calculate: TTL * write_rate = expected stale fraction. If > 20%, cache is not appropriate.

**Mode 3: Read Replica Lag Causes Stale Reads**
**Symptom:** Users see outdated data immediately after writing - "I just posted but I still see the old post."
**Root Cause:** Read replica lag (replication delay) means reads go to replica before primary change propagates.
**Diagnostic:**
```sql
-- Check replication lag on PostgreSQL
SELECT now() - pg_last_xact_replay_timestamp()
  AS replication_lag;
-- Should be < 5 seconds; if > 30s = problem
```
**Fix:** Route reads to primary for data just written by that user (read-your-writes consistency). Use sticky sessions or session tokens with replica lag awareness.
**Prevention:** Design consistency model explicitly: eventual consistency is acceptable for most data; read-your-writes is the minimum required for user-facing writes.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-003 - How to Approach Any System Design Problem]] - Read/write classification is part of Phase 1
- [[SYD-004 - Estimation and Back-of-Envelope Thinking]] - Estimate read/write ratio at Phase 2

**Builds On This (learn these next):**
- [[SYD-034 - Denormalization for Scale]] - Read-heavy optimization technique
- [[SYD-035 - Fan-Out on Write vs Read]] - Core trade-off in write-heavy social systems

**Alternatives / Comparisons:**
- [[SYD-007 - Horizontal Scaling]] - The scaling response based on read/write diagnosis

---

### 📌 Quick Reference Card

```
╔══════════════════════════════════════════╗
║ WHAT IT IS    Primary workload            ║
║               classification for system   ║
║               architecture decisions      ║
╠══════════════════════════════════════════╣
║ PROBLEM       Wrong architecture for      ║
║ IT SOLVES     workload type causes        ║
║               poor scaling                ║
╠══════════════════════════════════════════╣
║ KEY INSIGHT   Identify read/write ratio   ║
║               before choosing any         ║
║               technology                  ╠══════════════════════════════════════════╣
║ READ-HEAVY    Cache + read replicas +     ║
║               denormalization             ║
╠══════════════════════════════════════════╣
║ WRITE-HEAVY   LSM-DB + async processing   ║
║               + separate read model       ║
╠══════════════════════════════════════════╣
║ TRADE-OFF     Read opt → stale data risk; ║
║               write opt → read complexity ║
╠══════════════════════════════════════════╣
║ ONE-LINER     reads/writes > 10:1 = cache;║
║               < 1:10 = LSM-tree DB        ║
╠══════════════════════════════════════════╣
║ NEXT EXPLORE  SYD-034: Denormalization    ║
╚══════════════════════════════════════════╝
```

**If you remember only 3 things:**
1. Always estimate read/write ratio before choosing a database or adding a cache layer.
2. Caches help reads; read replicas help reads; sharding helps writes - these are not interchangeable.
3. Read/write ratio changes over an entity's lifetime - design for the dominant lifetime phase.

**Interview one-liner:**
"Read/write ratio is the first question I ask in any system design - it determines database choice, caching strategy, replication topology, and whether to use CQRS."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Classify before optimising. You cannot optimise something without knowing what dimension matters most. Read/write ratio is a proxy for a more general principle: identify the dominant constraint of your system before choosing solutions. Guessing and applying a generic "best practices" stack almost always produces a mismatch.

**Where else this pattern appears:**
- **CPU-bound vs I/O-bound processes:** Different profiling, different optimisation (threads vs async).
- **Memory vs disk trade-off in algorithms:** Algorithms optimised for in-memory operation fail when data exceeds RAM; classification changes the entire approach.
- **B2C vs B2B SaaS products:** Read patterns differ drastically - B2C has many users reading frequently; B2B has few users creating complex data.

---

### 💡 The Surprising Truth

The read/write asymmetry in modern systems is far more extreme than most engineers expect. A typical social media application has a read/write ratio of 100:1 to 1000:1 - for every post written, thousands or millions of people read it. This means that for most social applications, the write path is completely irrelevant to performance, and 99.9% of engineering effort on the read path (caching, CDN, read replicas) produces orders of magnitude more user-visible performance improvement than any write optimisation.

---

### 🧠 Think About This Before We Continue

**Q1 (First Principles):** Instagram stores photos that are written once (at upload) and then read millions of times over years. The write path has no special latency requirements. How does this inform every major architecture decision from storage to CDN to database choice?
*Hint:* Trace the implications of "write once, read many" through each layer - explore how S3 + CloudFront replaces a database for the hot path, and how metadata (likes, comments) has a different read/write ratio than the photo itself.

**Q2 (Scale):** At 1M DAU your 100:1 read/write ratio means 10K reads/sec and 100 writes/sec - easily handled. At 100M DAU you have 1M reads/sec and 10K writes/sec. Has the ratio changed? Has the problem changed?
*Hint:* The ratio stayed the same but absolute numbers changed - explore what 10K writes/sec means for PostgreSQL capacity, and at what point the write path (not the read path) becomes the bottleneck even in a read-heavy system.

**Q3 (Design Trade-off):** You are designing an e-commerce inventory system where 10 million users check product availability (read) but stock updates happen 100 times per minute (write). A user sees "In Stock" but by the time they buy, it is sold out. Should you optimise for read accuracy (strong consistency) or read speed (eventual consistency with cache)?
*Hint:* Calculate the probability of a stale read causing a bad purchase vs the latency increase of strong consistency, then look into optimistic locking, compare-and-swap, and how Amazon handles this exact problem.
