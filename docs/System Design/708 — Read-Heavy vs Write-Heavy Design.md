---
layout: default
title: "Read-Heavy vs Write-Heavy Design"
parent: "System Design"
nav_order: 708
permalink: /system-design/read-heavy-vs-write-heavy/
number: "708"
category: System Design
difficulty: ★★★
depends_on: "Caching, Sharding (System), Database Replication"
used_by: "Denormalization for Scale, Fan-Out on Write vs Read, CQRS"
tags: #advanced, #architecture, #database, #performance, #distributed
---

# 708 — Read-Heavy vs Write-Heavy Design

`#advanced` `#architecture` `#database` `#performance` `#distributed`

⚡ TL;DR — **Read-Heavy vs Write-Heavy Design** refers to architecting systems differently based on whether the dominant load is reads or writes — each has distinct bottlenecks, optimisation strategies, and trade-offs.

| #708            | Category: System Design                                   | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------- | :-------------- |
| **Depends on:** | Caching, Sharding (System), Database Replication          |                 |
| **Used by:**    | Denormalization for Scale, Fan-Out on Write vs Read, CQRS |                 |

---

### 📘 Textbook Definition

**Read-Heavy systems** are those where the volume of read (SELECT/GET) operations significantly exceeds write (INSERT/UPDATE/DELETE) operations — typical ratios of 10:1 to 1000:1. **Write-Heavy systems** have write operations dominating, often at near-parity or write-dominant ratios. The architectural choices for each differ fundamentally: read-heavy systems optimise for **read throughput** and **read latency** (caching, read replicas, CDNs, denormalisation, materialised views); write-heavy systems optimise for **write throughput** and **write durability** (write-ahead logging, write batching, LSM-trees, eventual consistency, queue-based ingestion, sharding write paths). Most real systems are read-heavy at the client-facing layer but write-heavy at the data pipeline layer. Characterising the dominant access pattern is the first step in database and infrastructure selection.

---

### 🟢 Simple Definition (Easy)

Read-Heavy: like a library — most people read books, few people write new ones. Optimise for fast checkouts (caching, many reading desks). Write-Heavy: like a live sports scoreboard — constantly updating scores. Optimise for fast score updates (write throughput, no complex joins). The bottleneck is different → the solution is different.

---

### 🔵 Simple Definition (Elaborated)

Wikipedia: 99.9% reads, 0.1% writes. Architecture: aggressive caching (Varnish, CDN), many read replicas, single primary database for rare writes. Twitter timeline: 99% reads. Architecture: pre-computed timeline cache (Redis), fan-out on write to follower caches. Stock exchange: ~50/50 read/write but write latency is critical (microseconds). Architecture: in-memory database (Redis, VoltDB), no disk writes in critical path. Uber's trip ingestion: write-heavy (GPS pings every 5 seconds from 3M active drivers). Architecture: Kafka for write buffering, Cassandra (LSM-tree optimised for writes), batch aggregation.

---

### 🔩 First Principles Explanation

**Architectural patterns for each access pattern:**

```
READ-HEAVY SYSTEM ARCHITECTURE:

  Characteristics:
  - Read:Write ratio > 10:1 (often 100:1 to 1000:1)
  - Common examples: news sites, social media feeds, product catalogues, Wikipedia
  - Bottleneck: read throughput, read latency

  OPTIMISATION 1: CACHING
    Application-level cache (Redis, Memcached):
    - Cache popular reads in memory
    - Cache hit: sub-millisecond response (no DB query)
    - Cache hit rate target: >90% for read-heavy systems

    CDN (for static content):
    - Media, JS, CSS, images cached at edge
    - 95%+ of bytes served from CDN

    Strategy:
    └── Read request → Check Redis (1ms) → Check DB (20ms) → Cache result

    Write path does NOT change for readers: asynchronous invalidation OK.

  OPTIMISATION 2: READ REPLICAS
    Primary DB: handles writes (single instance for consistency)
    Read replicas (3-5): handle all read queries
    Read:Write = 100:1 → 5 read replicas each at 20 reads/write = manageable

    // Spring: read-write routing
    @ReadOnly → routes to read replica
    @Transactional → routes to primary

    Trade-off: replication lag → replicas slightly behind primary (eventual consistency).
    Acceptable for most reads (see "reading from replica" consistency level).

  OPTIMISATION 3: DENORMALIZATION
    Normalised DB: products, categories, manufacturers in separate tables → 3 JOINs per read.
    Denormalised: all product data in one row (redundant but fast reads).

    // Product query (normalised): 3 joins, 20ms
    SELECT p.*, c.name, m.name FROM products p
    JOIN categories c ON p.category_id = c.id
    JOIN manufacturers m ON p.mfr_id = m.id
    WHERE p.id = ?

    // Product query (denormalised): 1 lookup, 2ms
    SELECT * FROM products_denormalized WHERE id = ?

    Cost: write complexity (must update denormalized table when category/manufacturer changes)
    Benefit: 10× read speedup, scales linearly with read replicas

  OPTIMISATION 4: MATERIALISED VIEWS / PRE-COMPUTATION
    Expensive aggregation query: "Top 10 products by revenue this week"
    Running on every request: full table scan on 1M orders → 500ms
    Materialised view: pre-computed and stored, refreshed every 5 minutes.
    Query response: 2ms (single index scan on materialised view)

    Trade-off: data is up to 5 minutes stale (acceptable for dashboards)
    Use case: analytics, leaderboards, aggregation queries

WRITE-HEAVY SYSTEM ARCHITECTURE:

  Characteristics:
  - Write rate: high (1,000+ writes/sec per node)
  - Common examples: IoT telemetry, financial transactions, activity logs, GPS tracking
  - Bottleneck: write throughput, write amplification, lock contention on writes

  OPTIMISATION 1: WRITE-OPTIMISED STORAGE (LSM-Trees)
    B-Tree (traditional RDBMS): random write I/O — slow for high write rates
    LSM-Tree (Cassandra, RocksDB, LevelDB): sequential write I/O — 10-100× faster writes

    LSM-Tree write path:
      Write → MemTable (in-memory buffer) → WAL (durability log) → return ACK
      Background: merge MemTable to SSTable (sequential disk write)
      Read: merge all SSTables + MemTable (more complex than B-Tree reads)

    Write-heavy: LSM-Tree wins. Read-heavy: B-Tree is faster.
    Cassandra: pure LSM → excellent for write-heavy, OK for reads with compaction.
    PostgreSQL: B-Tree → excellent for reads, good writes up to ~10K/sec.

  OPTIMISATION 2: WRITE BUFFERING (Kafka / Message Queues)
    Problem: DB write rate = 100K writes/sec. DB max = 10K writes/sec.
    Solution: Kafka buffer
      Producers → Kafka (100K/sec — Kafka handles this easily)
      Consumers → DB writers (10K/sec — multiple consumers, batched writes)

    Benefit: decouple write spikes from DB throughput limit.
    Trade-off: data not immediately in DB (seconds to minutes lag).
    Use when: write bursts > DB throughput AND eventual consistency OK.

  OPTIMISATION 3: WRITE BATCHING
    Individual writes: 100,000 INSERT statements = 100,000 DB round trips.
    Batched writes: 10 INSERT ... VALUES (...), (...), ... = 10 DB round trips.
    Throughput: 10× improvement. Latency per individual write: slightly higher.

    // JDBC batch insert:
    PreparedStatement ps = conn.prepareStatement("INSERT INTO events VALUES (?,?,?)");
    for (Event e : events) {
      ps.setLong(1, e.id);
      ps.setString(2, e.type);
      ps.setLong(3, e.timestamp);
      ps.addBatch();
      if (++count % 1000 == 0) ps.executeBatch(); // batch every 1000
    }
    ps.executeBatch(); // final batch

  OPTIMISATION 4: ASYNC WRITES + EVENTUAL CONSISTENCY
    Synchronous write: wait for DB ACK → 20ms per write → 50 writes/sec/thread.
    Async write: fire and forget → 1ms (just queue submission) → 1000 writes/sec/thread.

    // Write-heavy: async write to Redis + background persistence to DB
    redisTemplate.opsForValue().set(key, value);  // async: 0.1ms
    kafkaTemplate.send("db-writes", key, value);  // async: 0.1ms
    return;  // don't wait for DB write (it happens eventually)

    Risk: if crash between Redis write and DB write → data loss.
    Acceptable for: analytics, logs, metrics (loss of some data OK).
    Not acceptable for: financial transactions, user account data.

MIXED WORKLOADS: CQRS (Command Query Responsibility Segregation)

  Many systems: heavy reads in user-facing path, heavy writes in data pipeline.
  CQRS: separate read model (optimised for reads) from write model (optimised for writes).

  Write path: normalised DB (OLTP) → fast writes, data integrity
  Read path: denormalised read store (Elasticsearch, Redis, materialised views) → fast reads
  Sync: event-driven (write → publish event → update read store)

  Example:
    User posts tweet → write to MySQL (primary tweet store, write-optimised)
    Event: "tweet_created" published to Kafka
    Consumer: updates Elasticsearch index (for search reads)
    Consumer: updates Redis timeline cache (for home feed reads)
    Consumer: fan-out to follower caches (for follower feeds)

  Result: reads served from pre-optimised read stores (fast).
          writes go to simple primary store (clean, consistent).
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT read/write pattern analysis:

- Apply same architecture to all systems → wrong optimisations
- Read-heavy system with no cache → database overwhelmed by reads
- Write-heavy system with complex relational DB → write lock contention → backpressure

WITH read/write pattern analysis:
→ Read-heavy: cache aggressively, add read replicas, denormalise
→ Write-heavy: LSM-tree storage, batching, async queues
→ Right tool for the right job: orders of magnitude better performance

---

### 🧠 Mental Model / Analogy

> Library (read-heavy): hundreds of readers, one librarian who occasionally adds new books. Solution: many reading tables, fast catalogue search, books pre-sorted on shelves. vs. Post office (write-heavy): thousands of parcels arriving per hour, processed immediately. Solution: fast sorting conveyor (write queue), temporary staging shelves (write buffer), no time for perfect organisation — sort quickly, find later.

"Library" = read-heavy system (news site, Wikipedia, product catalogue)
"Many reading tables" = read replicas, caching (serve many concurrent readers)
"Post office conveyor" = write-heavy system (Kafka, LSM-tree database)
"Fast sorting, no perfection" = write throughput over read organisation (eventual consistency OK)
"Library catalogue" = materialised view / denormalised index (precomputed for fast reads)

---

### ⚙️ How It Works (Mechanism)

**System characterisation and architecture decision:**

```
STEP 1: MEASURE READ:WRITE RATIO

  DB slow query log + application metrics:

  # PostgreSQL: check read vs write statement ratio
  SELECT
    schemaname, tablename,
    seq_scan + idx_scan AS total_reads,
    n_tup_ins + n_tup_upd + n_tup_del AS total_writes,
    ROUND(
      (seq_scan + idx_scan)::numeric /
      NULLIF(n_tup_ins + n_tup_upd + n_tup_del, 0), 1
    ) AS read_write_ratio
  FROM pg_stat_user_tables
  ORDER BY read_write_ratio DESC;

STEP 2: IDENTIFY BOTTLENECK

  Read-heavy signals:
  - DB CPU: dominated by SELECT statements
  - Cache miss rate: high (>10% misses on hot data)
  - DB replica lag: reads overwhelming replica(s)
  - Read latency: p99 > 100ms on simple queries

  Write-heavy signals:
  - DB CPU: dominated by INSERT/UPDATE
  - Write queue: growing backlog of uncommitted writes
  - Replication lag: primary write throughput exceeds replica apply speed
  - Lock contention: high pg_locks / InnoDB lock waits

STEP 3: APPLY APPROPRIATE OPTIMISATIONS (decision matrix)

  ┌─────────────────────────────────────────────────────┐
  │ Problem              │ Read-Heavy  │ Write-Heavy    │
  ├──────────────────────┼─────────────┼────────────────┤
  │ Throughput           │ Read replicas│ Kafka, sharding│
  │ Latency              │ Caching     │ Async writes   │
  │ Storage engine       │ B-Tree      │ LSM-Tree       │
  │ Data model           │ Denormalize │ Normalise      │
  │ Query pattern        │ Materialised│ Append-only    │
  │ Consistency          │ Stale OK    │ Eventual OK    │
  │ Failure mode         │ Stale read  │ Write backlog  │
  └─────────────────────────────────────────────────────┘
```

---

### 🔄 How It Connects (Mini-Map)

```
System requirements (access pattern analysis)
        │
        ▼
Read-Heavy vs Write-Heavy ◄──── (you are here)
        │
        ├── READ-HEAVY → Caching, Read Replicas, Denormalization
        ├── WRITE-HEAVY → Kafka, LSM-Tree, Async, Batching
        └── MIXED → CQRS, Fan-Out on Write vs Read
```

---

### 💻 Code Example

**Spring Boot: read/write routing with primary + read replica:**

```java
@Configuration
public class DataSourceConfig {

    @Bean
    @Primary
    @ConfigurationProperties("spring.datasource.primary")
    public DataSource primaryDataSource() {
        return DataSourceBuilder.create().build();
    }

    @Bean
    @ConfigurationProperties("spring.datasource.replica")
    public DataSource replicaDataSource() {
        return DataSourceBuilder.create().build();
    }

    @Bean
    public DataSource routingDataSource(
            @Qualifier("primaryDataSource") DataSource primary,
            @Qualifier("replicaDataSource") DataSource replica) {

        AbstractRoutingDataSource router = new AbstractRoutingDataSource() {
            @Override
            protected Object determineCurrentLookupKey() {
                // Route to replica for read-only transactions:
                return TransactionSynchronizationManager.isCurrentTransactionReadOnly()
                    ? "replica" : "primary";
            }
        };
        router.setDefaultTargetDataSource(primary);
        router.setTargetDataSources(Map.of("primary", primary, "replica", replica));
        return router;
    }
}

// Read (routes to replica):
@Transactional(readOnly = true)
public List<Product> findAllProducts() {
    return productRepository.findAll();
}

// Write (routes to primary):
@Transactional
public Product createProduct(Product product) {
    return productRepository.save(product);
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                                                                                                                                                                                                                                              |
| --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Adding more replicas solves all read scalability problems | Read replicas help with throughput but replication lag grows with write rate. A heavily write-loaded primary can lag replicas by seconds to minutes — replicas become stale. Heavy write + heavy read systems need CQRS with separate data stores, not just more replicas                                            |
| Write-heavy systems need less caching                     | Write-heavy systems still have significant read load (often reads track writes: "show me what I just wrote"). Read-through caches on write-heavy systems prevent read load from further stressing the write-loaded primary. The cache write policy (write-through vs write-behind) matters                           |
| Read:Write ratio is fixed at system design time           | Access patterns change over time. A startup may launch with equal reads and writes; after viral growth, reads may dominate 1000:1. Capacity planning must re-evaluate read:write ratio quarterly. Architecture built for write-heavy may need caching/replica additions as the system matures                        |
| Denormalization only benefits read-heavy systems          | Write-heavy systems also benefit from denormalization when writes are batch-insert patterns (analytics ingestion). Writing a flat denormalized row is faster than normalised multi-table writes with foreign key constraints. The "normalise for writes" advice is specifically for high-contention update workloads |

---

### 🔥 Pitfalls in Production

**Read replica used for writes (accidental routing bug):**

```
PROBLEM: Application accidentally writes to read replica

  Bug: @Transactional annotation missing on write method.
  Result: Spring routes write request to read replica (readOnly=true default).

  Read replica: rejects write (PostgreSQL read replica: ERROR: cannot execute INSERT in a read-only transaction)

  OR worse: Some DBs don't reject (eventual sync issues):
    Write goes to replica → replication overrides with primary state → data lost.

CORRECT PATTERN:

  // WRONG — no @Transactional → might route to replica:
  public User createUser(User user) {
    return userRepository.save(user);  // might go to replica!
  }

  // CORRECT — explicit @Transactional → always routes to primary:
  @Transactional
  public User createUser(User user) {
    return userRepository.save(user);  // always primary
  }

  // CORRECT — read — explicitly read-only:
  @Transactional(readOnly = true)
  public User findUser(Long id) {
    return userRepository.findById(id).orElseThrow();
  }

MONITORING: Alert on writes to read replica:
  Track: replica write errors (rate > 0 → routing bug)
  Alert: any INSERT/UPDATE/DELETE on replica → PagerDuty alert.
```

---

### 🔗 Related Keywords

- `Caching` — primary optimisation for read-heavy systems
- `Denormalization for Scale` — data model strategy for read-heavy workloads
- `Fan-Out on Write vs Read` — key architectural choice in social/feed systems
- `CQRS` — separates read and write models for mixed workloads
- `Sharding (System)` — primary write throughput scaling for write-heavy systems

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Read-heavy → cache/replicas/denormalize;  │
│              │ write-heavy → queue/batch/LSM-tree        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Choosing DB engine; scaling architecture; │
│              │ diagnosing DB performance bottlenecks     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Same architecture for both patterns;      │
│              │ read replicas for write-heavy write path  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Library vs post office — different       │
│              │  bottlenecks, different solutions."       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Denormalization → Fan-Out on Write vs Read│
│              │ → CQRS                                    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You're designing a product review system for an e-commerce site: 10M products, each getting ~5 reviews per day (writes) but ~5,000 views per day (reads). Read:Write ratio = 1000:1. Design the read path and write path separately: what does the read path look like? What caching strategy? What does the write path look like? What happens to the read cache when a new review is submitted? How do you handle the eventual consistency window between a user submitting their review and seeing it appear?

**Q2.** You're building an IoT platform ingesting sensor data from 10 million devices, each sending 1 reading every 10 seconds (1M writes/second total). Users query "last 24 hours of readings for sensor X" frequently, but also "average temperature across all sensors in region Y for the last hour" (aggregation across millions of rows). Classify this system: what is the read:write ratio? What database engine(s) would you choose and why? How would you handle both the high write throughput and the complex aggregation query patterns?
