---
layout: default
title: "Virtual Nodes"
parent: "Distributed Systems"
nav_order: 599
permalink: /distributed-systems/virtual-nodes/
number: "599"
category: Distributed Systems
difficulty: ★★★
depends_on: "Consistent Hashing, Partitioning"
used_by: "Cassandra, DynamoDB, Riak"
tags: #advanced, #distributed, #partitioning, #scalability, #cassandra
---

# 599 — Virtual Nodes

`#advanced` `#distributed` `#partitioning` `#scalability` `#cassandra`

⚡ TL;DR — **Virtual Nodes (vnodes)** assign each physical node multiple positions on the consistent hash ring, smoothing load distribution and enabling fine-grained, automatic data redistribution when nodes join or leave.

| #599            | Category: Distributed Systems    | Difficulty: ★★★ |
| :-------------- | :------------------------------- | :-------------- |
| **Depends on:** | Consistent Hashing, Partitioning |                 |
| **Used by:**    | Cassandra, DynamoDB, Riak        |                 |

---

### 📘 Textbook Definition

**Virtual Nodes (vnodes)** extend consistent hashing by assigning each physical node K virtual positions (tokens) on the hash ring rather than a single position. With V vnodes per node and N physical nodes: the ring has N×V tokens, and each physical node's ownership is spread across V non-contiguous ranges. This approach solves two problems of single-token consistent hashing: (1) **Load imbalance**: single tokens lead to random, uneven ring coverage (some nodes own 5× more range than others); V=256 tokens per node reduces load variance to ±~6%. (2) **Coarse rebalancing**: single-token add/remove transfers one large range; vnodes allow fine-grained, parallel transfers from many neighbours simultaneously, reducing rebalancing time. **Trade-off**: more tokens → higher metadata overhead (routing table grows O(N×V)); with N=1000 nodes and V=256, the ring has 256,000 tokens (acceptable). Cassandra default: `num_tokens=256` per node. Amazon DynamoDB uses virtual nodes internally for partition management. Riak uses ring size (fixed power of 2) with vnodes allocated to physical nodes.

---

### 🟢 Simple Definition (Easy)

Without vnodes: each server has ONE seat on the hash ring. Random placement → Server A might own a huge chunk, Server B a tiny chunk. Hotspot on A. With vnodes: each server has 256 seats spread around the ring. Each server owns many small, scattered pieces instead of one big chunk. Total load on every server: roughly equal. New server joining: gets 256 evenly spread seats → takes a little bit from every existing server simultaneously. Smooth, parallel data transfer.

---

### 🔵 Simple Definition (Elaborated)

Vnodes in Cassandra (num_tokens=256): each node "owns" 256 small token ranges spread across the ring. When a 4th node joins a 3-node cluster: it gets 256 new token positions. Each existing node gives ~1/4 of its 256 ranges to the new node (about 85 ranges from each existing node, in parallel). Data transfer is parallelized across 3 sources simultaneously — much faster than single-token (all data comes from ONE source node). Operational benefit: hardware heterogeneity — large node can get num_tokens=512 (more ring share = more data). Small node: num_tokens=128. Fine-grained control of data ownership per node.

---

### 🔩 First Principles Explanation

**Why vnodes exist and how they solve consistent hashing's problems:**

```
PROBLEM 1: LOAD IMBALANCE WITH SINGLE-TOKEN CONSISTENT HASHING

  3 nodes. Each gets ONE random position on a 2^32 ring.
  Random positions (uniform distribution):
    Node A: token = 500,000,000 (11.6% of ring)
    Node B: token = 1,200,000,000 (27.9% of ring)
    Node C: token = 4,294,967,295 (at end; C owns from B's token to end + beginning to A's token = 60.5%)

  Ownership: A=11.6%, B=27.9%, C=60.5%.
  C handles 5.2× more traffic than A. Serious hotspot.

  This is NOT unusual — for 3 random points on a circle, variance is high.
  Expected standard deviation of owned range:
    σ ≈ 1/N (for N uniform random points on unit circle). Very high relative variance.

PROBLEM 2: COARSE REBALANCING WITH SINGLE-TOKEN CONSISTENT HASHING

  3 nodes. Single token each. Adding Node D:
    Node D: randomly placed between B and C.
    D takes over the range: B_token → D_token (all from B).
    Data transfer: B → D. Single source, single destination.
    If that range = 25% of data: B must transfer 25% of all cluster data over the network.
    Large transfer: takes minutes to hours. B overloaded during transfer.
    Other nodes: idle. No parallelism.

SOLUTION: VIRTUAL NODES

  V vnodes per physical node.

  Physical → virtual mapping:
    Node A (V=4): A1, A2, A3, A4 (4 tokens, evenly spread by design)
    Node B (V=4): B1, B2, B3, B4
    Node C (V=4): C1, C2, C3, C4

  Ring: A1...B1...C1...A2...B2...C2...A3...B3...C3...A4...B4...C4...
           ^-- interleaved vnodes from all nodes

  Each physical node: owns 4 non-contiguous ranges totalling ~33% of ring.

  LOAD BALANCE:
    Expected ownership: (V per node) / (total V) = V/(N×V) = 1/N = ~33%.
    Standard deviation: ~1/(N × √V). For N=3, V=256: σ ≈ 1/(3×16) ≈ 2%.
    ±6% variance around 33.3% target. Near-uniform. No hotspots.

    Mathematically: vnodes approximate sum of V independent uniform random variables.
    By Central Limit Theorem: variance shrinks as 1/V. More vnodes = better balance.

  FINE-GRAINED REBALANCING: Adding Node D (V=4 vnodes):
    D gets 4 new tokens: D1, D2, D3, D4 (spread across ring).
    D1 falls between A2 and B2: D takes that range from A (small piece).
    D2 falls between C1 and A2: D takes that range from C (small piece).
    D3 falls between B3 and C3: D takes that range from B (small piece).
    D4 falls between A4 and B4: D takes that range from A (small piece).

    Data transferred: 4 small ranges, from 3 different sources (A, B, C) simultaneously!
    Parallelism: A, B, C all send data to D in parallel.
    Transfer time: 4× smaller chunks, 3× parallelism = ~12× faster than single-token equivalent.

  CASSANDRA BOOTSTRAP WITH VNODES (num_tokens=256):
    New node joins. Gets 256 tokens spread across ring.
    Existing 3 nodes each donate ~85 ranges to new node.
    All 3 existing nodes stream data to new node simultaneously (streaming parallelism).
    New node: handles incoming streams from 3 sources. Self-configuring.
    No manual token calculation. No manual data migration.

  CASSANDRA DECOMMISSION WITH VNODES:
    Node C being removed. Donates its 256 ranges to clockwise successors.
    256 ranges → distributed to multiple successors.
    Multiple nodes receive data simultaneously (parallel).

  ANTI-ENTROPY IMPACT:
    With vnodes: anti-entropy and repair tools (nodetool repair) handle small ranges.
    Incremental repair: repair one vnode at a time. Reduces repair blast radius.
    Parallel repair: repair multiple vnodes on different nodes simultaneously.

HETEROGENEOUS CLUSTERS WITH VNODES:

  Node configurations:
    Large node (32 cores, 256GB RAM, 10TB SSD): num_tokens=512
    Medium node (16 cores, 128GB RAM, 4TB SSD): num_tokens=256
    Small node (8 cores, 64GB RAM, 2TB SSD): num_tokens=128

  Ring ownership:
    Total tokens = 512 + 256 + 128 = 896.
    Large: 512/896 = 57% of data. (Proportional to capacity.)
    Medium: 256/896 = 29%.
    Small: 128/896 = 14%.

  Traffic proportional to data ownership. Larger nodes handle more load.

  WITHOUT vnodes: every node gets ~1/N share regardless of hardware.
  "Big server" wastes 80% of capacity while small servers are overloaded.

OPERATIONAL GOTCHA — CHANGING num_tokens:

  Cannot change num_tokens on a running node.
  Token assignments are baked in at node startup.

  To change num_tokens for an existing node:
    1. nodetool decommission (safely remove node, distribute its data).
    2. Delete data and config.
    3. Change num_tokens in cassandra.yaml.
    4. Re-add node (bootstrap with new token count).

  For a new cluster: set num_tokens once, consistently across all nodes.

RIAK'S RING MODEL (FIXED RING SIZE):

  Riak: ring size = fixed number of partitions (power of 2, default=64).
  Physical nodes: share those 64 partitions dynamically.

  3 nodes, ring_size=64: each node owns 64/3 ≈ 21-22 partitions.
  Add 4th node: Riak re-assigns 64/4=16 partitions per node.
    4th node: takes ~5-6 partitions from each existing node.
    Parallel transfer: all 3 existing nodes send simultaneously.

  Vs Cassandra: ring size in Cassandra is 2^64 (continuous). Vnodes = token ranges.
  Riak: discrete partitions. Cassandra: continuous hash space with vnode ranges.
  Conceptually similar: vnodes ≈ Riak partitions in terms of rebalancing behaviour.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT virtual nodes:

- Single-token consistent hashing: random load imbalance (some nodes 5× heavier than others)
- Rebalancing: one large data transfer from a single source (slow, overloads that source)
- Heterogeneous hardware: no way to give larger nodes proportionally more data

WITH virtual nodes:
→ Near-uniform load distribution: ±~6% variance with V=256
→ Parallel rebalancing: new node receives from all existing nodes simultaneously
→ Proportional capacity: num_tokens can be tuned per node based on hardware specs

---

### 🧠 Mental Model / Analogy

> A seating chart for a conference with 10 tables. Without vnodes: each speaker is assigned ONE table. Speaker A randomly gets table 1 (seats 3); Speaker B gets table 7 (seats 12). B is overwhelmed; A is idle. With vnodes: each speaker is assigned MULTIPLE small seats spread across many tables — 4 seats at table 1, 2 at table 3, 3 at table 6, etc. Total seats per speaker is roughly equal. When a new speaker joins: they take a few seats from EVERY existing speaker's allocation simultaneously, not a massive chunk from one.

"Speaker assigned multiple seats" = physical node with multiple vnode positions on the ring
"Near-equal total seats" = near-uniform data/traffic load per physical node
"New speaker takes seats from everyone simultaneously" = parallel data transfer on node bootstrap

---

### ⚙️ How It Works (Mechanism)

```
CASSANDRA VNODE ASSIGNMENT:

  Node startup (bootstrap):
    1. Read num_tokens from cassandra.yaml (default: 256).
    2. Generate num_tokens token values via Murmur3 hash of
       (node_id + vnode_index), spread to maximize ring coverage.
    3. Announce tokens to cluster via Gossip.
    4. Streaming: for each new token range, stream data from current owner.

  Ring state (maintained by Gossip):
    Each node: knows full ring (all N × num_tokens token positions → node mapping).
    Token metadata table: sorted array of (token, node_address, datacenter, rack).
    Lookup: binary search → O(log(N × V)).

  Data routing:
    Client request for key K → hash(K) → binary search in token metadata → node.
    Any node can be coordinator (uses local copy of token metadata).

  nodetool ring (visualize current state):
    $ nodetool ring
    Address         Rack       Status  State   Load      Owns      Token
    10.0.0.1        rack1      Up      Normal  125.5 GiB  33.3%    -9223372036854775808
    10.0.0.1        rack1      Up      Normal  125.5 GiB  33.3%    -7608735541058718895
    10.0.0.2        rack1      Up      Normal  127.1 GiB  33.4%    -7571226671551055456
    ... (256 lines per node × 3 nodes = 768 lines total for 3-node cluster)
```

---

### 🔄 How It Connects (Mini-Map)

```
Consistent Hashing (ring structure; 1 token per node — load imbalance + coarse rebalancing)
        │
        ▼
Virtual Nodes ◄──── (you are here)
(V tokens per node; near-uniform load; parallel rebalancing)
        │
        ├── Gossip Protocol: broadcasts ring membership changes (vnode adds/removes)
        └── Replication Strategies: with vnodes, replicas = next RF distinct physical nodes
            clockwise on the ring (skip vnodes of same physical node)
```

---

### 💻 Code Example

**Cassandra vnode configuration and verification:**

```yaml
# cassandra.yaml — vnode configuration:

# Number of tokens (virtual nodes) per physical node.
# Default: 256. Increase for large nodes; decrease for small nodes.
num_tokens: 256

# DO NOT set initial_token when using vnodes (Cassandra auto-assigns).
# initial_token: (leave commented out)

# Partitioner: consistent hashing function.
# Murmur3Partitioner: best distribution (default since Cassandra 1.2).
partitioner: org.apache.cassandra.dht.Murmur3Partitioner
```

```bash
# Verify vnode distribution after cluster stabilizes:
nodetool status
# Look at "Owns" column — should be ~equal across all nodes (±5% for 256 vnodes)

# Example output (3-node cluster, num_tokens=256):
# UN  10.0.0.1   125.5 GiB  256     100.0%  33.3%  ...
# UN  10.0.0.2   127.1 GiB  256     100.0%  33.4%  ...
# UN  10.0.0.3   124.8 GiB  256     100.0%  33.3%  ...

# Verify token ranges:
nodetool describering keyspace_name
# Lists all 768 token ranges (256 × 3 nodes) with owners.

# Bootstrap new node (vnodes handle data transfer automatically):
# Just start Cassandra on new node. It:
#   1. Contacts seeds.
#   2. Gets ring metadata.
#   3. Assigns 256 tokens.
#   4. Streams data from existing owners of those ranges.
#   5. Joins ring.
nodetool status # Watch state: Joining (J) → Up Normal (UN)
```

```java
// Application-level: vnode awareness is transparent.
// Cassandra driver handles routing based on token metadata automatically.

CqlSession session = CqlSession.builder()
    .addContactPoint(new InetSocketAddress("10.0.0.1", 9042))
    .withLocalDatacenter("datacenter1")
    .build();

// Driver internally: hash(partition_key) → token → node lookup → direct connection.
// vnodes are transparent to application code.
ResultSet rs = session.execute(
    "SELECT * FROM orders WHERE order_id = ?",
    orderId  // Driver routes this to the correct node(s) for this partition key.
);
```

---

### ⚠️ Common Misconceptions

| Misconception                               | Reality                                                                                                                                                                                                                                                                                                                                                                                                                              |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| More vnodes always means better performance | Higher num_tokens improves load balance but increases metadata overhead and has diminishing returns. With num_tokens=256: variance ≈ ±6% (excellent). With num_tokens=1024: variance ≈ ±3% (marginal improvement). But 1024 tokens × 1000 nodes = 1,000,000 ring entries, and repair/streaming operations have more overhead. Cassandra 256 is the sweet spot. Very high vnodes can slow down ring operations and Gossip convergence |
| Cassandra vnodes were always the default    | Cassandra originally used single tokens (num_tokens=1) with manually assigned initial_token values. Operators had to calculate midpoints manually. vnodes (multi-token) were introduced in Cassandra 1.2 (2013) and became the default. Many legacy clusters still use single tokens; migrating requires full node decommission/recommission cycles                                                                                  |
| Vnodes eliminate hotspots entirely          | Vnodes reduce load imbalance to ±~6% (with num_tokens=256). There can still be hotspots if: (1) the application accesses a small set of partition keys disproportionately (hot partitions — not related to ring distribution); (2) one datacenter has many more tokens assigned (configuration error). Vnodes solve STRUCTURAL ring imbalance, not application-level access pattern hotspots                                         |
| All nodes must have the same num_tokens     | Different nodes in a cluster can have different num_tokens values (heterogeneous capacity). A node with num_tokens=512 owns ~2× more data than a node with num_tokens=256. This is used intentionally to weight larger hardware appropriately. However: mixing is an operational complexity, and Cassandra's nodetool status/ring output becomes harder to interpret                                                                 |

---

### 🔥 Pitfalls in Production

**Bootstrap failure leaves orphan token ranges:**

```
SCENARIO: Adding 4th node to 3-node Cassandra cluster. Bootstrap fails mid-stream.
  New node (D): bootstrapped, got 256 tokens, started receiving data streams.
  At 40% complete: network outage on Node D. D dies.

  Ring state: D's tokens still registered in Gossip (other nodes see D as Down/Leaving).
  Missing data: key ranges that were mid-transfer to D may be incomplete on D.
  Risk: if D is declared as owner of some ranges: reads to D's ranges return partial data.

BAD: Allowing incomplete bootstrap node to join ring:
  # Auto-bootstrap = true (default): node joins ring before streams complete.
  # If it crashes mid-stream: ring has node claiming ownership of incomplete ranges.
  # nodetool status shows D as DN (Down Normal) — owning ranges but not serving them.
  # Reads to D's ranges: timeout (no live replica at D).

FIX 1: Use replace_address (not re-bootstrap) if node failed mid-bootstrap:
  # cassandra.yaml on replacement node:
  auto_bootstrap: true
  # JVM option when starting:
  # -Dcassandra.replace_address=<original_D_address>
  # This tells Cassandra: "I'm replacing D's position. Stream D's exact ranges."
  # Avoids creating new token assignments.

FIX 2: Monitor bootstrap completion:
  nodetool netstats  # Shows streaming progress: pending ranges, bytes streamed.
  # Wait until all ranges show "0 bytes pending" before considering bootstrap complete.

FIX 3: If D is truly gone with incomplete data:
  nodetool removenode <D_host_id>   # Remove D from ring.
  nodetool repair --full             # Force full repair to ensure all ranges have RF copies.
  # Then re-add new node D cleanly.

ANTI-PATTERN: High num_tokens on low-memory nodes:
  num_tokens=256 means 256 token ranges per node = 256 memtables potentially in use.
  Low memory node (16GB RAM) with num_tokens=256 and RF=3: 256×3 = 768 range compactions.
  OOM errors from too many concurrent SSTables/memtables.

  FIX: Match num_tokens to available resources:
    Large node (256GB+ RAM): num_tokens=256 or 512.
    Small node (16-32GB RAM): num_tokens=64 or 128.
    Cassandra 4.x: Dynamic snitch + load-based token assignment (experimental).
```

---

### 🔗 Related Keywords

- `Consistent Hashing` — the ring mechanism that vnodes extend (multiple positions per node)
- `Gossip Protocol` — broadcasts vnode token assignments across cluster for ring consistency
- `Replication Strategies` — with vnodes, replication skips same-physical-node vnodes (NetworkTopologyStrategy)
- `Anti-Entropy` — incremental repair operates per-vnode range for targeted consistency checks

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Each physical node = V tokens on ring.   │
│              │ V=256: ±6% load variance. New node joins │
│              │ from all existing nodes in parallel.     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any consistent-hashing cluster needing   │
│              │ uniform load; heterogeneous hardware;    │
│              │ smooth online rebalancing                │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Very small clusters (< 3 nodes) where    │
│              │ token metadata overhead is noticeable;   │
│              │ or if cluster requires exact ring control│
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Multiple seats spread around the table  │
│              │  so every chef gets a fair portion."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Consistent Hashing → Gossip Protocol →  │
│              │ Replication Strategies → Cassandra       │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A 3-node Cassandra cluster uses num_tokens=256. You add a 4th node with num_tokens=512 (it's a much larger machine). After bootstrap completes, what percentage of the ring does the new node own? What percentage does each of the original 3 nodes own? Is this the desired behaviour for a heterogeneous cluster — and how do you prevent the large node from becoming a hotspot if it's receiving proportionally more writes than its disk I/O can handle?

**Q2.** Cassandra's NetworkTopologyStrategy (NTS) with vnodes ensures replicas are on different physical nodes even when multiple vnodes of the same physical node are near each other on the ring. How does NTS implement this: if selecting the next RF=3 clockwise tokens finds two tokens on the same physical node (NodeA), how does NTS handle it? What does "rack awareness" in NTS add on top of this?
