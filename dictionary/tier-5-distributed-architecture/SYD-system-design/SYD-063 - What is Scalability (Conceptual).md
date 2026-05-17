---
id: SYD-063
title: What is Scalability (Conceptual)
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★☆☆
depends_on: ""
used_by: SYD-001, SYD-002, SYD-003
related: SYD-001, SYD-002, SYD-004, SYD-042
tags:
  - fundamentals
  - scalability
  - conceptual
  - design
  - beginner
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 63
permalink: /syd/what-is-scalability/
---

# SYD-063 - What is Scalability (Conceptual)

⚡ TL;DR - Scalability is a system's ability to handle
growing load by adding resources. Two types:
Vertical scaling (scale-up): add more power to one
machine (bigger CPU, more RAM). Horizontal scaling
(scale-out): add more machines. Most large-scale systems
use horizontal scaling because vertical scaling hits a
ceiling (no single machine is infinitely powerful) and
horizontal scaling is cheaper at cloud prices. The hidden
challenge: state. Stateless services scale horizontally
trivially. Stateful services (databases, caches) require
careful partitioning strategies to scale.

| #063 | Category: System Design | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | (none - foundational concept) | |
| **Related:** | Load Balancing, Horizontal vs. Vertical Scaling, Replication, Data Partitioning Strategies | |

---

### 🔥 The Problem This Solves

A startup launches with 100 users and one server.
After viral growth: 1,000,000 users. The server is at
100% CPU, requests are queuing, users see timeouts.
How do you handle 10,000x the load?
Without understanding scalability options, teams
panic-upgrade to the most expensive server available
(vertical scaling), which delays the problem but does
not solve it fundamentally.

---

### 📘 Textbook Definition

**Scalability:** The ability of a system to handle
increasing load by adding resources, maintaining
acceptable performance.

**Vertical scaling (scale-up):** Upgrading a single
machine to a more powerful one (more CPU cores, more
RAM, faster SSD). Limited by the most powerful machine
available. No code changes required.

**Horizontal scaling (scale-out):** Adding more machines
of the same type and distributing load across them.
Theoretically unlimited. Requires the application to
work correctly with multiple instances (stateless or
explicitly distributed state).

**Linear scalability:** 2x resources = 2x throughput.
Ideal but rarely achieved due to coordination overhead.

**Amdahl's Law:** If fraction P of a program can be
parallelized, maximum speedup with N processors is
1 / ((1-P) + P/N). The serial portion of code limits
scalability regardless of how many machines you add.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Vertical: bigger machine. Horizontal: more machines.
State is the hard part of horizontal scaling.

**One analogy:**
> A restaurant facing more customers:
>
> Vertical scaling: hire a faster chef. Eventually,
> one chef is the fastest possible - cannot scale further.
>
> Horizontal scaling: hire more chefs, add more tables.
> This scales much further. But: chefs must not step on
> each other (state management), the kitchen must be large
> enough for multiple chefs (infrastructure), and orders
> must be routed to the right chef (load balancing).

**One insight:**
Scalability and performance are different.
Performance = how fast is one request?
Scalability = how does throughput change as load increases?
A system can be fast but not scalable (one server
handles 10K req/sec, but adding a second server does
not increase throughput because of a shared bottleneck).
You can have both: fast AND scalable. Designing for
scalability means eliminating or distributing bottlenecks.

---

### 🔩 First Principles Explanation

**VERTICAL VS. HORIZONTAL:**
```
VERTICAL SCALING:
  Single machine: 8 cores, 32GB RAM, 500GB SSD.
  Upgrade to: 32 cores, 256GB RAM, 4TB NVMe SSD.
  
  Benefit: No code changes. Works with any database.
  Limit: Most powerful server (e.g., 224-core AWS u-24tb1)
         costs $40/hour. Eventually hits physical limits.
  Risk: Single point of failure.
  Use: Legacy applications, databases (simpler than
       distributed alternatives).

HORIZONTAL SCALING:
  10 × (8 cores, 32GB RAM) instead of 1 × (80 cores, 320GB).
  Load balancer distributes traffic.
  
  Benefit: Linear cost scaling. Fault tolerant.
           Theoretically unlimited.
  Limit: Application must be stateless (or state must
         be distributed). Coordination overhead.
  Use: Web servers, API servers, stateless microservices.

COMBINING BOTH:
  Most real systems use both.
  Vertical: choose a reasonable machine size.
  Horizontal: run multiple instances.
  Database: vertical (larger machine) + read replicas
            + eventually sharding (horizontal for writes).
```

**STATELESS vs. STATEFUL SCALING:**
```
STATELESS SERVICE (easy to scale):
  No session data stored locally.
  Any instance can handle any request.
  Add instances: immediately share load.
  
  Example: REST API that reads from a database.
  User request → any API server → same database.
  Adding API servers: instant horizontal scale.

STATEFUL SERVICE (hard to scale):
  State stored in memory or locally.
  A request must go to the specific instance
  that has the state for that user.
  
  Example: WebSocket server with in-memory sessions.
  User connects to Server A. All subsequent messages
  for that user must go to Server A (sticky sessions).
  Adding Server B: does not help users on Server A.
  
  Solutions:
  1. Move state to external store (Redis, DB).
     API servers become stateless.
  2. Consistent hashing: route requests for the
     same key to the same server.
  3. Sticky sessions: load balancer routes same user
     to same server (limited scalability).
```

**MEASURING SCALABILITY:**
```
Throughput (RPS): requests per second the system handles.
Latency: time to process one request (P50, P95, P99).
Scalability curve: throughput as N servers increases.

Linear (ideal):
  1 server: 1,000 RPS
  2 servers: 2,000 RPS
  4 servers: 4,000 RPS
  
Sub-linear (common):
  1 server: 1,000 RPS
  2 servers: 1,800 RPS  (coordination overhead: 10%)
  4 servers: 3,200 RPS  (overhead grows)
  
Superlinear (rare, usually temporary):
  Cache warming: more servers = larger total cache.
  
Flat / negative (broken):
  All servers bottleneck on one shared resource
  (e.g., single database writer).
  Adding more app servers does nothing.
```

---

### 🧪 Thought Experiment

**SCALING A SOCIAL MEDIA FEED**

1 million users, 10M feed reads/day = 116 reads/second.
One server handles this easily.

Two years later: 100M users, 1B feed reads/day =
11,574 reads/second. P99 latency now 5 seconds.

**Step 1: Profile the bottleneck.**
Is the CPU maxed? Memory? Database queries?
Find the bottleneck before scaling.

**Step 2: Scale the bottleneck.**
Bottleneck: database reads (N+1 queries, JOIN-heavy).
Fix: add read replicas (horizontal DB scale).
Result: 4 read replicas, latency drops to 200ms.

**Step 3: App tier becomes bottleneck.**
Database now handles it; API servers CPU maxed.
Fix: add more API server instances (horizontal scale).
Requires: API servers are stateless (they call the DB).
Result: 10 API server instances. Latency drops to 50ms.

**Step 4: Traffic doubles again.**
Feed queries need pre-computation (fan-out on write).
Cache feeds in Redis. Database no longer in the hot path.
Result: 99% of feed reads from Redis (sub-millisecond).

This is the typical scaling progression: vertical →
replicas → horizontal app tier → caching.

---

### 🧠 Mental Model / Analogy

> Scalability is like a factory production line:
>
> Vertical: make the machine faster. Eventually
> the machine is the fastest possible.
>
> Horizontal: add more machines in parallel.
> Scales further, but requires coordination:
> - Work distribution (load balancer)
> - No duplicate work (state management)
> - Bottleneck at shared resources (database)
>
> You cannot make the entire factory 10x faster
> by adding machines to ONE step if other steps
> (the database, the shipping dock) are the bottleneck.
> Scalability requires identifying and distributing
> every bottleneck.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Scalability means your system can handle more users
by adding more computers, not just by getting a bigger
computer. More users = add more servers. Works as long
as the servers can share the work without getting in
each other's way.

**Level 2 - How to use it (junior developer):**
Make services stateless: store sessions in Redis not
memory. Put a load balancer in front. Add more instances.
Identify the next bottleneck (usually the database).
Add read replicas. Cache frequently-read data.

**Level 3 - How it works (mid-level engineer):**
Measure current bottleneck. Vertical for databases
(simpler), horizontal for API/app tiers (stateless).
Database horizontal scale: read replicas for reads,
sharding for writes. Caching reduces database load.
CDN reduces origin server load. Each layer scaled
independently. Monitor: P50/P95/P99 latency, CPU, RPS.

**Level 4 - Why it was designed this way (senior/staff):**
Horizontal scaling wins at cloud scale because it provides
fault tolerance (N-1 instances survive one failure) and
cost-efficiency (many small machines > one giant machine
at equivalent cost). The fundamental challenge is
distributed state: a single shared database is a
scalability ceiling. Solutions: read replicas (read
scale), sharding (write scale), caching (read offloading).
Amdahl's Law quantifies the ceiling: if 10% of your code
is serial (cannot be parallelized), maximum speedup is
10x regardless of machines. Eliminate serial bottlenecks.

**Level 5 - Mastery (distinguished engineer):**
Google's Bigtable, Amazon's Dynamo, and Facebook's
Cassandra were all designed to scale horizontally to
thousands of nodes, processing petabytes of data.
The key insight: at extreme scale, consistency becomes
the enemy of scalability (CAP theorem). These systems
chose availability and partition tolerance over strong
consistency, enabling linear scalability. The lesson
for system design: identify which parts of your system
REQUIRE strong consistency (payment, inventory) and
which can tolerate eventual consistency (news feeds,
product recommendations). Strong consistency limits
horizontal scale. Design each component with its
consistency requirement explicitly stated.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ SCALING STRATEGIES                                  │
│                                                      │
│ TIER 1: Vertical (quick, limited)                  │
│  [1 × m5.xlarge 4vCPU] → [1 × m5.4xlarge 16vCPU]  │
│  No code changes. Single point of failure.         │
│                                                      │
│ TIER 2: Add read replicas (DB read scale)          │
│  Primary DB ─┬─ Read Replica 1                     │
│              └─ Read Replica 2                     │
│  Read traffic: replicas. Write: primary only.      │
│                                                      │
│ TIER 3: Horizontal app (stateless scale)           │
│  LB → [API 1] [API 2] [API 3]                      │
│        All read from same DB pool                  │
│                                                      │
│ TIER 4: Caching (eliminate DB reads)               │
│  LB → [API 1..N] → Redis Cache → DB               │
│  80-95% cache hit rate → DB near-idle              │
│                                                      │
│ TIER 5: Sharding (DB write scale)                  │
│  Shard by user_id % N → N separate DB partitions  │
│  Each shard has its own primary + replicas         │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Stateless API (horizontally scalable)**
```python
from fastapi import FastAPI, Depends
import redis
import httpx

app = FastAPI()

# External state stores (not local memory)
redis_client = redis.Redis(host="redis-cluster")
# db = postgres connection pool

@app.get("/users/{user_id}/feed")
async def get_feed(user_id: str):
    """
    Stateless: reads from external stores only.
    Any instance can serve any request.
    Add more instances: immediately scales.
    """
    # Session: validated from JWT (no server-side session)
    # Cache: stored in Redis (shared across instances)
    cache_key = f"feed:{user_id}"
    cached = redis_client.get(cache_key)
    if cached:
        import json
        return json.loads(cached)

    # DB query (shared, external)
    feed = fetch_feed_from_db(user_id)
    redis_client.setex(cache_key, 60, 
                        json.dumps(feed))
    return feed

# BAD: storing session in instance memory
# This makes the service stateful - requests must
# go to the specific instance that has the session.
# sessions = {}  # LOCAL memory - NOT scalable
# @app.post("/login")
# def login(user_id: str):
#     sessions[user_id] = {"logged_in": True}
#     # If load balancer routes next request to
#     # a different instance: session not found!
```

---

### ⚖️ Comparison Table

| Aspect | Vertical Scaling | Horizontal Scaling |
|---|---|---|
| **Mechanism** | Bigger hardware | More machines |
| **Code changes** | None | Stateless design required |
| **Limit** | Physical machine size | None (theoretically) |
| **Fault tolerance** | Single point of failure | N-1 instances survive |
| **Cost** | Exponential at top end | Linear |
| **Best for** | Databases (initially), quick fix | API/app tiers, long-term strategy |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| More servers always means more throughput | Only if there are no shared bottlenecks. Adding 10 API servers that all write to one database master may not improve throughput at all - the bottleneck is the database, not the API tier. Always identify the bottleneck before scaling. |
| Scalability and performance are the same thing | Performance = speed of one request. Scalability = how performance degrades as load increases. A system can be fast (low latency at low load) but not scalable (latency grows rapidly with load due to shared resource contention). |
| Horizontal scaling is always better than vertical | Vertical scaling is simpler (no distributed state management). For databases especially, a larger vertical machine is often the right choice up to a significant scale threshold (hundreds of thousands of queries per second). Premature horizontal database scaling (sharding) introduces enormous complexity. Right-size vertically first. |

---

### 🚨 Failure Modes & Diagnosis

**Traffic Spike Exposes Hidden Bottleneck**

**Symptom:**
A launch event drives 10x normal traffic.
P99 latency increases from 100ms to 15 seconds.
CPU on app servers is only 20%. No obvious cause.

**Root Cause:**
Hidden bottleneck: the database connection pool is
exhausted. App servers are waiting for DB connections,
not for CPU. Adding more app servers made it WORSE:
more servers competing for the same pool.

**Diagnosis and fix:**
```python
# Symptom: high DB connection wait time
# Tool: check connection pool metrics

# psycopg2 connection pool (Python)
from psycopg2 import pool

# BAD: too small pool, shared across many app servers
connection_pool = pool.ThreadedConnectionPool(
    minconn=1,
    maxconn=5   # 10 app servers × 5 = 50 DB connections
               # Under 10x spike: 10 servers × 100 threads
               # each = 1000 threads fighting for 50 conns.
)

# FIX: size the pool correctly per instance
# Per instance: min(100, DB max_connections / num_instances)
# DB max_connections = 1000
# 10 app instances: 1000 / 10 = 100 connections each
connection_pool = pool.ThreadedConnectionPool(
    minconn=10,
    maxconn=100
)

# Better: use PgBouncer (connection pooler) in front
# of PostgreSQL to handle thousands of app connections
# while maintaining a smaller actual DB connection count.
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- (none - this is a foundational concept entry)

**Builds On This (learn these next):**
- `Load Balancing` - the mechanism that distributes
  traffic across horizontally-scaled instances
- `Data Partitioning Strategies` - how to scale
  databases horizontally (sharding)
- `Horizontal vs. Vertical Scaling` - detailed
  comparison with examples

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ VERTICAL    │ Bigger machine. Simple. Has a ceiling.    │
│             │ Single point of failure.                 │
├─────────────┼──────────────────────────────────────────  │
│ HORIZONTAL  │ More machines. Stateless design needed.  │
│             │ Theoretically unlimited. Fault tolerant. │
├─────────────┼──────────────────────────────────────────  │
│ STATELESS   │ No local state. Any instance serves any  │
│             │ request. Horizontal scale trivially.     │
├─────────────┼──────────────────────────────────────────  │
│ BOTTLENECK  │ Find the constraint first. Scaling the   │
│             │ wrong tier does nothing.                 │
├─────────────┼──────────────────────────────────────────  │
│ DB SCALE    │ Read replicas → caching → sharding.     │
│             │ In that order of increasing complexity.  │
├─────────────┼──────────────────────────────────────────  │
│ ONE-LINER   │ "Bigger machine vs. more machines.       │
│             │  State is the hard part of scale-out."  │
├─────────────┼──────────────────────────────────────────  │
│ NEXT        │ What is a Cache (Conceptual)              │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Vertical: bigger machine (no code change, single point
   of failure, limited ceiling). Horizontal: more machines
   (requires stateless design, unlimited scale, fault
   tolerant). Most systems use both.
2. State is the hard part of horizontal scaling. Stateless
   services scale out trivially. Stateful services require
   external state stores (Redis, database) or explicit
   data partitioning strategies.
3. Always find the bottleneck before scaling. Adding app
   servers when the database is the bottleneck wastes money
   and may worsen contention. Profile first.

**Interview one-liner:**
"Scalability: ability to handle growing load by adding resources. Vertical (bigger
machine): simple, no code change, limited ceiling, single point of failure.
Horizontal (more machines): requires stateless design (sessions in Redis, not
local memory), load balancer distributes traffic. DB scale: read replicas for
read scale, sharding for write scale. Always find the bottleneck first: adding
app servers when the DB is bottlenecked does nothing (or makes it worse via
increased connection pool contention)."
