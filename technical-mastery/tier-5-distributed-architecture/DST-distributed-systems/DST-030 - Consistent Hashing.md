---
id: DST-030
title: Consistent Hashing
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-013, DST-022
used_by: DST-038, DST-042
related: DST-013, DST-022, DST-027
tags:
  - distributed
  - partitioning
  - routing
  - scalability
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 30
permalink: /technical-mastery/distributed-systems/consistent-hashing/
---

⚡ TL;DR - Consistent hashing maps both keys and nodes
to positions on a virtual ring, so when a node is added
or removed, only the keys between that node and its
neighbor are remapped rather than all keys; this reduces
rebalancing cost from O(N) to O(K/n) and enables
efficient horizontal scaling of distributed caches
and databases.

---

### 📋 Entry Metadata

| #030 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Sharding / Horizontal Partitioning, Load Balancing | |
| **Used by:** | Distributed Cache, Gossip Protocol | |
| **Related:** | Sharding, Load Balancing, Read/Write Quorums | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A distributed cache has 4 nodes. Keys are assigned using
`hash(key) % 4`. A key hashes to 7; 7 % 4 = 3, so it
goes to node 3. When a 5th node is added, the formula
becomes `hash(key) % 5`. The key with hash 7 maps to
7 % 5 = 2, now node 2. But the data is still on node 3.
Every key must be moved. In a cache with 10 million
keys, adding one node invalidates nearly all entries
(statistically 80% of keys move). The cache hit rate
collapses to nearly zero. The database receives a sudden
10x traffic spike. This is a cache stampede triggered
by scaling.

**THE CORE INSIGHT:**
The modulo operator makes node assignment depend on the
total number of nodes. Changing node count invalidates
all assignments. Consistent hashing breaks this coupling:
by mapping both nodes and keys to a ring, only the
keys "owned" by the added/removed node need to move.
Everything else stays in place.

---

### 📘 Textbook Definition

**Consistent hashing** is a distributed hashing scheme
that maps keys and servers to positions on a virtual
ring (the "hash ring") using a hash function. Each key
is assigned to the first server clockwise from its
position on the ring (its "successor"). When a server
is added, it takes ownership of keys from its successor.
When a server is removed, its keys are transferred to
its successor.

**Key property:** When the number of servers changes
by 1, on average K/n keys need to be remapped, where
K is the total number of keys and n is the number of
servers. With modulo hashing, changing n by 1 remaps
nearly all K keys.

**Virtual nodes (vnodes):** Each physical server is
represented by multiple positions on the ring (virtual
nodes). This improves load distribution and allows
heterogeneous servers to hold proportionally more keys.

---

### ⏱️ Understand It in 30 Seconds

**The ring:**
```
             0
            ╱ ╲
      315  ╱   ╲  45
          │     │
    270 ──┤     ├── 90
          │     │
      225  ╲   ╱  135
            ╲ ╱
            180

Nodes:  A at 45°,  B at 135°,  C at 225°,  D at 315°
Keys:   hash(key) → position on ring
        Key ownership: walk clockwise to first node
```

**Adding a node:**
```
Before: A(45), B(135), C(225), D(315)
Add E at 90°:
  E takes ownership of keys between 45° and 90°
  These keys were owned by B (they were between A and B)
  Only keys in the 45°-90° arc move. B keeps the rest.
  ~1/5 of keys remapped (approximately K/n for n nodes)
```

---

### 🔩 First Principles Explanation

**THE RING CONSTRUCTION:**

1. Choose a hash function H with output range [0, 2^32)
   or [0, 2^64). This defines the ring size.
2. For each server s, compute H(s) (or H(s + "_1"),
   H(s + "_2"), ..., H(s + "_v") for v vnodes).
   Place the server at that position on the ring.
3. For each key k, compute H(k). Walk clockwise to
   find the first server. That server owns this key.

**WHY ONLY K/n KEYS MOVE:**

When server E is added at position p:
- E "cuts in" between two existing neighbors: its
  predecessor (server P, at position < p) and its
  successor (server S, at position > p)
- E takes ownership of keys in the arc from P to p
  (keys that clockwise resolve to E before they
  reach S)
- These keys were previously owned by S
- All other keys: unchanged (their clockwise
  resolution still reaches the same server)

```
Arc P→p contains approximately (p - P) / 2^32
fraction of all possible key hashes.

With n servers on the ring, each arc is ~1/n of the ring.
Adding one server: ~1/n of keys move.
  With 100 servers, 10M keys: ~100,000 keys move.
  With modulo hashing: ~9,900,000 keys move.
```

**THE VIRTUAL NODE PROBLEM:**

Without virtual nodes, servers land at arbitrary ring
positions. With only 4 servers, they may cluster:

```
A at 10°,  B at 12°,  C at 200°,  D at 205°

Arc A→B:  2° = 0.5% of keys (B gets almost nothing)
Arc B→C: 188° = 52% of keys (C gets overloaded)
Arc C→D:  5° = 1.4% of keys
Arc D→A: 165° = 45.8% of keys (A gets overloaded)
```

Load is wildly unbalanced. Virtual nodes solve this
by placing each server at multiple ring positions:

```
A at 10°,  90°, 170°, 250°
B at 12°,  92°, 172°, 252°
C at 200°, 280°, 360°, 80°
D at 205°, 285°, 365°, 85°

16 positions spread more evenly; load distribution
approaches 1/N per server as vnode count increases.
```

---

### 🧠 Mental Model / Analogy

> Imagine a circular table where 4 waiters stand at
> evenly spaced positions. Each waiter serves guests
> between their position and the next waiter clockwise.
> When a new waiter joins at a specific spot, they
> take over serving the guests between themselves and
> their clockwise neighbor. The other waiters' sections
> are unchanged. If a waiter leaves, their guests are
> absorbed by the clockwise neighbor. Total disruption
> is always proportional to the one waiter's section,
> not the entire table.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is:**
Consistent hashing is a way to distribute keys across
servers so that when you add or remove a server, only
the minimum necessary keys are moved. Instead of
`hash(key) % N`, you place both keys and servers on
a ring. Keys go to the nearest server clockwise.

**Level 2 - Where it is used:**
Distributed caches (Memcached, Redis Cluster), distributed
databases (DynamoDB, Cassandra), content delivery networks
(routing requests to cache nodes), load balancers (session
affinity), DHT-based peer-to-peer networks (BitTorrent,
Chord). Cassandra uses it for data distribution with
virtual nodes.

**Level 3 - The virtual node parameter:**
In Cassandra, `num_tokens` (default 256 in Cassandra 3.x)
controls virtual nodes per physical node. Higher vnode
count = better load distribution but higher metadata
overhead. Cassandra 4.0 introduced `allocate_tokens`
algorithm to place vnodes optimally for balanced
distribution.

**Level 4 - Weighted consistent hashing:**
Physical nodes may have different capacities. A server
with 2x memory should own 2x more keys. Virtual nodes
implement this: assign more vnodes to larger servers.
A server with 2x capacity gets 2x vnodes, owning ~2x
more of the ring. This generalizes consistent hashing
to heterogeneous clusters without changing the core
algorithm.

**Level 5 - Jump consistent hashing and alternatives:**
Karger et al.'s ring-based consistent hashing has O(log n)
lookup cost (binary search for the successor). Google's
"Jump Consistent Hash" (2014) achieves O(1) lookup cost
via a deterministic algorithm, but only supports adding
nodes at the end (no arbitrary placement). Rendezvous
hashing (highest random weight) is simple and excellent
but O(n) per lookup. The choice depends on the ratio
of reads to topology changes.

---

### ⚙️ Mechanism - Ring Implementation

```
Hash ring implementation:

Sorted list of (position, server) tuples.
For lookup: binary search for position ≥ hash(key).
If no such position: wrap around (ring property).

Add server: insert (H(server), server).
Remove server: delete all tuples for the server.
Lookup key: binary search, O(log(v × n)) where v=vnodes.

RING (sorted positions):
  [ (12, node-A), (78, node-A), (145, node-B),
    (201, node-C), (267, node-A), (312, node-B),
    (356, node-C) ]
  (each node appears 3 times = 3 vnodes each)

LOOKUP key with hash=100:
  Binary search for first position ≥ 100
  → position 145, node-B
  → key is assigned to node-B
```

---

### 💻 Code Example

**Wrong: Modulo Hashing**

```python
# BAD: modulo hashing - cache invalidated on scale events

class ModuloCache:
    def __init__(self, nodes: list[str]):
        self.nodes = nodes

    def get_node(self, key: str) -> str:
        # Adding one node: ~80% of keys map to new nodes
        # All those cache entries are invalidated
        return self.nodes[hash(key) % len(self.nodes)]

cache = ModuloCache(["node-1", "node-2", "node-3"])
cache.get_node("user:1001")  # → node-2

# Add node:
cache = ModuloCache(
    ["node-1", "node-2", "node-3", "node-4"]
)
cache.get_node("user:1001")  # May → node-1 (MOVED!)
# user:1001 cache entry invalidated. DB query required.
```

```python
# GOOD: consistent hashing - minimal key movement

import hashlib
import bisect

class ConsistentHashRing:
    def __init__(
        self,
        nodes: list[str],
        vnodes: int = 150
    ):
        self.vnodes = vnodes
        self.ring: dict[int, str] = {}
        self.sorted_keys: list[int] = []
        for node in nodes:
            self.add_node(node)

    def _hash(self, key: str) -> int:
        return int(
            hashlib.md5(key.encode()).hexdigest(), 16
        )

    def add_node(self, node: str) -> None:
        for i in range(self.vnodes):
            vnode_key = f"{node}#{i}"
            position = self._hash(vnode_key)
            self.ring[position] = node
            bisect.insort(self.sorted_keys, position)

    def remove_node(self, node: str) -> None:
        for i in range(self.vnodes):
            vnode_key = f"{node}#{i}"
            position = self._hash(vnode_key)
            del self.ring[position]
            self.sorted_keys.remove(position)

    def get_node(self, key: str) -> str:
        if not self.ring:
            raise ValueError("No nodes in ring")
        position = self._hash(key)
        # Find first ring position >= key position
        idx = bisect.bisect(self.sorted_keys, position)
        if idx == len(self.sorted_keys):
            idx = 0  # Wrap around the ring
        return self.ring[self.sorted_keys[idx]]

    def get_nodes(self, key: str, count: int) -> list[str]:
        """Get multiple distinct nodes for replication."""
        if not self.ring:
            return []
        position = self._hash(key)
        idx = bisect.bisect(self.sorted_keys, position)
        nodes = []
        seen = set()
        for i in range(len(self.sorted_keys)):
            ring_idx = (idx + i) % len(self.sorted_keys)
            node = self.ring[self.sorted_keys[ring_idx]]
            if node not in seen:
                nodes.append(node)
                seen.add(node)
                if len(nodes) == count:
                    break
        return nodes

# Usage:
ring = ConsistentHashRing(
    ["node-1", "node-2", "node-3"],
    vnodes=150
)
print(ring.get_node("user:1001"))  # → "node-2"

# Add node: only ~1/4 of keys remapped
ring.add_node("node-4")
print(ring.get_node("user:1001"))  # May still → "node-2"
# (1/4 chance of remapping; 3/4 chance: same node)

# Replication: get 3 distinct nodes for a key
replicas = ring.get_nodes("user:1001", count=3)
# ["node-2", "node-1", "node-4"]
```

---

### ⚖️ Comparison Table

| Hashing Method | Keys Moved on +1 Node | Load Balancing | Lookup Cost | Best For |
|---|---|---|---|---|
| **Modulo (hash % N)** | ~(N-1)/N of all keys | Perfect (uniform hash) | O(1) | Fixed cluster size |
| **Consistent Hash (ring)** | ~K/N keys | Good (with vnodes) | O(log N) | Dynamic scale |
| **Rendezvous Hashing** | ~K/N keys | Very good | O(N) | Small clusters |
| **Jump Consistent Hash** | ~K/N keys | Perfect | O(1) | Append-only scaling |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Consistent hashing means no keys move when scaling" | Keys always move; consistent hashing minimizes the movement to K/N. Some movement is unavoidable. |
| "Virtual nodes solve all load imbalance" | Virtual nodes reduce variance but do not guarantee perfect balance, especially with few nodes or skewed key distributions (hotspot keys). |
| "Consistent hashing is the same as rendezvous hashing" | Different algorithms with the same asymptotic remapping property. Rendezvous is simpler, O(N) lookup. Ring consistent hashing is O(log N). |
| "Adding more virtual nodes always improves performance" | Very high vnode counts (>1000/node) increase metadata overhead (memory, gossip protocol messages). 150-256 vnodes per node is the typical sweet spot. |

---

### 🚨 Failure Modes & Diagnosis

**Hotspot After Node Removal**

**Symptom:** After a node fails, one server CPU spikes
to 100%. Cache hit rate drops to 40%. Database load
3x normal.

**Root Cause:** The failed node's keys all moved to
its clockwise neighbor (the successor on the ring).
With 3 nodes, the successor now owns 2x as many keys.
Without vnodes, this can be even worse - the successor
might absorb all the failed node's keys.

**Diagnosis:**
```bash
# Cassandra: check token distribution after node removal
nodetool ring
# Look for: uneven arc sizes (one node owns 50%+)
# Ideal: each node owns ~1/N of ring

# After re-adding node or fixing vnodes:
nodetool status
# Check: Load column. Significant imbalance = hotspot.
```

**Fix:** Virtual nodes distribute the removed node's
key range across multiple successors (one per vnode).
With 150 vnodes, the removed node's key range is split
among many remaining nodes proportionally.

```python
# Verify vnode distribution in custom ring:
from collections import Counter

ring = ConsistentHashRing(
    ["node-1", "node-2", "node-3"],
    vnodes=150
)
# Sample 10,000 random keys and check distribution:
import random, string
distribution = Counter()
for _ in range(10_000):
    key = ''.join(
        random.choices(string.ascii_lowercase, k=10)
    )
    distribution[ring.get_node(key)] += 1

for node, count in sorted(distribution.items()):
    print(f"{node}: {count} keys "
          f"({count/100:.1f}% of sample)")
# Target: each node ~33.3% ± 2% with 150 vnodes
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `Sharding / Horizontal Partitioning` (DST-013)
- `Load Balancing` (DST-022)

**Builds On This:**
- `Distributed Cache` (DST-038)
- `Gossip Protocol` (DST-037)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ PROBLEM    │ hash(key)%N: adding a node remaps all keys │
│ SOLUTION   │ Ring: keys and nodes share the same space  │
│            │ Adding a node: only K/N keys remapped      │
├────────────┼────────────────────────────────────────────┤
│ VNODES     │ Each server appears at multiple ring slots │
│            │ Balances load; 150-256 vnodes typical      │
├────────────┼────────────────────────────────────────────┤
│ LOOKUP     │ hash(key) → clockwise to first node        │
│ COST       │ O(log N) with binary search on sorted ring │
├────────────┼────────────────────────────────────────────┤
│ USED IN    │ Cassandra, DynamoDB, Redis Cluster,        │
│            │ Memcached, Chord DHT                       │
├────────────┼────────────────────────────────────────────┤
│ ONE-LINER  │ "Add a node: only the new node's neighbors │
│            │  lose some keys. Everyone else is stable." │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

Consistent hashing solves a generalized version of
a ubiquitous problem: how to route requests or data
in a distributed system where the set of destinations
changes dynamically. The ring technique applies wherever
you need stable assignment under membership changes:
distributed caches, sharding, request routing, peer-to-peer
networks. The core insight transfers directly: use a
total order (the ring) that is stable under local
changes (add/remove one node affects only that node's
neighborhood). This is the same principle that makes
binary search trees efficient for inserts and deletes
compared to sorted arrays.

---

### 💡 The Surprising Truth

Consistent hashing was invented by Karger et al. in 1997
for CDN routing - not for databases. The original paper
described the problem of routing HTTP requests to cache
servers in Akamai's early CDN architecture. The insight
was that cache nodes are ephemeral (they fail, are
replaced, scale up and down), and using modulo hashing
caused catastrophic cache stampedes on every topology
change. The algorithm was published in a 1997 STOC paper
("Consistent Hashing and Random Trees") and Amazon
independently rediscovered and extended it for DynamoDB
in 2007, with virtual nodes added for load balancing.
It is now the standard routing algorithm for essentially
every distributed storage system. The entire field owes
its horizontal scaling property to an algorithm that
was originally designed for web caching.

---

### ✅ Mastery Checklist

1. [IMPLEMENT] Write a consistent hash ring with virtual
   nodes and verify that adding one node moves
   approximately 1/(N+1) of keys.
2. [CALCULATE] With N=5 nodes, 10M keys, and 150 vnodes
   per node, estimate how many keys move when a 6th
   node is added.
3. [COMPARE] Implement both modulo hashing and consistent
   hashing. Run a benchmark showing cache hit rate before
   and after adding a node for each approach.
4. [DESIGN] Specify the vnode count for a Cassandra cluster
   with 3 nodes of different sizes (1x, 2x, 4x memory)
   to achieve proportional data distribution.
5. [DEBUG] After a node removal, one node shows 3x higher
   CPU usage than peers. Diagnose whether the root cause
   is insufficient vnodes or a hotspot key, and fix each.
