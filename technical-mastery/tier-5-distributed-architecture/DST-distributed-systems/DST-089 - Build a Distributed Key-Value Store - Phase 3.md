---
id: DST-089
title: Build a Distributed Key-Value Store - Phase 3
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-060, DST-073
used_by: []
related: DST-019, DST-020, DST-060, DST-062, DST-073
tags:
  - distributed
  - lab
  - key-value-store
  - raft
  - log-compaction
  - snapshot
  - multi-raft
  - sharding
  - membership-change
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 89
permalink: /technical-mastery/distributed-systems/build-kv-store-phase3/
---

⚡ TL;DR - Phase 3 completes the distributed key-
value store started in Phase 1 (DST-060) and extended
in Phase 2 (DST-073): this lab adds log compaction
(Raft snapshot + truncation to prevent unbounded
log growth), dynamic membership change (adding and
removing nodes without downtime using Raft's joint
consensus), multi-Raft sharding (a router maps keys
to one of N Raft groups), and a production-quality
end-to-end test suite with chaos scenarios; by the
end of Phase 3, you have a sharded, compacted,
reconfigurable Raft-based KV store - the same
architecture used by etcd, CockroachDB, and TiKV.

---

### 📋 Entry Metadata

| #089 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Build KV Store Phase 1 (DST-060), Phase 2 (DST-073) | |
| **Used by:** | N/A (final entry in the series) | |
| **Related:** | Paxos (DST-019), Raft (DST-020), Raft Internals (DST-062) | |

---

### 🔥 The Problem This Solves

**WHY PHASE 3:**
After Phase 2: you have a working single-shard
Raft KV store with leader election, log replication,
and basic vector-clock eventual consistency.
But there are three unsolved problems:

1. **Log growth unbounded.** Raft's log grows indefinitely.
   After 1M write operations: the log takes gigabytes.
   Node restart requires replaying ALL entries. Slow.
   FIX: log compaction (snapshot + truncation).

2. **Single shard.** One Raft group holds all data.
   Write throughput is limited by the leader's capacity.
   FIX: multi-Raft sharding (N Raft groups, each owns a key range).

3. **Static cluster.** Adding or removing nodes requires
   downtime. Not production-grade.
   FIX: Raft membership change (joint consensus).

Phase 3 addresses all three.

---

### 📘 Textbook Definition

**Raft log compaction:** the process of replacing
a prefix of the Raft log with a snapshot (a complete
state machine image at a given log index).
After snapshotting at index N: log entries 1..N
are deleted. Entries N+1.. remain.

**Raft membership change (joint consensus):**
Raft's algorithm for safely changing the set of
cluster nodes. During the transition, a "joint
configuration" requires a majority from BOTH the
old and new configuration to commit entries.
This prevents split-brain during the change.

**Multi-Raft (sharding):** dividing the key space
into N ranges, each managed by a separate Raft group.
Each Raft group is independent: its own leader, its
own log, its own consensus. A router (often called
a "placement driver" or "range server") maps keys
to the correct Raft group.

---

### ⏱️ Understand It in 30 Seconds

```
PHASE 3 ARCHITECTURE:

  ┌─────────────────────────────────────────────┐
  │           KV STORE CLIENT                   │
  └────────────────┬────────────────────────────┘
                   │ lookup key → shard
  ┌────────────────▼────────────────────────────┐
  │           ROUTER / PLACEMENT DRIVER         │
  │  shard_id = hash(key) % num_shards          │
  │  shard_map: {shard_id: leader_endpoint}     │
  └──┬──────────────┬──────────────┬────────────┘
     │              │              │
  ┌──▼──┐        ┌──▼──┐       ┌──▼──┐
  │ RAFT│        │ RAFT│       │ RAFT│
  │SHARD│        │SHARD│       │SHARD│
  │  0  │        │  1  │       │  2  │
  │3node│        │3node│       │3node│
  └─────┘        └─────┘       └─────┘
     9 nodes total: 3 shards x 3 nodes.
     
     Each shard = independent Raft group.
     Writes scale: 3 shards = 3x write throughput.
     Failure isolation: shard 0 failure ≠ shard 1 failure.

LOG COMPACTION (per shard):
  Log entry count > threshold (e.g., 10000):
  → Take snapshot of state machine at current index.
  → Truncate log entries [0..snapshot_index].
  → Persist snapshot to disk.
  → Log restarts from snapshot_index + 1.
  → Node restart: load snapshot, replay remaining log.
```

---

### 🔩 First Principles Explanation

**STEP 7: LOG COMPACTION**

```python
import pickle
from dataclasses import dataclass, field
from typing import Optional, Dict

@dataclass
class Snapshot:
    """
    Complete state machine snapshot at a given Raft log index.
    After taking a snapshot at index N:
      - All log entries 0..N can be deleted.
      - On restart: load snapshot, then replay entries N+1..
    """
    last_included_index: int
    last_included_term: int
    data: Dict[str, str]  # The full KV store state

    def to_bytes(self) -> bytes:
        return pickle.dumps(self)

    @staticmethod
    def from_bytes(b: bytes) -> "Snapshot":
        return pickle.loads(b)


class RaftNodeWithCompaction:
    """
    Extends RaftNode from Phase 2 with:
    - Snapshot creation
    - Log truncation
    - Snapshot installation (for lagging followers)
    """
    
    COMPACTION_THRESHOLD = 10_000  # entries before snapshot

    def __init__(self, node_id: str, peers: list):
        self.node_id = node_id
        self.peers = peers
        self.log = []           # Raft log entries
        self.commit_index = -1
        self.state_machine = {}  # KV store: key→value
        self.snapshot: Optional[Snapshot] = None
        self.snapshot_index = -1  # last entry included in snapshot

    def maybe_compact(self):
        """
        Check if log compaction is needed.
        Take snapshot if log is too large.
        """
        log_size = len(self.log)
        if log_size < self.COMPACTION_THRESHOLD:
            return

        # Snapshot the state machine at commit_index:
        snap = Snapshot(
            last_included_index=self.commit_index,
            last_included_term=self.log[self.commit_index].term,
            data=dict(self.state_machine)  # copy current state
        )
        
        # Persist snapshot to disk:
        snap_bytes = snap.to_bytes()
        with open(f"snapshot_{self.node_id}.bin", "wb") as f:
            f.write(snap_bytes)
        
        # Truncate log: remove entries 0..commit_index.
        # Keep entries commit_index+1.. (not yet snapshotted).
        self.log = self.log[self.commit_index + 1:]
        self.snapshot = snap
        self.snapshot_index = snap.last_included_index
        
        print(f"[{self.node_id}] Compacted log. "
              f"Snapshot at index={self.snapshot_index}. "
              f"Remaining log entries: {len(self.log)}")

    def install_snapshot(self, snap: Snapshot):
        """
        Install a snapshot from the leader.
        Called when a follower is too far behind to catch up
        via normal log replication (its next index is before
        the leader's snapshot_index).
        
        InstallSnapshot RPC (Raft paper Section 7):
          Leader sends snapshot to lagging follower.
          Follower discards its entire log.
          Follower loads snapshot as its state.
          Follower resumes replication from snapshot_index + 1.
        """
        # Discard all existing log entries:
        self.log = []
        self.snapshot = snap
        self.snapshot_index = snap.last_included_index
        self.commit_index = snap.last_included_index
        
        # Restore state machine from snapshot:
        self.state_machine = dict(snap.data)
        
        print(f"[{self.node_id}] Installed snapshot "
              f"at index={snap.last_included_index}. "
              f"State restored: {len(self.state_machine)} keys.")

    def restart_from_disk(self):
        """
        On node restart: load snapshot first, then replay log.
        This is O(|state|) not O(|log|) for the snapshot phase.
        """
        import os
        snap_file = f"snapshot_{self.node_id}.bin"
        
        if os.path.exists(snap_file):
            with open(snap_file, "rb") as f:
                self.snapshot = Snapshot.from_bytes(f.read())
            self.state_machine = dict(self.snapshot.data)
            self.snapshot_index = self.snapshot.last_included_index
            self.commit_index = self.snapshot_index
            print(f"[{self.node_id}] Loaded snapshot "
                  f"at index={self.snapshot_index}.")
        
        # Replay log entries after snapshot:
        for entry in self.log:
            if entry.index > self.snapshot_index:
                self._apply_entry(entry)
        
        print(f"[{self.node_id}] Ready. "
              f"State: {len(self.state_machine)} keys.")
```

**STEP 8: DYNAMIC MEMBERSHIP CHANGE**

```python
# Raft joint consensus for membership change.
# Raft paper Section 6: "Cluster Membership Changes"
# Joint consensus: during transition, majorities
# from BOTH C_old and C_new are required.

@dataclass
class ClusterConfig:
    members: frozenset  # set of node IDs

class MembershipChangeProtocol:
    """
    Implements Raft's joint consensus for safe membership change.
    
    SAFETY INVARIANT:
      During any membership change, there must be only ONE
      cluster configuration that can form a majority.
      The joint configuration (C_old ∪ C_new) prevents
      two separate majorities from forming.
    """

    def __init__(self, current_config: ClusterConfig):
        self.current_config = current_config
        self.joint_config: Optional[ClusterConfig] = None

    def begin_add_node(self, new_node_id: str) -> ClusterConfig:
        """
        Step 1: Add the new node to a joint config.
        Joint = old_members UNION {new_node}.
        Commit the joint config entry to the log.
        During joint config: require majority of BOTH
          old_members AND joint_members to commit.
        """
        joint = ClusterConfig(
            members=frozenset(
                self.current_config.members | {new_node_id}
            )
        )
        self.joint_config = joint
        print(f"Joint config active: {joint.members}")
        return joint

    def commit_joint_config(self):
        """
        Step 2: Once the joint config entry is committed:
        Transition to the new config (C_new).
        The new_node_id is now a full member.
        Old nodes not in C_new are decommissioned.
        """
        self.current_config = self.joint_config
        self.joint_config = None
        print(f"New config committed: {self.current_config.members}")

    def quorum_met(self, votes: frozenset) -> bool:
        """
        During joint config: quorum requires majority of BOTH
        old AND new (joint) configurations.
        This prevents split-brain during the transition.
        """
        old = self.current_config.members
        new = self.joint_config.members if self.joint_config else old
        
        old_majority = len(votes & old) > len(old) // 2
        new_majority = len(votes & new) > len(new) // 2
        
        if self.joint_config:
            # Joint consensus: both must agree.
            return old_majority and new_majority
        else:
            # Normal operation: just current config.
            return old_majority


# DEMO:
config = ClusterConfig(members=frozenset({"A", "B", "C"}))
protocol = MembershipChangeProtocol(config)

# Add node D:
joint = protocol.begin_add_node("D")
print("Joint:", joint.members)  # {A, B, C, D}

# During joint config: majority of both {A,B,C} and {A,B,C,D}
# required. Prevents: A+B+C deciding without D being aware,
# AND D+new_nodes deciding without old cluster consent.

# Example votes: {A, B, D} - does this form quorum?
votes = frozenset({"A", "B", "D"})
print("Quorum met:", protocol.quorum_met(votes))
# old majority: A+B out of {A,B,C}: 2/3 = YES.
# new majority: A+B+D out of {A,B,C,D}: 3/4 = YES.
# Both → True.

# Commit the joint config:
protocol.commit_joint_config()
print("Final config:", protocol.current_config.members)
# → {A, B, C, D}
```

**STEP 9: MULTI-RAFT SHARDING**

```python
# Multi-Raft: divide key space into N shards.
# Each shard is an independent Raft group.

import hashlib

class ShardRouter:
    """
    Routes client requests to the correct shard.
    Each shard is a Raft group (3 nodes).
    """
    
    def __init__(self, num_shards: int):
        self.num_shards = num_shards
        # Shard map: shard_id → leader endpoint.
        # Updated when Raft group leader changes.
        self.shard_leaders: dict[int, str] = {}
    
    def shard_for_key(self, key: str) -> int:
        """Consistent hash: same key always → same shard."""
        h = int(hashlib.sha256(key.encode()).hexdigest(), 16)
        return h % self.num_shards
    
    def get_shard_leader(self, shard_id: int) -> str:
        """Get current leader endpoint for a shard."""
        leader = self.shard_leaders.get(shard_id)
        if not leader:
            raise ShardLeaderNotKnownError(
                f"Leader for shard {shard_id} unknown. "
                "Retry after routing table refresh."
            )
        return leader
    
    def update_leader(self, shard_id: int, leader: str):
        """Called when a shard elects a new leader."""
        self.shard_leaders[shard_id] = leader


class MultiRaftKVClient:
    """
    Client for the multi-shard KV store.
    Routes reads and writes to the correct Raft shard.
    Handles leader changes transparently (retry on redirect).
    """
    
    def __init__(self, router: ShardRouter, max_retries: int = 3):
        self.router = router
        self.max_retries = max_retries
    
    def get(self, key: str) -> Optional[str]:
        shard_id = self.router.shard_for_key(key)
        for attempt in range(self.max_retries):
            try:
                leader = self.router.get_shard_leader(shard_id)
                return raft_rpc.get(leader, key)
            except NotLeaderError as e:
                # The node we contacted is not the leader.
                # The error includes the current leader's address.
                self.router.update_leader(shard_id, e.leader)
            except ShardLeaderNotKnownError:
                # Refresh routing table from placement driver.
                self._refresh_routing_table(shard_id)
        raise MaxRetriesExceeded(key)
    
    def put(self, key: str, value: str) -> None:
        shard_id = self.router.shard_for_key(key)
        for attempt in range(self.max_retries):
            try:
                leader = self.router.get_shard_leader(shard_id)
                raft_rpc.put(leader, key, value)
                return
            except NotLeaderError as e:
                self.router.update_leader(shard_id, e.leader)
        raise MaxRetriesExceeded(key)
    
    def _refresh_routing_table(self, shard_id: int):
        """Query placement driver for current leader."""
        leader = placement_driver.get_leader(shard_id)
        self.router.update_leader(shard_id, leader)
```

**STEP 10: CHAOS TEST SUITE**

```python
# End-to-end chaos test suite for the complete system.
# Tests: correctness under failure conditions.

import random
import threading
import time

class MultiRaftChaosTests:
    """
    Chaos tests for the multi-Raft KV store.
    Each test: normal operations + fault injection.
    Verification: linearizability checker on the operation log.
    """

    def test_leader_failover_during_writes(self, cluster):
        """
        Write 100 keys.
        Kill the leader of shard 0 mid-write.
        Verify: all writes either succeeded or returned error.
        No write returns "success" but data is lost.
        """
        results = {}
        errors = {}

        def writer(key, val):
            try:
                cluster.client.put(key, val)
                results[key] = val
            except Exception as e:
                errors[key] = str(e)

        threads = [
            threading.Thread(target=writer, args=(f"k{i}", f"v{i}"))
            for i in range(100)
        ]
        # Start writers:
        for t in threads:
            t.start()
        # Kill leader of shard 0 after 50ms:
        time.sleep(0.05)
        cluster.kill_shard_leader(shard_id=0)
        # Wait for all writers:
        for t in threads:
            t.join()

        # Wait for new leader election:
        time.sleep(2.0)

        # Verify: every key in `results` must be readable.
        for key, expected in results.items():
            actual = cluster.client.get(key)
            assert actual == expected, (
                f"Lost write! key={key} expected={expected} "
                f"actual={actual}"
            )
        print(f"PASS: {len(results)} writes survived leader failure. "
              f"{len(errors)} writes correctly returned error.")

    def test_log_compaction_and_restart(self, cluster, node):
        """
        Write COMPACTION_THRESHOLD + 100 keys to trigger compaction.
        Kill and restart the node.
        Verify: all keys readable after restart.
        """
        for i in range(10_100):
            cluster.client.put(f"compact_key_{i}", f"val_{i}")
        
        # Verify compaction triggered:
        assert node.snapshot is not None, "Snapshot not taken!"
        assert len(node.log) < 10_100, "Log not compacted!"
        
        # Kill and restart the node:
        cluster.kill_node(node.node_id)
        time.sleep(0.5)
        cluster.restart_node(node.node_id)
        time.sleep(1.0)
        
        # Verify all keys readable (state restored from snapshot):
        for i in range(100):  # sample check
            k = f"compact_key_{i}"
            v = cluster.client.get(k)
            assert v == f"val_{i}", f"Lost key after restart: {k}"
        
        print("PASS: Log compaction and restart verified.")

    def test_add_node_to_cluster(self, cluster, new_node_id):
        """
        Add a 4th node to a 3-node Raft group.
        Verify: new node receives all existing data via log replication.
        Verify: writes during membership change succeed.
        """
        # Write some initial data:
        for i in range(100):
            cluster.client.put(f"before_add_{i}", f"val_{i}")
        
        # Add the new node:
        cluster.add_node(new_node_id, shard_id=0)
        
        # Write more data during membership change:
        for i in range(100):
            cluster.client.put(f"during_add_{i}", f"val_{i}")
        
        # Wait for new node to catch up:
        time.sleep(3.0)
        
        # Verify new node has all data:
        new_node = cluster.get_node(new_node_id)
        for i in range(100):
            assert new_node.state_machine.get(f"before_add_{i}") \
                == f"val_{i}", f"New node missing pre-add key {i}"
            assert new_node.state_machine.get(f"during_add_{i}") \
                == f"val_{i}", f"New node missing during-add key {i}"
        
        print("PASS: Node added to cluster. Data fully replicated.")
```

---

### 🧠 Mental Model / Analogy

> Building this KV store in three phases mirrors
> the journey of real production systems. Phase 1
> (correctness) = making it right. Phase 2 (fault
> tolerance) = making it resilient. Phase 3 (scale
> and operations) = making it production-ready.
> etcd, TiKV, and CockroachDB all started as
> "correct, basic implementations" and added log
> compaction, membership change, and multi-Raft
> over years of engineering. This three-phase
> journey is not just an educational path - it
> is the actual engineering journey of production
> distributed databases.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - Why Phase 3:**
A single-shard Raft KV store is limited in throughput
and has an ever-growing log. Phase 3 adds the
production features needed to run at scale.

**Level 2 - Log compaction:**
Snapshot the state at index N. Delete entries 0..N.
Restart = load snapshot, replay N+1..end.
O(|state|) restart instead of O(|log|) restart.

**Level 3 - Membership change is subtle:**
Joint consensus prevents two independent majorities
from forming during the transition. Without it:
a split-brain during node addition is possible.

**Level 4 - Multi-Raft:**
Sharding the key space to N Raft groups multiplies
write throughput by N. Each group is independent.
The router maps keys to groups. Leader changes
within a shard are transparent to the client.

**Level 5 - This IS how production systems work:**
TiKV (TiDB's storage engine) uses Multi-Raft with
a placement driver (PD) that manages shard leaders,
load balancing, and rebalancing. etcd uses a single
Raft group for its use case (configuration, not
high-throughput data). CockroachDB uses Multi-Raft
with automatic shard splitting when ranges get too
large. This three-phase lab implements the core
of all three systems.

---

### 💻 Code Example

*See the complete implementation of RaftNodeWithCompaction,
MembershipChangeProtocol, MultiRaftKVClient, and
MultiRaftChaosTests in First Principles above.*

---

### ⚖️ Comparison Table

| System | Log Compaction | Membership Change | Sharding |
|---|---|---|---|
| **etcd** | Snapshot (v3) | Joint consensus | Single Raft group |
| **TiKV** | RocksDB SST snapshot | Joint consensus | Multi-Raft + Placement Driver |
| **CockroachDB** | RocksDB snapshot | Joint consensus | Multi-Raft + auto-split |
| **This lab (Phase 3)** | Pickle snapshot | Joint consensus | Hash-based Multi-Raft |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Snapshotting is rare / optional" | In any long-running Raft system: log compaction is mandatory. Without it, the log grows unbounded and restart time grows linearly with uptime. Log compaction is a core production requirement, not an optimization. |
| "Adding a node is simple (just broadcast the new config)" | Adding a node requires joint consensus to prevent split-brain during the transition. Broadcasting the new config directly can result in a period where both old and new majorities are valid simultaneously. |
| "Multi-Raft is just N copies of the same code" | Multi-Raft requires a router (placement driver) that knows which shard is responsible for which key range. It also requires handling leader changes per shard (client must retry to the new leader). The coordination overhead is non-trivial. |
| "Chaos testing is only for large systems" | This lab has ~1000 lines of code and benefits directly from the chaos tests in Step 10. A single bug in the snapshot restore logic would be invisible without restarting a node after compaction. |

---

### 🚨 Failure Modes & Diagnosis

**Snapshot Restore Bug: Missing Entries After Restart**

**Symptom:** After restarting a node that had undergone
log compaction, some keys return `None` that should
have values. The node has fewer keys than its peers.

**Root Cause:** Off-by-one error in log truncation.
After snapshotting at index N: the code deleted
entries `0..N+1` (inclusive of N+1) instead of
`0..N` (inclusive). Entries at index N+1 were
deleted but not yet in the snapshot. On restart:
state machine loaded from snapshot (index N), then
replayed from index N+2 (skipped N+1). Entries
at N+1 were lost.

**Diagnosis:**
```python
# Reproduce the off-by-one error:
# WRONG:
self.log = self.log[self.commit_index + 2:]  # skips N+1

# CORRECT:
self.log = self.log[self.commit_index + 1:]  # keeps N+1..

# DETECTION (add to maybe_compact):
assert self.log[0].index == self.snapshot_index + 1, (
    f"Log compaction gap! "
    f"Snapshot at {self.snapshot_index}, "
    f"first log entry at {self.log[0].index}. "
    f"Gap: entries {self.snapshot_index+1}..{self.log[0].index-1} missing."
)

# PROPERTY TEST (run after each compaction):
def verify_compaction_consistency(node):
    if node.snapshot and node.log:
        expected_first = node.snapshot.last_included_index + 1
        actual_first = node.log[0].index
        assert actual_first == expected_first, (
            f"Compaction gap detected on {node.node_id}"
        )
```

---

### 🔗 Related Keywords

**Prerequisite phases:** `Build KV Store Phase 1` (DST-060),
`Build KV Store Phase 2` (DST-073)

**Underlying algorithms:** `Paxos` (DST-019),
`Raft` (DST-020), `Raft Internals` (DST-062)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ PHASE 3 STEPS                                           │
│ 7: Log compaction (snapshot + truncate)                │
│ 8: Membership change (joint consensus)                 │
│ 9: Multi-Raft sharding (router + N Raft groups)       │
│ 10: Chaos test suite (leader fail, restart, add node) │
├─────────────────────────────────────────────────────────┤
│ LOG COMPACTION:                                         │
│ snapshot(index=N) → delete log[0..N] → persist        │
│ restart: load snapshot + replay log[N+1..]            │
├─────────────────────────────────────────────────────────┤
│ MEMBERSHIP CHANGE:                                      │
│ joint consensus: majority(C_old) AND majority(C_new)  │
│ → prevents split-brain during transition              │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

Completing all three phases of this lab - from a
simple in-memory store to a sharded, compacted,
reconfigurable distributed KV store - demonstrates
a principle that applies to all large systems: the
hardest part is not the algorithm (Raft is well-
specified), it is the engineering discipline of
correct implementation, testing under failure, and
production-quality features (compaction, membership
change) that the paper treats as "implementation
details." Production distributed systems are 10%
algorithm and 90% these "implementation details."
The engineers at etcd, TiKV, and CockroachDB who
implemented these features discovered bugs (off-
by-one in compaction, split-brain in membership
change) that only appear under specific timing
conditions. Chaos tests reveal these bugs in your
code before they appear in production.

---

### 💡 The Surprising Truth

TiKV, the storage engine powering TiDB (a MySQL-
compatible distributed database), was built in Rust
from scratch starting in 2015. The team chose to
implement Multi-Raft rather than use an existing
Raft library because they needed integration with
RocksDB for log compaction, and the existing Raft
libraries did not support the snapshot installation
API they needed. The core Multi-Raft implementation
took 18 months to be production-ready (not counting
edge cases discovered in production afterward).
Three engineers. 18 months. The Raft paper is 18
pages. The gap between "understand the paper" and
"production-ready implementation" is one of the
largest gaps in systems software engineering.
This three-phase lab covers the first 20% of that
gap - and it is the most important 20%.

---

### ✅ Mastery Checklist

1. [IMPLEMENT] Implement `maybe_compact()` from Step 7.
   Write a property test that verifies: after compaction,
   `log[0].index == snapshot.last_included_index + 1`.
   Run it after every 1000 writes.
2. [TRACE] Describe the sequence of log entries and
   snapshot state for this scenario: Node has log
   [index=0..999]. Takes snapshot at index=499.
   Truncates. Then fails and restarts.
   What is the restart procedure? What is the final
   state after restart?
3. [IMPLEMENT] Implement `quorum_met()` from Step 8.
   Test: old={A,B,C}, new={A,B,C,D}. Votes={A,B,C}.
   Does quorum pass? Now try votes={A,B,D}. Does it pass?
   What about votes={B,C,D}?
4. [BUILD] Implement `MultiRaftKVClient.get()` with
   retry on NotLeaderError. Test: mid-operation leader
   change triggers a NotLeaderError, client retries
   to the new leader, operation succeeds.
5. [TEST] Implement `test_log_compaction_and_restart`
   from Step 10. Run it against your Phase 2 Raft
   implementation extended with compaction. Does it
   pass? If not: what is the bug?
