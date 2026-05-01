---
layout: default
title: "Quorum"
parent: "Distributed Systems"
nav_order: 591
permalink: /distributed-systems/quorum/
number: "591"
category: Distributed Systems
difficulty: ★★★
depends_on: "Replication Strategies, Strong Consistency"
used_by: "Raft, Cassandra, DynamoDB, Zookeeper"
tags: #advanced, #distributed, #consensus, #consistency, #availability
---

# 591 — Quorum

`#advanced` `#distributed` `#consensus` `#consistency` `#availability`

⚡ TL;DR — **Quorum** is the minimum number of nodes (majority or W/R subset) that must agree on an operation for it to be valid — mathematically guaranteeing overlap between any two quorums to prevent conflicting decisions.

| #591            | Category: Distributed Systems              | Difficulty: ★★★ |
| :-------------- | :----------------------------------------- | :-------------- |
| **Depends on:** | Replication Strategies, Strong Consistency |                 |
| **Used by:**    | Raft, Cassandra, DynamoDB, ZooKeeper       |                 |

---

### 📘 Textbook Definition

**Quorum** in distributed systems is a subset Q of nodes from a universe U of N nodes such that any two quorums Q1 and Q2 share at least one node (Q1 ∩ Q2 ≠ ∅). This intersection property guarantees that any two operations each confirmed by a quorum must have been seen by at least one common node — preventing split-brain, conflicting commits, or dual leadership. **Majority quorum**: Q = ⌊N/2⌋ + 1 (e.g., 3 of 5). Any two majorities of 5 nodes share ≥ 1 node. **Read/Write quorums** (Dynamo/Cassandra): W + R > N ensures read quorum R and write quorum W overlap — at least one node in every read has the latest write. **Grid quorums**: arrange N nodes in a √N × √N grid; quorum = any one full row + one element from each other row (reduces quorum size to O(√N)). **Weighted quorums**: assign weights to nodes; quorum = subset with total weight > W/2. Quorum is the core primitive enabling: Raft/Paxos (majority quorums for commit + election), Cassandra tunable consistency (W, R, N), distributed locking (acquire from majority), and consensus in general. Trade-off: larger quorum = stronger consistency + lower availability (more nodes must be up); smaller quorum = higher availability + weaker consistency.

---

### 🟢 Simple Definition (Easy)

Quorum: "enough" votes in a distributed system. For 5 nodes: quorum = 3 (majority). Write confirmed? 3 nodes must say yes. New leader elected? 3 nodes must vote for them. The key property: any two groups of 3 out of 5 MUST share at least 1 node. That shared node knows about both decisions — prevents two conflicting decisions happening simultaneously. Like requiring 3 out of 5 board members to pass a resolution: two conflicting resolutions can't both pass (they'd need separate 3-member majorities — impossible without sharing a member).

---

### 🔵 Simple Definition (Elaborated)

Why quorum size matters: N=5, quorum=2 (minority). Two groups of 2 nodes can make conflicting decisions simultaneously (2+2=4 < 5, no forced overlap). N=5, quorum=3 (majority). Any two groups of 3 must share ≥1 node (3+3=6 > 5 — pigeonhole). That shared node blocks conflicting decisions. Cost: need 3 of 5 nodes available to make decisions. If 3 nodes crash: system stops (can't form quorum). This is a fundamental trade-off: stronger consistency (larger quorum) → lower fault tolerance (more failures break quorum). Tunable quorums (W, R, N) let you set the trade-off per operation.

---

### 🔩 First Principles Explanation

**Quorum mathematics and production configurations:**

```
MAJORITY QUORUM MATHEMATICS:

  N nodes. Majority quorum Q = ⌊N/2⌋ + 1.

  N=1: Q=1. Trivial (single node).
  N=2: Q=2. Must have BOTH nodes. Any failure → can't commit. Useless for HA.
  N=3: Q=2. Tolerates 1 failure (3-2=1).
  N=4: Q=3. Tolerates 1 failure (4-3=1). Same as N=3 but more nodes!
           Reason: even N has no benefit over N-1 (odd). Always use odd cluster sizes.
  N=5: Q=3. Tolerates 2 failures (5-3=2).
  N=7: Q=4. Tolerates 3 failures (7-4=3).

  Failures tolerated = N - Q = N - (⌊N/2⌋+1) = ⌊(N-1)/2⌋.

  INTERSECTION PROOF:
    Q1 and Q2, both majority quorums of N nodes.
    |Q1| + |Q2| = (⌊N/2⌋+1) + (⌊N/2⌋+1) = 2⌊N/2⌋+2.
    For odd N=2k+1: 2k+2 > 2k+1 = N. So |Q1| + |Q2| > N.
    By pigeonhole: Q1 ∩ Q2 ≠ ∅ (can't fit N+something elements in N slots without overlap).

  WHY EVEN N IS WASTEFUL:
    N=4: Q=3. Tolerates 1 failure.
    N=3: Q=2. Tolerates 1 failure. Same tolerance, fewer nodes.
    N=4 is strictly worse than N=5 (same cost, less tolerance).
    Always use odd N: 1, 3, 5, 7.

READ/WRITE QUORUMS (ROWA — Read One, Write All variant):

  Parameters: N (replication factor), W (write quorum), R (read quorum).

  Consistency requirement: W + R > N.

  Proof:
    Write confirmed on W nodes.
    Read queries R nodes.
    W + R > N → at least one node is in BOTH write set and read set.
    That overlapping node has the latest write.
    Read returns that node's value (max timestamp/version).
    → Read returns latest write.

  CASSANDRA CONFIGURATIONS:

  N=3 (RF=3):
    W=1, R=1: write to 1, read from 1. W+R=2 ≤ 3. NOT consistent. Eventual consistency.
              Max performance. Flash sale: use this for view counts (approximate OK).

    W=2, R=2: write to 2, read from 2. W+R=4 > 3. Consistent. Tolerates 1 failure.
              "QUORUM" consistency level in Cassandra. Production default for most use cases.

    W=3, R=1: write to all 3, read from 1. W+R=4 > 3. Consistent.
              "ALL" write + "ONE" read. Writes are synchronous to all. Reads fast.
              Use: read-heavy workloads where writes are rare but reads are critical.

    W=1, R=3: write to 1, read from all 3. W+R=4 > 3. Consistent.
              "ONE" write + "ALL" read. Writes fast. Reads must wait for all 3.
              Use: write-heavy workloads (append-only logs). Rarely practical.

    W=3, R=3: W+R=6 > 3. Consistent but requires ALL nodes for BOTH read and write.
              ANY node failure → unavailable. Not recommended.

  N=5 (RF=5):
    W=3, R=3: W+R=6 > 5. Consistent. Tolerates 2 failures for BOTH reads and writes.
              "QUORUM" in RF=5 cluster. Strong consistency.

    W=5, R=1: W+R=6 > 5. Consistent. All 5 nodes must ACK writes. Any failure → write blocks.
              Very high write durability but low availability.

    W=1, R=5: opposite. Write fast. Read must get all 5. Not practical.

    W=3, R=1: W+R=4 < 5. NOT consistent. Possible stale reads.
              This is a common misconfiguration! RF=5, QUORUM level writes (W=3), but ONE reads.

  DYNAMO-STYLE CONFIGURATIONS:
    DynamoDB: N=3 (by default), W and R configurable.
    Strong consistency: R=2 (majority). Eventually consistent: R=1.
    Writes: always W=2 (majority).
    Strong read: R=2 (overlap with W=2: 2+2=4>3). Consistent.
    Eventually consistent read: R=1 (1+2=3 not > 3). Stale possible.

QUORUM IN RAFT/PAXOS:

  Raft uses MAJORITY quorum for BOTH writes AND leader elections.

  WRITE QUORUM:
    5-node cluster. Leader commits entry at index N when majority (3) ACK AppendEntries.
    3 nodes have entry → committed. 2 can crash → 3 remaining still have it. Safe.

  ELECTION QUORUM:
    Candidate gets votes from majority (3) → becomes leader.
    Two candidates can't BOTH get majority (intersection → at least 1 voter voted for only 1).
    → At most 1 leader per term.

  IMPORTANT: Raft uses SAME quorum size for both. This is not required in general.

  FLEXIBLE PAXOS (Heidi Howard et al., 2016):
    Observation: write quorum and read quorum (quorum for leader election) need not be equal.
    Only requirement: elect_quorum ∩ write_quorum ≠ ∅.
    Example N=5: elect_quorum=4 (large), write_quorum=2 (small).
    4+2=6>5. Overlap guaranteed.
    Write quorum of 2: very fast writes (only 2 nodes must ACK).
    Election quorum of 4: rare operation, 4 nodes needed (but elections are infrequent).
    Trade-off: fast normal operation (W=2) at the cost of slower elections.

QUORUM UNAVAILABILITY:

  N=5, Q=3. 3 nodes must be up for operations to proceed.

  If 3 nodes fail: system stops (cannot form quorum). Returns error to clients.
  This is CORRECT behavior under the CAP theorem (choosing C over A).

  Alternative: use W=1 or R=1 (minority quorum) → can operate with 1 node up.
  But: no consistency guarantee (W+R may not > N).
  This is AP (availability over consistency): Cassandra ONE consistency level.

  SLOPPY QUORUM (Cassandra fallback):
    If coordinator can't reach enough nodes for QUORUM:
    Option: write to first W available nodes (even if they're not the usual replicas).
    Store "hint" on those nodes for the original replica when it recovers.
    This is "sloppy quorum" — higher availability but weaker consistency.
    After recovery: "hinted handoff" delivers missed writes.
    Result: eventual consistency, not strong consistency.
    NOT safe for banking/financial. OK for social media (approximate counts, likes).
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT quorum (no minimum agreement required):

- Split-brain: two nodes independently make conflicting decisions, no overlap
- Two leaders simultaneously: both accept writes → data divergence
- Conflicting reads and writes: no guarantee that read sees latest write

WITH quorum:
→ Intersection guarantee: any two quorums overlap → shared node blocks conflicting decisions
→ Tunable consistency: W, R, N tunable per use case (consistency vs. availability)
→ Fault tolerance: mathematically defined failure tolerance (N - Q failures tolerated)

---

### 🧠 Mental Model / Analogy

> A democratic committee of 5 members voting on motions. A motion passes only if 3+ members vote yes (majority = quorum). Can two contradictory motions both pass? NO: both would need 3+ votes each = 6+ votes total, but there are only 5 members. At least one member would have to vote for BOTH — impossible in one vote. The one shared member blocks the contradiction. More members needed = harder to get quorum = committee is more resistant to hasty decisions (stronger consistency) but harder to convene (lower availability).

"Committee members" = distributed nodes
"Quorum of 3 votes to pass" = majority quorum for commit
"Two contradictory motions can't both get 3 votes" = no split-brain (quorum intersection)
"Harder to convene if members absent" = quorum unavailability on node failures

---

### ⚙️ How It Works (Mechanism)

**Cassandra quorum configuration:**

```bash
# Cassandra keyspace with RF=3 (3 replicas per row):
CREATE KEYSPACE payments
WITH replication = {'class': 'NetworkTopologyStrategy', 'us-east-1': 3, 'eu-west-1': 3};
# 6 total replicas (3 per DC). N=6 globally, N=3 per DC.

# QUORUM consistency in Cassandra = majority of replicas globally:
# Global quorum: W + R > 6. W=4, R=3 (or W=3, R=4, etc.)
# More commonly: LOCAL_QUORUM = majority of replicas in local DC only:
# LOCAL_QUORUM (dc1 only): W=2, R=2, N=3. W+R=4>3. Consistent within dc1.

# Write with LOCAL_QUORUM (wait for 2/3 dc1 replicas):
cqlsh> CONSISTENCY LOCAL_QUORUM;
cqlsh> INSERT INTO payments.transactions (id, amount, status)
       VALUES (uuid(), 100.00, 'PENDING');
# Returns after 2 of 3 dc1 replicas confirm. Fast (single DC).

# Read with LOCAL_QUORUM (read from 2/3 dc1 replicas):
cqlsh> SELECT * FROM payments.transactions WHERE id = ?;
# Queries 2 of 3 dc1 replicas. Takes value with latest timestamp. Consistent.

# Monitor quorum failures:
$ nodetool tpstats | grep -i quorum
# ReadRepairRepairedBackground: reads that triggered background repair (stale replica found).
# CoordinatorReadLatency: latency waiting for R replicas to respond.

# Check node status (availability of quorum):
$ nodetool status payments
# If < 2 nodes UN (Up/Normal) in a DC: LOCAL_QUORUM fails for that DC.
```

---

### 🔄 How It Connects (Mini-Map)

```
Replication Strategies (W/R/N parameters define quorum behavior)
        │
        ▼
Quorum ◄──── (you are here)
(minimum set of nodes with intersection guarantee)
        │
        ├── Raft (uses majority quorum for both commit and election)
        ├── Split Brain (the problem quorum prevents: two conflicting leaders)
        └── Consistent Hashing (where data lives on which nodes — affects which nodes form quorum)
```

---

### 💻 Code Example

**Application-level quorum for distributed key-value:**

```java
public class QuorumClient {

    private final List<KVNode> nodes; // All N nodes
    private final int writeQuorum;   // W
    private final int readQuorum;    // R

    public QuorumClient(List<KVNode> nodes, int W, int R) {
        this.nodes = nodes;
        this.writeQuorum = W;
        this.readQuorum = R;
        // Verify: W + R > N (consistency requirement)
        if (W + R <= nodes.size()) {
            throw new IllegalArgumentException(
                "W + R must be > N for consistency. W=" + W + " R=" + R + " N=" + nodes.size()
            );
        }
    }

    // WRITE: wait for W nodes to ACK.
    public void write(String key, String value, long version) throws QuorumException {
        AtomicInteger acks = new AtomicInteger(0);
        List<CompletableFuture<Void>> futures = nodes.stream()
            .map(node -> CompletableFuture.runAsync(() -> {
                try {
                    node.put(key, value, version);
                    acks.incrementAndGet();
                } catch (Exception e) {
                    // Node unavailable — don't count as ACK.
                }
            }))
            .collect(toList());

        // Wait for all, then check if quorum reached:
        CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
            .orTimeout(5, TimeUnit.SECONDS)
            .whenComplete((v, e) -> {}); // Ignore timeout — check acks count.

        if (acks.get() < writeQuorum) {
            throw new QuorumException("Write quorum not reached: " + acks.get() + "/" + writeQuorum);
        }
    }

    // READ: query R nodes, return highest-version value.
    public String read(String key) throws QuorumException {
        List<VersionedValue> responses = new CopyOnWriteArrayList<>();

        nodes.stream()
            .map(node -> CompletableFuture.supplyAsync(() -> {
                try {
                    return node.get(key); // Returns VersionedValue(version, value).
                } catch (Exception e) {
                    return null;
                }
            }))
            .collect(toList())
            .stream()
            .map(f -> f.orTimeout(5, TimeUnit.SECONDS))
            .forEach(f -> f.thenAccept(v -> { if (v != null) responses.add(v); }));

        if (responses.size() < readQuorum) {
            throw new QuorumException("Read quorum not reached: " + responses.size() + "/" + readQuorum);
        }

        // Return value with the highest version (latest write wins):
        return responses.stream()
            .max(Comparator.comparingLong(VersionedValue::getVersion))
            .map(VersionedValue::getValue)
            .orElse(null);
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                             | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Quorum = majority                         | Majority quorum is the most common type but not the only one. Raft and Paxos use majority quorums. But weighted quorums (nodes have different weights based on reliability/location), grid quorums (O(√N) instead of O(N/2)), and flexible quorums (different quorum sizes for reads vs. elections) are all valid. Cassandra's W + R > N allows any combination that satisfies the intersection property — W=1, R=5 is technically a quorum system |
| W + R > N guarantees linearisable reads   | W + R > N guarantees that a read will see at least one node that had the latest write. But if there are CONCURRENT writes (multiple writers), Last-Write-Wins (by timestamp) resolves conflicts. Clock skew can cause the "later" write (by wall clock) to be overwritten by an "earlier" write with a higher timestamp. True linearisability requires additional coordination (read repair + fencing, or a single leader for writes)              |
| A quorum system always prevents data loss | Quorum prevents loss of COMMITTED data (written to quorum), but only if you always read from quorum too. If a write goes to W=2 of 3 nodes, and you later read from only R=1 node — and that 1 node is the one that missed the write — you get stale data. W+R > N prevents this: 2+2=4>3. But if the configuration violates W+R>N (W=1, R=1, N=3): a write to 1 node + read from a different 1 node → stale read                                  |
| Raft's quorum is fixed at N/2+1           | Basic Raft uses N/2+1 majority for everything. But Raft implementations can use Flexible Paxos: different quorum sizes for commit vs. election. etcd uses standard majority. Some academic Raft variants allow smaller write quorums (W=1) as long as the election quorum is large enough to guarantee overlap with write quorum. Production systems typically use standard majority for simplicity and predictability                             |

---

### 🔥 Pitfalls in Production

**Misconfigured W+R quorum allows stale reads:**

```
PROBLEM: Cassandra cluster RF=5, keyspace 'users'.
         Team sets: WRITE consistency = QUORUM (W=3), READ consistency = ONE (R=1).
         W + R = 4, N = 5. 4 < 5 → NOT consistent! (W+R must be > N, not ≥ N).

         User updates email. Write to 3 of 5 nodes (QUORUM).
         User reads email immediately. Read from 1 node (ONE).
         That 1 node may be one of the 2 that MISSED the write.
         User sees old email despite just updating it. Support ticket raised.

BAD: W + R = N (not > N):
  # cqlsh:
  CONSISTENCY QUORUM; -- W=3 for RF=5
  UPDATE users.profiles SET email='new@example.com' WHERE id=123;

  CONSISTENCY ONE; -- R=1 ← BUG: W+R=3+1=4 not > 5
  SELECT email FROM users.profiles WHERE id=123;
  -- May return 'old@example.com' from one of 2 nodes that missed the write.

FIX: Ensure W + R > N:
  # For RF=5: both QUORUM (W=3 and R=3), W+R=6 > 5:
  CONSISTENCY QUORUM; -- For BOTH reads and writes.
  UPDATE users.profiles SET email='new@example.com' WHERE id=123;
  SELECT email FROM users.profiles WHERE id=123; -- Returns 'new@example.com' ✓

  # Or: use LOCAL_QUORUM (within one DC, if multi-DC deployment):
  # Each DC has its own RF and quorum. LOCAL_QUORUM = majority within DC.

  # Application-level enforcement:
  session.setDefaultConsistency(ConsistencyLevel.LOCAL_QUORUM); // Default for all operations.
  // Override per query only where weaker consistency is explicitly acceptable.

  # Operations team: set consistency levels per application layer in config, not per query.
  # Monitor: nodetool tpstats 'ReadRepairRepairedBackground' metric.
  # If high: many reads finding stale replicas → possibly W+R misconfigured.
```

---

### 🔗 Related Keywords

- `Replication Strategies` — W, R, N parameters that configure quorum behavior
- `Split Brain` — the problem quorum intersection prevents (two simultaneous conflicting decisions)
- `Raft` — uses majority quorum for both log commit and leader election
- `Consistent Hashing` — determines which N nodes store a key (the candidate nodes for quorum)
- `Hinted Handoff` — Cassandra's fallback when quorum unavailable (sloppy quorum)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Quorum Q of N nodes: any two quorums     │
│              │ overlap → prevents conflicting decisions  │
│              │ W + R > N guarantees consistent reads    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Configuring Cassandra/DynamoDB consistency│
│              │ levels; understanding Raft/Paxos safety; │
│              │ designing fault-tolerant distributed ops │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Minority quorum (W+R ≤ N): gives         │
│              │ availability illusion without consistency │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Any two majorities share a member;      │
│              │  that shared member blocks contradiction."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Split Brain → Raft → Cassandra →         │
│              │ Consistent Hashing → Replication Strategies│
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A DynamoDB table with N=3 and strong consistency reads (R=2). The table has 3 replicas: R1, R2, R3. A write completes to R1 and R2 (W=2). Immediately after, a read is issued that contacts R2 and R3. R3 hasn't received the write yet. Does the read return the latest value? Which replica provides it? Now what if the read contacted R1 and R3 only? What if R2 crashed after ACKing the write, so only R1 has the new value — can a W=2 read still be consistent?

**Q2.** Kafka uses ISR (In-Sync Replicas) with min.insync.replicas. A topic has replication-factor=3, min.insync.replicas=2. Producer uses acks=all. Is this a quorum system? What is N, W, and effectively R? If one replica falls out of ISR (too slow), can producers still write? What happens to consumers reading from the non-ISR replica — is this safe?
