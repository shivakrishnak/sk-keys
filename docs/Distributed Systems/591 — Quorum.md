---
layout: default
title: "Quorum"
parent: "Distributed Systems"
nav_order: 591
permalink: /distributed-systems/quorum/
number: "0591"
category: Distributed Systems
difficulty: ★★★
depends_on: Distributed Systems, Replication Strategies, CAP Theorem, Leader Election
used_by: Raft, Paxos, Consistent Hashing, Distributed Locking, Split Brain
related: Replication Strategies, Split Brain, Raft, Paxos, Consistent Hashing
tags:
  - distributed
  - consensus
  - reliability
  - algorithm
  - deep-dive
---

# 591 — Quorum

⚡ TL;DR — A quorum is the minimum number of nodes that must agree for a distributed operation to be considered valid; requiring majority agreement (N/2+1) mathematically prevents two disjoint partitions from both proceeding, eliminating split-brain.

| #591            | Category: Distributed Systems                                             | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------ | :-------------- |
| **Depends on:** | Distributed Systems, Replication Strategies, CAP Theorem, Leader Election |                 |
| **Used by:**    | Raft, Paxos, Consistent Hashing, Distributed Locking, Split Brain         |                 |
| **Related:**    | Replication Strategies, Split Brain, Raft, Paxos, Consistent Hashing      |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A 5-node cluster with no quorum requirement — any operation that reaches ANY node
proceeds. A network partition splits the cluster 3-2. The group of 3 elects a leader
and accepts writes. The group of 2 also elects a leader and accepts writes. Both
groups proceed independently, accepting conflicting changes. When the partition heals,
the cluster has two divergent histories with no principled way to merge them.

**THE INVENTION MOMENT:**
Quorum is the mathematical proof that split-brain is avoidable. If you require a
MAJORITY to proceed, then in any possible partition, at most ONE partition can form
a majority. The minority partition cannot proceed. This is not a protocol — it's
an arithmetic property of majority (N/2+1): two disjoint sets cannot both exceed N/2.

---

### 📘 Textbook Definition

A **quorum** is a subset of nodes in a distributed system that must participate for an operation to be valid. A **majority quorum** requires `⌊N/2⌋ + 1` nodes out of N. The fundamental property: any two majority quorums over the same set of N nodes share at least one common member. This **intersection property** ensures: if a write is acknowledged by a quorum, any subsequent read quorum will include at least one node that saw the write. Quorums are used in consensus protocols (Paxos Phase 1 and 2, Raft commit), leader election, and Dynamo-style read/write configurations. A generalisation: `W + R > N` for write quorum W and read quorum R guarantees that every read sees the latest write.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A quorum is the majority rule for distributed systems: any decision needs more than half the nodes to agree, so only one partition can ever decide at a time.

**One analogy:**

> Quorum is like a parliamentary vote that requires 51% to pass. If the parliament splits into two factions, only the faction with more than 50% of members can pass legislation. The smaller faction — even if unanimous — cannot form a quorum. This prevents two factions from simultaneously passing contradictory laws.

**One insight:**
The quorum intersection property is why Paxos and Raft are safe: any two quorums (e.g., Phase 1 quorum and Phase 2 quorum) must overlap. The overlapping node carries information from the first quorum into the second — preventing the second from making a decision that contradicts the first. The entire correctness argument of both Paxos and Raft reduces to this single arithmetic property.

---

### 🔩 First Principles Explanation

**THE INTERSECTION PROOF:**

```
N nodes: {1, 2, 3, 4, 5}
Majority = floor(5/2) + 1 = 3

Quorum A (any 3 nodes): e.g., {1, 2, 3}
Quorum B (any 3 nodes): e.g., {3, 4, 5}
Intersection: {3} — non-empty ✓

Could A and B be disjoint?
  |A| + |B| = 3 + 3 = 6 > 5 = N
  → Pigeonhole: they MUST share at least one element
  → Two majority quorums can NEVER be disjoint

For N=5: minority = 5 - 3 = 2 nodes
  The split that maximises minority: {3 majority} vs {2 minority}
  2-node side cannot form a quorum → cannot elect, cannot commit
```

**QUORUM IN PAXOS:**

```
Paxos Phase 1 Quorum: {A1, A2, A3}  (3/5)
Paxos Phase 2 Quorum: {A2, A3, A4}  (3/5)
Overlap: {A2, A3}

A2 and A3 saw Phase 1's prepare → they carry Phase 1's information
into Phase 2. Phase 2 cannot "forget" what Phase 1 established.
This intersection is WHY Paxos never chooses two different values.
```

**QUORUM TUNING IN DYNAMO-STYLE SYSTEMS:**

```
N = number of replicas for a key
W = write quorum (minimum replicas that must ACK a write)
R = read quorum (minimum replicas queried for a read)

Consistency rule: W + R > N
Availability:     min(W,R) < N (can tolerate N-min(W,R) failures)

Examples (N=5):
┌─────┬─────┬─────────────┬──────────────────────────────────┐
│  W  │  R  │ Consistent? │ Use case                         │
├─────┼─────┼─────────────┼──────────────────────────────────┤
│  3  │  3  │ Yes (W+R=6) │ Strong reads, balanced           │
│  1  │  5  │ Yes (W+R=6) │ Writes fast, reads slow          │
│  5  │  1  │ Yes (W+R=6) │ Writes slow, reads fast (rare)   │
│  1  │  1  │ No (W+R=2)  │ Best effort, fast but stale reads│
│  2  │  2  │ No (W+R=4)  │ Still not consistent             │
└─────┴─────┴─────────────┴──────────────────────────────────┘
```

**FLEXIBLE QUORUMS:**
Beyond majority, any family of subsets where every two members intersect can
be used as a quorum system. For read-heavy workloads: W=N, R=1 (all writes go
to all replicas, reads need only one — reads are cheaper, writes are expensive).
For write-heavy: W=1, R=N. Majority is just the symmetrical default.

---

### 🧪 Thought Experiment

**EVEN VS ODD NODE COUNTS:**
4-node cluster, majority = 3. A partition splits 2-2. Neither side has 3/4 majority.
NEITHER side can elect a leader or commit writes. The entire cluster is UNAVAILABLE.

5-node cluster, majority = 3. A partition splits 3-2. The 3-node side has majority.
The 3-node side remains available. The 2-node side is unavailable.

**THE LESSON:** Even numbers of nodes are generally bad for quorum systems: they
maximise the chance of a symmetric partition that renders the entire cluster unavailable.
This is why etcd documentation recommends 3, 5, or 7 nodes — never 4 or 6.

**QUORUM DURING ROLLING UPDATES:**
5-node cluster, 1 node taken down for update. 4 nodes remain. Majority = floor(5/2)+1 = 3.
4 - 3 = 1 more failure can be tolerated while the update is in progress.
If a second node fails during the update: only 3/5 remain — still a quorum (barely).
If a third node fails: 2/5 < 3 — cluster becomes UNAVAILABLE.
Rule: stagger rolling updates to minimize the concurrent reduction in quorum headroom.

---

### 🧠 Mental Model / Analogy

> Quorum is like a key that requires signatures from a majority of key-holders
> to open a vault. If the key-holders split into two groups — even if each group
> is unanimous — only the group with the majority of signatures can open the vault.
> The vault is designed so that two groups can never simultaneously open it,
> because you can't get majority signatures from two separate groups at the same time.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** A quorum is a group of servers that must all agree before a decision counts. The quorum must be more than half the total — this ensures only one group can form a quorum at a time, even if the cluster is split.

**Level 2:** Majority quorum (N/2+1) has the intersection property: any two quorums share at least one node. This overlapping node carries information between quorums, ensuring no conflicting decisions can be made independently. This is the core of Paxos and Raft safety.

**Level 3:** In Dynamo-style databases (Cassandra, DynamoDB), W and R are configurable. The consistency guarantee is W + R > N. For writes on N=5: W=3 requires majority confirmation; reads with R=3 will always hit at least one node with the latest write. Quorum failures: if fewer than W nodes ACK a write, the write fails. If fewer than R nodes are available for a read, the read fails.

**Level 4:** Production quorum systems must handle "phantom" quorums during cluster reconfiguration. When nodes are added or removed, the quorum size changes. A transition where old quorum Q1 and new quorum Q2 don't intersect is a correctness hazard. Raft's joint consensus (Joint Quorum = Q1 ∩ Q2 must be satisfied simultaneously) handles this safely. A "flexible quorum" system can use asymmetric quorums (EPaxos uses this to optimise for multi-leader commit without a fixed leader).

---

### ⚙️ How It Works (Mechanism)

**Checking quorum in Raft:**

```go
func (r *Raft) checkQuorum(matchIndexes []int) bool {
    // Sort matchIndex values descending:
    sort.Sort(sort.Reverse(sort.IntSlice(matchIndexes)))
    // The N/2+1-th largest value is the quorum-committed index:
    quorumIndex := matchIndexes[len(matchIndexes)/2]
    return quorumIndex > r.commitIndex
    // If quorumIndex > commitIndex: majority have this index → commit it
}
```

**Cassandra quorum monitoring:**

```bash
# Check how many nodes constitute a quorum for a keyspace:
nodetool status
# Count total nodes (N). Quorum = floor(N/2) + 1.

# For replication_factor=3, quorum=2:
# W=QUORUM + R=QUORUM → 2 + 2 = 4 > 3 → consistent reads
cqlsh> CONSISTENCY QUORUM;
cqlsh> SELECT * FROM users WHERE id='abc'; -- reads from 2/3 replicas
```

---

### ⚖️ Comparison Table

| Config       | Write Quorum | Read Quorum | Consistency  | Fault Tolerance          |
| ------------ | ------------ | ----------- | ------------ | ------------------------ |
| ALL          | N            | 1           | Strong       | 0 failures for writes    |
| QUORUM       | N/2+1        | N/2+1       | Strong       | (N-1)/2 failures         |
| ONE          | 1            | 1           | Weak         | N-1 failures for reads   |
| LOCAL_QUORUM | local N/2+1  | local N/2+1 | Local strong | Local partition tolerant |

---

### ⚠️ Common Misconceptions

| Misconception                          | Reality                                                                                                                                                        |
| -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| More replicas = more quorum safety     | Safety depends on the RATIO (majority), not just count. N=100, W=51 is the same ratio as N=5, W=3                                                              |
| W=1 with R=N is never used in practice | It's used when reads are cheap but writes must be lightning fast (write-optimised workloads with strong read consistency)                                      |
| Quorum prevents all data conflicts     | Quorum prevents split-brain decisions but doesn't prevent concurrent conflicts within a single quorum window — those need additional concurrency control       |
| Any set of N/2+1 nodes is equivalent   | In geographically-distributed systems, a quorum that spans datacentres incurs cross-DC latency. LOCAL_QUORUM (Cassandra) uses only local nodes for performance |

---

### 🚨 Failure Modes & Diagnosis

**Quorum Loss (Cluster Unavailable)**

Symptom: All writes and consensus operations fail; etcd/Consul reports "no leader";
Raft election cannot complete.

Cause: More than N/2 nodes are unreachable (failures + network partition exceeds quorum threshold).

Diagnosis:

```bash
# etcd:
etcdctl endpoint status --cluster  # shows which members are reachable
etcdctl endpoint health --cluster  # health check per endpoint

# If quorum is lost, etcd enters read-only mode for data safety.
# Recovery: fix network/node failures until majority are reachable.
```

---

### 🔗 Related Keywords

- `Split Brain` — the failure quorum prevents; two partitions both believing they're authoritative
- `Raft` — uses quorum commit: N/2+1 ACKs before an entry is considered committed
- `Paxos` — quorum intersection is the safety invariant that makes both Phase 1 and Phase 2 safe
- `Replication Strategies` — W and R quorum tuning for Dynamo-style systems

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  MAJORITY QUORUM: N/2 + 1 nodes must agree               │
│  INTERSECTION: any two quorums share ≥1 node             │
│  SPLIT-BRAIN PREVENTION: only one partition can have     │
│    majority at any time                                  │
│  DYNAMO RULE: W + R > N → read always sees latest write  │
│  CHOOSE ODD N: even N risks symmetric partition stall    │
│  N=3: quorum=2, tolerates 1 failure                      │
│  N=5: quorum=3, tolerates 2 failures                     │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A 6-node cluster uses majority quorum (4/6). A network partition creates a 3-3 split. What happens? Compare this to a 5-node cluster with a 3-2 split. Which cluster design is more resilient to a 50/50 partition? Now explain why databases like etcd and ZooKeeper explicitly recommend odd numbers.

**Q2.** Cassandra has N=6 replicas for a key (replication factor 6). You set W=4, R=3. Is W+R > N satisfied? What is the maximum number of node failures that still allows writes to succeed? What is the maximum number that allows reads? If you lose 3 nodes simultaneously, can you still read? Can you still write? Design a W/R configuration for N=6 that tolerates 2 simultaneous node failures for BOTH reads and writes, while minimising the total number of nodes contacted per operation.
