---
layout: default
title: "Conflict Resolution Strategies"
parent: "Distributed Systems"
nav_order: 622
permalink: /distributed-systems/conflict-resolution-strategies/
number: "0622"
category: Distributed Systems
difficulty: ★★★
depends_on: CRDT, Eventual Consistency, Vector Clock, Lamport Clock
used_by: Distributed Databases, Multi-Master Replication, Collaborative Apps
related: CRDT, Vector Clock, Lamport Clock, Eventual Consistency, Last-Write-Wins, Operational Transform
tags:
  - distributed
  - conflict
  - replication
  - consistency
  - deep-dive
---

# 622 — Conflict Resolution Strategies

⚡ TL;DR — In any system where concurrent updates can reach different replicas, conflicts must be resolved — two valid-but-incompatible states must be merged into one. Different strategies (Last-Write-Wins, multi-value registers, CRDT-based merge, application-level merge, operational transformation) differ in whether they lose data, require coordination, or need domain knowledge.

| #622            | Category: Distributed Systems                                                                   | Difficulty: ★★★ |
| :-------------- | :---------------------------------------------------------------------------------------------- | :-------------- |
| **Depends on:** | CRDT, Eventual Consistency, Vector Clock, Lamport Clock                                         |                 |
| **Used by:**    | Distributed Databases (DynamoDB, Cassandra, Riak), Multi-Master Replication, Sync Frameworks    |                 |
| **Related:**    | CRDT, Vector Clock, Lamport Clock, Eventual Consistency, Last-Write-Wins, Operational Transform |                 |

---

### 🔥 The Problem This Solves

**THE UNAVOIDABLE CONFLICT:**
In any distributed system where writes are accepted at multiple nodes (multi-master replication, offline-first apps, geo-distributed databases), concurrent writes to the same key will inevitably arrive at a replica in different orders — or simultaneously. Two scenarios:

1. **Concurrent writes**: Node A receives "price = $10" from client A at T=1; Node B receives "price = $12" from client B at T=1; they later sync. Which value is correct?
2. **Partition + reconnect**: During a network partition, Node A and B both processed writes. On reconnect, they have diverged state for some keys.

There is no universal correct answer — the right strategy depends on the data and application semantics. Understanding each strategy's trade-offs is critical to database configuration and application design.

---

### 📘 Textbook Definition

**Conflict Resolution Strategies** are the algorithms and policies used to reconcile divergent states when a distributed system encounters concurrent updates to the same data. A conflict occurs when two replicas have accepted different values for the same key, and there is no causal ordering between the updates (they are **concurrent** in the sense of Vector Clock theory). The main strategies are:

1. **Last-Write-Wins (LWW)**: the write with the highest timestamp (or sequence number) is kept; the other is discarded.
2. **Multi-Value Register (MVR)**: all conflicting versions are stored; conflict resolution is deferred to the reader or application.
3. **CRDT-Based Merge**: the data structure itself defines a correct merge operation (commutative, associative, idempotent).
4. **Application-Level / 3-Way Merge**: the application provides a semantic merge function (used in version control git-style merges).
5. **Operational Transformation (OT)**: transforming operations so that applying them out of order still produces a consistent result (Google Docs early approach).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Conflict resolution decides which value "wins" when two replicas accept different updates to the same key — strategies range from "newest timestamp wins" (simple, lossy) to "store all versions and let the application decide" (safe, complex).

**One analogy:**

> Imagine two co-authors editing a shared document while offline. Author A changed "Chapter 3 title: Foundations" to "Chapter 3 title: Theory". Author B changed it to "Chapter 3 title: Principles". When they sync: LWW picks whoever edits last (the other edit is lost). MVR shows both versions to a human editor. 3-way merge tries to intelligently combine (if no actual text overlap, it might even auto-merge). Operational Transform restructures each edit so both can apply cleanly on a shared document.

**One insight:**
There is no universally best strategy. The choice must be made based on: (1) can I afford to lose data? (LWW is acceptable for last-seen timestamps, terrible for financial data); (2) can the application resolve conflicts semantically? (application resolution is more powerful but requires business logic); (3) is the data type CRDT-compatible? (counters, sets — use CRDT, no conflict possible).

---

### 🔩 First Principles Explanation

**DETECTING CONFLICTS WITH VECTOR CLOCKS:**

```python
from typing import Dict, Any, List, Tuple

class VectorClock:
    def __init__(self, node: str, nodes: list):
        self.node = node
        self.clock = {n: 0 for n in nodes}

    def increment(self):
        self.clock[self.node] += 1

    def merge(self, other: 'VectorClock'):
        for n in self.clock:
            self.clock[n] = max(self.clock[n], other.clock.get(n, 0))

    def happened_before(self, other: 'VectorClock') -> bool:
        """self < other (self happened before other)"""
        return (all(self.clock[n] <= other.clock.get(n, 0) for n in self.clock) and
                any(self.clock[n] < other.clock.get(n, 0) for n in self.clock))

    def concurrent_with(self, other: 'VectorClock') -> bool:
        """Neither happened before the other → CONFLICT"""
        return (not self.happened_before(other) and
                not other.happened_before(self) and
                self.clock != other.clock)
```

**STRATEGY 1 — LAST WRITE WINS (LWW):**

```python
import time

class LWWRegister:
    """
    Last-Write-Wins Register.
    Simple: keep the version with the highest timestamp.
    Problem: clock skew → wrong winner; silent data loss.
    Use case: last-seen-at, presence status, telemetry values.
    """
    def __init__(self):
        self.value = None
        self.timestamp = 0

    def write(self, value: Any) -> None:
        ts = time.time()
        if ts > self.timestamp:
            self.value = value
            self.timestamp = ts

    def merge(self, other: 'LWWRegister') -> 'LWWRegister':
        result = LWWRegister()
        if self.timestamp >= other.timestamp:
            result.value, result.timestamp = self.value, self.timestamp
        else:
            result.value, result.timestamp = other.value, other.timestamp
        return result

# RISK: Clock skew allows "future" writes from slow clocks to lose to "older"
# writes from fast clocks. This is why DynamoDB offers LWW but also offers
# "conditional writes" for cases where this matters.
```

**STRATEGY 2 — MULTI-VALUE REGISTER (MVR):**

```python
class MVRegister:
    """
    Multi-Value Register (Amazon Dynamo-style).
    Store ALL concurrent versions; let the application resolve.
    Riak/DynamoDB: returns "siblings" on read — application must choose.
    """
    def __init__(self, node_id: str, nodes: list):
        # Each version: (value, vector_clock)
        self.versions: List[Tuple[Any, VectorClock]] = []
        self.node_id = node_id
        self.nodes = nodes

    def write(self, value: Any, vc: VectorClock) -> None:
        """Add version; prune any versions that are dominated by new vc."""
        vc.increment()
        new_versions = [(v, c) for v, c in self.versions
                        if not c.happened_before(vc)]
        new_versions.append((value, vc))
        self.versions = new_versions

    def read(self) -> List[Any]:
        """Return all concurrent versions (siblings)."""
        return [v for v, _ in self.versions]

    def resolve(self, resolved_value: Any, merged_vc: VectorClock) -> None:
        """Application provides the resolved value; discard all siblings."""
        self.versions = [(resolved_value, merged_vc)]

# Amazon DynamoDB/Riak usage:
#   cart = dynamo.get("cart:user123")
#   if len(cart.siblings) > 1:
#       resolved = application_merge_carts(cart.siblings)
#       dynamo.put("cart:user123", resolved, cart.context)
```

**STRATEGY 3 — APPLICATION-LEVEL 3-WAY MERGE:**

```python
def three_way_merge(base: str, version_a: str, version_b: str) -> str:
    """
    Git-style 3-way merge (simplified).
    Base: the common ancestor.
    Version A and B: two diverged modifications.

    If only one side changed a line: take that side's version.
    If both sides changed the same line differently: CONFLICT (mark for human resolution).
    If both sides changed the same line identically: no conflict, take either.
    """
    base_lines = base.splitlines()
    a_lines = version_a.splitlines()
    b_lines = version_b.splitlines()

    # Simplified: line-by-line merge (real git uses diff3/Myers algorithm)
    result = []
    max_len = max(len(base_lines), len(a_lines), len(b_lines))

    for i in range(max_len):
        base_line = base_lines[i] if i < len(base_lines) else None
        a_line = a_lines[i] if i < len(a_lines) else None
        b_line = b_lines[i] if i < len(b_lines) else None

        if a_line == b_line:
            result.append(a_line or "")     # Both same (or both absent)
        elif a_line == base_line:
            result.append(b_line or "")     # Only B changed: take B
        elif b_line == base_line:
            result.append(a_line or "")     # Only A changed: take A
        else:
            # Both changed differently: CONFLICT
            result.append(f"<<<<<<<\n{a_line}\n=======\n{b_line}\n>>>>>>>")

    return "\n".join(result)
```

**STRATEGY 4 — OPERATIONAL TRANSFORMATION (OT):**

```python
# Operational Transformation: used in collaborative text editors
# Operations: insert(pos, char) or delete(pos)
# Transform: adjust positions when concurrent ops are applied out of order

def transform_insert_vs_insert(op1, op2):
    """
    op1 = insert(pos=3, char='X')  [local op — being applied first]
    op2 = insert(pos=3, char='Y')  [remote concurrent op]

    After op1 is applied: all positions >= 3 shift right by 1.
    Transform op2: new position = pos + 1 = 4.
    Result: both chars are inserted; no conflict.
    """
    if op2['pos'] >= op1['pos']:
        return {'type': 'insert', 'pos': op2['pos'] + 1, 'char': op2['char']}
    return op2

# OT was used in Google Wave, early Google Docs.
# CRDTs (specifically RGA, LSEQ) have largely replaced OT in modern collaborative editors
# because OT requires a central server to order operations,
# while CRDTs work peer-to-peer.
```

---

### 🧪 Thought Experiment

**CHOOSING THE RIGHT STRATEGY FOR A DISTRIBUTED SHOPPING CART:**

**Scenario**: User has a mobile app that works offline. They add/remove items while offline on their phone. A family member does the same on their laptop. On reconnect, both carts must be merged.

| Operation                                | LWW                 | MVR                         | CRDT (OR-Set)                     | Application-level                                |
| ---------------------------------------- | ------------------- | --------------------------- | --------------------------------- | ------------------------------------------------ |
| Phone: add "milk"                        | ✅                  | ✅                          | ✅                                | ✅                                               |
| Laptop: remove "milk" (concurrent)       | ❌ (loses one edit) | ⚠️ (shows conflict to user) | ✅ (remove wins for that add-tag) | ✅ (app logic: "remove intent beats add intent") |
| Phone: add "eggs" (while laptop offline) | ❌ (may lose)       | ✅ (stored as sibling)      | ✅ (only phone added eggs)        | ✅                                               |
| Data preservation                        | POOR                | GOOD                        | GOOD                              | BEST                                             |
| Simplicity                               | HIGH                | MED                         | MED                               | LOW                                              |

Amazon DynamoDB's own Dynamo paper used MVR (siblings) for shopping carts — the application merges on read.

---

### 🧠 Mental Model / Analogy

> Conflict resolution strategies map exactly to how humans handle disagreement:
>
> - **LWW**: "whoever spoke last is right" — fast, but unfair and lossy.
> - **MVR**: "let's write down every position and decide later" — preserves all information, but defers the hard part.
> - **CRDT**: "we designed the system so disagreements are mathematically impossible" — ideal but only works for specific operation types.
> - **3-way merge**: "let's look at what we both started from (base) and understand how each person changed from that" — what git does.
> - **OT**: "we transform each person's edits so both can be applied to the same document simultaneously" — the most powerful, the most complex.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** When two nodes accept conflicting writes to the same key: LWW (keep the newest timestamp) is simple but can lose data. MVR (store all versions, let the app decide) is safe but complex. CRDT doesn't have conflicts in the first place.

**Level 2:** LWW requires synchronized clocks (NTP, TrueTime) for correctness. With NTP's inherent skew (~milliseconds), LWW can produce wrong results. DynamoDB LWW is based on system clocks — can lose writes from slightly-behind-clock nodes. Vector Clocks detect concurrency precisely (no clock sync needed) — required for true MVR systems. CvRDT merge = semilattice join; CmRDT merge = commutative operation application.

**Level 3:** Cassandra allows per-table conflict resolution policy: LWW (default) or custom. Riak uses MVR by default (with vector clocks), allows CRDT column families. Google Spanner avoids conflicts entirely via TrueTime + 2PC serializable transactions — pays in latency, gains strong consistency. The challenge with application-level resolution: you need the "base" version (common ancestor) for 3-way merge; without it, you only have 2 diverged versions → must use LWW or MVR fallback. MongoDB multi-master (before 5.x): LWW. Post-5.x change streams + retryable writes reduce conflicts.

**Level 4:** The theoretical foundation: conflicts arise exactly when two operations are **concurrent** (neither happened before the other in vector clock ordering). The ideal system would have zero concurrent operations (total order → strong consistency via serialization). The practical system must provide a conflict resolution strategy because total order is either impossible (FLP) or too expensive (Paxos latency). Research area: "semantic conflict resolution" — using domain knowledge (e.g., "a price must be ≥ 0") to intelligently resolve conflicts. CRDTs represent the current frontier of encoding semantic conflict-freedom directly into data structure design. Hybrid approaches combine strong consistency where needed (financial transactions) with eventual consistency elsewhere (view counts, preferences).

---

### ⚙️ How It Works (Mechanism)

**DynamoDB Conflict Resolution in Practice:**

```
DynamoDB (default): LWW based on item-level conditional writes.
  write: PutItem with ConditionExpression="version = :expected"
    - If condition fails: conditional check failed exception → client retries
    - If no condition: LWW (last writer wins based on request order)

Cassandra (default): LWW based on write timestamp:
  INSERT INTO orders (id, price) VALUES (123, 10.00) USING TIMESTAMP 1699000000;
  INSERT INTO orders (id, price) VALUES (123, 12.00) USING TIMESTAMP 1699000001;
  → price = 12.00 (higher timestamp wins, 10.00 is silently discarded)

Cassandra anti-pattern: multiple writes with same timestamp
  Both arrive at same microsecond → Cassandra picks lexicographically larger value.
  For maps/sets: Cassandra uses CRDT-like merge (union of additions).

Riak (MVR + siblings):
  1. PUT without vector clock → creates new sibling (conflict).
  2. Application: GET → receives siblings + context.
  3. Application: resolves → PUT with context → siblings merged.
  Health check: `riak-admin status | grep node_gets_total`
    rising sibling count without resolution → application bug.
```

---

### ⚖️ Comparison Table

| Strategy              | Data Loss              | Complexity    | Coordination         | Best For                           |
| --------------------- | ---------------------- | ------------- | -------------------- | ---------------------------------- |
| Last-Write-Wins       | Yes (silently)         | Low           | None                 | Timestamps, caches, presence       |
| Multi-Value Register  | No (stores all)        | Med           | None (on write)      | Shopping carts, user preferences   |
| CRDT                  | No (for supported ops) | Med           | None                 | Counters, sets, collaborative edit |
| 3-Way Merge           | Minimal                | High          | Need common ancestor | Version control, document editing  |
| Operational Transform | No                     | Very High     | Central sequencer    | Real-time collaborative text       |
| Serializable Txns     | No                     | Low (for app) | Yes (expensive)      | Financial, inventory               |

---

### ⚠️ Common Misconceptions

| Misconception                                                            | Reality                                                                                                                                                                    |
| ------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| LWW is fine because NTP keeps clocks in sync                             | NTP drift can be 100ms+ across nodes. At high write rates, LWW with NTP can silently discard valid writes. Use logical clocks or conditional writes                        |
| Application-level resolution means surfacing conflicts to users          | Application resolution can be entirely automated (e.g., "if both versions increment a counter, sum them") — only truly ambiguous domain conflicts need to surface to users |
| Choosing strong consistency eliminates the need to think about conflicts | Strong consistency (serializable) just moves the conflict to the lock/abort layer — conflicting transactions still occur and must be retried by the application            |

---

### 🚨 Failure Modes & Diagnosis

**Silently Losing Customer Data via LWW**

**Symptom:** Customer reports their order preferences keep resetting to old values.
Analytics shows writes succeed (no errors). Interleaved writes pattern in logs.
Two mobile devices for the same user account writing concurrently.

Cause: Mobile client A (clock slightly behind): writes "theme=dark" at T=100.
Mobile client B (clock ahead): writes "theme=light" at T=101 (concurrent with A).
Server-side LWW: T=101 > T=100 → keeps "theme=light", discards "theme=dark".
Client A's write was valid (user intent) but lost.

**Fix:** (1) Use conditional writes with an optimistic lock version counter:
GET: returns (value="dark", version=5)
PUT: ConditionExpression="version=5" → if another write changed version, retry.
(2) Use CRDT-compatible data (if the preference is a "last-known state" like theme,
LWW is actually correct — the "newer" write is what the user set more recently).
(3) Use vector clocks on the client to detect genuine concurrency vs. ordering.
Root cause often: two devices writing "simultaneously" is actually a device bug
(sync loop that re-writes last-read value unnecessarily).

---

### 🔗 Related Keywords

- `CRDT` — data structures designed to have no conflicts
- `Vector Clock` — the mechanism for detecting whether two writes are truly concurrent
- `Eventual Consistency` — the consistency model that relies on conflict resolution for convergence
- `Lamport Clock` — simpler causal ordering (doesn't detect concurrency, can't fully drive conflict detection)
- `Last-Write-Wins` — the simplest (and most common) conflict resolution strategy

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  CONFLICT RESOLUTION STRATEGIES                          │
│  LWW: highest timestamp wins — simple, lossy             │
│  MVR: store all versions, app resolves — safe, complex   │
│  CRDT: no conflict possible — limited to CRDT ops        │
│  3-Way Merge: use common ancestor — git-style            │
│  OT: transform ops for concurrent text edit             │
│  Detect concurrency: Vector Clocks (no clock sync needed)│
│  Cassandra default: LWW (USING TIMESTAMP)                │
│  Riak default: MVR with siblings                         │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** An e-commerce platform stores user cart data in Cassandra (LWW default). A customer uses two browsers simultaneously: Browser A adds "Item X" (timestamp 1699000100.000), Browser B adds "Item Y" (timestamp 1699000100.001). Each write is to the same cart key but a different field (ItemX: quantity=1, ItemY: quantity=1). Does LWW cause a conflict here? Why or why not? Now consider: both browsers remove "Item Z" at approximately the same timestamp — can LWW here cause a "zombie" return of Item Z?

**Q2.** Git uses 3-way merge with a common ancestor. What happens when the common ancestor is unknown (e.g., a distributed key-value store that doesn't track history)? What algorithm does such a system fall back to, and what data integrity properties does it sacrifice? Name a production system that solves this by maintaining the equivalent of a common ancestor.
