---
id: DST-067
title: "Amazon Dynamo Paper - 2007"
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-011, DST-017, DST-018, DST-019
used_by: []
related: DST-011, DST-012, DST-017, DST-018, DST-019, DST-029, DST-032
tags:
  - distributed
  - dynamo
  - amazon
  - consistent-hashing
  - vector-clocks
  - gossip
  - eventual-consistency
  - paper
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 67
permalink: /technical-mastery/distributed-systems/amazon-dynamo-paper/
---

⚡ TL;DR - The Amazon Dynamo paper (2007) described
how Amazon built an always-available key-value store
using: consistent hashing with virtual nodes for
partitioning, vector clocks for conflict detection,
gossip-based failure detection and membership,
anti-entropy with Merkle trees for replica sync,
sloppy quorum with hinted handoff for availability,
and tunable consistency (W+R>N for strong, W+R<=N
for eventual); it codified practical availability-
over-consistency design and inspired Cassandra, Riak,
and DynamoDB.

---

### 📋 Entry Metadata

| #067 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Consistent Hashing, Vector Clocks, Quorum, Gossip Protocol | |
| **Used by:** | N/A (foundational paper; influenced Cassandra, Riak) | |
| **Related:** | Consistent Hashing, Vector Clocks, Sloppy Quorum, Merkle Trees, Anti-Entropy | |

---

### 🔥 The Problem This Solves

**THE CONTEXT (2007):**
Amazon's shopping cart and catalog services needed
to be always available. A user must always be able
to add items to their cart, view product listings,
and complete purchases, even if a datacenter fails,
a network partition occurs, or a storage node crashes.

**THE STANDARD APPROACH FAILED:**
Traditional relational databases (MySQL with
replication) required:
- A primary node for writes (single point of failure)
- Manual sharding (operational complexity)
- Strong consistency (which requires coordination
  and can block under partition)

**THE INSIGHT:**
For shopping carts: "eventual consistency" is fine.
A user adding an item to their cart that briefly
shows up twice is a trivially solved problem (merge).
A user who CANNOT add to their cart is a lost sale.
The right trade-off: always accept writes, detect
conflicts later, resolve conflicts at read time.

Dynamo chose availability over consistency,
and built a system that made this choice operational.

---

### 📘 Textbook Definition

**Amazon Dynamo** (DeCandia et al., 2007, "Dynamo:
Amazon's Highly Available Key-Value Store", SOSP 2007):
a key-value store designed for high availability at
the cost of strong consistency. It introduced the
practical combination of:
- Consistent hashing with virtual nodes (partitioning)
- Vector clocks (causality tracking for conflict detection)
- Gossip protocol (failure detection and membership)
- Anti-entropy (background replica synchronization)
- Sloppy quorum + hinted handoff (availability)

**Not the same as Amazon DynamoDB:** DynamoDB is a
commercial database service inspired by Dynamo but
not the same system. Dynamo was an internal service
that is no longer the underlying technology.

---

### ⏱️ Understand It in 30 Seconds

```
DYNAMO'S SIX CORE TECHNIQUES:

1. CONSISTENT HASHING + VIRTUAL NODES:
   Hash key → position on ring.
   Each node owns multiple virtual positions (150/node).
   Balanced load distribution; easy node add/remove.

2. VECTOR CLOCKS:
   [A:1, B:2] causally before [A:2, B:2].
   [A:2, B:1] and [A:1, B:2] are CONCURRENT.
   Concurrent versions = conflict; caller resolves.

3. GOSSIP PROTOCOL:
   Each node periodically sends its membership view
   to a random neighbor. Failure detection via
   timeout on expected gossip messages.
   O(log N) propagation time.

4. ANTI-ENTROPY (MERKLE TREES):
   Each node builds a Merkle tree over its key range.
   Compare roots with neighbors: same root = in sync.
   Diff the tree: find which key ranges differ.
   Sync only the divergent ranges.

5. SLOPPY QUORUM + HINTED HANDOFF:
   Normal quorum: write to N=3 nodes in the ring.
   If a preferred node is down: write to NEXT live node
   (sloppy quorum). Add hint: "when node X recovers,
   give it this write." When X recovers: hint applied.

6. TUNABLE CONSISTENCY:
   N = total replicas (default 3)
   R = read quorum (how many must respond to read)
   W = write quorum (how many must respond to write)
   W+R > N → strong consistency (overlapping sets).
   W+R <= N → eventual consistency (faster).
   Amazon default: N=3, W=1, R=1 (max availability).
```

---

### 🔩 First Principles Explanation

**TECHNIQUE 1: CONSISTENT HASHING WITH VIRTUAL NODES:**

```
PROBLEM: Simple modulo hashing.
  node = hash(key) % N
  Adding a node: rehash ALL keys. Mass migration.
  
CONSISTENT HASHING:
  Hash space = 0 to 2^160 (SHA-1 ring).
  Each node placed at hash(node_id) on the ring.
  Each key routed to the FIRST node clockwise from
  hash(key) on the ring.
  
  Adding node X at position p:
    Only keys in (prev_node, p] move to X.
    All other keys unchanged.
    Average: 1/N fraction of keys moved.
  
VIRTUAL NODES (VNODE):
  Problem with basic consistent hashing:
  Non-uniform node placement → hotspots.
  Large nodes can't have proportionally more keys.
  
  Solution: each physical node has 150 virtual positions.
  Physical node A: vnode-A-1, vnode-A-2, ..., vnode-A-150
  All 150 placed on the ring by hashing vnode IDs.
  
  Benefits:
  - Uniform distribution (150 positions per node)
  - Heterogeneous hardware: big node = more vnodes
  - Failure spreads load across 150 neighbors (not 1)
```

**TECHNIQUE 2: VECTOR CLOCKS FOR CONFLICT DETECTION:**

```python
# Vector clock example (Dynamo shopping cart)

# Version 1: Cart updated by client (server A)
cart_v1 = {
    "items": ["item1"],
    "vector_clock": {"server_A": 1}
}

# Version 2: Cart updated by client (server A again)
cart_v2 = {
    "items": ["item1", "item2"],
    "vector_clock": {"server_A": 2}
}
# v2 vector_clock dominates v1: [A:2] >= [A:1] for all
# v2 causally follows v1. No conflict.

# Concurrent update: user adds item3 on server B
# while network partition prevents B from seeing v2
cart_v3_from_B = {
    "items": ["item1", "item3"],
    "vector_clock": {"server_A": 1, "server_B": 1}
}
# v3 clock: [A:1, B:1]
# v2 clock: [A:2]
# v3[A]=1 < v2[A]=2: v3 does NOT dominate v2
# v2[B]=0 < v3[B]=1: v2 does NOT dominate v3
# → CONCURRENT. Conflict. Both versions returned to client.

# CLIENT MERGES:
# Dynamo returns both versions to the shopping cart service.
# Cart service merges: take UNION of items.
cart_merged = {
    "items": ["item1", "item2", "item3"],  # union
    "vector_clock": {"server_A": 2, "server_B": 1}
    # merged clock = max of each component
}
# Next write supersedes both.

# VECTOR CLOCK TRUNCATION PROBLEM:
# After many servers, vector clocks grow unbounded.
# Dynamo truncated clocks after X entries, oldest first.
# This can cause false conflicts (treated as concurrent
# when they were actually causal). Dynamo accepted this
# as an operational trade-off.
```

**TECHNIQUE 3: ANTI-ENTROPY WITH MERKLE TREES:**

```
MERKLE TREE ANTI-ENTROPY:
  Problem: how does replica B know which keys it
  is missing compared to replica A?
  Naive: compare all keys. O(N) messages. Expensive.
  
  Merkle tree: binary hash tree over key ranges.
  
  Leaf nodes: hash(value) for individual keys.
  Internal nodes: hash(left_child || right_child).
  Root: single hash representing the entire key range.
  
  Comparison protocol:
  1. A sends root hash to B.
  2. B: same root? In sync. Stop.
  3. B: different root? Send children hashes.
  4. Recurse until we find the divergent leaves.
  5. Sync only the divergent keys.
  
  Cost: O(log N) messages to find divergent keys.
  Efficient even with millions of keys.

ANTI-ENTROPY TIMING:
  Dynamo runs anti-entropy continuously in the background.
  Frequency is tunable (default: every few seconds).
  This is how eventual consistency is eventually achieved:
  even if a write was missed during a partition, Merkle
  tree anti-entropy will eventually propagate it.
```

**TECHNIQUE 4: GOSSIP PROTOCOL FOR FAILURE DETECTION:**

```
GOSSIP-BASED MEMBERSHIP:
  Each node maintains a membership list:
  {node_id: (heartbeat_counter, timestamp)}
  
  Every T seconds: pick a random node from the list.
  Send it your full membership list.
  Receiver: merge (take max heartbeat_counter per node).
  
  FAILURE DETECTION:
  If node X's heartbeat_counter hasn't increased in
  T_fail seconds: X is considered temporarily unavailable.
  After T_delete seconds: X removed from membership list.
  
  Properties:
  - O(log N) propagation: information reaches all nodes
    in O(log N) gossip rounds.
  - No single coordinator: fully decentralized.
  - Eventually consistent membership: all nodes converge
    to the same view.
  - False positives possible: slow node = detected failed.
    Handled by hinted handoff (temporary storage).
```

---

### 🧠 Mental Model / Analogy

> Dynamo is like a city postal system with no central
> sorting facility. Each neighborhood post office (node)
> handles mail (keys) for a portion of the city.
> When a post office is temporarily closed (failure),
> the next open post office takes in the mail with a
> sticky note: "deliver to the closed office when it
> reopens" (hinted handoff). Post offices gossip with
> neighbors to learn about closures (gossip protocol).
> If two post offices independently delivered different
> versions of the same package (concurrent writes), they
> keep both versions and let the recipient (client)
> decide which they wanted (conflict resolution). The
> city never stops delivering mail, even if a post
> office goes down. Availability is paramount.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - Why Dynamo exists:**
Amazon's shopping cart needed to be always writable.
Strong consistency (which requires quorum agreement)
can block under partitions. Dynamo chose to always
accept writes and resolve conflicts later.

**Level 2 - Consistent hashing solves resharding:**
Adding nodes to a hash-based cluster normally requires
rehashing all keys. Consistent hashing with virtual
nodes means only O(1/N) of keys move when a node joins
or leaves.

**Level 3 - Vector clocks track causality:**
Vector clocks detect when two writes were concurrent
(happened without knowledge of each other). Dynamo
returns all concurrent versions to the client for
application-level conflict resolution. For shopping
carts: take the union.

**Level 4 - Sloppy quorum sacrifices strict consistency for availability:**
Normal quorum requires responses from the N designated
nodes. Sloppy quorum accepts responses from ANY N
live nodes. This means a write might be acknowledged
by a node that is not a long-term owner of that key.
Hinted handoff ensures the data is eventually moved
to the correct node when it recovers.

**Level 5 - Dynamo's design trade-offs and legacy:**
Dynamo's design influenced Cassandra (data model +
gossip + consistent hashing), Riak (full Dynamo clone),
and DynamoDB (simplified API, managed service). The
key lesson: CAP is a choice in system design. Dynamo
explicitly chose AP (availability over consistency)
for specific use cases. This was correct for shopping
carts, wrong for banking transactions. Cassandra
adopted Dynamo's availability-first approach but
added tunable consistency (QUORUM reads/writes) to
allow CP behavior for workloads that need it.

---

### 💻 Code Example

**Implementing a Simplified Dynamo-Style Read Path**

```python
# Simplified Dynamo read path (sloppy quorum, conflict merge)

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

VectorClock = dict[str, int]

@dataclass
class Value:
    data: Any
    vector_clock: VectorClock

def vc_dominates(vc_a: VectorClock, vc_b: VectorClock) -> bool:
    """Returns True if vc_a causally dominates vc_b."""
    all_keys = set(vc_a.keys()) | set(vc_b.keys())
    # a dominates b if a[k] >= b[k] for all k
    # and a[k] > b[k] for at least one k
    at_least_one_greater = False
    for k in all_keys:
        a_val = vc_a.get(k, 0)
        b_val = vc_b.get(k, 0)
        if a_val < b_val:
            return False
        if a_val > b_val:
            at_least_one_greater = True
    return at_least_one_greater

def resolve_versions(versions: list[Value]) -> list[Value]:
    """
    Filter versions to only concurrent (conflicting) ones.
    Remove any version that is causally dominated by another.
    If only one version: no conflict. If multiple: conflict.
    """
    # Keep only non-dominated versions:
    result = []
    for i, v in enumerate(versions):
        dominated = False
        for j, other in enumerate(versions):
            if i != j and vc_dominates(other.vector_clock,
                                       v.vector_clock):
                dominated = True
                break
        if not dominated:
            result.append(v)
    return result


class DynamoNode:
    """Single node in a Dynamo-like cluster."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        # key → list of Value (multiple versions possible)
        self.storage: dict[str, list[Value]] = defaultdict(list)

    def write(self, key: str, data: Any,
              context: VectorClock | None = None):
        """Write with optional context (client-provided vc)."""
        # Increment this node's component in the vector clock:
        if context is None:
            context = {}
        new_vc = dict(context)
        new_vc[self.node_id] = new_vc.get(self.node_id, 0) + 1

        new_value = Value(data=data, vector_clock=new_vc)

        # Replace any dominated versions:
        existing = self.storage[key]
        kept = [v for v in existing
                if not vc_dominates(new_vc, v.vector_clock)]
        kept.append(new_value)
        self.storage[key] = kept

    def read(self, key: str) -> list[Value]:
        return self.storage.get(key, [])


class DynamoCluster:
    """Simplified 3-node Dynamo cluster, N=3, R=2, W=2."""

    def __init__(self):
        self.nodes = {
            "A": DynamoNode("A"),
            "B": DynamoNode("B"),
            "C": DynamoNode("C"),
        }
        self.R = 2  # read quorum
        self.W = 2  # write quorum

    def get(self, key: str) -> list[Value]:
        """Read from R nodes; merge + resolve conflicts."""
        all_versions: list[Value] = []
        for name, node in self.nodes.items():
            all_versions.extend(node.read(key))

        # Resolve: keep only non-dominated versions
        resolved = resolve_versions(all_versions)
        return resolved  # Multiple = conflict (client resolves)

    def put(self, key: str, data: Any,
            context: VectorClock | None = None):
        """Write to W nodes."""
        written = 0
        for name, node in self.nodes.items():
            node.write(key, data, context)
            written += 1
            if written >= self.W:
                break


# EXAMPLE: Shopping cart concurrent writes

cluster = DynamoCluster()

# User adds item1 from server A:
cluster.put("cart:user1", ["item1"], context={})
v1 = cluster.get("cart:user1")
print("After item1:", [v.data for v in v1])
# [['item1']]

# Network partition: user simultaneously adds item2
# from server A and item3 from server B.
# Simulate by writing to individual nodes:
vc_before_partition = {"A": 1}  # Context from before

cluster.nodes["A"].write("cart:user1", ["item1", "item2"],
                         context=vc_before_partition)
cluster.nodes["B"].write("cart:user1", ["item1", "item3"],
                         context=vc_before_partition)
cluster.nodes["C"].write("cart:user1", ["item1", "item3"],
                         context=vc_before_partition)

# Read: cluster returns BOTH versions (conflict)
versions = cluster.get("cart:user1")
print("Concurrent versions:", [v.data for v in versions])
# [['item1', 'item2'], ['item1', 'item3']]

# CLIENT MERGES (union):
merged_items = list({
    item
    for v in versions
    for item in v.data
})
print("Merged:", sorted(merged_items))
# ['item1', 'item2', 'item3']
```

---

### ⚖️ Comparison Table

| Feature | Amazon Dynamo (2007) | Cassandra | Riak |
|---|---|---|---|
| **Data model** | Key-value | Wide-column | Key-value |
| **Consistency** | Tunable (W+R>N) | Tunable | Tunable |
| **Conflict resolution** | Client (vector clocks) | Last-Write-Wins (LWW) default | CRDT / client |
| **Partitioning** | Consistent hashing + vnodes | Consistent hashing + vnodes | Consistent hashing |
| **Gossip** | Yes | Yes | Yes |
| **Anti-entropy** | Merkle trees | Merkle trees | Yes |
| **Production status** | Internal; not available | Open source | Open source |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Amazon Dynamo is the same as Amazon DynamoDB" | DynamoDB is a commercial service inspired by Dynamo principles but it is not the Dynamo described in the 2007 paper. DynamoDB uses different internal mechanisms, provides a different API, and supports more data types and transactional operations. |
| "Dynamo provides eventual consistency for all writes" | Dynamo is tunable: W+R>N provides strong consistency (overlapping quorums guarantee you read the latest write). W=1, R=1 provides availability-first eventual consistency. Amazon used different settings for different services based on their consistency requirements. |
| "Vector clocks are used by Cassandra" | Cassandra does NOT use vector clocks. It uses Last-Write-Wins (LWW) based on a client-provided timestamp. This is simpler but can silently lose data if clocks diverge. Riak used true vector clocks (later switching to dotted version vectors to avoid explosion). |
| "Sloppy quorum is just a regular quorum with failures tolerated" | Sloppy quorum is weaker: it accepts writes from ANY N live nodes, not the PREFERRED N nodes. After recovery, hinted handoff moves the data to the correct nodes. This means during a partition, two different sets of N nodes might respond, and they may not overlap, violating the W+R>N consistency guarantee temporarily. |

---

### 🚨 Failure Modes & Diagnosis

**Stale Reads After Sloppy Quorum Write**

**Symptom:** User writes a value. Immediately reads
it back. Gets the old value (stale read). No error.
The write was acknowledged successfully.

**Root Cause:** The write went to a sloppy quorum
(three live nodes that are NOT the preferred replicas
for this key). The read went to the preferred replicas
(which have not yet received the hinted handoff).
The preferred replicas have the old value. Hinted
handoff is asynchronous.

**Diagnosis:**
```python
# Check if hinted handoff is backed up
# (too many hints queued = healthy nodes overwhelmed
# when failed nodes recover)

# In Cassandra (similar architecture):
# nodetool tpstats | grep HintedHandoff

# In monitoring: track hint delivery lag metric.
# High hint delivery lag = nodes recovering slowly
# or hint queue growing faster than delivery.

# For Dynamo-style systems:
# Check: is W+R > N?
# If W=1, R=1, N=3: W+R=2 < N=3: not strongly consistent.
# Stale reads are EXPECTED under this configuration.

# Fix for stale read in shopping cart:
# Accept it (eventual consistency: cart will converge).
# Or: use R=2, W=2 for strong consistency on that path.
```

**Fix:** For stale-read-sensitive operations: increase
R so that W+R > N. For shopping cart merges: accept
stale reads as expected behavior and implement
client-side merge on conflict.

---

### 🔗 Related Keywords

**Prerequisites:** `Consistent Hashing` (DST-011),
`Vector Clocks` (DST-017), `Gossip Protocol` (DST-018),
`Quorum` (DST-019)

**Related:** `Sloppy Quorum` (DST-032),
`Anti-Entropy` (DST-029)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ TECHNIQUE       │ PURPOSE                               │
├─────────────────┼───────────────────────────────────────┤
│ Consistent hash │ Partition keys; minimize resharding   │
│ + 150 vnodes    │ on node add/remove                    │
├─────────────────┼───────────────────────────────────────┤
│ Vector clocks   │ Detect concurrent writes (conflicts)  │
│                 │ Client merges concurrent versions     │
├─────────────────┼───────────────────────────────────────┤
│ Gossip          │ Failure detection + membership        │
│                 │ O(log N) propagation                  │
├─────────────────┼───────────────────────────────────────┤
│ Merkle trees    │ Anti-entropy: efficient diff between  │
│                 │ replicas; sync only divergent keys    │
├─────────────────┼───────────────────────────────────────┤
│ Sloppy quorum + │ Writes always accepted; moved to      │
│ hinted handoff  │ correct nodes on recovery             │
├─────────────────┼───────────────────────────────────────┤
│ W+R > N         │ Strong consistency (overlapping sets) │
│ W+R <= N        │ Eventual consistency (higher avail.)  │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

The Dynamo paper codified the principle that
"availability > consistency" is a valid and
rational engineering choice for specific use cases.
This was not a discovery - it was a documented,
deliberate trade-off with measurable business
consequences. The paper's lasting contribution
was not the individual techniques (consistent
hashing predates Dynamo; vector clocks predate it)
but the integration: how all six techniques work
together to create a coherent availability-first
system. Each technique addresses a specific failure
mode: consistent hashing handles node churn,
vector clocks handle conflicting writes, gossip
handles failure detection, Merkle trees handle
replica divergence, sloppy quorum handles node
failures during writes, and tunable consistency
handles different consistency requirements. This
decomposition - identify each failure mode,
design a targeted technique for each, integrate
them - is the template for designing any complex
distributed system.

---

### 💡 The Surprising Truth

The Dynamo paper revealed that Amazon's shopping
cart used a read-repair and client-side merge
strategy for conflicts: the shopping cart client
would receive multiple conflicting versions and
would merge them by taking the UNION of all items.
This meant that items deleted from the cart sometimes
"reappeared" after a merge. Amazon explicitly
accepted this behavior as a trade-off: a cart that
sometimes shows extra items is better than a cart
that is unavailable. The paper also noted that in
practice, concurrent updates were rare (most users
access their cart sequentially). The elaborate
vector clock machinery existed for the rare case,
not the common one. This illustrates a general
principle: design your system for correctness in
the uncommon case; optimize for performance in the
common case. The Dynamo design handles the uncommon
concurrent write case correctly (via vector clocks
and client merges) while delivering maximum
performance in the common sequential write case.

---

### ✅ Mastery Checklist

1. [EXPLAIN] Why does Dynamo use 150 virtual nodes
   per physical node? What problem does this solve
   compared to placing each physical node once on
   the ring?
2. [TRACE] Given a 3-node Dynamo cluster (N=3, W=2,
   R=2) and a network partition that splits the cluster
   into [A] and [B, C]: can writes proceed? Can reads
   proceed? When the partition heals, what happens?
3. [COMPARE] Dynamo vector clocks vs Cassandra LWW
   timestamps: which can silently lose data? Under
   what circumstances?
4. [DESIGN] A system needs: always accept writes,
   detect conflicts, let the application merge. Should
   it use Dynamo-style vector clocks, CRDTs, or LWW?
   What are the trade-offs for each choice?
5. [IMPLEMENT] Sketch the anti-entropy protocol using
   Merkle trees. How do two nodes efficiently find
   the subset of keys that differ between them without
   transferring all keys?
