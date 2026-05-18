---
version: 2
layout: default
title: "Consistent Hashing in Cache"
parent: "Caching"
grand_parent: "Technical Mastery"
nav_order: 32
permalink: /technical-mastery/caching/consistent-hashing/
id: CCH-016
category: Caching
difficulty: ★★★
depends_on: Distributed Cache, Redis Cluster
used_by: System Design, Distributed Systems, Caching
related: Redis Cluster, Distributed Cache, Memcached vs Redis
tags:
  - caching
  - consistent-hashing
  - vnodes
  - distribution
  - deep-dive
---

⚡ TL;DR - Consistent hashing distributes cache keys across N nodes such that when a node is added or removed, **only K/N keys are remapped** (minimal disruption) - compared to simple modulo hashing where adding/removing a node causes ALL keys to remap; virtual nodes (vnodes) improve load balance on the ring; Redis Cluster uses a related concept (16,384 hash slots) rather than pure consistent hashing.

| #492            | Category: Caching                                    | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------- | :-------------- |
| **Depends on:** | Distributed Cache, Redis Cluster                     |                 |
| **Used by:**    | System Design, Distributed Systems, Caching          |                 |
| **Related:**    | Redis Cluster, Distributed Cache, Memcached vs Redis |                 |

---

### 🔥 The Problem This Solves

**MODULO HASHING IS FRAGILE:**
Simple partitioning: `node = hash(key) % N`. With N=3 nodes: key "product:42" → hash % 3 = 1 → Node 1. Works perfectly. Now a node fails - N becomes 2. `hash(key) % 2` for EVERY key in the system: most keys map to different nodes than before. Cache miss rate: spikes to ~67% (2/3 of keys now go to "wrong" node, causing misses). The entire cache becomes ineffective during node transitions.

**DISTRIBUTED CACHE NODES COME AND GO:**
Production systems scale horizontally (add nodes at peak), experience failures (remove failed nodes), and undergo planned maintenance. Every node change should cause minimal disruption - only keys that were on the added/removed node should remap.

---

### 📘 Textbook Definition

**Consistent Hashing** is a distributed hashing scheme where both cache nodes and cache keys are mapped to positions on a conceptual **hash ring** (a circle, values 0 to 2³²-1). A key's "home" node is the **first node clockwise** from the key's position on the ring. Key property: when a node is added, only the keys between the new node and its predecessor on the ring remap (K/N remapping). When a node is removed, only its keys remap to its successor. All other keys are unaffected.

**Virtual Nodes (vnodes)**: instead of placing each physical node once on the ring, each node is placed at many positions (100-200 vnodes). Benefits: (1) more even key distribution (without vnodes, random placement may unevenly distribute keys); (2) when a node fails, its load is evenly spread across all remaining nodes (not just the single successor node). **Ketama algorithm**: the most common consistent hashing implementation used by Memcached clients; uses MD5(node:virtual_node_num) as the node position.

**Redis Cluster approach**: Redis Cluster does NOT use consistent hashing directly. Instead, it uses **16,384 predefined hash slots** (a fixed-size hash ring). Each key maps to a slot: `CRC16(key) % 16384`. Slots are assigned to nodes. When nodes are added/removed, slot assignments are migrated - only keys in migrated slots are affected. This achieves the same minimal-disruption property as consistent hashing but with a deterministic, fixed slot count.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Consistent hashing maps keys and nodes to a ring; add/remove a node → only keys on that segment remap; all others stay - minimal cache disruption.

**One analogy:**

> Imagine a clock face (the hash ring). N servers are placed at different hours (1 o'clock, 5 o'clock, 9 o'clock for N=3). Each key is placed at a time position (based on its hash). The key's server is the NEXT server clockwise. Add a new server at 3 o'clock: only keys between 1 o'clock and 3 o'clock are reassigned to the new server (1/4 of keys if evenly distributed). All other keys (3-9, 9-1) are unaffected. Compare to modulo: adding any server → ALL keys reassigned.

- "Clock face" → hash ring (0 to 2³²)
- "Servers at hour positions" → nodes at hash positions
- "Key at a time position" → key's hash position on ring
- "Next server clockwise" → first node clockwise from key's position
- "Only 1/4 of keys reassigned when adding 3 o'clock server" → K/N remapping

**One insight:**
Pure consistent hashing is rarely used directly in practice. Most distributed caches use a variant: Redis Cluster uses fixed hash slots (16,384), Amazon DynamoDB uses consistent hashing internally but abstracts it from users, and Memcached client libraries implement ketama consistent hashing. The key benefit (minimal rehashing on node change) is universal across all variants. When designing a system, you typically choose a technology (Redis Cluster, Memcached, Cassandra) that handles consistent hashing internally - you don't implement it yourself.

---

### 🔩 First Principles Explanation

**MODULO HASHING vs. CONSISTENT HASHING - THE DISRUPTION COMPARISON:**

```
MODULO HASHING (N=3 nodes):
Key → hash(key) % 3 = 0,1, or 2

Node assignments:
  "product:1"  → hash % 3 = 0 → Node A
  "product:2"  → hash % 3 = 1 → Node B
  "product:3"  → hash % 3 = 2 → Node C
  "product:4"  → hash % 3 = 0 → Node A
  "product:5"  → hash % 3 = 1 → Node B
  "product:6"  → hash % 3 = 2 → Node C

Node C fails → N=2:
  "product:1"  → hash % 2 = 0 → Node A ✓ (unchanged)
  "product:2"  → hash % 2 = 0 → Node A ✗ (was Node B)
  "product:3"  → hash % 2 = 1 → Node B ✗ (was Node C)
  "product:4"  → hash % 2 = 0 → Node A ✓ (unchanged)
  "product:5"  → hash % 2 = 1 → Node B ✓ (unchanged)
  "product:6"  → hash % 2 = 0 → Node A ✗ (was Node C)

Keys changed: 3 of 6 = 50% remapped → 50% cache miss rate
  spike

CONSISTENT HASHING (3 nodes on ring):
Ring positions (0-360°):
  Node A: 0°
  Node B: 120°
  Node C: 240°

Key positions (hash(key) % 360):
  "product:1": 10° → Node A (next clockwise from 10° is
    120°? No - 0°-120° → Node A)

Wait: key goes to FIRST NODE CLOCKWISE from its position:
  10° → next node clockwise = Node A (at 0°? No -
    clockwise from 10° is Node B at 120°)

Actually: "product:1" at 10° → clockwise → Node A at 0° is
  BEHIND...
Let's use proper ring: clockwise means increasing angle,
  wrapping at 360°.
From 10°: next clockwise node = Node B at 120°.

Let me use concrete positions:
  Node A: position 0
  Node B: position 100 (out of 360)
  Node C: position 200

  "product:1": position 50 → clockwise → Node B (100) ←
    first node clockwise
  "product:2": position 150 → clockwise → Node C (200)
  "product:3": position 250 → clockwise → wrap → Node A (0
    → 360)
  "product:4": position 80 → clockwise → Node B (100)
  "product:5": position 120 → clockwise → Node C (200)
  "product:6": position 300 → clockwise → wrap → Node A

Node C (200) fails:
  "product:1": position 50 → clockwise → Node B (100) -
    SAME ✓
  "product:2": position 150 → clockwise → Node A (360/0) -
    CHANGED (was Node C)
  "product:3": position 250 → clockwise → Node A (360/0) -
    SAME (was also Node A)
  "product:4": position 80 → clockwise → Node B - SAME ✓
  "product:5": position 120 → clockwise → Node A - CHANGED
    (was Node C)
  "product:6": position 300 → clockwise → Node A - SAME ✓

Keys changed: 2 of 6 = 33% (approximately K/N = 1/3)
vs. modulo: 50% changed

With virtual nodes (100 vnodes per server):
  Even distribution → closer to exactly 1/3 remapped on
    node removal
```

**JAVA CONSISTENT HASHING WITH VIRTUAL NODES:**

```java
// Custom consistent hash ring (illustrative - use production
// libraries in practice)
public class ConsistentHashRing<T> {
    private final TreeMap<Long, T> ring = new TreeMap<>();
    private final int virtualNodes;
    private final MessageDigest md5;

    public ConsistentHashRing(int virtualNodes) {
        this.virtualNodes = virtualNodes;
        this.md5 = MessageDigest.getInstance("MD5");
    }

    public void addNode(T node) {
        for (int i = 0; i < virtualNodes; i++) {
            // Hash the node with virtual node index to get ring
            // positions
            long hash = hash(node.toString() + ":" + i);
            ring.put(hash, node);
        }
    }

    public void removeNode(T node) {
        for (int i = 0; i < virtualNodes; i++) {
            long hash = hash(node.toString() + ":" + i);
            ring.remove(hash);
        }
    }

    public T getNode(String key) {
        if (ring.isEmpty()) throw new IllegalStateException(
            "No nodes in ring");
        long hash = hash(key);
        // Find the first node clockwise (≥ hash); wrap to first node
        // if none found
        Map.Entry<Long, T> entry = ring.ceilingEntry(hash);
        if (entry == null) entry = ring.firstEntry();
        return entry.getValue();
    }

    private long hash(String input) {
        byte[] digest =
            md5.digest(input.getBytes(StandardCharsets.UTF_8));
        // Use first 4 bytes as a long (unsigned)
        return ((long)(digest[3] & 0xFF) << 24) |
               ((long)(digest[2] & 0xFF) << 16) |
               ((long)(digest[1] & 0xFF) << 8)  |
               ((long)(digest[0] & 0xFF));
    }
}

// Usage (illustrative - use Jedis cluster or Lettuce cluster in
// practice):
ConsistentHashRing<String> ring = new ConsistentHashRing<>(150);
// 150 vnodes
ring.addNode("redis-node-1:6379");
ring.addNode("redis-node-2:6379");
ring.addNode("redis-node-3:6379");

String node = ring.getNode("product:42");
// → "redis-node-2:6379" (deterministic)
// Connect to this specific Redis node and GET/SET "product:42"
```

**MEMCACHED WITH KETAMA CONSISTENT HASHING (via SpyMemcached / Xmemcached):**

```java
// Xmemcached: built-in consistent hashing (ketama algorithm)
@Bean
public MemcachedClient memcachedClient() throws Exception {
    MemcachedClientBuilder builder = new XMemcachedClientBuilder(
        AddrUtil.getAddresses(
            "memcached-1:11211 memcached-2:11211 memcached-3:11211")
    );

    // Use ketama hashing (consistent hashing for Memcached)
    builder.setSessionLocator(new KetamaMemcachedSessionLocator());

    return builder.build();
}
// Under the hood: Ketama maps each key to a consistent node
// Adding/removing a node: only 1/N of keys are remapped
```

**REDIS CLUSTER HASH SLOTS (NOT PURE CONSISTENT HASHING):**

```
Redis Cluster: 16,384 hash slots (fixed)
Key → slot: CRC16(key) % 16384

3-node cluster:
  Node 1: slots 0-5460
  Node 2: slots 5461-10922
  Node 3: slots 10923-16383

Add Node 4:
  Reassign: ~4096 slots from each of nodes 1,2,3 → Node 4
  Only keys in reassigned slots are migrated
  ~1/4 of keys remapped ← same minimal disruption as
    consistent hashing

Differences from pure consistent hashing:
1. Fixed slot count (16,384) - always the same regardless
  of node count
2. Manual slot assignment (admin or automatic resharding)
3. Predictable hash space (CRC16 + modulo, not arbitrary
  ring positions)
4. Supports hash tags: {user:42}:profile → hashes on
  "user:42" → co-locate keys

Consistent hashing uses:
  - Memcached (ketama algorithm in clients)
  - Cassandra (token ranges - a form of consistent hashing)
  - Amazon DynamoDB (internal consistent hashing)

Redis Cluster uses: fixed hash slots (more predictable,
  easier to manage)
```

---

### 🧪 Thought Experiment

**UNEVEN DISTRIBUTION WITHOUT VIRTUAL NODES:**

3 physical nodes, randomly placed on ring:

- Node A: position 10 (out of 100)
- Node B: position 15 (very close to A!)
- Node C: position 50

Key distribution:

- Keys with positions 10-15 (5%) → Node B
- Keys with positions 15-50 (35%) → Node C
- Keys with positions 50-10 (wrapping = 60%) → Node A

Node A handles 60% of keys! Node B handles only 5%. Highly uneven.

**With 150 virtual nodes per server:**
Each server is placed at 150 random positions. The ring has 450 positions total, evenly spread. Each server handles ~1/3 of the ring on average, with small variance. Adding a server: displaces 1/4 of positions from existing servers = 1/4 of keys remap = correct K/N behavior.

---

### 🧠 Mental Model / Analogy

> Consistent hashing is like a rotating conveyor belt (the ring) with buckets (nodes) placed at intervals. Each item (key) is placed on the belt at a position based on its weight (hash). Each item slides clockwise until it falls into the nearest bucket. Remove a bucket: items that were in that bucket slide further clockwise into the next bucket. Items in other buckets are unaffected. Add a bucket between two existing ones: only items that were sliding past that position (and would have gone to the next bucket) now stop at the new bucket. All other items are unaffected.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Consistent hashing → nodes and keys on a ring → key goes to first clockwise node → only 1/N of keys remap on node change (vs. all keys with modulo). Redis Cluster uses hash slots (16,384) - a variant of the same principle.

**Level 2:** Virtual nodes (100-200 per server) → even distribution even if physical nodes are randomly placed on ring. TreeMap (Java) models the ring: `ceilingEntry(hash)` = first clockwise node. For Memcached: use Xmemcached/SpyMemcached with `KetamaMemcachedSessionLocator`. For Redis Cluster: client (Lettuce) handles routing automatically.

**Level 3:** Replication in consistent hashing: on write, replicate to the NEXT N clockwise nodes (N = replication factor). On a node failure, reads fall through to the replica. Cassandra uses this exact pattern (N=3 replicas, writes go to coordinator + 2 clockwise neighbors). For cache-only use: replication is optional (on failure, accept cache miss, serve from DB). Rendezvous hashing (HRW - Highest Random Weight): alternative to ring-based consistent hashing; each key is hashed with each candidate node; the node with the highest score wins. Simpler to implement, equally minimal rehashing, but requires iterating all nodes per key (O(N) lookup vs O(log N) for TreeMap ring).

**Level 4:** The choice of consistent hashing algorithm affects the tail latency of the routing operation itself. TreeMap ring lookup: O(log N). Rendezvous hashing: O(N). For N=10 nodes, this difference is negligible (O(log 10) ≈ 3 operations vs. O(10)). For N=1000 nodes, rendezvous hashing's O(1000) lookup adds measurable latency per cache request. Consistent hashing ring's O(log 1000) = 10 operations is more scalable. With virtual nodes, the ring size is N_nodes × N_vnodes = 1000 × 150 = 150,000 TreeMap entries. `ceilingEntry()` on a 150K-entry TreeMap: ~17 operations - still O(log N_vnodes). Redis Cluster avoids this entirely: `CRC16(key) % 16384` is a fixed O(1) computation + one array lookup. This is why Redis Cluster is faster to route than custom consistent hashing implementations.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ CONSISTENT HASHING RING                              │
├──────────────────────────────────────────────────────┤
│                                                      │
│           Node A (position 0)                        │
│        ↗                 ↖                           │
│    Node C               ...                          │
│    (pos 270)         ring (0-360°)                   │
│        ↘                 ↗                           │
│           Node B (pos 120)                           │
│                                                      │
│  Key "product:42" at position 180°:                  │
│  [CONSISTENT ← YOU ARE HERE: clockwise lookup]       │
│  Next clockwise from 180° → Node C (270°)            │
│                                                      │
│  Remove Node C:                                      │
│  "product:42" at 180° → next clockwise → Node A (0°/360°)
│  Only keys in 120°-270° range remap (1/3 of ring)   │
│  Keys in other ranges: UNCHANGED ✓                   │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
REDIS CLUSTER ROUTING (hash slots variant):
GET product:42
→ Lettuce: CRC16("product:42") % 16384 = 7842
→ Cluster topology (cached): slot 7842 → Node 2
→ Lettuce sends GET to Node 2 directly

Add Node 4 to cluster (reshard):
→ Admin moves slots 5000-6499 from Node 2 to Node 4
→ Keys in those slots migrated live (no downtime)
→ Other keys (including slot 7842) → unchanged ←
  consistent hashing benefit

Node 2 fails:
→ Replica for Node 2 promoted to primary (30s failover)
→ Lettuce: receives MOVED redirects to new primary
→ Keys on other nodes: unaffected ✓

Routing for "product:42" (slot 7842) after reshard:
→ CRC16("product:42") % 16384 = 7842 - unchanged
  computation
→ Topology update: slot 7842 still on Node 2 (not
  migrated) → still routes to Node 2
```

---

### ⚖️ Comparison Table

| Aspect                     | Modulo Hashing | Consistent Hashing        | Redis Cluster Slots            |
| -------------------------- | -------------- | ------------------------- | ------------------------------ |
| Node add/remove disruption | All keys remap | Only K/N keys remap       | Only keys in migrated slots    |
| Load balance               | Even (math)    | Uneven without vnodes     | Controllable (slot assignment) |
| Lookup complexity          | O(1)           | O(log N × vnodes)         | O(1): CRC16 + array            |
| Implementation             | Simple         | Medium (TreeMap + vnodes) | Built into Redis               |
| Multi-key operations       | N/A            | N/A                       | Hash tags required for MGET    |

---

### ⚠️ Common Misconceptions

| Misconception                                         | Reality                                                                                                                                                                                                           |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Redis Cluster uses consistent hashing"               | Redis Cluster uses a FIXED HASH SLOT scheme (16,384 slots + CRC16), not the traditional ring-based consistent hashing. The outcome (minimal disruption on node change) is similar, but the mechanism is different |
| "Consistent hashing means even load distribution"     | Without virtual nodes, physical node positions on the ring may be very uneven, causing some nodes to hold much more data than others. Virtual nodes (100-200 per physical node) achieve even distribution         |
| "Consistent hashing prevents cache misses on reshard" | Consistent hashing minimizes cache invalidation but does NOT prevent it entirely. Keys that remap to a different node after adding/removing a node are cache misses until they're re-fetched from the database    |

---

### 🚨 Failure Modes & Diagnosis

**1. Hot Spot - One Node Handles Most Traffic**

**Symptom:** Redis node monitoring shows Node 1 handles 60% of requests; Nodes 2 and 3 handle 20% each.

**Root Cause:** Consistent hashing ring with few virtual nodes. Physical node positions are unlucky - Node 1 claims a large arc of the ring.

**Diagnosis:**

```bash
# Check key distribution in Redis Cluster
redis-cli --cluster info redis-node-1:6379
# Look for: keys per slot - should be roughly equal across nodes

# Slot distribution (should be ~5461 slots per node for 3 nodes)
redis-cli -c CLUSTER NODES | awk '{print $3, $9}' | sort
# Uneven slot count per node → redistribute with reshard
```

**Fix (Redis Cluster):**

```bash
# Rebalance slots across nodes (Redis Cluster can auto-rebalance)
redis-cli --cluster rebalance redis-node-1:6379
# Moves slots so each node has ~equal slot count

# For custom consistent hashing: increase virtual nodes (100→200)
ConsistentHashRing ring = new ConsistentHashRing(200);
// More vnodes → better distribution
```

---

### 🔗 Related Keywords

**Prerequisites:** Distributed Cache, Redis Cluster

**Builds On This:** System Design, Distributed Systems

**Related:** Redis Cluster, Distributed Cache, Memcached vs Redis

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT         │ Keys + nodes on ring; key → first clockwi│
│ DISRUPTION   │ K/N keys remap on node add/remove        │
│ vs MODULO    │ Modulo: ALL keys remap (catastrophic)    │
│ VIRTUAL NODES│ 100-200/server → even distribution       │
│ REDIS CLUSTER│ 16,384 hash slots; CRC16(key) % 16384    │
│ MEMCACHED    │ Ketama algorithm (consistent hashing)    │
│ LOOKUP       │ TreeMap ceilingEntry → O(log N)          │
│ HASH TAGS    │ {user:42}: → same slot for co-located key│
│ RESHARD      │ Slot migration: live, no downtime        │
│ ONE-LINER    │ "Ring + clockwise lookup = only 1/N keys │
│              │  remap when topology changes"            │
│ NEXT EXPLORE │ Redis Cluster → Memcached vs Redis       │
└─────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C - Design Question) Design a distributed caching layer for 10M users where user session data must be co-located with user profile data (multi-key operations on both within a single request). Both datasets together are 500GB. You have 10 cache nodes. Design the key naming strategy, hash ring placement, and virtual node count to achieve: even distribution, minimal disruption on node failure, and support for multi-key operations.

**Q2.** (TYPE A - Algorithm) Trace through consistent hashing for this scenario: 4 nodes at ring positions 0, 90, 180, 270. Key "session:XYZ" hashes to position 200. Node at position 180 fails. (a) Which node does "session:XYZ" map to before the failure? (b) Which node after the failure? (c) If there are 1,000 keys uniformly distributed on the ring, approximately how many remap when the node at 180 fails? (d) Would this number change with 100 virtual nodes per physical node?
