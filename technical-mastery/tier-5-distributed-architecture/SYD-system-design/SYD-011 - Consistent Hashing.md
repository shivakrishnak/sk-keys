---
id: SYD-011
title: Consistent Hashing
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-008
used_by: SYD-031, SYD-052
related: SYD-008, SYD-009, SYD-010, SYD-031, SYD-052
tags:
  - architecture
  - distributed-systems
  - caching
  - performance
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 11
permalink: /technical-mastery/syd/consistent-hashing/
---

⚡ TL;DR - Consistent hashing assigns both servers
and keys to a ring, so adding or removing a server
only remaps ~1/N keys (not all keys), making it
the foundation of scalable distributed caches and
data stores that must change size without invalidating
the entire keyspace.

| #011 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Load Balancing | |
| **Used by:** | Sharding, Distributed Cache Design | |
| **Related:** | Load Balancing, Round Robin, Least Connections, Sharding, Distributed Cache Design | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You build a distributed cache with 4 nodes. To
distribute keys across nodes, you use the simplest
approach: `node = hash(key) % 4`. Keys are evenly
distributed. Life is good.

Six months later, traffic grows and you add a 5th
cache node. Now `node = hash(key) % 5`. Every single
key maps to a different node than before. When clients
start sending requests after the scale-out, every
cache miss - because every key is now on the "wrong"
node from the cache's perspective. You just invalidated
100% of your cache. Your database absorbs the full
load of all previously-cached keys simultaneously.
It collapses. This is a thundering herd, triggered
by an operational change (adding one node), caused
by a naive hashing strategy.

**THE BREAKING POINT:**
The `hash(key) % N` approach (modular hashing) couples
the mapping to N. Change N and the entire mapping
changes. For a cache, this means every node change
causes a full cache invalidation. For a distributed
data store, it means a full data migration is required.
At scale, this is operationally impossible.

**THE INVENTION MOMENT:**
Consistent hashing was invented by Karger et al. at MIT
in 1997 in the paper "Consistent Hashing and Random
Trees." The key insight: instead of mapping keys to
servers by modular arithmetic, map both keys and servers
to positions on a conceptual ring (0 to 2^32-1). Each
key is served by the first server clockwise from it
on the ring. Adding or removing one server only moves
the keys that were "owned" by that server to the next
server - approximately 1/N of all keys.

**EVOLUTION:**
Original consistent hashing had poor load distribution
(servers landed on the ring by random hash, causing
uneven distribution). Virtual nodes (vnodes) solved
this: each physical server has 100-150 virtual nodes
on the ring, spreading its "ownership" across many
ring segments. This is the production form used by
Cassandra, DynamoDB, Redis Cluster, and Memcached.

---

### 📘 Textbook Definition

Consistent hashing is a distributed hashing scheme
that maps both servers (nodes) and keys to positions
on a conceptual hash ring (a circular space of values
from 0 to 2^32-1). Each key is assigned to the first
server encountered moving clockwise from the key's
position on the ring. When a server is added, only
the keys previously assigned to the next clockwise
server are remapped (~1/N of all keys). When a server
is removed, its keys move to the next clockwise server.
Virtual nodes (multiple ring positions per physical
server) improve load distribution by giving each server
many small segments of the ring rather than one large
segment.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Map keys and servers to a ring; each key goes to the
nearest server clockwise. Adding/removing a server
only remaps 1/N of keys, not all keys.

**One analogy:**
> Imagine a circular clock face numbered 0-100.
> Servers are placed at positions 0, 25, 50, 75.
> A key hashing to 60 goes to the next server
> clockwise: position 75. A key hashing to 30 goes
> to position 50. Add a server at position 65:
> only keys between 51 and 65 move to the new server.
> Keys everywhere else are undisturbed.

**One insight:**
The breakthrough is that both servers and keys exist
in the same space. When the server space changes
(add/remove), only the keys immediately adjacent to
the change are affected. "Consistent" means adding
N+1 servers keeps the N-1 unchanged servers' key
assignments consistent with what they were before.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Both servers and keys are hashed to positions in
   the same ring space (0 to 2^32-1).
2. A key belongs to the first server clockwise from
   its position (the "successor" server).
3. Adding a server only affects keys in the ring
   segment [new_server's predecessor, new_server].
4. Removing a server moves its keys to its clockwise
   successor.
5. Expected keys remapped when adding 1 server =
   total_keys / (N+1) ≈ 1/N fraction.

**VIRTUAL NODES (VNODES):**
Without vnodes, physical server positions are random
hash outputs. By chance, one server might own 40% of
the ring and another 5%. Load is uneven. Virtual nodes
fix this: each physical server is given V virtual
positions on the ring (V = 100-200 in production).
Each virtual node owns 1/(N*V) of the ring. With
enough vnodes, each physical server owns approximately
1/N of total keys, regardless of where they landed
on the ring by chance.

**WHY NOT JUST USE A LOOKUP TABLE?**
A lookup table (key → server) would be consistent
(only update the entries you want) but would require
O(key_count) updates to rebalance, and can't handle
dynamic key sets. Consistent hashing is computable
in O(log N) without storing any per-key state.

**THE TRADE-OFFS:**

**Gain:** Adding/removing servers migrates ~1/N of keys
instead of all keys. Scales distributed caches and
data stores without full invalidation.

**Cost:** Ring lookup requires O(log N) binary search
instead of O(1) modular arithmetic. Implementation
complexity significantly higher. Vnodes require
careful tuning (too few = uneven, too many = memory
overhead in ring data structure).

---

### 🧪 Thought Experiment

**SCENARIO: Cache scale-out comparison**

Setup: 4-node cache, 1 million cached keys, 10k
database queries/second if cache misses occur.

**Modular hashing (hash % N):**
Scale from 4 to 5 nodes.
100% of keys now map to wrong nodes.
1 million cache misses. Database absorbs 10k QPS
for duration until caches re-warm (say, 30 minutes).
Database is overwhelmed. Outage.

**Consistent hashing:**
Scale from 4 to 5 nodes.
~20% of keys (1/5) now belong to the new node.
200,000 cache misses. Database absorbs 2k QPS.
Database handles it within normal capacity.
Cache re-warms gradually over minutes, not hours.
No outage.

**THE INSIGHT:**
The improvement is not just "less data migration."
It is the difference between an outage and a non-event.
This is why consistent hashing is a non-negotiable
requirement for any distributed cache or sharded store
that needs to change size in production.

---

### 🧠 Mental Model / Analogy

> Consistent hashing is like assigning responsibility
> zones around a circular track to security guards
> (servers). Each guard is responsible for the zone
> from their post clockwise to the next guard's post.
> When you hire a new guard (add a server), you put
> them between two existing guards. The new guard
> takes over part of one guard's zone. All other
> guards' zones are unchanged. When a guard leaves
> (server removal), their zone expands to cover
> the next guard clockwise.

- "Guards" → servers
- "Zone" → set of keys the server is responsible for
- "New guard between two existing" → server added to ring
- "Zone unchanged" → 1/N keys remapped, rest untouched
- "Hiring more guards" → adding virtual nodes for even coverage

**Where this analogy breaks down:**
Unlike physical zones, hash ring positions are
determined by a hash function - you cannot choose
exactly where on the ring a server lands without
virtual nodes to control placement granularity.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A smarter way to decide which server stores which data,
so that when you add or remove a server, you only move
a small fraction of the data, not all of it.

**Level 2 - How to use it (junior developer):**
Use an existing consistent hashing library (Guava's
`ConsistentHashFunction`, AWS SDK's consistent hashing
in the DynamoDB client, or Redis Cluster which handles
this automatically with 16,384 hash slots). You typically
don't implement consistent hashing from scratch in
application code.

**Level 3 - How it works (mid-level engineer):**
The ring is implemented as a `TreeMap<Integer, Server>`
(sorted by ring position). To find a key's server:
hash the key to an integer, call `TreeMap.ceilingEntry(hash)`.
This is O(log N) where N is the number of virtual nodes
on the ring (not physical servers). Adding a server
means adding V new entries to the TreeMap (V = vnode count).

**Level 4 - Why it was designed this way (senior/staff):**
The `TreeMap.ceilingEntry()` binary search is key to
performance. A naive implementation using a sorted array
and linear scan would be O(N*V) per lookup - unacceptable.
The sorted tree gives O(log N*V) per lookup. With N=10
servers and V=150 vnodes, that is O(log 1500) ≈ 11
operations per lookup - essentially free. The design
choice to use a sorted data structure instead of a hash
table here is what makes consistent hashing practical.

**Level 5 - Mastery (distinguished engineer):**
Real-world consistent hashing in Cassandra and DynamoDB
differs from the textbook version in important ways:
(1) Token assignment in Cassandra uses a carefully
computed set of vnode positions (not random) to ensure
even data distribution across heterogeneous nodes.
(2) DynamoDB uses consistent hashing at the partition
level, not the item level - the key maps to a partition
group, not a single server. (3) Redis Cluster avoids
consistent hashing entirely, using 16,384 static
"slots" instead of a ring - simpler to implement and
reason about at the cost of less flexibility in scaling
increments.

---

### ⚙️ How It Works (Mechanism)

**The ring data structure:**

```
┌─────────────────────────────────────────────────────┐
│ CONSISTENT HASH RING (simplified, 3 servers)        │
│                                                     │
│         0                                           │
│         │                                           │
│   ──────●──────                                     │
│  /  Server A   \                                    │
│ │  hash=100     │                                   │
│ │               │                                   │
│ ●               ●                                   │
│ Server C    Server B                                │
│ hash=800    hash=400                                │
│  \               /                                  │
│   ──────────────                                    │
│         │                                           │
│        max                                          │
│                                                     │
│ Key hash=150 → goes to Server B (next clockwise)   │
│ Key hash=500 → goes to Server C (next clockwise)   │
│ Key hash=900 → wraps around → goes to Server A     │
└─────────────────────────────────────────────────────┘
```

**Ring with virtual nodes:**

```
┌─────────────────────────────────────────────────────┐
│ VIRTUAL NODES (3 physical servers, 2 vnodes each)  │
│                                                     │
│ Physical: A, B, C                                   │
│ Virtual ring positions:                             │
│   0──A1──B1──A2──C1──B2──C2──────max              │
│      100  200  350  500  650  800                   │
│                                                     │
│ Key hash=250 → next clockwise from 250 = C1 → C    │
│ Key hash=600 → next clockwise from 600 = B2 → B    │
│                                                     │
│ Add Server D with 2 vnodes:                         │
│ D lands at positions 300 and 750 (by hash of D)    │
│ Keys in [200,300] move from A2 to D1               │
│ Keys in [650,750] move from C2 to D2               │
│ ~25% of keys remapped. 75% untouched.              │
└─────────────────────────────────────────────────────┘
```

**Implementation with TreeMap:**

```java
// Core data structure for consistent hashing ring
TreeMap<Integer, String> ring = new TreeMap<>();

// Add server with V virtual nodes
void addServer(String server, int vnodeCount) {
    for (int i = 0; i < vnodeCount; i++) {
        int pos = hash(server + "#" + i);
        ring.put(pos, server);
    }
}

// Find server for a key: O(log N*V)
String getServer(String key) {
    if (ring.isEmpty()) return null;
    int keyHash = hash(key);
    Map.Entry<Integer, String> entry =
        ring.ceilingEntry(keyHash);
    // Wrap around: if no entry clockwise, use smallest
    if (entry == null) entry = ring.firstEntry();
    return entry.getValue();
}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL KEY LOOKUP:**
```
[Client requests key "user:12345"]
  → [Client hashes key: hash("user:12345") = 47382]
  → [Ring lookup: TreeMap.ceilingEntry(47382)]
  → [Returns server B at ring position 52100]
  → [Client sends request to Server B]
  → [Cache hit or miss on Server B]
```

**ADDING A SERVER (scale-out):**
```
[New server E is added]
  → [Compute E's vnode positions: hash("E#0"),
    hash("E#1"), ...]
  → [Insert all vnode positions into ring TreeMap]
  → [Keys previously served by successor nodes that
     fall in E's new segments are now on E]
  → [Cache: those keys will miss until re-warmed]
  → [~1/N of keys affected. N-1 servers unaffected.]
```

**REMOVING A SERVER (failure or decommission):**
```
[Server B fails]
  → [Remove all B's vnode positions from ring]
  → [B's keys now route to B's clockwise successors]
  → [Cache: B's keys will miss until re-warmed on
     successor servers]
  → [Data store: B's data must be replicated from
     replicas before B is removed - separate concern]
```

**AT SCALE:**
- 100 servers, 150 vnodes each → ring has 15,000 entries
- O(log 15000) ≈ 14 operations per lookup
- Adding 1 server → 150 ring insertions + ~1% key migration
- Scales to thousands of servers without degradation

---

### 💻 Code Example

**Example 1 - Complete consistent hashing implementation**
```java
// BAD: Modular hashing - full invalidation on node change
public class ModularHashBalancer {
    private final List<String> nodes;

    public String getNode(String key) {
        // Adding/removing a node changes ALL mappings
        int idx = Math.abs(key.hashCode()) % nodes.size();
        return nodes.get(idx);
    }
}

// GOOD: Consistent hashing with virtual nodes
public class ConsistentHashRing {
    private final TreeMap<Long, String> ring;
    private final int vnodeCount;
    private final MessageDigest md5;

    public ConsistentHashRing(int vnodeCount)
        throws NoSuchAlgorithmException {
        this.ring = new TreeMap<>();
        this.vnodeCount = vnodeCount;
        this.md5 = MessageDigest.getInstance("MD5");
    }

    public void addNode(String node) {
        for (int i = 0; i < vnodeCount; i++) {
            long pos = hash(node + "#vnode#" + i);
            ring.put(pos, node);
        }
    }

    public void removeNode(String node) {
        for (int i = 0; i < vnodeCount; i++) {
            long pos = hash(node + "#vnode#" + i);
            ring.remove(pos);
        }
    }

    public String getNode(String key) {
        if (ring.isEmpty()) return null;
        long keyHash = hash(key);
        Map.Entry<Long, String> entry =
            ring.ceilingEntry(keyHash);
        // Wrap around the ring
        if (entry == null) entry = ring.firstEntry();
        return entry.getValue();
    }

    private long hash(String value) {
        byte[] digest = md5.digest(
            value.getBytes(StandardCharsets.UTF_8));
        // Use first 8 bytes as a long
        return ByteBuffer.wrap(digest).getLong();
    }
}
```

**Example 2 - Verifying even distribution**
```java
// Test: verify that vnodes achieve even distribution
public static void verifyDistribution() {
    ConsistentHashRing ring =
        new ConsistentHashRing(150); // 150 vnodes
    List<String> nodes =
        List.of("node-1", "node-2", "node-3",
                "node-4", "node-5");
    nodes.forEach(ring::addNode);

    Map<String, Integer> distribution = new HashMap<>();
    nodes.forEach(n -> distribution.put(n, 0));

    // Hash 100,000 random keys
    Random random = new Random(42);
    for (int i = 0; i < 100_000; i++) {
        String key = "key-" + random.nextInt(1_000_000);
        String node = ring.getNode(key);
        distribution.merge(node, 1, Integer::sum);
    }

    // Each node should have ~20,000 ± 2,000 keys
    // With 150 vnodes, standard deviation ≈ 1-2%
    distribution.forEach((node, count) ->
        System.out.printf("%s: %d (%.1f%%)%n",
            node, count, count * 100.0 / 100_000));
}

// Expected output (approximate):
// node-1: 20143 (20.1%)
// node-2: 19876 (19.9%)
// node-3: 20231 (20.2%)
// node-4: 19902 (19.9%)
// node-5: 19848 (19.8%)
```

**Example 3 - Verifying minimal remapping on node add**
```java
// Key invariant: adding 1 node should remap ~1/N keys
public static void verifyConsistency() {
    ConsistentHashRing ring =
        new ConsistentHashRing(150);
    ring.addNode("node-1");
    ring.addNode("node-2");
    ring.addNode("node-3");
    ring.addNode("node-4"); // 4 nodes

    // Record initial mapping for 100,000 keys
    Map<String, String> before = new HashMap<>();
    for (int i = 0; i < 100_000; i++) {
        String key = "key-" + i;
        before.put(key, ring.getNode(key));
    }

    // Add a 5th node
    ring.addNode("node-5");

    // Count remapped keys
    long remapped = before.entrySet().stream()
        .filter(e -> !e.getValue()
            .equals(ring.getNode(e.getKey())))
        .count();

    System.out.printf("Remapped: %d / 100000 (%.1f%%)%n",
        remapped, remapped * 100.0 / 100_000);
    // Expected: ~20,000 (20%) - approximately 1/(N+1)
    // vs modular: 100,000 (100%) - full invalidation
}
```

---

### ⚖️ Comparison Table

| Approach | Keys Remapped on Node Add | Keys Remapped on Node Remove | Implementation | Use Case |
|---|---|---|---|---|
| **Consistent Hashing** | ~1/N | ~1/N | Complex | Distributed caches, DHT |
| Modular (hash % N) | ~100% | ~100% | Simple | Not suitable for scaling |
| Range-based partitioning | ~0 (manual) | ~0 (manual) | Manual | Manual sharding |
| Redis Cluster (16384 slots) | ~1/N (slot migration) | ~1/N | Managed | Redis at scale |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Consistent hashing guarantees exactly 1/N remapping | It guarantees EXPECTED 1/N. Without vnodes, actual remapping can vary significantly due to random ring placement. With 150 vnodes, variance is <5%. |
| Virtual nodes are optional | Without vnodes, a 3-server ring might have one server owning 60% of the ring by chance. Production systems always use vnodes (100-200 per physical server). |
| Consistent hashing solves hot key problems | It solves uneven KEY DISTRIBUTION but not HOT KEYS. If one key receives 90% of traffic, its server is overloaded regardless of how keys are distributed. Hot keys require application-level solutions (replication of hot keys, local caching). |
| Redis uses consistent hashing | Redis Cluster uses a different approach: 16,384 fixed slots. Each key maps to a slot via CRC16, and slots are distributed to nodes. Simpler than a ring but achieves similar scaling properties. |

---

### 🚨 Failure Modes & Diagnosis

**Hot Spots from Too Few Virtual Nodes**

**Symptom:**
After adding a 5th cache node to a 4-node consistent
hash ring with 10 vnodes per server, one server
handles 45% of all cache traffic while another
handles only 8%.

**Root Cause:**
With only 10 vnodes per server, ring segments are large
and uneven. By chance, one server landed on a large
contiguous ring segment and owns a disproportionate
fraction of keys.

**Diagnostic:**
```java
// Check distribution of ring ownership
Map<String, Long> ringShare = new HashMap<>();
ring.getNodes().forEach(node -> ringShare.put(node, 0L));
long totalRingSize = Long.MAX_VALUE - Long.MIN_VALUE;

// Walk the ring and compute owned segment per node
List<Map.Entry<Long, String>> entries =
    new ArrayList<>(ring.getRawRing().entrySet());
Collections.sort(entries, Map.Entry.comparingByKey());
for (int i = 0; i < entries.size(); i++) {
    String node = entries.get(i).getValue();
    long segmentSize = (i + 1 < entries.size())
        ? entries.get(i + 1).getKey() - entries.get(i).getKey()
        : totalRingSize - entries.get(i).getKey();
    ringShare.merge(node, segmentSize, Long::sum);
}
// Print ownership fraction per node:
ringShare.forEach((n, share) ->
    System.out.printf("%s: %.1f%%%n",
        n, share * 100.0 / totalRingSize));
// Nodes with >30% share are hot spots
```

**Fix:**
Increase vnode count from 10 to 150. Rebuild the ring.
Data will need to be migrated from the overloaded node
to the newly-assigned nodes, but this is a one-time
rebalance.

**Prevention:**
Use at least 100-150 vnodes per physical server.
Benchmark distribution (as in the verification example
above) before putting a new consistent hash configuration
into production.

---

**Key Migration Storm During Scale-Out**

**Symptom:**
After adding a new cache node, cache hit rate drops
from 95% to 76% for 10 minutes. Database load spikes
to 3x normal. Not an outage, but a significant
degradation.

**Root Cause:**
~20% of keys now route to the new node (correct
behavior). But the new node's cache is empty. For
10 minutes until the cache warms up, those 20% of
keys are cache misses hitting the database.

**Diagnostic:**
```bash
# Check cache hit rate drop timing in metrics
# Correlate with node addition time
# AWS ElastiCache: CacheHits vs CacheMisses metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ElastiCache \
  --metric-name CacheHitRate \
  --period 60 --statistics Average \
  --start-time "$(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S)" \
  --end-time "$(date -u +%Y-%m-%dT%H:%M:%S)" ...
```

**Fix:**
Pre-warm the new cache node before routing traffic
to it. "Warm-up" approach: for the first 5 minutes
after adding the node, also route reads to the new
node's key range but serve from the old node (shadow
read), populating the new node's cache. Once hit rate
on the new node reaches 80%+, cut over fully.
Alternatively, use a slow roll strategy: add the
new node with weight=1 and others at weight=9, gradually
increasing new node weight as it warms up.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Load Balancing` - consistent hashing is one
  algorithm used by load balancers and distributed
  data stores for routing decisions

**Builds On This (learn these next):**
- `Sharding` - consistent hashing is commonly used
  as the sharding strategy for distributed databases
- `Distributed Cache Design` - consistent hashing
  is the standard distribution mechanism for multi-
  node cache clusters

**Alternatives / Comparisons:**
- `Round Robin` / `Least Connections` - simpler LB
  algorithms for stateless services; consistent
  hashing is for cache/data-affinity routing

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Map keys and servers to a ring; key goes │
│              │ to nearest clockwise server              │
├──────────────┼──────────────────────────────────────────┤
│ PROBLEM IT   │ Modular hashing invalidates 100% of keys │
│ SOLVES       │ on any node change; consistent hashing   │
│              │ only moves ~1/N keys                     │
├──────────────┼──────────────────────────────────────────┤
│ KEY INSIGHT  │ "Consistent" = adding a node only        │
│              │ affects keys in ONE ring segment, not all│
├──────────────┼──────────────────────────────────────────┤
│ USE WHEN     │ Distributed caches that need to scale;   │
│              │ sharded data stores; load balancing with │
│              │ server-affinity requirements             │
├──────────────┼──────────────────────────────────────────┤
│ AVOID WHEN   │ No scaling needed; cache invalidation    │
│              │ cost is acceptable; Redis Cluster handles│
│              │ it with slots (simpler)                  │
├──────────────┼──────────────────────────────────────────┤
│ MUST-DO      │ Use 100-150 vnodes per physical server to│
│              │ ensure even distribution                 │
├──────────────┼──────────────────────────────────────────┤
│ DATA         │ TreeMap<Long, Server>; lookup O(log N*V);│
│ STRUCTURE    │ V = vnode count per server               │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "The fix for 100% cache invalidation on  │
│              │  any node change: only move 1/N keys."   │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Sharding → Hot Shard → Distributed Cache │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. `hash(key) % N` breaks on scale - consistent hashing
   is the fix.
2. ~1/N keys remapped when adding 1 server - N-1
   servers are completely unaffected.
3. Always use virtual nodes (100-150 per server) -
   raw consistent hashing has poor distribution.

**Interview one-liner:**
"Consistent hashing maps both keys and servers to a
ring. Each key is served by the nearest clockwise
server. Adding or removing one server only remaps
1/N of keys (where N is the number of servers), not
all keys. This is critical for distributed caches
and sharded stores that must scale without full
invalidation. Virtual nodes (150 per server) are
required for even load distribution."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
When you need a mapping function that is stable under
structural changes (adding/removing nodes), the key
design requirement is that the mapping of existing
elements should be minimally disrupted when the
structure changes. Consistent hashing achieves this
for key-to-server mappings. The same principle applies
to any distributed assignment problem: minimize
reshuffling when the set of destinations changes.

**Where else this pattern appears:**
- **Cassandra token ring:** Uses consistent hashing
  with vnodes to distribute rows across replica sets.
  The replication factor determines how many clockwise
  successors also hold a copy of each row.
- **Amazon Dynamo (the paper):** The original DynamoDB
  design paper (2007) describes consistent hashing
  as its core distribution mechanism. Modern DynamoDB
  uses a different internal approach but the paper
  is the canonical reference.
- **Chord protocol (P2P DHT):** Uses consistent hashing
  to distribute data across peer-to-peer nodes in a
  self-organizing distributed hash table. No central
  coordinator.
- **Memcached client routing:** Most Memcached clients
  use consistent hashing to distribute keys across
  the Memcached cluster without any coordination
  server.

---

### 💡 The Surprising Truth

Amazon's DynamoDB paper (2007) revealed that when
they operated a naive modular-hash-based distributed
cache, a single node failure caused a 30% jump in
database read traffic - because 1/N of all cached
data suddenly had nowhere to go. The engineers who
designed DynamoDB described this as a "data avalanche"
problem. The switch to consistent hashing was not
a performance optimization - it was a reliability
requirement. Without it, any node failure in the
cache tier would create a secondary database outage.
Consistent hashing turned a "cache node fails → database
collapses" scenario into "cache node fails → ~1/N
cache miss rate increase for minutes until re-warm."
The algorithm is not just about avoiding unnecessary
data movement. It is about preventing a cascade
of failures from one tier to the next.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. [EXPLAIN] Describe why `hash(key) % N` causes
   100% remapping when N changes, and how consistent
   hashing limits this to ~1/N.
2. [IMPLEMENT] Implement a basic consistent hash ring
   using a TreeMap, including add/remove node operations
   and key lookup.
3. [TUNE] Explain why virtual nodes are necessary and
   what the trade-off is between vnode count (distribution
   quality) and ring size (memory and insert overhead).
4. [DEBUG] Given a cache with highly uneven traffic
   distribution across nodes, diagnose whether it is
   a hot key problem or a ring distribution problem,
   and describe how to fix each.
5. [EXTEND] Compare consistent hashing to Redis
   Cluster's slot-based approach: when would you
   prefer one over the other?

---

### 🧠 Think About This Before We Continue

**Q1.** You have a consistent hash ring with 3 servers
and 10 virtual nodes each. Server 2 fails. Describe
exactly what happens to: (a) keys currently cached
on Server 2, (b) new requests for those keys after
the failure, (c) keys cached on Server 1 and Server 3.

*Hint: Server 2's ring positions are removed. Keys
that were assigned to Server 2's vnodes now route to
the next clockwise server (Server 1 or 3 depending
on position). Server 1 and Server 3's existing key
assignments are completely unchanged.*

**Q2.** A teammate proposes using 5 virtual nodes
per server (instead of 150) to "reduce memory usage
in the ring." The ring has 10 physical servers.
What is the expected behavior with 5 vnodes vs 150
vnodes, and what is the actual memory cost difference
between the two?

*Hint: With 5 vnodes per server and 10 servers, the
ring has 50 entries. With 150 vnodes, it has 1,500
entries. The memory difference is ~50 entries × ~32 bytes
= ~1,600 bytes. Trivial. But the distribution with 5
vnodes may have one server owning 30%+ of keys by
chance - the "saving" is not worth the distribution
risk.*

**Q3 (Hands-On):** Implement the consistent hash ring
from Example 1. Write a test that: (1) adds 4 servers
with 150 vnodes each, (2) records the server assignment
for 100,000 random keys, (3) adds a 5th server,
(4) counts how many keys remapped. Verify the result
is approximately 20,000 (1/5 of all keys). Then
repeat the test with 5 vnodes per server instead of
150 and observe the distribution variance.

---

### 🎯 Interview Deep-Dive

**Q1: Design a distributed cache (like Memcached)
that can add and remove nodes without a full cache
invalidation. What algorithm would you use?**
*Why they ask:* Classic consistent hashing interview
question. Tests both the algorithm knowledge and
the problem it solves.
*Strong answer includes:*
- Use consistent hashing with virtual nodes
- Clients maintain the ring in memory; ring updates
  broadcast when nodes join/leave
- On node add: ~1/N keys miss until re-warmed from DB
- On node remove: same, ~1/N keys miss
- Replication: store each key on the next K clockwise
  nodes (K=2 or 3) so one node failure loses no data
  (just routes to replica)

**Q2: How does Cassandra use consistent hashing?**
*Why they ask:* Tests whether abstract knowledge
maps to real-world systems.
*Strong answer includes:*
- Each row key is hashed to a token (ring position)
- Each node owns a token range; it stores all rows
  whose token falls in its range
- Replication factor (RF): each row is stored on
  the RF nodes that own the next RF token ranges
  clockwise (the "coordinator" and RF-1 "replicas")
- Vnodes (Cassandra calls them "virtual nodes"):
  each physical node owns 256 token ranges by default,
  spread around the ring for even distribution
- Adding a node: it takes ownership of some token
  ranges from existing nodes; those rows stream from
  the old owner to the new owner

**Q3: What happens to consistent hashing when one
server is significantly slower than others due to
a GC pause? How would you mitigate this?**
*Why they ask:* Tests operational depth beyond the
algorithm itself.
*Strong answer includes:*
- Consistent hashing routes based on key position,
  not server load. A slow server continues receiving
  ~1/N of all requests even during a GC pause.
- Mitigation 1: at the client, use timeout + retry
  on a different server for keys that map to the slow
  server. The ring fallback logic: on timeout, try
  the next clockwise server.
- Mitigation 2: server-side circuit breaking at the
  client - if Server B has had 10 consecutive timeouts,
  temporarily skip it in the ring and use its clockwise
  successor until health recovers.
- This is why service meshes (Envoy) implement outlier
  detection on top of consistent hashing - removing
  a slow node from the ring temporarily even if it
  passes basic health checks.
