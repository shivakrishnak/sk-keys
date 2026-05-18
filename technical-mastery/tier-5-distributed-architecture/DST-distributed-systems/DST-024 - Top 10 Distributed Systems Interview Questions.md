---
id: DST-024
title: "Top 10 Distributed Systems Interview Questions"
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★☆☆
depends_on: DST-001, DST-016, DST-018, DST-019
used_by: []
related: DST-016, DST-018, DST-028, DST-029
tags:
  - distributed
  - interview
  - meta
  - foundational
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 24
permalink: /technical-mastery/distributed-systems/interview-questions/
---

⚡ TL;DR - This entry maps the 10 most common distributed
systems interview questions to the core concepts they test,
common wrong answers, and what a strong answer demonstrates;
it serves as both an interview guide and a knowledge map
for the entire category.

---

### 📋 Entry Metadata

| #024 | Category: Distributed Systems | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Meta Entry:** | Maps interview questions to DST category concepts | |
| **Prerequisites:** | DST-001 through DST-023 (all L0-L1 entries) | |
| **Core topics:** | CAP Theorem, Consistency, Idempotency, Delivery Semantics, Replication | |

---

### 🔥 Why This Entry Exists

Distributed systems interviews consistently test the same
conceptual foundations. Knowing the vocabulary and
individual concepts is not sufficient - interviews test
whether you can reason about them under pressure, apply
them to novel scenarios, and identify trade-offs without
prompting.

This entry is a structured guide to the 10 questions that
appear most frequently in distributed systems interviews
at principal-level and above. For each question: the
correct answer, the most common wrong answer, what depth
signals mastery, and which DST entry provides the full
technical foundation.

---

### 📘 The 10 Questions

---

**Q1. Explain the CAP theorem in plain terms.**

**What they're testing:** Do you understand that P is not
optional, and the real choice is C vs A during partitions?

**Wrong answer:** "You can pick any 2 of 3 properties -
consistency, availability, and partition tolerance."
*(This suggests you don't understand that P is mandatory.)*

**Strong answer:**
> "In a distributed system, network partitions are
> inevitable - nodes will lose connectivity. When that
> happens, you must choose: do you maintain consistency
> (return errors rather than stale data) or maintain
> availability (keep serving requests, possibly stale)?
> CP systems like ZooKeeper reject requests from minority
> partitions. AP systems like Cassandra continue serving,
> with eventual convergence after the partition heals.
> The 'CA' option is not real in distributed systems -
> it only exists for single-node systems."

**Depth signal:** Mention PACELC (the trade-off during
normal operation: latency vs consistency), and that many
databases are tunable (Cassandra with QUORUM is CP).

**Reference entry:** DST-016 (CAP Theorem)

---

**Q2. What is the difference between strong consistency
and eventual consistency?**

**What they're testing:** Can you map these to real
systems and describe business implications?

**Wrong answer:** "Strong consistency means the data is
always correct; eventual consistency means it might be
wrong sometimes."
*(Eventual consistency means stale, not wrong. The
data is not corrupted; it's just older.)*

**Strong answer:**
> "Strong consistency (linearizability) means every
> read sees the most recent write, globally. Eventual
> consistency means if no new writes occur, all replicas
> will converge to the same value - but in the meantime,
> different replicas may serve different values.
>
> For financial transactions, stale data means wrong
> decisions (overdraft, oversell) - requires strong
> consistency. For social media feeds, seeing a post
> 2 seconds late is acceptable - eventual consistency
> is fine and cheaper. The choice is always: what is
> the business cost of a stale read?"

**Depth signal:** Name the consistency spectrum (causal,
read-your-writes, monotonic reads between strong and
eventual), and give a concrete system for each level.

**Reference entry:** DST-014 (Consistency), DST-028
(Eventual Consistency)

---

**Q3. What is idempotency and why does it matter?**

**What they're testing:** Understanding of safe retries
and at-least-once delivery systems.

**Wrong answer:** "An idempotent operation is one that
doesn't have side effects."
*(Idempotency is about repetition producing the same
result, not about having no side effects.)*

**Strong answer:**
> "An idempotent operation produces the same result
> whether performed once or many times. `SET x=5` is
> idempotent; `INCREMENT x by 1` is not.
>
> In distributed systems, at-least-once delivery means
> a consumer may receive the same message twice. Without
> idempotency, double processing causes double charges,
> duplicate records, or duplicate emails. With idempotency
> (implemented via unique idempotency keys stored with
> the operation's result), retries are safe.
>
> The implementation: client generates a UUID per operation,
> server stores key+result on first execution, returns
> cached result on duplicate key. Critically: key storage
> and operation must be in the same transaction."

**Depth signal:** Explain why the key and the operation
must be stored atomically, and the failure mode if stored
separately (operation succeeds, key not stored, retry
re-executes).

**Reference entry:** DST-018 (Idempotency)

---

**Q4. Explain the at-least-once vs exactly-once delivery
trade-off.**

**What they're testing:** Understanding of messaging
semantics and what Kafka's "exactly-once" actually means.

**Wrong answer:** "Exactly-once is always better, we
should use it everywhere."
*(Exactly-once has real costs: latency, complexity,
and it is often not achievable end-to-end without
idempotent consumers.)*

**Strong answer:**
> "At-most-once may lose messages but never duplicates -
> used for metrics where losing a data point is acceptable.
> At-least-once guarantees delivery but may duplicate -
> requires idempotent consumers. Exactly-once guarantees
> each message is processed exactly once - very expensive
> to implement and often not achievable end-to-end.
>
> The production default: at-least-once delivery plus
> idempotent consumers achieves the same business result
> as exactly-once, with less complexity. Kafka's
> 'exactly-once semantics' only applies within Kafka -
> writing to an external database still requires an
> idempotent consumer to prevent double processing."

**Depth signal:** Describe the Kafka EOS configuration
(idempotent producer, transactional commits) and why
it still requires an idempotent consumer for external
side effects.

**Reference entry:** DST-019 (Delivery Semantics), DST-018

---

**Q5. How does replication work in a distributed database?**

**What they're testing:** Understanding of leader-follower
vs leaderless, synchronous vs asynchronous, and the
consistency implications.

**Strong answer:**
> "The most common approach is leader-follower: one node
> (primary) accepts all writes, maintains a WAL (write-
> ahead log), and streams log entries to followers.
> Followers apply the log in order, eventually matching
> the leader's state.
>
> With synchronous replication, the leader waits for at
> least one follower to confirm before acknowledging the
> write - no data loss on leader failure. With async,
> the leader acknowledges immediately and replicates in
> the background - lower latency but potential data loss
> if the leader fails before replicating.
>
> The practical implication: reads from followers may
> be stale (replication lag). Financial data should be
> read from the primary. Feed data can be read from
> replicas."

**Depth signal:** Mention the split-brain problem on
leader failover and fencing tokens as the solution.

**Reference entry:** DST-012 (Replication), DST-017
(Leader-Follower Replication), DST-026 (Replication Lag)

---

**Q6. What is sharding and how do you choose a shard key?**

**What they're testing:** Understanding of write scaling
vs read scaling, and the hotspot problem.

**Wrong answer:** "Sharding means distributing data
across multiple servers. You pick any field as the
shard key."
*(Missing: hotspot risk, sequential key anti-pattern,
and the impact on query routing.)*

**Strong answer:**
> "Sharding splits data across multiple nodes, with each
> node owning a subset. Unlike replication (which copies
> data), sharding partitions it - each record lives on
> exactly one shard. This scales write throughput and
> storage linearly with the number of shards.
>
> The shard key determines which shard a record goes to.
> A good key distributes records evenly AND keeps related
> records together (to minimize cross-shard queries).
> Common mistake: using a sequential key like timestamp
> or auto-increment ID - all new records go to the last
> shard, creating a hotspot. Better: hash of user_id.
>
> Cross-shard queries (no shard key in the WHERE clause)
> require scatter-gather across all shards - expensive.
> The shard key should be the field in the most common
> query's WHERE clause."

**Depth signal:** Mention consistent hashing as the
mechanism that makes rebalancing practical, and the
celebrity problem.

**Reference entry:** DST-013 (Sharding), DST-030
(Consistent Hashing)

---

**Q7. What is a network partition and how does your
system handle it?**

**What they're testing:** Whether you understand partitions
are normal events requiring designed behavior, not
exceptional cases.

**Strong answer:**
> "A network partition is when a subset of nodes cannot
> communicate with another subset. Both sides are still
> running, but each sees the other as 'down.' During a
> partition, the system must choose: stop serving (CP)
> or continue with potentially stale data (AP).
>
> For our payment service, we use a CP database
> (PostgreSQL with synchronous replica). During a
> partition, the minority side rejects writes - we
> prefer 'no service' over 'wrong balance.' For our
> notification service, we use an AP approach - sending
> a slightly delayed notification is acceptable; being
> unavailable is not.
>
> Recovery: after partition heals, replicas sync with
> the primary. If using AP, conflict resolution is
> applied (last-write-wins for our preferences store)."

**Depth signal:** Describe fencing tokens preventing
split-brain writes, and the specific CAP classification
of systems in your production stack.

**Reference entry:** DST-010 (Network Partition), DST-016

---

**Q8. Explain the difference between latency and
throughput.**

**What they're testing:** Whether you report percentiles,
understand Little's Law, and know the trade-offs.

**Strong answer:**
> "Latency is the time for a single request to complete.
> Throughput is the rate of completed requests per second.
> They are related via Little's Law: Throughput = Concurrency
> / Latency.
>
> The critical detail: always measure latency as
> percentiles (P99, P99.9), not averages. Averages mask
> outliers. A P99 of 500ms means 1% of users - potentially
> thousands per day - are experiencing half-second waits.
>
> The trade-off: batching improves throughput at the
> cost of latency. For user-facing APIs, I optimize P99
> latency. For data pipelines, I optimize throughput.
> Under saturation, both degrade - adding backpressure
> (rejecting excess requests) prevents latency from
> growing unboundedly."

**Reference entry:** DST-023 (Latency vs Throughput)

---

**Q9. How do health checks and heartbeats work in
practice?**

**What they're testing:** Operational depth, liveness vs
readiness, timeout calculation, and failure scenarios.

**Strong answer:**
> "A heartbeat is a periodic 'I'm alive' signal from a
> node to its monitor. A health check is the inverse:
> a probe from the load balancer or orchestrator to the
> node.
>
> I always separate liveness (is the process running?)
> from readiness (is it ready for traffic?). In Kubernetes:
> liveness probe failure = restart the pod. Readiness
> probe failure = remove from Service endpoints but do
> not restart. This matters when a database is temporarily
> unreachable - the pod should not be restarted (it would
> loop), just taken out of rotation.
>
> The critical parameter is timeout. Too short: false
> positives during GC pauses. Rule of thumb: timeout >
> 5x P99.9 GC pause time. False positives in a Raft
> cluster trigger unnecessary leader elections."

**Reference entry:** DST-020 (Heartbeat and Health Check)

---

**Q10. Design a simple distributed key-value store.**

**What they're testing:** Integration of all L1 concepts:
replication, partitioning, consistency, failure handling.

**Strong answer structure:**
> "I'll design for availability over strict consistency,
> based on typical KV store use cases.
>
> **Data model:** simple string keys, any binary values.
>
> **Partitioning:** consistent hashing across N nodes.
> Each key maps to 3 nodes (replication factor = 3).
>
> **Writes:** client sends to coordinator node, which
> sends to all 3 replicas. Acknowledge after W replicas
> confirm (W=2 for durability with reasonable latency).
>
> **Reads:** client reads from coordinator, which reads
> from R replicas (R=2). Returns value with highest
> timestamp. W + R > N (2+2 > 3) guarantees reading
> the latest write.
>
> **Failure:** if a node is unreachable, hinted handoff:
> coordinator stores the write locally and replays to
> the node when it returns.
>
> **Consistency model:** eventual for default reads.
> QUORUM reads for strong consistency when required."

**Reference entries:** DST-012, DST-013, DST-027, DST-030

---

### 📌 Interview Preparation Checklist

**Must explain clearly:**
- [ ] CAP theorem: C vs A during partitions (P is mandatory)
- [ ] Strong vs eventual consistency with business examples
- [ ] Idempotency: what, why, how to implement
- [ ] At-least-once + idempotent consumer = eventual exactly-once
- [ ] Replication: leader-follower mechanics, lag, failover
- [ ] Sharding: shard key selection, hotspot avoidance
- [ ] Network partitions: expected behavior, recovery
- [ ] Latency vs throughput: percentiles, Little's Law
- [ ] Health check: liveness vs readiness distinction
- [ ] System design: partitioning + replication + quorum

**Red flags interviewers watch for:**
- "CA is a valid CAP choice for distributed systems"
- "Eventual consistency means data might be wrong"
- "Average latency" (without mentioning percentiles)
- "Just use retries" (without mentioning idempotency)
- "Add more replicas for better consistency" (wrong direction)
- No mention of failure scenarios in system design

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ CAP       │ P is mandatory; choose C or A during fault  │
│ CONSISTEN.│ Strong=latest, Eventual=stale not wrong     │
│ IDEMP.    │ Safe to retry; key+operation same txn       │
│ DELIVERY  │ ALO + idempotent consumer = EO behavior     │
│ REPLICATION│ Leader-follower; lag; failover risk        │
│ SHARDING  │ Key selection: uniform + co-located data    │
│ PARTITION │ Expected; pre-designed CP or AP behavior    │
│ LATENCY   │ P50/P95/P99, not average; Little's Law     │
│ HEALTH    │ Liveness=restart; Readiness=remove traffic  │
│ SYSTEM    │ Partition + replicate + quorum W+R>N        │
└─────────────────────────────────────────────────────────┘
```
