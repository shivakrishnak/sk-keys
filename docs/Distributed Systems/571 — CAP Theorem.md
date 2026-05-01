---
layout: default
title: "CAP Theorem"
parent: "Distributed Systems"
nav_order: 571
permalink: /distributed-systems/cap-theorem/
number: "571"
category: Distributed Systems
difficulty: ★★★
depends_on: "Distributed Systems Fundamentals"
used_by: "PACELC, Consistency Models, NoSQL Databases"
tags: #advanced, #distributed, #consistency, #availability, #theory
---

# 571 — CAP Theorem

`#advanced` `#distributed` `#consistency` `#availability` `#theory`

⚡ TL;DR — **CAP Theorem** states a distributed system can guarantee at most two of three properties: **C**onsistency (every read sees the latest write), **A**vailability (every request gets a response), **P**artition tolerance (the system works despite network splits) — and since P is unavoidable in real networks, the real choice is CP vs AP.

| #571            | Category: Distributed Systems               | Difficulty: ★★★ |
| :-------------- | :------------------------------------------ | :-------------- |
| **Depends on:** | Distributed Systems Fundamentals            |                 |
| **Used by:**    | PACELC, Consistency Models, NoSQL Databases |                 |

---

### 📘 Textbook Definition

The **CAP Theorem** (Brewer's Theorem, 2000, proved by Gilbert & Lynch 2002) states that in a distributed system, it is impossible to simultaneously guarantee all three of: **Consistency** (C) — all nodes see the same data at the same time (linearisability — every read reflects the most recent write); **Availability** (A) — every request receives a response (not necessarily containing the most recent data); **Partition Tolerance** (P) — the system continues operating despite arbitrary network partitions (message loss between nodes). Since network partitions are an unavoidable reality in any distributed system (latency spikes, hardware failures, network failures), P must be tolerated. The real design decision is: **during a partition, do you sacrifice C (AP system) or A (CP system)**? This theorem guides architectural decisions for distributed databases, queues, and coordination services.

---

### 🟢 Simple Definition (Easy)

CAP Theorem: during a network split between two database nodes, you must choose — (1) keep both nodes available but potentially return stale data (AP: available, partition-tolerant) or (2) refuse requests on the isolated node until the split is healed, ensuring data is always fresh (CP: consistent, partition-tolerant). You cannot have BOTH fresh data AND 100% availability during a network split.

---

### 🔵 Simple Definition (Elaborated)

Bank example: two bank branches, connected by phone. Network cut: phone line goes dead. Branch A: customer asks balance. Branch B just processed a transfer — Branch A doesn't know yet. AP choice: Branch A serves the request with stale balance (available, not consistent). CP choice: Branch A says "I can't serve you right now — phone is down, I don't know current balance" (consistent — either returns correct data or nothing, but not available). Real banks choose CP: "System unavailable, please try later" rather than show wrong balances.

---

### 🔩 First Principles Explanation

**CAP theorem trade-off during network partitions:**

```
THE PARTITION SCENARIO:

  Two database nodes: Node A (San Francisco) and Node B (New York).
  Normal operation: write to Node A → replicate to Node B.

  Network partition: SF ↔ NY network link fails.

  While partition lasts:
    Write arrives at Node A: user updates their balance from $100 to $50.
    Node A: records $50.
    Node B: still shows $100 (can't receive replication from Node A).

  User reads balance:
    Request goes to Node B (load balancer routes there).

  CHOICE: What does Node B do?

  AP CHOICE: Node B returns $100 (stale but available).
    System continues operating. Data may be wrong.
    Examples: Cassandra, CouchDB, DynamoDB (eventual consistency mode)
    Use case: social media likes count (stale by 1 second: acceptable)

  CP CHOICE: Node B returns an error or waits for partition to heal.
    System correctly refuses to serve potentially stale data.
    Examples: HBase, Zookeeper, etcd, Consul
    Use case: inventory reservation, bank balance (must be correct)

WHY P IS NOT OPTIONAL:

  "Why can't we just choose CA (consistent + available, ignore partitions)?"

  Because partitions WILL happen in any distributed system:
    - Network cable cut
    - Router failure
    - Switch misconfiguration
    - Cloud provider network issue
    - Overloaded server dropping packets
    - GC pause causing missed heartbeats (false partition detection)

  In a single-machine system: no network → no partition → CA is possible.
  In any multi-machine system: partitions are inevitable.

  Therefore: all distributed systems MUST be partition-tolerant.
  CAP reduces to: "During a partition, choose Consistency or Availability."

CAP DIAGRAM:

  During normal operation (no partition):
    All three properties maintained simultaneously.
    Partition: replication keeps all nodes consistent.

  During partition:

     Consistency ──────────────── You must give up one
         │                         during a partition
         │
    ─────┼──── Partition
         │     Tolerance
         │         │
    ─────┼─────────┼
         │
       Availability

  CP: Bank DB, ZooKeeper, etcd, Redis Cluster (default)
      User impact: service temporarily unavailable during partition

  AP: Cassandra, CouchDB, DynamoDB (eventual), DNS
      User impact: stale data during partition; self-heals eventually

NUANCE: CAP IS NOT BINARY:

  CAP is often over-simplified. Real systems have spectrum:

  "Consistency" in CAP = linearisability (strongest consistency model).
  Many systems offer WEAKER consistency (not linearisability):
    Sequential consistency: reads ordered but not necessarily instant.
    Causal consistency: see writes in causal order.
    Eventual consistency: all nodes eventually agree.

  Weaker consistency = more availability during partitions.

  PACELC theorem (more nuanced):
    Even without partition: trade-off between Latency and Consistency.
    High consistency (synchronous replication): higher write latency.
    Low latency (async replication): weaker consistency.

  DynamoDB:
    Default: AP (eventual consistency, low latency reads)
    Strongly consistent reads: CP (higher latency, more expensive)
    User selects per-request: choose the trade-off for each use case.

PRACTICAL DECISION GUIDE:

  Choose CP when:
    Data integrity is critical: financial transactions, inventory
    "Wrong answer is worse than no answer"
    Users can tolerate temporary unavailability
    Examples: bank accounts, order processing, distributed locks

  Choose AP when:
    Availability is more valuable than freshness
    "Stale answer is better than no answer"
    Users can tolerate eventual consistency
    Examples: social media likes, DNS, product catalog, shopping cart

  Real-world hint: if you'd use a database transaction, you probably want CP.
                   if you'd use a cache, you probably can tolerate AP.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT understanding CAP Theorem:

- Architects choose databases without understanding partitioning behavior
- Inconsistency in production: "why does my DB return stale data during outages?"
- Wrong database for the use case: AP database for financial transactions → data corruption

WITH CAP Theorem:
→ Intentional design: choose CP or AP based on business requirements
→ No surprises: understand what the system sacrifices during partitions
→ Architecture vocabulary: communicate trade-offs precisely with "CAP CP/AP" framing

---

### 🧠 Mental Model / Analogy

> Two bank branches connected by a telephone line. When the phone line goes down (network partition): Branch A doesn't know about Branch B's recent transactions. CP Branch: "I can't serve you correctly right now — come back when the line is up" (refuse request to stay consistent). AP Branch: "Here's the balance I know about, but it might be outdated" (serve stale data to stay available). Both branches cannot simultaneously give accurate balances AND serve all customers when the phone is down. Pick one.

"Two bank branches" = two distributed database nodes
"Telephone line goes down" = network partition between nodes
"CP Branch refuses service" = CP system returns error during partition (sacrifices availability)
"AP Branch serves stale balance" = AP system returns potentially stale data (sacrifices consistency)
"Cannot have both accurate AND always-available during phone outage" = CAP impossibility result

---

### ⚙️ How It Works (Mechanism)

**CP vs AP behavior comparison in practice:**

```
CP SYSTEM (ZooKeeper example):

  3-node ZooKeeper cluster.
  Normal: leader + 2 followers. Leader handles writes.

  Network partition: Node 3 isolated from Node 1, Node 2.

  Node 3 receives read request:
    ZooKeeper: cannot satisfy consistent read (can't verify it's the current leader)
    Response: CONNECTION_LOSS exception
    Client must retry with Node 1 or Node 2 (majority partition).

  Behavior: Node 3 is UNAVAILABLE for reads during partition.
  Why: ZooKeeper guarantees linearisability → must reject rather than serve stale data.

AP SYSTEM (Cassandra example):

  3-node Cassandra cluster, replication_factor=3.
  Normal: writes go to all 3 nodes.

  Network partition: Node 3 isolated.

  Node 3 receives read request:
    Cassandra (consistency_level=ONE): returns data it has, even if stale.
    Response: returns data (potentially not the latest write if Node 3 is behind).

  On partition heal:
    Anti-entropy repair: nodes exchange data → Node 3 catches up.
    Read repair: client reads trigger background reconciliation.

  Behavior: Node 3 stays AVAILABLE but may return stale data.
  Why: Cassandra prioritises availability → eventual consistency.

JAVA: CHOOSING CONSISTENCY LEVEL PER QUERY (Cassandra):

  // Per-query consistency level selection:
  CqlSession session = CqlSession.builder().build();

  // Strong consistency: all replicas must respond (CP-like behavior):
  PreparedStatement strongRead = session.prepare(
      SimpleStatement.builder("SELECT balance FROM accounts WHERE id = ?")
          .setConsistencyLevel(ConsistencyLevel.QUORUM)  // majority must agree
          .build()
  );

  // Eventual consistency: just one replica (AP-like behavior):
  PreparedStatement fastRead = session.prepare(
      SimpleStatement.builder("SELECT last_login FROM users WHERE id = ?")
          .setConsistencyLevel(ConsistencyLevel.ONE)  // accept data from any one replica
          .build()
  );

  // Use strong for financial queries, fast for non-critical reads:
  session.execute(strongRead.bind(accountId));  // balance must be current
  session.execute(fastRead.bind(userId));        // last_login can be slightly stale
```

---

### 🔄 How It Connects (Mini-Map)

```
Distributed System (multiple nodes, network between them)
        │
        ▼
CAP Theorem ◄──── (you are here)
(Consistency vs Availability during Partition)
        │
        ├── PACELC (extends CAP: latency vs consistency even without partitions)
        ├── Consistency Models (spectrum: linearisability → eventual)
        └── NoSQL Database Selection (Cassandra=AP, HBase=CP, etc.)
```

---

### 💻 Code Example

**Database selection based on CAP requirements:**

```java
// Scenario: e-commerce platform choosing databases per feature

// INVENTORY (CP required): overselling = lost money → choose CP
@Repository
public class InventoryRepository {
    // Use PostgreSQL with serializable isolation:
    // Partition → DB temporarily unavailable → acceptable (show "temporarily unavailable")
    // Never show stale inventory count (would allow overselling)

    @Transactional(isolation = Isolation.SERIALIZABLE)
    public boolean reserveItem(String itemId, int quantity) {
        int available = jdbcTemplate.queryForObject(
            "SELECT stock FROM inventory WHERE item_id = ? FOR UPDATE",
            Integer.class, itemId);  // row-level lock

        if (available < quantity) return false;

        jdbcTemplate.update(
            "UPDATE inventory SET stock = stock - ? WHERE item_id = ?",
            quantity, itemId);  // atomic decrement
        return true;
    }
}

// PRODUCT VIEWS COUNTER (AP acceptable): stale by 1 second is fine → choose AP
@Repository
public class ProductAnalyticsRepository {
    // Use Cassandra with consistency_level=ONE:
    // Partition → counter may be slightly wrong → acceptable (not financial data)
    // Always available → never show error on product page

    public void incrementViewCount(String productId) {
        cassandraTemplate.execute(
            "UPDATE product_stats SET view_count = view_count + 1 WHERE product_id = ?",
            productId
            // Consistency.ONE → writes to any 1 replica → fast, AP behavior
        );
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                            | Reality                                                                                                                                                                                                                                                                                                                                                                          |
| -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CAP means you pick only 2 of 3 properties all the time   | CAP only applies during a network partition. Without a partition, you can have both consistency and availability. The theorem says: when a partition occurs, you must choose one to sacrifice. Most systems are fine >99.9% of the time (no partition) and only exhibit C vs A trade-offs during rare partition events                                                           |
| CP means always consistent, AP means always inconsistent | CP means: during a partition, the system prefers consistency over availability (may refuse requests). Between partitions, CP systems are both consistent AND available. AP means: during a partition, the system serves available (possibly stale) responses. After partition heals, AP systems converge to consistency. The difference only matters during the partition window |
| Cassandra is AP, so it's always inconsistent             | Cassandra's consistency level is configurable per query. With consistency_level=QUORUM (majority of replicas must agree), Cassandra behaves like a CP system. With consistency_level=ONE (any one replica), it's AP. A database's CAP classification is not absolute — it depends on configuration and usage                                                                     |
| NoSQL = AP, SQL = CP                                     | This is a dangerous oversimplification. CockroachDB and Google Spanner are distributed SQL databases that are CP. DynamoDB offers both CP and AP modes per query. MongoDB can be CP or AP depending on write concern settings. The storage engine architecture (SQL vs NoSQL) does not determine the CAP classification                                                          |

---

### 🔥 Pitfalls in Production

**AP system used for inventory causing overselling:**

```
PROBLEM: AP database chosen for inventory = orders accepted during partition

  Setup: DynamoDB (default eventual consistency) for inventory.
  Event: large sale, high traffic → DynamoDB replication lag increases.

  Item stock: 10 units. Two orders arrive simultaneously.

  Node 1: reads stock = 10 → confirms order A (reduces to 9)
  Node 2: reads stock = 10 (replication lag — hasn't received Node 1's write) → confirms order B

  Result: both orders confirmed. Stock becomes -1. OVERSOLD.

  This is the exact scenario AP databases allow during high load (not just partitions).
  Replication lag is functionally equivalent to a temporary partition.

BAD: Using DynamoDB eventual consistency for inventory:
  client.putItem(PutItemRequest.builder()
      .tableName("inventory")
      // No condition check → race condition allowed
      .build());

FIX 1: CONDITIONAL WRITES (DynamoDB optimistic locking):
  // Use condition expression: only succeed if stock > quantity being ordered
  client.updateItem(UpdateItemRequest.builder()
      .tableName("inventory")
      .key(Map.of("item_id", AttributeValue.fromS(itemId)))
      .updateExpression("SET stock = stock - :qty")
      .conditionExpression("stock >= :qty")  // atomic conditional update
      .expressionAttributeValues(Map.of(":qty", AttributeValue.fromN("1")))
      .build());
  // If condition fails (stock < qty): throws ConditionalCheckFailedException
  // Prevents overselling even with eventual consistency

FIX 2: STRONGLY CONSISTENT READS + CONDITIONAL WRITES:
  // DynamoDB strongly consistent read = CP for this operation
  GetItemRequest request = GetItemRequest.builder()
      .tableName("inventory")
      .key(Map.of("item_id", AttributeValue.fromS(itemId)))
      .consistentRead(true)  // CP: always reads latest, not stale
      .build();

FIX 3: SWITCH TO CP DATABASE FOR INVENTORY:
  PostgreSQL + SELECT FOR UPDATE (serializable transactions).
  Accept: DB temporarily unavailable during extreme events.
  Show: "Inventory system temporarily unavailable" rather than oversell.
```

---

### 🔗 Related Keywords

- `PACELC` — extends CAP: adds Latency vs Consistency trade-off even without partitions
- `Eventual Consistency` — AP systems' consistency model: all nodes converge eventually
- `Linearisability` — C in CAP (strongest consistency): every read sees latest write
- `Consistency Models` — spectrum from linearisability (strong) to eventual (weak)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Network partitions are unavoidable;       │
│              │ during partition: choose C or A           │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Choosing database for feature; diagnosing │
│              │ consistency bugs; architecture trade-offs │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Using AP database for financial/inventory │
│              │ data without conditional writes            │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Two bank branches, phone line down —     │
│              │  serve stale or refuse? Pick one."        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ PACELC → Consistency Models               │
│              │ → Eventual Consistency                    │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A shopping cart service uses Cassandra (AP, eventual consistency). User adds 3 items to cart → network partition → all 3 writes go to Node 1. User refreshes cart from Node 2 (which hasn't received the writes yet): sees empty cart. User re-adds the 3 items. Partition heals. Both sets of 3-item writes arrive at all nodes. Cassandra must reconcile conflicting writes. Describe the conflict resolution: what does the final cart look like? Is this acceptable for a shopping cart? How does Amazon handle this (research their Dynamo paper's approach)?

**Q2.** The CAP theorem defines Consistency as "linearisability" — the strongest consistency model. But many databases offer weaker consistency (causal, monotonic reads, read-your-writes). Does a system that offers "read-your-writes" consistency (but not full linearisability) still have to choose between C and A during a partition? Explain: is "read-your-writes" possible in an AP system during a partition? What about causal consistency?
