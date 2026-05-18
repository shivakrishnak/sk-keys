---
version: 2
layout: default
title: "Data Locality"
parent: "NoSQL & Distributed Databases"
grand_parent: "Technical Mastery"
nav_order: 42
permalink: /technical-mastery/nosql/data-locality/
id: NDB-043
category: NoSQL & Distributed Databases
difficulty: ★★★
depends_on: Distributed Systems, Sharding, Partitioning
used_by: System Design, Distributed Systems, Caching
related: Sharding, Hot Partition Problem, Caching
tags:
  - nosql
  - data-locality
  - partitioning
  - performance
  - deep-dive
---

⚡ TL;DR - Data locality means placing data close to where it is accessed: **close in time** (recently used data in fast cache - L1 cache, Redis), **close in space** (data on the same network node as the computation that processes it - Hadoop's "move computation, not data"), and **close geographically** (user data in the same region as the servers that serve that user); all three reduce latency by eliminating costly data movement.

| #475            | Category: NoSQL & Distributed Databases     | Difficulty: ★★★ |
| :-------------- | :------------------------------------------ | :-------------- |
| **Depends on:** | Distributed Systems, Sharding, Partitioning |                 |
| **Used by:**    | System Design, Distributed Systems, Caching |                 |
| **Related:**    | Sharding, Hot Partition Problem, Caching    |                 |

---

### 🔥 The Problem This Solves

**MOVING DATA IS EXPENSIVE:**
In computing, speed is determined by where data lives relative to where computation happens. Accessing data in CPU registers takes ~0.5ns. L1 cache: 1ns. RAM: 100ns. SSD: 100μs. Network (same datacenter): 500μs. Network (cross-region): 100ms. When computation and data are distant, every operation pays the cost of data movement - a 200× to 200,000× overhead compared to local access.

**DISTRIBUTED SYSTEMS COMPOUND THE PROBLEM:**
In a distributed database, a query may need data from 3 different shards on 3 different servers. Without locality-aware design, every query triggers cross-node network reads, adding 2-10ms of latency per hop. At 10,000 QPS, 2ms of unnecessary network overhead = 20,000ms of total wasted time per second. Designing for data locality eliminates the cross-node reads by ensuring data that is queried together is stored together.

---

### 📘 Textbook Definition

**Data Locality** is the principle of co-locating data with the computation that processes it (or in hardware, with the CPU that accesses it) to minimize the cost and latency of data movement. Three dimensions: **Temporal locality** - recently accessed data is likely to be accessed again soon; exploited by CPU caches (L1/L2/L3), application-level caches (Redis), page caches (OS). **Spatial locality** - data near recently accessed data is likely to be accessed soon; exploited by CPU cache lines (64 bytes loaded together), sequential disk reads (read-ahead), database pages, and row-vs-column storage layouts. **Geographic/Network locality** - data should be stored on the same server or cluster as the service that queries it; exploited by database sharding (partition user data to the region closest to that user), co-location of microservices with their databases, and CDNs (cache content close to users). In distributed databases: **partition key locality** - designing the partition key so that all data for a user, session, or entity is stored in the same partition, eliminating cross-partition reads. In Hadoop/Spark: **compute locality** - the processing engine moves the computation (task) to the node that holds the data, rather than moving the data to a central compute node ("move the code, not the data").

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Data locality = keep data close to what uses it - same CPU cache, same database node, same cloud region - because moving data costs time.

**One analogy:**

> A chef works in their kitchen with ingredients on the counter (L1 cache: immediate access). More ingredients are in the fridge (L2/L3 cache: fast but one step). If a special ingredient isn't in the kitchen, a sous chef fetches it from the storeroom (RAM: slower). If the ingredient must be ordered from a supplier across town (network: much slower). If it must be imported from another country (cross-region: slowest). Data locality is designing the kitchen so the most-used ingredients are on the counter, not across town.

- "Ingredients on the counter" → L1 cache (CPU registers, ~0.5ns)
- "Fridge" → L2/L3 CPU cache (~5-10ns)
- "Storeroom" → RAM (~100ns)
- "Supplier across town" → local network / same datacenter (~500μs)
- "Imported from another country" → cross-region data transfer (~100ms)
- "Design the kitchen" → data locality optimization (partition key, shard design)

**One insight:**
Data locality manifests differently at each level of the stack, but the principle is identical: access patterns determine where data should live. At the CPU level, the compiler and hardware automatically optimize for spatial and temporal locality. At the application level, you choose where to put data: Redis vs. database, which shard/partition, which region. The design question is always: "Where will this data be accessed from, and how can I ensure it lives there?" The answer drives partition key choice (same-user data on same shard), CDN design (assets in the region with most users), and cache warm-up strategy (pre-populate cache with frequently accessed data).

---

### 🔩 First Principles Explanation

**CPU CACHE HIERARCHY:**

```
Memory Hierarchy - Access Times:
┌─────────────────────────────────────────────────────────┐
│ Location            │ Latency   │ Size      │ Who manage│
├─────────────────────┼───────────┼───────────┼───────────┤
│ CPU Registers       │ ~0.5ns    │ 32 × 64b  │ Compiler  │
│ L1 Cache (per core) │ ~1ns      │ 32-64KB   │ CPU HW    │
│ L2 Cache (per core) │ ~5ns      │ 256KB-1MB │ CPU HW    │
│ L3 Cache (shared)   │ ~20ns     │ 8-64MB    │ CPU HW    │
│ RAM (DRAM)          │ ~100ns    │ 16-256GB  │ OS+HW     │
│ NVMe SSD            │ ~100μs    │ 1-8TB     │ OS (page) │
│ HDD                 │ ~5-10ms   │ 1-20TB    │ OS (page) │
│ Local Network       │ ~500μs    │ ∞ (remote)│ App design│
│ Cross-Region        │ ~100ms    │ ∞ (remote)│ App design│
└─────────────────────────────────────────────────────────┘

Cache line: 64 bytes loaded atomically
  → spatial locality: access array[0], array[1] is already
    in L1 cache

Cache miss example:
  Random access pattern (linked list traversal, HashMap
    with collisions):
  → each pointer dereference may be a cache miss (~100ns
    each)
  → 1 million pointer dereferences: 100ms (if all cache
    misses)

  Sequential access pattern (array traversal, ArrayList):
  → spatial locality: prefetcher loads next 64 bytes ahead
  → effectively no cache misses after first access per
    64-byte chunk
  → 1 million sequential reads: ~1ms (100× faster)

NUMA (Non-Uniform Memory Access):
  Multi-socket servers have NUMA topology:
  - CPU0 has local RAM (NUMA node 0): ~100ns access
  - CPU0 accessing RAM on NUMA node 1 (CPU1's RAM):
    ~200-300ns access

  NUMA misalignment: a process pinned to CPU0 with its
    memory allocated on NUMA node 1
  → all memory accesses cross NUMA boundary → 2-3× slower
    than optimal

  Fix: numactl --cpunodebind=0 --membind=0 ./myapp
  Database best practice: pin PostgreSQL/Redis processes
    to one NUMA node
  Redis recommendation: redis.conf → always set bind to
    interface on same NUMA node
  PostgreSQL: Linux huge pages + NUMA binding for
    shared_buffers
```

**DATABASE PARTITION KEY LOCALITY:**

```
Scenario: Multi-tenant SaaS application
Table: user_events(tenant_id, user_id, event_type,
  created_at, payload)

BAD partition key design (no locality):
  Partition key: event_id (UUID, random)
  → 100 events for tenant A, user 42 → distributed across
    100 random shards
  → Query: "all events for user 42 in the last 7 days"
  → Requires scatter-gather: query all N shards, aggregate
    results
  → Latency: N × single-shard latency (e.g., 10 shards ×
    5ms = 50ms)

GOOD partition key design (locality):
  Partition key: (tenant_id, user_id)
  → All events for tenant A, user 42 → same shard
  → Query: "all events for user 42 in the last 7 days"
  → Single shard read (one network hop)
  → Latency: 1 × 5ms = 5ms (10× faster)

  DynamoDB: PK = tenant_id#user_id, SK = created_at
    (ISO8601 for range queries)
  Cassandra: partition key = (tenant_id, user_id),
    clustering key = created_at DESC

GEOGRAPHIC LOCALITY:
  EU users' data → EU region shards (Frankfurt/Ireland)
  US users' data → US region shards (us-east-1/us-west-2)
  APAC users' data → APAC region shards
    (ap-southeast-1/ap-northeast-1)

  CockroachDB/Spanner: table locality pins can colocate
    rows in specific regions
  -- CockroachDB:
  ALTER TABLE user_events CONFIGURE ZONE USING
    constraints='[+region=eu-west]'
    WHERE tenant_region = 'EU';

  Benefit: EU user query hits EU region → no
    cross-Atlantic network hop (100ms savings)
  GDPR benefit: EU user data stays in EU region
    (regulatory compliance)
```

**HADOOP/SPARK COMPUTE LOCALITY:**

```
Hadoop MapReduce data locality:
  HDFS stores data blocks on DataNodes (distributed across
    the cluster)

  Without locality:
  Data block → DataNode A
  MapTask → assigned to Node B
  → Node B must fetch block from Node A (network I/O,
    ~10ms/block, GB scale)
  → For 1TB of input: significant network bottleneck

  With locality (default Hadoop behavior):
  YARN ResourceManager: assigns MapTask to Node A (where
    block is stored)
  → MapTask reads data from local disk (no network,
    ~100μs/block)
  → "Move the computation to the data"
  → 100× faster than moving data to computation

  Locality levels (in priority order):
  1. NODE_LOCAL: task runs on node that has the data (best)
  2. RACK_LOCAL: task runs on node in same rack (same
    switch, low latency)
  3. OFF_SWITCH: task runs anywhere (data must cross
    switches - avoid)

  Monitor: Hadoop Job UI → "Map input records" by locality
    level
  Alert: if OFF_SWITCH% > 5%, cluster may be imbalanced

Spark:
  spark.locality.wait = 3s  # wait up to 3s for a local
    task slot before relaxing
  spark.locality.wait.node = 3s
  spark.locality.wait.rack = 2s
  spark.locality.wait.any = 1s

  Broadcast joins (data locality optimization):
  Large table (100GB) JOIN small table (1MB):
  Instead of shuffling the large table (expensive network)
  → broadcast small table to all executors (1MB × N nodes
    = small)
  → each executor joins locally (no shuffle needed)
  → Spark automatically broadcasts tables <
    spark.sql.autoBroadcastJoinThreshold (10MB default)
```

**CACHE LOCALITY PATTERNS:**

```java
// TEMPORAL LOCALITY: Redis cache for frequently accessed data
@Service
public class ProductService {

    @Cacheable(value = "products", key = "#productId",
               unless = "#result == null")
    public Product getProduct(String productId) {
        // Redis hit: ~1ms | DB miss: ~20ms
        return productRepository.findById(productId).orElse(null);
    }

    // LOCALITY INSIGHT: cache key design matters
    // BAD: cache key = random UUID → no spatial locality, random
    // eviction
    // GOOD: cache key = category:productId → related products share
    // key prefix
    // → Redis scan("electronics:*") gets all electronics without
    // scanning all keys
}

// SPATIAL LOCALITY: fetch related data together (avoid N+1)
@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {

    // BAD: N+1 → 1 query for orders + N queries for each order's
    // items
    // Each query is a separate network round trip to PostgreSQL

    // GOOD: JOIN FETCH → single query, all data in one network round
    // trip
    @Query("SELECT o FROM Order o JOIN FETCH o.items WHERE o.customerId = :customerId")
    List<Order> findOrdersWithItemsByCustomerId(@Param(
        "customerId") Long customerId);

    // Locality benefit: single round trip vs. N+1 trips
    // For N=100 orders: 1 query vs 101 queries = 100× fewer network
    // round trips
}
```

---

### 🧪 Thought Experiment

**WHAT IF YOU DESIGNED CASSANDRA PARTITIONING WITHOUT LOCALITY?**

A healthcare app stores patient vitals: `patient_id, timestamp, heart_rate, blood_pressure`.

**Design A (no locality):** Partition key = `timestamp` (or `date`). All vitals for all patients on a given day → same partition. A doctor queries patient 42's vitals for the last 30 days → must read 30 partitions (one per day), each potentially on a different node, each needing a full partition scan with a filter on `patient_id`. Scatter-gather across 30 nodes. Each partition has millions of rows (all patients' vitals for that day) - range query requires ALLOW FILTERING or a secondary index. Performance: terrible.

**Design B (locality):** Partition key = `patient_id`. All vitals for patient 42 → same partition, same node. Doctor queries patient 42's last 30 days → single node, single partition scan with clustering column (`timestamp DESC`) - no filtering needed. O(results) instead of O(all patients' data). The design choice: put the partition key on the entity whose data is always accessed together (`patient_id`), not on a time value that spreads data randomly.

---

### 🧠 Mental Model / Analogy

> Data locality is like office desk organization. Papers you use every hour are on your desk (L1 cache). Papers used daily are in your drawer (L2 cache). Papers used monthly are in the filing cabinet (RAM). Last year's papers are in the archive room (SSD). Documents from other offices require a trip or a call (network). The ideal setup: organize your desk so the exact papers you need for today's project are in front of you - grouped together, not scattered across drawers. That's partition key design: group the data you query together, in the same "drawer" (partition/shard).

- "Papers on the desk" → L1 CPU cache / Redis hot keys
- "Drawer" → L2/L3 cache / warm partition
- "Filing cabinet" → RAM / local SSD
- "Archive room" → remote disk (network I/O)
- "Documents from other offices" → cross-node reads / cross-region queries
- "Organize desk for today's project" → partition key design for co-located access

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Data locality = fast access = no data movement. L1 cache (nanoseconds) → RAM (microseconds) → network (milliseconds) → cross-region (100ms). Design databases and caches so data you query together lives together. The partition key determines data locality in distributed databases.

**Level 2:** Apply locality thinking to: (1) DynamoDB PK design - same PK means same partition, same node; (2) Cassandra partition key - all rows with same partition key on same 3-node replica set; (3) Redis key naming - use namespaced keys (`user:42:profile`) to group related data; (4) Elasticsearch routing key - route a document to a specific shard to co-locate documents queried together; (5) CDN design - cache static assets at the PoP (Point of Presence) closest to users. Monitor cross-shard reads - they indicate locality problems.

**Level 3:** NUMA-aware deployment: bind Redis and PostgreSQL processes to a single NUMA node to avoid remote NUMA memory accesses. Use `numactl --hardware` to inspect NUMA topology. `numastat` to measure NUMA hit/miss rates. Linux huge pages for database buffer pools (reduces TLB misses - a form of address-translation locality). Spark executor placement: use `spark.executor.extraJavaOptions=-XX:+UseNUMA` to enable NUMA-aware JVM memory allocation. For DynamoDB: use same-region Lambda → DynamoDB to avoid cross-region latency; use DAX (DynamoDB Accelerator) in the same AZ as the Lambda to add sub-millisecond caching. Cassandra vnodes: `num_tokens = 1` with explicit token assignment (vs. default 256 vnodes) to improve data locality by ensuring a single contiguous token range per node instead of 256 scattered ranges.

**Level 4:** The fundamental insight behind all data locality optimizations is the same: the cost of computation grows linearly with distance from the data. At the hardware level, the memory hierarchy (registers → L1 → L2 → L3 → RAM → SSD → network) is a manifestation of physical distance - closer storage is faster but smaller. System architects and hardware designers both exploit temporal and spatial locality by predicting future access patterns from past behavior (CPU prefetcher, OS read-ahead, Redis LRU eviction). Database designers exploit it explicitly through partition key design, denormalization (co-locate related data in one document or row instead of across joins), and data replication (replicate hot data to all regions that query it). The Shared Nothing architecture of distributed databases (each node owns a partition, no shared disk, no cross-node locks) is fundamentally a locality architecture: route each query to the single node that owns the relevant partition, and the majority of queries need zero cross-node communication. The CAP theorem tension (network partition → either consistency or availability degrades) is another manifestation of locality: partition tolerance means accepting that some data will be geographically separated from its consumers at times, and the system must decide how to handle that separation.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ DATA LOCALITY LEVELS IN A WEB APPLICATION            │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Request: GET /users/42/orders                        │
│                                                      │
│ Level 1 - CPU cache (1-20ns):                        │
│   JVM JIT-compiled bytecode in I-cache               │
│   User object in L3 cache (recent access)            │
│   → Zero action needed (hardware manages)            │
│                                                      │
│ Level 2 - Application cache (1-5ms):                 │
│   Redis: GET user:42:orders → cache hit              │
│   [LOCALITY ← YOU ARE HERE: temporal locality]       │
│   → Return immediately, no DB query                  │
│   If miss → DB query, SET user:42:orders (TTL=300s)  │
│                                                      │
│ Level 3 - Database partition locality (1-10ms):      │
│   DynamoDB: PK=USER#42, SK begins_with ORDER#        │
│   → Single partition, single node → fast             │
│   If partition key = random hash: scatter-gather     │
│   → 10 shards × 5ms = 50ms vs 1 × 5ms = 5ms        │
│                                                      │
│ Level 4 - Geographic locality (0-100ms savings):     │
│   User 42 is in Frankfurt → EU shard (eu-west-1)     │
│   App server → EU DB: ~10ms                          │
│   Without locality: App server (EU) → US DB: ~100ms  │
│   Savings: 90ms per request                          │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**MULTI-REGION APPLICATION WITH DATA LOCALITY:**

```
User: Alice in Frankfurt → GET /api/v1/profile
CDN: CloudFront EU PoP → cache hit for /static assets
  (geographic locality ✓)
→ API request: forwarded to eu-west-1 (API Gateway +
  Lambda in EU)

Lambda (eu-west-1):
→ [DATA LOCALITY ← YOU ARE HERE: check cache first]
→ Redis (ElastiCache eu-west-1, same AZ as Lambda): GET
  profile:alice123
→ Cache HIT (temporal locality ✓): return in 1ms, skip DB
  entirely

If cache miss:
→ DynamoDB DAX (eu-west-1): GET PK=USER#alice123
→ DAX HIT (us-east-1 DynamoDB would be 100ms cross-region;
  eu DAX = 1ms) ✓

If DAX miss:
→ DynamoDB Global Table (eu-west-1 replica)
→ Alice's data is replicated to eu-west-1 (geo locality ✓)
→ Query hits EU replica: 10ms (not us-east-1: 100ms)
→ DynamoDB PK = USER#alice123 → single partition
  (partition locality ✓)
→ Returns profile

Comparative latencies:
  Optimized (all locality): 1ms (Redis hit)
  Semi-optimized (DAX hit): 5ms
  DB hit (EU replica): 10-15ms
  No locality (US primary): 100-120ms

Partition key ensures Alice's profile, orders, preferences
  all on same shard:
  PK = USER#alice123 → SK = PROFILE | ORDER#2024-001 |
    PREF#theme
  All Alice's data: same partition, same node, same AZ →
    zero cross-node reads
```

---

### ⚖️ Comparison Table

| Locality Type        | Level          | Mechanism                       | Latency Saved        | Who Manages               |
| -------------------- | -------------- | ------------------------------- | -------------------- | ------------------------- |
| Temporal (CPU)       | Hardware       | L1/L2/L3 cache, TLB             | 50-200ns per access  | CPU hardware              |
| Spatial (CPU)        | Hardware       | 64-byte cache lines, prefetcher | 50-200ns per access  | CPU hardware + compiler   |
| NUMA                 | Hardware + OS  | NUMA node memory binding        | 100-200ns per access | OS + ops config           |
| Application cache    | App layer      | Redis / Memcached               | 5-50ms per request   | Developer                 |
| Partition key design | Database       | Shard co-location               | 5-50ms per query     | Developer (schema design) |
| Geographic           | Infrastructure | Multi-region, CDN               | 50-200ms per request | Architect + ops           |
| Compute (Hadoop)     | Compute layer  | YARN task scheduling            | GB-scale I/O avoided | Framework automatic       |

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                                                                                                                         |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Data locality only matters at the database layer"    | Data locality matters at every layer: CPU cache lines (array vs. linked list), NUMA topology, OS page cache, application-level caches, database partitioning, and geographic CDNs. Each layer has 10x-1000x latency differences                 |
| "More shards = better locality"                       | More shards improve parallelism but hurt locality if the partition key is poorly designed. 1,000 shards with random partition key = 1,000-way scatter-gather for every query. Fewer shards with locality-aware keys can outperform              |
| "Caching solves locality problems"                    | Caching adds temporal locality for hot data but doesn't fix spatial locality at the database level. A poorly partitioned database still causes scatter-gather for cache misses, which occur for cold data and after cache eviction              |
| "Geographic locality is only for global applications" | Even single-region applications benefit from AZ locality: a Lambda in us-east-1a querying a database in us-east-1b adds ~1ms per query. At 10,000 QPS, that's 10,000ms/second of avoidable overhead. Same-AZ deployment is free and significant |

---

### 🚨 Failure Modes & Diagnosis

**1. Cross-Partition Scatter-Gather (Hidden Locality Bug)**

**Symptom:** DynamoDB `SELECT * WHERE user_id = 42` has p99 latency of 80ms despite small data size. CloudWatch: `ConsumedReadCapacityUnits` is 10× expected. `ReturnedItemCount` is normal (50 items).

**Root Cause:** Partition key is `status` (e.g., `ACTIVE`, `PENDING`) - low-cardinality, causing hot partitions AND requiring a full scan of the partition to find user 42's items. The query has no partition key targeting - it's a full scan. DynamoDB must check all partitions.

**Diagnosis:**

```bash
# DynamoDB: check if query uses partition key
aws dynamodb query --table-name orders \
  --key-condition-expression "pk = :pk" \
  --expression-attribute-values '{":pk":{"S":"USER#42"}}'
# ConsumedCapacityUnits should be proportional to result count
# If it's 100x result count → full scan or wrong partition key

# Check if using scan instead of query
# aws dynamodb scan = full table read (never use in production for
# targeted lookups)

# DynamoDB Contributor Insights: identify hot partitions
aws dynamodb describe-contributor-insights \
  --table-name orders \
  --status ENABLED
# Lists most read/written partition keys → locality analysis
```

**Fix:**

```
Redesign partition key for locality:
  BAD: PK = status (low cardinality, all users' orders
    mixed)
  GOOD: PK = USER#42 (all user 42's orders in one
    partition)

  Migration: create new table with correct PK, backfill
    via DynamoDB Streams + Lambda
  Blue/green: write to both tables during migration, cut
    over reads to new table

  Rule: partition key should be the entity whose data is
    always accessed together
```

---

### 🔗 Related Keywords

**Prerequisites:** Distributed Systems, Sharding, Partitioning

**Builds On This:** System Design, Distributed Systems

**Related:** Sharding, Hot Partition Problem, Caching

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ TEMPORAL    │ Recently used → fast cache (Redis, L1)    │
│ SPATIAL     │ Nearby data → prefetch together (arrays)  │
│ GEOGRAPHIC  │ User data → user's region (CDN, geo shard)│
│ PARTITION   │ Same-entity data → same partition key     │
│ NUMA        │ Bind DB process to single NUMA node       │
│ HADOOP      │ Move tasks to data, not data to tasks     │
│ DETECT      │ Scatter-gather = locality failure         │
│ MONITOR     │ DynamoDB Contributor Insights; Spark UI   │
│ ONE-LINER   │ "Keep data where it will be accessed -    │
│             │  same cache, same node, same region"      │
│ NEXT EXPLORE│ Caching → Hot Partition Problem           │
└─────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C - Design Question) Design a DynamoDB table for a multi-tenant SaaS project management tool. Entities: Workspace (1M workspaces), Project (10M projects, avg 10 per workspace), Task (100M tasks, avg 10 per project), Comment (500M comments, avg 5 per task). Access patterns: (a) get all projects in a workspace, (b) get all tasks in a project, (c) get all comments for a task, (d) get all tasks assigned to a user (across all workspaces). Design the single-table schema with partition key, sort key, and GSIs. Explain which access patterns have data locality and which require a GSI (with the locality tradeoff).

**Q2.** (TYPE D - Failure Scenario) A Spark job processes 2TB of log data daily. After a cluster resize (from 10 nodes to 50 nodes), the job takes 3× longer than before. Spark UI shows: 90% of tasks are `OFF_SWITCH` locality, vs. 5% before the resize. Explain: (a) why did the resize cause this? (b) what does `OFF_SWITCH` locality mean in practice for performance? (c) what are two configuration changes to fix it? (d) what is the tradeoff of each fix?
