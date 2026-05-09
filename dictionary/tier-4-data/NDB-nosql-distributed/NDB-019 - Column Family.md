---
version: 1
layout: default
title: "Column Family"
parent: "NoSQL & Distributed Databases"
grand_parent: "Technical Dictionary"
nav_order: 19
permalink: /nosql/column-family/
id: NDB-019
category: NoSQL & Distributed Databases
difficulty: ★★★
depends_on: Key-Value Store, LSM Tree, Distributed Systems
used_by: Cassandra Data Modeling, Wide Column vs Document, Time-Series DB
related: Cassandra Data Modeling, Wide Column vs Document, DynamoDB Patterns
tags:
  - nosql
  - column-family
  - cassandra
  - wide-column
  - deep-dive
---

# NDB-019 - Column Family

⚡ TL;DR - A column-family (wide-column) store organizes data by row key + column key rather than fixed columns - each row can have a different set of columns, columns are stored together on disk by family, enabling highly efficient writes and range scans on sorted keys, at the cost of ad hoc querying.

| #453            | Category: NoSQL & Distributed Databases                             | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------ | :-------------- |
| **Depends on:** | Key-Value Store, LSM Tree, Distributed Systems                      |                 |
| **Used by:**    | Cassandra Data Modeling, Wide Column vs Document, Time-Series DB    |                 |
| **Related:**    | Cassandra Data Modeling, Wide Column vs Document, DynamoDB Patterns |                 |

---

### 🔥 The Problem This Solves

**TIME-SERIES DATA IN RELATIONAL DB:**
Sensor readings: device_id, timestamp, temperature, humidity, pressure. 1 billion rows. Relational table with standard B-tree index: range query "all readings for device X from 2024-01-01 to 2024-01-31" = B-tree traversal across random pages. Poor locality. Slow.

**THE COLUMN-FAMILY MODEL:**
Model device_id as the partition key and timestamp as the clustering key. All readings for device X are physically sorted together on disk by timestamp. Range queries are sequential disk reads. Write throughput is massive (LSM-tree append). No random writes. This is exactly what Cassandra, HBase, and BigTable were built for.

---

### 📘 Textbook Definition

A **column-family store** (also called **wide-column store**) is a NoSQL database model where data is organized by (row key, column key) pairs rather than fixed relational columns. Each row can have a different set of columns. Columns are grouped into **column families** - groups of related columns stored together on disk. Rows within a partition are physically **sorted** by the column key, enabling efficient range scans. The data model is inspired by Google BigTable. Leading implementations: **Apache Cassandra** (distributed, leaderless, AP), **Apache HBase** (consistent, CP, runs on HDFS), **Google Bigtable** (managed, BigTable original), **Azure Table Storage** (cloud-managed). The storage engine is typically **LSM-tree** (Log-Structured Merge tree), optimizing for write throughput. Queries must be designed around the partition and clustering key structure - ad hoc secondary queries are expensive.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Column-family stores are sorted, partition-keyed maps where each row's columns are stored together on disk - ideal for write-heavy time-series and entity-attribute data, but queries must match the sort order.

**One analogy:**

> A library's index-card system. Each subject (partition key) has a drawer of index cards (rows). Within the drawer, cards are sorted alphabetically by title (clustering key). Finding all cards for "Physics" between "Quantum" and "Radiation": just open the Physics drawer and flip to the Q section - sequential and fast. Finding "all cards mentioning Einstein across ALL subjects": you must open every drawer in the library (full table scan) - slow.

- "Subject drawer" → partition (data co-located for one partition key)
- "Cards sorted by title within drawer" → rows sorted by clustering key
- "Open Physics drawer → Q to R" → partition key lookup + clustering key range scan
- "Open every drawer" → scatter-gather across all partitions (full scan = bad)
- "Index card has different fields" → rows in a partition can have different columns

**One insight:**
In Cassandra, queries drive schema design - not normalization. You design your tables around the queries you need to answer. Each query pattern usually requires a dedicated table (or materialized view). This is the opposite of relational design, where you normalize first and let the query optimizer figure out access patterns.

---

### 🔩 First Principles Explanation

**CASSANDRA DATA MODEL:**

```
Table structure:
  PRIMARY KEY (partition_key, clustering_col1, clustering_col2, ...)

  partition_key:   determines which node stores this row (hash ring)
  clustering_cols: sort order within the partition (sorted on disk)

Physical storage within a partition:
  All rows with the same partition_key are stored TOGETHER on the same node(s)
  Within that partition, rows are sorted by clustering key
  This makes range scans on clustering keys sequential reads = FAST
```

**EXAMPLE: IoT SENSOR READINGS:**

```sql
-- Cassandra CQL (looks like SQL but has very different semantics)
CREATE TABLE sensor_readings (
  device_id UUID,          -- partition key: all readings for this device together
  recorded_at TIMESTAMP,   -- clustering key: sorted by time within device
  temperature DOUBLE,
  humidity    DOUBLE,
  pressure    DOUBLE,
  PRIMARY KEY (device_id, recorded_at)
) WITH CLUSTERING ORDER BY (recorded_at DESC);  -- latest first

-- Efficient queries (use partition key):
SELECT * FROM sensor_readings
WHERE device_id = ? AND recorded_at > ? AND recorded_at < ?;
-- → goes to one node; sequential read of sorted partition; FAST

-- ILLEGAL in Cassandra (no partition key = full scan):
SELECT * FROM sensor_readings WHERE temperature > 25;
-- Cassandra will reject this (requires ALLOW FILTERING → dangerous in prod)
```

**COLUMN FAMILIES (physical storage):**

```
Column family = group of columns stored together on disk
In Cassandra/HBase, a table = one column family
Multiple column families = multiple tables (Cassandra best practice)
Different column families → different compression, TTL, bloom filter settings

COLUMN FAMILY FOR USER EVENTS:
Partition key: user_id
Clustering key: event_time DESC, event_id
Columns: event_type, properties (map<text,text>)

Physical layout on disk (SSTable):
  [user:42] → [(event_time=2024-01-15T14:00, event_id=abc), (event_type=login, properties={...})]
              [(event_time=2024-01-15T13:55, event_id=def), (event_type=purchase, properties={...})]
              [(event_time=2024-01-14T09:00, event_id=ghi), (event_type=view, properties={...})]
  [user:43] → ...  (physically on different node if different partition hash)
```

**CASSANDRA WRITE PATH (LSM-based):**

```
1. Write arrives
2. Written to CommitLog (WAL for durability/crash recovery)
3. Written to MemTable (in-memory sorted structure; fast)
4. When MemTable full → flush to SSTable on disk (immutable file)
5. Periodic compaction: multiple SSTables merged → one (GC tombstones, deduplication)

Result: writes are ALWAYS sequential (CommitLog + MemTable → SSTable)
        No random writes = no disk seek = massive write throughput
        Reads: MemTable + Bloom filter + SSTable(s) → read amplification
```

**HBASE vs CASSANDRA:**

```
HBase:
  - Consistent (CP in CAP): uses ZooKeeper for coordination; single master (HMaster)
  - Strongly consistent reads/writes
  - HDFS for storage: fault tolerance via HDFS replication
  - Use when: you need strong consistency AND wide-column model (e.g., HBase for Hadoop ecosystem)
  - Tradeoff: single master = write bottleneck; ZooKeeper = operational complexity

Cassandra:
  - Available (AP in CAP): leaderless ring; any node accepts reads/writes
  - Tunable consistency: ONE / QUORUM / ALL (per operation)
  - QUORUM reads + QUORUM writes → effectively strong consistency (but still no master)
  - Replication factor configurable (typically 3 = 3 copies per row)
  - Use when: high write throughput; geographic distribution; no SPOF tolerance
```

---

### 🧪 Thought Experiment

**CASSANDRA PARTITION KEY DESIGN: UNBOUNDED PARTITIONS**

Time-series table, sharded by day:

```sql
PRIMARY KEY ((device_id, date), recorded_at)
-- date = '2024-01-15' (YYYY-MM-DD)
```

Device X on 2024-01-15: every second = 86,400 rows/day.
Five years of data = 1,825 days × 86,400 rows = 157,680,000 rows in ONE partition.

**CASSANDRA PARTITION SIZE LIMIT:**
Cassandra documentation: partitions > 100MB cause read latency issues, OOM errors, and compaction problems. 157M rows = many GBs. **PARTITION TOO LARGE PROBLEM.**

**FIX: bucket the time:**

```sql
PRIMARY KEY ((device_id, bucket), recorded_at)
-- bucket = floor(unix_timestamp / 3600)  (1 hour buckets)
-- One partition = 3,600 rows (1 second resolution, 1 hour window)
-- Even after 5 years: each bucket has exactly 3,600 rows ✓

-- Query: last 2 hours of data for device X:
-- Must query 2 buckets: current and previous hour
-- Small number of buckets = acceptable
```

This "time bucketing" is a fundamental Cassandra pattern. Partition keys should produce partitions bounded in size. Unbounded partitions are one of the top Cassandra anti-patterns in production.

---

### 🧠 Mental Model / Analogy

> Imagine a multi-story file room where each floor is a partition (identified by a master key, like device ID). Within each floor, papers are arranged in strict date order in filing cabinets. Grabbing all papers from floor 7 between January 1 and January 31: go to floor 7, walk to the January section, pull papers in order. Fast. But "find all papers mentioning 'temperature > 25' across all floors": you must visit every floor in the building - slow, and the building might have millions of floors.

- "Floor number" → partition key (device_id)
- "Papers in date order" → rows sorted by clustering key (recorded_at)
- "Grab January papers from floor 7" → partition key + clustering key range query
- "Visit every floor" → ALLOW FILTERING / full scan (catastrophically slow in Cassandra)

---

### 📶 Gradual Depth - Four Levels

**Level 1:** A column-family store (like Cassandra) organizes data by a "partition key" (which determines which server stores it) and a "clustering key" (which sorts rows within that partition). Within each partition, data is physically sorted and stored together - so range queries within a partition are fast. But queries without the partition key touch all servers (slow).

**Level 2:** Design tables around your query access patterns. For each query you need: create a table (or materialized view) whose primary key satisfies that query. Use compound partition keys `(user_id, month)` to prevent unbounded partition growth. Avoid ALLOW FILTERING in production - it signals a query that doesn't match the table design. Set TTLs on time-series data to control disk usage (Cassandra writes tombstones on delete; too many tombstones → read performance degradation).

**Level 3:** Cassandra's consistency model: write to N nodes (replication factor 3 means 3 copies). Consistency level QUORUM = majority (2 of 3 must ACK). `QUORUM writes + QUORUM reads` = always overlap at least 1 node with latest data → linearizable reads (approximately). Under network partition: Cassandra (AP) continues accepting writes to available nodes; repair sync after partition heals (read-repair, anti-entropy repair). Hinted handoff: if a replica is temporarily down, another node stores the write as a "hint" and delivers it when the replica recovers. Tombstone accumulation: deletes in Cassandra are written as tombstones (with a `gc_grace_seconds` TTL, default 10 days). Until `gc_grace_seconds` passes, tombstones exist on disk and are scanned during reads. High tombstone density (from frequent deletes) → massive read latency. Solution: set appropriate TTLs instead of deletes for time-series data; use `gc_grace_seconds=0` only when you're sure all nodes have received the delete.

**Level 4:** The column-family model is a direct descendant of Google's Bigtable paper (2006). Bigtable's insight: the relational model imposes structure on data that many applications don't need. The map-of-maps model - `row_key → (column_key → (timestamp → value))` - is more flexible and maps more naturally to distributed storage. The sorted order within partitions is the key structural insight: because data is physically sorted, range queries become sequential disk reads (O(1) disk seeks for the whole range). This is fundamentally different from a B-tree index scan, which touches random pages. The tradeoff: you can only efficiently sort by one key structure (the clustering key). If you need a different sort order or a different query predicate: you need a different table (denormalized copy). Cassandra's design forces this at the data model level - it's not a limitation to work around but the fundamental design philosophy: storage is cheap; normalization is expensive in a distributed system. Duplicate your data in as many access-pattern-specific tables as you need.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ CASSANDRA PHYSICAL STORAGE (SSTABLE)                 │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Partition: device_id = "sensor-42"                   │
│ (stored on Node 3 based on consistent hash)          │
│                                                      │
│ SSTable on disk (sorted):                            │
│  [sensor-42] → recorded_at=2024-01-31T23:59:59 → {temp:25.1, hum:60}  │
│             → recorded_at=2024-01-31T23:59:58 → {temp:25.0, hum:60}  │
│             → ...                                    │
│             → recorded_at=2024-01-01T00:00:01 → {temp:22.0, hum:55}  │
│                                                      │
│ Query: sensor-42, last 1 hour:                       │
│   1. Bloom filter: is sensor-42 in this SSTable?     │
│   2. Partition index: find offset of sensor-42       │
│   3. Sequential read from offset to end-of-range     │
│   → All sequential I/O: fast                        │
│                                                      │
│ Compaction: multiple SSTables merged periodically    │
│   → Remove tombstones older than gc_grace_seconds    │
│   → Merge duplicate updates, keep latest             │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

**TIME-SERIES WRITE + READ:**

```
IoT device sends reading every second
→ API receives {device_id, temperature, humidity, recorded_at}
→ Cassandra INSERT INTO sensor_readings (device_id, recorded_at, temperature, humidity)
  VALUES (?, ?, ?, ?)
→ [COLUMN FAMILY ← YOU ARE HERE: partition write]
→ Hash(device_id) → Node 3 primary for this partition
→ Write to CommitLog (sync) + MemTable (in-memory)
→ Replicate to 2 other nodes (RF=3): Node 1, Node 7
→ ACK to API after QUORUM (2 nodes) confirms

Dashboard reads last 24h for device X:
→ SELECT * FROM sensor_readings WHERE device_id=?
  AND recorded_at > now()-24h ORDER BY recorded_at DESC
→ Route to any node (Cassandra coordinator)
→ Node looks up: which nodes own sensor-X partition?
→ Fetch from 1 (QUORUM=1 sufficient for this query)
→ Sequential read of ~86,400 rows
→ Return to dashboard
```

---

### ⚖️ Comparison Table

| Feature               | Column Family (Cassandra)     | Document (MongoDB)     | Relational (PostgreSQL)   |
| --------------------- | ----------------------------- | ---------------------- | ------------------------- |
| Data model            | Row + column key (sorted)     | Flexible JSON document | Fixed schema rows         |
| Write throughput      | Very high (LSM, append-only)  | High                   | Moderate (B-tree, WAL)    |
| Range scan efficiency | Excellent (within partition)  | Good (with index)      | Good (with index)         |
| Ad hoc queries        | Poor (partition key required) | Good                   | Excellent                 |
| Consistency           | Tunable (ONE to ALL)          | Strong (single-DC)     | Strong (ACID)             |
| Best for              | Time-series, IoT, write-heavy | Catalogs, profiles     | Transactional, relational |

---

### ⚠️ Common Misconceptions

| Misconception                                      | Reality                                                                                                                                                                                            |
| -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Cassandra is just a distributed SQL database"     | Cassandra's CQL looks like SQL but has fundamental restrictions: no joins, no subqueries, partition key required for most queries. It's optimized for specific access patterns, not ad hoc queries |
| "You can do any query as long as you add an index" | Secondary indexes in Cassandra are node-local - they scatter across all nodes and are expensive. ALLOW FILTERING is even worse. Query patterns must match the primary key design                   |
| "Tombstones are cleaned up immediately"            | Tombstones linger for `gc_grace_seconds` (default 10 days) to ensure all replicas have received the delete before garbage collection. High tombstone density causes read degradation               |
| "Column family = relational column"                | A "column" in column-family refers to a (key, value) pair per row. A "column family" groups related columns together for storage. The terminology is entirely different from relational columns    |

---

### 🚨 Failure Modes & Diagnosis

**1. Unbounded Partition / Large Partition Problem**

**Symptom:** Query latency spikes to seconds for specific partition keys. GC pressure on nodes hosting those partitions. `nodetool tablestats` shows large partition sizes.

**Root Cause:** Partition key has low cardinality or time-unbounded design - all writes go to the same partition indefinitely (e.g., partition key = `year` instead of `year:month:bucket`).

**Diagnostic:**

```bash
nodetool tablestats keyspace.table
# mean_partition_size and max_partition_size
# max >> mean = large partition hotspot

# Cassandra 4.0+: partition size warning in logs
# WARN: Writing large partition sensor_readings:sensor-42 (15 MiB)
```

**Fix:** Redesign the partition key to include a time bucket component. Migrate data to the new schema. Use the expand-contract pattern: new writes to new table, old data served from old table until migrated.

---

### 🔗 Related Keywords

**Prerequisites:** Key-Value Store, LSM Tree, Distributed Systems
**Builds On This:** Cassandra Data Modeling, Wide Column vs Document, Time-Series DB
**Related:** DynamoDB Patterns, Hot Partition Problem

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ MODEL        │ (partition_key, clustering_key) → columns │
│ STORAGE      │ LSM-tree; sorted within partition; append │
│ QUERY RULE   │ Must include partition key; range on clust│
│ ANTI-PATTERN │ Unbounded partition; ALLOW FILTERING;     │
│              │ too many tombstones; ad hoc queries       │
│ CONSISTENCY  │ Tunable: ONE < QUORUM < ALL               │
│ ONE-LINER    │ "Sorted distributed map - design for your │
│              │  query, not for normalization"            │
│ NEXT EXPLORE │ Cassandra Data Modeling → Hot Partition   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C - Design Question) Design a Cassandra schema for a social media notification system: users receive notifications (like, comment, follow, mention). Each user can have thousands of notifications. Requirements: (a) fetch the 20 most recent notifications for user X in < 10ms, (b) mark notifications as read, (c) count unread notifications per user, (d) notifications older than 30 days auto-expire. Design the table(s), primary key, TTL strategy, and note what queries are possible vs. impossible with this schema.

**Q2.** (TYPE F - Comparison Depth) Compare Cassandra vs. HBase on: (a) consistency model (AP vs. CP), (b) write path (both LSM but different coordination), (c) operational model (ZooKeeper dependency vs. leaderless), (d) geographic distribution (multi-DC). For what type of workload would you choose HBase over Cassandra, and vice versa?
