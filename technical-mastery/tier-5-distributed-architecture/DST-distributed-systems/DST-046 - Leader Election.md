---
id: DST-046
title: Leader Election
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-014, DST-020, DST-041
used_by: DST-047, DST-048, DST-049
related: DST-020, DST-041, DST-042, DST-047, DST-048, DST-049
tags:
  - distributed
  - leader-election
  - consensus
  - coordination
  - zookeeper
  - etcd
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 46
permalink: /technical-mastery/distributed-systems/leader-election/
---

⚡ TL;DR - Leader Election is the process by which
distributed nodes agree on a single coordinator (leader)
that is responsible for a specific task; it ensures
only one node acts as leader at any time, uses consensus
(Raft, Paxos, ZooKeeper ephemeral nodes) to coordinate
the election, and must handle split-brain prevention
via epoch numbers or fencing tokens.

---

### 📋 Entry Metadata

| #046 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Consistency, Heartbeat/Health Check, Raft | |
| **Used by:** | Fencing Token, Split-Brain, Distributed Locking | |
| **Related:** | Heartbeat, Raft, Paxos, Fencing Token, Split-Brain, Distributed Locking | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Three Kafka broker nodes need to decide which one
manages partition assignment for a topic. Without
election: all three try to assign partitions simultaneously,
each making conflicting decisions about which consumer
gets which partition. Consumers receive duplicate
messages or miss partitions entirely. Kafka needs
exactly one controller. Similarly: primary/replica
election in PostgreSQL streaming replication, leader
in etcd, master in Redis Sentinel. The distributed
system needs exactly one coordinator for certain
operations, but any node can fail at any time.

---

### 📘 Textbook Definition

**Leader Election** is a distributed algorithm that
allows nodes in a cluster to agree on exactly one
node as the designated leader for a specific role or
resource. The leader coordinates operations that
must be performed by exactly one node to maintain
correctness.

**Requirements:**
- **Safety:** At most one leader at any time
- **Liveness:** A leader is eventually elected (as
  long as a quorum is reachable)
- **Fault tolerance:** If the leader fails, a new
  leader is elected within a bounded time

---

### ⏱️ Understand It in 30 Seconds

```
TRIGGER: Current leader stops sending heartbeats.
         Followers detect via missed heartbeat timeout.

ELECTION (Raft example):
  Follower A waits 150ms (random timeout, no heartbeat).
  A increments term, votes for self, sends RequestVote.
  B receives RequestVote(term=3, A's log is up-to-date).
  B: no vote cast in term 3, A's log >= B's log → vote yes.
  C: same → vote yes.
  A: receives 3 votes (including self) = majority.
  A declares itself leader for term 3.
  A starts sending heartbeats. B and C become followers.

GUARANTEE:
  Only one node can receive a quorum of votes per term.
  Previous leader (if still running in partition) has
  lower term → its heartbeats are ignored.
```

---

### 🔩 First Principles Explanation

**ELECTION ALGORITHMS:**

**Bully Algorithm (simple, not partition-tolerant):**

```
Each node has a unique ID. Higher ID wins.

Election trigger: node P detects leader failure.
1. P sends ELECTION message to all nodes with ID > P.
2. If any respond: they take over (higher ID → bully).
3. If none respond: P declares itself leader.
4. P sends COORDINATOR message to all nodes.

Problem: not safe under network partitions.
Two sides of a partition can both elect leaders.
Used in: simple coordinator patterns without partition
tolerance requirements.
```

**ZooKeeper Ephemeral Nodes (practical approach):**

```
All nodes try to create the same ephemeral sequential
node: /election/leader_

ZooKeeper assigns sequence: node_0001, node_0002, node_0003
The node with the LOWEST sequence number is leader.

ALGORITHM:
1. Each node creates /election/leader_ (ephemeral
  sequential)
2. Each node queries all children of /election/
3. The node with the lowest sequence = leader
4. Non-leaders watch the node just before them in sequence
   (not the leader node directly - prevents herd effect)
5. If node_0001 (leader) disconnects:
   ZooKeeper deletes its ephemeral node automatically.
   node_0002 is watching node_0001.
   node_0002 receives deletion notification.
   node_0002 checks: am I now the lowest? Yes → leader.
   node_0002 becomes leader.

WHY WATCH PREVIOUS RATHER THAN LEADER:
   If all nodes watch the leader node:
   When leader dies → all nodes simultaneously try to
   determine if THEY are the new leader → herd effect.
   Watching only the previous node: only one node is
   woken up per failure.
```

**etcd-Based Leader Election (lease approach):**

```
All nodes race to put a key in etcd with a lease (TTL).
etcd guarantees atomic compare-and-swap.

1. Node A: PUT /leader value=A IF NOT EXISTS (with 10s TTL)
   etcd: key doesn't exist → created → A wins
2. Node B: PUT /leader value=B IF NOT EXISTS
   etcd: key exists (A holds it) → rejected → B is follower
3. A must renew lease (PUT with lease renewal) every 5s
   If A fails to renew: key expires after 10s.
4. After expiry: both B and C race to PUT /leader.
   etcd guarantees exactly one succeeds (atomic CAS).
   Winner becomes new leader.
```

**EPOCH NUMBERS:**

```
Every new leader election increments an epoch (term)
number. Old leader commands carry old epoch.

Scenario:
  Leader A (epoch 1) paused (GC pause, network partition).
  B elected as leader (epoch 2).
  A resumes, believes it is still leader (epoch 1).
  A sends write to follower C with epoch 1.
  C checks: my current epoch = 2. 1 < 2 → reject.
  A's stale command is ignored.
  A discovers epoch 2 → steps down → becomes follower.

Epoch numbers prevent stale leaders from corrupting
the system after they are replaced.
```

---

### 🧠 Mental Model / Analogy

> Leader election is like the game "King of the Hill."
> Multiple players compete to be on top. The one on
> top has authority. If the king falls off, there is a
> competition for who takes the top spot. The rules
> ensure only one person can be the king at any time -
> not two half-kings on opposite sides of the hill.
> The epoch number is like a crown: each new king
> gets a new crown with a new serial number. If the
> old king reappears claiming authority, others check
> the crown serial number - old serial means old
> authority, rejected.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is:**
Cluster nodes agree on which one is "in charge" of
a specific task. When the chosen node fails, they
agree on a replacement. Used to ensure exactly one
node does something (assigns partitions, takes writes,
holds a distributed lock).

**Level 2 - ZooKeeper approach:**
Nodes create ephemeral ZooKeeper nodes. The one
with the lowest sequence number is leader. If it
disconnects, its ephemeral node is deleted, and the
next-lowest becomes leader. ZooKeeper's consistency
guarantees make this safe.

**Level 3 - Raft election:**
Raft builds leader election into the consensus
algorithm. The leader with the most up-to-date log
wins. Uses term numbers (epochs) to prevent stale
leaders from acting after replacement.

**Level 4 - Lease-based election:**
etcd and similar systems use time-limited leases:
the leader holds a lease (key with TTL). It must
renew before expiry. If it fails to renew (due to
crash or pause), the lease expires, and a new leader
acquires it via CAS. The lease duration is the
maximum failover time.

**Level 5 - The unsolved problem:**
Even with correct leader election, a paused leader
can cause damage. Example: JVM GC pause for 20
seconds (longer than lease TTL). Leader A pauses,
lease expires, B becomes leader. A resumes, believes
it is still leader, attempts to write to shared storage.
The solution is not just election - it is fencing:
every write by the leader carries a fencing token
(epoch), and the storage rejects writes with old
epoch. Leader election alone does not ensure safety
without fencing. See DST-047.

---

### 💻 Code Example

**etcd Leader Election: Wrong vs Right**

```python
# BAD: Home-rolled leader election without atomicity

import redis
import time

class BadLeaderElection:
    def try_become_leader(self, node_id: str) -> bool:
        r = redis.Redis()
        # BUG 1: Two nodes can execute these lines
        # simultaneously and both see "no leader"
        current = r.get("leader")
        if current is None:
            r.set("leader", node_id)  # Race condition
            return True
        return current.decode() == node_id
```

```python
# GOOD: Atomic CAS-based leader election with lease

import etcd3
import threading
import time
from typing import Optional, Callable

class LeaderElection:
    def __init__(
        self,
        etcd_client,
        election_key: str,
        node_id: str,
        ttl_seconds: int = 10,
        renew_interval: float = 4.0
    ):
        self.client = etcd_client
        self.key = election_key
        self.node_id = node_id
        self.ttl = ttl_seconds
        self.renew_interval = renew_interval
        self._is_leader = False
        self._lease = None
        self._renew_thread: Optional[threading.Thread] = None
        self.on_elected: Optional[Callable] = None
        self.on_demoted: Optional[Callable] = None

    def start(self) -> None:
        """Start participating in leader election."""
        threading.Thread(
            target=self._election_loop, daemon=True
        ).start()

    def is_leader(self) -> bool:
        return self._is_leader

    def _election_loop(self) -> None:
        while True:
            try:
                self._try_acquire_leadership()
            except Exception:
                pass
            time.sleep(1)

    def _try_acquire_leadership(self) -> None:
        """Attempt atomic acquisition of leader key."""
        lease = self.client.lease(self.ttl)

        # Atomic: put key only if it doesn't exist
        # etcd compare-and-swap: create if not exists
        success, response = self.client.transaction(
            compare=[self.client.transactions.version(self.key) == 0],
            success=[self.client.transactions.put(
                self.key, self.node_id, lease=lease
            )],
            failure=[]
        )

        if success:
            self._is_leader = True
            self._lease = lease
            if self.on_elected:
                self.on_elected()
            # Start renewal thread
            self._start_renewal()
        else:
            # Another node holds the lease: watch for expiry
            events, cancel = self.client.watch(self.key)
            for event in events:
                if isinstance(event, etcd3.events.DeleteEvent):
                    cancel()
                    break  # Re-attempt election

    def _start_renewal(self) -> None:
        def renew():
            while self._is_leader:
                time.sleep(self.renew_interval)
                try:
                    self._lease.refresh()
                except Exception:
                    # Renewal failed: step down
                    self._is_leader = False
                    if self.on_demoted:
                        self.on_demoted()
                    break

        self._renew_thread = threading.Thread(
            target=renew, daemon=True
        )
        self._renew_thread.start()

    def resign(self) -> None:
        """Voluntarily step down as leader."""
        if self._is_leader:
            self._is_leader = False
            if self._lease:
                self._lease.revoke()  # Immediate expiry
            if self.on_demoted:
                self.on_demoted()
```

---

### ⚖️ Comparison Table

| Algorithm | Partition Safe | Herd Effect | Complexity | Used In |
|---|---|---|---|---|
| **Bully** | No | No | Low | Textbook only |
| **ZooKeeper ephemeral** | Yes | Mitigated (watch prev) | Medium | Kafka, HBase |
| **Raft election** | Yes | No | Medium | etcd, CockroachDB |
| **etcd lease CAS** | Yes | No | Low (uses etcd) | Kubernetes, Consul |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Leader election ensures only one node acts as leader" | Election ensures only one node WINS the election. A stale leader that was paused (GC, network) may resume and briefly act as leader alongside the new one. Fencing tokens (epoch numbers on writes) are required to prevent stale leaders from corrupting state. |
| "Lease TTL = recovery time" | Lease TTL is the maximum time between leader failure and new leader election. But: (1) the new leader may take additional time to take over operations, and (2) the failed leader may be paused (not failed), so it might resume acting before the TTL if the pause is shorter than TTL. |
| "More candidates = faster election" | More candidates increase the probability of split votes (e.g., in Raft, if randomized timeouts are too similar). Raft uses randomized timeouts specifically to stagger candidates and reduce split-vote probability. |
| "ZooKeeper leader election is free" | Every watch event, ephemeral node, and election attempt has overhead. In large clusters with frequent leader churn, ZooKeeper can become a bottleneck. Raft-based systems (etcd) often perform better at scale. |

---

### 🚨 Failure Modes & Diagnosis

**Double-Leader (Stale Leader Acting After Replacement)**

**Symptom:** Kafka shows duplicate messages being
produced. Two brokers believe they are controller.
Database shows conflicting writes.

**Root Cause:** Leader A paused (GC or network
isolation). B was elected. A resumed and still
believes it is leader (has not discovered new epoch).

**Diagnosis:**
```bash
# Kafka: check which broker believes it is controller:
kafka-topics.sh --bootstrap-server broker1:9092 \
  --describe --topic my-topic | grep "Leader:"
# If different leaders for different partitions point
# to the same broker: might be stale state

# ZooKeeper: check current controller:
echo "get /controller" | zkCli.sh -server zk:2181
# Shows: {"version":X,"brokerid":Y,...}
# Compare with what broker Y believes

# Kafka metrics:
# kafka.controller:type=KafkaController,
#   name=ActiveControllerCount
# Should be exactly 1 across cluster.
# If 2: two controllers - split brain.
```

**Fix:** Upgrade to KRaft mode (Kafka 2.8+) which
uses Raft and epoch-based fencing. For ZooKeeper-based
Kafka: increase GC tuning on controller broker to
prevent long pauses; reduce ZooKeeper session timeout
relative to GC pause duration.

---

### 🔗 Related Keywords

**Prerequisites:** `Consistency` (DST-014),
`Heartbeat and Health Check` (DST-020),
`Raft Consensus Algorithm` (DST-041)

**Builds On This:** `Fencing Token` (DST-047),
`Split-Brain` (DST-048), `Distributed Locking` (DST-049)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT       │ One node = leader for a specific role      │
│ HOW        │ Raft election, ZK ephemeral, etcd lease    │
│ EPOCH      │ Each election increments a monotonic term  │
├────────────┼────────────────────────────────────────────┤
│ SAFETY     │ At most one leader at any time             │
│ LIVENESS   │ Leader elected if quorum reachable         │
├────────────┼────────────────────────────────────────────┤
│ NOT ENOUGH │ Election alone: stale leader can still act │
│ ALSO NEED  │ Fencing token (epoch) on every write       │
├────────────┼────────────────────────────────────────────┤
│ TTL        │ Lease TTL = max time to elect new leader   │
│ RENEW      │ Leader renews at TTL/2 to prevent expiry   │
├────────────┼────────────────────────────────────────────┤
│ ONE-LINER  │ "Elect once, defend always - election is   │
│            │  necessary but not sufficient for safety." │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

Leader election encapsulates the core challenge of
distributed systems: agreement under failure. The
pattern is not limited to "leader" roles - any time
a distributed system needs exactly one node to perform
a task, leader election is the solution. Job schedulers
(only one node should trigger a cron job), distributed
rate limiters (one node holds the counter), database
primary selection (one node accepts writes): all are
instances of the leader election pattern. The
implementations vary (ZooKeeper, etcd, Raft, Redis
SETNX) but the structure is always: atomic acquisition
of a shared resource with a time-bounded lease,
renewal to maintain the role, and epoch/fencing to
handle stale holders.

---

### 💡 The Surprising Truth

Kubernetes uses leader election for its own controllers
(controller-manager, scheduler) using a lock object
in the API server (a ConfigMap or Lease resource).
Crucially, Kubernetes uses a soft-expiration model:
after the TTL expires, a new leader can acquire
the lock, but the old leader is NOT immediately
killed. The old leader might be mid-operation. The
guarantee relies on the fact that Kubernetes
controllers are designed to be idempotent: running
the same control loop twice produces the same result.
This is a deliberate architectural choice to avoid
the complexity of hard fencing. The lesson: sometimes
the better solution to the double-leader problem is
not to prevent it, but to make operations idempotent
so that double execution is harmless.

---

### ✅ Mastery Checklist

1. [IMPLEMENT] Write a leader election using etcd's
   compare-and-swap with a 10-second lease and a
   renewal thread that renews every 4 seconds.
2. [EXPLAIN] Why does leader election alone NOT
   guarantee safety against a stale leader acting
   after replacement? What additional mechanism is
   required?
3. [TRACE] Walk through a ZooKeeper ephemeral node
   election with 3 nodes (create, watch, notification
   on deletion, re-election).
4. [DESIGN] A distributed cron job must run exactly
   once per minute across 5 nodes. Design the leader
   election mechanism that ensures this.
5. [DIAGNOSE] Kafka shows ActiveControllerCount=2.
   Describe the root cause and the steps to resolve it.
