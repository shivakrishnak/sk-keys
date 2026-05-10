---
version: 2
layout: default
title: "Redis Cluster"
parent: "Caching"
grand_parent: "Technical Dictionary"
nav_order: 33
permalink: /caching/redis-cluster/
id: CCH-017
category: Caching
difficulty: ★★★
depends_on: Distributed Cache, Consistent Hashing in Cache, Redis Data Structures
used_by: System Design, Distributed Systems, Caching
related: Distributed Cache, Consistent Hashing in Cache, Memcached vs Redis
tags:
  - caching
  - redis-cluster
  - sharding
  - failover
  - deep-dive
---

# CCH-041 - Redis Cluster

⚡ TL;DR - Redis Cluster horizontally shards data across multiple primary nodes using **16,384 hash slots** (`CRC16(key) % 16384`), each node owns a range of slots; each primary has replicas for failover; the gossip protocol keeps all nodes informed of cluster topology; clients receive `MOVED` redirects when they hit the wrong node; multi-key operations require keys to be in the same hash slot (use hash tags `{tag}:key`).

| #493            | Category: Caching                                                     | Difficulty: ★★★ |
| :-------------- | :-------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Distributed Cache, Consistent Hashing in Cache, Redis Data Structures |                 |
| **Used by:**    | System Design, Distributed Systems, Caching                           |                 |
| **Related:**    | Distributed Cache, Consistent Hashing in Cache, Memcached vs Redis    |                 |

---

### 🔥 The Problem This Solves

**SINGLE REDIS NODE CAPACITY LIMITS:**
A single Redis node handles everything - but memory is bounded (~50-100GB practical), write throughput is single-threaded (one command at a time), and it's a single point of failure. For large-scale systems: sharding across multiple nodes is required. Redis Cluster provides this natively, with automatic failover and client-transparent routing.

**MANUAL SHARDING IS ERROR-PRONE:**
Without Redis Cluster, engineers implement client-side sharding manually (consistent hashing library). Problems: complex failover logic, manual rebalancing, no automatic replica promotion. Redis Cluster handles all of this built-in.

---

### 📘 Textbook Definition

**Redis Cluster** is Redis's built-in horizontal scaling solution that provides data sharding across multiple nodes with automatic partitioning, replication, and failover. **Architecture**: N primary nodes, each owning a range of the 16,384 hash slots. Each primary has M replicas (typically 1-2). The cluster uses a **gossip protocol** for node discovery, health monitoring, and topology dissemination. **Key routing**: `HASH_SLOT = CRC16(key) % 16384`. Clients receive `MOVED` redirects when they contact the wrong node; cluster-aware clients (Lettuce, Jedis cluster mode) learn the topology and route directly without redirects after the first miss. **Failover**: if a primary doesn't respond within `cluster-node-timeout` (default 15s), replicas initiate election. A replica gets promoted if it receives votes from the majority of masters in the cluster. **Multi-key limitations**: keys in different hash slots cannot be used in atomic operations (MGET, MSET, transactions, Lua scripts). **Hash tags**: `{tag}` in a key name causes the hash to be computed on the tag only - guaranteeing all keys with the same tag land in the same slot. **Minimum cluster size**: 3 primaries (for majority quorum). Recommended: 6 nodes (3 primaries + 3 replicas).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Redis Cluster = automatic sharding across N nodes with 16,384 hash slots, per-shard replication, gossip protocol, and automatic failover - horizontal Redis at scale.

**One analogy:**

> Redis Cluster is like a post office system with multiple branch offices. The central director (no single director - gossip protocol means all branches know about each other) divides all possible zip codes (16,384 hash slots) among the branches. Each letter (key) is delivered to the branch that handles its zip code. If a branch closes (primary fails), its sister office (replica) takes over its zip codes. Mailing a package to two zip codes handled by different branches requires separate trips - you can't do it in one (CROSSSLOT limitation).

**One insight:**
Cluster-aware clients (Lettuce, Jedis) maintain an in-memory copy of the cluster topology (which node owns which slots). They route requests directly to the correct node without asking the cluster. When the topology changes (node failure, reshard), the client receives `MOVED` or `ASK` redirects - signals to update its topology map. After topology refresh, routing is direct again. This is why Lettuce's `adaptive.refresh` is important: without it, the client's topology map grows stale after cluster changes.

---

### 🔩 First Principles Explanation

**CLUSTER SETUP AND KEY ROUTING:**

```bash
# Create a 6-node Redis Cluster (3 primaries + 3 replicas)
redis-cli --cluster create \
  node1:6379 node2:6379 node3:6379 \
  node4:6379 node5:6379 node6:6379 \
  --cluster-replicas 1
# --cluster-replicas 1: each primary gets 1 replica
# Redis auto-assigns slots: node1=0-5460, node2=5461-10922, node3=10923-16383

# Verify cluster:
redis-cli -c -h node1 CLUSTER INFO
# cluster_state: ok
# cluster_slots_assigned: 16384
# cluster_known_nodes: 6
# cluster_size: 3

redis-cli -c -h node1 CLUSTER NODES
# Lists all nodes, their roles (master/slave), and slot ranges
# b4b4d... node1:6379@16379 myself,master - 0 0 1 connected 0-5460
# a1c9f... node2:6379@16379 master - 0 0 2 connected 5461-10922
# f2d8e... node3:6379@16379 master - 0 0 3 connected 10923-16383
# <replicas...>

# Test key routing:
redis-cli -c -h node1 CLUSTER KEYSLOT product:42
# → 7842 (slot for this key)

redis-cli -c -h node1 CLUSTER KEYSLOT "{product:42}:detail"
# → 7842 (same slot - hash computed on "product:42" tag)
```

**SPRING BOOT + LETTUCE CLUSTER CLIENT:**

```yaml
# application.yml
spring:
  data:
    redis:
      cluster:
        nodes:
          - node1:6379
          - node2:6379
          - node3:6379
          # Seed nodes - client discovers full topology via CLUSTER NODES
        max-redirects: 3 # Follow MOVED/ASK redirects (max 3 hops)
      lettuce:
        cluster:
          refresh:
            adaptive: true # Auto-refresh topology on MOVED/ASK signals
            period: 30s # Proactive refresh every 30s (catches silent topology changes)
        pool:
          max-active: 8 # Per-node connection pool
          max-idle: 4
          min-idle: 1
```

```java
// MOVED redirect: sent by Redis when client contacts wrong node
// Client sends: GET product:42 to node1
// Key hashes to slot 7842 → owned by node2
// node1 responds: MOVED 7842 node2:6379
// Lettuce: updates topology → sends next request directly to node2 ✓

// ASK redirect: temporary, during key migration (reshard in progress)
// Slot being migrated from node2 to node4
// During migration: key may be on node2 (not yet migrated) or node4 (migrated)
// node2 responds: ASK 7842 node4:6379
// Lettuce: sends to node4 with ASKING prefix (one-time redirect, not topology update)
// After migration complete: MOVED directive updates permanently

// Cluster info via client:
@Autowired private RedisClusterConnection clusterConn;

public void checkClusterHealth() {
    ClusterInfo info = clusterConn.clusterGetClusterInfo();
    log.info("Cluster state: {}", info.getState());  // Should be "ok"
    log.info("Slots assigned: {}", info.getSlotsAssigned());  // Should be 16384
}
```

**GOSSIP PROTOCOL:**

```
Redis Cluster gossip: all nodes exchange state with each other

Every second (gossip interval):
  Each node sends PING to a few random other nodes
  PING contains: sender's view of all known nodes (ids, addresses, states, epochs)
  Receiver: PONG response with its own view

  Exchange detects:
  - New nodes not yet known to some members
  - Node state changes (PFAIL → FAIL)
  - Epoch updates (after failovers)

Node failure detection:
  Node X doesn't respond to PING within cluster-node-timeout (15s)
  → Sender marks X as PFAIL (Probable Failure)
  → Sender gossips PFAIL status to others
  → If majority of masters report X as PFAIL within 2× cluster-node-timeout:
    → X is marked FAIL (confirmed failure) by the cluster
    → X's replicas initiate failover election

Failover election:
  X's replica R asks all masters for election vote
  Condition: R's replication offset (how up-to-date it is) is recent
  If R receives votes from majority of masters → promoted to primary
  Other replicas become replicas of new primary R

  Timeline: cluster-node-timeout (15s) for PFAIL + election overhead = ~30s total
```

**MULTI-KEY OPERATIONS AND HASH TAGS:**

```java
// PROBLEM: MGET on keys in different slots → CROSSSLOT error
List<String> keys = List.of("user:42:profile", "user:42:orders");
// user:42:profile → CRC16("user:42:profile") % 16384 = some slot on node 1
// user:42:orders  → CRC16("user:42:orders") % 16384 = different slot on node 3
// MGET(keys) → RedisCommandExecutionException: CROSSSLOT

// FIX: Hash tags ensure both keys map to same slot
List<String> taggedKeys = List.of("{user:42}:profile", "{user:42}:orders");
// Both hash on "user:42" → same slot → same node
// MGET(taggedKeys) → works ✓

// In code:
public static String userProfileKey(String userId) {
    return "{user:" + userId + "}:profile";  // "{user:42}:profile"
}
public static String userOrdersKey(String userId) {
    return "{user:" + userId + "}:orders";   // "{user:42}:orders"
}

// MGET now works:
List<Object> results = redisTemplate.opsForValue()
    .multiGet(List.of(userProfileKey("42"), userOrdersKey("42")));
// → [profile data, orders data] - same node, no CROSSSLOT ✓

// IMPORTANT: only one {} hash tag per key is honored
// "{user}:{42}" → hash on "user" (the first {})
// "{user:42}" → hash on "user:42"
// Hash tags should be the natural grouping unit (user, tenant, order)
```

**CLUSTER MONITORING:**

```bash
# Key commands for cluster health monitoring

# Overall cluster health
redis-cli -c -h node1 CLUSTER INFO
# cluster_state: ok         (or fail if any slots uncovered)
# cluster_slots_ok: 16384   (slots with primary + replicas)
# cluster_slots_pfail: 0    (slots with probable-fail primary)
# cluster_slots_fail: 0     (slots with confirmed-fail primary)
# cluster_stats_messages_ping_sent: 12345  (gossip ping count)

# Node-level stats
redis-cli -h node2 INFO replication
# role: master
# connected_slaves: 1
# slave0: id=...,ip=node5,port=6379,state=online,offset=12345,lag=0
# master_replid: ...
# master_repl_offset: 12345

# Slot distribution - verify even distribution
redis-cli -c -h node1 CLUSTER NODES | awk '{print $3, $9}'
# Should show: 3 masters with ~5461 slots each

# Alert conditions:
# cluster_state != ok → some slots are down → investigate immediately
# cluster_slots_pfail > 0 → node(s) not responding → possible failure in progress
# Replication lag > 0 → replica is behind → data loss risk on failover
```

---

### 🧪 Thought Experiment

**NETWORK PARTITION: CLUSTER BRAIN SPLIT**

Setup: 3 primaries + 3 replicas across 2 data centers (DC1: primary 1,2 + replicas; DC2: primary 3 + replicas).

Network partition at T=0: DC1 and DC2 lose connectivity. From DC2's perspective: primary 1 and 2 are PFAIL (no PING response). From DC1's perspective: primary 3 is PFAIL.

`cluster-require-full-coverage yes` (default): Once any slot is marked FAIL (not just PFAIL), ALL primaries stop accepting writes. DC1's nodes: stop writes (can't confirm DC2 is alive). DC2's node: stops writes (can't confirm DC1 is alive). Both sides go read-only. Consistency preserved; availability lost for writes during partition.

`cluster-require-full-coverage no`: Each partition continues serving its own slots. DC1 serves slots of primaries 1,2. DC2 serves slots of primary 3. After partition heals: conflict resolution via Raft-like epoch comparison. The partition with more masters "wins". This is a brain-split scenario - potential data divergence. Tradeoff: availability during partition at the cost of potential data conflicts.

---

### 🧠 Mental Model / Analogy

> Redis Cluster is a distributed database shard map. Imagine dividing all possible keys into 16,384 numbered bins (hash slots). Each bin is assigned to one primary server (with one or more backup servers). To find any key: compute its bin number (CRC16 mod 16384), then look at the bin-to-server assignment table. If a server fails, its backup takes over its bins. Clients keep a copy of the bin-to-server table and update it when they receive a "wrong bin" error (MOVED/ASK). The gossip protocol keeps all servers' tables in sync.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Redis Cluster: 16,384 slots across N primaries. Each key → `CRC16(key) % 16384` → slot → primary node. Each primary has replicas. Failure: replica promoted to primary after ~30s. Client: Lettuce handles MOVED/ASK redirects automatically.

**Level 2:** Configure Spring Boot: `spring.data.redis.cluster.nodes`, `lettuce.cluster.refresh.adaptive=true`. Use hash tags `{tag}:key` for multi-key operations. Monitor: `CLUSTER INFO` for `cluster_state:ok`. Alert on `cluster_slots_fail > 0`. Minimum 3 primaries for quorum. Recommended: 6 nodes.

**Level 3:** Write operations: always go to primary. Read operations: can go to replicas with `READONLY` command (eventual consistency, may be stale). Pipeline with cluster: Lettuce batches commands per-node (same-slot commands in one batch, cross-slot commands in separate batches). Cluster size scaling: `redis-cli --cluster reshard` migrates slots live - no downtime, but increases latency during migration for affected slots.

**Level 4:** Redis Cluster's consistency model: sync replication is NOT used by default (unlike Zookeeper/etcd). Writes are replicated asynchronously. On primary failure, if the replica hasn't received the last N writes: those writes are lost. This is **bounded data loss** - acceptable for cache use cases (worst case: cache miss) but NOT for durable data. `WAIT N TIMEOUT` command: forces synchronous replication to N replicas before returning - trades latency for durability. For absolute durability: don't use Redis Cluster as a primary datastore; use a RDBMS with Redis Cluster as a cache in front. Redis Cluster's epoch system ensures that after a brain split heals, the cluster with the higher epoch "wins" - but data written to the losing partition is lost. This is a CAP-CP design (prioritize consistency + partition tolerance over availability).

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ REDIS CLUSTER: FULL PICTURE                          │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Primary 1        Primary 2        Primary 3         │
│  slots: 0-5460    5461-10922       10923-16383        │
│  Replica 4        Replica 5        Replica 6         │
│                                                      │
│  Client: SET product:42 {data}                       │
│  CRC16("product:42") % 16384 = 7842                  │
│  [CLUSTER ← YOU ARE HERE: slot 7842 → Primary 2]     │
│  Lettuce: routes to Primary 2 directly               │
│  Primary 2: SET key → async replicate to Replica 5  │
│                                                      │
│  Primary 2 fails (T=0):                              │
│  Gossip: other nodes mark P2 as PFAIL (T+15s)        │
│  Gossip: majority confirms FAIL (T+30s)              │
│  Replica 5: election → wins → becomes new Primary 2  │
│  Slots 5461-10922 now on Replica 5 (new primary)     │
│  Lettuce: receives MOVED → updates topology          │
│  Client: routes to new Primary 2 (former Replica 5)  │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
RESHARD: ADD NODE 4 TO 3-NODE CLUSTER

T=0: Cluster has 3 primaries, each ~5461 slots
T=1: Admin adds node4 to cluster:
     redis-cli --cluster add-node node4:6379 node1:6379

T=2: Admin reshards: move ~4096 slots to node4
     redis-cli --cluster reshard node1:6379 --cluster-slots 4096 --cluster-from all --cluster-to node4-id

T=2-T=10: Live migration begins
  Moving slot 1000 from node1 to node4:
    - Redis migrates keys in slot 1000 one by one (MIGRATE command)
    - During migration: node1 serves slot 1000 until done; then node4 takes over
    - Client GETs for slot-1000 keys: may receive ASK redirect (temporary)
    - Lettuce: handles ASK transparently (sends ASKING before GET to node4)
    - After slot migration: MOVED redirect for slot 1000 → node4 permanently

T=10: Reshard complete (100ms per key × N keys - large datasets take minutes)
  Cluster state: node1=0-3413, node2=5461-9238, node3=10923-14699, node4=3414-5460,9239-10922,14700-16383
  All 16384 slots still assigned ✓ No downtime ✓

MONITORING DURING RESHARD:
redis-cli -c -h node1 CLUSTER INFO
→ cluster_state: ok (maintained during reshard)
redis-cli -c -h node1 CLUSTER NODES
→ node4 shows increasing slot count as reshard progresses
```

---

### ⚖️ Comparison Table

| Aspect        | Redis Standalone   | Redis Cluster          | Redis Sentinel        |
| ------------- | ------------------ | ---------------------- | --------------------- |
| Sharding      | None (single node) | Automatic (hash slots) | None (single primary) |
| Replication   | Manual (REPLICAOF) | Automatic (per shard)  | Automatic (monitored) |
| Failover      | Manual             | Automatic (~30s)       | Automatic (~30s)      |
| Multi-key ops | Unrestricted       | Hash tags required     | Unrestricted          |
| Capacity      | Single node limit  | Scales with nodes      | Single node limit     |
| Use case      | Dev / small scale  | Production at scale    | HA without sharding   |

---

### ⚠️ Common Misconceptions

| Misconception                                       | Reality                                                                                                                                                                                                            |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "KEYS \* scans the entire cluster"                  | `KEYS *` on a cluster node returns ONLY the keys on that node's slots. To scan all keys in a cluster, run SCAN on each primary node separately                                                                     |
| "Replica reads are free (no staleness)"             | Replica reads (`READONLY` + GET) may serve stale data - async replication means replicas can lag behind the primary. Replication lag is typically 0-10ms but can spike under load                                  |
| "Redis Cluster guarantees no data loss on failover" | Redis uses async replication by default. If a primary fails before replicating its last N writes, those writes are lost. Use `WAIT` for synchronous replication, or accept this as acceptable for a cache use case |

---

### 🚨 Failure Modes & Diagnosis

**1. CROSSSLOT Error in Production**

**Symptom:** `CROSSSLOT Keys in request don't hash to the same slot` errors for MGET operations.

**Root Cause:** Multi-key operation with keys in different hash slots (different nodes).

**Fix:**

```bash
# Check which slots two keys are in:
redis-cli CLUSTER KEYSLOT user:42:profile     # → e.g., 4563
redis-cli CLUSTER KEYSLOT user:42:orders      # → e.g., 9012 (different!)

# Fix: use hash tags
redis-cli CLUSTER KEYSLOT "{user:42}:profile"  # → e.g., 7842
redis-cli CLUSTER KEYSLOT "{user:42}:orders"   # → 7842 (SAME!) ✓
```

**2. Cluster State `fail` - Degraded Service**

**Symptom:** `CLUSTERDOWN The cluster is down` errors.

**Root Cause:** `cluster-require-full-coverage yes` and one or more slots have no healthy primary.

**Diagnosis:**

```bash
redis-cli CLUSTER INFO | grep cluster_slots_fail
# If > 0: some slots have no primary - immediate action required

redis-cli CLUSTER NODES | grep fail
# Shows failed nodes

# Quick fix: if replica for failed node is available but not promoted:
redis-cli -h <replica-node> CLUSTER FAILOVER FORCE
# Force the replica to take over immediately (manual failover)
```

---

### 🔗 Related Keywords

**Prerequisites:** Distributed Cache, Consistent Hashing in Cache, Redis Data Structures
**Builds On This:** System Design, Distributed Systems
**Related:** Distributed Cache, Consistent Hashing in Cache, Memcached vs Redis

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ SLOTS        │ 16,384; CRC16(key) % 16384 → slot → node  │
│ MIN CLUSTER  │ 3 primaries (quorum); 6 nodes recommended  │
│ REPLICATION  │ Async (default); WAIT for sync            │
│ FAILOVER     │ ~30s (15s PFAIL + election)               │
│ MOVED        │ Topology change: update client map        │
│ ASK          │ Temp during migration: don't update map   │
│ MULTI-KEY    │ CROSSSLOT: use hash tags {tag}:key        │
│ KEYS *       │ Only returns keys on that node's slots    │
│ HEALTH       │ CLUSTER INFO → cluster_state: ok          │
│ TOPOLOGY     │ lettuce adaptive.refresh=true             │
│ ONE-LINER    │ "16384 slots → N nodes; gossip protocol; │
│              │  failover in ~30s; hash tags for MGET"    │
│ NEXT EXPLORE │ Memcached vs Redis → Local vs Distributed │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE D - Failure Scenario) A 6-node Redis Cluster (3 primaries + 3 replicas) is running in a cloud environment. A network partition splits the cluster into two groups: Group A (primary 1, primary 2, replica 3) and Group B (primary 3, replica 1, replica 2). `cluster-require-full-coverage yes`. Walk through: (a) what happens to each node in both groups, (b) which operations succeed/fail in Group A and Group B, (c) what happens when the partition heals at T+5 minutes, (d) what data is at risk.

**Q2.** (TYPE C - Design Question) You need to implement distributed rate limiting using Redis Cluster: user can make max 100 API calls per minute. Each API call increments a counter: `INCR rate:user:42:minute:1234`. This key must NOT use a hash tag (it's a simple rate limit counter). The problem: rate limit checks require comparing the counter to 100, which is a single-key operation - no CROSSSLOT issue. But what happens when the primary holding `rate:user:42:minute:1234` fails during a 30-second failover window? Design a rate limiting system that is resilient to Redis Cluster node failures.
