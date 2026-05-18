---
id: DST-086
title: The Consistency-Availability Spectrum
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-001, DST-059, DST-079, DST-085
used_by: []
related: DST-001, DST-059, DST-079, DST-085, DST-078
tags:
  - distributed
  - consistency-spectrum
  - pacelc
  - session-consistency
  - causal-consistency
  - sequential-consistency
  - linearizability
  - eventual-consistency
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 86
permalink: /technical-mastery/distributed-systems/consistency-spectrum/
---

⚡ TL;DR - Consistency is not binary (consistent vs
inconsistent); it is a spectrum of 8+ formally
defined levels from eventual consistency (weakest:
updates propagate eventually) to linearizability
(strongest: every operation appears atomic at a
single instant); each stronger level provides more
guarantees to application code but requires more
coordination across nodes; real systems offer tunable
consistency (choose per operation), and the key
engineering skill is knowing which level is minimally
sufficient for each data type - not defaulting to
the strongest (too slow) or weakest (too risky).

---

### 📋 Entry Metadata

| #086 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | CAP intro (DST-001), Consistency Levels (DST-059), CAP Navigation (DST-079), CAP Formalization (DST-085) | |
| **Used by:** | N/A (synthesizes prior entries) | |
| **Related:** | Multi-Region Consistency (DST-078), all above | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT A SPECTRUM MODEL:**
Engineers know the endpoints: "strong consistency"
and "eventual consistency." But the space between
them is vast and contains many distinct models.
An engineer who only knows the endpoints makes
two common mistakes:

1. Defaults to linearizability everywhere: every
   operation requires cross-node consensus → latency
   is 150ms globally when 5ms would have been fine.

2. Defaults to eventual consistency everywhere:
   financial writes are eventually consistent →
   oversell, double-charge, phantom inventory.

The spectrum model provides the vocabulary and
trade-off analysis to choose the minimum necessary
consistency level for each data type.

---

### 📘 Textbook Definition

**Consistency spectrum** (from weakest to strongest):

1. **Eventual consistency:** all replicas will converge
   to the same value eventually (when writes stop).
   No ordering guarantee. No real-time guarantee.

2. **Monotonic read consistency:** once a process reads
   a value, it never reads an older value.

3. **Read-your-writes consistency (RYW):** a process
   always sees its own writes.

4. **Monotonic write consistency:** writes from a
   single process are applied in the same order
   everywhere.

5. **Session consistency:** combination of monotonic
   reads + RYW within a single session.

6. **Causal consistency:** causally related operations
   appear in causal order. Concurrent operations
   may be observed in different orders at different nodes.

7. **Sequential consistency (Lamport 1979):** all
   operations appear to execute in some total order.
   All processes observe the same total order.
   Not necessarily real-time consistent.

8. **Linearizability (Herlihy and Wing, 1990):**
   all operations appear to execute atomically
   in a total order consistent with real-time
   wall-clock ordering. The strongest model.

---

### ⏱️ Understand It in 30 Seconds

```
SPECTRUM WITH TRADE-OFFS:

LEVEL    GUARANTEE               COST           USE CASE
-------  ----------------------  -----------
  ----------------
Eventual  Converges eventually    Very low       View
  counters
          No ordering             coordination
            Recommendations
          
Monotonic Read same or newer      Low            News feed
  Read    value each read         coordination   (no going
    back)
  
RYW       See your own writes     Low            Comments
                                                 User
                                                   profile

Session   RYW + monotonic reads   Medium         Shopping
  session
          within session          coordination

Causal    Causal ops in order     Medium
  Collaborative docs
          Concurrent may differ   (vector clocks) Chat
            messages
          
Sequential All see same order     High
  Leaderboards
          (not real-time)         coordination   (any
            total order)
          
Linear    All operations atomic,  Highest
  Distributed locks
(strong)  real-time consistent    coordination   Financial
  balance

KEY INSIGHT: You do NOT need linearizability for a
recommendation engine. You DO need it for a mutex.
Use the minimum level that satisfies correctness.
```

---

### 🔩 First Principles Explanation

**FORMAL DEFINITIONS WITH EXAMPLES:**

```
1. EVENTUAL CONSISTENCY (weakest):
   Definition: If no new writes occur, all replicas
   will eventually converge to the same value.
   
   Counterexample showing NOT stronger:
     P1 writes v1. P2 reads → gets v0 (old).
     P2 reads again → gets v0 (same old).
     This is valid: "eventually" might take 60 seconds.
     Does NOT guarantee reads see recent writes.
   
   Used in: Cassandra (ONE), DNS, CDN cache,
   recommendations, activity feeds.
   
   Code: Cassandra with ONE:
     session.execute("SELECT * FROM users WHERE id=%s",
       (user_id,), consistency_level=ConsistencyLevel.ONE)
     # Fast: reads from nearest replica.
     # Risk: replica may have stale data.

2. READ-YOUR-WRITES (RYW):
   Definition: A process always sees the effects of
   its own writes. If process P writes x=1, P's
   subsequent reads of x return >= 1.
   
   Note: OTHER processes may still see stale values.
   This is a guarantee per writer, not globally.
   
   Implementation options:
     a. Always read from primary (simple, high load).
     b. Session stickiness: route reads to the replica
        that received the write.
     c. Write token: include WAL LSN in write response;
        read-only queries that can't meet that LSN
        are redirected to primary.
   
   Used in: social media (post then refresh), email
   clients, form submission pages.

3. CAUSAL CONSISTENCY:
   Definition: if operation a happens-before operation b
   (a → b in Lamport's model), then all processes
   observe a before b. Concurrent operations may be
   observed in different orders.
   
   EXAMPLE: Collaborative document editing.
     P1 writes "Hello" (version 1).
     P2, having seen P1's write, adds "World".
     P3 (seeing both) sees: "Hello" then "World". Correct.
     
   CONCURRENT EXAMPLE: P3 writes "Foo" at same time as
   P2 writes "World" (neither saw the other).
     Observers may see "Foo" before "World" or vice versa.
     Both orderings are valid under causal consistency.
   
   Implementation: vector clocks (DST-015).
     Each write carries a vector clock.
     A replica only delivers an update when all
     causally preceding updates have been delivered.
   
   Used in: COPS (Causal+ Consistency), some CRDTs,
   Facebook TAO (modified causal for social graph).

4. SEQUENTIAL CONSISTENCY (Lamport 1979):
   Definition: the result of any execution is the
   same as if the operations by all processors were
   executed in some sequential order, and the
   operations of each individual processor appear
   in that sequence in the order specified by the
   program.
   
   KEY: all processes observe the SAME total order.
   NOT KEY: that total order matches wall-clock time.
   
   EXAMPLE:
     Wall clock: P1 writes x=1 at T=100.
                 P2 writes x=2 at T=105.
     Sequential consistency allows: some observers
     see x=2 before x=1 (if x=2 was assigned a
     lower position in the total order).
     But: ALL observers see x=2 before x=1 (same order).
   
   Used in: Intel x86 TSO memory model (approximately),
   some shared memory multiprocessors.
   Rarely used directly in distributed databases.

5. LINEARIZABILITY (Herlihy and Wing 1990):
   Definition: each operation appears to take effect
   instantaneously at some point between its invocation
   and response. This point is the "linearization point."
   All operations appear in a total order consistent
   with real-time.
   
   KEY ADDITION vs sequential: real-time compatible.
   If op1 completes before op2 starts (in wall time):
   op1 MUST precede op2 in the linearization order.
   
   EXAMPLE:
     T=100ms: P1 writes x=1. Completes at T=110ms.
     T=115ms: P2 reads x. Returns x=1.
     This is correct: P1's write completed before P2's
       read started.
     Any implementation that returns x=0 for P2's read
     VIOLATES linearizability.
   
   Implementation:
     Option 1: Single-leader replication; all reads
       from primary. Simple. Single point of failure.
     Option 2: Paxos/Raft multi-Paxos. All reads and
       writes go through consensus. High coordination cost.
     Option 3: TrueTime (Spanner). Timestamps bounded
       within epsilon (~7ms). Commit wait ensures no
       reader sees stale data.
   
   Used in: etcd, ZooKeeper, Spanner, CockroachDB
   (serializable isolation = linearizable reads).
```

**THE HIERARCHY (formal relationships):**

```
HIERARCHY:
  Linearizability
       ↓ (weaker)
  Sequential Consistency
       ↓ (weaker)
  Causal Consistency
       ↓ (weaker)
  Session Consistency
       ↓ (weaker)
  Read-Your-Writes
  Monotonic Read
  Monotonic Write
  (all roughly equivalent; combinable into session)
       ↓ (weaker)
  Eventual Consistency

IMPORTANT: these are PROVABLY distinct.
  You can have causal consistency WITHOUT sequential.
  You can have RYW WITHOUT causal.
  Providing a weaker model does NOT imply the stronger.

KEY PRACTICAL IMPLICATION:
  "We use eventual consistency" means:
    You have NO ordering guarantees.
    Even RYW may be violated (a user posts a comment,
    refreshes, comment not visible).
    This is often WORSE than teams expect.
    
  "We use session consistency" means:
    Within a session: RYW + monotonic reads guaranteed.
    Cross-session: no guarantees (other users may see
      stale).
    MUCH better than eventual for most UX requirements.
    
CASSANDRA CONSISTENCY LEVELS MAP:
  ONE       → Eventual (may return stale from any replica)
  LOCAL_ONE → Eventual (nearest replica in local DC)
  QUORUM    → Sequential (majority agreement)
  LOCAL_QUORUM → Causal (for single-DC, effectively strong)
  EACH_QUORUM → Strong (quorum across ALL DCs; very slow)
  SERIAL    → Linearizable (Paxos LWT; most expensive)
```

**WHERE REAL SYSTEMS FALL:**

```
SYSTEM                   CONSISTENCY LEVEL
-----------------------  -----------------------
Cassandra (ONE)          Eventual
DynamoDB (default read)  Eventual
Redis (single node)      Sequential
Redis Cluster            Eventual (cross-shard)
Kafka (committed offset) Sequential (per-partition)
PostgreSQL (replica)     Eventual (async replication)
PostgreSQL (primary)     Linearizable
CockroachDB              Serializable ≈ Linearizable
Spanner                  Linearizable (external)
etcd (GET)               Linearizable (with
  --consistency=l)
ZooKeeper                Sequential
HBase                    Linearizable (per-row)
MongoDB (w:majority)     Linearizable (effectively)
MongoDB (default)        Session consistency
Facebook Messenger       Causal (MAST system)
Google Docs              Eventual + OT merge
```

---

### 🧠 Mental Model / Analogy

> The consistency spectrum is like reading a
> newspaper vs live news. Eventual consistency:
> read last week's newspaper (eventually you'll
> have the news). Session consistency: you get
> the newspaper you last read, plus any new editions
> published since. Causal consistency: events
> are reported in causal order (the assassination
> is reported before the funeral). Sequential
> consistency: everyone reads the same sequence
> of stories, even if not in real time. Linearizability:
> the live feed - what you see is what is happening
> RIGHT NOW, as it happens.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - Strong vs eventual:**
Strong (linearizable) = every read is current.
Eventual = reads might be stale. Most systems are
somewhere in between.

**Level 2 - RYW and session are the practical sweet spot:**
For user-facing applications: session consistency
(RYW + monotonic reads) satisfies most requirements
at low coordination cost. Linearizability is
only needed for shared mutable state with conflict risks.

**Level 3 - Causal consistency is underused:**
Causal consistency is stronger than session but
weaker than linearizable. It is the right choice
for collaborative applications (chat, documents).
Implementing it requires vector clocks, which adds
complexity but not the full overhead of consensus.

**Level 4 - System heterogeneity:**
Different operations in the same system should use
different consistency levels. Cassandra SERIAL for
inventory decrements; Cassandra ONE for product
listings. This is the key operational insight.

**Level 5 - The research frontier:**
Beyond linearizability: there are stronger models
(strict serializability = linearizability + ACID
transactions). Beyond eventual: convergent consistency
via CRDTs. The spectrum continues to be refined
as researchers find new trade-off points.

---

### 💻 Code Example

```python
# PRACTICAL SELECTION: minimum required consistency
# per operation type.

# Inventory decrement (financial impact of oversell):
# → LINEARIZABLE (Cassandra SERIAL / LWT)
result = session.execute(
    """
    UPDATE inventory SET quantity = quantity - 1
    WHERE product_id = %s AND quantity > 0
    IF quantity > 0
    """,
    (product_id,),
    execution_profile='serial'  # SERIAL = Paxos LWT
)

# User profile read (eventual stale is fine):
# → EVENTUAL (Cassandra ONE)
user = session.execute(
    "SELECT * FROM users WHERE id = %s",
    (user_id,),
    execution_profile='one'
)

# User's own post read after write (RYW needed):
# → SESSION CONSISTENCY (read from same replica as write,
#   or add WAL-LSN token to ensure replica is current)
def read_with_ryw(session, user_id, write_lsn):
    # Pass write_lsn from prior write response.
    # Route to a replica that has replicated past write_lsn.
    replica = router.get_replica_at_lsn(write_lsn)
    return session.execute(
        "SELECT * FROM posts WHERE author_id = %s",
        (user_id,),
        host=replica
    )

# Collaborative document edit (causal consistency needed):
# → CAUSAL (vector clock on each write)
def apply_document_edit(
    doc_id: str,
    edit: str,
    vector_clock: dict
):
    # Only apply if all causally preceding edits
    # have already been applied.
    current_vc = doc_store.get_vector_clock(doc_id)
    if not causal_ready(current_vc, vector_clock):
        # Buffer: wait for preceding edits to arrive.
        buffer.add(doc_id, edit, vector_clock)
        return "BUFFERED"
    doc_store.apply_edit(doc_id, edit)
    doc_store.update_vc(doc_id, vector_clock)
    return "APPLIED"
```

---

### ⚖️ Comparison Table

| Level | Ordering Guarantee | Cross-Session? | Real-time? | Cost |
|---|---|---|---|---|
| **Eventual** | None | None | No | Very low |
| **RYW** | Own writes only | No | No | Low |
| **Session** | RYW + monotonic | No | No | Medium |
| **Causal** | Causal chains | Yes (causal) | No | Medium-high |
| **Sequential** | Total order | Yes | No | High |
| **Linearizable** | Total + real-time | Yes | Yes | Highest |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "If we use a distributed database, we get consistency" | "Consistency" in distributed databases ranges from eventual to linearizable. You get the level you configure per operation. Without explicit configuration: most databases default to something weaker than linearizable. |
| "Eventual consistency is dangerous" | Eventual consistency is dangerous for SOME data types (inventory, balances). For others (view counters, recommendations, cached content), it is perfectly appropriate and dramatically cheaper. |
| "Sequential consistency is the same as linearizability" | They differ in the real-time property. Sequential consistency allows total orders that don't respect wall-clock time (a write that completed first may be ordered after a later write). Linearizability requires real-time compatibility. This distinction matters for leases and TTL-based systems. |
| "Our database is ACID, so it's linearizable" | ACID's "Consistency" (the C in ACID) refers to application-level constraints (foreign keys, CHECK constraints), NOT the CAP/spectrum consistency. A database can be ACID and eventually consistent. Isolation level (serializable) is the ACID property closest to linearizability, and most databases default to a weaker isolation level (read committed). |

---

### 🚨 Failure Modes & Diagnosis

**Assuming Eventual Consistency Means RYW**

**Symptom:** A user posts a comment. They refresh
the page immediately. The comment is not shown.
The user reports: "my comment disappeared." The
system is actually working correctly - the comment
was written and is propagating. But the user
believes data was lost.

**Root Cause:** The team chose eventual consistency
for reads (reads from nearest replica). After the
write, the user's next read was served by a different
replica that hadn't yet received the replication.
The team assumed eventual consistency provides
"at least RYW" - it does not.

**Diagnosis:**
```bash
# Check replication lag on the replica serving the user:
# (PostgreSQL example)
SELECT NOW() - pg_last_xact_replay_timestamp()
  AS replication_lag_seconds;
# → 3.2 seconds lag

# The user read within 3 seconds of writing.
# The replica was 3.2 seconds behind.
# RYW was violated.

# FIX OPTION 1: Use session stickiness.
# After a write: route subsequent reads to the
# same replica (or to the primary) for 10 seconds.
# Implementation: store in session:
#   session["last_write_ts"] = datetime.utcnow()
#   session["sticky_replica"] = replica_that_received_write
# On read: if (now - last_write_ts) < 10s:
#   use sticky_replica.

# FIX OPTION 2: Read after write from primary.
# After a write, read from the primary for 
# the next request. More expensive but simple.

# FIX OPTION 3: Write token.
# Write response includes WAL LSN.
# Subsequent reads pass the LSN.
# Replica only serves the read if its replay_lsn >= LSN.
```

---

### 🔗 Related Keywords

**Foundation:** `CAP Theorem` (DST-001),
`Consistency Levels` (DST-059)

**Built on:** `CAP Navigation` (DST-079),
`CAP Formalization` (DST-085)

**Applied in:** `Multi-Region Consistency` (DST-078)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ CONSISTENCY SPECTRUM (weak → strong)                    │
│ Eventual → Monotonic → RYW → Session                   │
│ → Causal → Sequential → Linearizable                   │
├─────────────────────────────────────────────────────────┤
│ RULE: Use minimum level that satisfies correctness     │
│ Financial/lock: Linearizable                           │
│ User-facing session: Session consistency              │
│ Collaborative: Causal                                 │
│ Counters/feed: Eventual                               │
├─────────────────────────────────────────────────────────┤
│ GOTCHA: Eventual ≠ RYW. Specify RYW explicitly.       │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

The consistency spectrum teaches that precision in
naming matters. "We use eventual consistency" is
nearly meaningless without specifying WHICH
eventually consistent model. RYW, monotonic reads,
session consistency, and causal consistency are
all "weaker than linearizable" but they provide
very different guarantees to application code.
An engineer who says "eventual consistency is fine"
and means "session consistency" has made a defensible
choice. An engineer who says "eventual consistency
is fine" and means "reads may return data from 60
seconds ago, including the user's own writes" has
made a potentially serious product and reliability
error. Use precise vocabulary. Name the specific
consistency level you need for each data type.

---

### 💡 The Surprising Truth

Facebook TAO (the Tao of Storage, OSDI 2013) is
Facebook's primary social graph storage system.
It stores and serves billions of edges (friend
relationships, likes, post objects) per day.
TAO's consistency model is neither eventual nor
strong: it is causal+ (causal consistency with
read-your-writes guaranteed within a datacenter,
and eventual cross-datacenter). This design was
chosen because social graph data has clear causal
requirements (if you see a friend's post, you
should also see that friend's profile update
that was causally related to it) but cross-
datacenter strong consistency would be prohibitively
expensive. The TAO paper is a masterclass in
choosing the minimum necessary consistency level
for a specific use case and engineering it to work
at Facebook-scale.

---

### ✅ Mastery Checklist

1. [CLASSIFY] For each model (eventual, RYW, session,
   causal, linearizable): give a real-world system
   or scenario where EXACTLY that level is needed
   and stronger would be unjustified overkill.
2. [DISTINGUISH] A user writes x=1. Another process
   reads x and gets x=0. Which consistency models
   are violated? Which are NOT violated?
3. [IMPLEMENT] Using Cassandra: write code for three
   operations: place_order (needs linearizability),
   get_order_history (eventual is fine), get_my_latest_order
   (needs RYW). Specify the consistency level for each.
4. [TRACE] A system uses causal consistency. P1 writes
   A=1. P2, having read A=1, writes B=2. P3 reads:
   may P3 see B=2 but A=0? Why or why not?
5. [CONNECT] Facebook TAO uses causal+ consistency.
   Explain what "+read-your-writes" adds on top of
   causal consistency, and why this matters for the
   user experience of the Facebook news feed.
