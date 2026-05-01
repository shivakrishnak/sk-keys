---
layout: default
title: "Conflict Resolution Strategies"
parent: "Distributed Systems"
nav_order: 622
permalink: /distributed-systems/conflict-resolution-strategies/
number: "622"
category: Distributed Systems
difficulty: ★★★
depends_on: "Eventual Consistency, CRDT, Vector Clocks"
used_by: "Cassandra, DynamoDB, CouchDB, Riak, Git"
tags: #advanced, #distributed, #consistency, #replication, #conflict
---

# 622 — Conflict Resolution Strategies

`#advanced` `#distributed` `#consistency` `#replication` `#conflict`

⚡ TL;DR — When replicas diverge in an eventually consistent system, **conflict resolution** determines which version wins or how to merge them: LWW (last write wins), client-side merge, semantic merge, or CRDT-based conflict-free merging.

| #622            | Category: Distributed Systems             | Difficulty: ★★★ |
| :-------------- | :---------------------------------------- | :-------------- |
| **Depends on:** | Eventual Consistency, CRDT, Vector Clocks |                 |
| **Used by:**    | Cassandra, DynamoDB, CouchDB, Riak, Git   |                 |

---

### 📘 Textbook Definition

**Conflict resolution** in distributed systems addresses what happens when concurrent writes to the same data item on different replicas produce divergent values that must be reconciled during anti-entropy or read repair. A **conflict** arises when two replicas have different values for the same key, and vector clocks (or timestamps) indicate the writes are concurrent (neither happened before the other). Resolution strategies: (1) **Last Write Wins (LWW)** — compare timestamps; highest timestamp wins. Simple, but silently discards one update. (2) **Multi-Value** (Riak DVV, CouchDB) — return all conflicting versions ("siblings") to the client; client resolves. (3) **Application-level merge** — system detects conflict; application code determines the merged value. (4) **CRDT** — data structure designed so concurrent updates always merge without conflicts. (5) **Operational Transformation (OT)** — transform conflicting operations relative to each other (collaborative text editing). (6) **Custom semantic merge** — domain-specific logic (e.g., union of concurrent set additions). The right strategy depends on: whether lost updates are acceptable, whether merging is semantically meaningful, and operational complexity tolerance.

---

### 🟢 Simple Definition (Easy)

You and a colleague edit the same document simultaneously offline. Two versions exist. Who wins? Options: (1) Last saved wins (LWW) — simple, but your colleague's work is lost. (2) Show both versions and ask you to merge (multi-value) — correct but requires human decision. (3) Smart merge (CRDT/semantic) — automatically combine both changes. (4) Git-style merge — auto-merge where possible, flag conflicts for human resolution. The right choice depends on: can we afford to lose data? Can we merge automatically? How important is the data?

---

### 🔵 Simple Definition (Elaborated)

Cassandra: default is LWW (timestamp-based). For a user's last login timestamp: LWW is fine (we want the most recent). For a shopping cart: LWW is terrible (silently drops items). DynamoDB with DynamoDB Streams + custom resolver: detect conflicts, merge using application logic. The fundamental challenge: the system can't know the business semantics of conflicting updates. A shopping cart addition + shopping cart addition should both survive. A user profile update + user profile update: one should win. The strategy must match the data's business semantics.

---

### 🔩 First Principles Explanation

**Vector clock-based conflict detection, LWW, multi-value, and semantic merge:**

```
CONFLICT DETECTION WITH VECTOR CLOCKS:

  Vector clock: [A:2, B:1] means "I've seen 2 events from A, 1 from B."

  HAPPENED-BEFORE:
    V1 = [A:2, B:1] happened-before V2 = [A:3, B:2] if: all V1[i] <= V2[i].
    V2: supersedes V1. No conflict. Use V2.

  CONCURRENT (CONFLICT):
    V1 = [A:3, B:1]: A wrote 3 times, B wrote once.
    V2 = [A:2, B:2]: A wrote twice, B wrote twice.
    V1[A]=3 > V2[A]=2 but V1[B]=1 < V2[B]=2.
    Neither is dominated. CONCURRENT writes. CONFLICT.

  CONFLICT RESOLUTION needed: V1 and V2 are concurrent, different values for same key.

STRATEGY 1: LAST WRITE WINS (LWW)

  Compare timestamps. Highest timestamp wins.

  V1: value="John Smith", timestamp=10:00:00.123
  V2: value="Jonathan Smith", timestamp=10:00:00.456

  LWW: V2 wins. "Jonathan Smith" is the stored value.
  V1: silently discarded.

  IMPLEMENTATION (Cassandra):
    Each cell has a timestamp. On write: timestamp = microtime at coordinator.
    On conflict: max timestamp wins.

  PROS:
    Extremely simple. No application code needed. O(1) resolution.

  CONS:
    Silent data loss. V1's changes: gone forever.
    Clock skew: two writes microseconds apart → wrong winner due to clock skew.
    Not monotone: can cause "time travel" (newer write with old clock beats newer actual write).

  WHEN TO USE:
    Data where last value is the only relevant value: last-login-time, session token.
    Data with natural total order: configuration values (last config is current config).
    Data where loss of concurrent writes is acceptable: analytics approximate counts.

  WHEN NOT TO USE:
    Additive operations (counters, sets) → use CRDT.
    High-value data where loss is unacceptable → use multi-value or quorum writes.

STRATEGY 2: MULTI-VALUE (SIBLINGS — RIAK, COUCHDB)

  System: stores ALL conflicting versions.
  Client: reads ALL siblings. Application code: resolves.

  RIAK (Dotted Version Vectors):
    Write A: {cart: ["shoes"], dvv: [A:1]}
    Concurrent write B: {cart: ["shoes", "hat"], dvv: [B:1]}
    No causal relationship between A and B → siblings.

    GET request: returns BOTH siblings:
      Sibling 1: {cart: ["shoes"], dvv: [A:1]}
      Sibling 2: {cart: ["shoes", "hat"], dvv: [B:1]}

    Client (application code): merge = union of both carts = ["shoes", "hat"].
    PUT merged value with new DVV: {cart: ["shoes", "hat"], dvv: [A:1, B:1, C:2]}

  PROS:
    No silent data loss. Client sees all versions. Custom merge logic.

  CONS:
    Application complexity. Read returns multiple values → must always handle siblings.
    If clients don't resolve: siblings accumulate indefinitely (Riak "sibling explosion").

  COUCHDB:
    Conflict detection via revision IDs (_rev).
    API: returns all conflicting revisions.
    Client: choose winner + DELETE losers.

STRATEGY 3: APPLICATION-LEVEL MERGE

  System: detects concurrent writes (via vector clocks or version numbers).
  System: calls application merge callback.
  Application: knows business semantics → correct merge.

  EXAMPLE (shopping cart):
    Concurrent writes: both add different items.
    Merge function: union(set1, set2). Both items preserved.

    Concurrent writes: one sets quantity=3, other sets quantity=5.
    Merge function: max(q1, q2) = 5. Take larger quantity.
    (Business rule: don't reduce quantity via merge. Customer should see max.)

  DynamoDB with Lambda:
    DynamoDB Streams: captures every write event.
    Lambda: triggered on conflict (detects divergence between replicas).
    Lambda: implements custom merge logic.
    Writes merged value back to DynamoDB.

  Amazon Shopping Cart (historical):
    Used exactly this: never throw away a customer's cart item.
    Merge = union of all concurrent cart versions.
    "Add bias": in case of conflict, prefer the state that has MORE items.
    Rationale: it's better to have an extra item than to lose one.
    Customer: can always remove unwanted items. Can't recover lost items.

STRATEGY 4: SEMANTIC MERGE (OPERATION-BASED)

  Instead of merging STATE (what the value is), merge OPERATIONS (what changed).

  EXAMPLE: bank account balance.
    State V1: balance = $100 (after deposit +$50)
    State V2: balance = $80 (after withdrawal -$20)
    Both started from balance = $50.

    LWW: pick one ($100 or $80). Wrong: lost either the deposit or the withdrawal.

    Operation merge:
      Op A: deposit +$50
      Op B: withdrawal -$20
      Apply both: $50 + $50 - $20 = $80. Correct.

  REQUIRES: storing operations (event sourcing) not just final state.
  Commutative operations: can be applied in any order.
  Non-commutative: need causal ordering (vector clocks to order A and B relative to each other).

STRATEGY 5: CUSTOM SEMANTIC RULES PER DATA TYPE

  Different fields within one document → different resolution strategies.

  User profile example:
    Field: last_login (timestamp) → LWW (most recent login time).
    Field: cart_items (set) → CRDT OR-Set (preserve concurrent additions).
    Field: display_name (string) → multi-value (require explicit user resolution).
    Field: email_preferences (flags) → bitwise OR (preserve any concurrent opt-in).

  Implementation: per-field resolver registry.
  Some databases: support custom compare-and-set functions per column.

CONFLICT RATE MONITORING:

  In production: measure how often conflicts occur.
  High conflict rate: indicator of:
    - Hot keys (many writers on same data)
    - Clock skew (timestamps unreliable → LWW picks wrong winner)
    - Long network partitions (more time for divergence)

  Metrics: conflicts_detected/sec, siblings_per_key (Riak), resolution_latency.
  Alert: conflict rate > baseline → investigate hot keys or replica lag.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT conflict resolution strategy:

- Concurrent writes to eventually-consistent replicas silently overwrite each other
- Data loss without warning
- No way to detect when divergence occurred

WITH explicit conflict resolution:
→ Predictable behavior when concurrent writes occur
→ Appropriate strategy per data semantics (LWW for timestamps, union for sets)
→ Application-level control when system can't know business rules

---

### 🧠 Mental Model / Analogy

> Two doctors update the same patient record simultaneously. Conflict resolution options: (1) Whichever doctor saved last wins (LWW) — dangerous: may lose critical lab results. (2) Show both records to a third doctor for manual merge (multi-value) — safe but slow. (3) Merge automatically: take highest medication dose (max), union of all diagnoses (set union) — smart merge per field. (4) Use immutable event log: all changes preserved as events; current state = replay (event sourcing/semantic merge). In healthcare: multi-value or semantic merge is required — LWW too dangerous.

"Doctor saving their version" = replica receiving a write
"Conflict" = two concurrent saves to same patient record
"Show both to third doctor" = multi-value / sibling approach
"Smart merge per field" = application-level semantic merge

---

### ⚙️ How It Works (Mechanism)

```
CONFLICT DETECTION AND RESOLUTION PIPELINE:

  Write arrives at replica A with vector clock V1.
  Replica A: current value has vector clock V_current.

  V1 happens-after V_current: no conflict. Overwrite.
  V_current happens-after V1: no conflict. Discard (stale write).
  V1 and V_current are concurrent: CONFLICT.

  Resolution:
    LWW: compare timestamps. Winner = max timestamp.
    Multi-value: store both. Return siblings to reader.
    Custom merge: call registered merge function.
    CRDT: merge function is part of the data type definition.
```

---

### 🔄 How It Connects (Mini-Map)

```
Eventual Consistency (replicas diverge and must converge)
        │
        ▼ (how to converge when values conflict)
Conflict Resolution Strategies ◄──── (you are here)
(LWW / multi-value / semantic merge / CRDT — match to data semantics)
        │
        ├── Vector Clocks: detect whether writes are concurrent or causal
        ├── CRDT: eliminates conflict by design (subset of conflict resolution)
        └── Anti-Entropy: the process that discovers and resolves divergence
```

---

### 💻 Code Example

```java
// Application-level conflict resolver for a shopping cart:
public class ShoppingCartConflictResolver {

    // DynamoDB conditional write + conflict resolution via Streams:
    public Cart resolve(List<Cart> conflictingVersions) {
        // Semantic rule: "add bias" — never lose a cart item.
        // Union of all items across all conflicting versions.

        Set<CartItem> mergedItems = conflictingVersions.stream()
            .flatMap(c -> c.getItems().stream())
            .collect(Collectors.toSet()); // Set: deduplicates same items.

        // For quantities: take max across conflicting versions.
        Map<String, Integer> maxQuantities = new HashMap<>();
        for (Cart cart : conflictingVersions) {
            for (CartItem item : cart.getItems()) {
                maxQuantities.merge(item.getProductId(), item.getQuantity(), Math::max);
            }
        }

        // Build merged cart:
        Cart merged = new Cart();
        for (CartItem item : mergedItems) {
            merged.addItem(item.withQuantity(maxQuantities.get(item.getProductId())));
        }

        // Log resolution for audit:
        log.info("Resolved conflict: {} versions → {} items",
            conflictingVersions.size(), merged.getItems().size());

        return merged;
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                                              | Reality                                                                                                                                                                                                                                                                                                                                                                               |
| -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| LWW (last write wins) is safe for most use cases                           | LWW is only safe when: (1) concurrent writes are extremely rare, or (2) losing one of two concurrent writes is acceptable for the specific data. For counters, sets, or any additive operation: LWW silently loses updates. Cassandra's LWW default: fine for configuration data, dangerous for user-facing data with concurrent writes                                               |
| Conflict resolution only matters during network partitions                 | Conflicts can occur even without network partitions when you have multi-leader or leaderless replication. Any time two replicas accept concurrent writes to the same key (even within a healthy network), a conflict can arise. Replication lag: Replica A serves a write at t=10ms, replica B serves a different write at t=11ms for the same key before replicating the first write |
| Multi-value (siblings) is always better than LWW because it preserves data | Multi-value requires application code to resolve siblings — if not handled, siblings accumulate indefinitely ("sibling explosion" in Riak). Every read must handle multiple values. If the application doesn't merge and write back, the conflict is never resolved. More correct semantics, but requires ongoing engineering discipline                                              |

---

### 🔥 Pitfalls in Production

**Clock skew causes LWW to pick the wrong winner:**

```
SCENARIO: Two Cassandra nodes (Node A, Node B). Network partition for 1 second.

  t=10:00:00.100 — Client 1 writes to Node A: user.email = "alice@old.com", timestamp=100ms
  t=10:00:00.150 — Client 2 writes to Node B: user.email = "alice@new.com", timestamp=150ms

  Expected: "alice@new.com" wins (written later, timestamp=150).

  BUT: Node A's clock is 200ms AHEAD of Node B's clock (NTP not synchronized).

  From Node A's perspective:
    Its own write: timestamp = 10:00:00.100 (actual wall clock of Node A, which is 200ms ahead)
    = adjusted: 10:00:00.300 (in global time)
  From Node B's perspective:
    Its write: timestamp = 10:00:00.150 (actual wall clock of Node B)
    = adjusted: 10:00:00.150 (in global time)

  Cassandra uses local timestamps (not coordinated).
  LWW: Node A's timestamp (10:00:00.100 local ≈ 10:00:00.300 global) > Node B's (10:00:00.150 global).
  Result: "alice@old.com" wins despite being written BEFORE "alice@new.com" in real time.
  User: updated their email, but Cassandra kept the old one. Data regression.

BAD: Using Cassandra with LWW and unsynchronized clocks for critical data:
  UPDATE users SET email = 'alice@new.com' WHERE id = 123;
  -- No conditional write (no optimistic locking). Just LWW.
  -- Clock skew: wrong winner.

FIX 1: Synchronize clocks (reduce skew):
  Use NTP or PTP (Precision Time Protocol). Target: < 1ms skew.
  AWS: EC2 instances use Chrony. Target: sub-millisecond NTP sync.
  Reduces but doesn't eliminate clock skew.

FIX 2: Use Cassandra Lightweight Transactions (LWT):
  INSERT INTO users (id, email) VALUES (123, 'alice@new.com') IF NOT EXISTS;
  -- Or: UPDATE users SET email='alice@new.com' WHERE id=123 IF email='alice@old.com';
  -- Conditional write: uses Paxos (not LWW). Clock skew irrelevant.
  -- Higher latency (2 Paxos rounds). Use for critical writes only.

FIX 3: Use logical timestamps (client-generated version numbers):
  Client: manages explicit version number. Version = monotonically increasing.
  Write: includes version. Server: reject write if version < current.
  Not affected by clock skew.

MONITORING:
  Alert: NTP offset > 10ms on any Cassandra node → risk of LWW clock skew conflicts.
  Monitor: ntpstat, chronyc tracking.
```

---

### 🔗 Related Keywords

- `CRDT` — conflict-free data type: conflicts eliminated by data structure design
- `Vector Clocks` — detect concurrent writes (needed to know when conflict exists)
- `Anti-Entropy` — process for discovering and resolving replica divergence
- `Eventual Consistency` — the consistency model that requires conflict resolution
- `Read Repair` — one mechanism for resolving conflicts on read path

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Concurrent writes to same key → conflict.│
│              │ LWW: simple, loses data. Multi-value:    │
│              │ correct, needs app code. CRDT: no        │
│              │ conflict. Pick strategy per semantics.   │
├──────────────┼───────────────────────────────────────────┤
│ USE LWW WHEN │ Last value is the only value that matters│
│              │ (timestamps, session tokens, configs)    │
├──────────────┼───────────────────────────────────────────┤
│ USE MULTI-VALUE│ High-value data; cannot lose any write; │
│              │ application can merge meaningfully       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Two doctors updated same record: who   │
│              │  wins? Depends on the data — match the  │
│              │  strategy to the business semantics."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ CRDT → Vector Clocks → Anti-Entropy →   │
│              │ Read Repair → Cassandra LWT              │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Cassandra uses LWW by default. You're storing product inventory counts (how many units are in stock). A warehouse management system and an e-commerce order processing system both update the same SKU's inventory simultaneously. What problem occurs with LWW? How does it manifest in production? Design the correct solution — what consistency strategy matches inventory count semantics?

**Q2.** CouchDB uses multi-value conflict resolution: it stores all conflicting revisions and the client must pick a winner. A document has 50 unresolved conflicts (siblings) accumulated over 3 days because the resolving client was down. What is the performance impact on every read for that document? Write the CouchDB query and update strategy to detect, resolve, and prevent future conflict accumulation.
