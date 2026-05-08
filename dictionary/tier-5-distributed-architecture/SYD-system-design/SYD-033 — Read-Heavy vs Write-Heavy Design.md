---
layout: default
title: "Read-Heavy vs Write-Heavy Design"
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 33
permalink: /system-design/read-heavy-vs-write-heavy-design/
id: SYD-033
category: System Design
difficulty: ★★★
depends_on: Database Design, Scaling Patterns, Caching
used_by: System Architecture, Database Optimization
related: Caching, Replication, Denormalization
tags:
  - architecture
  - database
  - advanced
  - scaling
  - optimization
---

# SYD-033 — Read-Heavy vs Write-Heavy Design

⚡ TL;DR — Different systems require different optimizations. Read-heavy (100:1 read:write ratio): prioritize caching, replicas, denormalization. Write-heavy (1:10 write:read): optimize writes, batch inserts, write-ahead logging.

| #708            | Category: System Design                    | Difficulty: ★★★ |
| :-------------- | :----------------------------------------- | :-------------- |
| **Depends on:** | Database Design, Scaling Patterns, Caching |                 |
| **Used by:**    | System Architecture, Database Optimization |                 |
| **Related:**    | Caching, Replication, Denormalization      |                 |

---

### 🔥 The Problem This Solves

**ISSUE:**
One-size-fits-all DB design fails. Twitter (read-heavy): needs cache. Kafka (write-heavy): needs sequential write optimization.

**SOLUTION:**
Tailor design to access pattern.

---

### 📘 Textbook Definition

**Read-Heavy vs Write-Heavy Design:** Design philosophy optimizing for dominant access pattern. Read-heavy systems prioritize read latency/throughput (cache, replicas, denormalization). Write-heavy systems prioritize write throughput (batch, sharding, WAL).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Twitter = 1000 reads per 1 write. Optimize for reads: cache, replicas. Kafka = 1000 writes per 1 read. Optimize for writes: sequential disk, batching.

**One analogy:**

> Library: (1) mostly reading books (read-heavy): buy more copies, multiple branches. (2) mostly writing articles (write-heavy): optimize printing press, batching.

**One insight:**
Access pattern drives architecture.

---

### 🧠 Mental Model

```
Read-Heavy Design:
  User reads 100x for every write
  Priority: Fast reads
  Strategies:
    - Replicas (read from nearest)
    - Cache (Redis, Memcached)
    - Denormalization (pre-compute results)
    - Materialized views
  Trade: Writes slower (replicate to all)

Write-Heavy Design:
  User writes 100x for every read
  Priority: Fast writes
  Strategies:
    - Sequential writes (disk optimized)
    - Batch inserts (group 1000x writes)
    - Write-ahead logging (durability, not latency)
    - Sharding by write key
  Trade: Reads slower (eventual consistency, aggregation)
```

---

### 📶 Gradual Depth

**Level 1:** Twitter = read-heavy. Kafka = write-heavy. Different needs.

**Level 2:** Read-heavy: cache reads, replicate writes. Write-heavy: batch writes, accept stale reads.

**Level 3:** Metrics: read/write ratio. >100:1 = read-heavy; <1:100 = write-heavy. Design accordingly.

**Level 4:** Read-heavy emerged from observational patterns (social media, search). Write-heavy from message queues, time-series DBs. Facebook: read-heavy (News Feed = reads). Kafka: write-heavy (event ingestion = writes). Design choices: read-heavy uses cache (Memcached at scale 1000x); write-heavy uses WAL + batch (Kafka brokers with sequential disk).

---

### ⚙️ How It Works

```
READ-HEAVY SYSTEM (Social Media)
────────────────────────────────
Example: Twitter. 100 million followers read feed, 1M tweet per minute.

Reads: 100M * 10 feed loads/day = 1B reads/day
Writes: 1M tweets/min = 1.44B tweets/day
Ratio: 1000:1 (reads:writes)

Optimization:
  Cache: Hot tweets cached (Redis)
  Replicas: Feed in multiple DBs
  Denorm: Pre-compute top tweets (sorted)
  Timeline push: When user tweets, push to follower caches

Write flow: Tweet → DB → fanout to 100M followers' caches (slow)
Read flow: User → Cache → instant

WRITE-HEAVY SYSTEM (Message Queue)
──────────────────────────────────
Example: Kafka. Producers write logs at scale.

Writes: 1M messages/sec into Kafka
Reads: Consumers process 100K messages/sec
Ratio: 1:10 (reads:writes, heavily skewed toward writes)

Optimization:
  Sequential writes: Append-only log (disk-optimal)
  Batch: Group 1000 writes per disk block
  Sharding: Partition topics by producer
  WAL: Durability via log (not indexing)

Write flow: Message → append to log → flush batch → ack
Read flow: Consumer → scan log → aggregate (eventual consistency)

HYBRID (Balanced)
─────────────────
Read/write ratio ~1:1 (balanced)
  - OLTP: Normal operations
  - Cache useful but not critical
  - Replica coordination easier
  - Design: normalized DB + opportunistic cache
```

---

### 💻 Code Example

```python
class DatabaseOptimizer:
    def __init__(self, read_count, write_count):
        self.read_count = read_count
        self.write_count = write_count
        self.ratio = read_count / write_count if write_count > 0 else float('inf')

    def get_recommendation(self):
        if self.ratio > 100:
            return "READ-HEAVY"
        elif self.ratio < 0.01:
            return "WRITE-HEAVY"
        else:
            return "BALANCED"

    def optimize_read_heavy(self):
        return {
            'cache_strategy': 'Aggressive (LRU, TTL: 1h)',
            'replication': 'Read replicas (3+)',
            'denormalization': 'Pre-compute aggregates',
            'indexing': 'Multiple indexes for read patterns',
            'write_strategy': 'Fanout on write (eventual consistency)',
        }

    def optimize_write_heavy(self):
        return {
            'cache_strategy': 'Minimal (write-through only)',
            'replication': 'Async replication (fanout on read)',
            'batching': 'Batch 1000+ writes per flush',
            'indexing': 'Minimal (slow down writes)',
            'write_strategy': 'Append-only log (sequential disk)',
        }

# Usage
twitter_pattern = DatabaseOptimizer(read_count=1_000_000, write_count=10_000)
print(f"Twitter pattern: {twitter_pattern.get_recommendation()}")
print(f"Ratio: {twitter_pattern.ratio:.0f}:1")
print(f"Strategy: {twitter_pattern.optimize_read_heavy()}")

kafka_pattern = DatabaseOptimizer(read_count=100_000, write_count=1_000_000)
print(f"\nKafka pattern: {kafka_pattern.get_recommendation()}")
print(f"Ratio: 1:{1/kafka_pattern.ratio:.0f}")
print(f"Strategy: {kafka_pattern.optimize_write_heavy()}")
```

---

### ⚠️ Common Misconceptions

| Misconception                     | Reality                                              |
| --------------------------------- | ---------------------------------------------------- |
| "Cache always good"               | No. Bad for write-heavy (invalidation overhead).     |
| "Denormalization = always faster" | No. Slower for write-heavy (update multiple tables). |

---

### 🚨 Failure Modes

**Failure Mode: Wrong Pattern Assumption**

**Symptom:**
Assumed read-heavy. Actual write-heavy. Cache miss-hit due to high write rate.

**Prevention:**
Measure actual ratio. Re-evaluate quarterly.

---

### 📌 Quick Reference

```
Design by Access Pattern:

Read-Heavy (>100:1):
  Use: Cache, replicas, denormalization
  Avoid: Complex writes, validation

Write-Heavy (<1:100):
  Use: Batching, sequential disk, sharding
  Avoid: Caching, complex reads

Balanced (~1:1):
  Use: Normal DB design, selective caching
```

---

### 🧠 Questions

**Q1.** Product: 90% reads, 10% writes. Is caching worth the complexity?

**Q2.** You have write-heavy system. Customers want real-time reads. How?
