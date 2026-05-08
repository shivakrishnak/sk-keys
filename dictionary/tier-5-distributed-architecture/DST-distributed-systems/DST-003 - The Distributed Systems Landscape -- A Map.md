---
id: DST-003
title: The Distributed Systems Landscape -- A Map
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★☆☆
depends_on:
used_by:
related:
tags:
  - dst
  - foundational
  - mental-model
status: draft
version: 1
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 3
permalink: /dst/the-distributed-systems-landscape----a-map/
---

# DST-003 - The Distributed Systems Landscape -- A Map

⚡ TL;DR - The distributed systems landscape spans consistency (CAP/PACELC), coordination (Raft, Paxos), resilience (circuit breaker, saga), and observability (tracing, clocks) — this map shows how all the concepts connect.

| DST-003         | Category: Distributed Systems      | Difficulty: ★☆☆ |
| :-------------- | :--------------------------------- | :-------------- |
| **Depends on:** | DST-001, DST-002                   |                 |
| **Used by:**    | DST-006                            |                 |
| **Related:**    | DST-001, DST-002, DST-004, DST-005 |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Distributed systems concepts feel like a disconnected
collection of keywords: CAP theorem, Paxos, saga, CRDT,
circuit breaker. Without a map, it's unclear how they
relate, which applies to which problem, and in what
order to learn them.

**THE BREAKING POINT:**
An engineer learns about Raft (consensus), then CAP
(consistency trade-off), then sagas (distributed txns),
without a framework connecting them. They can't see
that Raft solves leader election, CAP explains why
strong consistency costs availability, and sagas are
the consequence of choosing availability over strong
consistency in the CAP space.

**THE INVENTION MOMENT:**
No single inventor; accumulated field structure. Martin
Kleppmann's "Designing Data-Intensive Applications"
(2017) provided the most comprehensive map of the field.
Kyle Kingsbury's Jepsen analyses provided empirical
evidence of which systems actually meet their guarantees.

**EVOLUTION:**
The landscape evolved as distributed systems entered
mainstream engineering: 2000s (Google papers: GFS, Bigtable,
MapReduce) → 2007 (Amazon Dynamo, Cassandra) → 2012
(Google Spanner, Kafka) → 2017 (Kafka exactly-once,
FoundationDB) → 2020s (FoundationDB, CockroachDB, CRDT-native
databases). The frontier is now verifiable distributed
systems (TLA+, Jepsen).

---

### 📘 Textbook Definition

The distributed systems landscape organises into five
problem domains: **Consistency** (how do nodes agree
on state?), **Ordering** (how do we sequence events
without a global clock?), **Coordination** (how do
nodes elect leaders and reach consensus?),
**Fault Tolerance** (how do systems survive partial
failures?), and **Observability** (how do we understand
what happened across nodes?). Each domain has theoretical
foundations (impossibility results) and practical
solutions (algorithms, patterns).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Distributed systems problems cluster into five areas — consistency, ordering, coordination, fault tolerance, and observability — each with theory and practical solutions.

**One analogy:**

> The distributed systems landscape is like a city map.
> There are five neighbourhoods (problem domains), each
> with their own streets (algorithms) and famous landmarks
> (impossibility results). Without the map, you wander;
> with the map, you know which neighbourhood has the
> solution you need.

**One insight:**
Every distributed systems pattern exists because of a
specific theoretical constraint (CAP theorem, FLP
impossibility, two generals). Understanding the constraint
first makes the pattern inevitable rather than arbitrary.

---

### 🔩 First Principles Explanation

**THE FIVE DOMAINS:**

```
1. CONSISTENCY
   Theory:    CAP theorem, PACELC
   Models:    Strong, eventual, causal, linear
   Patterns:  CRDT, quorum reads, read-your-writes
   DBs:       Spanner (strong), Dynamo (eventual)

2. ORDERING
   Theory:    Lamport (no global clock)
   Algorithms: Lamport clock, vector clock, hybrid
   Patterns:  Event sourcing, total-order broadcast

3. COORDINATION
   Theory:    FLP impossibility
   Algorithms: Paxos, Raft, Zab (Zookeeper)
   Patterns:  Leader election, distributed lock
   Tools:     Zookeeper, etcd, Consul

4. FAULT TOLERANCE
   Theory:    Byzantine fault tolerance
   Patterns:  Circuit breaker, bulkhead, saga,
              idempotency, retry, timeout
   Infra:     Chaos engineering (Netflix)

5. OBSERVABILITY
   Tools:     Distributed tracing (Jaeger, Zipkin)
   Patterns:  Correlation ID, structured logging
   Metrics:   Latency percentiles, error budgets
```

**CORE INVARIANTS:**

1. Theory defines what is possible and impossible — the ceiling, not the floor.
2. Algorithms achieve what theory permits — no more.
3. Patterns are engineering solutions within the algorithm constraints.
4. Observability is the prerequisite for diagnosing all other domains.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** The five domains represent irreducible problem areas in any distributed system.
**Accidental:** Reinventing solutions in domains with well-established algorithms (e.g., implementing your own leader election).

---

### 🧪 Thought Experiment

**SETUP:**
You're designing a distributed payment system. Map
your requirements to the five domains.

**DOMAIN MAPPING:**

```
Requirement: "Every payment must be processed exactly once"
  -> Domain: Fault Tolerance
  -> Solution: Idempotency key + at-least-once delivery

Requirement: "Two concurrent payments can't overdraw account"
  -> Domain: Consistency (strong)
  -> Solution: Linearizable reads; or Paxos/Raft-based
     optimistic concurrency

Requirement: "Audit log must show exact order of all events"
  -> Domain: Ordering
  -> Solution: Total-order broadcast (Kafka partition key)

Requirement: "System stays available if one region goes down"
  -> Domain: Fault Tolerance + Consistency trade-off
  -> CAP: choose availability; accept eventual consistency;
     design compensating transactions

Requirement: "Diagnose the 3-second P99 spike yesterday"
  -> Domain: Observability
  -> Solution: Distributed tracing (Jaeger) + correlation ID
```

**THE INSIGHT:**
Every real-world requirement maps to one or more of
the five domains. The map prevents solution-first
thinking: you don't reach for Raft before identifying
that you have a coordination problem.

---

### 🧠 Mental Model / Analogy

> The five domains are like the specialities in a hospital.
> Consistency is cardiology (vital functions must agree).
> Ordering is neurology (sequence of events matters).
> Coordination is surgery (precise agreement needed).
> Fault tolerance is emergency medicine (survive anything).
> Observability is diagnostics (imaging and tests).
> You need the right specialist; a surgeon can't treat
> a heart attack and a cardiologist can't fix a broken arm.

**Element mapping:**

- Hospital specialty = distributed systems domain
- Patient symptom = system problem/requirement
- Treatment = algorithm or pattern
- Impossibility result = medical limit (can't cure death)

Where this analogy breaks down: in distributed systems,
most problems require multiple domains simultaneously;
medical specialists usually work sequentially.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
All distributed systems problems fall into five categories:
agreeing on data (consistency), ordering events
(ordering), electing leaders (coordination), surviving
failures (fault tolerance), and understanding what
happened (observability).

**Level 2 - How to use it (junior developer):**
When picking up a new distributed systems concept: first
identify which domain it belongs to. Kafka = ordering +
fault tolerance. etcd = coordination. Circuit breaker =
fault tolerance. Jaeger = observability. The domain
tells you what problem it solves before you read a line
of documentation.

**Level 3 - How it works (mid-level engineer):**
The domains have theoretical constraints that shape
practical solutions. Ordering requires Lamport/vector
clocks because there's no global clock. Coordination
requires Paxos/Raft because FLP proves no simpler solution
exists. Consistency trade-offs are bounded by CAP.
Knowing the theory prevents "why don't we just..."
dead ends.

**Level 4 - Why it was designed this way (senior/staff):**
The landscape evolved around impossibility results:
FLP (1985) showed consensus is fundamentally hard →
Raft/Paxos emerged as the least-bad solution. CAP (2000)
showed consistency/availability trade-off is forced →
Dynamo/Cassandra chose availability, Spanner chose
consistency. CRDTs (2011) offer a third path: avoid
consensus entirely via merge-friendly data structures.
The landscape is shaped by what theory permits.

**Expert Thinking Cues:**

- When designing: map requirements to domains before choosing solutions.
- When debugging: identify which domain the failure is in (consistency issue? ordering issue? fault tolerance failure?).
- When evaluating tools: what domain is this tool solving, and what is the theoretical ceiling for its approach?

---

### ⚙️ How It Works (Mechanism)

**Domain-to-tool mapping:**

```
Consistency domain:
  Tools: CockroachDB, Spanner, FoundationDB
  Patterns: CRDT, quorum reads, read-your-writes

Ordering domain:
  Tools: Kafka (total order per partition)
  Patterns: Lamport clock, event sourcing

Coordination domain:
  Tools: etcd (Raft), Zookeeper (Zab)
  Patterns: Leader election, distributed lock,
    configuration management

Fault tolerance domain:
  Tools: Resilience4j, Istio, Chaos Monkey
  Patterns: Circuit breaker, bulkhead, saga,
    retry, idempotency

Observability domain:
  Tools: Jaeger, Zipkin, OpenTelemetry
  Patterns: Distributed tracing, correlation ID,
    structured logging
```

---

### 🔄 The Complete Picture - End-to-End Flow

**How the domains interact in a real system:**

```
Incoming request                     <- YOU ARE HERE
  |
Fault Tolerance layer:
  |-> Timeout, circuit breaker, retry
  |
Coordination layer:
  |-> Which node is leader? (Raft/Paxos)
  |-> Distributed lock if needed
  |
Consistency layer:
  |-> Which consistency model? (strong/eventual)
  |-> Quorum write/read?
  |
Ordering layer:
  |-> Assign Lamport/vector clock to event
  |-> Append to total-order log if needed
  |
Observability layer:
  |-> Correlation ID on all logs/spans
  |-> Trace spans for every hop
  |
Response
```

---

### ⚖️ Comparison Table

| Domain          | Core Problem                     | Key Theory            | Primary Pattern       |
| --------------- | -------------------------------- | --------------------- | --------------------- |
| Consistency     | Nodes disagree on state          | CAP theorem           | CRDT, quorum          |
| Ordering        | Can't order without global clock | Lamport (1978)        | Lamport/vector clock  |
| Coordination    | Consensus is hard                | FLP impossibility     | Raft, Paxos           |
| Fault Tolerance | Any node can fail                | Partial failure       | Circuit breaker, saga |
| Observability   | Can't see global state           | Uncertainty principle | Distributed tracing   |

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                       |
| ----------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| "Distributed systems are a single discipline"         | Five distinct domains; each with its own theory and solutions                                 |
| "Cloud infrastructure solves distributed systems"     | Cloud provides infrastructure; you still design consistency, ordering, and fault tolerance    |
| "Kafka solves all distributed problems"               | Kafka solves ordering + some fault tolerance; consistency and coordination still your problem |
| "If Jepsen tests pass, the system is correct"         | Jepsen tests specific failure scenarios; not all possible failure modes                       |
| "Learn Raft, then you understand distributed systems" | Raft solves coordination; four other domains remain                                           |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Wrong Domain Diagnosis**
**Symptom:** Team applies coordination solution (distributed lock) to consistency problem; doesn't fix it.
**Root Cause:** Problem was stale reads (consistency domain), not leader election (coordination domain).
**Fix:** Map the failure to the correct domain before choosing a solution.

**Mode 2: Missing Observability Layer**
**Symptom:** System fails intermittently; impossible to reproduce or diagnose.
**Root Cause:** No distributed tracing; no correlation IDs; logs not structured.
**Fix:** Add OpenTelemetry instrumentation; structured logging with trace context.

**Mode 3: Fault Tolerance Gap in Saga**
**Symptom:** Partial payment processed; compensating transaction not triggered.
**Root Cause:** Saga coordinator failed; no idempotent compensation.
**Fix:** Saga with outbox pattern; all saga steps idempotent; choreography not orchestration.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[DST-001 - What Is a Distributed System]]
- [[DST-002 - Why Distribution Is Hard]]

**Builds On This (learn these next):**

- [[DST-006 - CAP Theorem]]
- [[DST-022 - Leader Election]]
- [[DST-042 - Circuit Breaker]]

**Alternatives / Comparisons:**

- [[DST-005 - The Distributed Systems Ecosystem Map]] (tool-focused map)

---

### 📌 Quick Reference Card

```
+-----------------------------------------------------+
| WHAT IT IS      A map of 5 distributed systems      |
|                 problem domains + their solutions   |
| PROBLEM         Disconnected knowledge; no framework|
| IT SOLVES       for how concepts relate             |
| KEY INSIGHT     Every DS problem is in one of 5     |
|                 domains; identify domain first      |
| USE WHEN        Designing, debugging, or learning   |
|                 distributed systems                 |
| AVOID           Skipping domain identification and  |
|                 jumping straight to a tool          |
| TRADE-OFF       Map depth vs breadth                |
| ONE-LINER       5 domains: consistency, ordering,   |
|                 coordination, fault-tol, observ    |
| NEXT EXPLORE    DST-006, DST-022, DST-042, DST-049  |
+-----------------------------------------------------+
```

**If you remember only 3 things:**

1. Five domains: consistency, ordering, coordination, fault tolerance, observability.
2. Each domain has a theoretical constraint (CAP, Lamport, FLP) that shapes what solutions are possible.
3. Identify the domain first; choose the pattern second; choose the tool last.

**Interview one-liner:**
"Distributed systems problems fall into five domains: consistency (CAP), ordering (Lamport clocks), coordination (Raft/Paxos, FLP constraint), fault tolerance (circuit breaker, saga), and observability (distributed tracing) — the domain determines which theory and patterns apply."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Before choosing a solution, classify the problem.
Classification reveals which theory applies, which
algorithms are possible, and which patterns are
appropriate. Skipping classification leads to applying
the right solution to the wrong problem.

**Where else this pattern appears:**

- **Database selection** — classifying workload type (OLTP, OLAP, graph) before choosing DB
- **Algorithm selection in DSA** — classifying problem type (search, sort, graph) before choosing algorithm
- **Incident diagnosis** — classifying the failure domain (infra, app, data) before acting

---

### 💡 The Surprising Truth

The "distributed systems" field was considered academic
exotica until 2007, when Amazon published the Dynamo
paper and Google published Bigtable and Chubby (distributed
lock service). These three papers described systems
that handled billions of requests per day using techniques
from 1970s-1990s distributed systems theory. The field
that took decades to mature in academia became the
foundation of modern cloud infrastructure in five years.
Every AWS, GCP, and Azure service you use today is
built on the five domains described in papers written
before 2000.

---

### 🧠 Think About This Before We Continue

**Q1 (System Interaction):** A distributed payment system
has separate services for orders (using Kafka for event
streaming) and inventory (using Postgres with Raft-based
HA). Map each component to its primary distributed systems
domain, and identify where the domains interact.

_Hint:_ Kafka = ordering domain. Postgres+Raft = coordination

- consistency. Saga between them = fault tolerance domain.
  Correlation ID across both = observability. The interaction
  points are where failures are most complex.

**Q2 (Scale):** Google Spanner achieves global strong
consistency across data centres. What are the engineering
consequences of this choice in terms of latency, throughput,
and infrastructure cost, compared to a system that
chooses eventual consistency?

_Hint:_ Spanner: 2-7ms commit latency (TrueTime wait);
requires GPS receivers. Eventual consistency: sub-1ms
local commits; multi-region replication in background.
Strong consistency costs ~10x in latency for cross-region
transactions.

**Q3 (Design Trade-off):** A startup is building their
first distributed system. Should they start with a deep
understanding of all five domains before writing code,
or build first and learn the theory when problems arise?
What are the risks of each approach?

_Hint:_ Build-first risk: design decisions that are hard
to reverse (choosing eventual consistency, then needing
strong). Theory-first risk: over-engineering (implementing
Paxos for a system that could use a simple SQL lock).
Optimum: learn enough theory to make reversible design
decisions; go deep as specific problems arise.
