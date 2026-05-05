---
layout: default
title: "Sharding (System)"
parent: "System Design"
nav_order: 706
permalink: /system-design/sharding-system/
number: "0706"
category: System Design
difficulty: ★★★
depends_on: Database Partitioning, Distributed Systems, Consistent Hashing
used_by: Scalable Databases, Large-Scale Systems
related: Partitioning, Consistent Hashing, Hot Shard
tags:
  - database
  - scaling
  - advanced
  - distributed
  - partitioning
---

# 706 — Sharding (System)

⚡ TL;DR — Horizontal database partitioning by shard key. Data split across multiple independent database instances. Each shard handles subset of data. Enables scaling reads/writes beyond single-instance limits.

| #706            | Category: System Design                     | Difficulty: ★★★ |
| :-------------- | :------------------------------------------ | :-------------- |
| **Depends on:** | Database Partitioning, Consistent Hashing   |                 |
| **Used by:**    | Scalable Databases, Large-Scale Systems     |                 |
| **Related:**    | Partitioning, Consistent Hashing, Hot Shard |                 |

---

### 🔥 The Problem This Solves

**ISSUE:**
Single database can't scale writes. 1M users × 1000 writes/day = 1B writes/day. Single DB: 10M writes/sec max. Overloaded.

**SOLUTION:**
Split across 100 shards. Each shard: 10M writes/day. All shards: 1B writes/day. ✓

---

### 📘 Textbook Definition

**Sharding:** Horizontal database partitioning technique where data is split across multiple independent database instances (shards) based on a shard key. Each shard owns exclusive subset of data, enabling linear scalability for both reads and writes.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Users 0-100K → Shard A. Users 100K-200K → Shard B. Each shard independent. Scales linearly.

**One analogy:**

> Library books: all books in one building (overloaded). Split across 10 branches. Each handles local queries. Scales linearly with branches.

**One insight:**
Sharding trades consistency/complexity for horizontal scale.

---

### 🔩 First Principles

**SHARDING STRATEGIES:**

1. **Range-based**: user_id 0-1M → shard A, 1M-2M → shard B
   - Pros: simple, no rebalancing on add
   - Cons: hot shards if ranges uneven

2. **Hash-based**: hash(user_id) % num_shards → shard index
   - Pros: even distribution, fewer hot shards
   - Cons: rebalancing hard on shard addition

3. **Consistent Hashing**: hash(user_id) on ring → nearest shard
   - Pros: minimal rebalancing on shard add/remove
   - Cons: complex, uneven if shard sizes vary

4. **Directory-based**: metadata table maps key → shard
   - Pros: flexible, rebalancing easy
   - Cons: metadata lookup overhead, bottleneck risk

**TRADE-OFFS:**

**Gain:** Linear scale. Bypass single-instance limits.

**Cost:** Complexity (routing, rebalancing). Joins across shards hard. Transactions limited to single shard.

---

### 🧪 Thought Experiment

**SETUP:**
Social network. 100M users. Each user average 1KB. Total: 100GB.

**Single DB:**

- Storage: 100GB on 1 DB ✓
- Write QPS: 100M users × 1 write/day = 1.16M/day ≈ 13 writes/sec ✓
- But: 1M users online → 1M concurrent reads. Single DB: 10K concurrent max ✗

**10 Shards:**

- Storage: 10GB per shard ✓
- Write QPS: 13 writes/sec per shard ✓
- Concurrent reads: 100K per shard (1M / 10) ✓
- Scales!

---

### ⚙️ How It Works

```
Sharding Architecture:
──────────────────────

[Client Request] → [Router/Coordinator]
                        ↓
                    hash(user_id) = 42
                    42 % 10 shards = 2
                        ↓
                   [Shard 2 DB]
                   (users 2M-2.1M)
                        ↓
                  [Response to client]

Hash-based routing:
  user_id 123456
  hash(123456) = 0x7A4B2C
  0x7A4B2C % 10 = 2
  → Route to Shard 2

Consistent hashing (with rebalancing):
  Add Shard 11
  Ring: [S1, S2, ..., S10, S11, ...]

  Affected: users between S10 and S11 migrate
  Unaffected: rest stay put
  Migration: ~10% of data (1 shard out of 10)
```

---

### 💻 Code Example

```python
class ShardRouter:
    def __init__(self, num_shards):
        self.num_shards = num_shards
        self.shard_dbs = [f"shard_{i}" for i in range(num_shards)]

    def get_shard(self, user_id):
        """Route user to shard"""
        shard_id = hash(user_id) % self.num_shards
        return self.shard_dbs[shard_id]

    def write(self, user_id, data):
        shard = self.get_shard(user_id)
        # Write to correct shard DB
        print(f"Writing user {user_id} to {shard}")

    def read(self, user_id):
        shard = self.get_shard(user_id)
        # Read from correct shard DB
        print(f"Reading user {user_id} from {shard}")

# Usage
router = ShardRouter(num_shards=10)

# All requests for user 123 go to same shard
router.write(123, {'name': 'Alice'})
router.read(123)

# User 456 might go to different shard
router.write(456, {'name': 'Bob'})
```

---

### ⚠️ Common Misconceptions

| Misconception                 | Reality                                              |
| ----------------------------- | ---------------------------------------------------- |
| "Sharding = replication"      | No. Sharding = split. Replication = copy. Different. |
| "Sharding solves all scaling" | No. Cross-shard joins/transactions still hard.       |

---

### 🚨 Failure Modes

**Failure Mode 1: Hot Shard**
(Covered separately as keyword #707)

**Failure Mode 2: Uneven Shard Distribution**

**Symptom:**
Range-based sharding. First shard (0-1K) has power users. Last shard (9K-10K) has inactive users. First shard overloaded.

**Prevention:**
Hash-based or consistent hashing for even distribution. Monitor shard load.

---

### 📌 Quick Reference

```
Sharding:
  What: split data across multiple DBs
  Why: scale beyond single-instance limits
  How: route by shard_key to correct DB
  Cost: complexity, cross-shard operations hard
```

---

### 🧠 Questions

**Q1.** You shard by user_id % 10. Now you need 20 shards. How do you migrate without downtime?

**Q2.** Cross-shard transaction (transfer credit from user A to B, different shards). How?
