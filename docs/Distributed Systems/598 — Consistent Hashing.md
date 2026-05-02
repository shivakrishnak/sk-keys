---
layout: default
title: "Consistent Hashing"
parent: "Distributed Systems"
nav_order: 598
permalink: /distributed-systems/consistent-hashing/
number: "0598"
category: Distributed Systems
difficulty: ★★★
depends_on: Hashing, Distributed Systems Fundamentals
used_by: Cassandra, DynamoDB, Riak, Memcached, Kafka, CDNs
related: Virtual Nodes, Replication Strategies, Gossip Protocol
tags:
  - consistent-hashing
  - sharding
  - distributed-systems
  - advanced
---

# 598 — Consistent Hashing

⚡ TL;DR — Consistent hashing maps data keys and nodes to positions on a virtual ring. Each key is assigned to the nearest node clockwise on the ring. When a node joins or leaves, only the keys in the affected ring segment are remapped — not all keys. This minimizes data movement during cluster scaling: with N nodes and K keys, only K/N keys are moved on average when a node is added/removed. Used by Cassandra, DynamoDB, Riak (ring DHT), Kafka (partition-to-broker mapping), and CDN cache routing.

┌──────────────────────────────────────────────────────────────────────────┐
│ #598         │ Category: Distributed Systems      │ Difficulty: ★★★      │
├──────────────┼────────────────────────────────────┼──────────────────────┤
│ Depends on:  │ Hashing, Distributed Systems        │                      │
│ Used by:     │ Cassandra, DynamoDB, Riak, CDNs     │                      │
│ Related:     │ Virtual Nodes, Gossip Protocol      │                      │
└──────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

Naive sharding: `node = hash(key) % N`. Works fine with N nodes. Add one node → N becomes N+1 → EVERY key remaps to a different node. In a 10-node Memcached cluster: adding node 11 forces 10 of every 11 cache entries to point to different nodes. Cache miss rate spikes to ~90% → cache stampede → database overload. Consistent hashing solves this: adding a node only displaces the keys in its segment (≈ 1/N of all keys). The rest stay put.

---

### 📘 Textbook Definition

**Consistent hashing** (Karger et al., 1997) distributes both data keys and server nodes onto a virtual hash ring (space = [0, 2³²)):

1. **Hash nodes:** `position(node) = hash(node_id) mod 2³²`
2. **Hash keys:** `position(key) = hash(key) mod 2³²`
3. **Assignment:** key → nearest node clockwise on the ring
4. **Replication:** key → next R nodes clockwise (R = replication factor)

**Adding a node:** New node claims the ring segment between its predecessor and itself. Only keys in that segment are moved from the predecessor to the new node.

**Removing a node:** Node's ring segment is absorbed by its successor. Only the removed node's keys are moved to the successor.

**Key property:** On average, only K/N keys (out of K total) are remapped when adding or removing 1 node from an N-node cluster.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Map nodes and keys to a ring; key owns the next node clockwise; adding/removing a node only displaces its neighbor's data, not all data.

**Analogy:** Assigning tasks around a circular table. N people sit around a table, each responsible for tasks labeled with the angle nearest to them. A new person joins between Alice and Bob: they take over the tasks previously assigned to Bob in the arc between Alice and the new arrival. Alice and everyone else keeps their original assignments. Only Bob loses a slice of his tasks to the newcomer.

---

### 🔩 First Principles Explanation

```
CONSISTENT HASHING RING (simplified, 0-359 degrees):

  Nodes: hash(A)=0°, hash(B)=120°, hash(C)=240°
  
  Ring:
  0° ────── 120° ────── 240° ────── 0° (wrap-around)
  [A]        [B]          [C]
  
  Key assignment (go clockwise to next node):
  hash(key1)=30°  → A owns 0°-120°   → A handles key1
  hash(key2)=150° → B owns 120°-240° → B handles key2
  hash(key3)=270° → C owns 240°-360° → C handles key3
  
  ADD node D at 60°:
  Ring: [A=0°, D=60°, B=120°, C=240°]
  D owns 0°-60° (taken from A's range of 0°-120°)
  
  ONLY keys that hash to 0°-60° (previously owned by A) move to D.
  key2 (150°→B), key3 (270°→C) → UNCHANGED ✓
  
  NAIVE SHARDING comparison:
  Add node → N = N+1 → EVERY key_hash % N changes → all data moves
  
  REPLICATION (Cassandra style):
  Key at 150° → Primary: B (120°). Replicas: C (240°), A (0° next after wrap).
  Each key is handed to R=3 consecutive nodes clockwise on the ring.
```

---

### 🧠 Mental Model / Analogy

> Consistent hashing is like a postcode delivery district. Each post office covers the addresses from the last post office to theirs (clockwise on a circular map). When the postal service opens a new branch in District D, it absorbs a portion of District A's routes — only residents in that absorbed area get a new postman. Every other district's routes remain unchanged. If District B closes, their routes are transferred to District C (the next clockwise branch). Only B's residents get a new postman.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Map nodes + keys to a ring; clockwise nearest node = owner. Adding/removing one node moves only ~1/N of keys. Used for cache servers, database shards, CDN routing.

**Level 2:** Hot spots with basic consistent hashing: if nodes are unevenly positioned on the ring, some nodes may own very large or very small arcs. Node at 0° and next node at 359°: 0° node owns 359/360 of the ring — severe imbalance. Solution: virtual nodes (vnodes). Each physical node is assigned V positions on the ring (e.g., V=150 for Cassandra). V positions spread across the ring → nearly uniform load distribution. See keyword 599 — Virtual Nodes.

**Level 3:** Randomized consistent hashing (jump hash, rendezvous hashing): Rendezvous hashing — for a given key K, compute score=hash(K + node_id) for each node; assign K to the node with the highest score. Consistent: adding a node N takes ~1/N fraction of keys from all other nodes (uniformly, not just neighbors). Advantage: no ring data structure needed. Disadvantage: O(n) per lookup (evaluate n nodes). Used in distributed caches where n is small.

**Level 4:** Consistent hashing in Cassandra vs DynamoDB: Cassandra original = virtual ring, each token = one point on ring, data routed via token ranges. DynamoDB's partition layer: consistent hashing with automatic token management — DynamoDB moves tokens between partitions as load changes, transparently. Cassandra >= 3.0 (vnodes): automating token assignment — each node claims a set of tokens, Cassandra rebalances them. Kafka is NOT consistent hashing: partition-to-broker is a table-driven assignment managed by the controller, not a hash ring.

---

### ⚙️ How It Works (Mechanism)

```
CONSISTENT HASH RING IMPLEMENTATION:

  Data structure: TreeMap<Long, Node>  ← sorted positions on ring
  
  Adding a node:
  for (int i = 0; i < REPLICAS; i++) {
      long position = hash(node.id + "#" + i);  // V virtual positions
      ring.put(position, node);
  }
  
  Lookup for key:
  long keyhash = hash(key);
  Map.Entry<Long, Node> entry = ring.ceilingEntry(keyhash);  // The next node clockwise
  if (entry == null) {
      entry = ring.firstEntry();  // Wrap around: last key → first node on ring
  }
  return entry.getValue();
  
  Removing a node:
  for (int i = 0; i < REPLICAS; i++) {
      long position = hash(node.id + "#" + i);
      ring.remove(position);  // Keys in this arc automatically go to next node
  }
  
  REPLICATION (Cassandra-style):
  List<Node> replicas = new ArrayList<>();
  NavigableMap<Long, Node> tail = ring.tailMap(keyhash, true);  // From keyhash clockwise
  for (Map.Entry<Long, Node> e : Iterables.concat(tail.entrySet(), ring.entrySet())) {
      if (!replicas.contains(e.getValue())) replicas.add(e.getValue());
      if (replicas.size() == REPLICATION_FACTOR) break;
  }
  return replicas;  // [primary, replica1, replica2]
```

---

### 💻 Code Example

```java
// Simple consistent hash ring implementation
import java.util.TreeMap;

public class ConsistentHashRing {

    private final TreeMap<Long, String> ring = new TreeMap<>();
    private final int virtualNodesPerNode;

    public ConsistentHashRing(int virtualNodesPerNode) {
        this.virtualNodesPerNode = virtualNodesPerNode;
    }

    public void addNode(String node) {
        for (int i = 0; i < virtualNodesPerNode; i++) {
            long hash = hash(node + "#vnode-" + i);
            ring.put(hash, node);
        }
    }

    public void removeNode(String node) {
        for (int i = 0; i < virtualNodesPerNode; i++) {
            ring.remove(hash(node + "#vnode-" + i));
        }
    }

    public String getNode(String key) {
        if (ring.isEmpty()) throw new IllegalStateException("No nodes in ring");
        long keyHash = hash(key);
        // Find first node clockwise from keyHash
        Map.Entry<Long, String> entry = ring.ceilingEntry(keyHash);
        if (entry == null) entry = ring.firstEntry(); // Wrap around
        return entry.getValue();
    }

    private long hash(String value) {
        // MurmurHash3 or FNV-1a recommended for better distribution
        // Simple demo: MD5 truncated to long
        try {
            byte[] digest = MessageDigest.getInstance("MD5").digest(value.getBytes());
            return ((long)(digest[3] & 0xFF) << 24) |
                   ((long)(digest[2] & 0xFF) << 16) |
                   ((long)(digest[1] & 0xFF) << 8)  |
                   ((long)(digest[0] & 0xFF));
        } catch (Exception e) { throw new RuntimeException(e); }
    }
}

// Usage with Spring Cache routing
@Service
public class CacheRouter {
    private final ConsistentHashRing ring;

    public CacheRouter(List<String> cacheNodes) {
        this.ring = new ConsistentHashRing(150); // 150 vnodes per node
        cacheNodes.forEach(ring::addNode);
    }

    public String route(String cacheKey) {
        return ring.getNode(cacheKey); // Returns the server address for this key
    }
}
```

---

### ⚖️ Comparison Table

| Sharding Method | Keys Remapped on Node Add | Hot Spots | Implementation |
|---|---|---|---|
| **Modulo (hash % N)** | All (~100%) | Possible | O(1) lookup |
| **Consistent hashing** | ~K/N (minimal) | Possible without vnodes | O(log N) lookup |
| **+ Virtual nodes** | ~K/N | Minimal (uniform) | O(log N) + memory |
| **Rendezvous hashing** | ~K/N (all nodes) | Minimal | O(N) lookup |

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ RING          │ Nodes and keys → positions on [0, 2³²)       │
│ LOOKUP        │ Key → next node clockwise                    │
│ ADD NODE      │ Only ~K/N keys remapped (neighbor's slice)   │
│ REPLICATION   │ Key → next R nodes clockwise                 │
│ HOT SPOTS     │ Fix with virtual nodes (V positions/node)    │
│ SYSTEMS       │ Cassandra, DynamoDB, Riak, Memcached         │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** A Cassandra cluster with 6 nodes uses consistent hashing (no vnodes, V=1 per node). During an incident, one node is removed. (1) What fraction of data must be moved? To which node? (2) The removed node owned a very large arc (200° out of 360°). After removal, which node is overloaded? How does enabling vnodes (V=150) help? (3) DynamoDB hides all of this behind auto-scaling — its partition layer transparently splits hot partitions and moves data. What is the trade-off vs. manual vnode tuning in Cassandra?
