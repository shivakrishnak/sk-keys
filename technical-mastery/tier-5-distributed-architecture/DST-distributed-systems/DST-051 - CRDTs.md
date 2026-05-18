---
id: DST-051
title: "CRDTs - Conflict-free Replicated Data Types"
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-012, DST-028, DST-031
used_by: DST-079
related: DST-012, DST-028, DST-031, DST-032
tags:
  - distributed
  - crdts
  - eventual-consistency
  - conflict-free
  - replication
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 51
permalink: /technical-mastery/distributed-systems/crdts/
---

⚡ TL;DR - A CRDT is a data structure designed so that
concurrent updates on different replicas can always
be merged without conflicts; the merge is commutative
(order doesn't matter), associative (grouping doesn't
matter), and idempotent (applying twice = applying
once); CRDTs enable strong eventual consistency without
coordination, at the cost of restricted data structure
semantics.

---

### 📋 Entry Metadata

| #051 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Replication, Eventual Consistency, Vector Clocks | |
| **Used by:** | Multi-Region Consistency Strategy | |
| **Related:** | Replication, Eventual Consistency, Vector Clocks, Lamport Timestamps | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A collaborative document editor (Google Docs style)
runs on two nodes that can both be offline. User A
edits paragraph 3 while offline. User B also edits
paragraph 3 while offline. When both come back online
and replicas sync, there are two different versions
of paragraph 3. Which one wins? Last-write-wins loses
one edit. Manual merge requires human intervention.
The fundamental problem: two updates to the same
data, applied independently, often cannot be
automatically merged without losing information
or requiring coordination.

**THE INSIGHT:**
Design the data structure itself so that concurrent
updates ALWAYS merge correctly - mathematically.
Not by arbitrating which update wins, but by choosing
data structures where the result of merging is
uniquely determined regardless of the order updates
are applied. This eliminates the conflict entirely
by construction.

---

### 📘 Textbook Definition

A **CRDT** (Conflict-free Replicated Data Type) is a
data structure that can be replicated across multiple
nodes, where replicas can be independently updated,
and the replicas can always be merged into a consistent
final state without coordination.

**Two families:**
- **CvRDT (state-based):** Replicas exchange their
  full state. Merge is a join operation (least upper
  bound in a lattice).
- **CmRDT (operation-based):** Replicas exchange
  operations. Operations are designed to commute
  (can be applied in any order).

**Mathematical property (CvRDT):**
The merge function must form a **join-semilattice**:
- **Commutative:** merge(A, B) = merge(B, A)
- **Associative:** merge(A, merge(B, C)) = merge(merge(A, B), C)
- **Idempotent:** merge(A, A) = A

---

### ⏱️ Understand It in 30 Seconds

```
PROBLEM: Two replicas increment a counter.
  Replica A: counter = 5 (incremented from 3)
  Replica B: counter = 4 (incremented from 3)
  Merge: which is correct? 4? 5? 6?

  WRONG: MAX(5,4) = 5 (loses B's increment)
  WRONG: 5+4=9 (double counts original 3)
  RIGHT: Track increments per replica separately.

GROW-ONLY COUNTER (G-Counter):
  Replica A maintains: [A:2, B:1, C:0]  (own count=2)
  Replica B maintains: [A:1, B:2, C:0]  (own count=2)
  Merge = element-wise MAX:
    [A:max(2,1), B:max(1,2), C:max(0,0)]
    = [A:2, B:2, C:0]
  Total = 2+2+0 = 4 (correct! A added 2, B added 2)

  No matter what order replicas sync:
  merge is always commutative, associative, idempotent.
  No coordinator needed. No conflict possible.
```

---

### 🔩 First Principles Explanation

**COMMON CRDT TYPES:**

**G-Counter (Grow-only Counter):**

```python
class GCounter:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.counts: dict[str, int] = {node_id: 0}

    def increment(self) -> None:
        self.counts[self.node_id] += 1

    def value(self) -> int:
        return sum(self.counts.values())

    def merge(self, other: "GCounter") -> "GCounter":
        """Merge = element-wise max (join)."""
        result = GCounter(self.node_id)
        all_nodes = set(self.counts) | set(other.counts)
        result.counts = {
            node: max(
                self.counts.get(node, 0),
                other.counts.get(node, 0)
            )
            for node in all_nodes
        }
        return result

# Proof of properties:
# Commutative: merge(A,B) = max per node = merge(B,A) ✓
# Associative: merge(A, merge(B,C)) = max per node =
# merge(merge(A,B),C) ✓
# Idempotent:  merge(A, A) = max(x,x) = x for each ✓
```

**PN-Counter (Positive-Negative Counter):**

```python
class PNCounter:
    """Supports both increment and decrement."""
    def __init__(self, node_id: str):
        self.positive = GCounter(node_id)
        self.negative = GCounter(node_id)

    def increment(self) -> None:
        self.positive.increment()

    def decrement(self) -> None:
        self.negative.increment()

    def value(self) -> int:
        return self.positive.value() - self.negative.value()

    def merge(self, other: "PNCounter") -> "PNCounter":
        result = PNCounter(self.positive.node_id)
        result.positive = self.positive.merge(other.positive)
        result.negative = self.negative.merge(other.negative)
        return result
```

**LWW-Element-Set (Last-Write-Wins Set):**

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class TimestampedValue:
    value: Any
    timestamp: float

class LWWElementSet:
    """Elements added/removed tracked with timestamps."""
    def __init__(self):
        self.add_set: dict = {}     # elem -> timestamp
        self.remove_set: dict = {}  # elem -> timestamp

    def add(self, element: Any, timestamp: float) -> None:
        existing = self.add_set.get(element, -1)
        if timestamp > existing:
            self.add_set[element] = timestamp

    def remove(self, element: Any, timestamp: float) -> None:
        existing = self.remove_set.get(element, -1)
        if timestamp > existing:
            self.remove_set[element] = timestamp

    def contains(self, element: Any) -> bool:
        add_ts = self.add_set.get(element, -1)
        remove_ts = self.remove_set.get(element, -1)
        return add_ts > remove_ts  # Add wins ties convention

    def merge(self, other: "LWWElementSet") -> "LWWElementSet":
        result = LWWElementSet()
        for elem, ts in self.add_set.items():
            result.add(elem, ts)
        for elem, ts in other.add_set.items():
            result.add(elem, ts)
        for elem, ts in self.remove_set.items():
            result.remove(elem, ts)
        for elem, ts in other.remove_set.items():
            result.remove(elem, ts)
        return result
```

**OR-Set (Observed-Remove Set, no timestamp needed):**

```
Problem with LWW-Set: concurrent add and remove
require timestamp comparison (clock skew risk).

OR-Set: each add generates a unique tag (UUID).
To remove: remove all tags for the element.
Merge: union of add-sets, minus intersection of
       remove-sets with matching tags.

Semantics: "add wins" over concurrent remove.
Used in: shopping carts (add item wins over
concurrent remove from another device).
```

---

### 🧠 Mental Model / Analogy

> A CRDT is like a checklist where each person writes
> in their own column. Person A writes ✓ in column A.
> Person B writes ✓ in column B. When you merge the
> two checklists: take the maximum state from each
> column. If A checked something, it stays checked.
> If B checked it too, same result. Two checkmarks
> for the same item? You don't add them together -
> the item is just checked. You can never UNCHECK an
> item (grow-only). The merge is safe because no
> column can contradict another - they each only
> describe their own actions.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is:**
A data structure designed so that when the same
data is independently updated on multiple nodes and
then merged, there is never a conflict - the merge
always produces a single correct result, automatically.
No coordinator needed. No lock needed.

**Level 2 - Why the math works:**
The merge function must be commutative (A+B = B+A),
associative ((A+B)+C = A+(B+C)), and idempotent
(A+A = A). These three properties together mean:
no matter what order replicas sync, the final merged
state is always the same. This is called "strong
eventual consistency" (SEC).

**Level 3 - Trade-offs in data structure semantics:**
CRDTs don't support all operations. A G-Counter
supports only increment (not decrement). An OR-Set
has specific "add wins" or "remove wins" semantics.
The price of conflict-free merging: you must choose
data structure semantics that make conflicts
impossible by restricting what operations are allowed.

**Level 4 - Production use cases:**
Redis has built-in CRDT support in Redis Enterprise
(CRDTs for geo-distributed deployments). Riak uses
CRDTs for counters and sets. Apache Cassandra uses
a CRDT-like approach for counters. Collaborative
editors (Figma, Notion) use operation-based CRDTs
(OT or CRDT) for text editing.

**Level 5 - CvRDT vs CmRDT:**
State-based (CvRDT) sends full state on sync - simple
but bandwidth-intensive. Operation-based (CmRDT)
sends only operations - bandwidth-efficient but
operations must be delivered exactly-once (requires
reliable broadcast). In practice: many systems use
a hybrid - operation-based internally, state-based
for full sync after a long disconnection.

---

### 💻 Code Example

**CRDT vs Last-Write-Wins: Wrong vs Right**

```python
# BAD: Last-write-wins counter under concurrent updates
# (loses concurrent increments)

import time

class BadCounter:
    def __init__(self):
        self.value = 0
        self.timestamp = time.time()

    def increment(self) -> None:
        self.value += 1
        self.timestamp = time.time()

    def merge(self, other: "BadCounter") -> "BadCounter":
        # LWW: higher timestamp wins
        result = BadCounter()
        if self.timestamp >= other.timestamp:
            result.value = self.value
            result.timestamp = self.timestamp
        else:
            result.value = other.value
            result.timestamp = other.timestamp
        return result
        # BUG: if A and B both increment at same time,
        # one increment is silently lost.
```

```python
# GOOD: G-Counter CRDT (no concurrent update lost)

class GCounter:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.counts: dict[str, int] = {}

    def increment(self, amount: int = 1) -> None:
        self.counts[self.node_id] = (
            self.counts.get(self.node_id, 0) + amount
        )

    def value(self) -> int:
        return sum(self.counts.values())

    def merge(self, other: "GCounter") -> "GCounter":
        result = GCounter(self.node_id)
        all_nodes = set(self.counts) | set(other.counts)
        result.counts = {
            node: max(
                self.counts.get(node, 0),
                other.counts.get(node, 0)
            )
            for node in all_nodes
        }
        return result

# Test: concurrent increments on two replicas
node_a = GCounter("A")
node_b = GCounter("B")

node_a.increment(3)  # A increments 3 times
node_b.increment(2)  # B increments 2 times (concurrently)

# Sync: A gets B's state, B gets A's state
merged_a = node_a.merge(node_b)
merged_b = node_b.merge(node_a)

assert merged_a.value() == 5  # 3+2=5: correct!
assert merged_b.value() == 5  # Same result from either direction
# Commutative: merge(A,B) == merge(B,A) ✓
```

---

### ⚖️ Comparison Table

| CRDT Type | Supports | Does NOT Support | Use Case |
|---|---|---|---|
| **G-Counter** | Increment | Decrement | Page views, event count |
| **PN-Counter** | Increment, Decrement | Neither goes negative safely | Inventory (approximate) |
| **G-Set** | Add element | Remove element | Append-only sets |
| **2P-Set** | Add, Remove (once) | Re-add after remove | Tombstone-based sets |
| **LWW-Set** | Add, Remove | (LWW semantics) | User preferences |
| **OR-Set** | Add, Remove (add wins) | (complex but powerful) | Shopping carts, collaborative editing |

| Property | LWW (Last-Write-Wins) | CRDT |
|---|---|---|
| **Concurrent safety** | No (can lose writes) | Yes (merge is always correct) |
| **Coordination needed** | No | No |
| **Data richness** | Any data type | Restricted semantics |
| **Clock dependency** | Yes (timestamp) | No (state-based) |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "CRDTs work for any data type" | CRDTs only work for data structures specifically designed with merge semantics. A general-purpose mutable record cannot be made into a CRDT without redesigning its update operations. |
| "CRDTs replace all distributed databases" | CRDTs solve a specific problem: conflict-free merging of independently updated data. For transactions involving multiple objects with invariants (e.g., bank balance), CRDTs alone are insufficient. |
| "CRDTs are slow because of merging" | State-based CRDT merging is O(N) in state size. For most practical CRDTs (counters, small sets), merge is fast. The slowness concern is valid for large state (full-document CRDTs in editors). |
| "CRDTs guarantee no data loss" | CRDTs guarantee no conflict during merge. But OR-Set's "add wins" semantics means a concurrent remove is lost. The semantics are explicit - it is not data loss in the traditional sense, but the behavior may surprise users. |

---

### 🚨 Failure Modes & Diagnosis

**CRDT Counter Divergence After Long Partition**

**Symptom:** After a long network partition heals,
distributed counter values across nodes differ and
are unexpectedly high. Some nodes show a value that
exceeds what is expected from the actual number of
events.

**Root Cause:** Duplicate operations applied due to
idempotency violation. If an operation (increment)
was stored and replayed, but not properly de-duplicated
using the node's vector-clock-based tag, the same
operation was applied multiple times during sync.

**Diagnosis:**
```python
# Check for duplicate entries in the counter state:
def diagnose_gcounter(counter: GCounter) -> None:
    print(f"Total value: {counter.value()}")
    print("Per-node breakdown:")
    for node, count in sorted(counter.counts.items()):
        print(f"  {node}: {count}")
    # Unexpected: node with 10x the expected count
    # = duplicate increment events from that node

# OR-Set: check for orphaned tags
def diagnose_orset(orset) -> None:
    # Tags in add-set but in remove-set = elements removed
    # Tags in add-set only = elements present
    orphans = set(orset.add_tags) & set(orset.remove_tags)
    live_elements = set(orset.add_tags) - orphans
    print(f"Live elements: {live_elements}")
    print(f"Removed (tombstoned): {orphans}")
```

**Fix:** Ensure operation-based CRDTs use exactly-once
delivery (or idempotent operations with UUID-tagged
operations). For state-based CRDTs: element-wise MAX
is always safe regardless of delivery duplicates.

---

### 🔗 Related Keywords

**Prerequisites:** `Replication` (DST-012),
`Eventual Consistency and BASE` (DST-028),
`Vector Clocks` (DST-031)

**Builds On This:** `Multi-Region Consistency Strategy`
(DST-078), collaborative editing systems

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT       │ Data structure where concurrent updates    │
│            │ always merge correctly, no coordination   │
├────────────┼────────────────────────────────────────────┤
│ MERGE MUST │ Commutative: merge(A,B)=merge(B,A)        │
│ BE         │ Associative: merge(A,merge(B,C))=...      │
│            │ Idempotent: merge(A,A)=A                  │
├────────────┼────────────────────────────────────────────┤
│ TYPES      │ G-Counter (incr only), PN-Counter          │
│            │ G-Set, 2P-Set, LWW-Set, OR-Set            │
├────────────┼────────────────────────────────────────────┤
│ TRADE-OFF  │ No conflicts vs restricted semantics      │
│ USE WHEN   │ Multi-node updates, no coordination OK    │
│ AVOID WHEN │ Need complex invariants across objects    │
├────────────┼────────────────────────────────────────────┤
│ ONE-LINER  │ "CRDT: conflict-free by design, not by    │
│            │  arbitration."                            │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

CRDTs embody a powerful design principle: solve a
problem by eliminating the conditions that create it,
rather than by managing the problem when it arises.
Distributed conflicts are caused by operations that
do not commute (A then B ≠ B then A). Rather than
detecting and resolving conflicts, choose operations
that commute by construction. This principle applies
beyond data structures: idempotent API design (any
order of retries produces the same result), append-
only event logs (no update ordering conflicts),
content-addressed storage (no write conflicts -
content IS the key). When you design for
commutativity from the start, a class of failure
modes disappears.

---

### 💡 The Surprising Truth

Apple's Notes app, Figma, and several collaborative
editing systems use CRDT-based text representation
internally. The academic CRDT work for text (RGA -
Replicated Growable Array, LSEQ, YATA) was pioneered
at INRIA in France and originally seemed too
theoretical for practical use. The critical insight
that made it practical: for text editing, you don't
need to represent ALL operations as CRDTs - only the
structural ones (insert/delete characters). Formatting
(bold, italic) can use simpler LWW semantics because
concurrent formatting changes are semantically
non-conflicting to users. The lesson: CRDTs are most
powerful when applied surgically to the exact part
of the data model that has concurrent update conflicts,
not as a universal replacement for all state management.

---

### ✅ Mastery Checklist

1. [IMPLEMENT] Build a G-Counter CRDT with increment()
   and merge(). Verify merge is commutative, associative,
   and idempotent with unit tests.
2. [EXTEND] Extend G-Counter to a PN-Counter that
   supports both increment and decrement. Verify that
   two concurrent decrements from different nodes
   both take effect after merge.
3. [CHOOSE] For each: shopping cart, collaborative
   document, view count, user preferences (toggle
   on/off) - identify the most appropriate CRDT type.
4. [EXPLAIN] Why does LWW (last-write-wins) lose
   concurrent updates but G-Counter does not?
   Derive the mathematical property difference.
5. [IDENTIFY] Two scenarios where a CRDT is NOT
   the right choice, even though eventual consistency
   is acceptable.
