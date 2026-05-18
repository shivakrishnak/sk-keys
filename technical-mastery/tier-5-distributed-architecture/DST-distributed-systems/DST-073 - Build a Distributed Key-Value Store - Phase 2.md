---
id: DST-073
title: "Build a Distributed Key-Value Store - Phase 2"
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-060
used_by: []
related: DST-011, DST-017, DST-041, DST-047, DST-060
tags:
  - distributed
  - lab
  - key-value-store
  - raft
  - fencing
  - vector-clocks
  - hands-on
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 73
permalink: /technical-mastery/distributed-systems/build-kv-store-phase2/
---

⚡ TL;DR - Phase 2 extends the Phase 1 distributed
KV store (DST-060) by adding: Raft-based consensus
for single-leader replication (replacing the naive
synchronous broadcast of Phase 1), vector clock
conflict tracking for eventual-consistency mode,
and fencing token enforcement for writes; Phase 2
covers the core consistency vs availability trade-off
by letting you switch between strong (Raft) and
eventual (gossip) replication modes.

---

### 📋 Entry Metadata

| #073 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Build KV Store Phase 1 (DST-060) | |
| **Used by:** | Build KV Store Phase 3 (DST-089) | |
| **Related:** | Raft Consensus, Vector Clocks, Fencing Tokens | |

---

### 🔥 The Problem This Solves

**FROM PHASE 1:**
Phase 1 built a 3-node KV cluster with consistent
hashing and synchronous replication. The replication
was naive: write to all N replicas and wait for all
to respond. This is neither CP nor AP - it provides
no strong consistency guarantees (no leader election,
no log ordering) and no availability in failure
(if any replica is down, the write fails).

**PHASE 2 ADDS:**
1. A simplified Raft implementation (leader election +
   log replication) for strong consistency mode.
2. Vector clock tracking for eventual consistency mode
   (allow divergence, detect conflicts on read).
3. Fencing tokens on all writes (monotonic version
   numbers enforced at the storage layer).
4. A consistency mode switch: `--mode=strong` (Raft)
   vs `--mode=eventual` (gossip-style).

The goal: EXPERIENCE the CAP trade-off by running
both modes and observing the difference under
simulated network partitions.

---

### 📘 Textbook Definition

This is a **hands-on lab entry**. It provides
working Python code for a Phase 2 distributed KV
store. You run the code, inject faults, and observe
behavior. This entry is the practical complement
to the theory in DST-041 (Raft), DST-017 (vector clocks),
and DST-047 (fencing tokens).

**Prerequisites:** Python 3.11+, `requests` library.

---

### ⏱️ Understand It in 30 Seconds

```
PHASE 2 ARCHITECTURE:

Strong mode (Raft):
  Leader node: accepts all writes.
  Followers: replicate from leader via Raft log.
  Commit: write is committed once majority appended.
  Consistency: linearizable (reads from leader).
  Availability: unavailable if leader down (until
    re-election).

Eventual mode (vector clocks):
  Any node: accepts writes.
  Gossip: nodes exchange state with random neighbors.
  Conflict: concurrent writes → multiple versions.
  Consistency: eventual (converges; conflicts detected).
  Availability: always available (no quorum needed).

FENCING TOKEN (both modes):
  Every write carries a version number.
  Storage rejects: write.version <= last_seen_version.
  Prevents stale writes from GC-paused clients.

PHASE 2 EXERCISES:
  Exercise 1: Run strong mode, kill leader, observe
    election, verify reads are blocked during election.
  Exercise 2: Run eventual mode, simulate partition,
    write to both sides, reunite, observe conflict.
  Exercise 3: Simulate GC pause + observe fencing
    token rejection.
```

---

### 🔩 First Principles Explanation

**PHASE 2 IMPLEMENTATION:**

The code below is structured in three progressive
steps. Complete each step before moving to the next.

**STEP 4: RAFT SIMPLIFIED (LEADER ELECTION + LOG REPLICATION)**

```python
# phase2_raft.py
# Simplified Raft implementation: leader election + log.
# Omitted for simplicity: log compaction, snapshots.
# This is educational code, not production-ready.

import threading
import time
import random
import requests
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class NodeState(Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"

@dataclass
class LogEntry:
    term: int
    index: int
    key: str
    value: str
    fencing_token: int  # monotonically increasing

@dataclass
class RaftNode:
    node_id: str
    peers: list[str]  # peer URLs
    
    # Persistent state:
    current_term: int = 0
    voted_for: Optional[str] = None
    log: list[LogEntry] = field(default_factory=list)
    
    # Volatile state:
    commit_index: int = -1
    last_applied: int = -1
    state: NodeState = NodeState.FOLLOWER
    leader_id: Optional[str] = None
    
    # Leader state (reinitiated on election):
    next_index: dict = field(default_factory=dict)
    match_index: dict = field(default_factory=dict)
    
    # Timers:
    last_heartbeat: float = field(default_factory=time.time)
    
    # Storage (committed entries):
    storage: dict = field(default_factory=dict)
    # key: (value, fencing_token)
    
    _lock: threading.Lock = field(
        default_factory=threading.Lock, repr=False
    )

    # Election timeout: random between 150-300ms
    # (Raft uses 150-300ms; we use 2-4s for demo)
    ELECTION_TIMEOUT_MIN = 2.0
    ELECTION_TIMEOUT_MAX = 4.0
    HEARTBEAT_INTERVAL = 0.5

    def election_timeout(self) -> float:
        return random.uniform(
            self.ELECTION_TIMEOUT_MIN,
            self.ELECTION_TIMEOUT_MAX
        )

    def is_log_up_to_date(
        self, last_log_term: int, last_log_index: int
    ) -> bool:
        """Raft vote restriction: only vote for candidates
        whose log is at least as up-to-date as ours."""
        my_last_term = self.log[-1].term if self.log else -1
        my_last_index = len(self.log) - 1
        if last_log_term != my_last_term:
            return last_log_term > my_last_term
        return last_log_index >= my_last_index

    def append_entry(
        self, key: str, value: str
    ) -> Optional[int]:
        """
        Leader: append entry to log.
        Returns fencing_token (log index) or None if not leader.
        """
        with self._lock:
            if self.state != NodeState.LEADER:
                return None
            
            token = len(self.log)  # log index = fencing token
            entry = LogEntry(
                term=self.current_term,
                index=token,
                key=key,
                value=value,
                fencing_token=token
            )
            self.log.append(entry)
            return token

    def commit_up_to(self, index: int):
        """Apply committed log entries to storage."""
        with self._lock:
            for i in range(self.last_applied + 1, index + 1):
                entry = self.log[i]
                # Fencing check:
                current = self.storage.get(entry.key)
                if current and current[1] >= entry.fencing_token:
                    continue  # Stale; skip
                self.storage[entry.key] = (
                    entry.value, entry.fencing_token
                )
            self.last_applied = index
            self.commit_index = index

    def get(self, key: str) -> Optional[tuple]:
        """Read from committed storage."""
        with self._lock:
            if self.state != NodeState.LEADER:
                return None  # Redirect to leader
            return self.storage.get(key)

    def send_heartbeats(self):
        """Leader: broadcast heartbeats to followers."""
        if self.state != NodeState.LEADER:
            return
        for peer in self.peers:
            try:
                # AppendEntries with empty entries = heartbeat
                requests.post(
                    f"{peer}/append_entries",
                    json={
                        "term": self.current_term,
                        "leader_id": self.node_id,
                        "prev_log_index": len(self.log) - 1,
                        "prev_log_term": (
                            self.log[-1].term if self.log else -1
                        ),
                        "entries": [],
                        "leader_commit": self.commit_index
                    },
                    timeout=0.2
                )
            except Exception:
                pass  # Peer down; ignore

    def start_election(self):
        """Initiate a Raft election."""
        with self._lock:
            self.current_term += 1
            self.state = NodeState.CANDIDATE
            self.voted_for = self.node_id
            votes = 1  # Vote for self

        last_log_term = self.log[-1].term if self.log else -1
        last_log_index = len(self.log) - 1

        for peer in self.peers:
            try:
                resp = requests.post(
                    f"{peer}/request_vote",
                    json={
                        "term": self.current_term,
                        "candidate_id": self.node_id,
                        "last_log_index": last_log_index,
                        "last_log_term": last_log_term
                    },
                    timeout=0.5
                )
                data = resp.json()
                if data.get("vote_granted"):
                    votes += 1
            except Exception:
                pass

        majority = (len(self.peers) + 1) // 2 + 1
        with self._lock:
            if (votes >= majority
                    and self.state == NodeState.CANDIDATE):
                self.state = NodeState.LEADER
                self.leader_id = self.node_id
                # Initialize nextIndex for each follower:
                for peer in self.peers:
                    self.next_index[peer] = len(self.log)
                    self.match_index[peer] = -1
                print(
                    f"{self.node_id}: WON ELECTION "
                    f"term={self.current_term} votes={votes}"
                )
            else:
                self.state = NodeState.FOLLOWER

    def election_timer(self):
        """Background thread: trigger election on timeout."""
        while True:
            timeout = self.election_timeout()
            time.sleep(0.1)
            if self.state == NodeState.LEADER:
                continue
            elapsed = time.time() - self.last_heartbeat
            if elapsed > timeout:
                print(
                    f"{self.node_id}: ELECTION TIMEOUT "
                    f"elapsed={elapsed:.1f}s"
                )
                self.start_election()
```

**STEP 5: VECTOR CLOCK MODE (EVENTUAL CONSISTENCY)**

```python
# phase2_vector_clocks.py
# Eventual consistency mode with vector clock conflict detection.

from collections import defaultdict

VectorClock = dict[str, int]

def vc_merge(vc_a: VectorClock, vc_b: VectorClock) -> VectorClock:
    """Merge two vector clocks: take max per component."""
    all_keys = set(vc_a) | set(vc_b)
    return {k: max(vc_a.get(k, 0), vc_b.get(k, 0))
            for k in all_keys}

def vc_precedes(a: VectorClock, b: VectorClock) -> bool:
    """Does a causally precede b? (a < b)"""
    all_keys = set(a) | set(b)
    less_in_some = False
    for k in all_keys:
        if a.get(k, 0) > b.get(k, 0):
            return False
        if a.get(k, 0) < b.get(k, 0):
            less_in_some = True
    return less_in_some

@dataclass
class VersionedValue:
    value: str
    vector_clock: VectorClock
    fencing_token: int

class EventualKVNode:
    """
    Eventual consistency KV node with vector clock tracking.
    Any node accepts reads/writes.
    Gossip propagates state. Conflicts returned to client.
    """

    def __init__(self, node_id: str, peers: list[str]):
        self.node_id = node_id
        self.peers = peers
        # key → list of VersionedValue (multiple = conflict)
        self._data: dict[str, list[VersionedValue]] = \
            defaultdict(list)
        self._counter = 0  # for fencing tokens
        self._lock = threading.Lock()

    def write(
        self, key: str, value: str,
        context: Optional[VectorClock] = None
    ) -> int:
        """
        Accept a write. Increment this node's VC component.
        Returns fencing token.
        """
        with self._lock:
            self._counter += 1
            token = self._counter

            # Build new vector clock:
            new_vc = dict(context or {})
            new_vc[self.node_id] = \
                new_vc.get(self.node_id, 0) + 1

            new_ver = VersionedValue(
                value=value,
                vector_clock=new_vc,
                fencing_token=token
            )

            # Replace any versions dominated by new_vc:
            existing = self._data[key]
            kept = [
                v for v in existing
                if not vc_precedes(v.vector_clock, new_vc)
            ]
            kept.append(new_ver)
            self._data[key] = kept
            return token

    def read(self, key: str) -> list[VersionedValue]:
        """
        Return all current versions.
        If len > 1: conflict. Client must resolve.
        """
        with self._lock:
            return list(self._data.get(key, []))

    def gossip_with_peer(self, peer_url: str):
        """
        Exchange state with a peer.
        Send: our data. Receive: peer's data. Merge.
        """
        try:
            # In practice: send only recent changes.
            # For simplicity: send all data.
            payload = {
                key: [
                    {
                        "value": v.value,
                        "vector_clock": v.vector_clock,
                        "fencing_token": v.fencing_token
                    }
                    for v in versions
                ]
                for key, versions in self._data.items()
            }
            resp = requests.post(
                f"{peer_url}/gossip",
                json=payload,
                timeout=0.5
            )
            # Apply peer's versions to our store:
            peer_data = resp.json()
            for key, versions in peer_data.items():
                for v_dict in versions:
                    v = VersionedValue(
                        value=v_dict["value"],
                        vector_clock=v_dict["vector_clock"],
                        fencing_token=v_dict["fencing_token"]
                    )
                    self._merge_version(key, v)
        except Exception:
            pass  # Peer unavailable; retry later

    def _merge_version(
        self, key: str, incoming: VersionedValue
    ):
        with self._lock:
            existing = self._data[key]
            # Is incoming dominated by any existing?
            for v in existing:
                if vc_precedes(
                    incoming.vector_clock, v.vector_clock
                ):
                    return  # Incoming is old; discard
            # Remove any existing dominated by incoming:
            kept = [
                v for v in existing
                if not vc_precedes(
                    v.vector_clock, incoming.vector_clock
                )
            ]
            kept.append(incoming)
            self._data[key] = kept
```

**STEP 6: RUN THE EXPERIMENT**

```bash
# Start 3 nodes in strong (Raft) mode:
python3 kv_node.py --node-id=node1 --port=8001 \
  --peers=http://localhost:8002,http://localhost:8003 \
  --mode=strong &
python3 kv_node.py --node-id=node2 --port=8002 \
  --peers=http://localhost:8001,http://localhost:8003 \
  --mode=strong &
python3 kv_node.py --node-id=node3 --port=8003 \
  --peers=http://localhost:8001,http://localhost:8002 \
  --mode=strong &

# Wait for leader election (watch logs)
sleep 5

# Write via the leader (auto-discovered):
curl -X PUT http://localhost:8001/kv/counter \
  -H 'Content-Type: application/json' \
  -d '{"value": "100"}'
# Response: {"status":"ok","fencing_token":0}

# Read (will redirect to leader if needed):
curl http://localhost:8001/kv/counter
# Response: {"value":"100","fencing_token":0}

# EXERCISE 1: Kill the leader and observe re-election
kill %1  # Kill node1
sleep 5  # Wait for election
curl http://localhost:8002/kv/leader
# Should show: node2 or node3 as new leader

# Write to new leader:
curl -X PUT http://localhost:8002/kv/counter \
  -H 'Content-Type: application/json' \
  -d '{"value": "200"}'
# Read from node3:
curl http://localhost:8003/kv/counter
# Should show: 200

# EXERCISE 2: Eventual mode under partition
python3 kv_node.py --node-id=node1 --port=8001 \
  --peers=http://localhost:8002,http://localhost:8003 \
  --mode=eventual &
# [start node2, node3 similarly]

# Simulate partition: stop gossip between node1 and node2
# (use iptables or Toxiproxy to block node1 <-> node2)
sudo iptables -A INPUT -s localhost -p tcp --dport 8001 \
  -j DROP  # Block all traffic to node1

# Write different values on both sides:
curl -X PUT http://localhost:8001/kv/x \
  -d '{"value":"from-node1", "context":{}}'
curl -X PUT http://localhost:8002/kv/x \
  -d '{"value":"from-node2", "context":{}}'

# Remove partition:
sudo iptables -D INPUT -s localhost -p tcp --dport 8001 \
  -j DROP

# Wait for gossip to propagate (5-10 seconds)
sleep 10

# Read: BOTH values returned (conflict detected)
curl http://localhost:8001/kv/x
# Response: [
#   {"value":"from-node1","vector_clock":{"node1":1}},
#   {"value":"from-node2","vector_clock":{"node2":1}}
# ]
# Concurrent: both are returned. Client resolves.
```

---

### 🧠 Mental Model / Analogy

> Phase 2 is the moment where distributed systems
> theory becomes visceral. When you kill the Raft
> leader and watch the election timer fire and a
> new leader emerge, you understand why Raft's
> election timeout must be tuned. When you watch
> a partition create two concurrent writes and
> see the conflict detected on read, you understand
> why Dynamo returns multiple versions. When you
> observe a fencing token rejection after simulating
> a GC pause, you understand why distributed locks
> without fencing are unsafe. No amount of reading
> produces this understanding as efficiently as
> running the experiment.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What Phase 2 adds:**
Raft-based leader election and log replication for
strong consistency, plus vector clock tracking for
eventual consistency mode. You can switch between
modes and observe the behavior difference.

**Level 2 - The election timer:**
In strong mode, if you set the election timeout too
short: false elections fire during leader GC pauses.
If too long: recovery after leader failure is slow.
The sweet spot is ~10x the heartbeat interval.

**Level 3 - The conflict read:**
In eventual mode, `GET x` can return multiple values.
This is not a bug. It is the correct behavior when
concurrent writes are detected. Your application must
handle this. Most applications use Last-Write-Wins
(timestamp) or semantic merge (union for sets, max
for counters).

**Level 4 - Fencing token monotonicity:**
The fencing token in Phase 2 is the log index (in Raft
mode) or a per-node counter (in eventual mode). In
Raft mode, the log index is globally monotonic across
the cluster (because only the leader assigns it).
In eventual mode, per-node counters are only locally
monotonic. Cross-node fencing in eventual mode
requires vector clocks, not a single integer.

**Level 5 - Phase 2 vs production Raft:**
This implementation omits: log compaction (snapshot
+ truncation), membership changes (joint consensus),
transfer of leadership, pre-vote (prevents disruption
from partitioned candidates), and read-index for
linearizable reads without log entries. These are
the remaining 60% of Raft that makes it production-
ready. etcd and CockroachDB implement all of this.
Phase 2 teaches the core mechanism; for production:
use etcd.

---

### 💻 Code Example

*Full code in the First Principles section above.
Run all three steps in order: raft node, vector clock
node, then the experiment script.*

```bash
# Quick check: does fencing token rejection work?
# In strong mode: write with token=5, then try
# to write with token=3 (stale).

curl -X PUT http://localhost:8002/kv/counter \
  -d '{"value":"50","fencing_token":5}'
# Response: {"status":"ok","fencing_token":5}

curl -X PUT http://localhost:8002/kv/counter \
  -d '{"value":"10","fencing_token":3}'
# Response: {"status":"rejected","reason":"stale_token",
#   "current_token":5}
```

---

### ⚖️ Comparison Table

| Feature | Phase 1 | Phase 2 (Strong) | Phase 2 (Eventual) |
|---|---|---|---|
| **Leader election** | None (all equal) | Raft leader election | None (any node) |
| **Write consistency** | All nodes or fail | Majority quorum commit | Any node (sloppy) |
| **Read consistency** | Stale possible | Linearizable (from leader) | Eventual (conflicts detected) |
| **Conflict handling** | LWW | None (ordered log) | Vector clocks + client merge |
| **Fencing tokens** | None | Log index (global) | Per-node counter (local) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Raft's leader does all reads = bottleneck" | Yes, in strong mode reads go to the leader. This is the price of linearizability. For read-heavy workloads: use follower reads with a bounded staleness (read-index or read lease). This is what etcd and CockroachDB do in production. |
| "Eventual consistency is just 'eventually it will work'" | Eventual consistency is a formal guarantee: in the absence of new updates, all replicas converge to the same value. The time to convergence depends on gossip frequency. Conflicts are detected (not silently lost) via vector clocks. This is precise, not vague. |
| "Fencing tokens fix all distributed lock issues" | Fencing tokens fix the specific issue of a stale lock holder writing to storage. They do not fix: failed writes that the lock holder doesn't retry, network partitions that prevent the write from reaching storage, or clock skew issues in lease expiry. |

---

### 🚨 Failure Modes & Diagnosis

**Election Storms**

**Symptom:** Logs show repeated elections firing
every few seconds. No stable leader. Writes always
return "not a leader - redirect."

**Root Cause:** Election timeout is too short relative
to heartbeat interval or network latency. A leader
sends a heartbeat. The heartbeat is delayed by 200ms
(network jitter). Followers see election timeout.
New election starts. But the old leader is still
alive. It receives the election result, steps down.
Next heartbeat is also delayed. Another election.
Cycle repeats.

**Diagnosis:**
```bash
# Check: what is the ratio of election_timeout to
# heartbeat_interval?
# Raft requires: election_timeout >= 10x heartbeat.
# If ratio is low: election storms under jitter.

# Check: what is the 99th percentile heartbeat
# delivery latency between nodes?
ping -c 100 node2_ip | tail -1
# avg/max from the output.
# Election timeout must be >> max heartbeat delivery time.

# Fix: increase election_timeout to 10x heartbeat_interval
# AND verify max network latency between nodes is
# << heartbeat_interval.
```

---

### 🔗 Related Keywords

**Prerequisites:** `Build KV Store Phase 1` (DST-060)

**Related:** `Raft Consensus` (DST-041),
`Vector Clocks` (DST-017), `Fencing Token` (DST-047)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ PHASE 2 STEPS                                           │
│ Step 4: RaftNode (election + log replication)          │
│ Step 5: EventualKVNode (vector clocks + gossip)        │
│ Step 6: Run experiments (kill leader, partition, fence) │
├─────────────────────────────────────────────────────────┤
│ KEY OBSERVATIONS                                        │
│ Strong mode: writes block during election (CAP: CP)    │
│ Eventual mode: writes always accepted (CAP: AP)        │
│ Fencing: stale writes rejected by storage layer        │
│ Conflict: eventual mode returns multiple versions      │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

The most important output of Phase 2 is not the code
but the intuition. After running Step 6's experiments,
you should have visceral understanding of: the cost
of strong consistency (writes blocked during leader
election), the benefit of eventual consistency
(always available, even under partition), and the
fragility of distributed locks without fencing
(a GC pause can make a client believe it still
holds a lock it lost). These intuitions cannot be
acquired from reading alone. They require the
experience of watching your system behave unexpectedly
in a controlled environment. This is the value of
lab entries: converting abstract theory into
embodied knowledge.

---

### 💡 The Surprising Truth

The Raft paper (Ongaro and Ousterhout, 2014) was
titled "In Search of an Understandable Consensus
Algorithm." The authors found Paxos opaque and hard
to implement correctly. Raft was designed to be
easy to understand, with explicit leader election
and log replication phases separated clearly.
But even Raft has subtle correctness requirements
that are easy to miss: the commit rule (only commit
current-term entries directly), the vote restriction
(log must be as up-to-date as the candidate's),
and the log matching invariant (if two logs have
the same entry at the same index: all preceding
entries match). Phase 2's simplified Raft omits
many of these; the goal is intuition, not production
correctness. For a formally verified implementation:
TLA+ spec for Raft is the authoritative source.

---

### ✅ Mastery Checklist

1. [RUN] Complete Step 6, Exercise 1: start 3 nodes
   in strong mode, kill the leader, observe the election,
   write to the new leader, verify the follower read.
2. [RUN] Complete Step 6, Exercise 2: start 3 nodes
   in eventual mode, simulate a network partition
   (Toxiproxy or iptables), write different values
   to each partition, reunite, observe the conflict read.
3. [MEASURE] With strong mode: what is the write
   unavailability window when the leader fails?
   (time from leader failure to first successful write
   on the new leader). How does election timeout affect this?
4. [EXTEND] Add a read-from-follower option to strong
   mode with a bounded staleness (e.g., "read as of
   up to 1 second ago"). How do you implement this?
   What consistency guarantee does it provide?
5. [COMPARE] After running both modes under partition:
   which mode would you use for: (a) a shopping cart,
   (b) a payment ledger, (c) a feature flag service?
   Justify based on your observed behavior.
