---
id: DST-071
title: Distributed Consensus Algorithm Design (Raft, Paxos)
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on:
used_by:
related:
tags:
  - dst
  - advanced
  - deep-dive
  - first-principles
status: complete
version: 2
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 71
permalink: /distributed-systems/distributed-consensus-algorithm-design-raft-paxos/
---

# DST-071 - Distributed Consensus Algorithm Design (Raft, Paxos)

⚡ TL;DR - Raft and Paxos are algorithms that allow a cluster of nodes to agree on a single value despite node failures; Raft was designed to be understandable and is now the industry standard; Paxos was the theoretical foundation.

| DST-071         | Category: Distributed Systems               | Difficulty: ★★★ |
| :-------------- | :------------------------------------------ | :-------------- |
| **Depends on:** | DST-021, DST-022, DST-023, DST-026, DST-060 |                 |
| **Used by:**    | DST-066                                     |                 |
| **Related:**    | DST-021, DST-022, DST-023, DST-026, DST-060 |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A distributed system has 5 nodes. They need to agree
on who the leader is. Without a formal algorithm: two
nodes simultaneously declare themselves leader (split
brain); they both accept writes; the cluster has
contradictory state that cannot be resolved. Data is
corrupted.

**THE BREAKING POINT:**
Lamport (1977) described the problem precisely: how
can a set of processes, communicating only via messages,
agree on a single value when some processes may fail?
This is the consensus problem. Without a correct
algorithm, any approach has failure modes that produce
corrupted state.

**THE INVENTION MOMENT:**
Leslie Lamport's Paxos algorithm (1989, published 1998).
Understandable but complex to implement correctly.
Diego Ongaro and John Ousterhout (2014): Raft, designed
explicitly for understandability. Both are now in
production: etcd (Raft), Zookeeper (Zab, Paxos variant),
CockroachDB (Raft), FoundationDB (custom Paxos).

**EVOLUTION:**
Multi-Paxos → Raft (2014) → Flexible Paxos (2016,
reduced quorum for reads) → EPaxos (2012, leaderless
Paxos with higher throughput). The field moves toward
lower latency and higher throughput while maintaining
safety guarantees.

---

### 📘 Textbook Definition

**Consensus** in distributed systems is the problem
of getting a set of nodes to agree on a single value
when any node may fail or messages may be delayed.
Formal requirements: **Safety** — only proposed values
are chosen; at most one value is chosen. **Liveness** —
some proposed value is eventually chosen. **Agreement** —
all nodes that decide, decide the same value. FLP
impossibility: no deterministic algorithm satisfies all
three in an asynchronous system with crashes. Raft and
Paxos relax liveness under partitions (prefer safety;
sacrifice availability).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Raft/Paxos are algorithms for getting distributed nodes to agree on one value — like electing a leader — safely even when nodes crash.

**One analogy:**

> Consensus is like a jury reaching a unanimous verdict
> even if some jurors are sick and can't vote. The jury
> needs a quorum (majority present). The foreman (leader)
> proposes a verdict; the majority votes; that verdict
> is decided. Even if the foreman becomes sick, a new
> foreman is elected by majority vote, and the process
> continues. The verdict can only be changed by a new
> unanimous process.

**One insight:**
Quorum is the key insight: if you require a majority
(N/2+1) to approve any decision, and two majorities
cannot exist simultaneously, then no two decisions can
contradict each other, even if nodes fail.

---

### 🔩 First Principles Explanation

**WHY QUORUM WORKS:**

```
Cluster: 5 nodes (A, B, C, D, E)
Quorum: 3 (majority)

Any two quorums must overlap by at least 1 node.
  Quorum 1: {A, B, C}
  Quorum 2: {C, D, E}
  Overlap: {C}

Node C: knows what Quorum 1 decided AND what
  Quorum 2 is about to decide.
  C ensures Quorum 2 continues from Quorum 1's state.

Result: decisions are never contradictory, even though
  quorums change as nodes fail and rejoin.
```

**RAFT ALGORITHM (SIMPLIFIED):**

```
Phase 1: Leader Election
  - All nodes start as followers
  - If no heartbeat from leader: become candidate
  - Candidate increments term; requests votes
  - Node grants vote if: (a) hasn't voted this term;
    (b) candidate log is >= as up-to-date as voter's
  - First candidate to get majority: becomes leader

Phase 2: Log Replication
  - Leader receives client write
  - Leader appends to its log
  - Leader sends AppendEntries to all followers
  - Followers append to their logs; respond
  - Once majority respond: leader commits
  - Leader sends commit; followers apply to state machine

Phase 3: Safety
  - Only one leader per term (quorum-elected)
  - Committed entries never overwritten
  - Followers only accept entries from current leader
```

**PAXOS vs RAFT:**

```
Paxos:
  + Theoretically proven safe
  - Complex: multiple variants (Basic, Multi, Fast)
  - Implementation leaves many things underspecified
  - Production: requires significant interpretation

Raft:
  + Designed for understandability
  + Explicit leader election
  + Log-based; easier to implement than Paxos
  + Well-specified: the paper specifies edge cases
  - Slightly lower throughput than leaderless variants
  Production: etcd, CockroachDB, TiKV, Consul
```

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Quorum, term numbers, log replication are irreducible for safe consensus.
**Accidental:** Paxos's underspecification of leader election and log management.

---

### 🧪 Thought Experiment

**SETUP:**
A 5-node etcd cluster (Raft). Node A is leader.
Nodes A and B lose network connection to C, D, E.

**WHAT HAPPENS:**

```
Partition:
  Partition 1: {A, B} (old leader A)
  Partition 2: {C, D, E}

Partition 2:
  C, D, E: no heartbeat from A -> election timeout
  C becomes candidate; requests votes from D, E
  D and E vote for C (majority in partition 2)
  C becomes leader of term 2
  Write to C: committed (3/5 = majority of cluster)

Partition 1:
  A continues to think it's leader (it doesn't know)
  Client writes to A: A tries to replicate to B (only 1 follower)
  A cannot commit: needs 3 votes; only has 1 follower
  -> Writes to partition 1 are REJECTED (cannot reach quorum)
  -> No split-brain: old leader A cannot commit

Healing:
  A reconnects to cluster; discovers term 2 > term 1
  A steps down; becomes follower of C
  A's uncommitted entries: overwritten by C's log

Result: NO DATA LOSS for committed writes;
  NO SPLIT-BRAIN; safety maintained throughout
```

---

### 🧠 Mental Model / Analogy

> Raft/Paxos is like a parliamentary voting system
> with a twist: before any bill is passed, you need
> a majority. But if the parliament is split by a
> storm (network partition), the larger group can still
> pass bills (quorum = majority of total). The smaller
> group cannot pass bills without a majority.
> When the storm ends, the smaller group's bills are
> discarded; they adopt the larger group's record.

**Element mapping:**

- Parliament = Raft cluster
- Bill = log entry / write
- Majority = quorum (N/2 + 1)
- Storm = network partition
- Smaller group's bills discarded = uncommitted entries overwritten
- Parliamentary record = Raft log

Where this analogy breaks down: real parliaments can
retroactively ratify bills; Raft only adopts committed
entries from the majority partition.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Raft and Paxos are rules for how a group of computers
vote on decisions so that no two computers ever make
contradictory decisions, even when some computers crash.

**Level 2 - How to use it (junior developer):**
You use Raft indirectly: etcd (leader election, config
storage), Zookeeper, CockroachDB, Consul all implement
consensus internally. You don't implement Raft; you
use systems built on it. Understanding Raft helps you
understand why these systems behave as they do (why
a write to etcd is slow; why a leader election causes
a brief unavailability).

**Level 3 - How it works (mid-level engineer):**
Raft term numbers prevent old leaders from causing
problems: when a node receives a message with an old
term number, it rejects it. When a node receives a
message with a newer term, it immediately becomes a
follower of that term. This is why network-partitioned
nodes can't cause split-brain: their term is stale;
their writes can't reach quorum.

**Level 4 - Why it was designed this way (senior/staff):**
Flexible Paxos (2016, Howard et al.) proved that Raft's
requirement of quorum for both writes AND leader election
is stricter than necessary. For reads, you only need
a quorum with the most recent write quorum (not N/2+1).
This enables asymmetric quorums: fewer nodes needed
for reads than writes. This is the theoretical basis
for Dynamo-style quorum tuning (W + R > N for strong
consistency).

**Expert Thinking Cues:**

- A Raft cluster needs at least 3 nodes for fault tolerance (2 is not fault-tolerant: need majority of 2 = 2).
- Raft leader is a performance bottleneck: all writes go through the leader; multi-Raft or EPaxos (leaderless) for higher throughput.
- etcd write latency (~10ms) includes Raft round trip (leader -> quorum -> commit); this is irreducible.

---

### ⚙️ How It Works (Mechanism)

**Raft cluster state transitions:**

```
Node states:
  FOLLOWER: default; receives heartbeats from leader
  CANDIDATE: election timeout; requests votes
  LEADER: won election; sends heartbeats; accepts writes

Election timeout: randomised (150-300ms in Raft paper)
  Randomization prevents all nodes timing out simultaneously

Log entry lifecycle:
  1. Client sends write to leader
  2. Leader appends entry to log (uncommitted)
  3. Leader sends AppendEntries to all followers
  4. Followers append to log; respond OK
  5. Leader waits for majority OK
  6. Leader commits entry (applies to state machine)
  7. Leader notifies followers to commit
  8. All followers commit (apply to state machine)
  9. Leader responds to client
```

---

### 🔄 The Complete Picture - End-to-End Flow

**Write to an etcd (Raft) cluster:**

```
Client write: SET x=1               <- YOU ARE HERE
  |
Leader receives:
  -> Appends to log (uncommitted)
  -> AppendEntries RPC to followers (2, 3, 4, 5)
  |
Followers 2, 3 respond OK:
  -> Leader has quorum (itself + 2 = 3/5)
  -> Leader commits x=1 to state machine
  |
Leader responds to client: OK
  |
Leader notifies 4, 5 to commit (eventual):
  -> 4, 5 commit when they receive next heartbeat
  |
If leader crashes before step 3:
  -> Uncommitted; new leader elected; client retries
  -> Idempotent operation: same result on retry
If leader crashes after step 5 (committed):
  -> New leader will have the committed entry
  -> Client may not have received response: retry
  -> Idempotency: entry already committed; no duplicate
```

---

### ⚖️ Comparison Table

| Property          | Raft                     | Paxos                     | Zab (ZooKeeper) |
| ----------------- | ------------------------ | ------------------------- | --------------- |
| Understandability | High (designed for this) | Low                       | Medium          |
| Leader-based      | Yes                      | Variant-dependent         | Yes             |
| Throughput        | Medium                   | High (EPaxos)             | Medium          |
| Implementations   | etcd, CockroachDB        | FoundationDB, Chubby      | ZooKeeper       |
| Spec completeness | High                     | Low (many underspecified) | High            |
| Learner nodes     | Yes                      | No (in basic Paxos)       | Observer nodes  |

---

### ⚠️ Common Misconceptions

| Misconception                         | Reality                                                                                       |
| ------------------------------------- | --------------------------------------------------------------------------------------------- |
| "Raft is just Paxos with better docs" | Raft makes different design choices (strong leader, log-based) that simplify implementation   |
| "Quorum = majority = N/2+1"           | Flexible Paxos shows read and write quorums can differ as long as W + R > N                   |
| "Raft guarantees no downtime"         | Raft guarantees safety; liveness may be interrupted during leader election (typically <500ms) |
| "2-node etcd is safer than 1"         | 2-node etcd is less available: majority of 2 = 2; one node down = no quorum                   |
| "Paxos is obsolete"                   | Paxos variants (EPaxos, CASPaxos) are used in FoundationDB, Google Chubby; not obsolete       |

---

### 🚨 Failure Modes & Diagnosis

**Mode 1: Raft Election Storm**
**Symptom:** etcd repeatedly holds elections; write latency spikes every few seconds.
**Root Cause:** Network instability causes leaders to lose quorum; repeated re-elections.
**Diagnostic:**

```bash
kubectl -n kube-system logs etcd-master | grep 'election'
# Look for repeated "became leader" / "started campaign"
```

**Fix:** Increase election timeout; check network stability; reduce etcd leader load.

**Mode 2: Raft Log Divergence After Partition**
**Symptom:** After network heals, some nodes have different state.
**Root Cause:** Expected behaviour; uncommitted entries on old partition overwritten by new leader.
**Fix:** This is correct Raft behaviour; ensure application retries failed writes after leader change.

**Mode 3: etcd Slow due to Leader Bottleneck**
**Symptom:** All etcd writes serialised through leader; P99 latency high under load.
**Fix:** Read from followers for read-heavy workloads (serialise reads via leader only when linearizability needed); consider multi-Raft sharding.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- [[DST-021 - Leader Election]]
- [[DST-022 - Consensus]]
- [[DST-023 - Raft]]
- [[DST-060 - FLP Impossibility]]

**Builds On This (learn these next):**

- [[DST-026 - Paxos]]

**Alternatives / Comparisons:**

- EPaxos (leaderless; higher throughput)
- Viewstamped Replication (similar safety, different mechanism)

---

### 📌 Quick Reference Card

```
+-----------------------------------------------------+
| WHAT IT IS      Algorithm for N nodes to agree on   |
|                 one value despite node failures     |
| PROBLEM         Split-brain: two nodes both think   |
| IT SOLVES       they're leader; data corrupted      |
| KEY INSIGHT     Quorum (majority) ensures two        |
|                 quorums always overlap by >=1 node  |
| USE WHEN        Leader election, distributed locks, |
|                 replicated state machines           |
| AVOID           Implementing from scratch; use etcd |
| TRADE-OFF       Availability sacrifice on partition |
| ONE-LINER       Quorum = only one truth possible    |
| NEXT EXPLORE    etcd, CockroachDB, DST-060 (FLP)   |
+-----------------------------------------------------+
```

**If you remember only 3 things:**

1. Quorum is the key: any two majorities overlap by at least one node; that overlap ensures consistency.
2. Raft has three phases: leader election, log replication, safety; each is clearly specified.
3. Use Raft through battle-tested systems (etcd, CockroachDB); don't implement consensus yourself.

**Interview one-liner:**
"Raft achieves consensus via quorum: a write is committed when a majority of nodes acknowledge it; leader election requires a majority vote; any two majorities overlap, preventing split-brain; Raft was designed for understandability over Paxos, and is now the industry standard via etcd and CockroachDB."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Quorum is a general pattern for achieving agreement
without a single point of failure. Any system that
needs to make a decision without a trusted arbiter
can use quorum: N parties vote; majority wins; single
minority cannot make the decision alone. This principle
applies to database election, human team consensus,
and voting systems.

**Where else this pattern appears:**

- **Database read/write quorums** — DynamoDB, Cassandra: W + R > N for strong consistency
- **Blockchain** — proof-of-work / proof-of-stake is a Byzantine-tolerant consensus mechanism
- **Human organisations** — board votes; supermajority for constitutional changes

---

### 💡 The Surprising Truth

Leslie Lamport submitted the original Paxos paper to
ACM TOCS in 1989. The reviewers rejected it as too
fanciful (the paper described a fictional Greek
parliament passing laws). The paper circulated as a
DEC technical report for 8 years before being
published in 1998. During those 8 years, Lamport's
algorithm was already being implemented in Google's
internal systems. The algorithm that powers etcd,
Zookeeper, CockroachDB, and Google's global infrastructure
spent 8 years unpublished because reviewers found the
presentation style unconventional. Raft (2014) was
designed specifically to address this: Ongaro's primary
design goal was understandability over novelty.

---

### 🧠 Think About This Before We Continue

**Q1 (First Principles):** A 5-node Raft cluster has
nodes A, B, C, D, E. A network partition splits the
cluster into {A, B} and {C, D, E}. Partition 1 had
the old leader (A). Trace the complete sequence of
events that leads to a new leader being elected in
partition 2, including the role of term numbers.

_Hint:_ C, D, E: election timeout; C becomes candidate;
increments term to T+1; requests votes. D, E grant
vote (haven't voted in T+1). C has majority (3/5);
becomes leader of term T+1. A: cannot reach quorum;
writes rejected. When partition heals: A receives message
with term T+1 > T; A steps down immediately.

**Q2 (Design Trade-off):** Raft's election timeout is
randomised (150-300ms). Why is randomisation necessary?
What happens if all 5 nodes have the same election
timeout? Design a pathological scenario where identical
timeouts cause liveness failure (no leader ever elected).

_Hint:_ All nodes timeout simultaneously; all become
candidates; all request votes; votes are split evenly
(each votes for itself); no one reaches majority;
all time out and repeat. This is a livelock: the algorithm
is safe (no wrong leader) but not live (no leader elected).
Randomisation breaks symmetry; one node times out first
and gets elected before others time out.

**Q3 (Scale):** At what cluster size does Raft's quorum
latency become a practical problem? Consider: each
AppendEntries RPC must wait for quorum. With 3 nodes:
1 round trip. With 5 nodes: still 1 round trip (wait
for 3). With 101 nodes: still wait for 51. Is Raft
practical at 101 nodes, and if not, what's the alternative?

_Hint:_ Raft at 101 nodes: quorum = 51. Network is
random; some of the 51 will be slow. P99 write latency
= slowest of 51 responses. Typically: 3 or 5 nodes
is the practical maximum for Raft (3-5 is enough for
fault tolerance). For larger clusters: multi-Raft
(shard into multiple Raft groups of 3-5); used in
TiKV, CockroachDB.
