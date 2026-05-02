---
layout: default
title: "Virtual Nodes"
parent: "Distributed Systems"
nav_order: 599
permalink: /distributed-systems/virtual-nodes/
number: "0599"
category: Distributed Systems
difficulty: ★★★
depends_on: Consistent Hashing
used_by: Cassandra, DynamoDB (internal), Riak
related: Consistent Hashing, Replication Strategies
tags:
  - virtual-nodes
  - vnodes
  - consistent-hashing
  - distributed-systems
  - advanced
---

# 599 — Virtual Nodes

⚡ TL;DR — Virtual nodes (vnodes) solve the load imbalance problem in consistent hashing. Instead of placing each physical node at ONE position on the hash ring, each node occupies V positions (typically 64–256). These V positions are distributed across the ring space, so each node handles multiple small, non-contiguous ring segments rather than one large arc. Result: load is uniformly distributed across nodes; heterogeneous hardware is handled by assigning more vnodes to larger servers; re-distribution on node join/leave is spread across many nodes (no single hot receiver).

┌──────────────────────────────────────────────────────────────────────────┐
│ #599         │ Category: Distributed Systems      │ Difficulty: ★★★      │
├──────────────┼────────────────────────────────────┼──────────────────────┤
│ Depends on:  │ Consistent Hashing                  │                      │
│ Used by:     │ Cassandra, Riak, DynamoDB           │                      │
│ Related:     │ Consistent Hashing, Replication     │                      │
└──────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

Basic consistent hashing with 1 token per node: six nodes placed on a ring at arbitrary positions. Due to hash variance, node A might own 40% of the ring, node B owns 5%. A handles 40% of traffic, B handles 5% — massive imbalance. Virtual nodes give each node V positions: law of large numbers ensures each node ends up owning approximately 1/N of the ring (about 100/V% variance). Imbalance drops from potentially 8:1 to <1.1:1 with V=256.

---

### 📘 Textbook Definition

**Virtual nodes (vnodes):** Each physical node N_i is assigned V token positions on the consistent hash ring:
```
positions(N_i) = {hash(N_i + "#vnode-0"), hash(N_i + "#vnode-1"), ... , hash(N_i + "#vnode-V-1")}
```

Each token owns the ring arc from the previous token to itself. A physical node's data = union of all its vtokens' arcs.

**Benefits:**
1. **Load balance:** With V tokens per node, each physical node owns ~V/total_tokens of the ring → uniform distribution
2. **Heterogeneous hardware:** Assign V_big vnodes to large nodes, V_small to small → proportional allocation
3. **Smooth rebalancing:** When a new node joins, it claims V arcs distributed across the ring — data is redistributed from V different existing nodes (parallel transfer) rather than entirely from one neighbor

**Cassandra:** Default num_tokens = 256 vnodes per node. Change via cassandra.yaml: `num_tokens: 256`

---

### ⏱️ Understand It in 30 Seconds

**One line:** Instead of 1 point on the ring per node, use V points — uniformly distributed → each node handles a fair share of keys.

**Analogy:** Parking lot assignment. Without vnodes: Lot A is at position 3, Lot B at 7 — all spots 3-7 go to B (overflow). With vnodes: Lot A is at positions {3, 15, 27, ...}, Lot B is at {7, 19, 31, ...} — each lot handles short segments throughout the lot, evenly sharing overflow across the whole facility.

---

### 🔩 First Principles Explanation

```
WITHOUT VNODES (V=1):

  6 nodes hashed to ring positions (hash results in degrees, 0-360°):
  N1=15°, N2=25°, N3=190°, N4=195°, N5=200°, N6=350°
  
  Ring arc ownership:
  N1: 350°→15° = 25° of ring  ← 7% of total
  N2: 15°→25° = 10° of ring   ← 3% of total
  N3: 25°→190° = 165° of ring ← 46% of total  ← OVERLOADED
  N4: 190°→195° = 5° of ring  ← 1.4% of total ← UNDERLOADED
  N5: 195°→200° = 5° of ring  ← 1.4% of total ← UNDERLOADED
  N6: 200°→350° = 150° of ring ← 42% of total  ← OVERLOADED
  
  Worst case: 46% vs 1.4% load ratio = 33:1 imbalance ← unacceptable
  
  WITH VNODES (V=6 for illustration):
  Each of 6 nodes places 6 tokens → 36 tokens total on ring
  Expected arc per token: 360°/36 = 10°
  Expected arcs per node: 6×10° = 60° (= 1/6 of ring, as expected)
  
  Law of large numbers: with V=256, variance is ~±3%
  All nodes own approximately 1/6 of ring → balanced load ✓
  
  HETEROGENEOUS HARDWARE:
  8-core server: num_tokens=256
  2-core server: num_tokens=64
  8-core gets 256/(256+64) = 80% of data & traffic ✓ proportional
```

---

### 🧠 Mental Model / Analogy

> Virtual nodes are like lottery ticket distribution. With 1 ticket per player, a lottery is unfair — ticket #7 might be the only ticket before a huge consecutive block, making player 7 unlikely to win anything meaningful. With 256 tickets per player (each with a random number), the expected winnings converge to 1/n of the jackpot by the law of large numbers. Players with more resources can buy more tickets proportionally.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Vnodes = V positions per physical node on the ring → uniform load distribution. Cassandra default: 256 vnodes. More vnodes = better balance but more coordination overhead.

**Level 2:** Rebalancing with vnodes: when a new node joins Cassandra, it claims V vnodes from existing nodes. These V vnodes are scattered across V different existing nodes — so V different nodes each stream a small portion of data to the new node simultaneously. This parallelism speeds up join streaming. With V=1: only 1 existing node streams to the newcomer (bottleneck). With V=256: 256 different existing nodes stream 1/256 of the new node's data in parallel.

**Level 3:** Trade-offs of high vnode counts: (a) More tokens in the ring → more replica coordination messages per request (coordinator must track more replicas); (b) More entries in the gossip state per node (larger gossip payload); (c) Cassandra num_tokens > 256: not recommended, diminishing returns on balance with increasing gossip overhead. (d) Repair (anti-entropy) complexity: repair segments break on vnode boundaries → more repair ranges per node. Some operators prefer num_tokens=4 for operational simplicity at the cost of some balance. DynamoDB manages this automatically.

**Level 4:** Automatic vnode rebalancing in DynamoDB: DynamoDB's partition layer does NOT expose vnodes to users. Instead, DynamoDB monitors partition-level hot spots in real-time and automatically splits hot partitions, re-assigns token ranges, and moves data between storage nodes. This is more adaptive than static vnode assignment — it handles uneven key distributions (hot keys) that vnodes cannot help with (even with 256 vnodes, if all requests are for the same key, one partition handles all traffic). Solutions for hot key patterns: write sharding (append random suffix to hot keys), read caching at application layer.

---

### ⚙️ How It Works (Mechanism)

```
CASSANDRA VNODE RING (num_tokens=4 for illustration, actual default=256):

  Physical:  Node-1        Node-2        Node-3
  Vnodes:    T11 T12 T13 T14  T21 T22 T23 T24  T31 T32 T33 T34
  
  Ring (sorted by token):
  [T12=10] [T31=25] [T23=40] [T11=55] [T33=70] [T24=85]
  [T13=100][T22=115][T32=130][T14=145][T21=160][T34=175][→wrap→]
  
  Node-1 owns: T12(10), T11(55), T13(100), T14(145) — 4 non-contiguous arcs
  Node-2 owns: T23(40), T24(85), T22(115), T21(160) — 4 non-contiguous arcs
  Node-3 owns: T31(25), T33(70), T32(130), T34(175) — 4 non-contiguous arcs
  
  NEW NODE Node-4 joins (claims 4 new token positions):
  N4's new tokens split RANDOMLY into 4 different existing arcs:
  → Node-2 loses arc T23 chunk → Node-4 gets it
  → Node-1 loses arc T14 chunk → Node-4 gets it
  → Node-3 loses arc T32 chunk → Node-4 gets it
  → Node-1 loses arc T12 chunk → Node-4 gets it
  
  Data moves FROM 3 different nodes (N1×2, N2, N3) to N4 in PARALLEL. ✓
```

---

### 💻 Code Example

```java
// Cassandra vnode configuration in application.yml (Spring Data Cassandra)
// and programmatic verification of token distribution

// cassandra.yaml (server config):
// num_tokens: 256   ← 256 virtual nodes per physical node (default)
// allocate_tokens_for_local_replication_factor: 3  ← Cassandra 4.0+ auto-balances

// Spring Boot: query token distribution per node
@Repository
public class ClusterTopologyInspector {

    private final CqlSession session;

    public Map<String, List<String>> getTokenDistribution() {
        // Query system.local and system.peers for each node's token assignments
        ResultSet rs = session.execute("SELECT peer, tokens FROM system.peers");
        
        Map<String, List<String>> nodeTokens = new HashMap<>();
        for (Row row : rs) {
            String node = row.getInetAddress("peer").getHostAddress();
            Set<String> tokens = row.getSet("tokens", String.class);
            nodeTokens.put(node, new ArrayList<>(tokens));
        }
        
        // Each node should have ~256 tokens
        nodeTokens.forEach((node, tokens) -> 
            log.info("Node {}: {} tokens (expected ~256)", node, tokens.size()));
        
        return nodeTokens;
    }

    // Analyze ring coverage equality (should be ~1/N per node)
    public void analyzeLoadBalance() {
        Map<String, Long> tokensPerNode = getTokenDistribution().entrySet().stream()
            .collect(Collectors.toMap(Map.Entry::getKey, e -> (long) e.getValue().size()));
        
        long total = tokensPerNode.values().stream().mapToLong(Long::longValue).sum();
        tokensPerNode.forEach((node, count) -> {
            double percent = (double) count / total * 100;
            log.info("Node {}: {:.1f}% of ring ({} tokens)", node, percent, count);
        });
    }
}
```

---

### ⚖️ Comparison Table

| vnodes count | Load Balance | Rebalance Parallelism | Gossip Overhead | Repair Complexity |
|---|---|---|---|---|
| **V=1** | Poor (33:1 imbalance possible) | Sequential (from 1 node) | Minimal | Simple |
| **V=4** | OK (~25% variance) | Good (from 4 nodes) | Low | Low |
| **V=256** | Excellent (~1% variance) | Excellent (from up to 256 nodes) | Medium | High |
| **V=1000+** | Excellent | Excellent | High | Very High |

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ WHAT          │ V token positions per physical node on ring  │
│ PURPOSE       │ Uniform load distribution; parallel scale    │
│ CASSANDRA     │ num_tokens=256 (default as of 3.0+)         │
│ HETEROGENEOUS │ Bigger servers: assign more vnodes           │
│ INCREASE V    │ Better balance but more gossip/repair cost   │
│ HOT KEYS      │ Vnodes don't help — use request sharding    │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** A Cassandra production cluster has 10 nodes, each with num_tokens=256. A new node is added during peak traffic (node 11). (1) How many token positions does node 11 claim? From which existing nodes does data stream? (2) What is the expected % of cluster data that moves to node 11? (3) During the streaming phase, what happens to read consistency (CL=QUORUM) for data that is currently being streamed? Does Cassandra guarantee availability for those partitions during bootstrap? (4) How does `nodetool status` help monitor this process, and what metrics should you watch?
