---
layout: default
title: "CRDT"
parent: "Distributed Systems"
nav_order: 621
permalink: /distributed-systems/crdt/
number: "0621"
category: Distributed Systems
difficulty: ★★★
depends_on: Eventual Consistency, Vector Clock, Conflict Resolution Strategies
used_by: Collaborative Editing, Distributed Databases, Offline-First Apps
related: Conflict Resolution Strategies, Gossip Protocol, Anti-Entropy, Eventual Consistency, Vector Clock
tags:
  - distributed
  - data-structure
  - convergence
  - replication
  - deep-dive
---

# 621 — CRDT (Conflict-free Replicated Data Type)

⚡ TL;DR — CRDTs are special data structures designed so that concurrent updates on multiple replicas always merge correctly without conflicts — the merge operation is mathematically guaranteed to be commutative, associative, and idempotent. No coordination protocol is needed; nodes just exchange states (or operations), apply the merge function, and all replicas converge to the same value.

| #621            | Category: Distributed Systems                                                                     | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------------------------------------------------ | :-------------- |
| **Depends on:** | Eventual Consistency, Vector Clock, Conflict Resolution Strategies                                |                 |
| **Used by:**    | Redis, Riak, Collaborative Editing (Figma, Google Docs internals), Offline-First Apps             |                 |
| **Related:**    | Conflict Resolution Strategies, Gossip Protocol, Anti-Entropy, Eventual Consistency, Vector Clock |                 |

### 🔥 The Problem This Solves

**WORLD WITHOUT CRDTs:**
Generic distributed databases facing concurrent writes must choose: (1) queue all writes through a single leader (coordination overhead, latency, single point of failure), (2) Last-Write-Wins (loses updates silently), (3) manual conflict resolution that must be surfaced to the application (complex, user-hostile). For some data structures — counters, sets, registers — there's a smarter option.

**THE CRDT INSIGHT:**
Certain data structures have operations with mathematical properties that make conflicts impossible:

- **Increment counter**: increment(5) then increment(3) = increment(3) then increment(5) → commutative! No matter which replica applies which operation first, the result is the same.
- **Add-to-set**: add(A) then add(B) = add(B) then add(A) → commutative!
- If all operations are commutative, associative, and idempotent: no matter in what order replicas receive and apply operations, they all converge to the same state.

This insight powers a class of data structures where "conflict-free" merging is a provable mathematical property.

---

### 📘 Textbook Definition

A **CRDT (Conflict-free Replicated Data Type)** is a data structure that can be replicated across multiple nodes, updated independently on any replica without coordination, and reliably merged without conflicts. **Two types**: (1) **CvRDT (Convergent CRDT / State-based)**: replicas periodically exchange complete states; the merge function computes a join in a semi-lattice order (least upper bound). (2) **CmRDT (Commutative CRDT / Operation-based)**: replicas broadcast operations; operations must be commutative (any order gives same result). **Guarantee**: all replicas that have received the same updates (in any order) will be in identical states. **Examples**: G-Counter (grow-only counter), PN-Counter (positive/negative counter), G-Set (grow-only set), OR-Set (observed-remove set), LWW-Register (last-write-wins register), RGA (replicated growth array). **Used in**: Redis (geo-distributed), Riak (distributed database), Apple's Notes (offline sync), Figma (collaborative design), collaborative text editors.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
CRDTs are data structures where merge is always unambiguous and conflict-free, so distributed replicas can update independently and always converge — no leader, no locks, no conflict resolution needed.

**One analogy:**

> Imagine teammates submitting "vote slip" ballots for a feature. Ballot rule: you can only add new votes ("yes for feature A"), not retract them. Now team members in different locations each collect votes. When they sync, they just take the union of all slips. No matter who syncs in what order, or who has a subset, the final combined result is always the same. The union operation is commutative, associative, and idempotent. A G-Set CRDT works exactly like this.

**One insight:**
CRDTs don't eliminate disagreement — they eliminate the NEED to resolve disagreement by choosing data structures where merging is always unambiguous. The trade-off: not all data operations can be made CRDT-compatible. You can't have a "remove element and re-add it" set with full conflict-freedom without additional bookkeeping (see: OR-Set).

---

### 🔩 First Principles Explanation

**MATHEMATICAL FOUNDATION:**

```
For state-based CRDTs (CvRDT):

Requirement: State set S forms a join-semilattice.
  - Partial order: ≤ (e.g., counter value 5 ≤ counter value 7)
  - Join operation: ⊔ (merge = least upper bound)
  - Properties:
      s ⊔ s = s               (idempotent)
      s1 ⊔ s2 = s2 ⊔ s1      (commutative)
      (s1 ⊔ s2) ⊔ s3 = s1 ⊔ (s2 ⊔ s3)  (associative)

Because merge (⊔) is idempotent, commutative, associative:
  - Receiving a state update twice = same as once
  - Receiving updates out of order = same result
  - Replicas merging in any order = same result
  → CONFLICT FREE
```

**G-COUNTER (GROW-ONLY COUNTER):**

```python
class GCounter:
    """
    G-Counter CRDT: a distributed counter that can only increment.
    State: one slot per replica node — each node only increments its own slot.
    """
    def __init__(self, node_id: str, all_nodes: list):
        self.node_id = node_id
        # One counter per node — this replica only updates its own slot
        self.counts = {n: 0 for n in all_nodes}

    def increment(self, amount: int = 1) -> None:
        """Only this node increments its own slot."""
        self.counts[self.node_id] += amount

    def value(self) -> int:
        """Global value = sum of all node slots."""
        return sum(self.counts.values())

    def merge(self, other: 'GCounter') -> 'GCounter':
        """
        Merge = take element-wise max of the two count vectors.
        This is the "join" in the semilattice.
        Idempotent: merge(self, self) = self
        Commutative: merge(A, B) = merge(B, A)
        """
        result = GCounter(self.node_id, list(self.counts.keys()))
        for node in self.counts:
            result.counts[node] = max(
                self.counts.get(node, 0),
                other.counts.get(node, 0)
            )
        return result

# Example: 3 replicas each increment independently, then merge
node_a = GCounter("A", ["A", "B", "C"])
node_b = GCounter("B", ["A", "B", "C"])
node_c = GCounter("C", ["A", "B", "C"])

node_a.increment(3)   # e.g., 3 purchases on replica A
node_b.increment(7)   # 7 purchases on replica B
node_c.increment(2)   # 2 purchases on replica C

# After gossip sync:
merged = node_a.merge(node_b).merge(node_c)
print(f"Global count: {merged.value()}")  # 12 — always correct regardless of merge order
```

**OR-SET (OBSERVED-REMOVE SET) — handles add AND remove:**

```python
import uuid

class ORSet:
    """
    OR-Set CRDT: supports both add and remove operations.
    Problem with simple G-Set + tombstone-set:
      Node A adds "X", Node B removes "X" concurrently.
      Simple approach: whoever "wins" — loses some intent.

    OR-Set solution: each ADD creates a unique tag.
      REMOVE only removes specific tags it observed.
      If ADD and REMOVE are concurrent: ADD wins (not the tag REMOVE saw).
    """
    def __init__(self):
        # elements dict: element → set of unique tags
        self.elements = {}  # {value: {tag1, tag2, ...}}
        self.tombstones = set()  # removed tags

    def add(self, value):
        tag = str(uuid.uuid4())            # unique tag per add operation
        if value not in self.elements:
            self.elements[value] = set()
        self.elements[value].add(tag)
        return tag

    def remove(self, value):
        """Remove only the tags this replica has OBSERVED (not future adds)."""
        if value in self.elements:
            for tag in self.elements[value]:
                self.tombstones.add(tag)
            del self.elements[value]

    def contains(self, value) -> bool:
        if value not in self.elements:
            return False
        active_tags = self.elements[value] - self.tombstones
        return len(active_tags) > 0

    def merge(self, other: 'ORSet') -> 'ORSet':
        result = ORSet()
        # Union of all elements and tombstones
        all_keys = set(self.elements.keys()) | set(other.elements.keys())
        for val in all_keys:
            tags = (self.elements.get(val, set()) |
                    other.elements.get(val, set()))
            result.elements[val] = tags
        result.tombstones = self.tombstones | other.tombstones
        return result
```

---

### 🧪 Thought Experiment

**CRDT vs. LWW for Distributed Shopping Cart:**

Alice's cart on her phone (offline): adds "milk", removes "bread", adds "eggs".
Bob's cart on his laptop (online): removes "milk", adds "rice".

When Alice reconnects:

- **LWW**: the last timestamp wins. If Bob's laptop clock is 10ms ahead, ALL of Bob's state wins → Alice loses her "eggs" add. Silent data loss.
- **CRDT (OR-Set)**: merges both sets of operations. "milk": Alice added (tag_A), Bob removed (tag_A) → tag_A tombstoned → milk removed (Bob's intent honored). "eggs": Alice added (tag_E), Bob didn't see it → eggs present (Alice's intent honored). "rice": Bob added → rice present. Result: {eggs, rice} — both users' intents preserved.

The CRDT approach preserves user intent. LWW silently discards it.

---

### 🧠 Mental Model / Analogy

> Think of CvRDT state as a ratchet: it can only click forward (or stay put), never backward. Merging two ratchet positions means advancing to whichever is further ahead. Receiving an "old" state? The ratchet is already past it — no change. Receiving a "new" state? Click forward. Unlike a regular counter, which can be told to go backwards (decrement) in conflicting ways, the CRDT ratchet guarantees monotonic progress. The OR-Set is a ratchet for membership: add events advance it forward; removes mark specific historical advances as "invisible" without rewinding others.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** CRDTs are data structures where concurrent updates on different replicas can always be merged without conflict. A G-Counter stores one slot per replica; merge = take the max of each slot. No coordination needed; slaves just gossip state and merge.

**Level 2:** Two CRDT families: state-based (CvRDT — exchange full state, merge = join in semilattice) and operation-based (CmRDT — exchange operations, ops must be commutative). OR-Set solves the add/remove concurrency problem by tagging each add with a UUID — remove only tombstones observed tags (not future concurrent adds). Text CRDTs (RGA, LSEQ) enable conflict-free collaborative editing.

**Level 3:** CRDTs are used in Riak (ring-based KV store), Redis Cluster (CRDT-based counters in Redis Enterprise), Apple Notes sync, Figma's collaboration engine, and distributed mobile app sync frameworks. The OR-Set's implementation in databases reveals practical challenges: tombstone sets must be periodically garbage-collected (a metadata operation requiring coordination). The G-Counter's vector of node counts means state size grows with cluster size. Delta-state CRDTs optimize this by only sending the "delta" (difference) rather than the full state.

**Level 4:** CRDT design is constrained by the CAP theorem: CRDTs maximize availability and partition-tolerance. Their trade-off is that some operations require per-element unique identifiers (OR-Set) or lose semantic richness (G-Set can't remove). Advanced CRDTs for text editing (RGA — Replicated Growable Array; LSEQ) assign unique interleaved positions to characters, enabling insertion order to be preserved across concurrent inserts. Proving CRDT correctness requires showing the state space forms a join-semilattice (and/or that operations are commutative). Research area: composing CRDTs (can you build a distributed JSON document as a composition of CRDTs? Yes — Kleppmann's "Key-Value CRDT" papers). Production challenge: CRDTs require agreement on node identity (each node needs a unique ID), which requires a brief coordination phase at cluster formation.

---

### ⚙️ How It Works (Mechanism)

**Redis CRDT (Redis Enterprise Active-Active geo-replication):**

```
Redis Enterprise with CRDT replication:

1. Cluster spans two datacenters (NYC and LON)
2. Each datacenter has a copy of all keys
3. Writes go to the local datacenter (low latency)
4. Async replication stream between NYC ↔ LON

CRDT-enforced semantics:
  - String: LWW-Register (last timestamp wins)
  - Counter: PN-Counter (each DC tracks its own increments/decrements)
  - Set: OR-Set (concurrent adds win over concurrent removes)
  - Hash: dictionary of LWW-Registers per field
  - Sorted Set: NWW-sorted-set CRDT

Example — Counter:
  NYC: INCR page_views → NYC slot: 100
  LON: INCR page_views → LON slot: 75
  Replication sync:
    NYC receives LON state: max(100, 0) + max(0, 75) = 175
    LON receives NYC state: max(0, 100) + max(75, 0) = 175
  Result: both DCs converge to 175. No coordination required.

Without CRDT (classic master-slave):
  All writes routed to NYC master.
  LON writes have +100ms latency.
  NYC failure → reads from LON stale.
```

---

### ⚖️ Comparison Table

| Aspect               | CRDT                           | Operational Transform         | LWW                     | Paxos/Raft                 |
| -------------------- | ------------------------------ | ----------------------------- | ----------------------- | -------------------------- |
| Conflict handling    | Math-guaranteed no conflict    | Transform operations at merge | Discard older timestamp | Serialized through leader  |
| Coordination needed  | None (async)                   | None (for OT)                 | None                    | Yes (quorum)               |
| Data loss risk       | None (for operations in scope) | None                          | Yes (silent)            | None                       |
| Supported operations | Limited (depends on CRDT type) | Any (complex transforms)      | Any                     | Any                        |
| Latency              | Read/write local (low)         | Read/write local (low)        | Read/write local (low)  | Leader round-trip (higher) |
| Used in              | Redis, Riak, Figma             | Google Docs (early)           | Many DBs (fallback)     | etcd, ZooKeeper            |

---

### ⚠️ Common Misconceptions

| Misconception                                      | Reality                                                                                                                                                                             |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CRDTs can represent any data structure             | Only certain operations are CRDT-compatible. A "decrement-then-read-if-zero-delete" pattern requires coordination and can't be CRDT-ized                                            |
| CRDTs are only for counters                        | CRDTs include sets, maps, registers, sequences (text CRDTs), graphs — any data structure that can be modeled as a join-semilattice                                                  |
| CRDTs eliminate the need for consistency protocols | CRDTs give eventual consistency for their supported operations. You still need consensus for anything outside the CRDT model (e.g., unique ID generation, distributed transactions) |

---

### 🚨 Failure Modes & Diagnosis

**Tombstone Explosion (OR-Set in Production)**

Symptom: Riak cluster's disk usage growing unboundedly. Read performance degrading.
Keys that are modified frequently have 10MB+ of metadata even though the value is small.
CRDT merge operations are noticeably slow.

Cause: OR-Set tombstone sets grow without bound. Each remove() adds a UUID to the
tombstone set. GC is not running. After millions of add/remove cycles (e.g., a
shopping cart key that changes often), the tombstone set has millions of entries.

Fix: (1) Enable CRDT tombstone GC ("replica GC" or "active anti-entropy repair").
(2) Model volatile data differently: for frequently-cycled data, use timestamps
(LWW-Register) instead of OR-Set. (3) Bound the number of adds possible: assign
CRDT types carefully based on operation frequency. (4) Riak-specific: set
`object.size.maximum` to flag keys with bloated metadata.

---

### 🔗 Related Keywords

- `Conflict Resolution Strategies` — LWW, multi-value registers, and application-level merge
- `Gossip Protocol` — the dissemination mechanism CvRDTs use to propagate state
- `Anti-Entropy` — background state synchronization for eventual convergence
- `Eventual Consistency` — the consistency model CRDTs fulfill
- `Vector Clock` — used to track causality in CmRDT operation ordering

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  CRDT: Conflict-free Replicated Data Type                │
│  CvRDT (state-based): send full state; merge = join       │
│  CmRDT (op-based): send ops; ops must be commutative     │
│  Types: G-Counter, PN-Counter, G-Set, OR-Set, Register   │
│  Math: join-semilattice; merge: idempotent+commutative+  │
│        associative                                        │
│  Used in: Redis, Riak, Figma, Apple Notes                │
│  Trade-off: limited operations; tombstone growth         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Design a PN-Counter (positive/negative counter that supports both INCR and DECR) using two G-Counters: one `P` for increments and one `N` for decrements. Write the `increment()`, `decrement()`, `value()`, and `merge()` methods. Prove that your `merge()` operation is commutative, associative, and idempotent.

**Q2.** Why can't you create a CRDT for a "unique counter" (a counter that increments and, when it reaches 0, deletes the key from the distributed K-V store)? What operation would violate the CRDT properties, and what consistency primitive would you need to implement this correctly?
