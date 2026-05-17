---
id: SYD-020
title: Active-Active
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-008, SYD-019
used_by: ""
related: SYD-008, SYD-019, SYD-021, SYD-023, SYD-024
tags:
  - architecture
  - reliability
  - high-availability
  - distributed-systems
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 20
permalink: /syd/active-active/
---

# SYD-020 - Active-Active

⚡ TL;DR - Active-active means all redundant copies
of a service are simultaneously serving traffic.
No failover is needed because there is no standby;
when one node fails, the load balancer redistributes
traffic to the remaining nodes instantly. The benefit
is zero-downtime on node failure. The cost is that
all copies must handle writes consistently, making
stateful active-active (especially for databases)
one of the hardest distributed systems problems.

| #020 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Load Balancing, Redundancy and Failover | |
| **Used by:** | (applies to many HA designs) | |
| **Related:** | Load Balancing, Redundancy and Failover, Active-Passive, Geo-Replication, Multi-Region Architecture | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A service runs as active-passive: primary handles
all traffic; secondary is synchronized but idle.
When the primary fails, it takes 30-60 seconds to
detect the failure and promote the secondary. During
those 30-60 seconds, users get errors. For a payment
flow, that is unacceptable. The secondary is also
idle, wasting the capacity of a full server 100% of
the time to gain 0% throughput.

**THE BREAKING POINT:**
Active-passive wastes capacity and still has a
failover window. For systems where "any downtime
is unacceptable" (financial transactions, critical
APIs), the failover window is too long. For
systems where capacity efficiency matters (large
fleets), the passive standby wastes 50% of
infrastructure cost at the hot-standby tier.

---

### 📘 Textbook Definition

**Active-active** (also called active/active or multi-
active): a high-availability pattern in which two or
more instances of a service simultaneously handle
requests. All instances are "active" - they all accept
and process traffic at the same time. A load balancer
distributes requests across all active instances.
When one instance fails, the load balancer routes
its traffic to the remaining instances without a
failover step. Active-active is trivial for stateless
services (web servers, APIs with no shared state).
For stateful services (databases), active-active
requires all copies to coordinate writes, which
introduces consistency challenges (conflict resolution,
replication lag, distributed transactions).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Every copy of the service is running and handling
traffic. When one fails, others absorb its load -
no switchover required.

**One analogy:**
> A restaurant with 5 cashiers. All 5 are active and
> taking orders simultaneously. If cashier 3 calls in
> sick, the other 4 take on the extra load. There is
> no "backup cashier waiting in the back room." You
> do not need to wait for the backup to clock in
> before customers can pay.
>
> Compare to active-passive: 1 cashier takes all
> orders; 4 are standing by. When the 1 cashier
> gets sick, one of the 4 takes over - but there is
> a gap while the manager runs to the back room to
> get the backup started.

**One insight:**
Active-active is a natural fit for stateless services
and is the default pattern for web-tier scaling.
The hard version is active-active for stateful
services (especially write-heavy databases), where
multiple nodes accepting writes simultaneously can
lead to write conflicts that require either avoiding
conflict by design (partitioning writes) or resolving
conflict automatically (CRDTs, last-writer-wins).

---

### 🔩 First Principles Explanation

**WHY IT IS HARD FOR STATEFUL SERVICES:**

```
┌──────────────────────────────────────────────────────┐
│ STATELESS ACTIVE-ACTIVE (trivial)                   │
│                                                      │
│  Client → Load Balancer                              │
│             ├──> API Server 1 (reads from shared DB) │
│             ├──> API Server 2 (reads from shared DB) │
│             └──> API Server 3 (reads from shared DB) │
│                                                      │
│ No shared mutable state per server → trivial.       │
│ Any server can handle any request independently.    │
│ Server failure: LB stops routing to it. Done.       │
│                                                      │
│ STATEFUL ACTIVE-ACTIVE (hard)                        │
│                                                      │
│  Write: "user-1 balance = $100"                      │
│    → Sent to DB-node-1 AND DB-node-2 must agree     │
│                                                      │
│  Concurrent write conflict:                          │
│  t=0: DB-node-1 gets write: balance = $100           │
│  t=0: DB-node-2 gets write: balance = $90            │
│  (two clients updated simultaneously)                │
│  Which is correct? Last-writer-wins? Error?          │
│  Requires: conflict detection + resolution protocol  │
└──────────────────────────────────────────────────────┘
```

**STRATEGIES FOR STATEFUL ACTIVE-ACTIVE:**

```
Strategy 1: Write partitioning (sharding by key)
  user-1 always writes to DB-node-1
  user-2 always writes to DB-node-2
  Conflict: impossible by construction
  Tradeoff: hot shards; cross-shard transactions hard

Strategy 2: Multi-master with conflict resolution
  All nodes accept writes; replicate asynchronously
  Conflict resolution: last-write-wins (LWW),
  CRDTs (counter, set, list types), or custom logic
  Tradeoff: complexity; convergence not guaranteed

Strategy 3: Consensus-based writes (Paxos/Raft)
  Write accepted only if quorum agrees
  No conflicts; strong consistency
  Tradeoff: write latency (quorum round-trip);
  reduces to active-passive if quorum is 1 of N
```

**THE TRADE-OFFS:**
**Gain:** No failover window; full capacity utilization;
scale-out by adding nodes; natural load distribution.
**Cost:** Stateful active-active requires either write
partitioning (limits flexibility), multi-master conflict
resolution (complex, error-prone), or consensus-based
writes (higher write latency). Wrong implementation
leads to data corruption or split-brain.

---

### 🧪 Thought Experiment

**SCENARIO: DNS provider design - why active-active**

A DNS provider (like Cloudflare, Route53) must handle
billions of queries per day with zero downtime. Even
a 30-second failover window is unacceptable: millions
of DNS resolutions fail during that window, breaking
every website using the service.

**How it is built (active-active, anycast):**
- DNS servers run in 200+ data centers worldwide
- All serve DNS queries simultaneously (active-active)
- Anycast routing: client's DNS query goes to the
  nearest data center automatically
- If one data center fails: BGP routing withdraws
  its IP prefix; queries route to the next nearest
  data center within seconds
- No "failover" - the routing protocol handles it
- Client sees: one query might time out, retry succeeds
  against a different data center transparently

**Write coordination:**
DNS records (the stateful part) are not written by
clients in real-time. They propagate via a separate
control plane with strong consistency guarantees.
Reads (the hot path) are stateless: each data center
has a full copy of DNS records. Only writes require
coordination, and writes are rare vs reads.

**THE INSIGHT:**
Many systems that appear to need stateful active-active
can be architecturally split into a stateless read
path (trivially active-active) and a stateful write
path (consensus-based, lower throughput requirement).
Design the read path for active-active scale; design
the write path for consistency safety.

---

### 🧠 Mental Model / Analogy

> Active-active is like a highway with 4 lanes. All
> 4 lanes carry traffic simultaneously. If one lane
> closes (accident), traffic redistributes across
> the other 3 lanes. No driver has to wait for a
> "lane failover" to complete. The highway degrades
> gracefully (more congestion but still passable).
>
> Active-passive is like a highway with 1 lane and
> 3 backup lanes that open only after the primary lane
> is fully closed and construction crews have set up
> barriers. Faster speed on the normal lane; but a
> mandatory wait when it fails.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
All copies of the service handle requests at the same
time. No waiting for a backup to take over - when one
node fails, others automatically absorb the traffic.

**Level 2 - How to use it (junior developer):**
For stateless services: deploy N instances behind
a load balancer. Configure health checks. The load
balancer automatically removes failed instances.
This is active-active by default in every modern
web deployment.

**Level 3 - How it works (mid-level engineer):**
For databases: evaluate whether reads and writes can
be separated. Active-active for reads (read replicas)
is trivial. Active-active for writes requires a
conflict strategy. Most applications tolerate
read-replica architecture where all writes go to
one primary (effectively active-passive for writes)
while reads scale across replicas (active-active for
reads). True multi-master is reserved for systems
that need it.

**Level 4 - Why it was designed this way (senior/staff):**
The CAP theorem directly constrains stateful active-
active: under a network partition, a system must
choose consistency or availability. Active-active
(AP systems: available under partition) cannot
guarantee strong consistency. Multi-active databases
(CockroachDB, Cassandra) achieve this by relaxing
consistency during partition (eventual consistency
or configurable consistency levels per operation).
The architect must understand the consistency model
the application requires before choosing active-active
for the database tier.

**Level 5 - Mastery (distinguished engineer):**
The term "active-active" is often imprecise. Precisely:
it means all nodes accept operations from clients.
But this conflates availability semantics (all nodes
reachable) with write semantics (all nodes can modify
the same data). Systems like DynamoDB and Cassandra
are "active-active" in that all nodes accept writes -
but they use eventual consistency and last-writer-wins
to handle conflicts. Systems like CockroachDB are
"active-active" in that all nodes accept writes AND
provide serializable consistency - but at the cost
of higher latency on writes (Raft consensus round-
trips). When evaluating an "active-active database"
claim, always ask: what is the consistency model
during network partition?

---

### ⚙️ How It Works (Mechanism)

**Active-active with anycast (global DNS/CDN):**

```
┌──────────────────────────────────────────────────────┐
│ ANYCAST ACTIVE-ACTIVE FLOW                          │
│                                                      │
│ Client IP: 8.8.8.x (US East)                        │
│   → BGP routing → nearest datacenter (US East)      │
│   → US-East node handles request                     │
│                                                      │
│ US-East datacenter failure:                          │
│   → BGP withdraws US-East IP prefix                  │
│   → Client's next request routes to US-Central       │
│   → Transparent to client (one timeout + retry)      │
│                                                      │
│ No "failover" decision needed.                       │
│ Routing protocol handles it in ~seconds.             │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ LOAD BALANCER ACTIVE-ACTIVE (same region)           │
│                                                      │
│  Incoming → LB                                       │
│             ├─> Node 1 (serving) ←── health OK      │
│             ├─> Node 2 (serving) ←── health OK      │
│             └─> Node 3 (serving) ←── health FAIL    │
│                           ↑                          │
│                  LB removes from rotation            │
│                  Node 1+2 absorb 50% more load       │
│                                                      │
│ RTO: ~10-30 seconds (health check detection)        │
│ Capacity: N-1 nodes must handle peak load           │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Stateless active-active: Kubernetes HPA**
```yaml
# Stateless active-active: all pods serve traffic.
# HPA scales out nodes under load, scales in under idle.
# Node failure: k8s removes from endpoints automatically.

apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-service
spec:
  replicas: 3  # all active, all serving
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1  # keep 2 of 3 active during update
      maxSurge: 1
  template:
    spec:
      containers:
      - name: api
        image: api-service:1.2.3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          periodSeconds: 5
          failureThreshold: 2
          # Removed from service endpoints after 10s
          # Other nodes absorb its traffic: active-active
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-service
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  # Scale out when any node hit 70% CPU
  # All replicas active; new replicas added to rotation
```

**Example 2 - BAD: Active-active database without conflict strategy**
```python
# BAD: two DB nodes both accept writes without
# any conflict resolution. Leads to data divergence.

# Node 1 receives: UPDATE accounts SET balance=100
#   WHERE user_id=1
# Node 2 receives: UPDATE accounts SET balance=90
#   WHERE user_id=1 (concurrent)
# Both nodes apply locally, replicate to each other.
# Result: node-1 has $100, node-2 has $90.
# Last replication wins: whoever replicates last
# "wins" without business validation.
# This is NOT valid for financial data.

# SOLUTION: Route all writes for a given entity to
# a specific shard (write partitioning) or use
# a database with serializable multi-master (CockroachDB)
```

**Example 3 - GOOD: Active-active for reads, primary for writes**
```java
// GOOD: Separate read/write paths.
// Reads: any replica (active-active for reads)
// Writes: primary only (single authoritative writer)
@Repository
public class OrderRepository {

    private final DataSource primaryDataSource;   // writes
    private final DataSource replicaDataSource;   // reads

    // Reads: round-robin across replicas
    // All replicas active → active-active read path
    @Transactional(readOnly = true)
    public Order findById(Long id) {
        return replicaJdbcTemplate
            .queryForObject(
                "SELECT * FROM orders WHERE id = ?",
                ORDER_MAPPER, id);
    }

    // Writes: primary only → single-writer safety
    // Active-passive for writes
    @Transactional
    public Order save(Order order) {
        primaryJdbcTemplate.update(
            "INSERT INTO orders (...) VALUES (?,...)",
            order.toParams());
        return order;
    }
}
// Result: reads scale horizontally (active-active)
// Writes are safe (primary-only, no conflict possible)
// Classic CQRS-lite pattern for HA databases
```

---

### ⚖️ Comparison Table

| | Active-Active | Active-Passive |
|---|---|---|
| **All nodes serving** | Yes | No (standby idle) |
| **Failover required** | No (LB routes around failure) | Yes (promote standby) |
| **RTO** | ~0 (seconds) | 30s - minutes |
| **Capacity utilization** | 100% of all nodes | Only primary active |
| **Stateless** | Trivial | Easy |
| **Stateful (writes)** | Hard (conflict resolution) | Simpler (single writer) |
| **Cost** | Full capacity for all nodes | Lower (standby reduced) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Active-active means zero data loss | For stateful services: write conflicts in multi-active databases can cause data loss if resolved by last-writer-wins. Zero data loss requires consensus-based writes (all nodes agree before write is committed), which introduces write latency. |
| Active-active is always better than active-passive | For stateful services with strong consistency requirements, active-passive with consensus-based failover (Raft) is often safer and simpler to implement correctly. Active-active complexity is only justified if the availability requirement truly demands it. |
| All load-balanced services are active-active | True only if all instances can handle any request identically. If sticky sessions are required (stateful server-side sessions), it is not true active-active - the session affinity creates implicit primary-secondary relationships per user. |

---

### 🚨 Failure Modes & Diagnosis

**Cascading Overload After Node Failure**

**Symptom:**
Three nodes in an active-active cluster. Node 3
fails. Nodes 1 and 2 absorb node 3's traffic. CPU
on nodes 1 and 2 spikes to 100%. Both nodes slow
down and start timing out. Health checks start
failing on node 1 (slow GC, not truly down). LB
removes node 1. Now node 2 carries all traffic and
collapses. Full outage from a 1-node failure.

**Root Cause:**
The cluster was running at 80% capacity across 3
nodes. Removing 1 node pushed the remaining 2 to
110% capacity. The system was not designed for N-1
node failure at peak load.

**The rule:**
Active-active clusters must be sized so that at
peak load with N-1 nodes, the remaining nodes stay
below 70% CPU. For a 3-node cluster: each node must
handle 50% of peak load (to absorb a 1-node failure
with 2 remaining nodes at 100%, you need headroom).
Better: size to N+1 or N+2 nodes beyond what peak
traffic requires.

**Prevention:**
```
Required sizing rule:
  peak_load_per_node × N_nodes = total peak load
  remaining capacity with 1 failure = peak × (N-1)/N
  Safe threshold: total_peak ÷ (N-1) ≤ 70% of node capacity

Example: 100 RPS total, 3 nodes = 33 RPS each at peak
  With 1 failure: 50 RPS each
  Node capacity must be ≥ 72 RPS (50/0.70)
  If node max is 60 RPS: 3-node cluster is UNSAFE
  Need 4-node cluster: 25 RPS each; 1 failure = 33 RPS
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Load Balancing` - the mechanism that distributes
  traffic in active-active; essential foundation
- `Redundancy and Failover` - active-active is the
  extreme form of redundancy - all copies active

**Builds On This (learn these next):**
- `Active-Passive` - the complement pattern; compare
  tradeoffs to understand when to use which
- `Geo-Replication` - active-active across regions
  (the hardest form of the pattern)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS    │ All copies serve traffic simultaneously  │
│               │ No "standby" waiting for failover        │
├───────────────┼──────────────────────────────────────────┤
│ EASY          │ Stateless services (API servers, web)    │
│               │ Load balancer handles everything          │
├───────────────┼──────────────────────────────────────────┤
│ HARD          │ Stateful (DB writes): conflict resolution │
│               │ or write partitioning required           │
├───────────────┼──────────────────────────────────────────┤
│ KEY BENEFIT   │ RTO ≈ 0 (no failover step)               │
│               │ Full utilization of all nodes            │
├───────────────┼──────────────────────────────────────────┤
│ KEY RISK      │ Cascading failure if cluster not sized   │
│               │ for N-1 capacity at peak load            │
├───────────────┼──────────────────────────────────────────┤
│ SIZING RULE   │ Each node handles peak/N × (N/(N-1))     │
│               │ Target: ≤70% CPU with 1 failure          │
├───────────────┼──────────────────────────────────────────┤
│ DB SHORTCUT   │ Active-active reads + primary writes     │
│               │ = safe, scalable, most applications work │
├───────────────┼──────────────────────────────────────────┤
│ ONE-LINER     │ "All nodes serve traffic all the time.   │
│               │  Failure = redistribution, not failover."│
├───────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE  │ Active-Passive → Geo-Replication         │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Active-active = all nodes serving; failure causes
   load redistribution, not failover. RTO ≈ 0 for
   stateless services.
2. Stateless active-active is trivial (load balancer).
   Stateful active-active (write coordination) requires
   partitioning, CRDTs, or consensus.
3. Size for N-1 failure: at peak load with 1 node down,
   remaining nodes must stay below 70% capacity.

**Interview one-liner:**
"Active-active means all redundant copies simultaneously
serve traffic. Node failure causes load redistribution
to survivors - no failover step, so RTO is near zero.
This is trivial for stateless services behind a load
balancer. For databases, active-active for writes requires
either write partitioning (user 1 always writes to shard 1)
to avoid conflicts, or a multi-master protocol with conflict
resolution. Most applications solve this by making reads
active-active (read replicas) while keeping writes on
a single primary - getting the availability benefit on
the read path without the complexity of multi-master writes."
