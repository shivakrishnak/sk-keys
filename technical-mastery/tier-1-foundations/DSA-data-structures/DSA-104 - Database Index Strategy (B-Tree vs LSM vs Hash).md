---
id: DSA-104
title: "Database Index Strategy (B-Tree vs LSM vs Hash)"
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★★★
depends_on: DSA-055, DSA-081, DSA-012
used_by: DSA-103, DSA-107
related: DSA-055, DSA-081
tags:
  - database
  - indexing
  - b-tree
  - lsm-tree
  - hash-index
  - storage-engine
  - mysql
  - rocksdb
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 104
permalink: /technical-mastery/dsa/database-index-strategy/
---

## TL;DR

Database index choice determines read/write trade-offs:
B+ Tree (MySQL InnoDB, balanced read/write, range queries),
LSM Tree (Cassandra, RocksDB, write-optimized), Hash
Index (Redis, O(1) exact match, no range support).

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-104 |
| **Difficulty** | ★★★ Expert |
| **Category** | Data Structures & Algorithms |
| **Tags** | database, indexing, B-Tree, LSM Tree, hash index |
| **Prerequisites** | DSA-055, DSA-081, DSA-012 |

---

### The Three Index Families

**B+ Tree (balanced, read/write balanced):**

```
Structure: balanced tree with sorted data in leaf nodes
           leaf nodes linked for range scans
Reads:     O(log n) exact match, O(log n + k) range
Writes:    O(log n) with in-place updates
Range:     Excellent (linked leaf scan)
Used by:   MySQL InnoDB, PostgreSQL, Oracle, SQLite

Height for 100M rows (page size 16KB, 200 keys/page):
  Level 1 (root): 200 keys
  Level 2: 200^2 = 40,000 keys
  Level 3: 200^3 = 8M keys
  Level 4: 200^4 = 1.6B keys
  Height: 3-4 levels = 3-4 I/Os for any lookup in 100M rows

Write amplification (worst case):
  Random inserts cause page splits (rebalancing)
  Write amplification: ~10-20x for random workloads
```

**LSM Tree (write-optimized):**

```
Structure: in-memory MemTable + disk SSTables
           periodic compaction merges SSTables
Reads:     O(log n) with Bloom filter pre-check
Writes:    O(1) to MemTable (in-memory), O(1) to WAL
Range:     Good (SSTables are sorted, merged at read)
Used by:   Cassandra, RocksDB, LevelDB, HBase

Write amplification:
  Compaction rewrites data multiple times
  Write amplification: 10-30x total (acceptable for writes)

Read amplification:
  Without Bloom filter: check each SSTable
  With Bloom filter: 1 disk read for 99% of queries
  Read amplification: 1-3x (worse than B-Tree)
```

**Hash Index (fastest exact lookup):**

```
Structure: hash map (key → value or key → disk offset)
Reads:     O(1) exact match only
Writes:    O(1) append to log + update hash map
Range:     Not supported
Used by:   Redis (HASH type), Bitcask (Riak), memcached

Constraint: must fit in memory (no on-disk hash table
            efficient for range queries)
Best for:  in-memory key-value stores with known key set
```

---

### Decision Framework

```java
// When to choose each index type:

// 1. B+ Tree: default choice for relational data
//    - Mix of reads and writes
//    - Range queries required
//    - Predictable performance
//    - OLTP workloads
// Example: MySQL InnoDB for e-commerce order storage

// 2. LSM Tree: write-heavy workloads
//    - High write throughput (millions/sec)
//    - Reads acceptable at O(log n) with Bloom filter
//    - Time-series, event log, audit trail
// Example: Cassandra for IoT sensor data
//          RocksDB as embedded store in Kafka

// 3. Hash Index: extreme read performance
//    - Exact key lookup only (no range)
//    - Dataset fits in memory
//    - Simple key-value pairs
// Example: Redis for session store, rate limiting

// 4. Combined approach (most production systems):
//    Primary store: B+ Tree (PostgreSQL)
//    Cache layer: Redis Hash (frequently accessed rows)
//    Bloom filter: pre-screen cache misses
//    LSM Tree: append-only audit log (RocksDB)
```

---

### Write Amplification Comparison

```
Write amplification = bytes written to disk
                    / bytes written by application

B+ Tree (random inserts):
  1KB record → page split → 2x16KB pages rewritten
  Write amplification: ~10x
  InnoDB: write-ahead log (WAL) reduces amplification

LSM Tree:
  Write to MemTable: ~1x (fast)
  L0 → L1 compaction: ~10x
  L1 → L2 compaction: ~10x
  Total: ~10-30x depending on compaction strategy
  BUT: writes are sequential → much faster at disk level

Hash Index (append-only log + in-memory hash):
  1x write to log
  Compact when log > threshold (rewrite live entries)
  Effective amplification: ~2-3x
```

---

### Comparison Table

| Property | B+ Tree | LSM Tree | Hash Index |
|---------|--------|---------|-----------|
| Read (exact) | O(log n) | O(log n) + Bloom | O(1) |
| Read (range) | O(log n + k) | O(log n + k) | Not supported |
| Write | O(log n) | O(1) to memory | O(1) |
| Space | 1-2x | 1.1-2x (compaction) | 1x (in-memory) |
| Crash safety | WAL | WAL + MemTable | Depends on impl |
| Write amplification | 10-20x | 10-30x | 2-3x |
| Read amplification | 1-2x | 1-5x | 1x |
| Best workload | Mixed OLTP | Write-heavy | Exact lookup only |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "LSM Trees are always faster than B-Trees" | LSM Trees are faster for sequential WRITES. B-Trees are faster for random READS and range scans. The right choice depends on your read:write ratio |
| "Hash indexes are better than B-Trees because O(1) vs O(log n)" | For 1M rows, B-Tree height = 3 disk I/Os. Hash index = 1 disk I/O. The practical difference is 3x, but hash index doesn't support range queries. B-Tree wins for mixed workloads |

---

### Mastery Checklist

- [ ] Knows which index type backs MySQL InnoDB vs Cassandra vs Redis
- [ ] Can explain write amplification for LSM vs B-Tree
- [ ] Chooses index strategy based on read/write ratio and query pattern

---

### The Surprising Truth

Facebook uses RocksDB (LSM Tree) for their social graph
storage - one of the highest-read-throughput databases
in the world, typically considered a write-optimized
structure. Why? Facebook's social graph has billions
of edges, and Bloom filters in RocksDB make 99% of
reads a single disk I/O. The write throughput is also
excellent. The key insight: "LSM = write-optimized"
is a simplification. With good Bloom filter coverage,
LSM reads are competitive with B-Trees for exact lookups.
