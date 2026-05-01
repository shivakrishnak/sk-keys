---
layout: default
title: "Raft"
parent: "Distributed Systems"
nav_order: 586
permalink: /distributed-systems/raft/
number: "586"
category: Distributed Systems
difficulty: ★★★
depends_on: "Leader Election, Strong Consistency"
used_by: "etcd, CockroachDB, TiKV, Consul"
tags: #advanced, #distributed, #consensus, #replication, #fault-tolerance
---

# 586 — Raft

`#advanced` `#distributed` `#consensus` `#replication` `#fault-tolerance`

⚡ TL;DR — **Raft** is an understandable consensus algorithm that maintains a replicated log across N nodes (tolerating N/2 failures) via leader election, log replication, and safety guarantees — powering etcd, CockroachDB, and most modern strongly consistent distributed systems.

| #586 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Leader Election, Strong Consistency | |
| **Used by:** | etcd, CockroachDB, TiKV, Consul | |

---

### 📘 Textbook Definition

**Raft** (Ongaro & Ousterhout, 2014 — "In Search of an Understandable Consensus Algorithm") is a consensus protocol designed explicitly for understandability as an alternative to Paxos. Raft decomposes consensus into three relatively independent sub-problems: **Leader election** (select one leader per term using majority votes), **Log replication** (leader accepts entries, replicates to followers, commits when majority ACK), and **Safety** (at most one leader per term; committed entries never lost — ensured by the "log up-to-date" voting restriction). A Raft cluster of N nodes tolerates ⌊N/2⌋ failures while maintaining consistency (CP in CAP). The replicated log is the core abstraction: each entry is indexed and term-stamped; committed entries are applied to a state machine in index order, guaranteeing all nodes reach identical state. Raft is linearisable for writes (only leader commits) and for reads via the ReadIndex protocol (leader confirms majority still acknowledges it before serving a read). Implementations power etcd (Kubernetes backing store), CockroachDB (distributed SQL), TiKV (TiDB's storage layer), and HashiCorp Consul.

---

### 🟢 Simple Definition (Easy)

Raft: a consensus algorithm for keeping a distributed log identical on multiple servers. One server is the leader — all writes go to it. The leader copies each write to followers. Once a majority have the write: it's "committed" — can't be lost. If the leader crashes: followers elect a new leader. All servers apply writes in the same order → all servers have the same data. Paxos does the same thing but is harder to understand and implement — Raft was designed to be easier.

---

### 🔵 Simple Definition (Elaborated)

Raft guarantees: (1) only one leader per term (majority voting), (2) committed log entries are never lost (new leader has all committed entries — enforced by up-to-date log check during voting), (3) all nodes apply log entries in the same order (log index is a total order). Combined: every Raft node applies the same sequence of commands → identical state machines. Application: store config in etcd — all Kubernetes nodes see the same config because all etcd nodes apply the same Raft log. One node down: fine (3-node cluster tolerates 1 failure). Two nodes down: cluster stops (cannot form quorum) — correct! Better to stop than to serve inconsistent data.

---

### 🔩 First Principles Explanation

**Raft log replication and commit protocol:**

```
RAFT LOG STRUCTURE:

  Each log entry: [index, term, command]
  index: position in log (1, 2, 3, ... globally unique, never changes once written)
  term: leader's term when entry was created (used for safety checks)
  command: operation to apply to state machine (e.g., SET x=10, DELETE y)
  
  Example log:
  Index: | 1    | 2    | 3    | 4    | 5    | 6    |
  Term:  | 1    | 1    | 1    | 2    | 2    | 3    |
  Cmd:   |SET x1|SET y2|SET z3|SET x4|SET y5|SET z6|
  
  commitIndex: highest index known to be committed (applied to majority).
  appliedIndex: highest index applied to local state machine.
  Invariant: appliedIndex ≤ commitIndex ≤ log.lastIndex.

LOG REPLICATION PROTOCOL:

  Client → Leader: "SET x = 10"
  
  Step 1: LEADER APPENDS TO LOCAL LOG
    Leader: appends entry [index=6, term=3, cmd=SET_x_10] to its log.
    Leader's log: [..., 5, 6]
    Leader has NOT committed yet (only locally stored).
    
  Step 2: LEADER REPLICATES TO FOLLOWERS
    Leader → Follower1: AppendEntries(
        term=3,
        leaderId=N1,
        prevLogIndex=5, prevLogTerm=3,   ← ensures consistency check
        entries=[{6, 3, SET_x_10}],
        leaderCommit=5                   ← followers commit up to this index
    )
    Leader → Follower2: same AppendEntries.
    Leader → Follower3: same AppendEntries.
    
  PREVLOGINDEX/TERM CONSISTENCY CHECK:
    Follower checks: "Do I have entry at prevLogIndex with prevLogTerm?"
    If not: log is inconsistent → reject. Leader sends older entries to catch up follower.
    This ensures: before appending index 6, follower has exactly the same entries 1-5 as leader.
    
  Step 3: MAJORITY ACK → COMMIT
    Follower1: appends entry, ACKs. (Now: leader + follower1 have index 6 = 2 of 5)
    Follower2: appends entry, ACKs. (Now: 3 of 5 = MAJORITY)
    
    Leader: commitIndex = 6. Entry 6 is committed.
    Leader → applies SET_x_10 to state machine.
    Leader → responds to client: "x = 10 written ✓"
    
    Follower3 and Follower4: receive leaderCommit=6 in next AppendEntries → commit locally.
    
  WHAT "COMMITTED" MEANS:
    Committed = present on a majority of nodes.
    If leader crashes: new leader MUST HAVE all committed entries (ensured by voting rule).
    Therefore: committed entries can NEVER be lost (even if leader crashes).
    
  Uncommitted entries (only on leader): CAN be lost if leader crashes before majority ACK.
  Client retries if no response → idempotency required on state machine.

SAFETY INVARIANTS:

  ELECTION SAFETY: at most one leader per term.
    Proof: a node grants at most one vote per term.
    Two candidates cannot both get majority from a set of N nodes
    (majority = N/2+1; two majorities of N nodes must share ≥ 1 node;
     that shared node voted for only one candidate → only one candidate gets majority).
    
  LOG MATCHING PROPERTY: if two entries have same index and term → logs are identical up to that point.
    Proof: leaders create at most one entry per index per term.
           AppendEntries consistency check ensures follower's log matches leader's at prevLogIndex.
           By induction: entire log up to the entry is identical.
    
  LEADER COMPLETENESS: if an entry is committed in term T, all leaders of terms > T have that entry.
    Proof: entry committed in term T = present on majority.
           New leader (term > T) won election with majority votes.
           New leader's majority overlaps with commit majority (at least 1 shared node).
           That shared node has the committed entry.
           Up-to-date log check ensures new leader's log is ≥ voter's log → has committed entry.
    
  STATE MACHINE SAFETY: if node has applied entry at index i → no other node applies different entry at i.
    Proof: follows from Log Matching Property (logs identical at any committed index).

RAFT LOG COMPACTION (SNAPSHOTS):

  Problem: log grows unboundedly. 1 billion log entries → GB of storage.
  Solution: snapshot. Periodically:
    1. State machine: take snapshot of current state (e.g., full key-value store state).
    2. Log: discard all entries before snapshot's log index.
    3. Snapshot includes: snapshot index, snapshot term, state machine state.
    
  For slow followers: send snapshot (instead of replaying entire log).
    Leader → slow follower: InstallSnapshot RPC with snapshot.
    Follower: applies snapshot to state machine, discards its log up to snapshot index.
    
  Snapshot size: proportional to state machine size, not log length.
  etcd: snapshotCount = 100000 (snapshot after 100k writes); compacts log.

RAFT MEMBERSHIP CHANGES:

  Problem: adding/removing nodes while cluster is running.
  Naive approach: joint consensus.
    Phase 1: switch to "joint configuration" (old + new config). Requires majority of BOTH.
    Phase 2: commit new config alone. Requires majority of new config only.
    During joint: no split-brain possible (both old and new majorities must agree).
    
  etcd: uses single-server membership changes (add/remove one node at a time).
    Safer: no joint consensus needed. Each change: one node at a time.
    Process: add node N6 to 5-node cluster → 6-node cluster → quorum = 4.
             Remove node N1 from 6-node cluster → 5-node cluster → quorum = 3.
    Invariant: cluster never goes through state where quorum could be ambiguous.

PERFORMANCE CHARACTERISTICS:

  Write latency: leader → followers RTT + apply to state machine.
    Single DC (1ms RTT): ~2-3ms per write (append + ACK + apply).
    Multi-region (80ms RTT): ~160ms per write (2 RTTs: append + ACK).
    
  Throughput: limited by leader's write bandwidth.
    etcd v3: ~10,000 small writes/second.
    CockroachDB: ~50,000 writes/second per Raft group (with batching + pipelining).
    
  Read latency:
    Leader reads (ReadIndex): ~1ms (confirm leadership via heartbeat + apply).
    Follower reads (serialisable): ~0ms (local read, slightly stale).
    
  Pipelining: leader sends AppendEntries before previous one ACKed → higher throughput.
  Batching: accumulate multiple client writes → single AppendEntries round → amortise RTT.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Raft (only Paxos):
- Paxos is notoriously difficult to understand and implement correctly (Chubby paper admits this)
- Many implementations diverge from correctness guarantees due to implementation complexity
- Fewer engineers can audit, debug, and reason about Paxos-based systems

WITH Raft:
→ Understandable: can be explained in an hour; safety proofs are straightforward
→ Correct implementations: many battle-tested open-source implementations (etcd/raft library)
→ Powers critical infrastructure: etcd (Kubernetes), CockroachDB, TiDB, Consul

---

### 🧠 Mental Model / Analogy

> A parliamentary bill-passing system. The Prime Minister (leader) proposes bills (log entries). Bills are forwarded to MPs (followers) for their records. A bill is "passed into law" (committed) once a majority of MPs have recorded it. If the PM is incapacitated (crash): a new election. The new PM is only eligible if their records are at least as complete as the majority (log up-to-date check). All courts (state machines) apply passed bills in exact numerical order (log index) — regardless of which PM passed them. Result: every court has the same laws in the same order.

"Prime Minister proposes bills" = leader accepts and replicates log entries
"Bill passed when majority record it" = commit when quorum ACKs
"New PM must have complete records" = log up-to-date check in election
"Courts apply laws in numerical order" = state machines apply log in index order

---

### ⚙️ How It Works (Mechanism)

**etcd: using Raft via etcd client:**

```bash
# etcd cluster: 3 nodes, Raft consensus.
# All writes go to leader. Followers replicate.

# Check cluster status (which node is leader):
$ etcdctl --endpoints=https://etcd1:2379,https://etcd2:2379,https://etcd3:2379 \
    endpoint status --write-out=table
+----------------+------------------+---------+---------+-----------+------------+
|    ENDPOINT    |        ID        | VERSION | DB SIZE |  IS LEADER |  RAFT TERM |
+----------------+------------------+---------+---------+-----------+------------+
| https://etcd1  | 8e9e05c52164694d |   3.5.0 |   25 MB |     false  |         15 |
| https://etcd2  | 91bc3c398fb3c146 |   3.5.0 |   25 MB |      TRUE  |         15 |   ← LEADER
| https://etcd3  | fd422379fda50e48 |   3.5.0 |   25 MB |     false  |         15 |
+----------------+------------------+---------+---------+-----------+------------+

# Write (Raft replicates to majority before returning):
$ etcdctl put /config/feature-flag "enabled"
OK  # Returned after majority ACK (Raft commit)

# Read (linearisable — contacts leader to confirm):
$ etcdctl get /config/feature-flag
/config/feature-flag
enabled

# Simulate leader failure (stop etcd2):
$ systemctl stop etcd2
# Raft: etcd1 or etcd3 detects missed heartbeats (150-300ms timeout)
# New election in term 16: one of etcd1/etcd3 becomes leader.
$ etcdctl endpoint status --write-out=table
# etcd2 missing, etcd1 or etcd3 now shows IS_LEADER=true, RAFT_TERM=16
```

---

### 🔄 How It Connects (Mini-Map)

```
Consensus (agreement on a value/order)
        │
        ▼
Raft ◄──── (you are here)
(understandable consensus: leader election + log replication + safety)
        │
        ├── Leader Election (Raft's election sub-problem)
        ├── Log Replication (the core Raft mechanism)
        └── etcd / CockroachDB (production systems built on Raft)
```

---

### 💻 Code Example

**CockroachDB: Raft groups per range (shard):**

```sql
-- CockroachDB uses Raft internally per 64MB "range" (shard).
-- Each range is replicated across 3 nodes (Raft group of 3).
-- Writes to any key: routed to that key's range leader → Raft commit → applied.

-- Create table (data distributed across ranges, each range = separate Raft group):
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id BIGINT NOT NULL,
    balance DECIMAL(15,2) NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Write: goes to Raft leader for the range containing this row:
INSERT INTO accounts (user_id, balance) VALUES (1001, 1000.00);
-- Internally: Raft AppendEntries to 2 followers → majority ACK → commit → CRDB responds OK.

-- Show Raft ranges for this table:
SHOW RANGES FROM TABLE accounts WITH DETAILS;
-- Shows: range_id, start_key, end_key, replicas (3 nodes), lease_holder (current Raft leader)

-- Force re-balance (change which nodes host a range's replicas):
-- ALTER RANGE RELOCATE ALL FROM <store_id> TO <store_id>;
-- CockroachDB moves Raft log entries and state to new replicas safely.

-- Raft performance tuning:
-- Batch writes for higher throughput (CockroachDB auto-batches):
BEGIN;
  INSERT INTO accounts VALUES ...;
  INSERT INTO accounts VALUES ...;
  INSERT INTO accounts VALUES ...;
COMMIT;
-- One Raft round per COMMIT (not per INSERT) → 3× fewer Raft rounds than individual writes.
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Raft is just Paxos with better documentation | Raft and Paxos have different core algorithms. Paxos is based on "ballots" and "promises" with single-decree (one-value) consensus, extended to multi-Paxos for log replication. Raft is designed from the start for replicated log with built-in leader election, log matching property, and explicit safety proofs. The understandability difference is real: Raft has cleaner state (roles, terms, indices) compared to Paxos's abstract ballot numbers |
| Raft guarantees zero data loss | Raft guarantees no loss of COMMITTED entries. Entries that were accepted by the leader but not yet replicated to a majority can be lost if the leader crashes before a majority ACK. Clients that don't receive a response (timeout) must retry — the entry may or may not have been committed. Applications need idempotency (e.g., client-provided unique request ID) to handle retries safely |
| Raft requires all 3 nodes to be healthy to serve requests | Raft requires a majority (2 of 3, or 3 of 5) to commit writes. Read-only queries can be served by the leader alone (ReadIndex protocol) or by any node (serialisable reads). The cluster stops accepting WRITES when majority is unavailable — but can continue serving reads from the leader. 3-node cluster: 1 failure → reads continue, writes continue. 2 failures → reads may continue (from remaining node), writes stop |
| Raft's leader is a performance bottleneck that can't be scaled | The leader is a bottleneck for a single Raft group. Systems like CockroachDB and TiKV shard data across thousands of Raft groups (one per partition/range). Each range has its own leader — different keys can have leaders on different nodes. This distributes the write load across all nodes in the cluster. The per-Raft-group leader bottleneck becomes irrelevant at the cluster level |

---

### 🔥 Pitfalls in Production

**Raft log growing unboundedly due to missing snapshot configuration:**

```
PROBLEM: etcd cluster in production for 2 years without snapshot enabled.
         Raft log: 50 million entries. etcd startup: 30 minutes to replay log.
         New etcd member added: 4 hours to sync via log replay.
         
  etcd: snapshotCount = 0 (default: was not set, treated as "never snapshot")
  
  Impact:
    etcd restart (during upgrade): 30 minutes downtime.
    Adding new member: 4 hours catch-up (cannot serve Kubernetes API during sync).
    etcd data directory: 50GB disk usage (just logs).
    
BAD: Missing snapshot configuration in etcd:
  # /etc/etcd/etcd.conf — missing snapshot settings:
  # No snapshot-count or auto-compaction configured.
  
FIX: Configure snapshot and compaction in etcd:
  # /etc/etcd/etcd.conf:
  snapshot-count: 10000        # Take snapshot every 10000 Raft log entries
  auto-compaction-retention: 1 # Compact revision history older than 1 hour
  auto-compaction-mode: periodic
  
  # For existing large log — manual compaction:
  # 1. Find current revision:
  $ REV=$(etcdctl endpoint status --write-out=json | python3 -c "import json,sys; print(json.load(sys.stdin)[0]['Status']['header']['revision'])")
  # 2. Compact to revision (discard history before REV):
  $ etcdctl compact $REV
  # 3. Defragment (reclaim disk space):
  $ etcdctl defrag --endpoints=https://etcd1:2379,https://etcd2:2379,https://etcd3:2379
  
  # After fix:
  # etcd restart: < 1 minute (applies snapshot + recent log entries only).
  # New member sync: send snapshot (~MB) + recent log → minutes, not hours.
```

---

### 🔗 Related Keywords

- `Leader Election` — Raft's first sub-problem (term-based election with majority votes)
- `Paxos` — older consensus algorithm; Raft was designed as a more understandable alternative
- `etcd` — most widely used Raft implementation (Kubernetes backing store)
- `Log Replication` — the core mechanism: leader replicates entries, commits when quorum ACKs

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Leader election + log replication + safety│
│              │ = replicated state machine on N nodes     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Strongly consistent distributed state:    │
│              │ config, locks, metadata, distributed DB   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Cross-region writes (200ms+ RTT per write)│
│              │ or high-throughput events (use Kafka)     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Parliament: PM proposes bills, passed    │
│              │  by majority, new PM has full records."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Paxos → etcd → CockroachDB → Log         │
│              │ Replication → Quorum                      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A 5-node Raft cluster has: N1=leader(term=3), N2, N3 have log up to index=100. N4 and N5 only have log up to index=95 (they were slow). N1 crashes. N4 tries to become leader: sends RequestVote with lastLogIndex=95, lastLogTerm=3. N2 has lastLogIndex=100. Does N2 vote for N4? What if N4 sends to N5 first (N5 also has index=95) — can N4 become leader? What happens to entries 96-100?

**Q2.** CockroachDB creates a separate Raft group for each "range" (64MB partition). A cluster has 1000 ranges across 3 nodes. Each range has its own leader. Write: client inserts a row spanning 2 ranges (large insert). CockroachDB needs to atomically commit to both ranges' Raft groups. What coordination mechanism does CockroachDB use for cross-range atomic writes? What are the failure scenarios during this cross-range atomic commit?
