---
layout: default
title: "Consistent Hash Ring"
parent: "Data Structures & Algorithms"
nav_order: 45
permalink: /dsa/consistent-hash-ring/
number: "0045"
category: Data Structures & Algorithms
difficulty: ★★★
depends_on: Hashing Techniques, TreeMap
used_by: Distributed Locking, Caching, Gossip Protocol
related: Virtual Nodes, Rendezvous Hashing, Distributed Systems
tags:
  - datastructure
  - advanced
  - algorithm
  - distributed
  - deep-dive
---

# 045 — Consistent Hash Ring

⚡ TL;DR — A Consistent Hash Ring maps keys to nodes on a circular hash space so that adding/removing nodes only re-maps O(K/N) keys instead of O(K) with naive modulo hashing.

| #045 | Category: Data Structures & Algorithms | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Hashing Techniques, TreeMap | |
| **Used by:** | Distributed Locking, Caching, Gossip Protocol | |
| **Related:** | Virtual Nodes, Rendezvous Hashing, Distributed Systems | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A distributed cache has 4 nodes. You hash keys with `node = hash(key) % 4`. Client requests route correctly to the right node. Now a 5th node is added: `hash(key) % 5`. For a dataset with 1 million keys, ~80% of them map to a different node than before. All these keys are "cache misses" — the cache is effectively emptied. Similarly, removing a node causes mass rerouting. In a production system with millions of requests per second, this is catastrophic.

**THE BREAKING POINT:**
Simple modulo hashing ties every key's node assignment to the total number of nodes. Change the node count by 1, and the denominator changes, shuffling almost all assignments. The cost of scaling — adding or removing nodes — is proportional to the entire dataset, not just the affected fraction.

**THE INVENTION MOMENT:**
Place both keys and nodes on a circle (hash ring) from 0 to 2^32. Each key is assigned to the first node clockwise from its position. Adding a node only affects keys between the new node and its predecessor — typically 1/N of all keys. Removing a node only affects its own 1/N share. This is exactly why the Consistent Hash Ring was created.

---

### 📘 Textbook Definition

**Consistent Hashing** maps objects to nodes using a circular hash space (hash ring) of size 2^32 or 2^64. Both nodes and keys are hashed to points on the ring; each key is assigned to the first node at or clockwise from the key's hash position. When a node is added, only the keys in the arc between the new node and its clockwise predecessor need re-mapping — roughly K/N keys for K total keys and N nodes. When a node is removed, only its K/N keys are re-mapped. **Virtual nodes** (multiple hash positions per physical node) improve load balance.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A circular hash space where adding/removing a node only moves 1/N of the keys, not all of them.

**One analogy:**
> Picture a round clock face numbered 0–360. Four security guards are placed at 12, 3, 6, and 9 o'clock. Each guard protects all rooms "between" them and the previous guard. If a 5th guard joins at 1:30, only the rooms between 12 and 1:30 transfer to the new guard — not every room.

**One insight:**
The "ring" is not a data structure by itself — it is the *hash space* interpreted as circular. The implementation is a sorted map (TreeMap) from hash values to node IDs. The ring is just the conceptual mental model; `ceilingKey(hash)` wraps around to `firstKey()` for the "clockwise" lookup.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Both nodes and keys are mapped to the same circular hash space [0, 2^32).
2. A key is assigned to the node whose position is the smallest value ≥ the key's hash (clockwise neighbor).
3. Adding/removing a node changes assignments only for keys in the arc adjacent to that node.

**DERIVED DESIGN:**
**Implementation** using `TreeMap<Long, String>` (ring):
- Add node S: `ring.put(hash(S), S)`
- Remove node S: `ring.remove(hash(S))`
- Assign key K: `entry = ring.ceilingEntry(hash(K)); if null, use ring.firstEntry()` (wrap-around)

**Without virtual nodes**: N nodes, so each physical node owns approximately 2^32/N of the hash space. But random placement gives poor balance — some nodes might get 2× the expected keys.

**Virtual nodes** (vnodes): each physical node is hashed to V positions on the ring. With V=150, the law of large numbers produces near-uniform distribution across all physical nodes. V=150 means each physical node occupies 150 arcs; the probability of any arc being assigned to the wrong node is negligible.

**THE TRADE-OFFS:**
**Gain:** O(K/N) remapping on topology change, horizontal scaling without cache invalidation.
**Cost:** Implementation complexity with virtual nodes, uneven physical load without vnodes, ring requires O(N×V) memory.

---

### 🧪 Thought Experiment

**SETUP:**
Cache cluster of 3 nodes, 300 keys uniformly distributed (100 per node). Add a 4th node.

WITHOUT CONSISTENT HASHING (modulo):
Naive: `node = hash(key) % N`. Old N=3, new N=4. `hash(key) % 3 ≠ hash(key) % 4` for ~75% of keys. ~225 keys must be re-cached.

WITH CONSISTENT HASHING:
New node inserted between node A (at position 100) and node B (at position 200). Keys between positions 100 and new node's position (150) — approximately 50 keys — transfer from B to the new node. 250 keys stay exactly where they are. Only ~17% of keys remapped.

**THE INSIGHT:**
Consistent hashing limits the blast radius of topology changes to 1/N of the dataset — deterministically. This transforms "restart causes total cache miss" into "scale operation causes ~10% cache miss." The same principle applies to distributed database sharding (Dynamo, Cassandra) and load balancing.

---

### 🧠 Mental Model / Analogy

> Consistent hashing is like assigning countries on a globe to the nearest time zone capital. When a new capital is added, only countries between it and the previous capital reassign. Removing a capital redistributes only its own countries to the next capital — not the whole map.

- "Globe circumference" → hash ring [0, 2^32)
- "Time zone capital" → node hash position
- "Country" → key hash position
- "Nearest clockwise capital" → assigned node
- "New capital added" → new node absorbs adjacent arc

Where this analogy breaks down: Capitals are chosen geographically; nodes on the hash ring are placed by their hash value — uniform in expectation but clustered in practice without virtual nodes.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
A system to route requests to distributed nodes where adding or removing a node only affects a small fraction of the data, rather than scrambling everything.

**Level 2 — How to use it (junior developer):**
Use `TreeMap<Long, Node>` for the ring. `addNode(n)`: `ring.put(hash(n), n)` (add virtual nodes: loop V times). `getNode(key)`: `ceilingEntry(hash(key))`, if null use `firstEntry()`. `removeNode(n)`: remove all V virtual node entries. Libraries: consistent4j, Guava's `Hashing.consistentHash()` (for simple cases).

**Level 3 — How it works (mid-level engineer):**
Each physical node registers V virtual nodes: `for v in 0..V: ring.put(hash(node_name + v), node)`. Virtual nodes fill the ring densely, ensuring near-uniform load. Adding a physical node means adding V entries to the ring (O(V log N)). `getNode(key)`: one `ceilingKey` operation on a `TreeMap` — O(log N). Vector clock-style token metadata tracks which node owns which arc range, shared via gossip protocol in systems like Cassandra.

**Level 4 — Why it was designed this way (senior/staff):**
Amazon Dynamo's 2007 paper coined "consistent hashing with virtual nodes" as the foundation for DynamoDB, Cassandra, and Riak. The virtual node count V=150 is empirically chosen: at V=150, load imbalance across N nodes is bounded to ±10% with high probability. Lower V → higher imbalance. Higher V → more metadata overhead. Modern systems (Cassandra 3.0+) switched to a different approach: deterministic virtual node placement (evenly spaced token assignment) rather than random hash assignment, which guarantees perfect balance instead of probabilistic balance, at the cost of more complex rebalancing during scale events.

---

### ⚙️ How It Works (Mechanism)

**Ring implementation:**
```java
class ConsistentHashRing {
    private TreeMap<Long, String> ring = new TreeMap<>();
    private int virtualNodes;

    ConsistentHashRing(int virtualNodes) {
        this.virtualNodes = virtualNodes;
    }

    void addNode(String node) {
        for (int i = 0; i < virtualNodes; i++) {
            long hash = hash(node + "#" + i);
            ring.put(hash, node);
        }
    }

    void removeNode(String node) {
        for (int i = 0; i < virtualNodes; i++) {
            ring.remove(hash(node + "#" + i));
        }
    }

    String getNode(String key) {
        if (ring.isEmpty()) return null;
        long hash = hash(key);
        Map.Entry<Long, String> entry = ring.ceilingEntry(hash);
        if (entry == null) entry = ring.firstEntry(); // wrap
        return entry.getValue();
    }

    private long hash(String s) {
        // Use MurmurHash or MD5 for uniform distribution
        return Hashing.murmur3_128().hashString(
            s, UTF_8).asLong();
    }
}
```

**Ring with 3 nodes and 2 virtual nodes each:**
```
Hash ring [0, 2^32):

0               1B            2B            3B         4B=0
|───────────────|──────────────|─────────────|──────────|
A1   B1   C1   A2   B2    C2
↑    ↑    ↑    ↑    ↑     ↑
A's  B's  C's  A's  B's   C's

Key X hashes to position 1.5B → nearest clockwise = A2 → routes to A
```

┌──────────────────────────────────────────────┐
│  Add node D between B1 and C1               │
│                                              │
│  Before: B1 owns arc [B1..C1]               │
│  After:  D1 is placed in arc [B1..C1]       │
│          Keys in [B1..D1] transfer to D     │
│          Keys in [D1..C1] stay on C         │
│  Only ~1/N keys affected per addition       │
└──────────────────────────────────────────────┘

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
```
Client sends request with key K
→ hash(K) computed
→ ring.ceilingEntry(hash(K)) → nearest node
→ [CONSISTENT HASH RING ← YOU ARE HERE]
→ Request routed to target node
→ Node processes request
```

**FAILURE PATH:**
```
Target node fails
→ Ring doesn't automatically update
→ Requests route to failed node
→ Health check detects failure → removeNode()
→ Keys redistribute to next clockwise node
→ 1/N of requests experience temporary miss
```

**WHAT CHANGES AT SCALE:**
At 1,000+ nodes, each with V=150 virtual nodes, the ring has 150,000 entries. `TreeMap` lookups are O(log 150,000) ≈ 17 comparisons — still fast. The metadata size (ring) fits comfortably in memory. At 10,000+ nodes, gossip propagation of ring changes becomes the bottleneck — each topology change must propagate to all nodes. Consistent hashing is well-proven at Cassandra's scale (thousands of nodes, petabyte datasets).

---

### 💻 Code Example

**Example 1 — Cache routing:**
```java
ConsistentHashRing ring = new ConsistentHashRing(150);
ring.addNode("cache-server-1");
ring.addNode("cache-server-2");
ring.addNode("cache-server-3");

// Route request to correct cache server
String server = ring.getNode("user:alice:profile");
// e.g., "cache-server-2" — determined by hash position

// Scale out: add server. Only ~1/4 keys reroute.
ring.addNode("cache-server-4");
// Most keys unchanged in routing

// server = ring.getNode("user:alice:profile")
// still "cache-server-2" (probably)
```

**Example 2 — Guava simple consistent hash (no virtual nodes):**
```java
// Guava: deterministic, no virtual nodes, for limited use
int bucket = Hashing.consistentHash(
    Hashing.md5().hashString(key, UTF_8),
    3 // num buckets
);
// Returns same bucket for same key as long as N doesn't change
// On N: 3→4, ~25% of keys reroute (not 1/N)
// Less optimal for dynamic scaling than ring approach
```

---

### ⚖️ Comparison Table

| Strategy | Keys remapped on node add | Load balance | Implementation | Best For |
|---|---|---|---|---|
| **Consistent Hash Ring** | O(K/N) | Good+vnodes | Moderate | Distributed caches, DHT |
| Naive Modulo | O(K) | Perfect | Trivial | Static node count |
| Rendezvous Hashing | O(K/N) | Perfect | Simple | Small cluster, no vnodes needed |
| Jump Consistent Hash | O(K/N) | Perfect | Very simple | Sequential node IDs only |

How to choose: Use Consistent Hash Ring for general distributed caching with dynamic scaling. Use Rendezvous Hashing when virtual nodes add unwanted complexity and cluster size is small. Use Modulo only when the node count is fixed forever.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Adding a node remaps exactly 1/N keys | Without virtual nodes, remapping is approximately 1/N in expectation but can vary widely; virtual nodes ensure this |
| Consistent hashing guarantees perfect load balance | Without virtual nodes, random placement creates up to 2–3× load imbalance between nodes |
| The "ring" is a special data structure | The ring is a concept; the implementation is a TreeMap with modular (wrap-around) lookup |
| All hashing algorithms produce a consistent hash ring | Only hashing algorithms that map to a large uniform integer space work; use MurmurHash or SHA-256, not Java's `hashCode()` |

---

### 🚨 Failure Modes & Diagnosis

**1. Severe load imbalance without virtual nodes**

**Symptom:** One cache node handles 40% of requests while others handle 15% each.

**Root Cause:** Without virtual nodes, physical node hash positions cluster non-uniformly. One node may own an arc 4× larger than average.

**Diagnostic:**
```bash
# Check key distribution per node:
ring.getNodeKeyCount().forEach((node, count) ->
    System.out.println(node + ": " + count));
# Look for nodes with 2-3x average key count
```

**Fix:** Add V=150 virtual nodes per physical node. Rebalance data after adding vnodes.

**Prevention:** Always use virtual nodes in production. V≥100 is typical for good statistical balance.

---

**2. All keys route to same node after ring rebuild**

**Symptom:** After service restart, one node receives 100% of traffic.

**Root Cause:** `hash()` function is not deterministic across restarts (e.g., uses Java `hashCode()` which is JVM-instance dependent, random salt, etc.).

**Diagnostic:**
```java
// Test: same key, same hash before and after restart?
System.out.println(hash("test-key")); // run twice
// If different: hash is non-deterministic
```

**Fix:** Use a deterministic hash: MurmurHash3, SHA-256, or `Hashing.murmur3_128()` from Guava.

**Prevention:** Never use Java's `Object.hashCode()` or anything that changes between JVM runs for routing decisions.

---

**3. Hot shard from poor key distribution**

**Symptom:** One virtual node receives disproportionate traffic regardless of virtual node count.

**Root Cause:** Key space is not uniformly distributed. Many keys cluster at nearby hash values (e.g., monotonically increasing integer keys).

**Diagnostic:**
```bash
# Histogram of key hash values:
keys.stream().mapToLong(k -> hash(k)).sorted()
    .boxed().collect(groupingBy(h -> h >> 30))
    .forEach((bucket, list) ->
        System.out.println(bucket + ": " + list.size()));
```

**Fix:** Pre-hash keys through a secondary uniform hash before ring assignment. Apply a salt transformation to integer IDs.

**Prevention:** Validate key distribution is uniform before deploying consistent hashing; test with production key samples.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Hashing Techniques` — uniform hash functions are essential; poor hash functions cause imbalance.
- `TreeMap` — the ring is implemented as a sorted map with wrap-around lookup.

**Builds On This (learn these next):**
- `Virtual Nodes` — the essential extension that makes consistent hashing practically load-balanced.
- `Gossip Protocol` — ring membership updates propagate between nodes via gossip.

**Alternatives / Comparisons:**
- `Rendezvous Hashing` — simpler algorithm, same O(K/N) remapping, no virtualnode complexity.
- `Naive Modulo` — perfect balance but O(K) remapping on any topology change.

---

### 📌 Quick Reference Card

┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Circular hash space mapping keys to nodes;│
│              │ node changes only affect 1/N of keys      │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Modulo hashing remaps ALL keys when node  │
│ SOLVES       │ count changes — kills caches on scaling   │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Placing BOTH keys and nodes on a ring      │
│              │ localises the impact of topology changes  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Distributed caches, database sharding,    │
│              │ DHT, load balancing with dynamic scaling  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Node count is fixed (use modulo instead); │
│              │ or building is simpler with rendezvous    │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ O(K/N) remapping vs O(N×V) ring metadata  │
│              │ + virtual-node complexity                 │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "A round clock face: new security guard   │
│              │  only takes over adjacent rooms"          │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Virtual Nodes → Gossip Protocol → Dynamo  │
└──────────────────────────────────────────────────────────┘

---

### 🧠 Think About This Before We Continue

**Q1.** A Cassandra cluster uses consistent hashing with V=256 virtual nodes per physical node. When adding a new physical node to a 10-node cluster, how many virtual nodes does the new node receive (on average), where do they come from, and what is the expected percentage of data that must migrate? If each physical node stores 1 TB, what is the expected data transfer volume during this scale-out operation, and how does this compare to naive repartitioning?

**Q2.** Amazon DynamoDB partitions data using consistent hashing but also needs to guarantee that the N replicas for a given key are distributed across N different availability zones. Explain why a simple "next N clockwise nodes" replication strategy fails when multiple virtual nodes from the same physical node (or same AZ) are adjacent on the ring, and describe the modification to the ring traversal algorithm needed to guarantee AZ-aware replica placement.

