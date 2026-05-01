---
layout: default
title: "Vertical Scaling"
parent: "System Design"
nav_order: 681
permalink: /system-design/vertical-scaling/
number: "681"
category: System Design
difficulty: ★☆☆
depends_on: "Capacity Planning"
used_by: "Horizontal Scaling, Auto Scaling"
tags: #foundational, #distributed, #architecture, #performance, #cloud
---

# 681 — Vertical Scaling

`#foundational` `#distributed` `#architecture` `#performance` `#cloud`

⚡ TL;DR — **Vertical Scaling** (scale-up) adds more resources (CPU, RAM, disk) to a single server instead of adding more servers.

| #681            | Category: System Design          | Difficulty: ★☆☆ |
| :-------------- | :------------------------------- | :-------------- |
| **Depends on:** | Capacity Planning                |                 |
| **Used by:**    | Horizontal Scaling, Auto Scaling |                 |

---

### 📘 Textbook Definition

**Vertical Scaling** (also called "scaling up") is the process of increasing the capacity of a single server or instance by adding more resources to it: additional CPU cores, RAM, faster storage (NVMe SSD), or higher network bandwidth. In cloud environments, vertical scaling means changing the instance type to a larger size (e.g., AWS EC2 from `t3.medium` → `m5.2xlarge`). Vertical scaling is bounded by the maximum hardware configuration available (a physical ceiling exists) and typically requires downtime to resize unless the cloud provider supports live resizing. It is simple to implement (no application architecture changes) but limited in scalability and introduces a single point of failure.

---

### 🟢 Simple Definition (Easy)

Vertical scaling = make your one server bigger (more CPU, more RAM). Like upgrading your laptop from 8GB to 32GB RAM. Simple, but you can't keep upgrading forever — hardware has limits.

---

### 🔵 Simple Definition (Elaborated)

Your database server is slow because it's running out of memory — queries are hitting disk instead of cache. Vertical scaling: move from a 32GB RAM instance to a 128GB RAM instance. Now all frequently-accessed data fits in memory, queries are fast. No code changes, no architecture changes. Simple. The limit: you can't add RAM beyond what a single machine supports, and more RAM per machine costs exponentially more per GB than distributing across multiple smaller machines.

---

### 🔩 First Principles Explanation

**When vertical scaling makes sense vs. when it fails:**

```
VERTICAL SCALING WORKS WELL:
  - Stateful workloads: databases, caches (Redis, Postgres, MySQL)
    → Hard to distribute; single-node is architecturally simpler
  - Short-term fixes: buy time before architectural redesign
  - Latency-sensitive: inter-process calls vs network calls (no hop overhead)
  - Licensing: some software licenses per server (per-core pricing cheaper on fewer big nodes)

VERTICAL SCALING FAILS WHEN:
  - Hardware ceiling: AWS largest single instance is ~24TB RAM, 448 vCPU
    (data sets beyond this: must go horizontal or distributed DB)
  - Cost curve: doubling resources often > 2x price at high end
    t3.medium: $0.0416/hr (2 vCPU, 4 GiB)
    m5.2xlarge: $0.384/hr  (8 vCPU, 32 GiB) — 4x resources, ~9x cost
  - Availability: single server = single point of failure
    Resizing typically requires instance restart (minutes of downtime)
  - Traffic spikes: cannot resize fast enough to handle sudden 10x traffic
    (instance resize: 5-15 min; auto-horizontal scale: 2-3 min for stateless)

PRACTICAL RULE:
  Databases: vertical first (up to ~16x traffic) → then read replicas → then sharding
  Stateless apps: horizontal from day 1 (easier, cheaper, more resilient)
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Vertical Scaling (or any scaling):

- Single undersized server handles all load → CPU at 100% → latency spikes
- Cannot serve traffic increases without code changes or redeployment

WITH Vertical Scaling:
→ Immediate capacity increase with zero code changes
→ Appropriate for stateful systems where horizontal scaling is architecturally complex
→ Buys time while longer-term scaling work is in progress

---

### 🧠 Mental Model / Analogy

> Vertical scaling is like upgrading a single chef in a restaurant with better equipment — a faster oven, more prep space, sharper knives. The chef works faster and handles more orders. But there's a limit to how much one person can cook, regardless of equipment.

"Chef" = server
"Better equipment" = more CPU/RAM/storage
"Orders per hour limit" = hardware ceiling

---

### ⚙️ How It Works (Mechanism)

**AWS vertical scaling — changing instance type:**

```bash
# AWS CLI: resize EC2 instance (requires stop → resize → start)

# 1. Stop instance:
aws ec2 stop-instances --instance-ids i-0abcdef1234567890

# 2. Resize to larger type:
aws ec2 modify-instance-attribute \
  --instance-id i-0abcdef1234567890 \
  --instance-type '{"Value": "m5.2xlarge"}'

# 3. Restart:
aws ec2 start-instances --instance-ids i-0abcdef1234567890

# Downtime: typically 3-5 minutes
# Data: persistent (EBS volume retains all data)

# RDS vertical scaling (managed, brief downtime):
aws rds modify-db-instance \
  --db-instance-identifier my-prod-db \
  --db-instance-class db.m5.4xlarge \
  --apply-immediately
# Downtime: 1-5 minutes for instance resize + failover
```

---

### 🔄 How It Connects (Mini-Map)

```
Capacity Planning
(determines when scaling needed)
        │
        ▼
Vertical Scaling  ◄──── (you are here)
(scale up: bigger server)
        │
        ├── Horizontal Scaling (scale out: more servers)
        └── Auto Scaling (automates the scale decision)
```

---

### 💻 Code Example

**JVM heap sizing after vertical scale — critical post-resize step:**

```bash
# After vertical scaling from 16GB → 64GB RAM:
# WRONG: leave JVM heap at old setting
# java -Xmx4g -Xms4g -jar order-service.jar  ← wastes 60GB of new RAM

# CORRECT: resize JVM heap proportionally
# Rule: JVM heap = 50-75% of available RAM (leave room for OS, off-heap, GC)
# 64GB server: heap = 40-48GB
java -Xmx48g -Xms48g \
  -XX:+UseG1GC \
  -XX:MaxGCPauseMillis=200 \
  -jar order-service.jar

# For containerised services — use memory limits not -Xmx:
# Kubernetes resource limits:
resources:
  requests: {memory: "48Gi", cpu: "8"}
  limits: {memory: "64Gi", cpu: "16"}
# JVM (Java 17+): reads container memory limits automatically:
# java -XX:MaxRAMPercentage=75 -jar app.jar  (75% of container limit)
```

---

### ⚠️ Common Misconceptions

| Misconception                                               | Reality                                                                                                                                                                                               |
| ----------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Vertical scaling eliminates the need for horizontal scaling | Vertical scaling has a hard ceiling (maximum instance size) and a single point of failure. For high availability and elastic scalability, horizontal scaling is ultimately required                   |
| Vertical scaling is always faster/easier than horizontal    | Resizing a stateful database instance requires downtime. Horizontal scaling of a stateless service via Kubernetes HPA takes ~2 minutes with zero downtime                                             |
| More CPU cores always makes applications faster             | Applications bottlenecked on a single-threaded bottleneck (a lock, a sequential algorithm) don't benefit from more cores. Profiling first determines whether CPU cores, RAM, or I/O is the bottleneck |
| Cloud instances can be resized instantly                    | Most cloud instance resizes require a stop/start cycle (minutes of downtime). Some providers offer live migration for certain instance families, but it's not universal                               |

---

### 🔥 Pitfalls in Production

**Vertical scaling a database without resizing connection pool:**

```java
// BEFORE: 8 vCPU server, max 100 connections
HikariConfig config = new HikariConfig();
config.setMaximumPoolSize(10);  // 10 app connections per pod × 10 pods = 100 total

// AFTER vertical scale: 32 vCPU server (can handle more connections)
// But: connection pool not updated → 32 cores idle, still only 100 connections
// Database at 20% CPU (waiting on application connection requests, not DB)

// CORRECT:
// PostgreSQL rule: max_connections per server ≈ (RAM_GB × 50) or (vCPU × 50)
// 32 vCPU, 128 GB → max_connections = 500 is reasonable
// App pool: max_connections / (instances × pods) = 500 / 10 = 50 per pod
config.setMaximumPoolSize(50);  // tune after measuring actual usage
```

---

### 🔗 Related Keywords

- `Horizontal Scaling` — the complementary pattern: more servers instead of bigger servers
- `Auto Scaling` — automatically adjusts scale (vertical or horizontal) based on load
- `Capacity Planning` — determines when and how much to scale
- `Load Balancing` — required when horizontal scaling adds multiple servers
- `Sharding (System)` — horizontal data partitioning when vertical DB scaling hits ceiling

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Add resources to ONE server (CPU/RAM).    │
│              │ Simple, bounded by hardware ceiling.      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Stateful workloads (DB, cache); quick     │
│              │ fix while horizontal scaling is designed  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Need high availability; hit hardware      │
│              │ ceiling; cost curve is exponential        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Upgrade the chef's kitchen, not the      │
│              │  number of chefs."                        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Horizontal Scaling → Load Balancing       │
│              │ → Auto Scaling                            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a PostgreSQL database server at 32GB RAM, 8 vCPU running at 80% CPU and 90% memory utilisation. You vertically scale to 128GB RAM, 32 vCPU. Two weeks later, utilisation is back to 80% CPU and 90% memory. What does this pattern tell you about the workload's growth trajectory, and at what point does the cost/benefit analysis favour horizontal scaling (read replicas + sharding) over continued vertical scaling?

**Q2.** A single-threaded Java application processes a queue of tasks. The server is vertically scaled from 4 vCPU to 32 vCPU. Task throughput improves by only 15%. Identify the architectural bottleneck and explain why more CPU cores did not help. What application-level change is required to benefit from the additional cores, and how would you validate the hypothesis before recommending the vertical scale?
