---
layout: default
title: "Data Partitioning Strategies"
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 42
permalink: /system-design/data-partitioning-strategies/
id: SYD-042
category: System Design
difficulty: ★★★
depends_on: Sharding, Capacity Planning, Query Patterns
used_by: Large Databases, Analytics Systems, Multi-Tenant Platforms
related: Sharding, Hot Shard, Geo-Partitioning
tags:
  - database
  - partitioning
  - advanced
  - scalability
  - storage
---

# SYD-042 - Data Partitioning Strategies

⚡ TL;DR - Data partitioning splits large datasets into smaller pieces so storage and query load can scale. The best strategy depends on how data is accessed: by range, hash, tenant, geography, or time.

| #717            | Category: System Design                                    | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------- | :-------------- |
| **Depends on:** | Sharding, Capacity Planning, Query Patterns                |                 |
| **Used by:**    | Large Databases, Analytics Systems, Multi-Tenant Platforms |                 |
| **Related:**    | Sharding, Hot Shard, Geo-Partitioning                      |                 |

---

### 🔥 The Problem This Solves

**ISSUE:**
One huge table or cluster becomes slow, expensive, and hard to rebalance.

**SOLUTION:**
Split data based on access-friendly boundaries.

---

### 📘 Textbook Definition

**Data Partitioning Strategies:** Techniques for dividing a dataset into independently stored or processed segments based on key ranges, hashes, time windows, tenants, or geography to improve scalability and manageability.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Partition by the dimension that matches how you read and write the data.

**One analogy:**

> Filing cabinets can be organized alphabetically, by year, by customer, or by city. The right cabinet scheme depends on how clerks search most often.

**One insight:**
Partitioning is not only about size. It is about routing the right workload to the right slice.

---

### 🧠 Mental Model

```
Range:       ids 1-1M | 1M-2M | 2M-3M
Hash:        hash(key) % N
Time:        2024-01 | 2024-02 | 2024-03
Tenant:      tenant A | tenant B | tenant C
Geo:         us | eu | apac
```

---

### 📶 Gradual Depth

**Level 1:** Break data into smaller groups.

**Level 2:** Choose strategy based on common query filters and write patterns.

**Level 3:** Rebalancing cost, hotspot risk, archival behavior, and cross-partition query cost drive design quality.

**Level 4:** Partitioning is a workload-shaping decision. Bad partitioning shifts bottlenecks instead of removing them.

---

### ⚙️ How It Works

```
Range partitioning:
  good for scans and ordering
  risk: newest range becomes hot

Hash partitioning:
  good for even distribution
  risk: range queries scatter-gather

Time partitioning:
  good for logs, metrics, retention
  risk: recent partition hot

Tenant partitioning:
  good for isolation and quota control
  risk: large tenant imbalance
```

---

### 💻 Code Example

```python
def route_partition(user_id, strategy="hash"):
    if strategy == "hash":
        return hash(user_id) % 16
    if strategy == "range":
        return user_id // 1_000_000
    raise ValueError("unknown strategy")
```

---

### ⚖️ Comparison Table

| Strategy | Best for           | Main risk            |
| -------- | ------------------ | -------------------- |
| Range    | ordered queries    | hotspot ranges       |
| Hash     | even distribution  | poor locality        |
| Time     | logs, metrics      | hot latest partition |
| Tenant   | isolation          | large-tenant skew    |
| Geo      | latency/compliance | cross-region joins   |

---

### ⚠️ Common Misconceptions

| Misconception                         | Reality                                                         |
| ------------------------------------- | --------------------------------------------------------------- |
| "Hash partitioning solves everything" | It hurts range scans and time-ordered queries.                  |
| "Partitioning is free"                | Cross-partition joins, rebalancing, and routing add complexity. |

---

### 🚨 Failure Modes

**Failure Mode 1: Wrong partition key**

**Symptom:**
Most traffic lands on one partition.

**Prevention:**
Model real workload first, not just schema shape.

---

**Failure Mode 2: Cross-partition query explosion**

**Symptom:**
Simple request fans out to all partitions.

**Prevention:**
Align partition key with dominant lookup path.

---

### 📌 Quick Reference

```
Partition by:
  time for logs
  tenant for isolation
  hash for even load
  range for ordered access
  geography for latency/compliance
```

---

### 🧠 Questions

**Q1.** Which is worse for your workload: one hot partition or fan-out reads across all partitions?

**Q2.** How will you rebalance when one tenant outgrows its partition?
