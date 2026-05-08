---
layout: default
title: "Distributed Computing"
parent: "Big Data & Streaming"
grand_parent: "Technical Dictionary"
nav_order: 6
permalink: /big-data-streaming/distributed-computing/
id: BIG-006
category: Big Data & Streaming
difficulty: ★★☆
depends_on: Networking, Operating Systems, Data Structures
used_by: Apache Hadoop, Apache Spark, Distributed Systems, Microservices
related: MapReduce, Apache Hadoop, Distributed Systems
tags:
  - distributed-computing
  - parallel-processing
  - scalability
  - big-data
  - deep-dive
---

# BIG-006 - Distributed Computing

⚡ TL;DR - Distributed computing is the use of **multiple networked computers working together as a unified system** to solve problems too large for a single machine - by dividing work across nodes, achieving parallelism, fault tolerance, and horizontal scalability; the core challenges are: coordination, consistency, partial failure handling, and network unreliability.

| #531            | Category: Big Data & Streaming                                  | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------------------------------- | :-------------- |
| **Depends on:** | Networking, Operating Systems, Data Structures                  |                 |
| **Used by:**    | Apache Hadoop, Apache Spark, Distributed Systems, Microservices |                 |
| **Related:**    | MapReduce, Apache Hadoop, Distributed Systems                   |                 |

---

### 🔥 The Problem This Solves

**SINGLE-MACHINE LIMITS:**
A single machine has bounded CPU (cores), memory (RAM), and disk. For a dataset of 10 petabytes or a computation requiring 1 million CPU-hours: no single machine can handle it in any reasonable timeframe. Distributed computing breaks the problem into chunks, processes them on many machines simultaneously, and aggregates results - effectively multiplying compute capacity by the number of machines.

---

### 📘 Textbook Definition

**Distributed Computing** is a model where **multiple autonomous computers** communicate through a network to coordinate and complete a shared computational task. Each node has its own local memory and processor; there is no shared global memory (unlike multi-core computing). Key paradigms: **(1) Client-Server**: one node requests, another serves. **(2) Peer-to-Peer**: all nodes are equal participants. **(3) Data-Parallel (MapReduce/Spark)**: same computation applied to different data partitions on different nodes. **(4) Task-Parallel**: different computations on the same or different data. Fundamental challenges: **Partial failure** (some nodes fail while others run - must detect and tolerate), **Network unreliability** (messages may be lost, delayed, reordered), **Consistency** (keeping data consistent across nodes - CAP theorem), **Coordination** (electing leaders, distributed locking, consensus - Paxos, Raft).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Distributed computing = many computers working together as one, dividing work for speed and resilience, but facing coordination, failure, and consistency challenges single machines don't have.

**One analogy:**

> Building a skyscraper: one construction worker could theoretically build it, but it would take centuries. A crew of 1,000 workers, each with their own tools and their assigned section (distributed), completes it in 2 years. Challenge: workers must coordinate (distributed consensus - "which floor are we on?"), handle a sick worker's absence (fault tolerance - reassign their work), and ensure all sections connect precisely (data consistency - interfaces match).

**One insight:**
The **fallacies of distributed computing** (Deutsch, 1994) are still the most important concepts: (1) The network is reliable - it isn't; (2) Latency is zero - it isn't; (3) Bandwidth is infinite - it isn't; (4) The network is secure - it isn't; (5) Topology doesn't change - it does; (6) There is one administrator - there isn't; (7) Transport cost is zero - it isn't; (8) The network is homogeneous - it isn't. Every distributed system must be designed assuming all 8 fallacies are violated.

---

### 🔩 First Principles Explanation

**WHY DISTRIBUTION IS HARD:**

```
Single machine:
  - Failure: full stop (everything fails together, easy to detect)
  - Consistency: shared memory, atomic operations, easy
  - Communication: function calls, nanoseconds
  - Coordination: mutex, semaphore, all in one process

Distributed system:
  - Failure: PARTIAL (some nodes up, some down - ambiguous state)
    Node A sends message to Node B. No response.
    Options: B is down? Network partition? Message in transit? B busy?
    Cannot distinguish without additional protocol.

  - Consistency: no shared memory. Each node has local copy.
    Node A updates record 42. Node B has stale cached copy.
    "Is Node B's copy valid?" - depends on consistency model.

  - Communication: network calls, milliseconds (100,000× slower)
    Every remote call = potential failure, latency, and partial result.

  - Coordination: requires distributed algorithms
    Leader election: Bully algorithm, Raft consensus
    Distributed lock: ZooKeeper, Redis SETNX
    Consensus: Paxos, Raft - "agree on one value when nodes disagree"
```

**HORIZONTAL vs VERTICAL SCALING:**

```
Vertical scaling (scale up):
  Start: 1 server × 32 cores, 128GB RAM
  Scale: upgrade to 128 cores, 2TB RAM
  Limit: physical hardware maximum (~96 cores, 24TB RAM on largest servers)
  Cost: exponential (2× performance → 10× cost at high end)
  Failure: single point of failure - one server down = full outage

Horizontal scaling (scale out) - distributed computing:
  Start: 10 servers × 32 cores, 128GB RAM each
  Scale: add more servers (11, 20, 100, 10,000...)
  Limit: network, coordination overhead (Amdahl's law)
  Cost: linear (2× performance → 2× servers)
  Failure: one server down → 1/N of work affected; others continue

Amdahl's Law: max speedup = 1 / (S + (1-S)/N)
  S = serial portion of workload (fraction that can't be parallelized)
  N = number of processors/nodes

  If 10% of work is serial (S=0.1): max speedup with 1000 nodes = 9.9×
  No matter how many nodes you add: serial bottleneck limits gain
  → Minimize serial portions for distributed systems to scale well
```

**DISTRIBUTED TASK EXECUTION (SPARK EXAMPLE):**

```
Computation: count words in 10TB of text files

Sequential (1 machine):
  Read 10TB → process → output
  Time: ~10TB / 500MB/s read = 20,000 seconds = 5.5 hours

Distributed (1000 Spark workers):
  Driver: splits 10TB into 1000 partitions (10GB each)
  Each worker: reads its 10GB partition → count words locally
  Driver: aggregate all 1000 local counts → final count
  Time: ~10GB / 500MB/s = 20 seconds (1000× faster)

  Plus coordination overhead:
  - Job scheduling: ~1s
  - Network transfer for aggregation: ~100MB final counts across network
  - Fault tolerance: if 3 workers fail, re-run their partitions (adds ~5s)
  Total: ~30 seconds vs. 5.5 hours = ~660× speedup (not 1000× due to overhead)
```

---

### 🧪 Thought Experiment

**THE PARTIAL FAILURE PROBLEM:**

Node A sends a payment request to Node B. Node A waits 30 seconds. No response. What happened?

Option 1: Node B received the request, processed it (payment committed), then crashed before sending the response. If Node A retries: **double payment**.

Option 2: Node B never received the request (network dropped it). If Node A doesn't retry: **payment not processed**.

Option 3: Node B received it, is processing (taking longer than 30s), hasn't responded yet. If Node A retries: **double payment**. If not: **correct but slow**.

**Resolution:** **Idempotency keys**. Node A includes a unique `requestId`. Node B: checks if `requestId` was already processed (DB lookup) → if yes, return the previous result (idempotent). Node A can safely retry any number of times. This is why distributed systems require idempotency design - you cannot guarantee exactly-once delivery without it.

---

### 🧠 Mental Model / Analogy

> Distributed computing is like a company with offices in 10 cities. Each office has its own resources (local memory, disk) and makes decisions locally (autonomy). They communicate by email (network - unreliable, delayed). Sometimes an office doesn't respond - you don't know if they're busy, on vacation, or the email was lost. The company still functions: other offices cover the work (fault tolerance). But coordinating a company-wide decision (consensus) is much harder than if everyone sat in the same room - it requires explicit protocols (Raft, Paxos = company's decision-making procedure).

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Distributed computing = multiple computers working together. Benefit: more compute than any single machine. Challenge: failures, slow networks, consistency.

**Level 2:** Key challenges: partial failure (can't tell if node crashed or network failed), consistency (multiple copies of data diverge), coordination (leader election, distributed locks). Key tools: idempotency for retry safety; Raft/Paxos for consensus; CAP theorem for tradeoffs.

**Level 3:** Amdahl's Law bounds the speedup: if 5% of your computation is serial, you can never get more than 20× speedup regardless of nodes. Minimize serial bottlenecks (central coordinator, single-threaded leader). Data locality (Spark/Hadoop): process data where it lives (avoid network transfer) → send computation to data, not data to computation.

**Level 4:** The fundamental limits of distributed computing stem from the **FLP impossibility theorem** (Fischer, Lynch, Paterson, 1985): in an asynchronous distributed system, it's impossible to guarantee consensus with even one faulty node. This means no distributed system can simultaneously guarantee: (1) safety (never returning a wrong result), (2) liveness (always eventually returning a result), and (3) fault tolerance - in the presence of arbitrary node failures. All practical consensus algorithms (Raft, Paxos, Zab) make tradeoffs: they guarantee safety always, but sacrifice liveness during leader election periods. This is why distributed systems design is fundamentally about carefully managing tradeoffs rather than solving an impossible problem.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ DISTRIBUTED COMPUTATION MODEL                        │
├──────────────────────────────────────────────────────┤
│                                                      │
│  [Driver / Coordinator]                              │
│       │ split work                                   │
│       ├────────────────────────────────────────────┐ │
│       ↓           ↓          ↓           ↓        ↓ │
│  [Worker 1]  [Worker 2] [Worker 3] [Worker 4] [W5] │ │
│  process      process    process    FAILED    process│
│  partition 1  part 2     part 3     ← retry!  part 5│
│       │           │          │           │        │  │
│       └───────────┴──────────┴───────────┴────────┘  │
│                   [DIST COMPUTING ← here: aggregate] │
│                   Driver: merge partial results      │
│                   Final result returned to caller    │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Spark WordCount on 10TB:
T=0: Driver submits job
T=1: Spark divides 10TB into 1000 partitions → assigns to 1000 executors
T=2-20: Each executor processes 10GB partition (read+count local words)
   Executor 42 fails at T=15 (partial failure)
   → Spark detects via heartbeat timeout (~5s)
   → Re-assigns partition 42 to spare executor
   → Executor runs partition 42 again (retry = idempotent: count words)
T=25: All 1000 partitions complete (including re-run of partition 42)
T=26: Driver: aggregate all 1000 word count maps → final global count
T=27: Result returned: {"the": 10B, "and": 8B, ...}

[DISTRIBUTED ← YOU ARE HERE: fault tolerance transparent to caller]
Total time: 27s vs. 5.5 hours sequential
```

---

### ⚖️ Comparison Table

| Aspect       | Single Machine                 | Distributed System               |
| ------------ | ------------------------------ | -------------------------------- |
| Scale        | Bounded (hardware max)         | Unbounded (add nodes)            |
| Failure mode | Total failure (easy to detect) | Partial failure (hard to detect) |
| Consistency  | Easy (shared memory)           | Hard (CAP tradeoffs)             |
| Coordination | Local (mutex/semaphore)        | Distributed (Raft, Paxos)        |
| Latency      | Nanoseconds (memory)           | Milliseconds (network)           |
| Cost         | Exponential at high end        | Linear                           |

---

### ⚠️ Common Misconceptions

| Misconception                                   | Reality                                                                                                                                                                                                                                  |
| ----------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Distributed = faster"                          | Distribution adds coordination overhead and network latency. For small datasets, a single machine is faster. Distribution pays off only above a crossover point (dataset > machine capacity, or computation > single-machine capability) |
| "Adding more nodes always improves performance" | Amdahl's Law: serial portions bound the maximum speedup. Beyond the optimal node count, adding more nodes can increase coordination overhead and DECREASE performance                                                                    |
| "The network is reliable"                       | The most common mistake in distributed system design. Network partitions, dropped packets, high latency, and split-brain scenarios must be assumed and handled                                                                           |

---

### 🚨 Failure Modes & Diagnosis

**1. Split-Brain - Two Leaders Simultaneously**

**Symptom:** Two nodes both believe they are the cluster leader. Both accept writes. Data diverges. After recovery, data conflicts are discovered.

**Root Cause:** Network partition. Node A can't see Node B (and vice versa). Both assume the other failed and promote themselves to leader.

**Prevention:** Quorum-based consensus (Raft, ZooKeeper): a leader must have acknowledgment from majority (N/2+1) of nodes. During partition, the minority partition can't form a majority → can't elect a leader → no writes accepted → no split-brain.

---

### 🔗 Related Keywords

**Prerequisites:** Networking, Operating Systems
**Builds On This:** Apache Hadoop, Apache Spark, Distributed Systems
**Related:** MapReduce, Apache Hadoop, Distributed Systems

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT        │ Multiple computers as one unified system    │
│ WHY         │ Scale beyond single machine capacity        │
│ CHALLENGES  │ Partial failure, consistency, coordination  │
│ AMDAHL      │ Serial portion limits max speedup           │
│ FALLACIES   │ Network not reliable, not zero latency      │
│ IDEMPOTENCY │ Safe retries in face of partial failure     │
│ CONSENSUS   │ Raft/Paxos for agreeing on state            │
│ ONE-LINER   │ "Many computers, one system - but partial  │
│             │  failure and network unreliability rule"    │
│ NEXT        │ MapReduce → Apache Hadoop                   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE A) Explain the FLP impossibility result in practical terms. What does it mean for a database engineer choosing between consistency and availability? Give a concrete example of a system that chooses availability over consistency and one that chooses consistency.

**Q2.** (TYPE C - Design) A distributed job processing system processes 1M tasks/day. Each task involves: (1) read from DB, (2) call external API, (3) write result to DB. Node failures occur ~3× per day. Design the system to handle failures without duplicate processing or lost tasks.
