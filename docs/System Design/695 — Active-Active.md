---
layout: default
title: "Active-Active"
parent: "System Design"
nav_order: 695
permalink: /system-design/active-active/
number: "695"
category: System Design
difficulty: ★★★
depends_on: "Redundancy / Failover, Load Balancing"
used_by: "Geo-Replication, Multi-Region Architecture"
tags: #advanced, #reliability, #distributed, #architecture, #pattern
---

# 695 — Active-Active

`#advanced` `#reliability` `#distributed` `#architecture` `#pattern`

⚡ TL;DR — **Active-Active** runs all redundant instances simultaneously as live traffic servers; every node handles requests, so any node failure is absorbed transparently with no switchover delay.

| #695 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Redundancy / Failover, Load Balancing | |
| **Used by:** | Geo-Replication, Multi-Region Architecture | |

---

### 📘 Textbook Definition

**Active-Active** (also called multi-master or multi-active) is a high-availability architecture pattern where all redundant nodes simultaneously handle live traffic. Unlike Active-Passive (where one node is primary and one is idle standby), Active-Active distributes load across all nodes at all times. When a node fails, the load balancer stops routing to it and the remaining nodes absorb its traffic — no promotion or switchover is required. Active-Active requires that all nodes be fully capable of serving any request, which for stateless services is trivially achieved, but for stateful services (databases) requires bidirectional replication or a shared data layer. The trade-off: Active-Active is more efficient (no idle capacity) and faster to recover (no switchover), but architecturally more complex, especially for databases requiring conflict resolution for concurrent writes to the same data.

---

### 🟢 Simple Definition (Easy)

Active-Active: all servers are live and handling requests at once. If one server fails, the others just handle more traffic — no need to "wake up" a standby. Compare to Active-Passive: one server works, one sits idle waiting to take over. Active-Active is like having all checkout lanes open at once vs. one open and others closed (waiting for the first to break).

---

### 🔵 Simple Definition (Elaborated)

Three application servers in Active-Active: each handles 1,000 requests/second (33% of 3,000 total). One fails. The load balancer stops routing to it. The remaining two each handle 1,500 requests/second (50% each). The system is degraded (reduced capacity) but still operational — no failover delay. In Active-Passive with one standby: the standby must be promoted and traffic redirected — takes 30-90 seconds. Active-Active for stateless services: simple. For databases (write-accepting): complex (who resolves conflicting writes to the same row from two different nodes?).

---

### 🔩 First Principles Explanation

**Active-Active for stateless vs. stateful services:**

```
STATELESS ACTIVE-ACTIVE (easy):
  Service: REST API (no server-side state, reads shared DB)
  All nodes: identical, any node handles any request
  Load balancer: round-robin or least-connections across all nodes
  Node failure: remove from LB pool, remaining nodes absorb traffic
  
  No data consistency problem (no local state → no conflict)
  No switchover: traffic immediately redirected by LB health check
  
  3 nodes at 33% capacity each:
  1 node fails → remaining 2 at 50% → degraded but functional
  Recovery: add new node, LB adds to pool, back to 33%

DATABASE ACTIVE-ACTIVE (complex):
  
  CHALLENGE: concurrent writes to same data from two nodes
  
  Example: User balance = $100
    Node A receives: Debit $30 → new balance = $70
    Node B receives (same instant): Debit $50 → new balance = $50
    Both writes committed on their respective nodes.
    Replication: both nodes receive each other's write.
    CONFLICT: which value is correct? $70 or $50?
    
    Actual answer: $20 ($100 - $30 - $50) — but neither node got this.
    Data corruption.
    
  CONFLICT RESOLUTION STRATEGIES:
  
  1. LAST WRITE WINS (LWW):
     Timestamp-based: latest timestamp wins.
     A wrote at T=100.01, B wrote at T=100.00 → A's write wins ($70)
     Problem: B's $50 debit is silently lost → user debited $50 without effect.
     Use: non-critical data, eventually consistent systems (social media "likes"),
          where approximate consistency is acceptable.
  
  2. CRDT (Conflict-free Replicated Data Types):
     Data structure designed so concurrent operations always merge correctly.
     Counters (G-Counter, PN-Counter): each node increments its own counter.
       Merge: sum all counters. Never conflicts.
     Example: shopping cart (add-only set): both carts merged = union.
     Limitations: only works for specific data structures.
                  Not suitable for "set balance to X" operations.
  
  3. APPLICATION-LEVEL CONFLICT DETECTION:
     Vector clocks track causal order.
     On conflict: expose to application → application resolves.
     DynamoDB with "last_writer_wins" or custom resolver.
     Amazon Dynamo paper: conflict resolution at application layer.
     Use: when business logic can decide (e.g., accept both, take max, etc.)
  
  4. MULTI-MASTER WITH WRITE COORDINATION:
     All writes for a record routed to the same primary node.
     Routing: consistent hashing by record ID → always same node.
     "Active-Active" in traffic terms but writes are actually serialised per record.
     CockroachDB, YugabyteDB: distributed SQL with Raft consensus per range.
     MySQL Group Replication: certify writes across all nodes before committing.
  
  5. SHARED STORAGE (easiest):
     All nodes write to same distributed storage.
     Aurora Multi-Master: multiple writer nodes, single storage layer.
     Storage layer: serialises conflicting writes.
     DB nodes: compute layer only (stateless from storage perspective).
     No conflict: storage layer handles write ordering.

ACTIVE-ACTIVE ACROSS REGIONS:
  Primary use case: latency reduction + availability
  
  Users in US → us-east-1 cluster (low latency)
  Users in EU → eu-west-1 cluster (low latency)
  
  Data consistency: each region may serve slightly stale data
  (asynchronous replication between regions, ~100ms lag)
  
  Pattern: Route writes to user's home region.
           Route reads to nearest region (may be slightly stale).
           Global DB: DynamoDB Global Tables (replication across 5 regions).
  
  Amazon DynamoDB Global Tables:
    Multi-region Active-Active
    Last Write Wins conflict resolution (timestamp-based)
    Replication lag: typically < 1 second
    Use: globally distributed applications tolerating eventual consistency
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Active-Active (Active-Passive only):
- Half capacity sits idle (standby server)
- Failover time: 30-90 seconds (promotion + DNS change) → users see outage
- Uneven geographic load: some regions serve more users than others

WITH Active-Active:
→ 100% utilisation: all nodes serve live traffic (no idle capacity)
→ Zero-failover: node failure absorbed instantly by remaining nodes
→ Geographic affinity: serve users from nearest region for low latency

---

### 🧠 Mental Model / Analogy

> A restaurant with two kitchens, both cooking at full capacity during service. If Kitchen A has a fire and shuts down, Kitchen B continues serving all orders — possibly slower (higher load), but no restaurant closure. Compare to having one kitchen active and one closed (Active-Passive): fire in Kitchen A → diners wait while Kitchen B fires up ovens, preheats, and gets ready (the "failover delay"). Active-Active trades the simplicity of a single kitchen for the resilience of two busy ones.

"Two kitchens both cooking" = both nodes actively serving traffic
"Kitchen fire" = node failure
"Restaurant stays open (Kitchen B absorbs)" = no failover, just capacity reduction
"Closed kitchen warming up" = Active-Passive standby promotion time

---

### ⚙️ How It Works (Mechanism)

**Multi-region Active-Active with AWS Global Accelerator:**

```
ARCHITECTURE:
  us-east-1: App cluster + Aurora Primary
  eu-west-1: App cluster + Aurora Read Replica (promoted to writer on failover)
  
  AWS Global Accelerator: anycast routing → nearest healthy region
  
  Traffic flow:
    User in New York → Global Accelerator → us-east-1 (nearest) → App → DB
    User in London → Global Accelerator → eu-west-1 (nearest) → App → Aurora
    
    If us-east-1 fails (unhealthy health check):
    User in New York → Global Accelerator → reroutes to eu-west-1
    Wait time: ~30 seconds (health check detection + routing update)
    Note: this is close to Active-Active but still has a brief RTO
    
    True Active-Active for DB: Aurora Global Database
    Both regions: write capability (multi-master mode)
    Replication: storage level, ~100ms lag

KUBERNETES MULTI-CLUSTER ACTIVE-ACTIVE:
  Two clusters: cluster-a (us-east-1), cluster-b (eu-west-1)
  Istio + Kiali: cross-cluster service mesh
  DNS: weighted routing (50/50) → both clusters serve traffic
  
  Any pod in either cluster can receive requests.
  Cross-cluster: pod in cluster-a can call pod in cluster-b transparently.
  Shared state: centralised database or DynamoDB Global Tables.
  
  Failure: cluster-b network outage → mesh detects → routes all to cluster-a
  Recovery: cluster-b recovers → mesh rebalances to 50/50
```

---

### 🔄 How It Connects (Mini-Map)

```
Redundancy / Failover
(the general concept)
        │
        ├── Active-Passive (one active, one idle standby)
        │   + Simple, no conflict resolution
        │   + Switchover time: 30-90 seconds
        │
        └── Active-Active ◄──── (you are here)
            (all nodes active simultaneously)
            + Zero-failover time
            + Better capacity utilisation
            + Complex for stateful services
                    │
                    ├── Geo-Replication
                    └── Multi-Region Architecture
```

---

### 💻 Code Example

**Spring Boot: multi-region read preference (nearest region):**

```java
// DynamoDB Global Tables: read from local region, write to local region
@Configuration
public class DynamoConfig {
    @Bean
    public DynamoDbClient dynamoDbClient() {
        // Read from current region (low latency)
        // Writes: DynamoDB Global Tables replicate to all regions automatically
        return DynamoDbClient.builder()
            .region(Region.of(System.getenv("AWS_REGION")))  // set per region
            .build();
    }
}

@Service
public class UserService {
    // Write: goes to local region → Global Tables replicates to all regions
    // Read: local region → possibly stale by < 1 second (eventual consistency)
    // Accept this: 1-second stale user profile is acceptable for most use cases
    
    public void updateUserPreference(String userId, Map<String, String> prefs) {
        // This write is committed locally, then replicated globally
        // LWW conflict resolution: if two regions update simultaneously,
        // the later timestamp wins (DynamoDB Global Tables default)
        dynamoDb.updateItem(UpdateItemRequest.builder()
            .tableName("users")
            .key(Map.of("userId", AttributeValue.fromS(userId)))
            .updateExpression("SET preferences = :prefs, updatedAt = :ts")
            .expressionAttributeValues(Map.of(
                ":prefs", AttributeValue.fromM(toAttributeMap(prefs)),
                ":ts", AttributeValue.fromN(String.valueOf(System.currentTimeMillis()))
            ))
            .build());
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Active-Active means no data loss on failure | Active-Active for stateless services: no data loss (no state). Active-Active for databases with async replication: replication lag means very recent writes to failed node may not have replicated. RPO is near-zero (milliseconds), not guaranteed zero |
| Active-Active is always better than Active-Passive | Active-Active is more complex and costly to implement correctly for stateful services. For databases, conflict resolution is difficult. For small organisations or non-critical services, Active-Passive is simpler and sufficient. Use Active-Active when the complexity cost is justified by the availability requirement |
| Multi-region Active-Active provides consistent low latency everywhere | Users are routed to nearest region (low read latency). But writes that require cross-region coordination (synchronous commit) have latency proportional to inter-region RTT (100-200ms). For most use cases, writes go to the nearest region's DB (no cross-region wait), but users near no region still experience higher latency |
| Active-Active databases eliminate the need for conflict resolution | Any Active-Active write-accepting database must handle conflicts. Even "serialisable" distributed databases (CockroachDB, Spanner) use distributed consensus (Raft/Paxos) that serialises conflicting writes — but this serialisation has a performance cost and cross-region latency for geographically distributed writes |

---

### 🔥 Pitfalls in Production

**Active-Active with stale reads causing double processing:**

```
PROBLEM: e-commerce order processing with DynamoDB Global Tables (LWW)

  User places order in us-east-1 at T=0.
  Order record written: { orderId: "123", status: "pending", region: "us-east-1" }
  
  Replication to eu-west-1: ~500ms delay.
  
  At T=200ms: user refreshes page; request goes to eu-west-1 (round-robin LB).
  eu-west-1: order "123" not yet replicated → "order not found" → 404!
  
  User: clicks "place order" again → second order "124" created.
  At T=600ms: both "123" and "124" exist → user charged twice.
  
  ROOT CAUSE: Read-your-writes consistency not guaranteed across regions.
  Active-Active + async replication = eventual consistency = stale reads possible.

SOLUTIONS:

  1. READ-YOUR-WRITES (Session consistency):
     After write in region A: redirect subsequent reads to region A
     (for the duration of the session or until replication confirmed).
     
     AWS Global Accelerator: route user to same region for duration of session.
     Cookie: X-Write-Region: us-east-1 → force reads to us-east-1 for 2 seconds.
     
  2. CONDITIONAL WRITES (Optimistic concurrency):
     DynamoDB condition expressions:
       // Only create order if orderId does NOT already exist:
       ConditionExpression: attribute_not_exists(orderId)
       // Second "place order" click: orderId "123" exists → ConditionalCheckFailed
       // Returns 400, not 200 → idempotent order creation
     
  3. IDEMPOTENCY KEY:
     Client generates idempotency key (UUID) per order attempt.
     Server: deduplicate on idempotency key (even across regions).
     DynamoDB conditional write on idempotency key ensures exactly-once creation.
  
  4. SINGLE-REGION WRITE PATH (Active-Active reads, Active-Passive writes):
     All writes: routed to us-east-1 (single write primary)
     All reads: served from nearest region (read replicas)
     Not "true" Active-Active for writes — but simpler and consistent.
```

---

### 🔗 Related Keywords

- `Active-Passive` — the simpler alternative; one active, one standby
- `Redundancy / Failover` — the parent concept; Active-Active is an implementation
- `Geo-Replication` — often used to implement multi-region Active-Active
- `Multi-Region Architecture` — Active-Active is the highest tier of multi-region HA
- `Consistent Hashing (Load Balancing)` — used to route to correct node in Active-Active clusters

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ All nodes serve live traffic simultaneously│
│              │ — node failure absorbed, no switchover    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Zero-tolerance for failover delay; global │
│              │ low-latency; maximum utilisation needed   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Strong consistency required for DB writes;│
│              │ small team lacking operational expertise  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Two kitchens both cooking full-time —    │
│              │  one fire, the other keeps the restaurant │
│              │  open without missing a beat."            │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Active-Passive → Geo-Replication          │
│              │ → Multi-Region Architecture               │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Netflix uses Active-Active across multiple AWS regions. A user starts watching a movie in London (served by eu-west-1). Midway through, eu-west-1 has a partial outage — Global Accelerator reroutes the user to us-east-1. The user's streaming position (watched 47 minutes) was stored in eu-west-1's session store with 200ms replication lag. What happens to the user's experience? Design a playback position sync strategy that survives regional failover with at most 5 seconds of "forgotten" position, without requiring synchronous cross-region writes.

**Q2.** You're designing an Active-Active database for a distributed inventory system: 3 warehouses in 3 different countries, each with local writes. Two warehouses simultaneously sell the last unit of a product: Warehouse A: inventory=1, places sale → inventory=0. Warehouse B (at same moment): inventory=1 (not yet replicated), places sale → inventory=0. Both transactions committed locally. Explain the inventory problem this creates, and design a solution using one of: (a) synchronous distributed locking, (b) saga pattern with compensation, (c) CRDT-based inventory counter. Evaluate trade-offs.
