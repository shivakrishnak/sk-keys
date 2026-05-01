---
layout: default
title: "Anti-Entropy"
parent: "Distributed Systems"
nav_order: 623
permalink: /distributed-systems/anti-entropy/
number: "623"
category: Distributed Systems
difficulty: ★★★
depends_on: "Gossip Protocol, Consistent Hashing, CRDT"
used_by: "Cassandra, Riak, DynamoDB, Amazon S3"
tags: #advanced, #distributed, #replication, #consistency, #repair
---

# 623 — Anti-Entropy

`#advanced` `#distributed` `#replication` `#consistency` `#repair`

⚡ TL;DR — **Anti-entropy** is a background process that compares replicas and repairs divergence by syncing missing or stale data — using **Merkle trees** to efficiently identify which data ranges differ without comparing every item.

| #623 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Gossip Protocol, Consistent Hashing, CRDT | |
| **Used by:** | Cassandra, Riak, DynamoDB, Amazon S3 | |

---

### 📘 Textbook Definition

**Anti-entropy** is a background synchronization mechanism in distributed databases that ensures eventual consistency by periodically comparing data between replicas and repairing divergence. Unlike reactive repair (read repair triggers on read), anti-entropy is proactive: it continuously scans for inconsistencies regardless of read traffic. The key challenge: comparing large datasets between two replicas efficiently. Solution: **Merkle trees** (hash trees) — a binary tree where leaf nodes are hashes of individual data ranges (token ranges in consistent hashing), and each parent is the hash of its children. Two nodes compare only the root hash first; if equal: no divergence; if different: binary search the tree to find differing subtrees → only transfer the specific data ranges that differ. Cassandra `nodetool repair`: triggers anti-entropy repair for a node. Types: (1) **Full repair** — compares all data on the node. (2) **Incremental repair** — only compares data changed since last repair. (3) **Sub-range repair** — repair a specific token range. Critical for: ensuring all replicas have consistent data when replication lag or node failures cause missed writes.

---

### 🟢 Simple Definition (Easy)

Two copies of a library catalog. Books added to one but not the other. Anti-entropy: a librarian periodically checks both catalogs, finds differences, and adds missing books to the other. Challenge: how to find differences in 10 million books without checking all 10 million? Merkle trees: organize books by section. Compare section hashes first. If section A differs: compare subsections. Quickly narrow down to exactly which shelf has the missing book. Only transfer the missing books, not the entire catalog.

---

### 🔵 Simple Definition (Elaborated)

Why replicas diverge: node was temporarily down, network partition, read-heavy node with rare writes that weren't propagated, clock skew causing LWW to drop writes. Anti-entropy: the safety net that catches all these divergences. Read repair only fixes data that's actively read. Anti-entropy repairs everything, even cold data never read. Critical for: compliance ("all 3 replicas must have identical data"), disaster recovery ("can I restore from any replica?"), ensuring durable data isn't silently missing on one replica.

---

### 🔩 First Principles Explanation

**Merkle tree construction, node comparison, and Cassandra repair:**

```
MERKLE TREE STRUCTURE:

  Data: organized by token range (consistent hashing).
  Token range: 0 to 2^64. Each node owns a range.
  
  Cassandra example: Node A owns token range 0 to 1,000,000.
  Repair: compare Node A's range with replicas (Node B, Node C own same range).
  
  MERKLE TREE FOR TOKEN RANGE [0, 1,000,000]:
  
                    [Root Hash: H(H1, H2)]
                    /                    \
         [H1: H(H11, H12)]        [H2: H(H21, H22)]
            /          \               /          \
  [H11: hash(          [H12: hash(  [H21: hash(  [H22: hash(
    data[0-250K])]       data[250K-500K])] data[500K-750K])] data[750K-1M])]
    
  Hash of each leaf: computed from all keys+values in that token sub-range.
  Parent hash: hash of concatenated child hashes.
  
  COMPARISON PROTOCOL:
    Node A sends root hash to Node B.
    Node B compares: root hashes match → NO divergence in this range. Done. O(1).
    Root hashes differ → compare children (H1, H2).
    H1 matches, H2 differs → descend right subtree.
    H21 matches, H22 differs → data in [750K, 1M] is different.
    Transfer only the differing data: [750K, 1M] keys from whichever replica is authoritative.
    
  EFFICIENCY:
    Without Merkle trees: compare ALL 1M key-value pairs. O(n) network transfer.
    With Merkle trees: O(log n) comparisons to find divergence.
    For 1 trillion keys: ~40 comparisons to find differing subtree vs. 1T comparisons.
    Transfer only the differing data range. Huge bandwidth savings.
    
  TREE DEPTH:
    Cassandra: default 15 levels deep. 2^15 = 32,768 leaf nodes per repair range.
    Each leaf covers: token_range / 32,768 keys.
    Finer granularity: more efficient (smaller divergent range found faster).
    Coarser granularity: less memory for tree. Trade-off.

CASSANDRA REPAIR TYPES:

  FULL REPAIR (nodetool repair):
    Compares all sstables (including previously repaired).
    Expensive: computes Merkle tree for entire data set.
    Run frequency: every gc_grace_seconds (default 10 days) to avoid zombie resurrections.
    
    nodetool repair -full keyspace table
    
  INCREMENTAL REPAIR (Cassandra 2.2+):
    Only repairs data NOT yet marked as repaired.
    Marks sstables as "repaired" after repair.
    Next repair: only looks at new/unrepaired sstables.
    Faster: only processes data changed since last repair.
    CRITICAL: must use incremental repair consistently. Mix of full + incremental: can miss data.
    
    nodetool repair keyspace table  # Default: incremental in Cassandra 2.2+
    
  SUB-RANGE REPAIR:
    Repair a specific token range: faster than full node repair.
    Distribute repair across time (time-windowed repair).
    Prevents all nodes being repaired simultaneously (thundering herd).
    
    # Repair token range 0 to 1000000000:
    nodetool repair -st 0 -et 1000000000 keyspace table
    
  REPAIR COORDINATOR:
    The node running nodetool repair: acts as coordinator.
    Coordinator: contacts all replicas, exchanges Merkle trees, identifies divergence.
    Coordinator: orchestrates streaming of missing data between replicas.
    
ANTI-ENTROPY WITH GOSSIP:

  Some systems: piggyback anti-entropy on gossip protocol.
  
  Node A: sends gossip message to Node B containing hash of recently updated data.
  Node B: compares hash. If different: request specific keys from Node A.
  
  Push-pull gossip anti-entropy:
    Push: Node A sends its state updates to Node B.
    Pull: Node A requests Node B's state that A is missing.
    Exchange: bidirectional sync. Both converge to union.
    
  CONVERGENCE TIME:
    With n nodes and f fanout (nodes per gossip round):
    Expected convergence: O(log(n) / log(f)) rounds.
    At n=1000, f=3: ~6 rounds. Very fast.

AMAZON S3 AND DYNAMODB (Background ANTI-ENTROPY):

  S3: continuous background reconciliation of all object metadata.
    If any replica diverges: background process re-replicates from authoritative replica.
    Target: 11 nines durability (99.999999999%).
    
  DynamoDB: internal anti-entropy ensures all replicas (3 replicas per partition) converge.
    Replica lag: typical < 1 second.
    Background reconciliation: ensures even lagging replicas catch up.

REPAIR SCHEDULING IN PRODUCTION:

  Run repair on schedule: before gc_grace_seconds elapses (default 10 days).
  If repair not run in gc_grace_seconds: deleted data may "resurrect" (tombstone purged before replica synced).
  
  SCHEDULING STRATEGY:
    Repair one node at a time: don't repair all nodes simultaneously.
    Repair window: off-peak hours.
    Distribute across time: repair 1/N of token range per day (N = days in window).
    
  Reaper (open-source Cassandra repair scheduler):
    Automates repair scheduling.
    Time-windowed incremental repair.
    Monitors repair progress. Alerts on repair lag.
    
  nodetool compactionstats: check if repair-triggered compaction is running.
  nodetool tpstats: "ValidationActive" = active Merkle tree validations (repair in progress).
  
ANTI-ENTROPY METRICS:

  cassandra.db.AntiEntropy:
    PendingTasks: number of pending repair tasks
    ActiveRepairs: currently running repairs
    
  Repair lag: days since last successful repair per node.
  ALERT: repair lag > gc_grace_seconds / 2 → urgent: run repair before tombstone expiry.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT anti-entropy:
- Replicas diverge over time due to missed writes, temporary failures, replication lag
- Data on replica 3 may be weeks out of date — user reads stale data
- Tombstones expire before repair — deleted data resurfaces ("zombie data")

WITH anti-entropy:
→ Continuous background repair ensures all replicas converge
→ Merkle tree: efficient — find diverging data ranges without comparing every key
→ Durability guarantee: even rarely-read cold data is kept consistent across replicas

---

### 🧠 Mental Model / Analogy

> Tax auditors comparing two copies of a financial ledger: instead of comparing every single transaction (millions of entries), they first compare annual totals. Totals match → no discrepancy. Totals differ in Q3 → compare Q3 months. September differs → compare September weeks. Week 3 differs → compare specific days. Day 15 differs → compare individual transactions. Found: 3 transactions on Sept 15 that differ. Fix only those. Same idea: Merkle tree binary search finds exactly which "leaf" is different without scanning everything.

"Annual totals comparison" = Merkle tree root hash comparison
"Narrowing down to Q3, September, Week 3, Day 15" = descending the Merkle tree
"Three transactions on Sept 15" = specific data range with divergence
"Fix only those transactions" = streaming only the differing data between replicas

---

### ⚙️ How It Works (Mechanism)

```
REPAIR FLOW (CASSANDRA):

  1. nodetool repair triggered on Node A.
  2. Node A: computes Merkle tree for its token range.
  3. Node A: contacts Node B, Node C (replicas for same range).
  4. All nodes: exchange Merkle tree root hashes.
  5. Root hashes differ: binary search to find diverging subtrees.
  6. Repair coordinator: identifies specific token sub-ranges that differ.
  7. Streaming: Node B sends missing keys to Node A (and vice versa).
  8. After streaming: Merkle trees match → repair complete for this range.
```

---

### 🔄 How It Connects (Mini-Map)

```
Eventual Consistency (replicas may diverge temporarily)
        │
        ▼ (anti-entropy: background repair to converge)
Anti-Entropy ◄──── (you are here)
(Merkle tree comparison → efficient diff → stream missing data)
        │
        ├── Read Repair: reactive repair (triggered on read, not background)
        ├── Gossip Protocol: some systems piggyback anti-entropy on gossip
        └── Hinted Handoff: reactive repair for temporarily unavailable nodes
```

---

### 💻 Code Example

```java
// Simple Merkle tree for anti-entropy comparison:
public class MerkleTree {
    
    // Build tree from a range of key-value pairs.
    public static MerkleNode build(Map<String, String> data, int tokenStart, int tokenEnd) {
        if (tokenEnd - tokenStart <= LEAF_SIZE) {
            // Leaf node: hash all key-value pairs in this range.
            String hash = hashRange(data, tokenStart, tokenEnd);
            return new MerkleNode(hash, tokenStart, tokenEnd, null, null);
        }
        
        int mid = (tokenStart + tokenEnd) / 2;
        MerkleNode left = build(data, tokenStart, mid);
        MerkleNode right = build(data, mid, tokenEnd);
        String hash = sha256(left.hash + right.hash);
        return new MerkleNode(hash, tokenStart, tokenEnd, left, right);
    }
    
    // Find diverging ranges between two trees. Returns list of token ranges to sync.
    public static List<TokenRange> findDivergence(MerkleNode local, MerkleNode remote) {
        List<TokenRange> divergent = new ArrayList<>();
        findDivergenceHelper(local, remote, divergent);
        return divergent;
    }
    
    private static void findDivergenceHelper(MerkleNode a, MerkleNode b, List<TokenRange> divergent) {
        if (a.hash.equals(b.hash)) return; // Subtrees match: no divergence.
        
        if (a.isLeaf()) {
            // Leaf diverges: this specific range needs repair.
            divergent.add(new TokenRange(a.tokenStart, a.tokenEnd));
            return;
        }
        
        // Internal node differs: recurse into children to find specific diverging leaves.
        findDivergenceHelper(a.left, b.left, divergent);
        findDivergenceHelper(a.right, b.right, divergent);
    }
    // Result: only the specific token ranges that differ — minimizes data to transfer.
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Anti-entropy repair is only needed after failures | Anti-entropy is needed as a routine operation in any eventually consistent system. Even without failures: hinted handoff might have failed to deliver, compaction might have missed a tombstone, very old writes might have been reordered. Cassandra documentation: "repair should be run regularly, not only after failures." Missing repair = eventual divergence, zombie data, durability gaps |
| Merkle trees ensure real-time consistency | Merkle tree repair is a background process running on a schedule (daily, weekly). Between repairs: replicas may diverge. Read repair + hinted handoff handle the hot path. Anti-entropy handles the cold path (rarely-read data, long-term divergence). Real-time consistency during writes requires quorum writes, not repair |
| Running nodetool repair is harmless to production | Repair is a heavyweight operation. Merkle tree computation: significant I/O and CPU. Streaming (after finding divergence): network bandwidth. Running repair on all nodes simultaneously: can cause performance degradation. Best practice: time-windowed repair (repair one range per hour), off-peak, one node at a time. Production incidents caused by all-at-once repair are well-documented |

---

### 🔥 Pitfalls in Production

**Zombie data resurrection — repair lag exceeds gc_grace_seconds:**

```
SCENARIO: Cassandra cluster. gc_grace_seconds = 10 days (default).
  Node B: down for maintenance for 7 days.
  During downtime: 5000 rows deleted from the cluster (tombstones written to A and C).
  Node B: comes back online on day 7. 
  Days 8-9: repair not run (operators busy).
  Day 10: gc_grace_seconds expires. Compaction: purges tombstones from Node A and Node C.
  Day 11: operator runs repair to sync Node B.
  
  PROBLEM:
    Node A and C: tombstones gone (purged by GC). Only the data rows (delete targets) remain.
    Node B: still has the original data rows (deletion never reached it).
    Repair: sees Node B has data that A and C don't have → repairs A and C WITH Node B's data.
    Result: DELETED DATA RESURRECTED. 5000 rows come back from the dead.
    Users: see data that was explicitly deleted. GDPR violation if PII data.
    
BAD: No repair schedule monitoring:
  # Node B was down > gc_grace_seconds / 2.
  # Alert should have fired. Didn't.
  # Repair should have run within gc_grace_seconds. Didn't.
  
FIX AND PREVENTION:
  1. Alert when node has been down > gc_grace_seconds / 2:
    // If node down > 5 days: DO NOT restart without running repair first.
    // OR: run repair immediately on restart.
    
  2. Run repair BEFORE gc_grace_seconds elapses:
    nodetool repair -full keyspace  // Run within 10 days of last repair.
    
  3. Consider higher gc_grace_seconds for critical data:
    ALTER TABLE sensitive_data WITH gc_grace_seconds = 1728000;  // 20 days
    // More time for repair to run before tombstone GC.
    // Cost: more storage (tombstones kept longer).
    
  4. Monitor repair lag:
    Alert: "last successful repair on node X was more than 7 days ago" → run repair.
    Tool: Reaper (open-source) automates this monitoring and scheduling.
    
  5. For decommissioned node (not coming back):
    nodetool removenode [node-host-id]  // Remove node before its tombstones expire.
    Cassandra: redistributes data, including tombstones, to remaining nodes.
    gc_grace_seconds: resets for the redistributed data.
```

---

### 🔗 Related Keywords

- `Read Repair` — reactive repair on the read path (vs. anti-entropy's background proactive repair)
- `Hinted Handoff` — reactive repair for temporarily down nodes on write path
- `Merkle Tree` — the data structure enabling efficient replica comparison
- `Gossip Protocol` — used to propagate repair information in peer-to-peer systems
- `Tombstone` — the delete marker that anti-entropy must propagate before gc_grace_seconds expires

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Background replica comparison using      │
│              │ Merkle trees: O(log n) to find diverging  │
│              │ ranges → stream only differing data.     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Any eventually consistent DB with        │
│              │ multiple replicas (mandatory for         │
│              │ Cassandra: run before gc_grace_seconds)  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Strongly consistent systems (no need);  │
│              │ avoid ALL-AT-ONCE repair in production   │
│              │ (use time-windowed, staggered repair)    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Tax audit: compare annual totals first,│
│              │  narrow down to specific transactions." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Read Repair → Hinted Handoff → Merkle   │
│              │ Tree → Gossip Protocol → Cassandra Repair│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A Cassandra table has 100 billion rows. A full anti-entropy repair generates a Merkle tree with 32,768 leaf nodes. Each leaf covers ~3 million rows. The repair finds 10 leaf nodes that differ between replicas. Those 10 leaves contain 30 million rows total. In reality, only 500 rows actually differ (due to 500 missed writes on one replica). The repair streams ALL 30 million rows. Is this efficient? How would you increase the Merkle tree resolution to reduce the streaming scope? What are the costs of increasing tree depth?

**Q2.** You're designing a distributed key-value store with 3 replicas and eventual consistency. You want to ensure replicas don't diverge for more than 1 hour without repair. Design the anti-entropy scheduling: how often should repair run? How do you partition the repair work (so you're not comparing all 1TB of data every hour)? How does incremental repair (only repair data changed since last repair) help? What metadata do you need to track to make incremental repair work correctly?
