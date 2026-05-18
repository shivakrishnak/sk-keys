---
id: DST-041
title: Raft Consensus Algorithm
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-014, DST-020, DST-046
used_by: DST-042, DST-046, DST-048
related: DST-027, DST-029, DST-042, DST-046, DST-047, DST-048
tags:
  - distributed
  - consensus
  - leader-election
  - replication
  - etcd
  - raft
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 41
permalink: /technical-mastery/distributed-systems/raft-consensus/
---

⚡ TL;DR - Raft is a consensus algorithm designed for
understandability; it elects a leader that handles
all writes, replicates log entries to a quorum of
followers, and ensures that any two committed entries
at the same log index are identical across all nodes;
it tolerates up to (N-1)/2 node failures in a cluster
of N nodes.

---

### 📋 Entry Metadata

| #041 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Consistency, Heartbeat/Health Check, Leader Election | |
| **Used by:** | Leader Election, Split-Brain, etcd, Kubernetes | |
| **Related:** | Quorums, Linearizability, Paxos, Leader Election, Fencing Token | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Three database nodes must agree on which writes are
committed. Node 1 receives a write and commits it.
Network partition: Node 1 is isolated from Nodes 2
and 3. Now Node 2 also receives the "write 42"
operation and commits it. Partition heals: both Node 1
and Node 2 believe their write is authoritative.
Conflict: which value is correct? Without a consensus
algorithm, you have **split-brain** - two nodes
diverged with no principled way to reconcile. All
distributed systems that replicate state face this
problem; consensus is the principled solution.

---

### 📘 Textbook Definition

**Raft** is a distributed consensus algorithm that
replicates a log of commands to a cluster of state
machines, ensuring that all non-faulty nodes apply
the same commands in the same order.

Raft decomposes consensus into three subproblems:
1. **Leader election:** select one node to coordinate
2. **Log replication:** leader receives commands and
   replicates them to followers
3. **Safety:** if any node has committed an entry at
   log index i with term T, no other node commits a
   different entry at index i with term >= T

---

### ⏱️ Understand It in 30 Seconds

```
CLUSTER: 3 nodes {A, B, C}. A is leader.

NORMAL OPERATION:
  Client sends write "x=5" to A.
  A appends to its log: [(term=1, index=1, x=5)]
  A sends AppendEntries RPC to B and C.
  B and C append, acknowledge.
  A receives 2 acks (quorum of 2 from 3 nodes).
  A commits the entry, applies to state machine.
  A tells B and C the entry is committed.
  B and C apply to their state machines.
  Result: all nodes have x=5.

NODE FAILURE:
  A crashes. B and C detect via missed heartbeats.
  B and C start election: increment term, vote for self.
  Node with most up-to-date log wins.
  New leader handles writes. Cluster continues.

GUARANTEE:
  Any committed log entry is present on a quorum of nodes.
  A new leader must have won a quorum election.
  At least one voter in the quorum has the latest
    committed entry.
  New leader will not overwrite committed entries.
```

---

### 🔩 First Principles Explanation

**NODE STATES:**

```
FOLLOWER:
  Default state. Waits for leader heartbeats.
  If election_timeout elapses with no heartbeat:
    converts to Candidate.

CANDIDATE:
  Increments current_term.
  Votes for self.
  Sends RequestVote RPC to all other nodes.
  If receives votes from majority:
    becomes Leader.
  If receives AppendEntries from a valid leader:
    reverts to Follower.
  If election_timeout elapses without majority:
    starts new election (increments term again).

LEADER:
  Sends periodic AppendEntries (heartbeats) to all
    followers.
  Receives client requests.
  Replicates log entries to followers.
  Commits entries acknowledged by majority.
  Notifies followers of committed entries.
```

**TERM:**
Raft divides time into terms (monotonically increasing
integers). Each term starts with an election. At most
one leader per term. Terms serve as a logical clock:
if a node receives a message with a higher term than
its own, it immediately reverts to Follower and updates
its term. Stale leaders are detected and overridden.

**LOG STRUCTURE:**

```
Leader log:
Index: 1    2    3    4    5
Term:  1    1    2    2    3
Cmd:   x=1  y=2  x=3  z=1  y=5
       ^committed^   ^uncommitted^
             |
          commit_index=4 (acknowledged by quorum)
```

**LOG REPLICATION RULES:**

1. Leader receives command, appends to local log.
2. Leader sends `AppendEntries(term, leader_id,
   prev_log_index, prev_log_term, entries[], leader_commit)`
   to all followers.
3. Follower checks `prev_log_index` and `prev_log_term`
   match its own log. If yes: appends entries.
4. Once a majority acknowledge: leader commits.
5. Leader broadcasts `commit_index` in next heartbeat.
6. Followers commit up to `leader_commit` index.

**ELECTION SAFETY (KEY INVARIANT):**

A candidate's log must be at least as up-to-date as
any voter's log (checked via last_log_term and
last_log_index in RequestVote). This ensures no
node can win the election unless it has all committed
entries. Combined with quorum voting, this prevents
any committed entry from being overwritten.

---

### 🧠 Mental Model / Analogy

> Raft is like a company with a CEO (leader) who
> signs all official decisions. Every decision is
> logged in a ledger and copied to all board members
> (followers). A decision is final only when a
> majority of board members have logged it. If the
> CEO is unavailable (crashes), the board holds an
> election - the candidate with the most complete
> ledger wins. The new CEO continues from where the
> old one left off. No decision that was signed by
> a quorum can be reversed, because any new CEO
> must have won with at least one vote from someone
> who has all signed decisions.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is:**
A way for multiple database nodes to agree on a
sequence of writes. One node is elected leader; it
handles all writes and replicates them to the others.
A write is only considered committed once a majority
of nodes have it. If the leader crashes, a new one
is elected from nodes with the most up-to-date log.

**Level 2 - Leader election:**
When a follower doesn't hear from the leader for
150-300ms (randomized election timeout), it becomes
a candidate. It increments its term and asks others
to vote. A node grants one vote per term to the first
candidate whose log is at least as up-to-date as the
voter's log. Randomized timeouts prevent all nodes
starting elections simultaneously.

**Level 3 - Log matching:**
Raft maintains a key invariant: if two logs have the
same term and index for an entry, all preceding entries
are also identical. This is enforced by the
AppendEntries RPC's consistency check: it rejects
an append if the preceding log entry doesn't match.
A leader fixes inconsistent follower logs by finding
the point of divergence and overwriting the divergent
entries (followers always defer to the current leader's
log, because the leader was elected by a quorum
that has all committed entries).

**Level 4 - Membership changes:**
Adding or removing nodes from a Raft cluster is
dangerous: if you add 2 nodes to a 3-node cluster
simultaneously, two different leaders could be elected
(one from the old 3-node quorum, one from the new
5-node quorum). Raft uses a joint consensus or
single-server change protocol: change one server at
a time. The cluster is never in a state where two
independent quorums can be formed.

**Level 5 - Performance characteristics:**
Raft adds 1 RTT to every write (leader → followers,
wait for quorum, commit). In a 3-node cluster with
5ms inter-node latency: each write adds 10ms latency.
At 10ms per write: maximum ~100 writes/second in
strict Raft. Log batching (batching multiple client
requests into one AppendEntries RPC) improves
throughput significantly. etcd uses Raft with batching;
typical production throughput: 1,000-10,000 writes/s
depending on entry size and cluster latency.

---

### ⚙️ Raft in Production: etcd

etcd is the primary production implementation of
Raft, used as the backing store for Kubernetes.

```
ETCD CLUSTER SETUP (3 nodes):
  etcd --name node1 --initial-cluster-state new \
    --initial-cluster \
    "node1=http://10.0.0.1:2380,\
     node2=http://10.0.0.2:2380,\
     node3=http://10.0.0.3:2380" \
    --initial-advertise-peer-urls \
    http://10.0.0.1:2380 \
    --advertise-client-urls http://10.0.0.1:2379 \
    --listen-peer-urls http://10.0.0.1:2380 \
    --listen-client-urls http://10.0.0.1:2379

CLUSTER HEALTH:
  etcdctl endpoint health \
    --endpoints=http://10.0.0.1:2379,\
    http://10.0.0.2:2379,http://10.0.0.3:2379

LEADER CHECK:
  etcdctl endpoint status --write-out=table
  # Shows: IS LEADER column

KEY METRICS TO MONITOR:
  etcd_server_leader_changes_seen_total
    - High: leader instability (network issues)
  etcd_disk_wal_fsync_duration_seconds
    - High: slow disk; election timeouts may trigger
  etcd_network_peer_round_trip_time_seconds
    - High: slow inter-node; heartbeat misses
```

---

### 💻 Code Example

**Wrong vs Right: Quorum Check**

```python
# BAD: Assuming writes succeed if any node acknowledges
# (no quorum check)

class FakeRaftLeader:
    def write(self, key: str, value: str) -> bool:
        for node in self.followers:
            if node.append(key, value):
                return True  # BUG: one ack is not a quorum
        return False
# If the one acking node is isolated later,
# the commit is lost. Split brain possible.
```

```python
# GOOD: Quorum check before committing

class RaftLeader:
    def __init__(self, nodes: list, quorum_size: int):
        self.nodes = nodes
        self.quorum_size = quorum_size  # (N+1)//2

    def write(self, key: str, value: str) -> bool:
        # Append to own log first
        entry = LogEntry(
            term=self.current_term,
            index=len(self.log) + 1,
            key=key,
            value=value
        )
        self.log.append(entry)

        # Replicate to followers
        acks = 1  # Count self
        for node in self.followers:
            success = node.append_entries(
                term=self.current_term,
                prev_log_index=entry.index - 1,
                prev_log_term=self._prev_term(entry),
                entries=[entry],
                leader_commit=self.commit_index
            )
            if success:
                acks += 1

        # Commit only when quorum acknowledges
        if acks >= self.quorum_size:
            self.commit_index = entry.index
            self._notify_followers_of_commit(entry.index)
            return True
        else:
            # Roll back - quorum not reached
            self.log.pop()
            return False
```

---

### ⚖️ Comparison Table

| Property | Raft | Paxos | 2PC |
|---|---|---|---|
| **Understandability** | Designed for clarity | Notoriously complex | Simple |
| **Leader needed** | Yes (strong leader) | No (multi-paxos uses one) | Coordinator needed |
| **Blocking failure** | No | No | Yes (if coordinator crashes) |
| **Fault tolerance** | (N-1)/2 node failures | (N-1)/2 node failures | Zero (coordinator must be up) |
| **Real-world use** | etcd, CockroachDB, TiKV | Chubby (Google), Zookeeper | RDBMS XA transactions |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Raft requires all nodes to be online for writes" | Raft requires a quorum (majority) for writes. A 5-node cluster tolerates 2 node failures. |
| "Leader election is instantaneous" | Election takes 2-3 election timeouts (150-450ms typically). During this window, writes are rejected. Applications must handle this. |
| "Raft guarantees no data loss under network partition" | Raft guarantees committed entries are not lost. Entries that were replicated to only the leader before a partition ARE at risk of being rolled back if that leader loses the election to a more up-to-date node. |
| "Adding nodes to a Raft cluster improves availability" | More nodes = higher availability (more failures tolerated) but LOWER throughput (larger quorum = more ACKs to wait for). Typical: 3 or 5 nodes. 7+ is rarely used. |

---

### 🚨 Failure Modes & Diagnosis

**Leader Instability (Frequent Elections)**

**Symptom:** etcd logs show frequent leader changes.
`etcd_server_leader_changes_seen_total` increases
rapidly. Kubernetes API server shows connectivity
issues.

**Root Cause candidates:**
1. Disk I/O too slow: leader cannot fsync WAL before
   heartbeat timeout. Followers don't receive heartbeats.
2. Network latency too high: heartbeats take longer
   than election timeout.
3. Insufficient CPU: leader can't send heartbeats
   fast enough under load.

**Diagnosis:**
```bash
# Check etcd WAL fsync latency:
# In Prometheus:
histogram_quantile(
  0.99,
  rate(etcd_disk_wal_fsync_duration_seconds_bucket[5m])
)
# Should be < 10ms. If > 100ms: disk is bottleneck.

# Check peer latency:
histogram_quantile(
  0.99,
  rate(etcd_network_peer_round_trip_time_seconds_bucket[5m])
)
# Should be < 50ms. If high: network issue.
```

**Fix:** Move etcd data directory to an SSD or
dedicated volume. Increase `--heartbeat-interval`
and `--election-timeout` proportionally (default:
100ms heartbeat, 1000ms election timeout). Never
use NFS for etcd data directory.

---

### 🔗 Related Keywords

**Prerequisites:** `Consistency` (DST-014),
`Heartbeat and Health Check` (DST-020),
`Leader Election` (DST-046)

**Builds On This:** `Paxos` (DST-042),
`Split-Brain` (DST-048), etcd, CockroachDB, TiKV

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ NODES      │ Follower → Candidate → Leader              │
│ TERM       │ Logical clock; higher term wins            │
│ QUORUM     │ (N+1)/2 nodes must ack to commit           │
├────────────┼────────────────────────────────────────────┤
│ ELECTION   │ Missed heartbeat → election                │
│            │ Win = majority + up-to-date log            │
│ COMMIT     │ Leader appends, replicates, waits quorum   │
├────────────┼────────────────────────────────────────────┤
│ FAULT TOL  │ Tolerates (N-1)/2 failures                 │
│            │ 3 nodes: 1 failure; 5 nodes: 2 failures   │
├────────────┼────────────────────────────────────────────┤
│ REAL-WORLD │ etcd, CockroachDB, TiKV, Consul            │
├────────────┼────────────────────────────────────────────┤
│ ONE-LINER  │ "One leader, replicated log, quorum commit:│
│            │  correctness by design, not by accident."  │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

The log-based approach in Raft (all state changes
as ordered log entries) is the foundational pattern
for distributed state machine replication. The same
pattern appears in: Kafka (replicated commit log),
database WAL (write-ahead log), event sourcing
(event log as source of truth), blockchain (chain
of blocks as immutable log). Once you understand
why Raft needs a log (to replay and synchronize
state across nodes), you recognize the same insight
everywhere. The log is not an implementation detail;
it is the mechanism by which all distributed state
agreement is made possible.

---

### 💡 The Surprising Truth

The Raft paper (Ongaro & Ousterhout, 2014) was
explicitly designed as a teaching tool, not a
performance-optimized algorithm. The authors were
frustrated that Paxos was taught in distributed
systems courses but almost no students could
implement it correctly afterward. Raft introduced
structural constraints (strong leader, sequential
log) specifically to make it easier to reason about
- some of which make it slightly less efficient than
multi-Paxos in specific scenarios. The gamble paid
off: etcd, the most widely deployed consensus system
in the world (backing every Kubernetes cluster),
uses Raft. Understandability turned out to be more
valuable than theoretical optimality in production.

---

### ✅ Mastery Checklist

1. [EXPLAIN] Describe the three Raft node states and
   the transitions between them, without looking.
2. [DERIVE] Given a 5-node cluster, how many node
   failures can Raft tolerate? Explain why.
3. [TRACE] Walk through a leader election starting
   from "leader crashes" to "new leader elected and
   first write committed."
4. [IDENTIFY] What is the election safety property
   and why does it prevent committed entries from
   being overwritten?
5. [DIAGNOSE] etcd shows frequent leader changes.
   List three root causes and the diagnostic command
   for each.
