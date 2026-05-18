---
id: DST-061
title: Distributed Systems Knowledge Self-Assessment
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-040, DST-050, DST-060
used_by: DST-081
related: DST-040, DST-050, DST-060
tags:
  - distributed
  - assessment
  - meta
  - self-test
  - review
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 61
permalink: /technical-mastery/distributed-systems/knowledge-self-assessment/
---

⚡ TL;DR - A self-assessment covering L1 through L2
Distributed Systems knowledge (DST-001 through
DST-060); use this to identify gaps before advancing
to L3 topics (DST-062+); each section includes
short diagnostic questions and expected answers at
the engineer level.

---

### 📋 Entry Metadata

| #061 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | DST-040 (L2 Interview), DST-050 (Design Patterns), DST-060 (Lab) | |
| **Used by:** | Staff-Level Interview Scenarios (DST-081) | |
| **Type:** | META - Knowledge verification |

---

### 🔥 The Problem This Solves

After completing 60 entries covering Distributed
Systems fundamentals through advanced L2 topics,
you need a structured way to verify what you have
internalized vs what you have only passingly read.
This self-assessment provides that verification.

If you can answer all questions here without
looking anything up, you are ready for L3 topics
(Byzantine fault tolerance, Spanner, distributed
systems research papers).

---

### 📘 How to Use This Entry

1. Read each question.
2. Answer mentally or write it down.
3. Check the expected answer.
4. If you miss a question: revisit the linked entry
   before continuing to L3.

**Scoring:**
- 0-5 correct: Re-read L1 entries (DST-001 to DST-025)
- 6-10 correct: Re-read L2 entries (DST-026 to DST-060)
- 11-15 correct: Ready for L3 (DST-062+)
- 16-20 correct: Strong foundation; interview-ready

---

### ⏱️ Quick-Fire Assessment (20 Questions)

**Answer before reading the expected response.**

---

### 🔩 The 20 Questions

**L1: FOUNDATIONS (DST-001 to DST-025)**

**Q1: What does CAP theorem say? State all three components.**

```
Expected:
A distributed system cannot simultaneously provide
all three of:
  C - Consistency: all nodes see the same data
    simultaneously
  A - Availability: every request receives a response
  P - Partition tolerance: system operates despite
      network partitions

During a network partition, you must choose between
C and A. Partition tolerance is not optional in
distributed systems; the choice is C vs A.

Common mistake: saying "you choose 2 of 3."
Partitions will happen. The real choice: CP vs AP.
```

---

**Q2: What is the difference between vertical and horizontal scaling?**

```
Expected:
Vertical: make one machine bigger (more CPU/RAM/disk).
  Limit: hardware ceiling; single point of failure.
  Benefit: no code changes needed.

Horizontal: add more machines.
  Limit: requires stateless design or sharding.
  Benefit: theoretically unlimited; fault tolerant.
  
When to go horizontal: when vertical ceiling reached,
  or when high availability requires redundancy.
```

---

**Q3: What is consistent hashing and why is it used over simple modulo hashing?**

```
Expected:
Consistent hashing: keys mapped to a ring; each node
  owns an arc of the ring; a key maps to the next
  node clockwise from its hash position.

Why not modulo: if you have N nodes and add one,
  modulo (N+1) remaps ~N/(N+1) of all keys.
  With 100 nodes: adding 1 node remaps 99% of keys.
  
Consistent hashing: adding/removing 1 node remaps
  only ~1/N of keys (the keys on that node's arc).
  Virtual nodes (vnodes) improve load distribution.
```

---

**Q4: What are the four Coffman conditions for deadlock?**

```
Expected:
1. Mutual exclusion: resources held exclusively.
2. Hold and wait: process holds while waiting for more.
3. No preemption: resources cannot be forcibly taken.
4. Circular wait: A waits for B, B waits for A (cycle).

Deadlock requires ALL four simultaneously.
Prevention: eliminate any one condition.
Most practical: eliminate circular wait via lock ordering.
```

---

**Q5: What is the purpose of a circuit breaker in distributed systems?**

```
Expected:
Prevents cascade failures.
When a dependency is slow/failing, the circuit breaker
  stops sending requests (OPEN state).
This prevents:
  - Thread pool exhaustion from waiting on slow responses
  - Cascade: all services waiting for the failing one
  - Resource waste on requests that will fail anyway

States: CLOSED (normal), OPEN (failing fast), HALF-OPEN
  (probe: send one test request, restore if it succeeds).
```

---

**L2: ADVANCED TOPICS (DST-026 to DST-060)**

**Q6: What is the difference between Raft and Paxos?**

```
Expected:
Both solve distributed consensus.

Raft:
  Leader-based. Strong leader handles all proposals.
  Simpler to understand/implement.
  Election: random timeout; first candidate to start
  usually wins (avoids split vote).
  Used by: etcd, CockroachDB, TiKV.

Paxos:
  Multi-Paxos: de-facto leader for efficiency.
  Leaderless in theory; any node can propose.
  More general; harder to understand/implement.
  Liveness issue: dueling proposers can livelock.
  Used by: Google Chubby, Spanner (Multi-Paxos).

Key difference: Raft prioritizes understandability.
  The Raft paper explicitly aims for
  "understandable consensus."
```

---

**Q7: Explain the Saga pattern. When would you use orchestration vs choreography?**

```
Expected:
Saga: sequence of local transactions, each with a
  compensating transaction. Used to replace 2PC
  for long-running distributed transactions.

Choreography: each service publishes an event;
  other services react. Decoupled; no central coordinator.
  Good for: simple, short sagas. Bad for: complex
  flows with many conditions.

Orchestration: central saga orchestrator tells each
  service what to do. More visible; easier to debug.
  Good for: complex flows; business process management.
  Bad for: creates coupling to orchestrator.

Choose orchestration when: steps are complex,
  conditional branches exist, you need visibility.
```

---

**Q8: What is a fencing token and when is it needed?**

```
Expected:
A fencing token is a monotonically increasing number
given to a lock holder when they acquire the lock.
Every write includes the fencing token.
The storage layer rejects writes with a token
lower than the highest seen.

Needed when: a lock holder thinks it holds the lock
  but the lock actually expired (GC pause, network
  partition). Without fencing: two processes both
  think they hold the lock; both write; last write wins
  (unsafe). With fencing: the storage rejects the
  stale lock holder's write (token is lower).

Classic: Redis SETNX lock + GC pause (Redlock critique
  by Martin Kleppmann, 2016).
```

---

**Q9: What is CQRS and when should you NOT use it?**

```
Expected:
CQRS: Command Query Responsibility Segregation.
  Separate write model (normalized, handles commands)
  from read model (denormalized, handles queries).
  Read model updated asynchronously from write events.

When NOT to use:
  Simple CRUD apps where sync reads suffice.
  When eventual consistency on reads is unacceptable.
  Small teams where operational complexity outweighs
  benefits. When query patterns are uniform (no
  need for a separately optimized read model).

Use CQRS when: write and read access patterns differ
  dramatically (e.g., write once, read 1000 different
  ways), or when you need read scaling independent
  of write scaling.
```

---

**Q10: What are the three properties that must hold for a CRDT merge function?**

```
Expected:
A CRDT merge function must be:
1. Commutative:  merge(A, B) = merge(B, A)
2. Associative:  merge(A, merge(B,C)) = merge(merge(A,B),C)
3. Idempotent:   merge(A, A) = A

These ensure: regardless of the order replicas sync,
  the final merged state is always the same.
  No coordinator needed. No conflict possible.

Example: G-Counter merge = element-wise MAX.
  MAX is commutative, associative, and idempotent. ✓
```

---

**Q11: State the FLP impossibility theorem and its practical implication.**

```
Expected:
FLP (Fischer, Lynch, Paterson, 1985):
  In an asynchronous distributed system with at least
  one crash-stop process failure, there is no
  deterministic algorithm that can guarantee all three
  consensus properties simultaneously:
  - Validity
  - Agreement
  - Termination

Practical implication:
  Raft/Paxos guarantee validity + agreement (safety).
  They sacrifice termination (liveness): may not
  terminate if quorum is unavailable.
  This is the correct trade-off: safety is paramount;
  a system that halts rather than decides wrongly is safer.
  Real networks are partially synchronous (not fully
  async), which is why Raft terminates in practice.
```

---

**Q12: What is tail latency and why does it matter more than mean latency?**

```
Expected:
Tail latency: high-percentile latency (P99, P999).
  P99 = 99th percentile: 1% of requests take this long.

Why it matters more than mean:
  Mean hides outliers. A service with P50=1ms and
  P99=1000ms has mean ≈11ms. 11ms looks fine;
  1000ms is a user-visible problem.
  
  At scale: 1% of 10,000 requests/sec = 100 users/sec
  experiencing 1000ms latency.
  
  Fanout: if 10 services are called in serial, each
  with P99=20ms, the end-to-end P99 is dominated by
  at least one service hitting its P99 (≈10×20ms in
  worst case serial). Monitor and optimize P99.
```

---

**Q13: What is the confused deputy problem?**

```
Expected:
A confused deputy is a security vulnerability where
a service with elevated privileges is tricked into
performing unauthorized actions on behalf of a
less-privileged caller.

Example:
  Service A (user-facing, limited trust) calls
  Service B (internal, high trust) with a user's
  request. Service B trusts Service A and performs
  the action without re-verifying the original
  user's authorization. Attacker compromises Service A
  → accesses all data via Service B's privilege.

Fix: Service B must verify the ORIGINAL caller's
  authorization, not just that the caller is Service A.
  Pass the original JWT/token through the call chain.
```

---

**Q14: What does "eventual consistency" actually guarantee?**

```
Expected:
Eventual consistency guarantees:
  If no new updates are made to an object, eventually
  all accesses to that object will return the last
  updated value.

It does NOT guarantee:
  - When convergence will happen
  - That all nodes have the same value at any given time
  - Order of writes from different clients (without
    additional mechanisms like vector clocks)

Practical: in most systems with healthy replication,
  convergence happens within milliseconds to seconds.
  But during network partitions or high write rates,
  staleness windows grow.
```

---

**Q15: When would you use event sourcing? When should you NOT?**

```
Expected:
Use when:
  - Full audit trail required (compliance, finance)
  - Time-travel queries needed
  - Multiple read models needed from same events
  - Domain model changes frequently

Do NOT use when:
  - Simple CRUD with no audit requirement
  - Team is small and unfamiliar with event sourcing
  - Query patterns are simple and uniform
  - Storage cost of event log is prohibitive
  
Complexity cost: schema evolution (upcasting),
  snapshot management, event replay time, new
  consistency model to reason about.
```

---

**APPLIED QUESTIONS (L2)**

**Q16: Design question: your Kafka consumer is lagging. What do you check first?**

```
Expected (in order):
1. Consumer lag metric (kafka_consumer_group_lag):
   is it growing (worse) or stable (manageable)?
2. Consumer throughput: is the consumer processing
   rate lower than the producer rate?
3. Partition count: can parallelism be increased
   (add consumers up to partition count)?
4. Consumer processing time: is one message type
   taking much longer than others?
5. GC pauses: is the consumer JVM pausing?
6. External dependencies: is the consumer slow
   because its downstream (DB write) is slow?
7. Rebalance loop: is the group frequently rebalancing
   (consumer timeout too short under load)?
```

---

**Q17: Your distributed database is showing split-brain. What happened and how do you fix it?**

```
Expected:
Split-brain: two nodes both believe they are the
  primary/leader simultaneously. Both accept writes.
  Data diverges.

Cause: network partition + quorum failure.
  If quorum was not required for leadership, both
  sides of a partition can elect a leader.

Detection: two nodes each report being primary.
  Duplicate writes visible in data.

Fix:
1. Require quorum for leadership (prevents it).
2. STONITH (Shoot The Other Node In The Head):
   fencing mechanism that kills the stale leader.
3. Fencing tokens: storage rejects writes from
   stale leader.

Immediate: take the stale leader offline, reconcile
  diverged data (manual or automated conflict resolution).
```

---

**Q18: Describe the write path of a Raft cluster.**

```
Expected:
1. Client sends write to leader.
2. Leader appends entry to its local log (uncommitted).
3. Leader sends AppendEntries RPC to all followers.
4. When quorum of followers (N/2+1) acknowledges:
   leader marks entry as committed.
5. Leader applies committed entry to state machine.
6. Leader sends response to client.
7. Leader notifies followers of commit in next
   AppendEntries (commitIndex).
8. Followers apply committed entry to their state machine.

Key: entry is not applied until committed.
Committed = durable on quorum (safe even if leader dies).
```

---

**Q19: What is backpressure and how do you implement it?**

```
Expected:
Backpressure: mechanism to propagate slowness from
  a consumer upstream to a producer, preventing
  the producer from overwhelming the consumer.

Without: unbounded queue → OOM → crash.

Implementation options:
1. Bounded queue: producer blocks when queue is full
   (natural backpressure via blocking).
2. Reactive Streams: consumer signals demand;
   producer only sends what consumer requests.
3. gRPC flow control: built-in backpressure via
   HTTP/2 flow control windows.
4. Reject with 429: API gateway rejects when
   downstream buffer is full; client backs off.

Key metric: queue depth. Alert when sustained >50%
  capacity.
```

---

**Q20: What is the difference between a Saga and a 2PC transaction?**

```
Expected:
2PC (Two-Phase Commit):
  Phase 1: coordinator asks all participants to PREPARE.
  Phase 2: if all prepared: COMMIT; else: ROLLBACK.
  Strong consistency: atomic across all participants.
  Problems: blocking (coordinator crash = all blocked),
  not partition-tolerant, slow (2 round trips min).

Saga:
  Sequence of local transactions, each published
  as events. Compensating transactions undo earlier
  steps if a later step fails.
  Eventual consistency: temporary inconsistency visible.
  Problems: no atomicity guarantee; compensating
  transactions must be idempotent; semantic rollback
  (not true rollback - compensations may not fully undo).

Use 2PC: single datacenter, short transactions,
  strong consistency required.
Use Saga: long-running transactions, multi-service,
  eventual consistency acceptable.
```

---

### 📶 Scoring Guide

```
SCORING:

0-5 correct:
  Re-read L1 foundations (DST-001 to DST-025).
  Focus on: CAP, scaling, consistency, fault tolerance.

6-10 correct:
  L1 solid. Re-read L2 entries you missed.
  Focus on the specific concepts you struggled with.

11-15 correct:
  Good L2 knowledge. Minor gaps remain.
  Review the 5-9 questions you missed before L3.
  Ready for most senior engineer interviews.

16-19 correct:
  Strong foundation. Minor edge cases needed.
  Ready for L3 content and staff-level topics.

20/20 correct:
  Excellent. Ready for L3 (DST-062 onward):
  Byzantine fault tolerance, Spanner, research papers,
  distributed systems design at planetary scale.
```

---

### ⚖️ Comparison Table

| Topic Area | Questions | Key DST Entries |
|---|---|---|
| **CAP + Scaling** | Q1, Q2 | DST-001 to DST-010 |
| **Data Management** | Q3, Q10, Q15 | DST-011 to DST-020 |
| **Service Coordination** | Q5, Q7, Q8 | DST-021 to DST-030 |
| **Consensus + Clocks** | Q6, Q11 | DST-031 to DST-045 |
| **Patterns + Performance** | Q9, Q12, Q19, Q20 | DST-043 to DST-056 |
| **Security** | Q13 | DST-057 |
| **Operations** | Q14, Q16, Q17, Q18 | DST-038 to DST-060 |

---

### ⚠️ Common Gaps Found

| Gap | Why People Miss It | Entry to Review |
|---|---|---|
| FLP vs CAP | Conflated; FLP is about consensus, CAP is about storage | DST-058, DST-015 |
| Fencing tokens | Know Redlock, miss the race condition it creates | DST-047 |
| CRDT properties | Know the concept; can't state the three merge properties | DST-051 |
| Saga compensation | Know Saga pattern; unclear what "compensating transaction" means | DST-043 |
| Tail latency math | Know P99 matters; can't explain why P99 compounds with fanout | DST-056 |

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ READY FOR L3?  │ Score 16+ on this self-assessment      │
│ ENTRY RANGE    │ This covers DST-001 through DST-060    │
│ L3 TOPICS      │ DST-062 onward: BFT, Spanner, papers  │
├────────────────┼────────────────────────────────────────┤
│ TOP GAPS       │ FLP vs CAP, fencing tokens, CRDT props │
│ ALWAYS ASKED   │ CAP, consistency, Raft, Saga, 2PC     │
├────────────────┼────────────────────────────────────────┤
│ ONE-LINER      │ "You don't know distributed systems    │
│                │  until you can explain it to a junior  │
│                │  AND to a principal engineer."         │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

Self-assessment is more valuable than re-reading.
Reading gives the illusion of understanding.
Attempting to recall and explain without notes
reveals actual gaps. The discipline of answering
"can I explain this clearly without looking it up?"
is the difference between knowing a concept and
being able to use it in a design discussion or
incident response. For every distributed systems
concept you study: close the material, state the
concept in your own words, draw the failure mode,
write the fix. If you struggle with any step, that
is your actual knowledge gap, not the parts you
re-read and found familiar.

---

### 💡 The Surprising Truth

Research on knowledge retention shows that testing
yourself (retrieval practice) is significantly more
effective than re-reading for long-term retention.
A 2008 study (Roediger & Karpicke) found that
students who tested themselves retained 80% of
information after a week, versus 36% for students
who re-read the material. For distributed systems
specifically: the concepts that are hardest to
retain (FLP, fencing, CRDTs) are the ones most
likely to appear in system design interviews because
interviewers know they distinguish engineers who
have truly internalized the concepts from those who
have only read about them. Self-testing is not
just evaluation - it is the most efficient study
strategy for technical interviews.

---

### ✅ Mastery Checklist

1. [SELF-ASSESS] Take the 20-question test without
   looking anything up. Score yourself honestly.
2. [REVISIT] For any question you scored less than
   full marks: go to the linked entry and re-read
   the 🔩 First Principles and ✅ Mastery Checklist.
3. [TEACH] Pick 3 concepts from L2 that you found
   hardest. Explain each one out loud to an imaginary
   junior engineer. If you get stuck: study gap found.
4. [DESIGN] Without notes: sketch the write path
   of a Raft cluster (Q18). Draw the nodes, the
   messages, and the commit sequence.
5. [ADVANCE] Score 16+? Proceed to DST-062
   (Raft Internals) and the L3 content.
