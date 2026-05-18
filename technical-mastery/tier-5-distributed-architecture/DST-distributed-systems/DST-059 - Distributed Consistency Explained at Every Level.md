---
id: DST-059
title: Distributed Consistency Explained at Every Level
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-014, DST-015, DST-028
used_by: DST-078, DST-079
related: DST-014, DST-015, DST-028, DST-058
tags:
  - distributed
  - consistency
  - linearizability
  - eventual-consistency
  - causal-consistency
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 59
permalink: /technical-mastery/distributed-systems/consistency-at-every-level/
---

⚡ TL;DR - Consistency in distributed systems is a
spectrum from linearizability (strongest: reads
always reflect latest write, as if single machine)
to eventual consistency (weakest: converges given
no new writes); intermediate models include causal
consistency (causally related writes ordered),
read-your-writes (you see your own writes), and
monotonic reads (no going back in time); choose
the weakest model that satisfies your use case.

---

### 📋 Entry Metadata

| #059 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Consistency, CAP Theorem, Eventual Consistency | |
| **Used by:** | Multi-Region Consistency, CAP Navigation | |
| **Related:** | Consistency, CAP Theorem, Eventual Consistency, Consensus | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A senior engineer says "we use strong consistency."
A junior engineer says "we use eventual consistency."
Neither can have a useful conversation because both
terms mean different things to different people.
Is "strong consistency" the same as linearizability?
As serializability? As read-your-writes? What are
the actual guarantees, and what are the costs?

Without a precise vocabulary for consistency models,
distributed systems engineers make decisions based
on vague intuitions, implement systems that accidentally
violate consistency guarantees, and debug production
incidents caused by subtle consistency violations
that no one expected.

---

### 📘 Textbook Definition

**Consistency models** define the contract between
a distributed storage system and its clients:
what a client can assume about the values it reads
relative to writes that have occurred.

From strongest to weakest:

| Model | Guarantee | Cost |
|---|---|---|
| **Linearizability** | Every op appears to happen atomically at a point in real time | Highest (requires quorum coordination) |
| **Sequential consistency** | All ops appear in some global sequential order | High (no wall-clock constraint) |
| **Causal consistency** | Causally related ops appear in order; concurrent may differ | Medium |
| **Read-your-writes** | You always read your own writes | Low-medium |
| **Monotonic reads** | Once you read X, you never read a value older than X | Low |
| **Eventual consistency** | Replicas converge with no new writes | Lowest (no real-time guarantee) |

---

### ⏱️ Understand It in 30 Seconds

```
LINEARIZABILITY (strongest):
  User A writes name="Alice" at T=10.
  User B reads at T=11.
  User B MUST see name="Alice".
  Used by: etcd, ZooKeeper, HBase.

CAUSAL CONSISTENCY:
  User A posts "Question".
  User A posts "Answer" (caused by seeing Question).
  Any user who sees "Answer" MUST see "Question".
  Used by: MongoDB (causal sessions), Cosmos DB.

READ-YOUR-WRITES:
  You always see your own writes.
  Other users may not see them yet.
  Used by: social media (your own posts appear
           immediately to you).

EVENTUAL CONSISTENCY (weakest):
  Alice and Bob update the same record on
  different datacenters.
  Eventually they agree. When? Not specified.
  Used by: DNS, Cassandra (default), DynamoDB.
```

---

### 🔩 First Principles Explanation

**EXPLAINING TO DIFFERENT AUDIENCES:**

**To a Junior Engineer:**

```
Think of a whiteboard in a shared office.
When you erase and write a new number,
everyone looking at the board RIGHT NOW
sees the new number immediately.
That's linearizability: one whiteboard, real-time.

Now imagine the whiteboard is photographed and
copies are sent to 3 remote offices.
The copy in office B may arrive 5 seconds after
office A's copy. During those 5 seconds, office B
shows the old number while office A shows the new.
That's eventual consistency: eventually all copies
match, but there's a window of inconsistency.

The trade-off: the "one whiteboard" requires
everyone to go to the same place (expensive,
slow for remote offices). The copies are faster
and more available but temporarily inconsistent.
```

**To a Senior Engineer:**

```
LINEARIZABILITY (Herlihy & Wing, 1990):
  An operation appears to take effect atomically
  at some point between its invocation and response.
  
  WHAT THIS MEANS:
  If write(x=1) completes at T=10, then any read
  that starts at T>10 must return 1 (or a later
  value). Real-time ordering is preserved.

  IMPLEMENTATION:
  Requires quorum reads + quorum writes, or
  leader-only reads (Raft's linearizable reads).
  Cost: P99 latency increase due to coordination.

  WHEN TO USE:
  Financial transactions, leader election,
  configuration distribution, any operation
  where stale reads would cause incorrect behavior.

CAUSAL CONSISTENCY (Lamport, 1978 - logical clocks):
  If A→B (A causally precedes B), then A must be
  visible before B everywhere. Concurrent ops
  may be seen in any order.
  
  IMPLEMENTATION:
  Vector clocks or Lamport timestamps to track
  causal dependencies. Operation not visible until
  all causal dependencies visible.
  
  WHEN TO USE:
  Social feeds (you see the reply after you see
  the original post), collaborative editing
  (you see edits in causal order), chat (reply
  visible after the message it replies to).
```

**To a Staff Engineer:**

```
SERIALIZABILITY vs LINEARIZABILITY:
  These are often confused. They are orthogonal.

  SERIALIZABILITY: transaction property.
  A schedule (interleaving of transactions) is
  serializable if it is equivalent to SOME serial
  execution. No constraint on WHICH serial order.
  
  LINEARIZABILITY: single-operation property.
  Each operation appears to happen at a point
  in REAL TIME (wall clock).

  STRICT SERIALIZABILITY = SERIALIZABLE + LINEARIZABLE
  The most conservative model. Used by:
  Google Spanner, FoundationDB, CockroachDB.

  WHAT CAN GO WRONG:
  Serializable but NOT linearizable:
    T1 reads old value even though T2's write completed
    earlier in real time (but T1 started a snapshot
    before T2 committed).
  
  Linearizable but NOT serializable:
    Single operations are real-time ordered, but
    multi-operation transactions can be interleaved
    in ways that produce non-serializable histories.
    (Unlikely in practice - most systems providing
    linearizable reads also provide serializable txns.)

TO AN ARCHITECT:
  Consistency level is a product decision, not
  just a technical one.
  
  QUESTIONS TO ASK:
  1. What is the cost of a stale read?
     (Financial data: high cost. User profile: low.)
  2. What is the expected write rate and geography?
     (Multi-region writes: linearizability very expensive.)
  3. What consistency model matches user expectations?
     (Search index: eventual OK. Shopping cart:
       read-your-writes minimum.)
  
  DECISION MATRIX:
  Single-region + consistency required: linearizable
  Multi-region + globally consistent: strong (Spanner)
  Multi-region + partition-tolerant: causal
  Multi-region + high availability: eventual
  User-session data: read-your-writes
  Analytics/reporting: eventual (bounded staleness)
```

---

### 🧠 Mental Model / Analogy

> Consistency models are like different versions of
> a shared Google Doc:
> - **Linearizable:** You see every edit instantly,
>   in real time. Your edit appears at the exact
>   millisecond you hit Enter. Requires that everyone
>   goes through the same "master" server.
> - **Causal:** You see edits in logical order. If
>   Alice replied to Bob's comment, you see Bob's
>   comment before Alice's reply - but you might see
>   a comment from Charlie before you see Charlie's
>   earlier edit (they're not causally related to you).
> - **Eventual:** All edits will appear to everyone
>   eventually. For a few seconds after you type,
>   others might not see it. But after a while,
>   everyone converges.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - The intuition:**
In a single-node database: you always read the latest
write. In a distributed database: some reads may
return old values. How old? Depends on the consistency
model. Stronger model = less staleness = more cost.

**Level 2 - The three key models:**
Linearizable (real-time, strongest): if write completed
before your read started, you see it. Causal: you
see writes in causal order (replies after posts).
Eventual: you'll see writes eventually, no guarantee
when.

**Level 3 - The practical hierarchy:**
Read-your-writes: you see your own writes immediately.
Monotonic reads: you never read a value older than
one you've already read (no time-travel). These are
weaker than causal but stronger than eventual.
Most applications can tolerate these without
noticing consistency issues.

**Level 4 - Serializability vs linearizability:**
These are different dimensions. Serializability:
multiple operations in a transaction appear atomic
as a group. Linearizability: a single operation
appears atomic at a real-time point. Databases
often provide one or the other. Spanner provides
both (strict serializability = external consistency).

**Level 5 - The engineering decision:**
Choosing consistency level is a product decision.
What is the cost of showing a user stale data?
For a bank balance: very high. For a tweet like count:
low. For a product recommendation: near-zero. The
consistency model should match the cost of violation.
Using strong consistency everywhere is over-engineering.
Using eventual consistency everywhere is risky.

---

### 💻 Code Example

**Consistency Violations in Practice**

```python
# BAD: Assuming eventual consistent read reflects latest write
# (Lost Update: read-modify-write with eventual consistency)

class BadProfileUpdater:
    def __init__(self, db):
        self.db = db

    def add_achievement(
        self, user_id: str, achievement: str
    ) -> None:
        # Read from eventual consistent replica:
        profile = self.db.get(user_id)
        # Profile may be stale (replica lag)!
        
        achievements = profile.get("achievements", [])
        achievements.append(achievement)
        
        # Write to primary:
        self.db.set(user_id, {"achievements": achievements})
        
        # PROBLEM: Two concurrent calls to add_achievement
        # both read the same stale achievements list.
        # First write: ["badge_1"]
        # Second write: ["badge_1"] (read stale, overwrites!)
        # Result: achievement lost.
```

```python
# GOOD: Use compare-and-swap or dedicated operation
# that works under eventual consistency

class GoodProfileUpdater:
    def __init__(self, db):
        self.db = db

    def add_achievement(
        self, user_id: str, achievement: str
    ) -> None:
        # Option 1: Atomic set-add operation
        # (If DB supports it: MongoDB $addToSet,
        #  Redis SADD, DynamoDB SET ADD)
        self.db.add_to_set(
            key=user_id,
            field="achievements",
            value=achievement
        )
        # DB applies atomically: no lost updates.

    def add_achievement_with_cas(
        self, user_id: str, achievement: str
    ) -> None:
        # Option 2: Compare-and-swap retry loop
        # (for DBs that don't support atomic set-add)
        max_retries = 5
        for attempt in range(max_retries):
            # Read from STRONG consistent primary:
            profile, version = self.db.get_versioned(
                user_id,
                consistency="strong"  # Not replica
            )
            achievements = profile.get("achievements", [])
            
            if achievement not in achievements:
                achievements.append(achievement)
            
            # Conditional write: only if version unchanged
            try:
                self.db.conditional_put(
                    key=user_id,
                    value={"achievements": achievements},
                    expected_version=version
                )
                return  # Success
            except VersionConflictError:
                # Another writer updated concurrently.
                # Retry with fresh read.
                continue

        raise MaxRetriesExceededError(
            f"Could not add achievement after "
            f"{max_retries} retries"
        )
```

---

### ⚖️ Comparison Table

| Model | Stale Read? | Cross-Client? | Cross-Region? | Use Case |
|---|---|---|---|---|
| **Linearizable** | Never | Yes | Very expensive | Bank balance, leader election |
| **Sequential** | Never (but may be reordered) | Yes | Expensive | Coordination services |
| **Causal** | Maybe (concurrent ops) | Yes (causal deps) | Moderate cost | Social feeds, messaging |
| **Read-your-writes** | Only your own | No (others may be stale) | Possible | User profiles, settings |
| **Monotonic reads** | May be stale (never backwards) | No | Low cost | Any read-heavy workload |
| **Eventual** | Yes (until convergence) | No | Minimal cost | DNS, caches, analytics |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Eventual consistency means data is always stale" | Eventual consistency guarantees convergence in the absence of new writes. In practice, most replicas converge within milliseconds to seconds. The staleness window depends on replication lag, not an inherent flaw. |
| "Strong consistency is always safer" | Strong consistency eliminates stale reads but introduces availability and latency costs. A strongly consistent system that is unavailable (e.g., quorum not achievable during partition) is worse than an eventually consistent system that serves slightly stale data. Choose based on use case. |
| "Cassandra is eventually consistent" | Cassandra is configurable. With quorum reads and quorum writes (QUORUM/QUORUM), Cassandra provides strong consistency (at least in practice - not linearizable, but read-your-writes). With ONE consistency level: eventually consistent. The consistency level is per-operation, not a global database property. |
| "Consistency and durability are the same" | Durability: once a write is confirmed, it will survive crashes (fsync, WAL). Consistency: what version of data is visible to readers. A database can be durable (data not lost) but eventually consistent (replicas temporarily diverge). They are orthogonal ACID/distributed system properties. |

---

### 🚨 Failure Modes & Diagnosis

**Stale Read Causing Business Logic Bug**

**Symptom:** Users report duplicate transactions.
Two orders were created for the same item, but the
inventory check showed quantity > 0 for both.
Payment system sees the total correctly, but warehouse
received two fulfillment requests.

**Root Cause:** Inventory read was served from an
eventually consistent replica. Both requests read
quantity=1, both decremented, both placed orders.
The first decrement had not yet propagated to the
replica serving the second request.

**Diagnosis:**
```python
# Check which consistency level inventory reads use:
# (This is the code that needs to change)

def check_inventory_bad(item_id: str) -> int:
    # BAD: reads from any replica (eventual consistency)
    return db.get(item_id, consistency="eventual")

def check_inventory_good(item_id: str) -> int:
    # GOOD: reads from leader/quorum (strong consistency)
    return db.get(item_id, consistency="strong")

# DynamoDB: use ConsistentRead=True for inventory
# Cassandra: use QUORUM consistency for inventory reads
# MongoDB: use readConcern: "linearizable" or 
#          read from primary

# For ordering: use compare-and-swap:
def reserve_inventory(item_id: str, qty: int) -> bool:
    """Reserve qty items atomically. Returns False if OOS."""
    # Atomic conditional update:
    result = db.update_if(
        key=item_id,
        condition="quantity >= :qty",  # Check before update
        update="quantity = quantity - :qty",  # Atomic decrement
        values={":qty": qty}
    )
    return result.updated
    # This is atomic: no race condition possible.
    # If two requests run simultaneously, one wins,
    # the other gets False (condition fails).
```

**Fix:** Use strong consistent reads for any
read-modify-write that has financial or inventory
consequences. Or: use atomic conditional updates
that don't require reading first.

---

### 🔗 Related Keywords

**Prerequisites:** `Consistency` (DST-014),
`CAP Theorem` (DST-015),
`Eventual Consistency and BASE` (DST-028)

**Builds On This:** `Multi-Region Consistency` (DST-078),
`CAP Theorem Navigation` (DST-079)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ STRONGEST  │ Linearizable: real-time, quorum needed     │
│            │ Sequential: serial order, no wall-clock   │
│            │ Causal: causal order preserved            │
│            │ Read-your-writes: see own writes          │
│            │ Monotonic reads: no backward in time      │
│ WEAKEST    │ Eventual: converge eventually             │
├────────────┼────────────────────────────────────────────┤
│ KEY RULE   │ Weakest model that meets use case needs   │
│ COST       │ Stronger = higher latency + lower avail   │
├────────────┼────────────────────────────────────────────┤
│ SERIALIZABLE│ Transaction property (ACID "I")          │
│ vs LINEAR  │ Linearizable: single-op real-time         │
│            │ Strict serial = both (Spanner, CRDB)      │
├────────────┼────────────────────────────────────────────┤
│ ONE-LINER  │ "Consistency = how stale is the read?     │
│            │  Stronger = never stale = more expensive" │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

The principle of "choose the weakest consistency
that satisfies your requirements" is an application
of a broader engineering principle: make the weakest
possible assumptions. The weaker your assumptions,
the more robust your system. If your code assumes
linearizability when it only needs read-your-writes,
you are over-constrained: your system cannot use
eventually consistent replicas (faster, cheaper)
even when they would be correct. This principle
appears in: API design (expose minimal interfaces),
concurrency (use the weakest synchronization primitive
that is correct - don't use a mutex when a concurrent
map suffices), data modeling (don't normalize more
than needed). In distributed systems: always ask
"what is the weakest consistency guarantee my use
case actually needs?" and implement exactly that.

---

### 💡 The Surprising Truth

The consistency model that most engineers intuitively
expect - "I should see any data that has been written
before my read started" (linearizability) - is
actually the MOST EXPENSIVE and least commonly
provided model in distributed databases. Most
distributed databases marketed as "strongly consistent"
provide something weaker: read-committed or snapshot
isolation (serializable but not linearizable). True
linearizability requires real-time ordering of ALL
operations across ALL nodes, which requires
coordination on every operation. Even Google Spanner -
often cited as "the world's most consistent database"
- took years and special hardware (TrueTime GPS clocks)
to achieve strict serializability at global scale.
The lesson: before requiring "strong consistency,"
define precisely what model you need - you often
find causal consistency or read-your-writes is
sufficient at 10x less cost.

---

### ✅ Mastery Checklist

1. [EXPLAIN] Explain linearizability to a junior
   engineer using a concrete analogy. Then explain
   why it is expensive in a multi-region system.
2. [CHOOSE] For each: bank balance check, social
   media like count, user session token, DNS lookup,
   order inventory check - choose the consistency
   model and justify.
3. [IDENTIFY] Describe a read-modify-write scenario
   that would produce a lost update under eventual
   consistency. Write the correct fix using either
   atomic operations or compare-and-swap.
4. [COMPARE] Serializability vs linearizability:
   give a concrete example of a history that is
   serializable but NOT linearizable.
5. [DESIGN] A multi-region e-commerce system needs:
   product catalog reads (fast, any region), cart
   contents (user should see their own adds), and
   payment confirmations (must be globally consistent).
   Assign a consistency model to each and justify.
