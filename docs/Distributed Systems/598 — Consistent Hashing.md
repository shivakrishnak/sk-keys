---
layout: default
title: "Consistent Hashing"
parent: "Distributed Systems"
nav_order: 598
permalink: /distributed-systems/consistent-hashing/
number: "598"
category: Distributed Systems
difficulty: ★★★
depends_on: "Replication Strategies, Partitioning"
used_by: "Cassandra, DynamoDB, Memcached, Chord DHT, Riak"
tags: #advanced, #distributed, #partitioning, #scalability, #hashing
---

# 598 — Consistent Hashing

`#advanced` `#distributed` `#partitioning` `#scalability` `#hashing`

⚡ TL;DR — **Consistent Hashing** maps both data keys and nodes onto a circular hash ring, so adding or removing a node only remaps ~K/N keys (where K = total keys, N = nodes) instead of all keys — enabling near-zero redistribution cost when scaling clusters.

| #598            | Category: Distributed Systems                   | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------- | :-------------- |
| **Depends on:** | Replication Strategies, Partitioning            |                 |
| **Used by:**    | Cassandra, DynamoDB, Memcached, Chord DHT, Riak |                 |

---

### 📘 Textbook Definition

**Consistent Hashing** is a distributed hashing scheme in which both data keys and nodes are mapped to positions on a circular ring (modular hash space, typically 0 to 2^64-1). A key is assigned to the first node whose position is ≥ the key's hash (clockwise). When a node is added: it takes over the key range from its counterclockwise neighbour; only K/N keys need to move (not all K). When a node is removed: its key range is taken over by its clockwise neighbour; again only K/N keys move. Compare to simple modular hashing (hash(key) mod N): adding one node (N→N+1) remaps ~N/(N+1) of all keys — catastrophic for caches (mass cache misses). Consistent hashing solves this. **Virtual nodes (vnodes)**: each physical node maps to multiple positions on the ring (100-256 tokens). Smooths load distribution (physical nodes hold more uniform key ranges) and makes ring re-balancing smoother when nodes join/leave. Used by: Cassandra (vnodes), Amazon DynamoDB, Amazon Dynamo (original), Riak, Memcached (libketama), Apache Cassandra, Chord DHT. Hash functions: MD5 (Dynamo original), SHA-1, Murmur3 (Cassandra default).

---

### 🟢 Simple Definition (Easy)

Without consistent hashing: adding 1 server to a 10-server cache = ~90% of cache keys moved (10 mod 10 → 10 mod 11 for most keys). Cache miss storm. With consistent hashing: adding 1 server to a 10-server ring = ~10% of keys move (only the new server's slice). The "ring" means: data and servers are placed on a circle. Each data item belongs to the nearest server clockwise. Add server: only that server's clockwise slice is re-assigned. Everything else stays. Scale without pain.

---

### 🔵 Simple Definition (Elaborated)

Consistent hashing in 3 steps: (1) Hash space: imagine 0 to 100 on a circle. Hash Node A → position 10. Hash Node B → position 40. Hash Node C → position 70. (2) Key assignment: hash("user_123") → 35. Clockwise from 35: Node B (at 40). user_123 belongs to B. hash("order_456") → 65. Clockwise: Node C (at 70). order_456 belongs to C. (3) Node addition: Node D joins at position 25. Keys 10–25 (previously belonging to B) now belong to D. All other keys unchanged. ~25% of keys moved (D took one-quarter of the ring). Without consistent hashing: ALL keys would re-hash, causing catastrophic redistribution.

---

### 🔩 First Principles Explanation

**Hash ring mechanics, vnodes, and load distribution:**

```
NAIVE MODULAR HASHING:

  3 nodes: N0, N1, N2. Assign key to: hash(key) mod 3.

  Keys assigned: hash("a") mod 3 = 2 → N2. hash("b") mod 3 = 0 → N0. ...

  Add N3 (now 4 nodes). Reassign keys: hash(key) mod 4.

  "a": hash("a") mod 4 = 1 → N1 (WAS N2). Moved!
  "b": hash("b") mod 4 = 2 → N2 (WAS N0). Moved!

  Average fraction of keys moved when adding 1 node to N-node cluster:
    = N / (N+1) ≈ ~90% for 10 nodes → 11 nodes.

  For a 10M key cache: ~9M keys would move → cache miss storm.
  Database hot-spot: ~9M records re-routed to different nodes → read amplification.

  PROBLEM: modular hashing is catastrophically unstable for cluster membership changes.

CONSISTENT HASHING — THE RING:

  Hash space: 0 to 2^32 - 1 (32-bit hash) visualized as a circle.

  (0) ←──────────────────────────────────────────────────────────────────── (2^32 - 1)
                                                                                 ↑ same point

  Placing nodes: hash each node's identifier. Place at that position on ring.
    hash("NodeA") = 1,073,741,824 (2^30, roughly at 25% of ring)
    hash("NodeB") = 2,147,483,648 (2^31, roughly at 50% of ring)
    hash("NodeC") = 3,221,225,472 (3×2^30, roughly at 75% of ring)

  Ring visual (positions as percentages of ring):
    0%      25%      50%      75%     100%(=0%)
    |       |        |        |        |
    ●───────A────────B────────C────────●

  Key assignment: hash(key) → position. Clockwise to nearest node.
    hash("user_1") = 15% → clockwise → A (at 25%). Assigned to A.
    hash("user_2") = 35% → clockwise → B (at 50%). Assigned to B.
    hash("user_3") = 60% → clockwise → C (at 75%). Assigned to C.
    hash("user_4") = 80% → clockwise → A (at 100%/0%, wraps around). Assigned to A.

  Key ranges owned by each node:
    A: 75%–25% (the range AFTER C, wrapping around to A). (= 50% of ring)
    B: 25%–50%. (= 25% of ring)
    C: 50%–75%. (= 25% of ring)
    (Uneven — this is the load distribution problem for basic consistent hashing)

  ADDING NODE D at 37.5%:
    New ring:
    0%      25%  37.5%  50%      75%     100%
    |       |    |      |        |        |
    ●───────A────D──────B────────C────────●

    D takes over key range: 25%–37.5% (previously assigned to B).
    ONLY keys in 25%–37.5% moved (from B to D). ~12.5% of ring = ~12.5% of keys.
    A, rest of B, C: unchanged.

  REMOVING NODE B:
    B's key range (37.5%–50%) is taken by... the next clockwise node = C? No.
    The NEXT node clockwise from the START of B's range: that's the node that takes over.
    Actually: B's predecessor is D. So D extends its range from 25%–50% (takes B's range).
    Wait — assignment is clockwise to first node ≥ key's position.
    B removed. key at 45%: clockwise from 45% → C (at 50%). B's former keys go to C.

  KEY INSIGHT: Only ~1/N fraction of keys move for any single node add or remove.
    vs. modular: ~(N-1)/N fraction moves.

VIRTUAL NODES (VNODES) — FIXING LOAD IMBALANCE:

  Problem with basic consistent hashing:
    Nodes map to random positions → uneven ring coverage.
    Node A might own 1% of ring; Node B might own 30% of ring.
    Hotspot: B handles 30× more traffic than A.

  Solution: each physical node has multiple positions (virtual nodes / tokens).

  With 3 virtual nodes per physical node (9 total tokens on ring):

    Physical: NodeA → Tokens: A1, A2, A3 (3 positions on ring, spread evenly)
    Physical: NodeB → Tokens: B1, B2, B3
    Physical: NodeC → Tokens: C1, C2, C3

    Ring: ...A1...B1...C1...A2...B2...C2...A3...B3...C3...

    Each physical node owns ~3/9 = ~33% of ring (much more uniform).

  With many vnodes per node (e.g., 256 in Cassandra):
    Distribution is near-perfectly uniform.
    Adding a new node: it gets ~N_vnodes/(total_vnodes) share of each existing node's range.
    More incremental, smoother re-balancing.

  CASSANDRA VNODE REBALANCING:
    Old: num_tokens=1 per node (Cassandra < 1.2). Manual token assignment.
          Adding node: operator calculates midpoints, assigns token, move data.
    New: num_tokens=256 per node (default). Automatic token assignment.
          Adding node: Cassandra assigns 256 tokens spread across ring.
          Data transfer: each existing node gives ~1/N of its ranges to new node.
          Smooth, incremental, automatic.

REPLICATION WITH CONSISTENT HASHING:

  Replication factor RF=3: each key is replicated to RF consecutive nodes clockwise.

  key "user_1" → primary: A. Replicas: B, C (next 2 clockwise).
  key "user_2" → primary: B. Replicas: C, A.
  key "user_3" → primary: C. Replicas: A, B.

  NODE FAILURE: A fails.
    keys owned by A: now served by B (first replica). Data not lost (RF=3 still has B, C).
    Read/write: coordinator routes to B or C for A's key range.

  HINTED HANDOFF: when A is down, writes for A's range are stored on D (nearest available).
    When A recovers: D forwards buffered writes to A. A re-syncs.

LOOKUP COMPLEXITY:

  Finding which node owns a key:
    Binary search in sorted array of node positions: O(log N).
    Hash the key → find successor in sorted array.

  With vnodes: N×V tokens in sorted array. Binary search: O(log(N×V)).
    N=100 nodes, V=256 vnodes: 25,600 tokens. log2(25600) ≈ 14 operations. Negligible.

  Space: O(N×V) for the ring structure. For 100 nodes × 256 vnodes: 25,600 entries. Trivial.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT consistent hashing:

- Cluster resize triggers mass cache invalidation: adding 1 of 10 servers moves ~90% of keys
- Read amplification: requests routed to wrong node (no data) until rebalancing completes
- Slow scale-up/down: manual data migration for each cluster change

WITH consistent hashing:
→ Minimal redistribution: only ~1/N keys move per node add/remove
→ Smooth scaling: cluster can grow/shrink without cache miss storms
→ Replication: RF consecutive nodes provides data redundancy automatically

---

### 🧠 Mental Model / Analogy

> A circular sushi conveyor belt. Each seat around the belt is a "position." Dishes (data keys) are placed at specific positions on the belt. Chefs (nodes) each own a section of the belt — from the previous chef's section end to their section start. Each chef serves any dish in their section. A new chef joins: they take over the section immediately before their position (just a slice from one neighbor). No other chef is disturbed. A chef leaves: their section is absorbed by the next chef clockwise.

"Circular sushi belt" = the consistent hash ring (0 to 2^64 wrapping)
"Dishes on the belt" = data keys hashed to ring positions
"Chefs owning sections" = nodes owning key ranges
"New chef taking a slice from one neighbor" = only ~1/N keys migrate on node add

---

### ⚙️ How It Works (Mechanism)

```
CONSISTENT HASH RING OPERATIONS:

  Data structure: sorted array of (token → node) mappings.

  ADD NODE:
    1. Generate K virtual node hashes for new node.
    2. For each vnode hash: insert into sorted array.
    3. For each new position: keys in range (predecessor_position, new_position]
       must migrate from their current owner (successor of new_position) to new node.
    4. Trigger data migration for affected ranges.

  REMOVE NODE:
    1. Mark node as departing.
    2. Transfer data: for each vnode owned by departing node, transfer key range
       to the node's successor (clockwise).
    3. Remove vnode positions from sorted array.
    4. Update routing tables.

  KEY LOOKUP:
    1. hash(key) → position P.
    2. Binary search in sorted array for first token ≥ P.
    3. Return node owning that token.
    4. If position > max token: wrap to first token (ring property).
```

---

### 🔄 How It Connects (Mini-Map)

```
Partitioning (deciding how to split data across nodes)
        │
        ▼
Consistent Hashing ◄──── (you are here)
(data AND nodes on a circular ring; minimal redistribution on change)
        │
        ├── Virtual Nodes (vnodes): improve load balance on the ring
        ├── Replication Strategies: RF consecutive clockwise nodes
        └── Gossip Protocol: how nodes learn about ring membership changes
```

---

### 💻 Code Example

**Consistent hash ring implementation:**

```java
import java.util.SortedMap;
import java.util.TreeMap;

public class ConsistentHashRing<T> {

    private final SortedMap<Long, T> ring = new TreeMap<>();
    private final int virtualNodes;

    public ConsistentHashRing(int virtualNodes) {
        this.virtualNodes = virtualNodes; // e.g., 256 per node
    }

    public void addNode(T node) {
        for (int i = 0; i < virtualNodes; i++) {
            long hash = hash(node.toString() + "#" + i);
            ring.put(hash, node);
        }
    }

    public void removeNode(T node) {
        for (int i = 0; i < virtualNodes; i++) {
            long hash = hash(node.toString() + "#" + i);
            ring.remove(hash);
        }
    }

    public T getNode(String key) {
        if (ring.isEmpty()) return null;
        long keyHash = hash(key);

        // Find first node with position >= keyHash (clockwise successor)
        SortedMap<Long, T> tailMap = ring.tailMap(keyHash);

        // If no node clockwise from keyHash: wrap around to first node on ring
        long nodeHash = tailMap.isEmpty() ? ring.firstKey() : tailMap.firstKey();
        return ring.get(nodeHash);
    }

    // Murmur3-inspired simple hash (use proper library in production)
    private long hash(String key) {
        long h = 0;
        for (char c : key.toCharArray()) h = h * 31 + c;
        return h & 0xFFFFFFFFL; // Positive 32-bit value
    }

    public static void main(String[] args) {
        ConsistentHashRing<String> ring = new ConsistentHashRing<>(256);

        ring.addNode("Node-A");
        ring.addNode("Node-B");
        ring.addNode("Node-C");

        // Test distribution (1 million keys → count per node):
        Map<String, Integer> distribution = new HashMap<>();
        for (int i = 0; i < 1_000_000; i++) {
            String node = ring.getNode("key_" + i);
            distribution.merge(node, 1, Integer::sum);
        }
        distribution.forEach((node, count) ->
            System.out.printf("%s: %d keys (%.1f%%)%n", node, count, count / 10000.0));
        // Expected: ~333,333 per node (±5% with 256 vnodes per node).
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                | Reality                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Consistent hashing guarantees perfectly uniform distribution | Basic consistent hashing (1 position per node) is highly non-uniform — variance in node positions means some nodes own much more of the ring than others. Virtual nodes (vnodes) with N=256 tokens per node reduce standard deviation of load to ~√N/N ≈ ~6% (vs 100%+ variance without vnodes). "Consistent" in consistent hashing refers to stability of assignment on cluster changes, NOT uniformity of load distribution |
| Consistent hashing is only for caches                        | Consistent hashing is foundational in distributed databases (Cassandra, Riak, DynamoDB), distributed file systems, load balancers, and CDN request routing. Cassandra uses consistent hashing + vnodes as its primary partitioning strategy. DynamoDB uses consistent hashing for its partition key → node mapping. It's a general distributed partitioning technique, not specific to caching                                |
| Adding a node redistributes ~50% of keys                     | Adding 1 node to an N-node cluster redistributes ~1/N of keys — NOT ~50%. Adding to 10 nodes: ~10% move. Adding to 100 nodes: ~1% move. This is the core property of consistent hashing. Only the new node's clockwise predecessors (the nodes from which the new node takes ownership) need to transfer data                                                                                                                 |
| Consistent hashing eliminates the need for a routing layer   | Consistent hashing defines WHICH node owns a key, but doesn't eliminate the need for routing coordination. Nodes still need to maintain a consistent view of the ring (gossip, ZooKeeper). In Cassandra, every node knows the full ring and can act as coordinator. In Memcached, clients implement the ring locally. The ring state must be synchronized — consistent hashing doesn't solve membership management itself     |

---

### 🔥 Pitfalls in Production

**Hotspot from poor vnode configuration:**

```
SCENARIO: Cassandra cluster with num_tokens=1 (old default, pre-1.2 style).
  3 nodes. Manual token assignment gone wrong:
    Node A: token = 0
    Node B: token = 1    (tiny gap — B owns almost nothing)
    Node C: token = 100  (C owns 99% of ring)

  100% of traffic goes to C. A and B idle.

BAD: Old Cassandra with uneven manual tokens and no vnodes:
  # cassandra.yaml (node C — owns 99% of ring):
  initial_token: 100
  num_tokens: 1  # Only 1 position on ring — entire ring split by 3 positions.

  Result: C handles 99% of reads/writes. A, B: nearly idle.

FIX: Enable vnodes (num_tokens=256):
  # cassandra.yaml (all nodes — Cassandra auto-assigns 256 spread tokens):
  num_tokens: 256
  # Remove initial_token — let Cassandra generate evenly distributed tokens.

  # After restart + bootstrap: each node owns ~33% of ring (±5%).
  # Verify distribution:
  nodetool ring | grep -v "host" | awk '{print $7}' | sort -n
  # Ownership should show ~33.3% per node.

  # On a running cluster: changing num_tokens requires node decommission + re-add.
  # Cannot change num_tokens in place.

HOTSPOT 2: Hash skew — poor hash function:
  Using hashCode() % (2^32) for string keys.
  Java String.hashCode(): many collisions for similar strings ("key_1" vs "key_2").
  Many keys map to same or nearby ring positions → single node hotspot.

  FIX: Use Murmur3 (Cassandra default), xxHash, or FNV hash.
  These have near-perfect avalanche properties: similar inputs → wildly different outputs.
  Cassandra: com.google.common.hash.Hashing.murmur3_128()
```

---

### 🔗 Related Keywords

- `Virtual Nodes` — vnodes are the practical extension of consistent hashing that solves load imbalance
- `Gossip Protocol` — how nodes discover and share ring membership updates
- `Replication Strategies` — with consistent hashing, replicas = next N clockwise nodes
- `Partitioning` — consistent hashing is one of several partitioning strategies (vs. range-based)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Both keys and nodes on circular ring.    │
│              │ Node add/remove moves only ~1/N keys    │
│              │ (not all keys like modular hashing).    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Distributed caches or databases that    │
│              │ need to scale nodes dynamically; CDN    │
│              │ request routing; DHT implementations   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Small, static clusters where simple     │
│              │ modular hashing + manual sharding is    │
│              │ simpler and sufficient                  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A sushi belt where adding one chef only│
│              │  takes a slice — not a full rotation."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Virtual Nodes → Gossip Protocol →       │
│              │ Replication Strategies → Cassandra      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Cassandra cluster has 3 nodes with num_tokens=256. You add a 4th node. Cassandra assigns 256 new tokens spread evenly across the ring. How much data (as a percentage) does the new node receive? Which existing nodes contribute data to the new node? If num_tokens were 1 instead: how much data would the new node receive and from how many existing nodes?

**Q2.** Consistent hashing was designed for peer-to-peer DHTs (Chord algorithm) and adapted for distributed databases. In Chord DHT, each node only knows its successor and predecessor (O(1) routing table) but lookup takes O(N) hops. In Cassandra, every node stores the full ring (O(N) routing table) but lookup is O(1) (route directly to correct node). What is the trade-off between these two approaches, and when would Chord's O(1) routing table size matter?
