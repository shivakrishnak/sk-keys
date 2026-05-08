---
layout: default
title: "Hot Shard"
parent: "System Design"
nav_order: 32
permalink: /system-design/hot-shard/
id: SYD-032
category: System Design
difficulty: ★★★
depends_on: Sharding, Load Balancing, Monitoring
used_by: Database Scaling, Distributed Systems
related: Sharding, Load Imbalance, Partitioning
tags:
  - sharding
  - failure
  - advanced
  - scaling
  - monitoring
---

# SYD-032 — Hot Shard

⚡ TL;DR — Problem where one shard receives disproportionate load (traffic/data) compared to others. Causes performance degradation, bottleneck. Solution: detect via monitoring, rehash shard key, or split hot shard further.

| #707            | Category: System Design                | Difficulty: ★★★ |
| :-------------- | :------------------------------------- | :-------------- |
| **Depends on:** | Sharding, Load Balancing, Monitoring   |                 |
| **Used by:**    | Database Scaling, Distributed Systems  |                 |
| **Related:**    | Sharding, Load Imbalance, Partitioning |                 |

---

### 🔥 The Problem This Solves

**ISSUE:**
Sharded by user_id. Celebrity user_id gets 1M requests/sec. All others: 100 each. One shard (celebrity) overloaded. Others idle.

**CAUSE:**
Shard key (user_id) not uniformly distributed. Hot keys monopolize single shard.

---

### 📘 Textbook Definition

**Hot Shard:** Shard receiving disproportionate load due to uneven distribution of shard key values. Results in bottleneck: one shard CPU-bound while others idle. Degrades overall system performance.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Sharded data, but one shard got all hot users. That shard overloaded while others idle.

**One analogy:**

> Restaurant with 10 branch locations. All customers go to central branch (poor shard key choice). Other branches empty.

**One insight:**
Sharding scales only if load evenly distributed.

---

### 🧠 Mental Model

Sharding illusion vs. reality:

```
Illusion: 10 shards, each handles 10% load
Reality: 1 shard handles 50%, others 5% each
```

---

### ⚙️ How It Works

```
Scenario: Celebrity user hotspot
──────────────────────────────

Sharded by user_id % 10:
  Shard 0: users 0, 10, 20, 30, ... (normal users, low volume)
  Shard 5: users 5, 15, 25, 35, ...
    But user 12345 (celebrity) = 12345 % 10 = 5
    User 12345: 1M requests/sec
    Shard 5: CPU 100%, saturated
  Shard 9: users 9, 19, 29, ...
    Normal: 100 req/sec
    Shard 9: CPU 10%, idle

Solution 1: Rehash shard key
──────────────────────────
Old: user_id % 10 (hot user 12345 → shard 5)
New: hash(user_id + random_salt) % 10
  - Redistribute evenly
  - But requires data migration

Solution 2: Split hot shard
───────────────────────────
Original 10 shards. Shard 5 hot.
Split shard 5 → 50 micro-shards
  - Shard 5.0, 5.1, ..., 5.49
  - Distribute load across 50 instead of 1
  - Celebrity user: hash-based split among sub-shards

Solution 3: Local caching
─────────────────────────
Celebrity user data cached in memory/Redis
  - Requests served from cache (fast)
  - Reduces DB shard load
  - Cache consistency maintained via invalidation
```

---

### 💻 Code Example

```python
class HotShardDetector:
    def __init__(self, num_shards=10):
        self.shard_load = {i: 0 for i in range(num_shards)}
        self.threshold = 2.0  # 2x avg = hot

    def record_request(self, user_id):
        shard = hash(user_id) % 10
        self.shard_load[shard] += 1

    def detect_hot_shards(self):
        total = sum(self.shard_load.values())
        avg_load = total / len(self.shard_load)

        hot_shards = []
        for shard_id, load in self.shard_load.items():
            if load > avg_load * self.threshold:
                hot_shards.append({
                    'shard': shard_id,
                    'load': load,
                    'ratio': load / avg_load
                })

        return hot_shards

# Usage
detector = HotShardDetector()

# Simulate requests
for i in range(1000):
    user_id = i
    detector.record_request(user_id)

# Add hot user
celebrity_id = 12345
for i in range(1000):
    detector.record_request(celebrity_id)

# Detect
hot_shards = detector.detect_hot_shards()
print(f"Hot shards: {hot_shards}")

# Output: Shard 5 is 11x average load
```

---

### ⚠️ Common Misconceptions

| Misconception                             | Reality                                                              |
| ----------------------------------------- | -------------------------------------------------------------------- |
| "Sharding automatically distributes load" | No. Must choose good shard key. Wrong key creates hot shards.        |
| "Hot shard = single-point failure"        | Related but different. Hot shard = performance, SPOF = availability. |

---

### 🚨 Failure Modes

**Failure Mode: Cascading Overload**

**Symptom:**
Hot shard slow. Clients retry. More requests pile on hot shard. Cascade.

**Prevention:**
Detect early. Rehash/split before saturation.

---

### 📌 Quick Reference

```
Hot Shard Issue:
  Cause: Uneven shard key distribution
  Impact: One shard CPU-bound, others idle
  Detection: Monitor per-shard load ratios
  Fix: Rehash key, split shard, or cache hot data
```

---

### 🧠 Questions

**Q1.** Shard by user_id % 100. Hot user: 100K req/sec. How would you split without downtime?

**Q2.** What makes a good shard key? Bad shard key?
