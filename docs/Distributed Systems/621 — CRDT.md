---
layout: default
title: "CRDT"
parent: "Distributed Systems"
nav_order: 621
permalink: /distributed-systems/crdt/
number: "621"
category: Distributed Systems
difficulty: ★★★
depends_on: "Eventual Consistency, Conflict Resolution Strategies"
used_by: "Redis, Riak, AntidoteDB, Figma, Google Docs, Automerge"
tags: #advanced, #distributed, #consistency, #conflict-free, #data-structures
---

# 621 — CRDT

`#advanced` `#distributed` `#consistency` `#conflict-free` `#data-structures`

⚡ TL;DR — A **CRDT** (Conflict-free Replicated Data Type) is a data structure that can be replicated across nodes and updated independently — **concurrent updates always merge automatically without conflicts**, guaranteeing strong eventual consistency.

| #621 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Eventual Consistency, Conflict Resolution Strategies | |
| **Used by:** | Redis, Riak, AntidoteDB, Figma, Google Docs, Automerge | |

---

### 📘 Textbook Definition

**CRDT** (Conflict-free Replicated Data Type, Shapiro et al., 2011) is a class of data structures designed for distributed systems where: (1) replicas can be updated independently and concurrently; (2) all replicas will eventually converge to the same state; (3) convergence is guaranteed by the mathematical properties of the data structure itself — without requiring coordination or conflict resolution logic. Two types: **State-based CRDT (CvRDT)** — replicas periodically exchange full state; merge function is commutative, associative, and idempotent (forms a join-semilattice). **Operation-based CRDT (CmRDT)** — replicas broadcast operations; operations are commutative (any order → same result). Examples: **G-Counter** (grow-only counter), **PN-Counter** (positive-negative counter), **LWW-Register** (last-write-wins register), **OR-Set** (observed-remove set, handles concurrent add/remove), **RGA** (replicated growable array, for collaborative text editing). Key property: merge is always possible and deterministic — no "conflicts" in the traditional sense. Strong Eventual Consistency (SEC): all replicas that receive the same updates (in any order) have the same state.

---

### 🟢 Simple Definition (Easy)

Two people editing a shared document offline. Both add different items to a to-do list while offline. When they reconnect: a CRDT-based list just merges both additions — no conflict. Traditional approach: "they both edited at the same time — conflict! Pick one." CRDT: mathematically designed so any merge always works. Each operation is designed so ORDER of applying operations DOESN'T MATTER — the result is always the same.

---

### 🔵 Simple Definition (Elaborated)

Why CRDTs vs. traditional conflict resolution: Git merge conflicts require human resolution. Database "last write wins" silently discards updates. CRDTs: guarantee merge is always automatic and correct by design. Example: G-Counter (grow-only counter). Each node has its own counter slot. Increment: only increment your slot. Total: sum all slots. Two nodes increment independently: just sum. Can never conflict (each writes only to its own slot). The "no conflict" property is achieved by restricting operations to those that always commute.

---

### 🔩 First Principles Explanation

**Join-semilattice, state vs. operation-based, and common CRDT types:**

```
MATHEMATICAL FOUNDATION:

  A CRDT's merge function must form a JOIN-SEMILATTICE:
  
  1. COMMUTATIVE: merge(A, B) = merge(B, A)
     Order of merging doesn't matter.
     
  2. ASSOCIATIVE: merge(merge(A, B), C) = merge(A, merge(B, C))
     Grouping of merges doesn't matter.
     
  3. IDEMPOTENT: merge(A, A) = A
     Merging the same state twice: same result as once. (Handles duplicate messages.)
     
  Together: any ordering, any number of duplicates → same final state.
  This guarantees STRONG EVENTUAL CONSISTENCY (SEC):
  "All replicas that have received the same set of updates are in the same state."

G-COUNTER (GROW-ONLY COUNTER):

  Each node i has a slot in vector: [n0, n1, n2, ...]
  
  Node A: [3, 0, 0]  (A incremented 3 times)
  Node B: [0, 5, 0]  (B incremented 5 times)
  Node C: [0, 0, 2]  (C incremented 2 times)
  
  Increment(nodeId): counter[nodeId]++  (only write to own slot)
  Value(): sum(counter)                 (3 + 5 + 2 = 10)
  Merge(A, B): take max of each slot = [max(3,0), max(0,5), max(0,2)] = [3, 5, 0]
  
  MERGE: after A receives B's state: [3, 5, 0]
  After all merge: [3, 5, 2]. Value = 10.
  
  CONFLICT FREE: node A writes only slot 0. Node B writes only slot 1.
  Never contend on the same slot. Merge = max per slot. Always consistent.
  
  IDEMPOTENT: merge([3,5,0], [3,5,0]) = [3,5,0]. Duplicate merge = no-op.
  COMMUTATIVE: merge([3,5,0], [3,0,2]) = merge([3,0,2], [3,5,0]) = [3,5,2]. ✓
  
PN-COUNTER (INCREMENT AND DECREMENT):

  Two G-Counters: P (increments) + N (decrements).
  
  increment(nodeId): P[nodeId]++
  decrement(nodeId): N[nodeId]++
  value(): sum(P) - sum(N)
  merge(A, B): merge(A.P, B.P) + merge(A.N, B.N) (merge each G-counter)
  
  Example:
    Node A: incremented 3, decremented 1. P=[3,0], N=[1,0].
    Node B: incremented 0, decremented 2. P=[0,2], N=[0,2].
    Merged: P=[3,2], N=[1,2]. Value = (3+2) - (1+2) = 2.
    
  Concurrent increment on A + decrement on B: naturally merged. No conflict.

OR-SET (OBSERVED-REMOVE SET — HANDLES CONCURRENT ADD/REMOVE):

  Problem: simple "add/remove" set has a conflict: what if A adds element X and B removes X simultaneously?
  
  OR-Set solution: each add creates a UNIQUE TAG for the element.
  Remove: removes specific tags (the ones observed at remove time).
  Add wins over concurrent remove of same element (different tags).
  
  Example:
    Initial state: {(X, tag1)}   — X added with tag1.
    Replica A: remove X → removes {tag1}: state = {}
    Replica B (concurrent): add X → generates {tag2}: state = {(X, tag1), (X, tag2)}
    
    Merge A + B:
      A removed (X, tag1). B added (X, tag2). 
      Merged: {(X, tag2)} — X survives because tag2 is unique (B's add happened concurrently).
      
    "Add wins" over concurrent remove because the add creates a new unique tag that the remove never knew about.
    
LWW-REGISTER (LAST-WRITE-WINS REGISTER):

  Each write tagged with logical timestamp (Lamport clock, or physical timestamp with node ID tiebreak).
  Merge: take value with highest timestamp.
  
  Risk: concurrent writes → one silently discarded.
  Use: when losing concurrent writes is acceptable (user preference, settings).
  Not for: counters, sets (use G-Counter, OR-Set instead).
  
COLLABORATIVE TEXT EDITING CRDTs:

  Requirements: concurrent edits to text → eventual consistent document.
  
  RGA (Replicated Growable Array — used in Riak):
    Each character: unique identifier (nodeId + sequence).
    Insert: reference previous character's ID + new character.
    Delete: mark character as "tombstone" (don't remove immediately).
    Merge: re-order characters by their unique IDs.
    
  LOGOOT / LSEQ:
    Each character: position in a tree with fractional positioning.
    Concurrent inserts: never conflict (fractional positions are unique).
    
  Automerge / Yjs (modern implementations):
    Used in: Figma (real-time collaborative design), Notion, Liveblocks.
    CRDT for: text, arrays, maps, counters.
    Works offline: reconnect → automatic merge.
    
  EXAMPLE: Figma uses CRDTs for real-time collaborative editing.
    Two users: move the same shape simultaneously.
    LWW-Register (position): last writer's position wins. Small conflict (acceptable).
    Two users: add text to document simultaneously.
    Sequence CRDT (text): both inserts preserved, interleaved by position.

CRDT IN REDIS (RedisGears / Redis Enterprise):

  Redis: active-active geo-replication using CRDTs.
  
  Data types: CRDT counter, CRDT set, CRDT register, CRDT hash.
  
  Scenario: two Redis clusters in US and EU. Customer adds item to cart on EU.
  Simultaneously: recommendation engine (US) adds discount item to same cart.
  Both add to CRDT OR-Set (cart). Replication: both additions preserved.
  No conflict. Cart = both items.
  
  Without CRDT: "last write wins" → one addition lost. Customer: missing cart item.

CRDT LIMITATIONS:

  1. SPACE OVERHEAD: tombstones accumulate.
     Deleted elements: kept as tombstones (needed for merge semantics).
     Garbage collection needed: compact tombstones after all replicas have merged.
     
  2. MONOTONICALLY INCREASING STATE:
     State-based CRDTs: state only grows (join-semilattice).
     Cannot "undo" a G-Counter increment. Design limitation.
     
  3. NOT ALL DATA TYPES HAVE CRDT VERSIONS:
     Sorted set with unique ranks: hard to CRDTify.
     Transactions (multi-key atomicity): no CRDT solution.
     CRDTs work best: individual data items, not multi-key operations.
     
  4. SEMANTIC GAPS:
     OR-Set "add wins" might not be desired semantics.
     Example: "if user removes item from cart: should concurrent add win?"
     Business logic: depends on intent. CRDTs: provide one merge semantics.
     May not match business intent.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT CRDTs:
- Concurrent updates require coordination (locks/consensus): high latency
- Without coordination: conflicts requiring explicit resolution (LWW silently discards)
- Offline editing: impossible without resolving conflicts on reconnect

WITH CRDTs:
→ Always-available writes: no coordination needed; merge is automatic
→ Offline-first applications: edits merge correctly on reconnect
→ Geo-distributed systems: each region writes independently; automatic eventual consistency

---

### 🧠 Mental Model / Analogy

> Voting tally boards in separate rooms: each room has a local tally board. Voters arrive and mark their vote. When rooms merge: add the tallies. No conflict — you just add. The G-Counter works exactly this way: each node has its own slot (its own room), adds to only its slot. Final count: sum all rooms. No one steps on anyone else's tally. This only works because counting is "add-only" — you can't take votes away (G-Counter: grow-only).

"Separate room tally boards" = per-node counter slots in G-Counter
"Adding tallies when rooms merge" = max-merge of G-Counter slots
"Only adding votes (never removing)" = monotonic grow-only property
"Sum all rooms for final count" = value() = sum of all slots

---

### ⚙️ How It Works (Mechanism)

```
STATE-BASED CRDT (CvRDT):
  Replicas: periodically send full state.
  Receiver: merge(localState, receivedState) using join operation.
  Convergence: after all messages delivered, all replicas identical.
  
OPERATION-BASED CRDT (CmRDT):
  Replicas: broadcast each operation.
  All replicas: apply same operations (in any order — operations are commutative).
  Requirement: at-least-once delivery. Operations idempotent or deduplication needed.
```

---

### 🔄 How It Connects (Mini-Map)

```
Eventual Consistency (replicas converge, but may conflict during divergence)
        │
        ▼ (CRDTs: convergence WITHOUT conflicts)
CRDT ◄──── (you are here)
(data structure designed so concurrent updates always merge automatically)
        │
        ├── Conflict Resolution Strategies: CRDT eliminates many conflicts by design
        ├── Anti-Entropy: mechanism for propagating CRDT state between replicas
        └── Vector Clocks: CmRDT operations use vector clocks for causal ordering
```

---

### 💻 Code Example

```java
// G-Counter CRDT implementation:
public class GCounter {
    private final String nodeId;
    private final Map<String, Long> counts = new ConcurrentHashMap<>();
    
    public GCounter(String nodeId) {
        this.nodeId = nodeId;
        counts.put(nodeId, 0L);
    }
    
    // Increment: only update own slot.
    public void increment() {
        counts.merge(nodeId, 1L, Long::sum);
    }
    
    // Value: sum all slots.
    public long value() {
        return counts.values().stream().mapToLong(Long::longValue).sum();
    }
    
    // Merge: take max of each slot. Idempotent, commutative, associative.
    public GCounter merge(GCounter other) {
        GCounter merged = new GCounter(this.nodeId);
        Set<String> allNodes = new HashSet<>(this.counts.keySet());
        allNodes.addAll(other.counts.keySet());
        
        for (String node : allNodes) {
            long myCount = this.counts.getOrDefault(node, 0L);
            long theirCount = other.counts.getOrDefault(node, 0L);
            merged.counts.put(node, Math.max(myCount, theirCount));
        }
        return merged;
    }
}

// Usage:
GCounter nodeA = new GCounter("A");
GCounter nodeB = new GCounter("B");

nodeA.increment(); nodeA.increment(); // A: 2
nodeB.increment(); // B: 1 (concurrent with A)

// Merge (in any order — same result):
GCounter merged = nodeA.merge(nodeB);
System.out.println(merged.value()); // 3: A's 2 + B's 1. No conflict.
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| CRDTs solve all distributed consistency problems | CRDTs solve concurrent update conflicts for SPECIFIC data operations. They don't handle: multi-key transactions (atomicity across multiple CRDTs), business-semantic conflicts (when "add wins over remove" is wrong for the domain), or operations that require seeing a globally consistent state before deciding. CRDTs are a targeted tool for specific consistency problems, not a general solution |
| CRDT merge is the same as "last write wins" | LWW silently discards one of two concurrent writes. CRDT merge PRESERVES both concurrent operations (OR-Set: concurrent add and remove both reflected; G-Counter: concurrent increments both counted). LWW: one update lost. CRDT: no information lost. Fundamentally different semantics — CRDTs are designed to never lose information |
| CRDTs don't need any network coordination | Operation-based CRDTs (CmRDT): require at-least-once reliable broadcast (operations must reach all replicas eventually). State-based CRDTs (CvRDT): require periodic anti-entropy (state exchange). Neither requires COORDINATION (locks, consensus), but both require COMMUNICATION (eventual message delivery). Offline: operations stored locally; propagated when reconnected |

---

### 🔥 Pitfalls in Production

**OR-Set tombstone accumulation — unbounded memory growth:**

```
SCENARIO: OR-Set used for real-time online user tracking.
  Users: connect → added to OR-Set. Disconnect → removed from OR-Set.
  10,000 users per day. System running for 1 year.
  
  OR-Set internals: deleted elements kept as tombstones.
  After 1 year: 3.65 million tombstones. Memory: gigabytes.
  Merge operations: O(tombstones) → slow.
  
BAD: OR-Set without GC policy:
  orSet.add("user-12345", tag);  // Tag persisted even after remove.
  orSet.remove("user-12345");    // Tombstone added, original tag kept for merge semantics.
  // After 1 year: millions of tombstones.
  
FIX 1: Background tombstone compaction (GC):
  // After all replicas have merged past version V:
  // Safe to delete tombstones from version < V.
  // Requires tracking: which version each replica has confirmed.
  orSet.compact(confirmedVersion); // Delete tombstones older than confirmedVersion.
  
  // Implementation: vector clock tracks what each replica has seen.
  // When all replicas have seen version V: tombstones up to V are safe to remove.
  
FIX 2: Time-bounded tombstones:
  Tombstone: includes expiry timestamp (e.g., now + 7 days).
  Background job: deletes expired tombstones.
  Risk: if a replica is offline > 7 days → might re-add an element that was removed.
  Acceptable for: user presence tracking (rare offline replicas).
  Not acceptable for: financial data (never lose a delete).
  
FIX 3: Choose appropriate data structure:
  For "online users": LWW-Register per user is simpler.
  "User-12345: online/offline" — LWW (last write wins: last update is current status).
  No tombstone accumulation. Concurrent status updates: LWW resolves (minor risk for presence).
  OR-Set: for data where "concurrent add wins over remove" is the right semantic.
  
MONITORING:
  Alert: OR-Set tombstone count > 100K → trigger GC.
  Metric: crdt.orset.tombstone.count, crdt.orset.live.count.
```

---

### 🔗 Related Keywords

- `Eventual Consistency` — CRDTs achieve Strong Eventual Consistency (SEC)
- `Conflict Resolution Strategies` — CRDTs eliminate the need for most conflict resolution
- `Anti-Entropy` — mechanism for propagating CRDT state between replicas
- `Vector Clocks` — used in operation-based CRDTs for causal ordering of operations
- `Automerge` — popular JavaScript CRDT library for collaborative applications

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Data structure where all concurrent ops  │
│              │ merge automatically. No conflicts.       │
│              │ Mathematical guarantee: commutative +    │
│              │ associative + idempotent merge.          │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Collaborative editing; offline-first apps;│
│              │ geo-distributed with concurrent writes;  │
│              │ counters / sets without coordination     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Multi-key atomic transactions; business  │
│              │ logic requires seeing global state;      │
│              │ "add wins" semantics don't fit domain    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Separate vote tallies merge by adding:  │
│              │  no conflict, no coordination needed."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Conflict Resolution → Anti-Entropy →     │
│              │ Vector Clocks → Automerge → Yjs → Figma  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A shopping cart (OR-Set CRDT) holds items. User removes "Blue Shirt" from cart on their phone (offline). Simultaneously, a marketing automation system adds "Blue Shirt" back to the cart because the user abandoned it (a re-engagement feature). When the phone reconnects: OR-Set merge says "add wins over concurrent remove" → Blue Shirt is back. Is this the correct semantic for a shopping cart? If not, how would you design the shopping cart differently? What CRDT variant or alternative approach fits the business requirement better?

**Q2.** You're implementing a distributed collaborative text editor using CRDT (RGA algorithm). Two users simultaneously insert text at the same position: User A inserts "Hello" and User B inserts "World" at position 5. How does RGA determine which text comes first? What is the "unique character identifier" and how does it provide a total order for concurrent inserts? What happens to a client that is offline for 1 hour and makes 500 edits — describe the merge process when they reconnect.
