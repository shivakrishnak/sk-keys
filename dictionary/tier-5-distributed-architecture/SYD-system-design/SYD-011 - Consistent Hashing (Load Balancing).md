---
id: SYD-011
title: "Consistent Hashing (Load Balancing)"
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-008, SYD-009
used_by: SYD-031
related: SYD-031, SYD-009, SYD-008
tags:
  - algorithm
  - deep-dive
  - distributed
  - advanced
status: complete
version: 3
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 11
permalink: /syd/consistent-hashing/
---

# SYD-011 - Consistent Hashing (Load Balancing)

⚡ TL;DR - A hashing technique that maps requests to servers using a ring structure, minimizing the data that must be moved when servers are added or removed-critical for distributed caches and databases.

| #686            | Category: System Design                                  | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------- | :-------------- |
| **Depends on:** | Hash Functions, Load Balancing, Distributed Systems      |                 |
| **Used by:**    | Distributed Caching, Sharding, Memcached, Redis Clusters |                 |
| **Related:**    | Hash Functions, Sharding, Rendezvous Hashing             |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You have 5 cache servers. You hash a key modulo 5: `hash(key) % 5` to pick which server stores it. Works great. But then traffic grows-you add a 6th server. Now the formula becomes `hash(key) % 6`. Almost every key hashes to a different server now! You must rehash every key in the entire cache, moving 83% of the data. Massive overhead. Every time you add/remove a server, reshuffling happens.

**THE BREAKING POINT:**
Simple modulo hashing doesn't scale. Adding one server causes cache invalidation storm.

**THE INVENTION MOMENT:**
"This is why consistent hashing was invented-add servers without reshuffling most data."

**EVOLUTION:**
Consistent hashing was invented by Karger et al. in 1997 to solve CDN cache invalidation at internet scale - when a cache server is added or removed, only 1/N of keys should move, not all of them. Amazon's Dynamo (2007) brought consistent hashing to production databases, making it a foundational distributed systems pattern. Modern implementations add token-based partitioning (Cassandra), bounded load (Google), and virtual node counts tuned to the expected cluster size. Today, consistent hashing is the default partitioning strategy for distributed caches, databases, and service mesh load balancers.

---

### 📘 Textbook Definition

Consistent hashing is a distributed hashing scheme where keys and servers are mapped to points on a ring (typically using a hash function mapping to a large integer space, e.g., 2^32 or 2^160). A key's assigned server is the next server clockwise on the ring. When a server is added/removed, only keys in the arc between the old and new server positions must be rehashed-typically 1/N of total keys (where N = number of servers), versus ~all keys with naive modulo hashing.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Place servers and keys on a circle; each key belongs to the next server clockwise. Adding one server only relocates ~1/N of keys.

**One analogy:**

> Imagine a clock face with 12 hours. You have 3 servers at 12, 4, and 8 o'clock. A key (say, "user_123") hashes to 2 o'clock. It belongs to the next server clockwise: Server at 4 o'clock. Add a new server at 6 o'clock. Now keys between 4 and 6 (old boundary) move to the new server. Keys between 6 and 8 stay with the 8 o'clock server. Only a slice moves, not everything.

**One insight:**
Consistent hashing is elegant but not magic-it reduces rehashing from 100% to ~1/N. Memcached, Redis Cluster, and DynamoDB use it to scale without cache invalidation storms.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Hash space is a circle (ring) with a fixed, large size (e.g., 2^160)
2. Both keys and servers hash to points on this ring
3. A key's owner is the first server encountered clockwise from the key's hash
4. Removing/adding servers affects only a contiguous arc of keys

**DERIVED DESIGN:**
Hash each server's ID to a point on the ring (e.g., SHA1(server_ip) → 160-bit integer, mapped to [0, 2^160)). Hash each key's name the same way. For a key, find its hash value, then scan clockwise on the ring until you hit a server. That server owns the key. When you add a server, only keys between the new server and the next server (clockwise) must migrate. All other keys stay put. This dramatically reduces data movement.

**THE TRADE-OFFS:**
**Gain:** Adding/removing servers causes minimal data movement (~1/N keys). Scales gracefully. Predictable and deterministic.

**Cost:** Slightly uneven distribution (some servers may own more keys due to hashing randomness). Requires hash ring management. Hot spots can still occur if many keys hash nearby. Complexity > simple modulo.

---

### 🧪 Thought Experiment

**SETUP:**
5 cache servers. 1 million keys. Using `hash(key) % 5`. All servers have ~200K keys.

**SCENARIO 1: ADD 6TH SERVER (WITHOUT CONSISTENT HASHING)**
New formula: `hash(key) % 6`. Each key rehashes. Expected: 833K keys (~83%) move to different servers. Must migrate 833K keys from old servers to new ones. During migration: cache misses spike, database gets hit hard, latency increases 10x. Takes hours to stabilize.

**SCENARIO 2: ADD 6TH SERVER (WITH CONSISTENT HASHING)**
Place all 6 servers on a ring. New server occupies a position. Keys in the arc from previous server to new server migrate. Expected: ~166K keys (1/6 of total) move. During migration: 166K cache misses (vs 833K). Database load increases, but manageable. Takes minutes.

**THE INSIGHT:**
Consistent hashing makes scaling graceful instead of catastrophic.

---

### 🧠 Mental Model / Analogy

> Imagine a round table with 12 seats. Guests (keys) arrive and sit at the closest seat clockwise. When a new seat is added, only guests between the old and new seats must move. Everyone else stays in their seat. With naive seating (modulo), you'd reshuffle the entire table.

- "Seats at table" → servers on ring
- "Guests" → keys
- "Sitting at closest seat clockwise" → hash → find next server clockwise
- "Adding a seat" → adding a server
- "Guests between old and new" → keys that migrate

**Where this analogy breaks down:** Real tables aren't perfectly round; real hashes can have collisions. But the mental model captures the essence.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Instead of assigning keys randomly, use a formula that remembers where each key is. When you add a new server, only some keys move. Most stay where they are.

**Level 2 - How to use it (junior developer):**
Use a consistent hashing library (Memcached client, Redis Cluster client). When initializing, pass the list of servers. The library handles ring creation. Add a key: `cache.set(key, value)`. The library hashes the key to a server automatically. Add a new server to the pool. The library rebalances; some keys move automatically (or lazily on access).

**Level 3 - How it works (mid-level engineer):**
Create a hash ring: sort all servers by hash(server_id). For each key, compute hash(key), find the position on the ring, do binary search to find the next server >= hash(key). That server owns the key. When adding a server: insert into sorted list, find affected keys (those between old and new boundary), migrate them. Optimization: replicate each key to K servers for fault tolerance (key lives on next K servers clockwise, not just one).

**Level 4 - Why it was designed this way (senior/staff):**
Consistent hashing solved a fundamental problem in distributed systems: scaling without invalidation. Introduced by Karger et al. (1997) for Akamai CDN. The elegance is mathematical-the ring structure ensures any hash function has the property. Modern improvements include virtual nodes (replicate each server N times on the ring for better distribution) and weighted hashing (give some servers more virtual nodes if they're more powerful).

---

### ⚙️ How It Works (Mechanism)

Consistent hashing operation:

```
RING SETUP (2^32 space, simplified to 0–360 degrees):
  hash(Server1) → 30°
  hash(Server2) → 120°
  hash(Server3) → 240°
  Servers sorted: [30, 120, 240]

KEY LOOKUP:
  hash(key1) → 50°  → next server clockwise → Server2 (120°)
  hash(key2) → 150° → next server clockwise → Server3 (240°)
  hash(key3) → 280° → next server clockwise → Server1 (30°, wrapped)

ADD NEW SERVER:
  hash(Server4) → 180°
  Sorted: [30, 120, 180, 240]

  Keys that were going to Server3 (240°) and hashed 120°–180°
    now go to Server4 (180°)
  Keys hashed 180°–240° still go to Server3 (240°)
  All other keys: no change

  Result: Only keys in arc [120°, 180°] migrate (~1/4 of keys between old servers)
```

**In Happy Path:**
Request arrives with key → Hash key → Find server on ring → Request served from cache → Hit rate maintained.

**When Something Goes Wrong:**
Server fails → Remove from ring → Keys that were on it rehash to next server clockwise → Automatic failover. Existing keys lost (cache miss), but no corruption.

---

### 🔄 The Complete Picture - End-to-End Flow

```
Client Request (cache.get(key))
    ↓
Hash the key: hash(key) → position on ring
    ↓
CONSISTENT HASHING LOOKUP (YOU ARE HERE)
Find next server clockwise from position
    ↓
Send request to that server
    ↓
Server checks cache
    ├─ Cache hit: return value
    └─ Cache miss: fetch from DB, cache it, return value

Scale-Out Path:
    New server added to cluster
    ↓
    Update ring: insert new server in sorted order
    ↓
    Identify keys in migration arc
    ↓
    Background: migrate keys to new server
    ↓
    (Or lazy: let misses happen, refetch from DB on first access post-migration)
    ↓
    System scales with minimal disruption
```

**WHAT CHANGES AT SCALE:**
At 1 million keys with 10 servers, adding 1 new server causes ~100K key migrations. At 1 billion keys with 100 servers, adding 1 new server causes ~10M migrations-but this is 1% of total. At extreme scale (petabytes of data across 10K servers), even migrating 0.01% is significant. Optimization: use virtual nodes (each server mapped N times on ring) for better granularity and faster convergence.

---

### 💻 Code Example

Consistent hashing requires careful implementation. Libraries exist:

**Example 1 - Using Memcached Client (Consistent Hashing Built-in):**

```python
from pymemcache.client.hash import HashClient

# Create client with 3 servers
client = HashClient([
    ('server1.internal', 11211),
    ('server2.internal', 11211),
    ('server3.internal', 11211),
])

# Set a key-automatically goes to consistent-hashed server
client.set(b'user_123', b'{"name": "Alice"}')

# Get key-automatically looks up from consistent-hashed server
value = client.get(b'user_123')  # Returns from same server

# Add a new server-keys rebalance automatically
client = HashClient([
    ('server1.internal', 11211),
    ('server2.internal', 11211),
    ('server3.internal', 11211),
    ('server4.internal', 11211),  # NEW
])
# Only ~25% of keys rehash
```

**Example 2 - Simple Consistent Hashing Implementation:**

```python
import hashlib
import bisect

class ConsistentHash:
    def __init__(self, servers, virtual_nodes=3):
        self.servers = servers
        self.virtual_nodes = virtual_nodes
        self.ring = {}
        self.sorted_keys = []
        self._build_ring()

    def _hash(self, key):
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def _build_ring(self):
        self.ring = {}
        for server in self.servers:
            for i in range(self.virtual_nodes):
                virtual_key = f"{server}:{i}"
                hash_val = self._hash(virtual_key)
                self.ring[hash_val] = server

        self.sorted_keys = sorted(self.ring.keys())

    def get_server(self, key):
        hash_val = self._hash(key)
        idx = bisect.bisect_right(self.sorted_keys, hash_val)
        if idx == len(self.sorted_keys):
            idx = 0  # Wrap around
        return self.ring[self.sorted_keys[idx]]

    def add_server(self, server):
        self.servers.append(server)
        self._build_ring()

    def remove_server(self, server):
        self.servers.remove(server)
        self._build_ring()

# Usage:
ch = ConsistentHash(['server1', 'server2', 'server3'])
print(ch.get_server('user_123'))  # → 'server1' (or one of the 3)

ch.add_server('server4')
print(ch.get_server('user_123'))  # → Still 'server1' (unless in migration arc)
```

**Example 3 - Redis Cluster (Uses Consistent Hashing):**

```python
from redis.cluster import RedisCluster

# Create Redis cluster with 3 nodes
nodes = [
    {"host": "redis1.internal", "port": 6379},
    {"host": "redis2.internal", "port": 6379},
    {"host": "redis3.internal", "port": 6379},
]
rc = RedisCluster(startup_nodes=nodes, decode_responses=True)

# Set key-goes to consistent-hashed node
rc.set("user:123", '{"name": "Alice"}')

# Get key-from same consistent-hashed node
value = rc.get("user:123")

# Add new node-cluster rebalances automatically
# (Redis cluster adds the node and migrations happen in background)
```

---

### ⚖️ Comparison Table

| Hashing Scheme         | Data Movement on Add             | Complexity          | Best For                     | Overhead                      |
| ---------------------- | -------------------------------- | ------------------- | ---------------------------- | ----------------------------- |
| **Modulo (hash % N)**  | ~100% of keys (all rehash)       | O(1)                | Toy systems                  | Low                           |
| **Consistent Hashing** | ~1/N of keys                     | O(log N) per lookup | Distributed caches, clusters | Medium (ring management)      |
| **Rendezvous Hashing** | ~1/N of keys                     | O(N) per lookup     | Some use cases               | Medium                        |
| **Virtual Nodes**      | ~1/N of keys (finer granularity) | O(log N) per lookup | Production clusters          | Higher (more objects on ring) |

**How to choose:** Use consistent hashing for any distributed cache or partitioned database. Use virtual nodes for even distribution. Modulo only for non-distributed systems where rebalancing is rare.

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                                                                           |
| -------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| "Consistent hashing has zero data movement on rebalance" | Moving 1/N of keys is still significant at scale. If 1 billion keys, adding server = 250M key migrations. Not zero.               |
| "Consistent hashing perfectly distributes load"          | No. If servers hash unevenly, load becomes uneven. Use virtual nodes to improve distribution.                                     |
| "All clients use the same consistent hash"               | Must be true. If one client hashes differently, keys map to wrong servers-corruption/misses. All clients must use same algorithm. |
| "Consistent hashing solves all scaling problems"         | Solves key-to-server mapping only. Database bottleneck, cache invalidation logic, and other issues remain unsolved.               |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Server Fails, Keys Lost**

**Symptom:**
Server 2 crashes. Keys that were on Server 2 are lost (cache miss). Clients fail over to Server 3 (next clockwise). Database queries spike. Latency increases 10x for 1/N of requests.

**Root Cause:**
Consistent hashing maps keys to single server (no replication by default). Single server failure = data loss.

**Diagnostic Command:**

```bash
# Check which keys were on Server 2
# (Requires logging or external discovery)

# Check cache hit rate drop
redis-cli --stat
# Hit rate drops from 95% to 70% (20% of keys lost to Server 2)

# Check DB query rate spike
SELECT COUNT(*) FROM query_log WHERE timestamp > now() - INTERVAL 1 hour;
# Spike by ~25% (failover requests)
```

**Fix:**
Bad approach: Accept data loss.
Good approach: (1) Replicate keys to K next servers clockwise (K=3 is common). (2) Implement persistence (if cache misses, fetch from DB and cache). (3) Add health monitoring; remove dead servers from ring quickly.

**Prevention:**
Always replicate to K ≥ 3 servers. Implement circuit breaker to isolate failed servers. Set up monitoring for cache hit rate drops.

---

**Failure Mode 2: Uneven Key Distribution**

**Symptom:**
Hash space is [0, 2^32). Servers hash to: 100, 500, 10,000. Keys are uneven: Server 1 (100–500) has 400 keys, Server 2 (500–10K) has 9500 keys, Server 3 (10K–2^32) has rest. Massive imbalance.

**Root Cause:**
Servers hash unevenly on the ring. Some servers get huge arcs, others small.

**Diagnostic Command:**

```bash
# Check ring layout
for server in servers:
    hash_val = hash(server)
    print(f"{server}: {hash_val}")

# If hashes are clustered: imbalance
```

**Fix:**
Bad approach: Accept imbalance and let some servers be overloaded.
Good approach: Use virtual nodes. Map each server N times (e.g., 3 times). Now: server1 at [100, 500, 700], server2 at [5000, 5001, 5002], etc. Spreads servers across ring. Much more even distribution.

**Prevention:**
Always use virtual nodes (default in modern libraries). Set virtual_nodes ≥ 100 for large clusters (1000+ servers), ≥ 3 for small clusters.

---

**Failure Mode 3: Inconsistent Hashing Across Clients**

**Symptom:**
Client A hashes key "user_123" → Server 1. Client B hashes same key → Server 2. They're asking different servers. Data corruption/inconsistency.

**Root Cause:**
Clients use different hash functions, or servers are added/removed at different times, resulting in different ring layouts.

**Diagnostic Command:**

```bash
# Verify consistent hash from all clients
for client in all_clients:
    server = client.get_server("test_key")
    print(f"Client {client}: test_key → {server}")

# If servers differ: inconsistency
```

**Fix:**
Bad approach: Ignore and accept inconsistency.
Good approach: (1) Centralize ring management (shared config server). (2) All clients read same server list + same hash algorithm from config. (3) On server changes, all clients update ring atomically. (4) Use version numbers to ensure all clients are synchronized.

**Prevention:**
Have a single source of truth for server list (config server, service discovery). Clients pull it on startup and when it changes. Version each ring. Clients only accept requests if ring version matches server.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-008 - Load Balancing]] - the distribution problem this solves
- [[SYD-009 - Round Robin]] - the simpler algorithm to compare against

**Builds On This (learn these next):**
- [[SYD-031 - Sharding (System)]] - uses consistent hashing to partition data across nodes

**Alternatives / Comparisons:**
- [[SYD-009 - Round Robin]] - simpler, no affinity, correct for stateless workloads
- [[SYD-010 - Least Connections]] - adaptive but no cache/session affinity

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Map keys to servers on a ring;      │
│              │ minimize data movement on scaling    │
├──────────────┼────────────────────────────────────────┤
│ PROBLEM IT   │ Adding servers causes ~100% of       │
│ SOLVES       │ cache keys to rehash (modulo);       │
│              │ cascade invalidation storm           │
├──────────────┼────────────────────────────────────────┤
│ KEY INSIGHT  │ Only keys in arc between old and     │
│              │ new server must migrate (~1/N);      │
│              │ rest unaffected                      │
├──────────────┼────────────────────────────────────────┤
│ USE WHEN     │ Distributed cache, partitioned DB,   │
│              │ cluster that grows/shrinks           │
├──────────────┼────────────────────────────────────────┤
│ AVOID WHEN   │ Data never moved (static cluster);   │
│              │ complete rebalancing acceptable      │
├──────────────┼────────────────────────────────────────┤
│ TRADE-OFF    │ [Graceful scaling] vs [ring          │
│              │ complexity, potential imbalance]     │
├──────────────┼────────────────────────────────────────┤
│ ONE-LINER    │ "Place servers on a ring; only      │
│              │ keys in the new arc move."          │
├──────────────┼────────────────────────────────────────┤
│ NEXT EXPLORE │ Sharding → Virtual Nodes →           │
│              │ Rendezvous Hashing                   │
└──────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Minimise the amount of work required to rebalance when the cluster changes. This principle appears in every partitioning system: database sharding adds extra partitions for flexibility, Kafka over-partitions topics to allow consumer rebalancing, and virtual nodes in consistent hashing absorb failures without full rehashing. The invariant: design for change with minimal disruption.

**Where else this pattern appears:**
- **Cassandra token ring:** Each node owns a range of tokens on a consistent hash ring - adding a node splits existing ranges rather than redistributing all data.
- **Redis Cluster:** Uses a 16,384-slot consistent hashing variant where slots are assigned to nodes and migrate incrementally when nodes are added.
- **CDN edge routing:** Consistent hashing routes requests for the same URL to the same edge server - maximising cache hit rate across the fleet.

---

### 💡 The Surprising Truth

The original consistent hashing paper by Karger et al. was written specifically to solve the CDN cache problem: when a web cache server is added or removed, how do you avoid invalidating all cached content? The ring abstraction solved a CDN problem but became the foundation of every major distributed database. Cassandra, Riak, Amazon DynamoDB, and CockroachDB all use consistent hashing variants - not because of load balancing but because of the CDN insight about minimising key movement during cluster topology changes.

---

### 🧠 Think About This Before We Continue

**Q1.** With consistent hashing, adding one server rehashes ~1/N keys. With N=1000 servers and 1 billion keys, that is 1 million migrations. They happen in the background. But what if a client queries a key that hasn't migrated yet - it's still on the old server? How does the system handle this during the migration window?

*Hint:* Think about what migrated means from the client's perspective - does the client know which server owns a key, and how quickly does migration happen? Explore whether the migration is atomic (all-at-once switch) or gradual (background copy with dual reads).

**Q2.** A server crashes. Keys map to next server clockwise (automatic failover). But if you add a replacement server at the same position on the ring, old keys migrate back. What happens to data on the new server - is it overwritten? How do you handle keys on two servers temporarily?

*Hint:* Think about what happens to data on the replacement server when old keys migrate back - do clients write to the new server before, during, or after the migration? Explore how distributed databases handle this with read repair or hinted handoff.

**Q3 (Root Cause):** A consistent hashing ring has 10 servers. Server 5 is removed. Server 6 now owns all of Server 5's keys. Server 6's load triples and it starts to slow down. How does this hotspot form, and what prevents it in production systems?

*Hint:* Think about how many virtual nodes each server has and whether virtual node distribution was uniform across the ring. Explore how bounded load extensions to consistent hashing cap the maximum load ratio on any single server.
