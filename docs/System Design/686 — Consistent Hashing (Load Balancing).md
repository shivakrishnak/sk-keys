---
layout: default
title: "Consistent Hashing (Load Balancing)"
parent: "System Design"
nav_order: 686
permalink: /system-design/consistent-hashing/
number: "686"
category: System Design
difficulty: ★★★
depends_on: "Load Balancing, Round Robin"
used_by: "Sticky Sessions, Sharding"
tags: #advanced, #distributed, #algorithm, #architecture, #performance
---

# 686 — Consistent Hashing (Load Balancing)

`#advanced` `#distributed` `#algorithm` `#architecture` `#performance`

⚡ TL;DR — **Consistent Hashing** maps requests to servers on a virtual ring, so adding or removing a server only remaps ~1/N of keys instead of remapping everything — critical for cache efficiency in distributed caches.

| #686            | Category: System Design     | Difficulty: ★★★ |
| :-------------- | :-------------------------- | :-------------- |
| **Depends on:** | Load Balancing, Round Robin |                 |
| **Used by:**    | Sticky Sessions, Sharding   |                 |

---

### 📘 Textbook Definition

**Consistent Hashing** is a distributed hashing technique that maps both servers and request keys onto the same circular hash space (a "ring"). Each server is assigned one or more positions on the ring based on `hash(server_id)`. Each request key is mapped to a position on the ring via `hash(key)`, then routed to the first server clockwise from that position. When a server is added or removed, only the keys that mapped to that server's segment of the ring are remapped — on average 1/N of all keys, where N is the number of servers. Traditional modular hashing (`server = hash(key) % N`) remaps nearly all keys when N changes, causing cache invalidation storms. Consistent Hashing is used by: Amazon DynamoDB (partition routing), Apache Cassandra (token ring), Memcached clients (libmemcached), Redis Cluster, and Envoy's ring hash load balancer.

---

### 🟢 Simple Definition (Easy)

Consistent Hashing puts servers and requests on an imaginary circle. Each request "belongs" to the nearest server clockwise on the circle. If you add or remove a server, only requests near that server's spot on the circle need to be redirected — not everyone else's. Compare to modular hashing: if you change the number of servers, almost every request gets a different server (cache miss storm).

---

### 🔵 Simple Definition (Elaborated)

Memcached cluster: 4 servers caching user profile data. With modular hashing: `server = hash(userId) % 4`. You add a 5th server: `hash(userId) % 5` gives different results for ~80% of users → 80% of cache entries must be fetched from database (cache miss storm). With Consistent Hashing: adding server 5 only disrupts the ~20% of keys that were between server 4 and server 5 on the ring. 80% of cache entries remain valid on their original servers. Cache hit rate barely changes during scaling.

---

### 🔩 First Principles Explanation

**The modular hashing problem — why it catastrophically remaps on server changes:**

```
MODULAR HASHING: server = hash(key) % N

  N=3 servers: {A, B, C}
  hash("user:1234") % 3 = 1 → Server B
  hash("user:5678") % 3 = 2 → Server C
  hash("user:9012") % 3 = 0 → Server A

  ADD Server D (N=4):
  hash("user:1234") % 4 = 3 → Server D  ← was B
  hash("user:5678") % 4 = 1 → Server B  ← was C
  hash("user:9012") % 4 = 2 → Server C  ← was A

  ALL THREE keys remapped. Statistically: (1 - N/(N+1)) ≈ 75% remapped.
  Cache: all data on old servers → wrong server → miss → database load spikes

  For a 10M-key cache adding 1 server: ~7.5M cache misses hitting the DB.
  Under traffic: DB overwhelmed → cascade failure.

CONSISTENT HASHING: remaps only 1/N of keys on server changes

  Hash ring: 0 to 2^32 (positions)
  Server A → hash("server-A") = 10
  Server B → hash("server-B") = 30
  Server C → hash("server-C") = 70
  Ring (sorted): 0..10(A)..30(B)..70(C)..100(wrap to A)

  hash("user:1234") = 15 → clockwise → Server B (at 30)
  hash("user:5678") = 45 → clockwise → Server C (at 70)
  hash("user:9012") = 80 → clockwise → wraps → Server A (at 10+100=110)

  ADD Server D at position 50:
  Ring: 0..10(A)..30(B)..50(D)..70(C)..100

  hash("user:1234") = 15 → Server B (unchanged)
  hash("user:5678") = 45 → NOW Server D (was C: D inserted between B and C)
  hash("user:9012") = 80 → Server A (unchanged)

  Only "user:5678" remapped (it was between B=30 and C=70, D inserted at 50).
  All other keys: unchanged. ~1/N = ~25% remapped.
```

**Virtual nodes — solving uneven distribution:**

```
PROBLEM WITH BASIC CONSISTENT HASHING:
  3 servers, random hash positions:
  A at position 10, B at position 12, C at position 60
  Server A: handles range 60-10 = 50% of ring
  Server B: handles range 10-12 = 2% of ring
  Server C: handles range 12-60 = 48% of ring

  Uneven! Server B almost idle, Server A/C overloaded.

VIRTUAL NODES (vnodes):
  Each physical server gets V virtual nodes (positions on ring).
  Typical V: 100-200 vnodes per server.

  Server A: positions {10, 45, 78, 23, 91, ...} (100 positions)
  Server B: positions {15, 52, 83, 37, 66, ...} (100 positions)
  Server C: positions {8, 31, 70, 18, 95, ...}  (100 positions)

  300 total positions → each server handles ~100/300 = 33% of ring.
  With 100 vnodes: standard deviation of load ≈ 10% (acceptable).
  With 1 vnode: standard deviation ≈ 100% (very uneven).

  ADD Server D: gets 100 vnodes spread across ring.
  Each existing server loses ~25 of its 100 vnodes to D.
  Load redistribution: uniform (~25% of keys moved).
```

**Cassandra's token ring — consistent hashing in production:**

```
Cassandra cluster: 3 nodes, replication factor 3
Token ranges (simplified):
  Node A: owns tokens 0-33 (primary + replica for 33-66, 66-100 ranges)
  Node B: owns tokens 34-66
  Node C: owns tokens 67-100

Write: hash(partition_key) = 45 → Node B is primary coordinator
  Node B writes → replicates to Node C (next on ring) → Node A (next)
  All 3 nodes have this data (RF=3)

Node B fails:
  Node A + C still have all B's replicas (RF=3 → no data loss)
  Reads for token 45: routed to Node C (has replica) or Node A (has replica)

New node added:
  Gets token range 17-33 (split from Node A)
  Node A streams its data for range 17-33 to new node
  Only A's data for 17-33 moved — all other data unchanged

# nodetool ring: shows token assignments
# nodetool status: shows load distribution per node
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Consistent Hashing:

- Adding/removing a server from a distributed cache: massive cache miss storm (75-80% remapping)
- Cache miss storm → all misses hit the database → DB overload → cascade failure
- Scale events are dangerous: must do them at low-traffic times

WITH Consistent Hashing:
→ Adding/removing a server: only ~1/N keys remapped
→ Cache hit rate barely changes during scaling events
→ Scale events are safe to do at any time, including under load

---

### 🧠 Mental Model / Analogy

> A circular city directory where street addresses are assigned to delivery drivers. Each driver owns a segment of the circle. A package goes to the driver whose segment starts at or after the package's address. If a driver is added to cover a new neighbourhood, only packages in that neighbourhood change drivers — everyone else's delivery route stays the same. With modular hashing (traditional): adding one driver re-routes almost every package.

"Delivery drivers" = backend servers / cache nodes
"Addresses" = hash values of request keys
"Driver's segment" = server's arc on the hash ring
"Adding a driver" = adding a server (only nearby packages rerouted)

---

### ⚙️ How It Works (Mechanism)

**Java consistent hash implementation using TreeMap:**

```java
public class ConsistentHashRouter<T> {
    private final TreeMap<Long, T> ring = new TreeMap<>();
    private final int virtualNodes;

    public ConsistentHashRouter(List<T> nodes, int virtualNodes) {
        this.virtualNodes = virtualNodes;
        nodes.forEach(this::addNode);
    }

    public void addNode(T node) {
        for (int i = 0; i < virtualNodes; i++) {
            long hash = hash(node.toString() + "#vn" + i);
            ring.put(hash, node);
        }
    }

    public void removeNode(T node) {
        for (int i = 0; i < virtualNodes; i++) {
            long hash = hash(node.toString() + "#vn" + i);
            ring.remove(hash);
        }
    }

    public T getNode(String key) {
        if (ring.isEmpty()) throw new IllegalStateException("No nodes");
        long hash = hash(key);
        // Find first node clockwise from hash position:
        Map.Entry<Long, T> entry = ring.ceilingEntry(hash);
        // Wrap around ring if past last node:
        if (entry == null) entry = ring.firstEntry();
        return entry.getValue();
    }

    private long hash(String key) {
        // MurmurHash3 or MD5 for good distribution:
        return Math.abs(key.hashCode());  // simplified; use MurmurHash in prod
    }
}

// Usage:
ConsistentHashRouter<String> router = new ConsistentHashRouter<>(
    List.of("cache-1:6379", "cache-2:6379", "cache-3:6379"),
    150  // 150 virtual nodes per server
);
String cacheNode = router.getNode("user:42");  // deterministic routing
```

---

### 🔄 How It Connects (Mini-Map)

```
Load Balancing        Round Robin / Modular Hashing
(routing to backends) (fails on server add/remove: full remap)
        │                          │
        └──────────┬───────────────┘
                   ▼ (solves the remap problem)
        Consistent Hashing  ◄──── (you are here)
        (ring-based: only 1/N remap on change)
                   │
        ┌──────────┴──────────────┐
        ▼                         ▼
Sticky Sessions               Sharding
(session affinity)            (data partitioning)
```

---

### 💻 Code Example

**Redis Cluster — consistent hashing in action:**

```bash
# Redis Cluster uses consistent hashing (hash slots: 16384 slots)
# Each node owns a range of slots: hash(key) % 16384 → slot → node

redis-cli cluster info
# cluster_state: ok
# cluster_slots_assigned: 16384
# cluster_known_nodes: 6 (3 primary + 3 replica)

# Key routing:
redis-cli -c cluster keyslot "user:1234"
# → 3847 (slot number)
redis-cli -c cluster nodes | grep "3847"
# → 10.0.0.1:6379 owns slots 0-5460 (includes 3847)

# Add a new node: reshards ~1/4 of slots (Consistent Hashing property)
redis-cli --cluster add-node 10.0.0.7:6379 10.0.0.1:6379
redis-cli --cluster reshard 10.0.0.1:6379
# Only migrates slots from existing nodes — other keys unaffected
```

---

### ⚠️ Common Misconceptions

| Misconception                                               | Reality                                                                                                                                                                                                                                                                                        |
| ----------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Consistent Hashing distributes load perfectly evenly        | With few virtual nodes, distribution can be highly uneven. 150+ vnodes per server are needed for acceptably uniform distribution (≤10% imbalance). Cassandra and Dynamo-style systems use 256 vnodes                                                                                           |
| Consistent Hashing is only for caches                       | Consistent Hashing is used for: distributed cache routing (Memcached, Redis), database sharding (Cassandra, DynamoDB), service routing (Envoy ring_hash), and partition assignment (Kafka partition → consumer mapping)                                                                        |
| Consistent Hashing prevents ALL cache misses during scaling | It minimises remapping to ~1/N, but the remapped keys still miss on their new server until re-cached from the database. The difference: 1/N misses (manageable) vs N/(N+1) misses (cache miss storm)                                                                                           |
| Removing a server is the same as adding one                 | Removing: all of the removed server's keys must move to successor nodes (cold start for 1/N of keys). Adding: 1/N of existing keys move from existing nodes to the new node (those servers get cache relief). Both remap ~1/N, but removal requires successor nodes to absorb load immediately |

---

### 🔥 Pitfalls in Production

**Hot key problem — consistent hashing can't distribute a single key:**

```
PROBLEM:
  Consistent Hashing distributes KEYS across nodes.
  But a single hot key ("product:viral-item-12345") → always one node.
  That one node handles all traffic for the viral product.

  During flash sale: 100,000 requests/sec for "product:viral-item-12345"
  All hit cache-node-2 (hash("product:viral-item-12345") maps there).
  Cache-node-2: overwhelmed → returns errors → all misses hit DB → cascade.

  Other 7 cache nodes: idle.
  Consistent Hashing: doing its job correctly.
  The problem: traffic distribution is by key, not by request count.

SOLUTIONS:
  1. Key replication with random suffix:
     Write: cache.set("product:viral#1", data) + cache.set("product:viral#2", data)
            ... × 10 replicas on different nodes
     Read: cache.get("product:viral#" + random(1,10))
     → 10x distribution of reads across 10 nodes

  2. Local in-process cache (L1 cache) per app instance:
     @Cacheable(value = "product-local", key = "#id")  // Caffeine (local JVM)
     → Hot product cached in every JVM → never hits distributed cache for reads
     TTL: 5 seconds (stale for 5s is acceptable for product display)

  3. Read-through cache at edge (CDN):
     Hot products cached in CloudFront/Fastly → never reaches origin cache
```

---

### 🔗 Related Keywords

- `Load Balancing` — Consistent Hashing is a routing algorithm for load balancers
- `Round Robin` — the simpler alternative that fails on server changes
- `Sticky Sessions` — session affinity can use consistent hashing to route by session ID
- `Sharding (System)` — Consistent Hashing is used to determine which shard owns a key
- `Virtual Nodes` — technique to improve distribution uniformity in the hash ring

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Ring-based hashing: add/remove server     │
│              │ remaps only 1/N keys (not all keys)       │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Distributed cache routing; cache affinity │
│              │ needed; frequent server add/remove        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Hot key problem: one key gets all traffic │
│              │ (use key replication instead)             │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Adding a delivery driver only re-routes  │
│              │  packages in their new neighbourhood."    │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Virtual Nodes → Sharding → Hot Shard      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Memcached cluster uses Consistent Hashing with 100 virtual nodes per server. The cluster has 5 servers. Server 3 fails unexpectedly (hardware failure). Describe: (a) what fraction of cached keys are affected, (b) where those keys are now routed, (c) how the load on Server 3's successor servers changes, and (d) whether the cluster can handle the redistributed load if all servers were previously running at 70% capacity before the failure.

**Q2.** You are designing a consistent hashing implementation for a distributed cache with heterogeneous servers: Server A (16GB RAM, can hold 4M items), Server B (4GB RAM, 1M items), Server C (8GB RAM, 2M items). Design the virtual node allocation to make load proportional to capacity. Calculate how many virtual nodes each server should receive if the total is 1000, and explain what happens to load balance as the cluster grows from 3 to 30 servers (does the proportional allocation become more or less accurate?).
