---
layout: default
title: "CRDTs"
parent: "NoSQL & Distributed Databases"
grand_parent: "Technical Dictionary"
nav_order: 24
permalink: /nosql/crdts/
id: NDB-024
category: NoSQL & Distributed Databases
difficulty: ★★★
depends_on: Eventual Consistency in NoSQL, Multi-Master Replication, Distributed Systems
used_by: Distributed Systems, Collaborative Applications, Real-Time Systems
related: Eventual Consistency in NoSQL, Multi-Master Replication, Vector Clock
tags:
  - nosql
  - crdt
  - distributed-systems
  - deep-dive
---

# NDB-024 — CRDTs

⚡ TL;DR — CRDTs (Conflict-free Replicated Data Types) are data structures mathematically designed to merge concurrent updates from multiple replicas without conflicts, enabling strong eventual consistency — all replicas converge to the same value without coordination or manual conflict resolution.

| #458            | Category: NoSQL & Distributed Databases                                      | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | Eventual Consistency in NoSQL, Multi-Master Replication, Distributed Systems |                 |
| **Used by:**    | Distributed Systems, Collaborative Applications, Real-Time Systems           |                 |
| **Related:**    | Eventual Consistency in NoSQL, Multi-Master Replication, Vector Clock        |                 |

---

### 🔥 The Problem This Solves

**THE CONCURRENT UPDATE PROBLEM:**
Multi-master database. Node A and Node B both accept writes. User's shopping cart on Node A: `{laptop: 1}`. User opens cart on mobile, hitting Node B (not yet synced). Adds headphones: `{headphones: 1}`. Network reconnects. Merge: `{laptop: 1, headphones: 1}` or just the latest? Or conflict requiring human intervention?

**WITHOUT CRDTs:**
Last-write-wins silently drops one write. Conflict detection requires human or application resolution code. Vector clocks detect conflicts but don't resolve them.

**WITH CRDTs:**
Design the data structure so that merging any two versions always produces a deterministic, correct result. A set where "add wins over remove" always converges. A counter where each node tracks its own increments and the total is always the sum. No conflicts — by mathematical construction.

---

### 📘 Textbook Definition

**CRDTs (Conflict-free Replicated Data Types)** are data structures whose operations are designed to be commutative, associative, and idempotent — allowing any two replicas to merge in any order and always reach the same final state, without coordination or locking. There are two main types: **State-based CRDTs (CvRDTs)**: the entire state is periodically sent to replicas; merge uses a join operation (the least upper bound in a semilattice); **Operation-based CRDTs (CmRDTs)**: individual operations are sent to replicas; operations must be commutative. Common CRDT types: **G-Counter** (grow-only counter), **PN-Counter** (increment/decrement), **G-Set** (grow-only set), **OR-Set** (add/remove set where add-wins), **LWW-Register** (last-write-wins register with timestamps), **RGA** (Replicated Growable Array — collaborative text editing). Used in: **Riak** (database), **Redis Enterprise** (CRDT data types), **Figma** (collaborative design), **Apple Notes** (sync), **Amazon Shopping Cart**.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
CRDTs are data types that merge themselves — any two replicas can merge in any order and always reach the same correct result, without needing to ask "who wrote this last?"

**One analogy:**

> Google Docs. Two people edit the same document simultaneously. When they reconnect, both edits appear — neither is lost. The document "merges" both edits automatically. This isn't magic — it's because text is modeled as a CRDT (specifically a list CRDT): each character is uniquely identified, and inserting or deleting characters from two ends simultaneously always produces a deterministically merged result.

- "Two people editing simultaneously" → two replicas accepting concurrent writes
- "Both edits appear" → CRDT merge: no conflict, no silent loss
- "Neither is lost" → the CRDT merge operation preserves all additions
- "Reconnect + automatic merge" → state-based CRDT: send full state, merge deterministically
- "Google Docs" → uses Operational Transformation (OT) or RGA CRDT

**One insight:**
The key mathematical property: a CRDT's merge operation is a **join** in a **join-semilattice** — it's commutative (merge(A, B) = merge(B, A)), associative (merge(merge(A, B), C) = merge(A, merge(B, C))), and idempotent (merge(A, A) = A). These three properties guarantee that regardless of the order replicas receive updates, they all converge to the same final state.

---

### 🔩 First Principles Explanation

**G-COUNTER (Grow-only Counter):**

```
Problem: distributed counter (page view count, like count)
  Multiple nodes increment; single integer → concurrent increments lost

G-Counter structure:
  Each node maintains its OWN increment count:
  state = { nodeA: 5, nodeB: 3, nodeC: 7 }
  value() = sum(all) = 15

  Node A increments: { nodeA: 6, nodeB: 3, nodeC: 7 }
  Node B increments concurrently: { nodeA: 5, nodeB: 4, nodeC: 7 }

  Merge: take MAX per node:
  { nodeA: max(6,5)=6, nodeB: max(3,4)=4, nodeC: max(7,7)=7 }
  value() = 6+4+7 = 17  ← both increments preserved ✓

Why merge is join (semilattice):
  Partial order: A ≤ B if A[i] ≤ B[i] for all i
  Join = pairwise max → least upper bound
  Commutative: merge(A,B) = merge(B,A) ✓ (max is symmetric)
  Associative: merge(merge(A,B),C) = merge(A,merge(B,C)) ✓
  Idempotent: merge(A,A) = A ✓ (max(x,x)=x)
```

**PN-COUNTER (Increment + Decrement):**

```
Two G-Counters: P (positive increments), N (negative decrements)
value() = sum(P) - sum(N)

Increment on Node A: P[A]++
Decrement on Node B: N[B]++
Merge: merge(P), merge(N) independently
value() = correct net count

Use case: distributed inventory count, like/unlike counts
Limitation: value can go negative (no lower-bound enforcement)
For bounded counters (e.g., seats remaining ≥ 0): use reservations, not PN-Counter
```

**OR-SET (Observed-Remove Set, "Add Wins"):**

```
Problem: set with adds and removes
  Node A: add("apple"), add("banana")
  Node B (before seeing A's adds): remove("banana")
  Merge: should "banana" be in or out?

OR-Set solution: each element has a unique tag on add
  Node A: add("apple", tag=a1), add("banana", tag=b1)
  Node B: remove("banana") — removes all tags it knows about: {b1}
    But: Node B hasn't seen b1 yet (network partition!)
    So Node B's remove set is empty (it has no tags to remove)

  Merge:
    Added elements: {(apple,a1), (banana,b1)} from A
    Removed tags:   {} from B (didn't know about b1)
    Elements still tagged: {(apple,a1), (banana,b1)}
    Result: {"apple", "banana"} — ADD WINS

  After merge, if B removes "banana":
    B now sees tag b1 → removes (banana, b1)
    Result after subsequent merge: {"apple"}  ← "banana" now gone

Use case: shopping carts ("add wins" — never silently lose items)
Riak 2.0: built-in CRDT types including Map, Set, Counter
```

**COLLABORATIVE TEXT EDITING (RGA CRDT):**

```
Replicated Growable Array: text as a sequence of uniquely-identified characters
  Each character: (nodeId, counter) unique ID
  Insert operation: (insert after characterId, new char, new char's ID)
  Delete operation: tombstone (mark as deleted but keep ID for reference)

Merge: combine all insertion operations from all replicas
  Deterministic ordering by unique IDs → consistent final document order

Example:
  Initial: "cat"
  Node A: insert 's' after 't' → "cats"
  Node B (concurrent): insert ' ' and 'a' and 'r' after 't' → "cart"

  Merge: both inserts preserved (different positions by ID)
  Final: "carts" or "scart"? → deterministic by tie-breaking rule on IDs
  All replicas apply same tie-breaking → same result

Real systems: Y.js (browser collaborative editing), Automerge,
              Figma (design collaboration), Apple Notes
```

---

### 🧪 Thought Experiment

**WHERE CRDTs BREAK: HARD CONSTRAINTS**

PN-Counter for available tickets: starts at 100. Ten nodes each try to sell tickets simultaneously. Each decrements the counter.

**THE PROBLEM:**
Each node checks `value() ≥ 1` and then decrements. With eventual consistency and PN-Counters: each node sees `value()=100` (not yet propagated decrements from other nodes), decrements, and confirms the sale. After merge: 10 nodes each sold a ticket, but the PN-Counter can only correctly decrement by 10 if all decrements are tracked independently. The value converges to 90 — but 10 tickets were "sold" based on each node thinking 100 were available. If only 5 tickets were actually available, you've oversold.

**THE LESSON:**
CRDTs guarantee eventual consistency of the counter value. They do NOT enforce constraints like "value ≥ 0 at all times across all nodes." A PN-Counter doesn't know that "going below 0 is invalid" — it just merges. For bounded resources (seats, inventory, account balances), CRDTs alone are insufficient. You need either: (a) strong consistency for the constraint check (pessimistic locking on inventory), or (b) bounded counters with reservations (each node "pre-allocates" a budget, spending from its local budget without central coordination — used in Google's distributed credit system).

CRDTs solve the "merge without conflict" problem. They don't solve the "enforce business invariants across concurrent distributed operations" problem.

---

### 🧠 Mental Model / Analogy

> CRDTs are like a bag of colored marbles where everyone has a copy and everyone can add marbles. The "merge" operation is just: put all the marbles from all the bags into one bag. It doesn't matter whose bag you merge first or last — the final merged bag always has the same total contents. You can never un-add a marble (G-Set), or you can remove marbles using special tagged tokens (OR-Set). No argument about "who added which marble last" — the structure prevents the argument from being possible.

- "Bag of marbles" → set CRDT
- "Everyone can add marbles" → concurrent writes from multiple replicas
- "Merge = combine all bags" → join operation (deterministic, commutative)
- "Never un-add" → G-Set (grow-only; deletions not supported)
- "Tagged tokens for removal" → OR-Set (tracked removes, add-wins)
- "No argument about who added last" → no conflict by design

---

### 📶 Gradual Depth — Four Levels

**Level 1:** CRDTs are special data structures where two copies can always be merged automatically without any conflicts. Unlike a regular variable (last write wins, one write lost), a CRDT counter tracks each machine's count separately and the total is always the sum — so concurrent increments from different machines are never lost.

**Level 2:** Use CRDTs for: distributed counters (page views, likes), shopping carts (OR-Set: add-wins), collaborative editing (RGA for text, Map CRDT for structured data), presence/availability markers. Don't use CRDTs for: operations with global invariants (inventory bounded by physical count), transactions requiring "check then act" atomicity. Redis Enterprise provides built-in CRDT data types for its Active-Active (multi-master) mode.

**Level 3:** The mathematical foundation: a CRDT's state space forms a **join-semilattice** — a partially ordered set where every pair of elements has a least upper bound (join). The join operation is the merge function. States can only move "upward" in the partial order — once an element is added, it can never be removed from the version vector perspective (though tombstoning allows logical deletion). This monotonicity is what guarantees convergence: states can only increase; merging always produces a state ≥ both inputs. Operation-based CRDTs (CmRDTs) require reliable delivery guarantees (operations must be delivered exactly once and in causal order) — implemented via vector clocks or causal broadcast. State-based CRDTs (CvRDTs) are simpler (just send full state, merge with max), but require sending the full state on each sync (large state = bandwidth expensive).

**Level 4:** CRDTs formalize a fundamental insight about distributed coordination: the cost of coordination (synchronization, consensus, locking) can be avoided if you constrain the data model to only support operations that are mathematically mergeable. This is the "coordination-free" programming paradigm. The Bloom language (Berkeley) explores coordination-free programming more broadly. CRDTs are the data structure embodiment; CRDTs + Bloom's CALM theorem (Consistency As Logical Monotonicity) suggest that any computation expressible in monotonic logic can be executed without coordination. Non-monotonic operations (anything that checks an upper bound, requires uniqueness, or needs to "take back" a previous action) require coordination. This gives you a precise characterization of when you need distributed locks/consensus vs. when you can be coordination-free: if your operation is monotone, use a CRDT; if it's not monotone, you need coordination. Modern collaborative editors (Google Docs, Figma) moved from Operational Transformation (OT — requires a central server to order operations) to RGA CRDTs (P2P merge without central ordering) precisely for this coordination-freedom property.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ RIAK CRDT WRITE + MERGE                              │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Client: increment counter "page_views"              │
│  Riak G-Counter state on Node A: {A:5, B:3, C:7}     │
│  Increment on Node A:            {A:6, B:3, C:7}     │
│  Concurrent increment on Node B: {A:5, B:4, C:7}     │
│                                                      │
│  Anti-entropy: Node A and B gossip states            │
│  Node A merges B's state:                            │
│    {max(6,5)=6, max(3,4)=4, max(7,7)=7} = {A:6,B:4,C:7}│
│  Node B merges A's state: same result                │
│  value() = 6+4+7 = 17  ← both increments counted    │
│                                                      │
│  [CRDTs ← YOU ARE HERE: coordination-free merge]     │
│  No locks. No consensus. No conflict. Convergent.    │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**COLLABORATIVE DOCUMENT EDITING:**

```
User A and User B both editing the same document (offline sync app)
Document uses OR-Map CRDT: keys = section names, values = text CRDTs

User A (offline): edits "Introduction" section
User B (offline): edits "Conclusion" section
Both come online → sync

[CRDTs ← YOU ARE HERE: state merge]
Merge: OR-Map merge
  "Introduction": User A's version (only A edited it)
  "Conclusion": User B's version (only B edited it)
  Other sections: unchanged (same in both — idempotent merge)

Result: merged document with BOTH edits, no conflicts, no human review needed
Contrast with LWW: one user's edits silently overwrite the other's
```

---

### ⚖️ Comparison Table

| Conflict Strategy         | Data Loss?               | Application Complexity     | Use Case                |
| ------------------------- | ------------------------ | -------------------------- | ----------------------- |
| **LWW (Last Write Wins)** | Yes (earlier write lost) | Low                        | Presence, session data  |
| **Vector Clocks**         | No (both versions kept)  | High (app resolves)        | Complex merge semantics |
| **CRDTs**                 | No (by design)           | Low (no resolution needed) | Counters, sets, carts   |
| **Strong Consistency**    | No                       | Low                        | Financial, inventory    |
| **Manual Merge**          | No                       | Very High                  | Complex domain logic    |

---

### ⚠️ Common Misconceptions

| Misconception                                      | Reality                                                                                                                                                                                                               |
| -------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "CRDTs solve all distributed consistency problems" | CRDTs solve conflict-free merging for specific data types. They don't enforce global invariants (e.g., stock quantity ≥ 0) or support non-monotonic operations                                                        |
| "CRDTs always preserve all user intent"            | OR-Set's "add wins" means a concurrent remove is silently ignored if the add from another replica isn't yet visible. The merge is deterministic and conflict-free, but the application semantics might surprise users |
| "CRDT state-based sync sends just the delta"       | State-based CRDTs send the full state on sync (the whole vector or set). For large states, this is bandwidth-intensive. Delta-state CRDTs (a newer variant) send only the change since last sync                      |
| "CRDTs are complex to implement"                   | The math is complex; using a library (Automerge, Y.js, Riak CRDT types) is straightforward. You shouldn't implement CRDTs from scratch for production use                                                             |

---

### 🚨 Failure Modes & Diagnosis

**1. CRDT Tombstone Accumulation**

**Symptom:** OR-Set (or RGA text CRDT) grows indefinitely in memory/storage, even as logical content shrinks. Performance degrades over time for collaborative documents with heavy editing history.

**Root Cause:** Deleted elements are tombstoned (marked deleted but kept for merge correctness). Old tombstones cannot be garbage collected safely until all replicas have received and applied the deletion — in a system with offline clients, this may never happen.

**Fix:** Implement a "distributed garbage collection" protocol: when all replicas have acknowledged a tombstone, remove it. Or: use a "epoch" mechanism — periodically, the server takes a snapshot of the current state, broadcasts it, and all clients restart from the snapshot (tombstones GC'd).

**Prevention:** For text CRDTs: Y.js implements GC via "garbage collection awareness" — tracks which deletions all peers have acknowledged. Long-term: design offline sync windows (clients disconnected > N days are reset to server state, clearing old tombstones).

---

### 🔗 Related Keywords

**Prerequisites:** Eventual Consistency in NoSQL, Multi-Master Replication, Distributed Systems
**Builds On This:** Distributed Systems, Collaborative Applications
**Related:** Eventual Consistency in NoSQL, Vector Clock

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ TYPES        │ G-Counter, PN-Counter, G-Set, OR-Set, RGA │
│ PROPERTY     │ Commutative + Associative + Idempotent    │
│ MERGE        │ Always deterministic; never loses data    │
│ CANNOT DO    │ Enforce global invariants (value ≥ 0)     │
│ USED BY      │ Riak, Redis Enterprise, Y.js, Automerge   │
│ USE FOR      │ Carts, counters, collaborative editing    │
│ ONE-LINER    │ "Math-guaranteed conflict-free merging — │
│              │  coordination-free distributed updates"   │
│ NEXT EXPLORE │ Vector Database → NewSQL                  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C — Design Question) Design a distributed real-time collaborative whiteboard using CRDTs: users can draw shapes, move them, change colors, and delete them. Multiple users may edit simultaneously with occasional network partitions. What CRDT type(s) would you use for the shape list (ordered), shape position (x, y coordinates), shape color (last writer), and shape deletion? What "last writer wins" vs. "all changes preserved" semantics make sense for each?

**Q2.** (TYPE F — Comparison Depth) Compare CRDTs vs. Operational Transformation (OT) for collaborative text editing: (a) topology requirements (peer-to-peer vs. requires central server), (b) merge semantics for conflicting edits, (c) tombstone/memory growth, (d) implementation complexity. Why did Google Docs originally use OT? Why are Y.js and Automerge (CRDT-based) now preferred for new collaborative applications?
