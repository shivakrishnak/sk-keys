---
layout: default
title: "Raft"
parent: "Distributed Systems"
nav_order: 586
permalink: /distributed-systems/raft/
number: "0586"
category: Distributed Systems
difficulty: ★★★
depends_on: Leader Election, Log Replication, Quorum, Consensus, State Machine Replication
used_by: etcd, Kubernetes, CockroachDB, TiKV, Distributed Locking
related: Paxos, Zab, Multi-Paxos, Log Replication, State Machine Replication
tags:
  - distributed
  - consensus
  - algorithm
  - deep-dive
  - reliability
---

# 586 — Raft

⚡ TL;DR — Raft is a consensus algorithm designed to be understandable: it decomposes the consensus problem into leader election, log replication, and safety, allowing a cluster of servers to agree on a sequence of values even as servers fail and recover.

| #586            | Category: Distributed Systems                                                  | Difficulty: ★★★ |
| :-------------- | :----------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Leader Election, Log Replication, Quorum, Consensus, State Machine Replication |                 |
| **Used by:**    | etcd, Kubernetes, CockroachDB, TiKV, Distributed Locking                       |                 |
| **Related:**    | Paxos, Zab, Multi-Paxos, Log Replication, State Machine Replication            |                 |

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Paxos was the dominant consensus algorithm for decades — and nearly everyone who tried to implement it described it as notoriously difficult to understand and even harder to extend to practical systems (leader election, log compaction, cluster membership changes). Google's Chubby, Yahoo's ZooKeeper, and many databases implemented bespoke consensus variants. Every implementation was different. Every implementation had different correctness trade-offs. And most of them had bugs.

**THE INVENTION MOMENT:**
Diego Ongaro and John Ousterhout, motivated by the Paxos understandability crisis, designed Raft in 2014 with a primary goal: make consensus comprehensible. They decomposed consensus into three independent subproblems — leader election, log replication, and safety — and chose design decisions that prioritise clarity over message-count efficiency. Raft is now the most widely implemented consensus algorithm in production systems.

---

### 📘 Textbook Definition

**Raft** is a consensus algorithm that ensures a cluster of servers maintain identical replicated logs. One server is elected **leader** per term; the leader accepts all client requests, appends them to its log, and replicates them to followers using `AppendEntries` RPCs. An entry is **committed** when stored on a majority (`N/2 + 1`) of servers. Committed entries are applied to state machines in order. Raft guarantees: **Election Safety** (at most one leader per term); **Leader Append-Only** (a leader never overwrites its log); **Log Matching** (if two logs have an entry with the same index and term, logs are identical through that index); **Leader Completeness** (a committed entry must be present in all future leaders' logs); **State Machine Safety** (if any server has applied a log entry at index i, no server will apply a different log entry at index i).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Raft is the consensus algorithm that finally made distributed agreement easy enough to get right: one leader, a shared append-only log, and a majority vote.

**One analogy:**

> Raft is like a distributed secretary: the elected secretary (leader) receives all meeting minutes (client commands), writes them down in order, sends copies to every committee member (follower), and a decision is final when more than half confirm they've written it down. If the secretary quits, the committee elects a new one whose notes are the most complete.

**One insight:**
Raft's key insight over Paxos: by having a strong leader that is authoritative for the entire log, Raft avoids the need for complex "promise" and "accept" two-phase voting per slot. The leader linearises all decisions. This simplification costs some throughput (all writes must go through one node) but makes the algorithm dramatically easier to understand, implement, and debug.

---

### 🔩 First Principles Explanation

**THE THREE SUBPROBLEMS:**

```
┌──────────────────────────────────────────────────────────┐
│  1. LEADER ELECTION                                      │
│     Problem: pick exactly one authoritative node         │
│     Solution: randomised timeouts → RequestVote RPC      │
│              win majority → LEADER; term monotonically ↑│
│                                                          │
│  2. LOG REPLICATION                                      │
│     Problem: replicate leader's log to all followers     │
│     Solution: AppendEntries RPC (also doubles as heartbeat│
│              commit when N/2+1 acknowledge               │
│              leader applies → notifies followers to apply│
│                                                          │
│  3. SAFETY (LOG MATCHING INVARIANT)                      │
│     Problem: ensure all committed entries are preserved  │
│              across leader changes                       │
│     Solution: log completeness check in vote grant       │
│              only vote for candidates with logs ≥ own    │
└──────────────────────────────────────────────────────────┘
```

**RAFT LOG REPLICATION FLOW:**

```
Client: "SET x=42"
          │
          ▼
    Leader (N1, term=3)
    1. Append to local log: {index:7, term:3, cmd:"SET x=42"}
    │
    ├──AppendEntries{term:3, index:7, entry:{...}}──▶ N2 (follower)
    ├──AppendEntries{term:3, index:7, entry:{...}}──▶ N3 (follower)
    └──AppendEntries{term:3, index:7, entry:{...}}──▶ N4 (follower)
    │
    N2 ──▶ ACK         ← majority achieved (N1+N2+N3 = 3/5)
    N3 ──▶ ACK
    │
    Leader commits entry 7, applies to state machine
    Leader responds "OK" to client
    Leader's next AppendEntries includes commitIndex=7
    N2, N3 apply entry 7 on receiving updated commitIndex
```

**LOG MATCHING PROPERTY:**

```
If two logs contain an entry with same (index, term):
  → All entries BEFORE that index are identical in both logs

Why? Leader sends AppendEntries with prevLogIndex+prevLogTerm.
     Follower REJECTS if its prevLog doesn't match.
     Leader decrements prevLogIndex, retries.
     Eventually finds matching point → follower overwrites diverged entries.
     This backtracking ensures leader's log is the truth.
```

**LEADER ELECTION SAFETY:**

```
Candidate gets vote from N only if:
  candidate's lastLog.term > voter's lastLog.term  OR
  (terms equal AND candidate's log.length >= voter's log.length)

→ Only a candidate with the most complete log can win an election.
→ All committed entries (majority knows them) will be in any future leader's log.
→ Leader Completeness property: committed entries are NEVER lost.
```

---

### 🧪 Thought Experiment

**LEADER FAILURE DURING REPLICATION:**
Cluster: N1 (leader), N2, N3, N4, N5. Log entry X is appended.

**Case A:** N1 sends to N2 and N3 (majority). N2 and N3 ACK. N1 commits entry X.
N1 crashes before notifying N4, N5. N3 starts election. N3 voted in the old ACK,
so N3's log includes X. N3 wins election (most up-to-date log wins). N3 replicates
X to N4, N5. **Entry X is not lost.** ✓

**Case B:** N1 appends X locally. Sends to N2 only. N1 crashes before N2 ACKs.
Entry X is NOT committed (only 2/5 nodes: N1+N2 know it). N3 or N4 starts election.
N3's log doesn't have X (only N1 and N2 do). N3 could win election if N3's log
matches N4 and N5. N3 becomes leader. N3's log DOES NOT include X. N3 OVERWRITES
N2's copy of X. **Entry X is lost.** ✓ — This is CORRECT: X was never committed.
The client never got an ACK. The client will retry. Safety is preserved.

**THE GUARANTEE:** Raft only confirms a write to the client after a COMMITTED ACK
(majority replication). A write that only reached one follower before leader crash
was never confirmed to the client. Retrying is the client's responsibility.

---

### 🧠 Mental Model / Analogy

> Raft is like a distributed append-only ledger with a rotating notary.
> The notary (leader) is the only person authorised to add new entries.
> An entry is "official" when the notary stamps it AND at least N/2 witnesses
> co-sign. If the notary steps down, the new notary is chosen from whoever
> has the most complete signed ledger. The new notary starts from where
> the old one left off — no entries are lost, no double-entries are possible.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Raft is a "distributed agreement" protocol. One node is the leader; it receives all writes, puts them in an ordered log, and gets a majority of other nodes to confirm each entry. If the leader fails, nodes vote on a replacement who takes over the log.

**Level 2:** Every write goes through three phases: (1) leader appends to local log; (2) leader replicates to followers (AppendEntries); (3) leader commits when majority ACK. The commit message is piggybacked on the next AppendEntries. Only committed entries are applied to the state machine and acknowledged to clients.

**Level 3:** Raft's safety comes from two invariants: Log Matching (if two logs agree at index i, they agree on all previous indices — enforced by the AppendEntries consistency check) and Leader Completeness (a new leader always has all committed entries — enforced by only voting for candidates with the most up-to-date log). Together these ensure the replicated log is an append-only, irreversible history of committed operations.

**Level 4:** Raft's simplicity has a performance cost: all writes go through the leader (single bottleneck). Production optimisations: pipelining AppendEntries (don't wait for one to commit before sending next), batch commits (accumulate N entries before sending), leader/follower read scaling (read from committed followers for linearisable reads using Raft ticks, or use lease-based reads). Log compaction via snapshots (snapshotting the state machine, discarding old log entries) is essential for bounded storage. Raft's joint consensus for cluster membership changes (add/remove nodes) uses a two-phase approach to avoid split-brain during the membership transition.

---

### ⚙️ How It Works (Mechanism)

**Raft AppendEntries RPC:**

```
Leader → Follower:
  AppendEntries {
    term:         3,          // leader's current term
    leaderId:     "N1",
    prevLogIndex: 6,          // index of log entry before new ones
    prevLogTerm:  3,          // term of prevLogIndex entry
    entries:      [{index:7, term:3, cmd:"SET x=42"}],
    leaderCommit: 6           // leader's commitIndex
  }

Follower reply:
  success: true/false
  term:    follower's term (if > leader.term, leader steps down)

Safety check on follower:
  if log[prevLogIndex].term != prevLogTerm:
    return success=false  ← leader will decrement prevLogIndex and retry
  else:
    append entries, update commitIndex if leaderCommit > commitIndex
    return success=true
```

**etcd Raft State (production):**

```bash
# Check Raft leader and term:
etcdctl endpoint status --cluster -w table
# Shows: leader ID, current term, committed index, applied index for all members

# Watch for election events:
journalctl -u etcd -f | grep -E "became leader|started election|term"
```

---

### ⚖️ Comparison Table

| Property           | Raft                       | Paxos (Multi-Paxos)             |
| ------------------ | -------------------------- | ------------------------------- |
| Understandability  | High (primary design goal) | Low (notoriously complex)       |
| Leader-based       | Yes (strong leader)        | Yes (proposer) but weaker       |
| Log compaction     | Built-in (snapshots)       | Not specified (impl-dependent)  |
| Membership change  | Joint consensus (built-in) | Not specified                   |
| Throughput         | Good (pipelining)          | Slightly better (more flexible) |
| Production systems | etcd, CockroachDB, TiKV    | Chubby, some internal systems   |

---

### ⚠️ Common Misconceptions

| Misconception                         | Reality                                                                                                                                               |
| ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Raft is slow because of single leader | Pipelining and batching give Raft competitive throughput. Single-leader IS a bottleneck for geo-distributed systems but fine for cluster coordination |
| Raft 100% guarantees no data loss     | Raft guarantees no loss of COMMITTED entries. Un-committed entries (acknowledged to client before majority ACK — which shouldn't happen) CAN be lost  |
| Raft requires all nodes to be up      | Raft requires only a MAJORITY (N/2+1). A 5-node Raft cluster remains functional with 2 node failures                                                  |
| etcd IS Raft                          | etcd implements Raft but adds its own storage layer, watch mechanism, transaction KV API on top                                                       |

---

### 🚨 Failure Modes & Diagnosis

**Slow Commit Latency (Replication Bottleneck)**

Symptom: Write latency is consistently at 2× single-machine latency;
leader CPU is low but throughput is capped.

Root Cause: Each write waits for follower ACK before next write dispatched
(not pipelining). Or: network latency between leader and followers is high.

Fix: Enable AppendEntries pipelining. For geo-distributed Raft, use MultiRaft
(multiple independent Raft groups with different leaders) to avoid single-region
leader bottleneck. CockroachDB uses MultiRaft with one Raft group per range.

---

**Leader Flapping During Network Instability**

Symptom: Rapid leader changes; high term numbers; etcd alarms.

Root Cause: Follower election timeouts misconfigured too short for network jitter.

Fix: `--election-timeout` should be ≥ 10× `--heartbeat-interval` and ≥ 5× the
99th-percentile network RTT between nodes.

```bash
# etcd tuning:
etcd --heartbeat-interval=100 --election-timeout=1000  # (ms)
# General rule: election-timeout ≥ 10 * heartbeat-interval
```

---

### 🔗 Related Keywords

- `Leader Election` — the first phase of Raft; defines how a leader is chosen per term
- `Log Replication` — the second phase; defines how entries are replicated to followers
- `Paxos` — the predecessor/alternative; Raft was designed as a more understandable Paxos
- `State Machine Replication` — the target application of Raft: identical state machines via identical logs
- `etcd` — the most widely deployed Raft implementation (powers Kubernetes)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  RAFT = Leader Election + Log Replication + Safety       │
│                                                          │
│  Write path: client → leader → AppendEntries → ACK N/2+1│
│              → commit → apply state machine → respond    │
│                                                          │
│  Safety invariants:                                      │
│    Log Matching: if logs agree at i, they agree at [0,i] │
│    Leader Completeness: new leader has ALL committed logs│
│                                                          │
│  Key: only committed entries guaranteed durable          │
│  Used by: etcd, CockroachDB, TiKV, Consul               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A 5-node Raft cluster has leader N1 with log entries up to index 10 (all committed). N1 appends entry 11 locally, sends AppendEntries to N2 and N3, but N2 and N3 crash before responding. N4 and N5 haven't received entry 11. N1 then crashes too. Who can become leader? What happens to entry 11? Walk through the election, the log state of each candidate, and the exact Raft rules that govern the outcome.

**Q2.** You're designing a Raft-based key-value store that needs to serve linearisable reads WITHOUT routing every read through the leader. Describe the "read index" optimisation that allows followers to serve linearisable reads, what guarantee it requires from the leader, and why naively serving reads from a follower's local state without this mechanism violates linearisability.
