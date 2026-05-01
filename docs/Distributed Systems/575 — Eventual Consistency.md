---
layout: default
title: "Eventual Consistency"
parent: "Distributed Systems"
nav_order: 575
permalink: /distributed-systems/eventual-consistency/
number: "575"
category: Distributed Systems
difficulty: ★★★
depends_on: "Consistency Models, CAP Theorem"
used_by: "Cassandra, DNS, Shopping Cart, CRDTs"
tags: #advanced, #distributed, #consistency, #availability, #replication
---

# 575 — Eventual Consistency

`#advanced` `#distributed` `#consistency` `#availability` `#replication`

⚡ TL;DR — **Eventual Consistency** guarantees that if no new writes occur, all replicas will **eventually** converge to the same value — trading immediate consistency for higher availability, lower latency, and fault tolerance.

| #575            | Category: Distributed Systems        | Difficulty: ★★★ |
| :-------------- | :----------------------------------- | :-------------- |
| **Depends on:** | Consistency Models, CAP Theorem      |                 |
| **Used by:**    | Cassandra, DNS, Shopping Cart, CRDTs |                 |

---

### 📘 Textbook Definition

**Eventual Consistency** is the weakest consistency model in the distributed systems hierarchy, guaranteeing that given sufficient time without new writes, all replicas of a data item will converge to the same value. Reads on an eventually consistent system may return stale data — the value of an older write — because replicas propagate updates asynchronously, and a read may hit a replica that has not yet received the latest write. The model was formalised in Werner Vogel's 2008 paper "Eventually Consistent" and is closely associated with Amazon's Dynamo architecture. Eventual consistency is typically implemented via: asynchronous multi-master replication; gossip protocol for update propagation; read repair (correct stale values on read) and anti-entropy (background sync process). The model enables high availability under network partitions (the A in CAP) and low write latency (no synchronous replication round-trip). Applications using eventual consistency must handle conflicts (concurrent writes to the same key on different replicas) via Last-Write-Wins (LWW), CRDTs, or application-level merge logic.

---

### 🟢 Simple Definition (Easy)

Eventual consistency: all copies of the data will agree eventually, but right now some might be behind. Like a Wikipedia article: if you edit it, the change appears on some servers before others. A few seconds later: all servers show the updated article. During those few seconds: some users see the old version. The database accepts writes fast (no waiting for all replicas) and syncs in the background.

---

### 🔵 Simple Definition (Elaborated)

DNS is the most familiar eventually consistent system. Update: change your domain's IP from 1.2.3.4 to 5.6.7.8. TTL = 300 seconds (5 minutes). Global DNS propagation: 24-48 hours for all 13 root nameserver caches to update. During propagation: some users in Asia resolve to the old IP, some in the US to the new IP. Eventually: all caches expire and re-resolve to 5.6.7.8. This is acceptable for DNS — most users don't even notice a brief inconsistency in domain resolution. The alternative (strongly consistent DNS that waits for all caches globally to acknowledge) would make every DNS change a multi-minute operation. Eventual consistency is the right model here.

---

### 🔩 First Principles Explanation

**Eventual consistency mechanisms: gossip, read repair, anti-entropy:**

```
EVENTUAL CONSISTENCY IMPLEMENTATION IN CASSANDRA:

Setup:
  6-node Cassandra cluster, RF (Replication Factor) = 3.
  Table: user_sessions (user_id, last_active, session_token)
  Consistency level for writes and reads: ONE (single node ACK).

WRITE PATH (eventual consistency):

  Client → Coordinator node (any node, random or hash-routed).
  Coordinator → determines replica nodes via consistent hashing.
  Coordinator → writes to 3 replica nodes simultaneously.

  Write with ONE consistency:
    Coordinator waits for ACK from 1 of 3 replicas.
    As soon as 1 ACK received → responds to client: OK.
    Other 2 replicas: receive write asynchronously.

  Timeline:
    T=0: Client writes user_id=123, last_active=14:30:00, token=abc123.
    T=0: Replica A receives write → ACKs coordinator.
    T=0.001: Coordinator responds to client: written ✓.
    T=0.005: Replica B receives async write.
    T=0.010: Replica C receives async write.

  What if client reads at T=0.003?
    Read goes to Replica B (not yet updated).
    Returns: last_active=14:00:00, token=oldtoken → STALE READ.
    This is legal under eventual consistency.

  What if client reads at T=0.015?
    All 3 replicas updated → any read returns latest value.
    Convergence achieved. Eventual consistency satisfied.

CONFLICT: CONCURRENT WRITES TO SAME KEY ON DIFFERENT REPLICAS:

  Network partition (Replica A and B cannot communicate):

  T=0: Alice updates password on Replica A: token=alice_v1.
  T=0: Alice also updates from mobile on Replica B: token=alice_v2.
  T=5: Partition heals. A and B must reconcile.

  Which write wins?

  Strategy 1: LAST-WRITE-WINS (LWW) — Cassandra default:
    Each write carries a server timestamp.
    Higher timestamp wins: if A's write is T=1000ms and B's is T=1001ms → B wins.

    RISK: clock skew. If B's clock is 2 seconds ahead, B always wins regardless of true order.
    Acceptable for: user profile updates, cache data, analytics events.
    NOT acceptable for: counters, financial balances (silent data loss).

  Strategy 2: CRDTs (Conflict-Free Replicated Data Types):
    Data structure designed so concurrent writes always MERGE correctly.
    G-Counter (Grow-only counter): each replica tracks its own count.
    Total count = sum of all replica counts.
    Concurrent increments on different replicas → merge = sum of all → no conflict possible.
    See keyword #621 (CRDT).

  Strategy 3: APPLICATION-LEVEL MERGE (Amazon Dynamo shopping cart):
    Shopping cart modelled as a set of items.
    Concurrent adds on 2 replicas → merge = union of both sets.
    Result: user gets both items in cart (never loses items).
    User must manually remove duplicates if they added same item twice.
    Acceptable for: shopping cart (losing items = worse experience than having duplicates).

READ REPAIR:

  When: a read with QUORUM or ALL consistency contacts multiple replicas.
  Some replicas return stale data. Coordinator detects inconsistency.

  Action: coordinator sends the latest value back to the stale replicas asynchronously.
  Effect: stale replicas are updated as a side effect of the read operation.

  In Cassandra: read_repair_chance = 0.1 (10% of reads trigger async repair of stale replicas).

  Timeline:
    Client: GET user_id=123 with QUORUM (contacts 2 of 3 replicas).
    Replica A: returns last_active=14:30:00 (latest).
    Replica B: returns last_active=14:00:00 (stale).
    Coordinator: detects discrepancy → returns 14:30:00 to client.
    Coordinator (async): sends 14:30:00 to Replica B → background repair.

ANTI-ENTROPY (MERKLE TREE):

  Problem: replicas can silently diverge due to node failures, dropped messages.
  Solution: background process periodically compares replicas and repairs differences.

  Cassandra: merkle tree-based repair.
  Each node builds a Merkle tree (hash tree) of its data.
  Nodes exchange Merkle tree roots → if roots differ, data differs.
  Efficient comparison: O(log N) messages to find which ranges diverge.
  Cassandra repair: `nodetool repair` command triggers manual anti-entropy.

  DNS anti-entropy: zone transfer (AXFR/IXFR) between primary and secondary nameservers.

EVENTUAL CONSISTENCY TIMING:

  "Eventual" is ambiguous — no upper time bound guaranteed by the model.
  In practice:
    Cassandra within datacenter: ~1-10ms for all replicas to converge.
    Cassandra cross-datacenter: ~50-200ms.
    DNS: minutes to hours (TTL-limited propagation).
    Git distributed repos: minutes to days (manual push/pull).

  The "eventual" in eventual consistency has no SLA in the abstract model.
  Real systems often have empirical convergence bounds: "99.9% within 200ms."

LAST-WRITE-WINS: TIMESTAMP CONFLICT RESOLUTION:

  Cassandra LWW:
    Each write stamped with client-provided timestamp (microseconds since epoch).
    Write with highest timestamp wins for each column.

  Risk: NTP clock drift.
    Node A clock: 1000ms ahead of actual time.
    Node B clock: accurate.

    True sequence: B writes x=10 at T_real=14:30:00.000, A writes x=5 at T_real=14:30:00.001.
    Cassandra sees: A's timestamp = 14:30:01.000 (1s ahead), B's timestamp = 14:30:00.001.
    LWW: A wins (higher timestamp) → x=5 despite B's write being more recent in real time.

  Mitigation: use server-side timestamps (Cassandra USING TIMESTAMP = <microseconds>).
              Monitor NTP synchronization. Use CRDTs for counters instead of LWW.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT eventual consistency (strong consistency everywhere):

- Every write waits for all replicas to acknowledge (cross-continental: 200ms+ per write)
- Partition = system unavailable (AP business like Amazon's cart = catastrophic)
- Write throughput limited by slowest replica's acknowledgment time

WITH eventual consistency:
→ High write throughput: writes return after first replica ACK (1ms vs 200ms)
→ Fault tolerance: system continues serving reads/writes during partial failures
→ Geographic distribution: accept writes in any region without cross-region coordination

---

### 🧠 Mental Model / Analogy

> A WhatsApp group chat where messages are delivered to some members instantly and some members' phones briefly go offline. When the offline members reconnect, they receive the queued messages in order and eventually see the same conversation as everyone else. During the offline period: the offline member has a "stale" view. After reconnection: convergence. "Read repair" = someone forwards a missed message they saw was missing. "Anti-entropy" = WhatsApp's background sync of missed messages on reconnect. Conflicts = two members trying to edit the same document simultaneously (merge needed).

"Message delivered instantly to online members" = fast write (ONE consistency)
"Offline member catches up on reconnect" = eventual convergence via anti-entropy
"Two members edit same document simultaneously" = write conflict (needs merge strategy)
"Forwarding a missed message" = read repair (fixing stale replica as side effect of read)

---

### ⚙️ How It Works (Mechanism)

**Cassandra eventual consistency configuration:**

```cql
-- Cassandra: create table with eventual consistency (RF=3):
CREATE KEYSPACE social WITH REPLICATION = {
    'class': 'NetworkTopologyStrategy',
    'us-east-1': 3,     -- 3 replicas in US East
    'eu-west-1': 3      -- 3 replicas in EU West
};

CREATE TABLE social.user_posts (
    user_id UUID,
    post_id TIMEUUID,
    content TEXT,
    created_at TIMESTAMP,
    PRIMARY KEY (user_id, post_id)
) WITH CLUSTERING ORDER BY (post_id DESC);

-- WRITE with eventual consistency (ONE = write to 1 replica, async to rest):
INSERT INTO social.user_posts (user_id, post_id, content, created_at)
VALUES (uuid(), now(), 'Hello from Paris!', toTimestamp(now()))
USING CONSISTENCY ONE;
-- Fast! Returns as soon as 1 replica ACKs. Other 2 replicas get update async.

-- READ with eventual consistency (ONE = read from 1 replica, may be stale):
SELECT * FROM social.user_posts WHERE user_id = ?
CONSISTENCY ONE;
-- Fast but may return stale data if read hits a replica that missed a recent write.

-- READ with stronger consistency (QUORUM = contact 2 of 3 replicas):
SELECT * FROM social.user_posts WHERE user_id = ?
CONSISTENCY QUORUM;
-- Slower (contacts majority) but ensures latest data returned.
-- Tradeoff: use QUORUM for critical reads, ONE for high-volume feeds.
```

---

### 🔄 How It Connects (Mini-Map)

```
Consistency Models (full spectrum)
        │
        ▼
Eventual Consistency ◄──── (you are here)
(weakest model; highest availability)
        │
        ├── Gossip Protocol (mechanism for propagating updates)
        ├── Read Repair (fix stale replicas on read)
        ├── Anti-Entropy (background Merkle tree sync)
        └── CRDTs (conflict-free merge for concurrent writes)
```

---

### 💻 Code Example

**DynamoDB: eventual vs consistent reads:**

```python
import boto3

dynamodb = boto3.client('dynamodb', region_name='us-east-1')

# EVENTUALLY CONSISTENT READ (default — cheaper, faster):
# ConsistentRead=False: reads from any replica, may be up to 1 second stale.
# Cost: 0.5 × (size/4KB) read capacity units.
response = dynamodb.get_item(
    TableName='UserSessions',
    Key={'user_id': {'S': 'alice-123'}},
    ConsistentRead=False  # eventual consistency (default)
)
session = response.get('Item')  # May return slightly stale session data.

# STRONGLY CONSISTENT READ (linearisable — more expensive, always fresh):
# ConsistentRead=True: contacts the leader node for this partition key.
# Cost: 1.0 × (size/4KB) read capacity units (2× the cost of eventually consistent).
response = dynamodb.get_item(
    TableName='UserSessions',
    Key={'user_id': {'S': 'alice-123'}},
    ConsistentRead=True  # strong consistency
)
session = response.get('Item')  # Guaranteed to be the latest committed value.

# WHEN TO USE EACH:
# Eventual: high-read features (feed, recommendations, display-only data)
# Strong: authentication (must see the latest session token after login)
#
# Pattern: write session → read session with ConsistentRead=True
# for immediate post-login reads. Switch to eventually consistent
# after a few seconds (replication has likely caught up).
```

---

### ⚠️ Common Misconceptions

| Misconception                                                            | Reality                                                                                                                                                                                                                                                                                                                                                                   |
| ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Eventual consistency means data can be permanently wrong                 | Eventual consistency guarantees convergence to the CORRECT (latest) value given no new writes and sufficient time. The concern is WHEN you read — during the propagation window you may see stale data. After convergence: all replicas have the correct value. Data is never permanently wrong under eventual consistency (assuming no bugs in the convergence protocol) |
| Last-Write-Wins is the only conflict resolution for eventual consistency | LWW is the simplest and most common, but it silently discards concurrent writes (data loss risk). Alternatives: CRDTs (mathematically merge-safe data structures), vector clocks + application merge (Riak), multi-value registers (Dynamo — return both conflicting values, let application choose), operational transforms (Google Docs real-time editing)              |
| Eventual consistency is only for NoSQL                                   | Eventual consistency can be configured in traditional SQL databases. PostgreSQL: async replication creates eventual consistency between primary and replica. MySQL async replication: same. The model is about the replication strategy, not the database type. Even a relational database can be configured for eventual consistency                                     |
| Eventual consistency solves the CAP theorem                              | Eventual consistency doesn't "solve" CAP — it makes the AP choice in CAP. By weakening consistency (no guarantee of latest value), the system can remain available during partitions. This is the CAP trade-off, not a way around it. PACELC adds: even during normal operation (no partition), eventual consistency = EL (low latency)                                   |

---

### 🔥 Pitfalls in Production

**Last-Write-Wins silently discards counter increments:**

```
PROBLEM: Using Cassandra's LWW (eventual consistency) for a counter.
         Concurrent increments on different replicas → only one survives.

  Table: page_views (page_id, view_count)
  Writes: increment view_count for page_id = 'homepage'.
  Concurrent writes:
    Replica A at T=1000: view_count = 42 (was 41, incremented by +1)
    Replica B at T=1001: view_count = 42 (also was 41, also incremented by +1)

  Both replicas had stale value (41) and both wrote 42.
  After LWW reconciliation: view_count = 42 (B's timestamp wins if B's clock is later).

  Reality: 2 views happened → count should be 43. LWW gives us 42 → 1 view lost silently.

  At scale: millions of concurrent increments → massive undercounting.

BAD: Regular column with LWW for a counter:
  UPDATE page_stats SET view_count = view_count + 1 WHERE page_id = 'homepage';
  -- This is NOT atomic in Cassandra. Read-modify-write with LWW → lost updates.

FIX 1: USE CASSANDRA COUNTERS (CRDT-like counter table):
  CREATE TABLE page_counters (
      page_id TEXT PRIMARY KEY,
      view_count COUNTER
  );

  UPDATE page_counters SET view_count = view_count + 1 WHERE page_id = 'homepage';
  -- Cassandra COUNTER is a CRDT: merges correctly across all replicas.
  -- No lost updates under concurrent increments.
  -- Trade-off: COUNTER columns have restrictions (cannot mix with non-counter columns).

FIX 2: BATCH COUNTING WITH EVENTUAL FLUSH:
  -- Local Redis counter per node (strongly consistent locally):
  INCR page:homepage:views  -- atomic, local Redis

  -- Periodic background job: flush local Redis counts to Cassandra aggregate.
  -- Reduces concurrent writes to Cassandra. Each node owns its own count partition.
  -- Anti-entropy: sum all node counts for total. No conflicts between nodes.
```

---

### 🔗 Related Keywords

- `Consistency Models` — the full spectrum; eventual is the weakest model
- `CAP Theorem` — eventual consistency = the A (Available) choice in CAP
- `CRDTs` — conflict-free replicated data types for eventually consistent systems
- `Gossip Protocol` — common propagation mechanism for eventual consistency
- `Read Repair` — fixing stale replicas as a side effect of reads

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ All replicas converge to same value given │
│              │ no new writes — stale reads are legal     │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ High availability required; low-latency   │
│              │ writes; staleness briefly tolerable (DNS, │
│              │ feeds, shopping cart)                     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Financial balances; distributed locks;    │
│              │ unique constraint enforcement             │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "WhatsApp messages delivered eventually — │
│              │  offline members catch up on reconnect."  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ CRDTs → Gossip Protocol → Read Repair    │
│              │ → Anti-Entropy → Vector Clocks            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Amazon's Dynamo paper (2007) describes a shopping cart that uses eventual consistency with vector clocks. When two replicas diverge (e.g., items added to the cart on both replicas during a network partition), Dynamo returns BOTH conflicting versions to the client application rather than silently picking one. The application (or user) must merge them. Compare this to Cassandra's default Last-Write-Wins approach. What are the trade-offs? In which cases is returning multiple versions better than LWW?

**Q2.** A startup builds a collaborative document editor (like Google Docs). Documents are stored with eventual consistency across 5 distributed nodes. Two users simultaneously edit the same paragraph: User A changes "The cat sat on the mat" to "The cat sat on the floor". User B changes it to "The big cat sat on the mat". After convergence, what does the document say under Last-Write-Wins? Under Operational Transforms? Why do collaborative editing systems use Operational Transforms or CRDTs instead of LWW?
