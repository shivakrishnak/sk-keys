---
id: DST-014
title: Consistency
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★☆☆
depends_on: DST-009, DST-012, DST-014
used_by: DST-016, DST-028, DST-029, DST-036
related: DST-012, DST-015, DST-016, DST-028, DST-029
tags:
  - distributed
  - data
  - consistency
  - foundational
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 14
permalink: /technical-mastery/distributed-systems/consistency/
---

⚡ TL;DR - Consistency in distributed systems is a spectrum
of guarantees about what value a read returns relative to
recent writes; it ranges from linearizability (every read
sees the most recent write globally) to eventual consistency
(reads eventually see the latest write, but may see stale
data now).

---

### 📋 Entry Metadata

| #014 | Category: Distributed Systems | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Message Passing, Replication, CAP Theorem | |
| **Used by:** | CAP Theorem, Eventual Consistency, Linearizability | |
| **Related:** | Replication, Availability, CAP Theorem, Eventual Consistency, Linearizability | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT (no consistency guarantees):**
A distributed bank has three replicas of account data. A
customer deposits $1,000 at 9:00am. At 9:01am, they call
customer support to confirm the deposit. The support agent
queries a replica that has not yet received the write. The
agent says "we show no deposit." The customer is furious.
At 9:05am, all replicas have the data. The deposit was always
safe - but the system appeared inconsistent to the user.

**THE CORE TENSION:**
A system could provide perfect consistency (every replica
always agrees) but this requires coordination on every
operation - expensive, slow, and unavailable during
partitions. Or a system could have no consistency guarantees
(each replica does whatever) but then reads are useless
for anything requiring correct current state. All real systems
are somewhere between these extremes, and the choice has
direct business consequences.

---

### 📘 Textbook Definition

In distributed systems, **consistency** defines what value
a read operation is guaranteed to return given the history
of prior write operations. Unlike the "C" in ACID (which
means application-level invariants hold), the "C" in
distributed systems refers to the **consistency model** -
the contract between the storage system and the application
about what reads can return. The consistency spectrum
ranges from **strong consistency** (reads always return
the most recent write) to **weak consistency** (no guarantee
of what a read returns) with many formal models in between:
linearizability, sequential consistency, causal consistency,
read-your-writes, monotonic reads, and eventual consistency.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Consistency in distributed systems is a promise about whether
what you read is up to date - and different systems make
different (weaker or stronger) promises.

**One analogy:**
> You and your partner share a bank account. You deposit
> $1,000 at an ATM and immediately call your partner to
> say "I deposited $1,000, you can use it now."
> **Strong consistency**: your partner's ATM shows $1,000
> immediately. Every ATM always shows the latest state.
> **Eventual consistency**: your partner's ATM might show
> the old balance for a few seconds or minutes. Eventually
> it will show $1,000.
> The difference: convenience and correctness guarantees.
> The cost of strong consistency: ATMs must coordinate
> on every transaction, adding latency.

**One insight:**
Consistency is not binary. There is a precise mathematical
model for every level on the spectrum. Choosing "eventual
consistency" is not vague - it is a precise guarantee with
defined behavior. The same is true for linearizability,
causal consistency, etc. Knowing where your system sits on
this spectrum, and where it needs to sit for correct
application behavior, is a critical engineering decision.

---

### 🔩 First Principles Explanation

**THE CONSISTENCY MODEL HIERARCHY:**

```
┌────────────────────────────────────────────────────────┐
│            CONSISTENCY SPECTRUM                        │
│            (strongest → weakest)                       │
│                                                        │
│  Linearizability (Strict Consistency)                  │
│  └── Reads see the most recent write globally          │
│      Appears as if there is only one copy of data.    │
│      Expensive: requires coordination for every op.   │
│                    │                                   │
│  Sequential Consistency                                │
│  └── All nodes see operations in the same order,      │
│      but that order may not match real-world time.    │
│                    │                                   │
│  Causal Consistency                                    │
│  └── Causally related operations are seen in order.  │
│      Concurrent operations may appear in any order.  │
│                    │                                   │
│  Read-Your-Writes (Session Consistency)               │
│  └── A client always sees its own writes.             │
│      Other clients may see stale data.               │
│                    │                                   │
│  Monotonic Reads                                       │
│  └── A client never sees data older than what it      │
│      previously read. No "going back in time."        │
│                    │                                   │
│  Eventual Consistency                                  │
│  └── If no new writes occur, all replicas converge   │
│      to the same value. No timing guarantee.          │
└────────────────────────────────────────────────────────┘
```

**WHY THE TRADE-OFF IS REAL:**

For linearizability, every read must either:
(a) return data from the node that received the last write,
    meaning routing to the primary on every read (expensive),
OR
(b) coordinate across replicas before responding, ensuring
    no other write has occurred since the last observed write.

Both options add latency or reduce availability. The stronger
the consistency guarantee, the more coordination required.
Coordination requires network round-trips. Under partition,
coordination cannot complete. This is the CAP theorem in
practical terms.

**THE COST HIERARCHY:**

| Model | Latency Cost | Availability During Partition |
|---|---|---|
| Linearizability | Highest (coordination on every op) | Lowest (requires quorum) |
| Sequential | High | Low |
| Causal | Medium | Medium |
| Eventual | Lowest | Highest |

---

### 🧠 Mental Model / Analogy

> Imagine a global news headline. In a strongly consistent
> system, the moment a headline changes, every reader on
> earth sees the new headline simultaneously (impossible
> due to speed of light, which is why pure strong
> consistency has a physical cost). In an eventually
> consistent system, the headline change propagates like
> a radio wave: closest readers see it first, then the
> wave spreads globally. Eventually everyone sees the
> same headline, but some readers saw the old headline
> for a few seconds or minutes.

**The mapping:**
- "Headline change" - write operation
- "All readers" - read operations from any node
- "Wave propagating" - replication propagating the write

**Where the analogy is exact:** Eventually consistent systems
literally have a propagation delay proportional to network
latency between replicas. The further geographically
separated the replicas, the longer the window of
inconsistency.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Consistency answers: "When I write something to the database,
can I immediately read it back?" Strong consistency: yes,
always. Eventual consistency: it will be readable soon, but
maybe not in the very next millisecond.

**Level 2 - How to use it (junior developer):**
Most databases let you choose consistency per operation.
In Cassandra: CONSISTENCY QUORUM for strong reads, CONSISTENCY
ONE for fast (possibly stale) reads. In DynamoDB: strong
consistency for financial data, eventual consistency for
feed/recommendation data where slight staleness is acceptable.
Know your data's consistency requirement before choosing.

**Level 3 - How it works (mid-level engineer):**
Linearizability is implemented by routing all reads and writes
through the same leader, or by requiring quorum (W + R > N)
acknowledgment. Eventual consistency is implemented by
asynchronous replication: write to one node and replicate
in the background. The gap between when the write is
committed at the leader and when it is applied at all
replicas is the "inconsistency window."

**Level 4 - Why it was designed this way (senior/staff):**
The formal definition of linearizability (Herlihy & Wing,
1990) was created to reason about the correctness of concurrent
programs. Its application to distributed databases gives
us a precise way to state "this distributed database behaves
as if it were a single node." This is the highest useful
consistency guarantee - any stronger guarantee (like strict
serializability) adds transaction ordering on top, which
is a separate concern.

**Level 5 - Mastery (distinguished engineer):**
Kyle Kingsbury's Jepsen project (2012-present) tests
real databases' consistency guarantees against their
documentation claims. Many databases that claimed linearizability
or sequential consistency were found to violate those guarantees
under network partitions or process pauses. The lesson:
consistency guarantees are hard to implement correctly, and
the correctness of a system's consistency model must be
verified by testing under adversarial conditions, not just
assumed from documentation.

---

### ⚙️ Why It Holds True

**THE SYNCHRONY CONSTRAINT:**

Linearizability requires that a read operation's result
reflects the state of the system at some point between
the read's start and end. For a globally replicated system,
this means either:

1. All writes are applied before any read is served
   (sequential write propagation - very slow), or

2. Before serving a read, the serving node confirms with
   a quorum of other nodes that no unobserved write exists
   (coordination on every read), or

3. All reads are served by the same node that processes
   all writes (single-primary reads)

None of these can be achieved during a partition. Under a
partition, a node may have received writes that the other
side has not seen. Serving a read from either side risks
returning a value that is not the globally latest. This
is why linearizability is a CP property: it requires
coordination, which requires availability of the majority.

---

### 🗺️ System Design Implications

**CHOOSING THE CONSISTENCY LEVEL:**

The correct consistency model is determined by asking:
"What is the business consequence of a stale read?"

```
FINANCIAL SYSTEM:
  What happens if account balance is stale?
  → User sees $100 but account is actually $0
  → Can double-spend / overdraft
  → Requires: Linearizability or Serializability

SOCIAL MEDIA FEED:
  What happens if feed is 2 seconds stale?
  → User sees slightly old post ordering
  → No business harm
  → Fine with: Eventual Consistency

INVENTORY SYSTEM:
  What happens if inventory count is stale?
  → User can order item that is out of stock
  → Rare but costly (customer order to cancel)
  → Requires: Read-Your-Writes at minimum
  → Probably: Serializability for stock decrements

USER PREFERENCES (language, theme):
  What happens if preference is stale?
  → User sees English instead of Spanish for ~1 second
  → No harm
  → Fine with: Eventual Consistency
```

---

### 💻 Code Example

**Consistency Level Selection (Wrong vs Right)**

```python
# BAD: Use eventual consistency for financial operation
from cassandra.cluster import Cluster
from cassandra.policies import ConsistencyLevel

session = Cluster().connect('bank')
session.default_consistency_level = ConsistencyLevel.ONE

def get_balance(account_id: str) -> Decimal:
    # ConsistencyLevel.ONE = read from any single replica
    # That replica may be seconds behind primary
    row = session.execute(
        "SELECT balance FROM accounts WHERE id=%s",
        [account_id]
    ).one()
    return row.balance

# Problem: Read from stale replica.
# User sees $500. They initiate $400 transfer.
# Actual balance is $100 (from a concurrent write).
# Transfer is approved based on stale read.
# Account goes to -$300.
```

```python
# GOOD: Use quorum consistency for financial reads/writes
from cassandra.cluster import Cluster
from cassandra.policies import ConsistencyLevel

session = Cluster().connect('bank')

def get_balance(account_id: str) -> Decimal:
    # QUORUM = read from majority of replicas
    # Returns most recent committed value
    row = session.execute(
        "SELECT balance FROM accounts WHERE id=%s",
        [account_id],
        timeout=2.0,
        # Raises if cannot achieve quorum
        consistency_level=ConsistencyLevel.QUORUM
    ).one()
    return row.balance

def update_balance(
    account_id: str,
    delta: Decimal
) -> None:
    # QUORUM write: majority must confirm
    # before operation is considered committed
    session.execute(
        "UPDATE accounts SET balance=balance+%s "
        "WHERE id=%s",
        [delta, account_id],
        consistency_level=ConsistencyLevel.QUORUM
    )

# With W=QUORUM, R=QUORUM, and N=3:
# Minimum guaranteed: 2 replicas have the latest write
# When reading from 2 replicas, at least 1 has the write
# → linearizable reads guaranteed
```

---

### ⚖️ Comparison Table

| Model | Guarantee | Example System | Use Case |
|---|---|---|---|
| **Linearizability** | Read sees globally latest write | etcd, ZooKeeper, Spanner | Config, locks, financial |
| Sequential | All agree on operation order | Multi-core CPU with sequential consistency | Coordination primitives |
| Causal | Causally related ops in order | MongoDB (causal sessions), CockroachDB | Comment threads, workflows |
| Read-Your-Writes | You see your own writes | Most databases with session stickiness | User profile, settings |
| Monotonic Reads | Reads don't go back in time | Most replicated databases | Feed, dashboards |
| Eventual | Converges eventually | Cassandra ONE, DynamoDB (default) | Caches, counters, feeds |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "ACID consistency and distributed consistency are the same" | ACID "C" means application invariants hold (no partial state). Distributed "C" means all nodes agree on the current value. They are related but distinct concepts. |
| "Eventual consistency means the data might be wrong" | Eventual consistency means the data might be stale (old but correct). It does not mean the data might be corrupted or lost. |
| "Strong consistency has no use case tradeoff" | Strong consistency adds latency and reduces availability. Systems like Google Spanner achieve global linearizability but at higher cost and latency. The trade-off is real. |
| "All NoSQL databases are eventually consistent" | Many NoSQL databases support tunable consistency. Cassandra with QUORUM is strongly consistent. DynamoDB with strongly consistent reads is strongly consistent. |

---

### 🚨 Failure Modes & Diagnosis

**Stale Read Causes Incorrect Business Decision**

**Symptom:** Two users simultaneously book the last seat on
a flight. Both succeed. The airline is oversold.

**Root Cause:** Both read operations returned the same seat
count (1 remaining) from stale replicas. Both bookings
were submitted based on this stale read. The system accepted
both writes without a conflict check.

**Diagnosis:** The failure is a concurrency/consistency
design problem, not a runtime bug. It is identified in
post-mortem by examining the timestamps of the two writes
relative to each replica's replication position.

**Fix:**
```sql
-- Use optimistic locking to detect stale reads at commit:
-- Check that the value has not changed since read

-- Read:
SELECT seat_count, version FROM flights WHERE id=123;
-- Returns: count=1, version=42

-- Book (conditional update with version check):
UPDATE flights
SET seat_count = seat_count - 1, version = version + 1
WHERE id=123
  AND version = 42   -- fails if someone else updated first
  AND seat_count > 0;

-- If 0 rows updated: someone else booked first.
-- Retry or return "seat unavailable."
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Message Passing` - Replication that creates consistency
  lag travels through message passing
- `Replication` - The mechanism that creates the consistency
  challenge

**Builds On This (learn these next):**
- `CAP Theorem` - Formalizes the trade-off between consistency
  and availability under partitions
- `Eventual Consistency / BASE` - Deep dive into the weakest
  widely-used consistency model
- `Linearizability` - Deep dive into the strongest
  consistency guarantee and how it is implemented

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ A promise about what a read returns      │
│              │ relative to recent writes                │
├──────────────┼──────────────────────────────────────────┤
│ SPECTRUM     │ Linearizability → Eventual Consistency   │
│              │ Stronger = more correct, higher cost     │
├──────────────┼──────────────────────────────────────────┤
│ KEY QUESTION │ "What is the business impact of a        │
│              │  stale read?" → determines required level│
├──────────────┼──────────────────────────────────────────┤
│ LINEARIZABLE │ Every read sees most recent write.       │
│              │ Required for: locks, counters, financial │
├──────────────┼──────────────────────────────────────────┤
│ EVENTUAL     │ All replicas converge eventually.        │
│              │ OK for: feeds, caches, preferences       │
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ Default to eventual consistency for      │
│              │ all data; it is not always safe          │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Choose the weakest consistency you can  │
│              │  tolerate; pay the cost of what you need.│
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ CAP Theorem → Eventual Consistency →     │
│              │ Linearizability → Serializability        │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
The consistency level decision is the same class of problem
as choosing a lock granularity in concurrent programming.
Coarse-grained locks are "consistent" (only one operation
at a time) but slow. Fine-grained or optimistic concurrency
control allows more concurrency but requires conflict
detection. In both cases, the right choice depends on the
rate of conflicts and the cost of resolving them.

---

### 💡 The Surprising Truth

Amazon published a "Dynamo" paper in 2007 describing
their choice of eventual consistency for their internal
key-value store. The stated reason was not performance or
cost - it was developer productivity. Amazon found that
programmers using strongly consistent storage spent enormous
time reasoning about transaction isolation levels and
lock contention. Eventual consistency, while requiring
conflict resolution code, was easier to reason about at
high concurrency. The surprising insight: eventual consistency
may make application code more complex (conflict resolution)
but makes storage behavior simpler (no locks, no blocking).
The tradeoff is between storage simplicity and application
complexity, not just between correctness and performance.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. [CLASSIFY] Given any read operation (read-after-write,
   read by different user, read during partition), determine
   which consistency model is needed.
2. [SELECT] Given a system description (ride-sharing,
   e-commerce, social media), assign the appropriate
   consistency level to each type of data.
3. [CODE] Implement read-your-writes consistency in a
   service that reads from replicated database with
   session-level LSN tracking.
4. [DEBUG] Given two concurrent operations that produced
   incorrect results, identify which consistency invariant
   was violated and what consistency level would prevent it.
5. [CALCULATE] With N=5 replicas, calculate the minimum
   W and R values to achieve strong consistency, and the
   maximum number of node failures the system can tolerate
   while maintaining reads and writes.
