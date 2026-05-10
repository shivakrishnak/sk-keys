---
id: DST-038
title: "Consistent Hashing"
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-006
used_by: DST-039
related: DST-039, DST-040
tags:
  - distributed
  - algorithm
  - foundational
  - deep-dive
  - architecture
status: complete
version: 2
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 38
permalink: /distributed-systems/consistent-hashing/
---

# DST-038 - Consistent Hashing

⚡ TL;DR - Consistent hashing maps both data keys and server nodes onto a shared ring; when a node is added or removed, only K/N keys are remapped (where K=keys, N=nodes) rather than remapping all keys, making it the standard algorithm for minimal disruption data partitioning in distributed caches and databases.

| Metadata        |                  |     |
| :-------------- | :--------------- | :-- |
| **Depends on:** | DST-006          |     |
| **Used by:**    | DST-039          |     |
| **Related:**    | DST-039, DST-040 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Naive modulo sharding: `server = hash(key) % N`. This is simple and fast. But add or remove one server: N changes. Every key's server assignment changes. A cache with 1 million keys and 10 servers: adding one server remaps ~909,000 keys (91%). Every remapped cache key is a cache miss. Under traffic: a cascade of misses hits the database simultaneously — thundering herd. The database is overwhelmed. The system falls over.

**THE BREAKING POINT:**
Large-scale distributed systems require adding and removing nodes for capacity management, failure recovery, and rolling upgrades. Modulo hashing makes any topology change catastrophic — the entire dataset must be redistributed. This was the fundamental barrier to elastic scaling of distributed caches and key-value stores in the early 2000s.

**THE INVENTION MOMENT:**
Karger et al. (1997, MIT) published "Consistent Hashing and Random Trees" — introducing a ring-based hash space where adding/removing a node affects only the keys immediately "next to" that node on the ring, not all keys. Average disruption: K/N keys (1/N fraction of the dataset). For 10 servers: adding one remaps ~10% of keys, not 91%. This made elastic scaling practically feasible. Akamai's CDN, Amazon's Dynamo (2007), and Cassandra all adopted consistent hashing as their core data placement algorithm.

**EVOLUTION:**
1997: Karger's consistent hashing. 2007: Amazon Dynamo — consistent hashing + virtual nodes + vector clocks. 2008: Cassandra — consistent hashing with configurable replication. 2012: Cassandra adopts virtual nodes (vnodes) by default, replacing single-token assignment. 2013: Discord blog on scaling to 5 billion messages with consistent hashing in Redis. Today: consistent hashing is the default algorithm in distributed caches (Memcached, Redis Cluster), key-value stores (Cassandra, DynamoDB, Riak), CDNs, and load balancers.

---

### 📘 Textbook Definition

**Consistent hashing** is a data partitioning scheme that places both data keys and server nodes onto a fixed-size circular hash space (the "ring"), ranging from 0 to 2^32-1. Each server is hashed to one (or more) positions on the ring. Each key is hashed to a position and assigned to the FIRST server encountered by moving clockwise around the ring. **Key property:** when a server is added: only the keys between the new server's predecessor and the new server are remapped (to the new server). When a server is removed: only the keys assigned to that server are remapped (to the removed server's clockwise successor). In both cases: approximately K/N keys are affected, where K is the total number of keys and N is the number of servers. In contrast: modulo hashing affects all K keys on any topology change. **Replication:** Cassandra/Dynamo replicate each key to the next R clockwise servers (replication factor R). Data is automatically replicated without a central coordinator — each server knows the ring topology and routes requests accordingly.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Consistent hashing maps servers AND keys onto a ring — add/remove one server and only ~1/N of keys move, not all of them.

> Consistent hashing is like assigning seats in a circular stadium. Each player (server) sits at a position on the ring. Each fan (key) sits at the next player clockwise. Add a new player — only the fans "near" that player's new seat move. Remove a player — their fans shift to the next player clockwise. Most fans don't move at all.

**One insight:** The ring abstraction makes node addition and removal local operations — only keys between the new node and its predecessor are affected, not keys elsewhere on the ring. This locality is what limits disruption to K/N.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **Fixed ring space:** the hash space is fixed (e.g., 0 to 2^32-1). Keys and nodes are mapped into this space. The space size doesn't change regardless of the number of nodes.
2. **Clockwise assignment:** a key is assigned to the first node encountered moving clockwise from the key's ring position. This is the "successor node" rule.
3. **Local disruption on topology change:** adding a node inserts it between two existing nodes. Only the keys that were assigned to the new node's clockwise successor (between the new node's position and its predecessor) move. All other keys are unaffected.
4. **Load balance via distribution:** if node positions are uniformly distributed on the ring: each node holds approximately K/N keys. If positions are non-uniform (some nodes clump together): some nodes are overloaded. Virtual nodes (DST-039) solve this.

**DERIVED DESIGN:**
Lookup: `hash(key)` → position on ring → binary search for first node ≥ position (clockwise). O(log N) lookup in a sorted node list. Addition: `hash(new_node)` → insert into sorted node list → O(log N). Affected keys: those previously assigned to the new node's successor, between new node position and successor.

**THE TRADE-OFFS:**
**Gain:** O(K/N) disruption on topology change vs O(K) for modulo. Elastic scaling of distributed systems. Decentralized data placement (no coordinator needed for routing).
**Cost:** Non-uniform load distribution (unequal arc lengths). Hot spots on the ring. Rebalancing complexity when load is uneven. Virtual nodes (vnodes) mitigate load imbalance at the cost of complexity.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Any hash-based partitioning scheme that limits disruption to K/N must be "consistent" — stable node assignments for keys not adjacent to the topology change. This is the invariant that consistent hashing provides.
**Accidental:** The ring visualization and clockwise assignment are implementation conveniences — the invariant (local disruption) is what matters. Jump consistent hashing (Google, 2014) achieves the same property without a ring, with O(1) lookup.

---

### 🧪 Thought Experiment

**SETUP:** 4 servers on a consistent hashing ring. 100 keys distributed across them.

**MODULO HASHING (before consistent hashing):**

- Initial: 4 servers. Key `k1`: `hash(k1) % 4 = 2` → Server 2.
- Add Server 5: 5 servers now. Key `k1`: `hash(k1) % 5 = 3` → Server 3.
- EVERY key must be checked and potentially remapped. 100 keys, ~80 of them move.

**CONSISTENT HASHING:**

- Ring positions (0-100): S1=10, S2=35, S3=60, S4=85.
- Key assignments: keys 0-10→S1, 11-35→S2, 36-60→S3, 61-85→S4, 86-100→S1.
- Add Server 5 at position 50:
  - S5 is between S2 (35) and S3 (60).
  - Only keys 36-50 (previously S3's) move to S5.
  - Keys 51-100 and 0-35: UNCHANGED.
  - ~15 of 100 keys move — approximately K/N = 100/5 = 20. Close.
- Remove S3 (position 60):
  - Keys 36-60 (S3's) move to S4 (next clockwise).
  - All other keys: UNCHANGED.
  - ~25 of 100 keys move — approximately K/N = 100/4 = 25.

**THE INSIGHT:** The ring ensures that topology changes are LOCAL — only keys adjacent to the changed node move. The rest of the ring is untouched. This is the mathematical property that makes consistent hashing dramatically better than modulo hashing for elastic systems.

---

### 🧠 Mental Model / Analogy

> Consistent hashing is like a clock face with servers at specific hour positions, and each task being assigned to the next server clockwise. Add a new server at the 3 o'clock position: only tasks between 2 o'clock and 3 o'clock (previously going to 4 o'clock) now go to 3 o'clock. Tasks at other hours are unaffected. Remove the server at 9 o'clock: its tasks shift to the server at 10 o'clock. All other tasks continue to their original servers.

**Mapping:**

- **Clock face (0-12 hours)** → hash ring (0 to 2^32-1)
- **Servers at hour positions** → nodes hashed to ring positions
- **Task assigned to next server clockwise** → key assigned to clockwise successor node
- **Adding server at 3 o'clock** → inserting a new node between two existing positions
- **Only 2-3 tasks move** → only K/N keys affected

Where this analogy breaks down: a real clock has fixed hours. The hash ring has exponentially more positions (2^32 ≈ 4 billion), allowing fine-grained node placement. The clock analogy works for intuition but understates the precision of the ring.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Consistent hashing is a smarter way to decide "which server stores this data." With normal hashing: if you change the number of servers, almost all data must move. With consistent hashing: only ~1/N of the data moves when you add or remove a server. This makes adding capacity or replacing failed servers much faster and cheaper.

**Level 2 - How to use it (junior developer):**
In Java: use `TreeMap<Long, Server>` to represent the ring. Add servers with `treeMap.put(hash(server), server)`. Route key: `Long hash = hash(key); Map.Entry<Long, Server> entry = treeMap.ceilingEntry(hash); if (entry == null) entry = treeMap.firstEntry();`. This gives the first server clockwise. Libraries: Guava's `Hashing.consistentHash()`, `ketama` for Memcached, Redis Cluster's hash slot algorithm (not a ring but achieves similar distribution).

**Level 3 - How it works (mid-level engineer):**
Ring representation: sorted array or TreeMap of (hash, node) pairs. Lookup: binary search for the smallest hash ≥ key's hash (ceiling). Add node: insert into sorted structure → redistribute keys between new node and its predecessor (migrate data from predecessor's range). Replication: for replication factor R: assign key to next R distinct nodes clockwise. Cassandra uses a partition ring with token-based routing — each coordinator can route any request to the correct replica without a central directory.

**Level 4 - Why it was designed this way (senior/staff):**
The consistent hashing ring achieves O(K/N) disruption by construction: nodes partition the ring into arcs, and each arc is "owned" by one node. Topology change only affects the arcs immediately adjacent to the changed node. The sorted structure (TreeMap/binary search) achieves O(log N) routing. The alternative — a distributed hash table (DHT) like Chord, Kademlia — uses consistent hashing as its core primitive but adds a decentralized routing protocol (finger tables, O(log N) hops). For single-DC distributed caches: direct ring lookup (O(log N), O(1) hops) is better than DHT O(log N) hops. Jump consistent hashing (2014): `y = 0; j = -1; while (y < num_buckets) { j = y; b = (b * 2862933555777941757ULL + 1); y = floor((j+1) * (real(1 << 31) / real((b >> 33) + 1))); } return j;` — O(1) time, O(1) space, no ring data structure. Used in Google's Guice configuration routing.

**Expert Thinking Cues:**

- "Our Redis Cluster is having hotspot issues" → Consistent hashing distributes by key hash, not by data size. A single very large key dominates its node. Use application-level sharding (append shard ID to key prefix) or use Redis Cluster hash tags (`{user_id}key_suffix`) to co-locate related keys on the same slot.
- "Cassandra has uneven load on nodes" → Consistent hashing with single tokens can produce large arc lengths (some nodes handle large ranges). Solution: virtual nodes (vnodes) — each physical node has 256 virtual tokens, distributing the arc lengths evenly. See DST-039.
- "We need to add a node without any downtime" → Consistent hashing: adding a node triggers migration of ~K/N keys from the new node's clockwise predecessor. Use background migration: new node serves traffic immediately, migrates data lazily. Cassandra `nodetool bootstrap` handles this automatically.
- "Hash collision between two nodes" → Two nodes hash to the same ring position. Solution: use double-hashing or include node index in the hash input. Alternative: explicitly assign tokens (Cassandra with `num_tokens` and token allocation algorithm) rather than random hash.

---

### ⚙️ How It Works (Mechanism)

**Ring data structure:**

```
Ring (0 to 2^32-1, shown as 0-100):

    0 ─── S1(10) ─── S2(35) ─── S3(60) ─── S4(85) ─── 100
    ↑                                                     │
    └─────────────────────────────────────────────────────┘
                    (wraps around: 100 → 0)

Key assignment (clockwise successor):
  key at pos 5  → S1 (10, first clockwise from 5)
  key at pos 20 → S2 (35, first clockwise from 20)
  key at pos 50 → S3 (60)
  key at pos 70 → S4 (85)
  key at pos 90 → S1 (10, wraps: 10 is first clockwise from 90)

Add S5 at position 50:
  Ring: S1(10) S2(35) S5(50) S3(60) S4(85)
  Keys previously at 36-50 (assigned to S3) → now S5
  All other keys unchanged

Remove S3 (pos 60):
  Ring: S1(10) S2(35) S4(85)
  Keys previously at 36-60 (assigned to S3) → now S4
```

**Replication (R=3, Cassandra-style):**

```
Key at pos 50 with R=3:
  Primary: S5 (50)
  Replica 1: S3 (60, next clockwise)
  Replica 2: S4 (85, next clockwise after S3)
Key is replicated to 3 consecutive clockwise nodes
Any of the 3 can serve reads (with quorum or eventual consistency)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL READ/WRITE FLOW (Cassandra-style):**

```
Client  Coordinator  Ring (S1=10, S2=35, S3=60, S4=85)
  │          │
  │─WRITE────▶│
  │ key='user:42'
  │           │ hash('user:42') = 48 → S3 primary
  │           │─write────────────────▶S3 (pos 60)
  │           │─replicate────────────▶S4 (pos 85)
  │           │─replicate─────────────────────────▶S1
  │◀──ACK─────│ (quorum of 2/3 replicas ACK'd)
  │           │        ← YOU ARE HERE
```

**FAILURE PATH (node added — migration):**
New node S5 added at position 50. S3 (60) was primary for keys 36-60. Keys 36-50 now belong to S5. Cassandra initiates "streaming": S3 streams keys 36-50 to S5. During streaming: keys can be read from S3 (still holds the data). After streaming: S5 owns range 36-50. S3 no longer replicates those keys.

**WHAT CHANGES AT SCALE:**
At scale: the ring lookup is O(log N) — trivial even for 1000 nodes. The challenge is DATA MIGRATION on topology change. For a 1TB Cassandra cluster (10 nodes, 100GB each): adding one node triggers migration of ~91GB from neighboring nodes. At 100MB/s network: ~15 minutes of background migration. During migration: no service disruption (old nodes still serve the migrating range). The real operational challenge is NOT the ring lookup — it's managing migration bandwidth without impacting production traffic.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Ring topology changes must be propagated to all nodes. Gossip protocol (DST-040) handles this in Cassandra: nodes gossip ring topology updates. A node that hasn't received the update may route to the wrong node. Solution: coordinator nodes always have up-to-date ring topology (they receive all gossip). Any node can be a coordinator and knows the full ring — clients connect to any node.

---

### 💻 Code Example

**BAD - Modulo hashing (catastrophic on topology change):**

```java
// Simple modulo: catastrophic on topology change
public class ModuloHashRouter {
    private List<Server> servers;

    public Server route(String key) {
        int idx = Math.abs(key.hashCode()) % servers.size();
        return servers.get(idx);
        // PROBLEM: add/remove one server
        // → servers.size() changes
        // → almost ALL keys rerouted
        // → cache invalidation storm
    }
}
```

**GOOD - Consistent hashing with TreeMap ring:**

```java
import java.util.TreeMap;
import java.security.MessageDigest;

public class ConsistentHashRouter {
    // Ring: sorted map of hash positions to servers
    private final TreeMap<Long, String> ring = new TreeMap<>();
    private final int virtualNodes;

    public ConsistentHashRouter(
            List<String> servers, int virtualNodes) {
        this.virtualNodes = virtualNodes;
        for (String server : servers) {
            addServer(server);
        }
    }

    public void addServer(String server) {
        // Add virtualNodes positions for each physical server
        // (virtual nodes = DST-039, improves load balance)
        for (int i = 0; i < virtualNodes; i++) {
            long hash = hash(server + "#" + i);
            ring.put(hash, server);
        }
        // Only keys between predecessor and new positions move
    }

    public void removeServer(String server) {
        for (int i = 0; i < virtualNodes; i++) {
            long hash = hash(server + "#" + i);
            ring.remove(hash);
        }
        // Only keys that were on removed positions move
        // (to their new clockwise successors)
    }

    public String route(String key) {
        if (ring.isEmpty()) return null;
        long hash = hash(key);
        // Find first server clockwise from key's position:
        Map.Entry<Long, String> entry =
            ring.ceilingEntry(hash);
        if (entry == null) {
            // Wrap around: key is past all nodes, use first
            entry = ring.firstEntry();
        }
        return entry.getValue();
        // O(log N) lookup — efficient even for 1000 nodes
    }

    private long hash(String key) {
        try {
            MessageDigest md5 =
                MessageDigest.getInstance("MD5");
            byte[] digest = md5.digest(
                key.getBytes(StandardCharsets.UTF_8));
            // Use first 8 bytes as long for ring position:
            long hash = ((long)(digest[3] & 0xFF) << 24)
                | ((long)(digest[2] & 0xFF) << 16)
                | ((long)(digest[1] & 0xFF) << 8)
                | ((long)(digest[0] & 0xFF));
            return hash & 0xFFFFFFFFL; // unsigned 32-bit
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }
    }
}
```

**How to test / verify correctness:**

```java
// Verify: adding a server affects only ~1/N keys
ConsistentHashRouter router =
    new ConsistentHashRouter(
        List.of("S1","S2","S3","S4"), 100);
Map<String, String> initialRouting = new HashMap<>();
for (int i = 0; i < 10000; i++) {
    String key = "key:" + i;
    initialRouting.put(key, router.route(key));
}
router.addServer("S5");
int changed = 0;
for (int i = 0; i < 10000; i++) {
    String key = "key:" + i;
    if (!router.route(key).equals(initialRouting.get(key)))
        changed++;
}
System.out.println("Keys changed: " + changed + "/10000");
// Expected: ~2000 (10000/5) = ~20%
// Modulo would change: ~8000 = ~80%
```

---

### ⚖️ Comparison Table

| Scheme               | Keys moved on add | Keys moved on remove | Lookup cost      | Use case                       |
| :------------------- | :---------------- | :------------------- | :--------------- | :----------------------------- |
| Modulo hashing       | O(K) — all keys   | O(K) — all keys      | O(1)             | Stable topology                |
| Consistent hashing   | O(K/N) — 1/N keys | O(K/N) — 1/N keys    | O(log N)         | Elastic clusters               |
| Jump consistent hash | O(K/N)            | O(K/N)               | O(log N)         | No ring — stateless routing    |
| Rendezvous hashing   | O(K/N)            | O(K/N)               | O(N) — all nodes | Small N, simple implementation |

---

### 🔁 Flow / Lifecycle

**Node Addition Lifecycle:**

1. **New node joins:** administrator or orchestrator assigns the new node to the ring (specific token position or auto-assigned).
2. **Ring propagated:** gossip protocol (DST-040) propagates the new ring topology to all existing nodes.
3. **Migration begins:** the new node's predecessor starts streaming (migrating) the key range now owned by the new node.
4. **Dual-serve period:** during migration, both the new node and the predecessor serve the migrating range (for read availability).
5. **Migration complete:** predecessor stops owning the migrated range. Ring is stable.
6. **New node fully active:** serves its full token range, participates in replication.

**Node Removal Lifecycle:**

1. **Node marked for removal:** decommission initiated (intentional) or node detected dead (gossip timeout).
2. **Ring updated:** gossip propagates the removal.
3. **Data migration:** the removed node's successor begins receiving the migrated range. Or (if intentional): node streams its data OUT before leaving.
4. **Node fully removed:** ring is stable with N-1 nodes.

---

### ⚠️ Common Misconceptions

| Misconception                                                   | Reality                                                                                                                                                                                                                                                                                                                                                              |
| :-------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Consistent hashing means equal load distribution"              | Without virtual nodes: arc lengths between nodes depend on hash values — inherently unequal. A node with a large arc handles proportionally more keys. Equal load requires virtual nodes (DST-039) — many positions per physical node, averaging out the arc lengths.                                                                                                |
| "Consistent hashing eliminates cache misses on topology change" | Consistent hashing REDUCES cache misses from ~100% (modulo) to ~1/N (1 node in N). It does not eliminate them. Adding a node always causes cache misses for the remapped ~1/N keys — but the miss rate is manageable vs catastrophic.                                                                                                                                |
| "Consistent hashing is only for caches"                         | Consistent hashing is a general data partitioning algorithm. Uses: Cassandra (storage), Kafka (partition assignment to consumers), CDN (server selection), load balancers (session persistence), Redis Cluster (hash slots — a variant of consistent hashing).                                                                                                       |
| "Redis Cluster uses consistent hashing"                         | Redis Cluster uses HASH SLOTS — 16,384 fixed slots, each assigned to a node. Keys are mapped to slots by `hash(key) % 16384`. This is NOT consistent hashing (it's modulo hashing on hash slots). However: adding/removing a node in Redis Cluster triggers slot migration (similar to consistent hashing migration). The disruption is configurable, not automatic. |
| "The ring hash function must be MD5"                            | Any good hash function works. Requirements: (1) uniform distribution over the ring space (2) deterministic (same input → same output). MD5 is common for consistent hashing, but MurmurHash3 (faster, better distribution) or xxHash are better choices for performance.                                                                                             |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Hot Spot from Uneven Ring Distribution**

**Symptom:** One Cassandra node consistently shows 3x the CPU and disk I/O compared to other nodes. Cassandra `nodetool tpstats` shows one node handling far more requests. Cluster appeared balanced when set up, but over time data is uneven.
**Root Cause:** Single-token consistent hashing: each node has one position on the ring. If the ring positions cluster together (hash collisions, similar server names producing similar hashes): some arcs are large (one node handles many keys), others small. Data distribution is proportional to arc length, not number of nodes.
**Diagnostic:**

```bash
# Check token distribution in Cassandra:
nodetool ring
# Shows each node's token and % data owned
# If any node shows >20% (for 10 nodes, expected ~10%):
# uneven distribution

# Check actual data distribution:
nodetool status
# "Load" column shows data each node holds
# Significant variance = hot spots

# For Redis: check memory distribution:
redis-cli --cluster check redis-host:6379
# Shows % of hash slots per node
# Variance indicates potential hotspots
```

**Fix:**
BAD: Single token per node (original Cassandra config).
GOOD: Enable virtual nodes (`num_tokens: 256` in cassandra.yaml). Each physical node gets 256 ring positions — arcs average out across many positions. Expected variance reduces from O(N) to O(sqrt(N)) with virtual nodes.
**Prevention:** Always use virtual nodes in new Cassandra deployments. For Redis Cluster: monitor slot distribution with `redis-cli --cluster info`.

**Failure Mode 2: Migration Storm on Rapid Topology Change**

**Symptom:** During a capacity expansion (adding 3 new Cassandra nodes simultaneously): all existing nodes show 100% disk read I/O and 80% network utilization for 30 minutes. Production read/write latency increases 10x. The expansion causes more downtime than it prevents.
**Root Cause:** Adding multiple nodes simultaneously triggers concurrent migration from multiple source nodes. Each source node streams data to the new nodes. If migration bandwidth is not throttled: production I/O is saturated by migration traffic. Multiple simultaneous migrations multiply the impact.
**Diagnostic:**

```bash
# Check Cassandra streaming operations:
nodetool netstats
# "Streaming" section: active streams, bytes transferred
# If Active = many, bytes/s = high → migration is ongoing

# Check I/O during migration:
iostat -x 1 5
# If %util > 80% on data disk during migration:
# migration is saturating I/O
```

**Fix:**
BAD: Adding multiple nodes at once without throttling.
GOOD: Add nodes one at a time. Throttle Cassandra streaming bandwidth: `nodetool setstreamthroughput 100` (100 MB/s cap). Allow each migration to complete before adding the next node.
**Prevention:** Add nodes during low-traffic periods. Use `cassandra.yaml: stream_throughput_outbound_megabits_per_sec: 200` to cap migration bandwidth permanently. Monitor migration ETA before starting the next node addition.

**Failure Mode 3: Security - Targeted Hash Key Attack to Overload a Node**

**Symptom:** An attacker sends millions of requests all mapping to the same ring position — overloading one specific node. Other nodes are idle while the targeted node is overwhelmed. The consistent hashing guarantees that all keys in a specific hash range go to the same node — creating an exploitable concentration.
**Root Cause:** If the hash function and ring topology are known (public or discoverable), an attacker can craft keys that hash to the same node's arc. All crafted keys go to the same physical node — a denial of service targeting one node while others are unaffected.
**Diagnostic:**

```bash
# Detect suspicious key distribution:
# Cassandra: check read requests per token range:
nodetool tpstats | grep "Read Stage"
# High rate on one node, low on others during attack

# Redis: check request rate per node:
redis-cli --cluster check redis-host:6379
# Unusual request distribution (not proportional to slots)

# Application: count unique keys per shard:
# If one shard receiving 90%+ of traffic: hash attack possible
```

**Fix:**
BAD: Predictable hash function with no key randomization.
GOOD: (1) Add random salt to key hashing (HMAC-based): `hash(salt + key)`. Attacker doesn't know the salt, cannot predict ring placement. (2) Rate limit per key: if any single key receives > threshold requests/s: throttle. (3) Virtual nodes: even if attacker targets one arc, the arc is small (with many virtual nodes), limiting overload to a fraction of one physical node.
**Prevention:** Treat the hash function as a security parameter. Use HMAC or salted hash for key-to-ring mapping in public-facing systems. Monitor per-shard request distribution for anomalies.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-006 - CAP Theorem (consistent hashing is a technique for distributed data placement; understanding CAP provides context for the trade-offs in distributed key-value stores that use it)

**Builds On This (learn these next):**

- DST-039 - Virtual Nodes (vnodes extend consistent hashing to improve load balance)

**Alternatives / Comparisons:**

- DST-039 - Virtual Nodes (the standard extension for consistent hashing)
- DST-040 - Gossip Protocol (how ring topology changes are propagated between nodes)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Keys and nodes on a ring;      |
|                  | key → first node clockwise     |
+------------------+--------------------------------+
| PROBLEM SOLVED   | Modulo hashing remaps all keys |
|                  | on topology change; consistent |
|                  | hashing remaps only K/N keys   |
+------------------+--------------------------------+
| KEY INSIGHT      | Topology changes are LOCAL:    |
|                  | only adjacent arc is affected  |
+------------------+--------------------------------+
| USE WHEN         | Elastic caches, distributed    |
|                  | databases, CDN server selection|
+------------------+--------------------------------+
| AVOID WHEN       | Fixed topology (N never changes|
|                  | → modulo is simpler + faster)  |
+------------------+--------------------------------+
| TRADE-OFF        | O(K/N) disruption on change    |
|                  | vs O(log N) lookup overhead    |
+------------------+--------------------------------+
| ONE-LINER        | Both keys and servers on ring; |
|                  | add server → only K/N move     |
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-039 Virtual Nodes,         |
|                  | DST-040 Gossip Protocol        |
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. Consistent hashing maps BOTH keys AND nodes to a circular ring. Keys are assigned to the first node clockwise.
2. Adding or removing one node affects only ~K/N keys (where N = node count). Modulo hashing affects all K keys. This is the essential advantage.
3. Without virtual nodes (DST-039): load distribution is uneven (arc length variance). With virtual nodes (256 positions per node): load is approximately equal across all physical nodes.

**Interview one-liner:**
"Consistent hashing places both data keys and server nodes on a circular hash ring. Each key is assigned to the first server encountered moving clockwise. When a server is added: only the keys between the new server and its predecessor move — approximately K/N keys. Modulo hashing remaps all K keys on any topology change. Consistent hashing is used in Cassandra, DynamoDB, and CDNs for elastic scaling. Single-position consistent hashing causes uneven load; virtual nodes (multiple ring positions per physical server) solve this."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Localize the impact of change. When designing systems that must change over time (add nodes, remove nodes, update configurations): design the data structure or assignment algorithm so that changes affect only the MINIMUM necessary set of elements. Consistent hashing's ring achieves this by making topology changes LOCAL — only adjacent elements are affected. The principle extends: local routing tables in networking (only neighbors updated on link change), incremental compilation (only files that changed are recompiled), event sourcing (only new events added, past events immutable). The common pattern: create a structure where the "blast radius" of a change is bounded and proportional to the change's scope, not to the total system size.

**Where else this pattern appears:**

- **CDN edge server selection:** CDNs like Akamai use consistent hashing to assign content URLs to edge servers. When an edge server is added or removed: only the content that was on that server's hash ring arc needs to be migrated. Most cached content stays on its current server. The "local disruption" principle enables CDN capacity expansion without global cache invalidation.
- **Kafka consumer group partition assignment:** Kafka uses a consistent-hashing-like algorithm (RangeAssignor, RoundRobinAssignor, StickyAssignor) to assign partitions to consumers. The StickyAssignor minimizes partition movement when consumers join or leave — implementing the "localize disruption" principle. Most partitions stay on their current consumer; only the "freed" partitions from a leaving consumer are redistributed.
- **Database sharding routing (ProxySQL, Vitess):** Database sharding routers use consistent hashing to route queries to shards. Adding a shard triggers migration of only the corresponding key range — not all data. Vitess (YouTube's MySQL sharding system) implements "resharding" that migrates one shard's range without affecting other shards — consistent hashing's local disruption property applied to SQL database scaling.

---

### 💡 The Surprising Truth

Consistent hashing was not invented for distributed databases or caches — it was invented for a completely different problem: making CDN (Content Delivery Network) routing resilient to server failures. Karger et al.'s 1997 paper at MIT was motivated by the problem of routing web requests to proxy caches when proxy servers fail. The paper's abstract doesn't mention databases, key-value stores, or distributed systems beyond CDN proxies. The algorithm became the foundation of distributed databases (Dynamo, Cassandra, Riak) only because Amazon's engineers read the paper while designing Dynamo in 2006-2007 and recognized that the ring property solved their elastic partitioning problem. The surprising truth: many of the most important algorithms in distributed databases were not designed by database researchers — they were invented by networking, CDN, or theoretical computer science researchers solving completely different problems. Consistent hashing, gossip protocols, vector clocks, and Bloom filters all originated outside the database field and were adopted by distributed database designers. Algorithm literacy across fields is a competitive advantage in distributed systems engineering.

---

### 🧠 Think About This Before We Continue

**Q1 (D - Root Cause):** A Cassandra cluster with 10 nodes and consistent hashing (no virtual nodes) has been running for 6 months. One node is now holding 35% of the total data while two others hold 2% each. The original setup used random token assignment. How did this happen? What would have happened differently if virtual nodes (num_tokens=256) had been used from the start? What is the correct remediation without downtime?
_Hint:_ Random token assignment: each node gets one random ring position. By chance (birthday paradox in reverse): some nodes end up adjacent (small arc = 2% data), others have large gaps (large arc = 35% data). The probability distribution of arc lengths with random positions is exponential — high variance. With virtual nodes (256 positions): each physical node gets 256 random positions, distributed across the ring. The law of large numbers: 256 samples average out, variance drops to ~1/256 of single-token variance. Remediation without downtime: enable virtual nodes requires decommissioning the heavy node (nodetool decommission), reconfiguring num_tokens, and re-joining as a new node with distributed virtual tokens.

**Q2 (A - System Interaction):** Redis Cluster does NOT use consistent hashing — it uses 16,384 fixed hash slots with modulo assignment (`hash(key) % 16384`). Yet Redis Cluster claims to support elastic scaling (adding/removing nodes). How does Redis Cluster achieve elastic scaling without consistent hashing? What is the unit of migration in Redis Cluster vs Cassandra with consistent hashing? When does one approach favor over the other?
_Hint:_ Redis Cluster: elastic scaling = SLOT MIGRATION, not ring migration. Hash slots are pre-assigned to nodes. Resharding = moving slot ownership from one node to another (explicit, administrator-initiated). Slot migration: `CLUSTER SETSLOT <slot> MIGRATING <target>` + `MIGRATE` commands. Cassandra: ring migration = automatic on node join/leave, no administrator needed. Unit of migration: Redis = hash slot (1/16384 of key space, explicit); Cassandra = token arc (dynamic, automatic). Redis Cluster advantage: predictable, controlled migration. Cassandra advantage: automatic, node-join triggers migration. Trade-off: operational control vs automation. For systems that need controlled migration schedules (compliance, window-based operations): Redis Cluster is better. For fully automated elastic scaling: Cassandra with virtual nodes is better.

**Q3 (C - Design Trade-off):** Jump consistent hashing (Google, 2014) achieves O(K/N) disruption without a ring, with O(log N) time and O(1) space. Standard consistent hashing needs O(N) space for the ring (or O(N × virtual_nodes) with vnodes). Compare: when would you choose jump consistent hashing vs standard ring-based consistent hashing? What capability does the ring provide that jump consistent hashing lacks?
_Hint:_ Jump consistent hashing: stateless (no ring data structure), fast (O(log N) time), O(1) space — just run the algorithm with (key, num_buckets). Limitation: only supports adding nodes at the end (num_buckets = num_buckets + 1). Cannot remove arbitrary nodes or remove specific nodes. Ring-based consistent hashing: supports arbitrary node removal and non-sequential addition (any position). Supports node-specific placement (important for rack awareness, geography-aware placement). Jump consistent hash advantage: embedded in request routing code without coordination. Ring advantage: flexible topology management. Use jump when: stateless routing with monotone node addition. Use ring when: arbitrary topology changes, node affinity/placement control, geographic-aware routing.

