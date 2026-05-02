---
layout: default
title: "BASE"
parent: "Distributed Systems"
nav_order: 579
permalink: /distributed-systems/base/
number: "0579"
category: Distributed Systems
difficulty: ★★☆
depends_on: Eventual Consistency, CAP Theorem, Replication Strategies
used_by: NoSQL Databases, Large-Scale Web Applications, Microservices
related: ACID, Eventual Consistency, CAP Theorem, CRDTs
tags:
  - base
  - eventual-consistency
  - nosql
  - distributed-systems
  - intermediate
---

# 579 — BASE

⚡ TL;DR — BASE (Basically Available, Soft State, Eventually Consistent) is the design philosophy of AP distributed systems, contrasting with ACID. It accepts that data may be temporarily inconsistent and focuses on high availability and performance. "Basically Available" means the system responds even during failures; "Soft State" means data validity can expire and may change over time; "Eventually Consistent" means replicas will converge when writes stop.

| #579 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Eventual Consistency, CAP Theorem, Replication Strategies | |
| **Used by:** | NoSQL Databases, Large-Scale Web Applications, Microservices | |
| **Related:** | ACID, Eventual Consistency, CAP Theorem, CRDTs | |

### 🔥 The Problem This Solves

**WORLD WHERE EVERYTHING MUST BE ACID:**
An e-commerce platform serves 10M concurrent users globally. Every shopping cart action requires a globally consistent transaction across 50 database replicas. Each add-to-cart requires acquiring distributed locks, waiting for all replicas to confirm, and blocking while any replica is slow or unreachable. At peak load: timeouts, queue buildup, cascading failures. During a datacenter outage: entire cart system unavailable.

The real-world question Amazon faced (Werner Vogels, 2007): "Can users add items to their cart even when one of our databases is unavailable?" ACID says no. BASE says: let the add-to-cart succeed locally, mark the cart state as "soft" (might merge with updates from other regions), and converge the final cart state eventually. The shopping cart may briefly show slightly different state in different regions, but it is ALWAYS available and always accepts writes. BASE is the principled acknowledgment that perfect consistency can be sacrificed for availability at scale.

---

### 📘 Textbook Definition

**BASE** is an acronym describing the properties of AP (Available + Partition-tolerant) distributed systems, proposed by Eric Brewer (the author of the CAP theorem) and elaborated by Dan Pritchett (Amazon) in 2008:

- **Basically Available:** The system guarantees availability (responses to every request), possibly at the cost of consistency. It responds even during partial failures — some data may be stale or unavailable, but the system itself is up.

- **Soft State:** The system state may change over time even without input — due to eventual consistency propagation, TTL expiration, background reconciliation. There is no guarantee the state is "durable" at any given instant without explicit confirmation.

- **Eventually Consistent:** Once all inputs stop, all replicas will eventually converge to the same state. During active propagation, replicas may diverge briefly.

BASE contrasts with ACID (Atomicity, Consistency, Isolation, Durability) — the properties of traditional relational database transactions. Systems choosing BASE sacrifice Isolation (operations may interleave) and immediate Consistency (reads may be stale) in favor of availability and performance.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
BASE = it's okay to be temporarily inconsistent, as long as the system stays available and data eventually converges.

**One analogy:**
> BASE is like a news website with cached content. When a breaking story is published, the homepage might show the old headlines for a few seconds while CDN caches refresh. The website is BASICALLY AVAILABLE (never goes down, always returns a page). The state is SOFT (it might change in 30 seconds without you doing anything). It will EVENTUALLY be CONSISTENT (within 30 seconds, all CDN nodes show the new headline).
> ACID would require the homepage to be unavailable until all CDN nodes have the new headline simultaneously — unacceptable for a news site serving 50M readers.

---

### 🔩 First Principles Explanation

```
BASE — THREE PROPERTIES IN DETAIL:

BASICALLY AVAILABLE:
  System responds to requests even when:
  - Some replicas are unavailable (failed/partitioned)
  - The response might return stale data
  - Some writes might not immediately propagate
  
  Implementation:
  - Route requests to any available replica (not required to be primary)
  - Accept writes even when not all replicas are reachable
  - Return partial results rather than errors
  - Use fallback/degraded responses instead of complete failures
  
  Example: DynamoDB returns responses even when 1 of 3 replicas is down
           (consistency may be temporarily reduced, but availability is maintained)

SOFT STATE:
  Data validity is not permanent without continuous reinforcement.
  - Data has TTLs (cache entries expire)
  - Replicas may hold different values for an interval
  - "Current" state is the best guess at a point in time, not a formal guarantee
  - Application must tolerate that "what I saw 50ms ago might have changed"
  
  Examples:
  - Redis cache entries (TTL: state "expires" without renewal)
  - Cassandra replica with pending sync (stale until anti-entropy repairs it)
  - Session data expiring after inactivity timeout

EVENTUALLY CONSISTENT:
  Given no new updates, all accessible copies of the data will converge.
  Time-bounded in practice (milliseconds to seconds for typical intra-DC scenarios).
  Conflict resolution required when concurrent writes create divergence.
  
  Mechanisms that enforce convergence:
  - Gossip protocol (nodes exchange state, detect and fill gaps)
  - Read repair (coordinator detects inconsistency during multi-replica read, fixes it)
  - Hinted handoff (writes for down nodes are buffered and delivered on recovery)
  - Anti-entropy (Merkle tree-based background sync finds divergent ranges)
```

---

### 🧪 Thought Experiment

**SCENARIO:** Flight seat reservation during a load spike (Super Bowl week).

```
Option A: ACID flight booking
  Every seat select requires transaction across all booking system nodes
  During load spike: transactions queue, timeout after 30s
  Users see: "Unable to book at this time. Please try again."
  Revenue impact: $2M in abandoned bookings during 2-hour spike
  
Option B: BASE flight booking (hybrid)
  
  BASICALLY AVAILABLE:
  Show seat map as "probably available" (stale cache from 5s ago)
  Accept seat selection immediately, locally
  
  SOFT STATE:
  Seat availability shown is soft: it might change before ticket is issued
  "Selected" status held for 10 minutes (TTL) while payment completes
  
  EVENTUALLY CONSISTENT:
  After payment: confirmed booking propagates to all systems
  Duplicate bookings (if any, rare): resolved by overbooking compensation system
  
  Result: 0 user-visible failures during spike, 0.03% double-booking rate
         → airline's existing overbooking protocol handles the 0.03%
         → $0 in lost bookings vs $2M loss
  
  This is how Amadeus and Sabre work: optimistic booking with eventual reconciliation.
```

---

### 🧠 Mental Model / Analogy

> BASE is like a restaurant that takes orders for the day's special even when the kitchen doesn't yet know the exact ingredient count. "Basically, we have salmon today." Orders are accepted. If the salmon runs out mid-service (eventual reconciliation reveals oversold special), the restaurant offers a substitute or upgrade — a compensating transaction. The alternative (ACID restaurant): seal the kitchen, count every ingredient, then open for orders. Customers wait 30 minutes before placing orders. No one eats.
> 
> Technically: BASE systems accept the possibility of compensating actions (human or automated) to handle rare conflicts, because the cost of preventing conflicts (coordination, blocking) exceeds the cost of resolving them.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** BASE means your system will always be up and accepting requests (Basically Available), data might be outdated for a moment (Soft State), and it will catch up eventually (Eventually Consistent). This is the trade-off that lets systems like DynamoDB, Cassandra, and DNS scale to billions of requests without global locking.

**Level 2:** BASE is not a binary choice vs ACID. A single system can use ACID for critical operations (payment commits, stock deduction) and BASE for non-critical operations (profile views, recommendation scores, activity feeds). The art is identifying which operations can tolerate staleness (most reads on social media, catalog browsing, analytics) vs. which cannot (inventory purchases, financial deductions, identity changes).

**Level 3:** The "Soft State" property has a specific implication for stateful services: you cannot rely on previously observed state remaining valid. This drives design patterns like: (a) optimistic concurrency control (check version before relying on state); (b) idempotent operations (safe to replay if unsure if completed); (c) saga pattern (long-running transactions with compensating transactions for rollback in BASE systems); (d) event sourcing (state is derived from immutable event log, not mutable shared state). Each of these is an architectural response to Soft State.

**Level 4:** The academic and practical evolution: Eric Brewer introduced BASE as a contrast to ACID in 1999 (same year as CAP hypothesis). Dan Pritchett formalized it in the 2008 QCon talk "BASE: An Acid Alternative." The Dynamo paper (2007) is the practical architecture for a BASE system. The debate "ACID vs BASE" is increasingly resolved in practice by Hybrid Transaction/Analytical Processing (HTAP) databases and NewSQL databases (CockroachDB, Spanner) which deliver ACID semantics on distributed systems — partly obsoleting the ACID vs BASE binary. Pure BASE systems remain optimal for highest-scale scenarios (billions req/s), but most applications can now have ACID at scale if they choose NewSQL.

---

### ⚙️ How It Works (Mechanism)

```
CASSANDRA — BASE ARCHITECTURE IN ACTION:

  BASICALLY AVAILABLE:
  ┌─────────────────────────────────────────┐
  │ Node A (primary) │ Node B │ Node C     │
  │    ✅ UP          │  ❌ DOWN│  ✅ UP     │
  └─────────────────────────────────────────┘
  
  Write with CL=ONE: reaches Node A → ACK → success
  (Node B is down, but write is accepted — basically available)
  
  Hinted Handoff: Node A stores a "hint" for Node B
  When Node B recovers: hint is delivered → Node B gets the write ✓
  
  SOFT STATE:
  Read from Node C with CL=ONE:
  Node C hasn't received the write yet (was routed from Node A → B → C in propagation)
  Read returns OLD value (soft state — valid for this 50ms window)
  
  EVENTUAL CONSISTENCY:
  Mechanisms running in background:
  1. Node A → Node C: async replication delivers write (50ms)
  2. Anti-entropy: Merkle tree comparison finds Node C missing write → syncs it
  3. Read repair: next CL=ALL read compares Node A and Node C → fixes Node C
  
  After 50-200ms: ALL nodes consistent. Soft state → hard state.

  SUMMARY:
  Write succeeded (BA) even with Node B down
  Read returned stale data briefly (S)
  All nodes converge within 200ms (EC)
  This is BASE in operation.
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
AMAZON SHOPPING CART — BASE DESIGN:

  Customer adds "Kindle" to cart from mobile app (EU datacenter):
  
  1. BASICALLY AVAILABLE:
     Write accepted by EU coordinator node immediately
     EU coordinator → returns success to mobile app in 50ms
     No wait for US or AP replication
  
  2. SOFT STATE:
     Cart state in EU: [Kindle]
     Cart state in US: [] (hasn't propagated yet)
     If customer switches to desktop in US within 200ms: cart shows empty (soft state)
     
  3. EVENTUALLY CONSISTENT:
     EU → US replication: 120ms
     US cart now: [Kindle] ✓
     
  4. CONFLICT SCENARIO (concurrent addition from two devices):
     Mobile (EU): add Kindle [cart: Kindle]
     Laptop (US): add iPad concurrently [cart: iPad]
     Network partition for 2s
     After partition heals: two cart versions: {EU: [Kindle]}, {US: [iPad]}
     
  5. CONFLICT RESOLUTION:
     Amazon's policy: merge > discard (losing cart items is worse than showing both)
     Final cart: [Kindle, iPad] — both preserved via set union CRDT
     
  This is the real Amazon Dynamo shopping cart design from the 2007 paper.
```

---

### 💻 Code Example

```java
// Spring Boot + DynamoDB: BASE-compliant shopping cart service
@Service
public class ShoppingCartService {

    private final DynamoDbClient dynamoDb;
    private static final String TABLE = "shopping_carts";

    // BASICALLY AVAILABLE: write succeeds even if some DynamoDB replicas are down
    // Uses eventual consistency (default) for maximum availability
    public void addItem(String userId, CartItem item) {
        // DynamoDB writes go to primary, then replicate asynchronously (BASE)
        UpdateItemRequest request = UpdateItemRequest.builder()
            .tableName(TABLE)
            .key(Map.of("userId", AttributeValue.fromS(userId)))
            .updateExpression("SET #items = list_append(if_not_exists(#items, :empty), :newItem)")
            .expressionAttributeNames(Map.of("#items", "items"))
            .expressionAttributeValues(Map.of(
                ":newItem", AttributeValue.fromL(List.of(toAttributeValue(item))),
                ":empty", AttributeValue.fromL(Collections.emptyList())
            ))
            // No condition expression — optimistic, always accepts (Basically Available)
            .build();

        dynamoDb.updateItem(request);
        // Returns immediately; replication is async (Soft State, Eventually Consistent)
    }

    // SOFT STATE: reads may return stale data (ms window after concurrent writes)
    public Cart getCart(String userId) {
        GetItemRequest request = GetItemRequest.builder()
            .tableName(TABLE)
            .key(Map.of("userId", AttributeValue.fromS(userId)))
            .consistentRead(false) // Eventually consistent read (fast, may be ms stale)
            .build();

        Map<String, AttributeValue> item = dynamoDb.getItem(request).item();
        return item.isEmpty() ? Cart.empty(userId) : toCart(item);
    }

    // EVENTUALLY CONSISTENT: for checkout, upgrade to strongly consistent read
    // to ensure we process the final, converged cart state
    public Cart getCartForCheckout(String userId) {
        GetItemRequest request = GetItemRequest.builder()
            .tableName(TABLE)
            .key(Map.of("userId", AttributeValue.fromS(userId)))
            .consistentRead(true) // Strong read for checkout (EC-like)
            .build();
        Map<String, AttributeValue> item = dynamoDb.getItem(request).item();
        return item.isEmpty() ? Cart.empty(userId) : toCart(item);
    }
}
```

---

### ⚖️ Comparison Table

| Property | BASE | ACID |
|---|---|---|
| **Availability** | Always responds (BA) | May block/fail for consistency |
| **Consistency** | Eventual (temporarily stale OK) | Immediate, strong |
| **State** | Soft (can change without input) | Hard (durable, transactional) |
| **Failure response** | Degrade gracefully (stale reads) | Fail with error (maintain invariants) |
| **Performance** | High throughput, low latency | Lower throughput, higher latency |
| **Use cases** | Social feeds, carts, counters, DNS | Banking, inventory, medical records |
| **Conflict handling** | Application-level merge needed | Transaction rollback/retry |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| BASE = unsafe for production | Enormous production systems (AWS, Meta, Google) use BASE for most of their data. Safety depends on whether the workload can tolerate temporary staleness and conflict resolution |
| ACID and BASE are mutually exclusive | The same system can use ACID for some tables/operations and BASE for others. DynamoDB (BASE) offers strongly consistent reads. Cassandra (BASE by default) offers QUORUM (ACID-like) |
| BASE means "no data loss" risk is acceptable | BASE systems can lose data if designed incorrectly. The "eventual" convergence guarantee requires specific mechanisms (anti-entropy, hinted handoff). "Hope it syncs" is not a BASE strategy |

---

### 🚨 Failure Modes & Diagnosis

**Stale Cache (Soft State Never Refreshed)**

```
Symptom:
User's profile page shows old avatar (uploaded 30s ago) on every page load.
Cache never expires.

Root Cause:
TTL not set on cache entry (infinite TTL = soft state never refreshes)
Update path didn't invalidate cache

Diagnosis:
Redis: TTL user:profile:12345 → returns -1 (no expiry = PROBLEM)

Fix 1: Set TTL on all soft-state cache entries
  redis.set("user:profile:" + userId, json, Duration.ofSeconds(300));

Fix 2: Explicit cache invalidation on write
  @Service:
  public void updateAvatar(String userId, String avatarUrl) {
      userRepository.save(userId, avatarUrl);
      cacheService.evict("user:profile:" + userId);  // invalidate on write
  }
```

---

### 🔗 Related Keywords

- `Eventual Consistency` — the consistency model that BASE is built upon
- `ACID` — the contrasting transactional model (Atomicity, Consistency, Isolation, Durability)
- `CAP Theorem` — BASE systems are AP, ACID systems are CP
- `CRDTs` — data structures designed for conflict-free BASE merges
- `Saga Pattern` — long-running transaction pattern for BASE microservices

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ B — Basically    │ Always responds, even with stale data     │
│     Available    │ System up during partial failures         │
├──────────────────┼─────────────────────────────────────────┤
│ S — Soft State   │ Data may change without new input        │
│                  │ (TTL expiry, async replication catch-up) │
├──────────────────┼─────────────────────────────────────────┤
│ E — Eventually   │ All replicas converge given quiescence  │
│     Consistent   │ Time-bounded in practice (ms-seconds)   │
├──────────────────┼─────────────────────────────────────────┤
│ VS ACID          │ Sacrifices I (isolation) and immediate  │
│                  │ C for availability and performance      │
├──────────────────┼─────────────────────────────────────────┤
│ SYSTEMS          │ Cassandra, DynamoDB, Riak, Couchbase,   │
│                  │ Redis, Elasticsearch                    │
└──────────────────┴─────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** A social media platform uses a BASE-designed comment counter (vote count on posts) stored in Cassandra with eventual consistency. The counter stores post_id → vote_count. The team uses a simple read-modify-write pattern: read count, increment, write back. Under load, multiple concurrent incrementers cause "lost update" bugs (count ends up at 150 when 200 votes were cast — 50 votes lost due to concurrent reads of stale values). The team considers: (a) Cassandra's built-in counter type, (b) CRDTs (specifically a PN-Counter), (c) upgrading to QUORUM consistency. For each approach, explain the mechanism that prevents lost updates, the trade-off vs a simple counter, and why the BASE "Soft State" property can still hold after fixing the lost-update bug.
