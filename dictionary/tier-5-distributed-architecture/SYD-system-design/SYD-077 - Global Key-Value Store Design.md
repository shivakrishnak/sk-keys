---
id: SYD-077
title: Global Key-Value Store Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-010, SYD-033, SYD-052
used_by: ""
related: SYD-010, SYD-033, SYD-052, SYD-042, SYD-019
tags:
  - architecture
  - distributed
  - key-value
  - design
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 77
permalink: /syd/global-key-value-store-design/
---

# SYD-077 - Global Key-Value Store Design

⚡ TL;DR - Design a globally distributed key-value
store like Amazon DynamoDB, Apache Cassandra, or
Google Bigtable. Core decisions: (1) Data partitioning -
consistent hashing distributes keys across nodes;
(2) Replication - each key is replicated to N nodes
(typically 3); (3) Consistency model - EVENTUAL
(accept stale reads, high availability) vs. STRONG
(linearizable reads, lower availability); (4) Conflict
resolution - last-write-wins (timestamp) or vector
clocks for multi-leader; (5) Fault tolerance - gossip
protocol for node failure detection, sloppy quorum
for availability during failures. This is the Amazon
Dynamo paper (2007) made concrete.

| #077 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Consistent Hashing, Database Internals, Distributed Cache Design | |
| **Related:** | Consistent Hashing, Database Internals, Distributed Cache Design, Data Partitioning Strategies, Database Replication (System) | |

---

### 🔥 The Problem This Solves

Amazon needs a key-value store for shopping cart data:
100 million users, each with a cart that must be read
and written on every page load. Requirements: (1) always
writable (adding to cart must never fail, even during
network partitions); (2) global availability (US, EU,
Asia all serve locally with low latency); (3) horizontal
scale (add nodes = add capacity); (4) no single point
of failure. SQL databases with a single primary cannot
meet all four. Dynamo was built to solve this: sacrifice
strong consistency for always-writable availability
(the "AP" choice in CAP theorem).

---

### 📘 Textbook Definition

**Key-value store:** A database that stores data as
key-value pairs. Lookup: O(1) by key. No query by
value or range queries (in basic implementations).
Values are opaque bytes.

**Consistent hashing:** A technique to distribute keys
across nodes such that adding or removing a node
requires only O(K/N) key remappings (K=keys, N=nodes),
not O(K) remappings as in mod-N hashing.

**Replication factor (N):** Number of nodes that hold
a copy of each key. N=3 is typical: a key is on nodes
A, B, and C. Any node failure: two others still serve reads.

**Quorum:** Minimum nodes that must agree for an
operation to succeed. For W (write) and R (read):
if W + R > N → strong consistency. Typical:
N=3, W=2, R=2 → W+R=4 > 3 → strong consistency.
N=3, W=1, R=1 → W+R=2 ≤ 3 → eventual consistency.

**Gossip protocol:** Nodes exchange state with random
peers periodically. Information propagates exponentially
(like a rumor). Failure detection: a node that doesn't
respond to gossip is marked down. Scales to thousands
of nodes without centralized coordination.

**Vector clock:** A data structure tracking causality
between events: a vector of (node, counter) pairs.
Used to detect concurrent writes and determine which
version is "newer."

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Consistent hashing partitions keys across nodes.
Replication factor N. Quorum reads/writes.
Gossip detects failures. Eventual consistency for
maximum availability.

**One analogy:**
> A distributed post office system:
>
> Without consistent hashing: one post office handles
> all mail. It fails → no mail.
>
> With consistent hashing: mail is routed to post
> offices by first letter (A-F → office 1, G-M → 2...).
> Each piece of mail is held in 3 offices (replication).
> If office 1 is closed: offices 7 and 8 (replicas)
> still have the mail.
>
> Quorum: two out of three offices must agree that the
> mail has been "delivered" before confirming. Otherwise:
> if one office incorrectly records delivery, you still
> have two correct confirmations overriding it.

**One insight:**
The key insight of the Amazon Dynamo paper: "always
writeable" is more important than "always consistent"
for a shopping cart. A user adding to their cart with
a slight inconsistency is manageable (the cart might
show an outdated count briefly). A user unable to
add to their cart because the system is in a network
partition is a lost sale. The design choice is explicit:
favor availability over consistency for this workload.
Not all data has this property: bank balances require
strong consistency. The KV store design requires knowing
which end of the consistency-availability spectrum
your use case requires.

---

### 🔩 First Principles Explanation

**CONSISTENT HASHING:**
```
Problem with mod-N hashing:
  4 nodes. Key "cart:123" → hash(key) % 4 = 2 → node 2.
  Add a 5th node: hash(key) % 5 = 3 → node 3. DIFFERENT!
  Must move all keys: O(N × K) rehashing. Unavailable
  during migration.

Consistent hashing:
  Hash space: 0 to 2^32 (a ring).
  Nodes placed on ring by hash(node_id):
  Node A: 100, Node B: 300, Node C: 600.
  
  Key "cart:123": hash("cart:123") = 250.
  250 → clockwise to Node B (300). B stores this key.
  
  Add Node D at position 450:
  Keys between 300 and 450 that were on C: → D.
  Only keys in [300,450] are remapped. All others: unchanged.
  
  Virtual nodes (vnodes):
  Each physical node has 100-200 virtual positions.
  Ensures more uniform key distribution.
  Node A has positions [100, 512, 830, 1200, ...].
  Node B has positions [200, 450, 700, 1500, ...].
  Adding a node: vnodes spread evenly. Better balance.

Replication:
  Key "cart:123" maps to Node B (position 300).
  Replicate to next N-1 clockwise nodes: C and A.
  Replication factor: N=3.
  B is coordinator (primary). A and C are replicas.
```

**QUORUM READS AND WRITES:**
```
N=3 (3 replicas per key).
W=2 (write to 2 nodes minimum before acknowledging).
R=2 (read from 2 nodes, return latest).

Write:
  Client → Coordinator (Node B).
  Coordinator: send write to B, C, A.
  Wait for W=2 acknowledgments (any 2 of 3).
  Return success to client when 2 have confirmed.
  Third replica: will eventually get the write (async).

Read:
  Client → Coordinator.
  Coordinator: read from B, C, A (or a subset).
  Wait for R=2 responses.
  Return the value with the highest version (timestamp).

Consistency:
  W + R > N → strong consistency.
  W=2, R=2: 2+2=4 > 3. Any read sees the latest write
  because at least 1 node that was in the write quorum
  is always in the read quorum.

Eventual consistency (W=1, R=1):
  W+R = 2 ≤ 3. Read may miss the latest write
  (reads node that hasn't received the write yet).
  Trade-off: lower latency (return after 1st response),
  higher availability (write succeeds with just 1 replica).

Sloppy quorum (hinted handoff):
  Node B is down. Coordinator must write W=2.
  Can it write to A and C only? Yes (sloppy quorum).
  The write is "hinted": stored temporarily on A with
  a hint that it belongs to B. When B recovers,
  A forwards the hinted write to B. Maximizes availability.
```

**CONFLICT RESOLUTION:**
```
Two concurrent writes to key "cart:user:123":
  Client 1 (US): cart = [item:A, item:B]  at t=1000
  Client 2 (EU): cart = [item:A, item:C]  at t=1001

Simple last-write-wins (LWW):
  Compare timestamps. t=1001 > t=1000.
  EU version wins. Cart = [item:A, item:C].
  Item B is LOST. Data loss.
  
  Issue: wall clocks are not perfectly synchronized.
  NTP drift: a write at t=1001 may have been CAUSALLY
  before t=1000. LWW can lose writes.

Vector clocks:
  Each version of a key has a vector clock:
  Version 1: {(A, 1)}  (written by node A, counter 1)
  Version 2: {(B, 1)}  (written by node B, counter 1)
  
  If Version 1 happened before Version 2:
  Vector 1 would be {(A, 1)} and Version 2 = {(A, 1), (B, 1)}.
  The causal order is clear: apply both in order.
  
  If concurrent (neither happened before the other):
  No causal relationship. CONFLICT.
  Options: 
    - Return both versions to the client for resolution.
    - Application merges (union of cart items).
    - Last-write-wins (accepting possible data loss).
  
  Amazon Dynamo's shopping cart: merge both versions
  (union of items). Result: [item:A, item:B, item:C].
  Client sees merged cart. Better than data loss.
```

**FAILURE DETECTION (GOSSIP):**
```
N=100 nodes.
Centralized monitoring: 100 nodes pinging one monitor.
Monitor becomes bottleneck / single point of failure.

Gossip protocol:
  Every 1 second: each node sends heartbeat to
  K=3 random other nodes.
  Heartbeat: "I'm alive. I've heard A is alive,
             B is alive, C is down."
  
  If a node doesn't send heartbeats for T=10 seconds:
  Marked as "suspected." After T=30s: "down."
  
  Convergence: with N=100 nodes, K=3, information
  propagates to all nodes in O(log N) = ~7 rounds.
  Each round = 1 second. Failure detected globally
  in ~7 seconds.
  
  Scale: gossip scales to thousands of nodes.
  No centralized coordinator needed.
  Each node has an eventually-consistent view of
  which other nodes are alive.
```

---

### 🧪 Thought Experiment

**CAP Trade-off: DynamoDB vs. Spanner**

DynamoDB (AP):
  Strong consistency: optional (disabled by default).
  Default: eventually consistent reads.
  Availability: multi-region, always accepts writes.
  Use: session data, user preferences, shopping cart.
  CAP choice: AP during network partition.

Google Spanner (CP):
  Strong consistency: always. Linearizable globally.
  Uses TrueTime API (atomic clocks + GPS = bounded clock
  uncertainty of 7ms globally).
  Availability: lower than DynamoDB in partitions.
  Use: financial transactions, inventory levels.
  CAP choice: CP during network partition.

Interview framing:
  "Should this be AP or CP?" is always the first question.
  AP: user preferences, cart, session, feed, notifications.
  CP: payment, balance, inventory count, booking.
  
  Most data in a typical application is AP-appropriate.
  Payment data is CP-required.
  Design the KV store for the workload, not generically.

---

### 🧠 Mental Model / Analogy

> Global KV store is like a distributed hotel chain:
>
> Consistent hashing: reservations routed to the hotel
> responsible for that booking number range.
>
> Replication: same reservation recorded at 3 hotels
> (primary + 2 backups). If one hotel burns down:
> reservation exists at two others.
>
> Quorum: a reservation only confirmed when 2 of 3
> hotels have recorded it. If only 1 has it:
> not confirmed (not enough consensus).
>
> Gossip: hotels call each other daily: "Are you open?
> Hotel X hasn't called in 3 days." News spreads via
> gossip, not a central registry.
>
> Vector clocks: each hotel records who made the last
> update. If two hotels got conflicting updates:
> they show both to the customer to resolve.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A global key-value store stores data (like a dictionary)
across many servers worldwide. When you look up a key,
you get the value from the nearest server. Data is
copied to multiple servers for safety. If one server
fails, others still have the data.

**Level 2 - How to use it (junior developer):**
DynamoDB, Cassandra, or Redis Cluster. Choose a good
partition key (high cardinality, even distribution).
Understand eventual consistency: reads may return
stale data by a few milliseconds. For strongly
consistent reads: use DynamoDB's ConsistentRead=true
(higher cost). Set TTL on items with expiry requirements.

**Level 3 - How it works (mid-level engineer):**
Consistent hashing: keys distributed by hash of key,
clockwise to next node on ring. N=3 replicas per key
(coordinator + 2 neighbors). Write quorum W=2, read
quorum R=2: W+R=4 > N=3 = strong consistency.
W=1, R=1: eventual. Gossip: failure detection via
periodic heartbeats. Sloppy quorum + hinted handoff:
writes still succeed when coordinator is down.

**Level 4 - Why it was designed this way (senior/staff):**
The Dynamo paper (DeCandia et al., 2007) was a
foundational paper in distributed systems because it
explicitly articulated the CAP trade-off as a product
decision, not just a technical constraint. Amazon's
insight: for shopping cart data, an incorrect read
(showing stale cart) is less bad than an unavailable
write (cannot add to cart). This is a business decision
that led to the technical design of "always-writable"
with eventual consistency as default. The paper also
introduced sloppy quorum and hinted handoff as practical
alternatives to strict quorum under partition: if the
nodes in the replication preference list are unavailable,
temporarily write to ANY available node with a "hint"
to pass the write along when the intended node recovers.

**Level 5 - Mastery (distinguished engineer):**
DynamoDB's evolution from the original Dynamo design
(2007) illustrates the operational complexity of
large-scale KV stores. The original Dynamo required
manual partition management and was operationally
complex. DynamoDB (2012) abstracted away partition
management entirely: the system automatically manages
partition splits and rebalancing based on throughput
metrics, invisible to users. DynamoDB's 2022 paper
("Amazon DynamoDB: A Scalable, Predictably Performant,
and Fully Managed NoSQL Database Service") describes
how they achieved single-digit millisecond p99 latency
at petabyte scale by: (1) separating the request router
(stateless, horizontally scalable) from the storage node
(stateful, consistent hashing); (2) moving to a log-
structured storage engine (replacing B-tree) for more
predictable write performance; (3) using disaggregated
storage (AWS S3 for durability) from compute nodes
(eliminating the durability cost of in-node replication).

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ GLOBAL KV STORE ARCHITECTURE                       │
│                                                      │
│ Consistent hash ring:                              │
│   [Node A: 100] [Node B: 300] [Node C: 600]      │
│   [Node D: 800] ← clockwise wrap                 │
│                                                      │
│ Write: SET cart:user:123 = {...}                   │
│   hash(key) = 250 → Node B (coordinator)          │
│   Node B → write to B, C, A (N=3 replicas)       │
│   Wait for W=2 ACKs                              │
│   Return success                                  │
│                                                      │
│ Read: GET cart:user:123                            │
│   hash(key) = 250 → Node B (coordinator)          │
│   Node B → read from B, C (R=2 nodes)           │
│   Compare version timestamps                      │
│   Return latest                                   │
│                                                      │
│ Node B is down:                                    │
│   Sloppy quorum: write to C, D instead           │
│   Hinted handoff: D stores with hint "for B"    │
│   Node B recovers: D forwards hinted write      │
│                                                      │
│ Failure detection:                                 │
│   Each node: gossip to 3 random nodes every 1s  │
│   No heartbeat for 10s: suspect                 │
│   No heartbeat for 30s: down                    │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Consistent hashing implementation (Python)**
```python
import hashlib
import bisect
from typing import List, Optional

class ConsistentHashRing:
    """
    Consistent hashing ring with virtual nodes.
    Distributes keys across nodes with minimal remapping
    when nodes are added/removed.
    """
    
    def __init__(self, virtual_nodes: int = 150):
        self.virtual_nodes = virtual_nodes
        self.ring: list = []      # sorted hash values
        self.hash_to_node: dict = {}  # hash → node_id
    
    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(),
                   16)
    
    def add_node(self, node_id: str):
        """Add a node with virtual_nodes positions."""
        for i in range(self.virtual_nodes):
            vnode_key = f"{node_id}:vnode:{i}"
            h = self._hash(vnode_key)
            bisect.insort(self.ring, h)
            self.hash_to_node[h] = node_id
    
    def remove_node(self, node_id: str):
        """Remove a node and all its virtual nodes."""
        for i in range(self.virtual_nodes):
            vnode_key = f"{node_id}:vnode:{i}"
            h = self._hash(vnode_key)
            if h in self.hash_to_node:
                self.ring.remove(h)
                del self.hash_to_node[h]
    
    def get_node(self, key: str) -> Optional[str]:
        """Get the node responsible for a key."""
        if not self.ring:
            return None
        h = self._hash(key)
        # Find first ring position >= key hash
        idx = bisect.bisect_left(self.ring, h)
        # Wrap around (ring is circular)
        if idx == len(self.ring):
            idx = 0
        return self.hash_to_node[self.ring[idx]]
    
    def get_replication_nodes(self,
                               key: str,
                               n: int = 3) -> List[str]:
        """Get N nodes for key (for replication)."""
        if not self.ring:
            return []
        h = self._hash(key)
        idx = bisect.bisect_left(self.ring, h)
        nodes = []
        seen = set()
        
        for i in range(len(self.ring)):
            pos = (idx + i) % len(self.ring)
            node = self.hash_to_node[self.ring[pos]]
            if node not in seen:
                nodes.append(node)
                seen.add(node)
                if len(nodes) == n:
                    break
        
        return nodes

# Usage:
ring = ConsistentHashRing(virtual_nodes=150)
ring.add_node("node-1")
ring.add_node("node-2")
ring.add_node("node-3")

key = "cart:user:12345"
nodes = ring.get_replication_nodes(key, n=3)
print(f"Key '{key}' → nodes: {nodes}")
# Key 'cart:user:12345' → nodes: ['node-2', 'node-3', 'node-1']

# Add a node: minimal remapping
ring.add_node("node-4")
new_nodes = ring.get_replication_nodes(key, n=3)
# Some keys remapped from node-3 to node-4; most unchanged.
```

**Example 2 - Quorum-based write (pseudo-code)**
```python
import asyncio
from typing import List, Tuple

class KVNode:
    """Simplified KV node for a single partition."""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.store = {}
        self.versions = {}
    
    async def put(self, key: str, value: bytes,
                  version: int) -> bool:
        """Write a key-value pair with version."""
        current = self.versions.get(key, 0)
        if version > current:
            self.store[key] = value
            self.versions[key] = version
        return True
    
    async def get(self, key: str) -> Tuple[bytes, int]:
        """Read a key, returning (value, version)."""
        value = self.store.get(key, b"")
        version = self.versions.get(key, 0)
        return value, version

class KVCoordinator:
    """Coordinator for quorum-based operations."""
    
    N = 3  # Replication factor
    W = 2  # Write quorum
    R = 2  # Read quorum
    
    def __init__(self, nodes: List[KVNode]):
        self.nodes = nodes
    
    async def put(self, key: str, value: bytes) -> bool:
        """Write with quorum. Return True if successful."""
        import time
        version = int(time.time() * 1000)  # Millisecond timestamp
        
        # Send write to all N nodes concurrently
        tasks = [node.put(key, value, version)
                 for node in self.nodes]
        results = await asyncio.gather(*tasks,
                                        return_exceptions=True)
        
        # Count successful writes
        successes = sum(1 for r in results
                       if r is True)
        
        if successes >= self.W:
            return True  # Write quorum achieved
        
        # W not met: write failed (or partially applied)
        # In production: rollback applied writes or
        # wait for repair via anti-entropy.
        return False
    
    async def get(self, key: str) -> bytes:
        """Read with quorum. Return most recent value."""
        tasks = [node.get(key) for node in self.nodes]
        results = await asyncio.gather(*tasks,
                                        return_exceptions=True)
        
        # Filter out errors
        valid = [(val, ver) for val, ver in results
                 if not isinstance(val, Exception)]
        
        if len(valid) < self.R:
            raise Exception("Read quorum not met")
        
        # Read repair: find the most recent version
        latest = max(valid, key=lambda x: x[1])
        value, version = latest
        
        # Read repair: if some nodes have older versions,
        # update them with the latest value (async)
        for node in self.nodes:
            node_val, node_ver = await node.get(key)
            if node_ver < version:
                asyncio.create_task(
                    node.put(key, value, version))
        
        return value
```

---

### ⚖️ Comparison Table

| Database | Consistency | Availability | Partition Tolerance | Use Case |
|---|---|---|---|---|
| **DynamoDB** | Eventual (default) / Strong (option) | Very high | Yes | Session, cart, user prefs |
| **Cassandra** | Eventual (tunable quorum) | Very high | Yes | IoT, time series, analytics |
| **Redis Cluster** | Strong (single shard) | High | Limited | Cache, leaderboard, session |
| **Google Spanner** | Strong (linearizable) | High | Yes | Financial, inventory |
| **Apache ZooKeeper** | Strong | Medium | Yes | Config, coordination |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Consistent hashing is about data consistency | "Consistent" in consistent hashing refers to the consistent behavior when nodes are added or removed: only O(K/N) keys are remapped, not O(K). It has nothing to do with the CAP-theorem consistency (linearizability). A system using consistent hashing for partitioning can still be eventually consistent. The terms are confusingly similar but mean different things. |
| Quorum guarantees strong consistency | Quorum only guarantees strong consistency if W + R > N AND there are no failures causing sloppy quorum. During a network partition or node failure, sloppy quorum may accept writes from non-preferred nodes. A read quorum of R nodes may not include any of the nodes that received the sloppy write. Strong consistency requires either: (a) no sloppy quorum, or (b) read repair to detect and fix inconsistencies. |
| Adding more nodes improves read/write latency | Adding nodes improves throughput (more requests handled in parallel) but may not improve per-request latency. Quorum requires W or R responses from different nodes; with more nodes, the coordinator must still wait for the required quorum count. Network latency between nodes is the binding constraint for quorum latency, not the number of nodes. |

---

### 🚨 Failure Modes & Diagnosis

**Hot Partition: One Node Overwhelmed**

**Symptom:**
Cluster monitoring: one node at 95% CPU, others at 10%.
Latency for certain keys: 500ms+. Other keys: < 5ms.
Node restart temporarily fixes it; problem recurs.

**Root Cause:**
Poor partition key choice: most writes go to the same
key (and thus the same node). Example: all events for
a popular user (celebrity's social feed) map to the same
node. Consistent hashing distributes keys by hash, but
if one key has 1,000,000× more traffic than others,
no amount of partitioning helps - it still goes to one node.

**Diagnosis:**
```
# AWS DynamoDB: check CloudWatch metrics
# ConsumedWriteCapacityUnits per partition key value
# Look for single partition key consuming 90%+ of capacity

# Cassandra: nodetool tpstats (thread pool stats)
# Large number of dropped messages: overloaded node

# Redis: monitor command (1-second sampling)
# redis-cli monitor | grep "your_hot_key"
```

**Fix:**
```python
# Strategy 1: Key sharding (add random suffix)
# Spread hot key across N shards

import random

def put_hot_key(user_id: int, value: bytes, shards: int = 8):
    """
    Shard a hot key across multiple partitions.
    Writes: random shard. Reads: check all shards.
    """
    shard = random.randint(0, shards - 1)
    key = f"user:{user_id}:shard:{shard}"
    kv_store.put(key, value)

def get_hot_key(user_id: int, shards: int = 8):
    """Read all shards, return latest by timestamp."""
    keys = [f"user:{user_id}:shard:{i}"
            for i in range(shards)]
    results = [kv_store.get(k) for k in keys]
    # Return the non-empty result with latest version
    valid = [(v, ver) for v, ver in results if v]
    if not valid:
        return None
    return max(valid, key=lambda x: x[1])[0]

# Strategy 2: Caching at a higher level
# Redis/CDN cache: absorb the read traffic.
# KV store: only see cache misses and write-throughs.
# Read-to-write ratio: 1000:1 → CDN absorbs 999/1000.
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Consistent Hashing` - the fundamental data
  partitioning algorithm for distributed KV stores
- `Database Internals` - understanding LSM trees,
  WAL, and storage engines used in KV stores
- `Distributed Cache Design` - Redis as a KV store;
  simpler but related architecture

**Builds On This (learn these next):**
- `Data Partitioning Strategies` - advanced sharding
  patterns beyond consistent hashing
- `Database Replication (System)` - replication
  strategies: synchronous, asynchronous, multi-leader

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ HASHING     │ Consistent hashing: O(K/N) remapping.    │
│             │ Vnodes for even distribution.            │
├─────────────┼──────────────────────────────────────────  │
│ REPLICATION │ N=3 (coordinator + 2 neighbors on ring). │
│             │ W=2, R=2: W+R>N = strong consistency.   │
│             │ W=1, R=1: eventual, higher availability. │
├─────────────┼──────────────────────────────────────────  │
│ QUORUM      │ W+R > N: at least 1 overlap guaranteed. │
│             │ Sloppy quorum: any node for availability.│
├─────────────┼──────────────────────────────────────────  │
│ GOSSIP      │ Each node → 3 random peers every 1s.    │
│             │ Failure: O(log N) rounds to propagate.  │
├─────────────┼──────────────────────────────────────────  │
│ CONFLICTS   │ LWW: simple, may lose data.             │
│             │ Vector clocks: detect concurrent writes. │
│             │ App merge: union for shopping cart.     │
├─────────────┼──────────────────────────────────────────  │
│ CAP         │ AP (Dynamo): always write, stale reads.  │
│             │ CP (Spanner): strong consistency.       │
├─────────────┼──────────────────────────────────────────  │
│ ONE-LINER   │ "Consistent hashing + N replicas +     │
│             │  quorum + gossip + sloppy quorum."     │
├─────────────┼──────────────────────────────────────────  │
│ NEXT        │ System Design Interview Framework        │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Consistent hashing: place nodes on a ring (hash space).
   A key maps to the first node clockwise from its hash.
   Replication: copy to next N-1 nodes clockwise.
   When a node is added/removed: only adjacent keys remapped.
   Virtual nodes ensure even distribution.
2. Quorum: W writes + R reads. If W + R > N: strong
   consistency (every read sees the latest write).
   Dynamo default (W=1, R=1): eventual consistency,
   maximum availability. Strong: W=2, R=2 with N=3.
3. Sloppy quorum + hinted handoff: if the intended replica
   nodes are unavailable, write to any available nodes
   (with a "hint" to forward to the intended node when
   it recovers). This makes writes nearly always succeed,
   at the cost of temporary inconsistency.

**Interview one-liner:**
"Global KV store (Dynamo-style): consistent hashing with virtual nodes distributes
keys; each key replicated to N=3 nodes (clockwise neighbors on ring). Quorum:
W+R>N for strong consistency (W=2, R=2, N=3); W=1, R=1 for eventual. Sloppy
quorum: write to any available node when intended replicas are down; hinted handoff
forwards write when target recovers. Gossip protocol: O(log N) failure detection
without centralized coordinator. Conflict resolution: LWW (risk data loss) or
vector clocks (detect concurrent, merge application-side). CAP: Dynamo is AP;
Spanner is CP. Hot partition: key sharding with random suffix."
