---
id: DST-028
title: Eventual Consistency and BASE Properties
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-014, DST-016, DST-026, DST-027
used_by: DST-031, DST-032
related: DST-014, DST-016, DST-027, DST-029
tags:
  - distributed
  - consistency
  - foundational
  - BASE
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 28
permalink: /technical-mastery/distributed-systems/eventual-consistency/
---

⚡ TL;DR - Eventual consistency guarantees that if no
new updates are made to a data item, all replicas will
converge to the same value; BASE (Basically Available,
Soft state, Eventually consistent) is the design
philosophy of systems that prioritize availability and
partition tolerance over immediate consistency, and
"stale, not wrong" is the key distinction that
determines when it is safe to use.

---

### 📋 Entry Metadata

| #028 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Consistency, CAP Theorem, Replication Lag, Read/Write Quorums | |
| **Used by:** | Vector Clocks, Lamport Timestamps | |
| **Related:** | Consistency, CAP Theorem, Quorums, Linearizability | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You build a social network. Every post, like, and view
count is stored in a strongly consistent database. Every
write blocks until all replicas confirm. At 10 users,
this works fine. At 10 million users, the database
cannot keep up. Every like on a viral post (10,000 per
second) requires a globally consistent write. The system
becomes unavailable. You could shard, but cross-shard
consistency still limits throughput. The fundamental
problem: strong consistency is expensive and throughput-
limiting at global scale.

**THE INSIGHT:**
Not all data requires strong consistency. A like count
does not need to be exact to the millisecond - being
accurate within a few seconds is acceptable. A shopping
cart does not need to be visible globally instantly -
users only view their own cart. Eventual consistency
defines the explicit, weaker guarantee that some systems
legitimately provide, enabling them to scale to
throughput levels that strong consistency cannot reach.

---

### 📘 Textbook Definition

**Eventual consistency** is a consistency model that
guarantees that, if no new updates are applied to a
data item, all replicas will eventually converge to
the same value. It makes no guarantee about when
convergence occurs or what intermediate states are
visible.

**BASE** is an acronym contrasting with ACID:
- **B**asically **A**vailable: the system guarantees
  availability (responses are returned) even during
  partial failures; some data may be stale
- **S**oft state: the system's state may change over
  time even without new input (due to replication
  catching up and convergence)
- **E**ventually consistent: the system will converge
  to a consistent state after updates stop

BASE systems accept temporary inconsistency in exchange
for higher availability, higher throughput, and
partition tolerance.

---

### ⏱️ Understand It in 30 Seconds

**The contract:**
```
STRONG CONSISTENCY (ACID):
  Write → immediate → all nodes agree → read sees latest
  Cost: latency (wait for all), lower throughput

EVENTUAL CONSISTENCY (BASE):
  Write → primary → async propagation → eventually all
    agree
  Cost: stale reads during propagation window
  Benefit: lower write latency, higher throughput, AP
    behavior
```

**"Stale, not wrong":**
```
Acceptable (eventually consistent):
  - Like counts (off by N for a few seconds)
  - User profiles (stale for <1 second)
  - Shopping carts (user-scoped, self-consistent)
  - DNS records (propagates over minutes - by design)

Not acceptable:
  - Account balance (stale = potential overdraft)
  - Inventory (stale = oversell)
  - Authentication tokens (stale = security bypass)
```

---

### 🔩 First Principles Explanation

**WHY EVENTUAL CONSISTENCY EXISTS:**

From CAP theorem (DST-016): during a network partition,
a system must choose between C (consistency) and A
(availability). AP systems choose availability - they
continue serving requests even when nodes cannot
communicate, accepting that different nodes may
temporarily return different values. The guarantee
is convergence after the partition heals.

Even without partitions, high write throughput to
globally distributed nodes requires asynchronous
replication (DST-026). Asynchronous replication inherently
means followers lag behind the leader. During this lag,
reads from different followers may return different values.
Eventual consistency names and formalizes this reality.

**THE SPECTRUM OF EVENTUAL CONSISTENCY:**

"Eventual consistency" is not a single model but a
spectrum of guarantees. From weakest to strongest:

```
Eventual Consistency (weakest)
  └─ All replicas converge. No timing guarantee.
     No ordering guarantee during convergence.

Monotonic Read Consistency
  └─ Once you read value V, future reads return
     V or something newer. Never go backwards.
     Not globally consistent, but no regressions.

Read-Your-Writes Consistency
  └─ Your own writes are always visible to your
     future reads (from any node). Other users
     may not yet see them.

Session Consistency
  └─ Read-your-writes + monotonic reads within
     a session (same client). Cross-session:
     eventually consistent.

Causal Consistency
  └─ Operations related by cause-and-effect
     appear in order everywhere. Causally
     independent operations may appear in
     different orders.

Sequential Consistency
  └─ All operations appear in the same order
     everywhere (though not necessarily real-time).

Linearizability (strongest - NOT eventual)
  └─ Every operation appears instantaneous and
     in real-time order. Requires coordination.
```

---

### 🧠 Mental Model / Analogy

> DNS is the classic example of eventual consistency
> that every engineer has already experienced. When you
> change a DNS record, the change propagates through
> the global DNS hierarchy over minutes to 48 hours.
> During propagation, different resolvers return different
> IP addresses for the same hostname. After propagation
> completes, all resolvers agree. Nobody considers DNS
> "broken" because of this - it is the designed behavior.
> The question is whether your application data has the
> same tolerance for temporary inconsistency.

> Another analogy: stock price tickers on news websites
> show "15-minute delayed" quotes. The data is stale by
> design. It is still useful for most readers. For trading
> decisions, you need the real-time feed (strongly
> consistent). The application determines which version
> of consistency is required, not the database.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is:**
Eventually consistent means: after you stop writing,
all copies of the data will eventually agree. During
writes, copies may temporarily disagree. No errors,
no notifications - just temporary staleness. Safe to
use when your application can tolerate reading slightly
old data.

**Level 2 - When to use it:**
Use eventual consistency for: user-generated content
(posts, likes, views), recommendation engines, activity
feeds, shopping cart contents, preferences and settings
(where 1-second staleness is imperceptible), and any
data with high write volume where strong consistency
would create a throughput bottleneck.

Do NOT use it for: financial balances, inventory counts,
authentication credentials, access control lists, or
any data where stale = incorrect business logic.

**Level 3 - How it manifests:**
Cassandra with `ConsistencyLevel.ONE` provides eventual
consistency. A write to one replica succeeds immediately;
other replicas catch up asynchronously. If two clients
write to the same key on different replicas simultaneously,
both writes are accepted. The conflict is resolved
by last-write-wins (LWW) using timestamps. The "loser"
write is silently discarded. Applications using Cassandra
ONE must be designed for this conflict resolution
behavior.

**Level 4 - The conflict resolution problem:**
The key engineering challenge with eventual consistency
is defining what "convergence" means when concurrent
writes occur. Options:

| Strategy | Mechanism | Risk |
|---|---|---|
| Last-Write-Wins (LWW) | Highest timestamp wins | Clock skew can discard newer writes |
| Multi-Value / Siblings | Store all conflicting versions, expose to app | App complexity |
| CRDTs | Data structures that merge automatically | Limited to specific operations |
| Custom merge | App-defined merge function | Highest complexity, most control |

LWW is the default in many systems (Cassandra, DynamoDB).
Its failure mode: if clocks are not synchronized (within
a few milliseconds), writes with "earlier" timestamps
that were logically newer get discarded. NTP synchronization
is mandatory for LWW correctness.

**Level 5 - Vector clocks and causal ordering:**
To detect whether two writes are concurrent (conflict)
vs causally related (one came after the other), you
need a mechanism beyond wall-clock timestamps. Vector
clocks (one counter per node, incremented on write,
merged on read) capture causal relationships. If write
A happened before write B, B's vector clock will
dominate A's (every counter >= A, at least one >).
If they are concurrent, neither dominates. Amazon
Dynamo and Riak use vector clocks for this detection.
Causal consistency with vector clocks is a middle ground:
stronger than basic eventual consistency, cheaper than
linearizability.

---

### ⚙️ Why It Holds True

**BASE PROPERTIES IN PRACTICE:**

```
B - BASICALLY AVAILABLE:
  System returns responses, possibly degraded.
  Node failure → other nodes still serve requests.
  Partition → both sides serve requests (stale OK).
  Not: "the system is mostly available" (vague).
  Precisely: responses are guaranteed, content may vary.

S - SOFT STATE:
  System state can change without new client input.
  Replication catching up: value changes on replica
    without any client write.
  TTL expiry: cache entries disappear automatically.
  Gossip convergence: node membership changes propagate.
  Soft state is the consequence of convergence processes.

E - EVENTUALLY CONSISTENT:
  If writes stop, all replicas will agree.
  "Eventually" is undefined: could be milliseconds
    (normal) or hours (during severe partition).
  Not a hard SLA - a structural guarantee.
```

**CONVERGENCE MECHANISMS:**

```
┌────────────────────────────────────────────────────────┐
│ Anti-entropy:                                          │
│   Replicas periodically exchange summaries            │
│   (Merkle trees) to detect and repair divergence.     │
│   Cassandra runs anti-entropy repairs periodically.   │
│                                                        │
│ Read repair:                                           │
│   On quorum read, coordinator detects which replica   │
│   has stale data and sends the latest value to it.    │
│   Repairs drift on read path without explicit job.    │
│                                                        │
│ Hinted handoff:                                        │
│   Write to temporarily unavailable node is stored     │
│   on coordinator as a "hint." When node recovers,     │
│   coordinator replays the hint. Prevents permanent    │
│   divergence from temporary unavailability.           │
└────────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Designing for Eventual Consistency Correctly**

```python
# BAD: Assuming immediate consistency in an EC system
# Counter that requires exact accuracy

class LikeCounterBroken:
    def __init__(self, cassandra_session):
        self.db = cassandra_session

    def add_like(self, post_id: str, user_id: str):
        # Read current count, increment, write back
        # (read-modify-write in an EC system = WRONG)
        result = self.db.execute(
            "SELECT likes FROM posts WHERE id=%s",
            (post_id,)
        )
        current_likes = result.one().likes
        self.db.execute(
            "UPDATE posts SET likes=%s WHERE id=%s",
            (current_likes + 1, post_id)
            # TWO concurrent writers both read 5,
            # both write 6. One like is lost.
        )
```

```python
# GOOD: Use a counter data type designed for
# eventual consistency (CRDT counter)

class LikeCounterCorrect:
    def __init__(self, cassandra_session):
        self.db = cassandra_session

    def add_like(self, post_id: str, user_id: str):
        # Cassandra counter: each node tracks its own
        # increment independently, sums on read.
        # No read-before-write needed.
        self.db.execute(
            "UPDATE post_likes SET likes = likes + 1 "
            "WHERE post_id=%s",
            (post_id,)
            # Each node increments its own delta.
            # No conflict possible - deltas merge.
        )

    def get_likes(self, post_id: str) -> int:
        result = self.db.execute(
            "SELECT likes FROM post_likes WHERE id=%s",
            (post_id,)
        )
        # Returns sum of all replica deltas.
        # May not include the last N milliseconds
        # of likes from other replicas (eventually
        # consistent, not exact to the millisecond).
        return result.one().likes
```

**Testing for Eventual Consistency Behavior**

```python
# Test: verify eventual convergence after partition
def test_eventual_convergence():
    # Write to replica-A (simulated partition)
    replica_a.write("key", "value-1", ts=1000)

    # Write to replica-B during partition
    replica_b.write("key", "value-2", ts=2000)

    # Repair: resolve conflict via LWW
    merged = last_write_wins(
        replica_a.read("key"),   # ts=1000
        replica_b.read("key")    # ts=2000
    )
    assert merged.value == "value-2"  # LWW: ts=2000 wins
    assert merged.ts == 2000

    # After convergence: both replicas agree
    replica_a.apply(merged)
    replica_b.apply(merged)
    assert replica_a.read("key") == replica_b.read("key")
```

---

### ⚖️ Comparison Table

| Property | ACID | BASE |
|---|---|---|
| **Consistency** | Strong (immediate) | Eventual (convergent) |
| **Availability** | May reject during conflict | Always responds |
| **Partition behavior** | CP: reject | AP: serve stale |
| **Conflict handling** | Serialization/locking | LWW or CRDTs |
| **Write throughput** | Limited by consensus | High |
| **Read freshness** | Always current | May be stale |
| **Use case** | Financial, inventory | Feeds, preferences, counts |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Eventual consistency means the data might be wrong" | Data is stale (temporarily older than the latest write), not wrong (not corrupted). The difference matters: stale = tolerable in many cases; wrong = never tolerable. |
| "BASE is inferior to ACID" | They are different trade-offs. BASE enables scale that ACID cannot achieve. The choice depends on business requirements. Instagram uses BASE for likes. Banks use ACID for balances. Both are correct for their use cases. |
| "Eventual consistency resolves all conflicts" | LWW can lose valid concurrent writes. CRDTs only apply to specific data structures. "Eventual" just means replicas converge - not that every write survives. |
| "Cassandra is eventually consistent" | Cassandra is tunable. QUORUM consistency is strongly consistent (for practical purposes). ONE is eventually consistent. The system's consistency is determined by the configuration, not the product. |

---

### 🚨 Failure Modes & Diagnosis

**Lost Updates in an Eventually Consistent System**

**Symptom:** Two users simultaneously update the same
record. Only one update survives. The other update is
silently discarded. Users report "the app ignored my
changes."

**Root Cause:** Last-Write-Wins conflict resolution.
Two writes with different timestamps on different replicas.
Replica with higher timestamp wins during convergence.
The "losing" write never appears.

**Detection:**
```python
# Detect via change data capture or version vectors:
# Cassandra: if using lightweight transactions (LWT),
# detect conflict explicitly:

result = session.execute("""
    UPDATE users
    SET name = %s
    WHERE id = %s
    IF name = %s
""", (new_name, user_id, expected_current_name))

if not result.one().applied:
    # Another write happened between read and write
    # Surface conflict to user rather than silently
    # discarding one update
    raise ConflictError(
        "Another update occurred simultaneously. "
        "Please reload and retry."
    )
```

**Fix:** Use conditional writes (CAS operations) for
data that cannot use LWW. Accept that eventually
consistent systems with LWW have a conflict probability
proportional to the concurrent write rate.

---

### 🔗 Related Keywords

**Prerequisites:**
- `Consistency` (DST-014), `CAP Theorem` (DST-016)
- `Replication Lag` (DST-026), `Read/Write Quorums` (DST-027)

**Builds On This:**
- `Vector Clocks` (DST-031), `Lamport Timestamps` (DST-032)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ CONTRACT   │ If writes stop, all replicas converge      │
├────────────┼────────────────────────────────────────────┤
│ STALE vs   │ STALE = old but correct                    │
│ WRONG      │ WRONG = incorrect business logic           │
│            │ Only stale is acceptable in EC systems     │
├────────────┼────────────────────────────────────────────┤
│ BASE       │ Basically Available (serve during fault)   │
│            │ Soft state (changes during convergence)    │
│            │ Eventually consistent (converges)          │
├────────────┼────────────────────────────────────────────┤
│ CONVERGENCE│ Anti-entropy repair, read repair,          │
│            │ hinted handoff                             │
├────────────┼────────────────────────────────────────────┤
│ CONFLICT   │ LWW (most common), CRDTs, custom merge     │
├────────────┼────────────────────────────────────────────┤
│ ONE-LINER  │ "Eventual = stale, not wrong; design       │
│            │  your reads around that contract."         │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

BASE is not a database implementation detail - it is a
system design philosophy. Any asynchronous data flow
creates eventual consistency: message queues, event
streams, search indexes, caches, CDNs. The BASE contract
applies to all of them. When designing any system with
asynchronous data propagation, explicitly specify: What
is the convergence time SLO? What is the conflict
resolution strategy? Which reads require real-time
data vs which tolerate staleness? Answering these
questions upfront prevents the class of bugs where
developers implicitly assume strong consistency in
a system that provides eventual consistency.

---

### 💡 The Surprising Truth

Werner Vogels (CTO, Amazon) published "Eventually
Consistent" in 2008 and described how Amazon DynamoDB's
design philosophy emerged from a specific failure
incident. In 2004, Amazon's shopping cart had a bug:
the database rejected write operations during network
partitions, making the cart appear empty. The cost of
showing an empty cart (lost sales) exceeded the cost
of showing slightly stale cart contents. This is the
origin of DynamoDB's AP design: preserve the shopping
cart, even if the contents are slightly stale. "Never
lose a customer's cart" became a design requirement
that BASE satisfies and ACID (with CP behavior) does not.
The business constraint - not the technology - drove
the consistency model.

---

### ✅ Mastery Checklist

1. [CLASSIFY] For each data type (user balance, profile
   name, activity feed, authentication token, like count),
   determine whether eventual consistency is acceptable
   and justify why.
2. [IMPLEMENT] Write a Cassandra counter increment that
   is safe under eventual consistency, and explain why
   a read-modify-write is not safe in the same context.
3. [DESIGN] Specify the convergence mechanism (anti-
   entropy, read repair, or hinted handoff) most
   appropriate for each of three scenarios: 100ms lag,
   5-minute partition, node offline for 12 hours.
4. [DEBUG] Given a symptom of "user B's write silently
   lost while user A's survived," diagnose whether LWW,
   a clock skew issue, or a network partition is
   the root cause.
5. [EXPLAIN] The difference between "stale" and "wrong"
   data in an eventually consistent system, with a
   concrete production example of each.
