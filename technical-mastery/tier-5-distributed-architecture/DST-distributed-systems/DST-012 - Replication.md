---
id: DST-012
title: Replication
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★☆☆
depends_on: DST-008, DST-009, DST-011
used_by: DST-017, DST-026, DST-027, DST-028
related: DST-011, DST-013, DST-014, DST-017
tags:
  - distributed
  - data
  - reliability
  - foundational
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 12
permalink: /technical-mastery/distributed-systems/replication/
---

⚡ TL;DR - Replication is storing copies of the same data
on multiple nodes to achieve fault tolerance, increased read
throughput, and lower latency; the core challenge is keeping
those copies consistent when the same data is written from
multiple locations or at different times.

---

### 📋 Entry Metadata

| #012 | Category: Distributed Systems | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | Node, Message Passing, Fault Tolerance | |
| **Used by:** | Leader-Follower Replication, Replication Lag, Quorums | |
| **Related:** | Fault Tolerance, Sharding, Consistency, Leader-Follower Replication | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A bank's entire customer record database lives on one
server. At 11am on a weekday, the server's hard drive
fails. All customer data is inaccessible. The backup
tape from last night's backup is restored, losing 12 hours
of transactions. In the age of continuous online banking,
this is catastrophic.

**THE BREAKING POINT:**
A single node is a single point of failure, a read throughput
bottleneck, and a latency ceiling. If all 10 million users
send read requests to the same node, the node saturates.
If the node is in Virginia and a user in Tokyo sends a
read request, latency is 200ms+. Without replication, none
of these problems have solutions.

**THE CORE TENSION:**
Replication is conceptually simple: make copies of the data.
The challenge emerges immediately when two clients write to
different copies of the same data simultaneously. Both copies
think they have the authoritative value. Resolving this conflict
- deciding which value is "correct" - is the core problem of
distributed systems that entire textbooks are written about.

---

### 📘 Textbook Definition

**Replication** is the process of maintaining copies of the
same data on multiple nodes (replicas). Replication serves
three purposes: (1) **fault tolerance** - if one replica
fails, others continue serving requests; (2) **read scaling**
- read requests can be distributed across multiple replicas;
(3) **latency reduction** - replicas can be placed
geographically close to users. The primary challenge of
replication is **replica consistency**: all replicas should
return the same value for the same key. Achieving strong
consistency (all replicas always agree) under concurrent
writes and network delays is expensive; most systems offer
a consistency spectrum from strong to eventual, trading
consistency for availability and performance.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Replication means keeping multiple copies of data on multiple
nodes - the hard part is keeping all copies in sync.

**One analogy:**
> A library has one copy of a popular book, and 100 people
> want to read it simultaneously. The solution is to make
> 10 copies. Now, the problem: the author publishes an
> updated edition. The library must update all 10 copies.
> If some copies are updated and some are not, some readers
> get the old version. This is the replication consistency
> problem: keeping all copies synchronized when the data
> changes.

**One insight:**
Replication is not just about having copies. The consistency
guarantee of those copies determines what application behavior
is possible. An application that reads from a stale replica
may make incorrect decisions (show the user a seat that was
already sold). The consistency model - what staleness is
acceptable - must be a conscious design decision, not an
afterthought.

---

### 🔩 First Principles Explanation

**WHY REPLICATION IS HARD:**

```
┌────────────────────────────────────────────────────────┐
│  SINGLE NODE: Simple                                   │
│  Client writes X=5 → server stores X=5 → done         │
│                                                        │
│  REPLICATED: Complex                                   │
│  t=0: Node A: X=5,  Node B: X=5  (in sync)           │
│  t=1: Client 1 → Node A: write X=10                   │
│  t=2: Client 2 → Node B: write X=20                   │
│  t=3: Node A replicates X=10 to Node B                │
│  t=4: Node B replicates X=20 to Node A                │
│                                                        │
│  Final state: Node A has X=20 or X=10?                │
│               Node B has X=10 or X=20?                │
│  Which write wins?                                     │
│  Without coordination, the answer is undefined.        │
└────────────────────────────────────────────────────────┘
```

**THE REPLICATION STRATEGY SPECTRUM:**

**Single-Leader (Master-Slave):**
One node (the leader/primary) accepts all writes. It
replicates changes to followers (replicas) which serve reads.
The leader is the source of truth. Writes go to one place;
conflicts are impossible by design. Downside: the leader
is a write throughput bottleneck.

**Multi-Leader (Multi-Master):**
Multiple nodes accept writes independently. Each leader
replicates its writes to other leaders. Writes are fast
(geographically local). Downside: conflicts are possible
when the same data is written to two leaders simultaneously.
Requires conflict resolution.

**Leaderless (Peer-to-Peer):**
Any node can accept writes. The client writes to N replicas
directly. Uses quorums (W + R > N) to determine if a
read sees the latest write. Conflicts handled by timestamps
(last-write-wins) or merge functions. Used by Amazon Dynamo,
Cassandra, Riak.

**THE REPLICATION TIMING DIMENSION:**

**Synchronous:** Leader waits for replica confirmation before
acknowledging the write to the client. Guarantee: if the leader
fails, at least one replica has the data. Cost: write latency
includes replica network round-trip.

**Asynchronous:** Leader acknowledges the write immediately,
replicates to followers in the background. Benefit: low write
latency. Risk: if the leader fails before replicating, data
is lost.

**Semi-Synchronous:** One replica is synchronous; the rest
are asynchronous. Balance: at least one reliable replica with
reasonable write latency.

---

### 🧠 Mental Model / Analogy

> Think of replication as distributed version control (like
> Git). Each replica is a branch. Writing to a single leader
> is like committing to main and having all branches
> automatically fast-forward. Multi-leader is like merging
> two branches that have diverged - conflicts are possible
> and must be resolved. Leaderless is like peer-to-peer
> version control where any peer can accept commits and
> the history is reconciled through comparison.

Mapping:
- "Commit to main" - write to single leader
- "Branches fast-forward" - replicas receive replication
- "Merge conflict" - concurrent writes to different leaders
  update the same key to different values
- "Conflict resolution" - last-write-wins or merge function

**Where this analogy breaks down:** Git preserves history
so merges can be intelligent. Most replicated databases
only keep the current value, making conflict resolution
a last-write-wins coin flip unless explicitly coded otherwise.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Replication means keeping identical copies of data on multiple
servers. If one server fails, the others still have the data.
Multiple servers also serve more read requests simultaneously.

**Level 2 - How to use it (junior developer):**
Your database (PostgreSQL, MySQL, MongoDB) supports replication
configuration. Configure one primary node and one or more
replica nodes. Write requests always go to the primary. Read
requests can go to any replica (for read scaling) or the
primary (for strong consistency). Use a connection string that
knows which endpoints accept reads vs writes.

**Level 3 - How it works (mid-level engineer):**
In single-leader replication, the leader maintains a
replication log (WAL in PostgreSQL, binlog in MySQL). Every
write is recorded as an entry in this log. Followers connect
to the leader and stream the log, applying each entry to their
own storage. This is called log-based replication. Followers
may lag behind the leader by milliseconds or seconds depending
on write rate and network latency. This lag (replication lag)
means reads from followers may return stale data.

**Level 4 - Why it was designed this way (senior/staff):**
Log-based replication was designed to be both complete and
ordered. The log captures every change in the exact order
applied by the leader, allowing followers to exactly replay
the leader's state. Earlier approaches (statement-based
replication) replicated the SQL statement itself, which
failed for non-deterministic statements (NOW(), RAND()).
Log-based replication is deterministic: given the same
starting state and the same log, every follower reaches
the same final state.

**Level 5 - Mastery (distinguished engineer):**
The fundamental theorem of replicated state machines is:
given N nodes that start in the same state and receive
the same operations in the same order, they will reach
the same final state. This is why consensus protocols
(Paxos, Raft) focus on getting all nodes to agree on the
ORDER of operations. Ordering is the key. In multi-leader
and leaderless systems, the lack of a single order source
means writes can interleave in different orders at different
replicas, creating divergence. CRDTs (Conflict-free Replicated
Data Types) are a mathematical approach to designing data
structures where any interleaving produces the same result -
making ordering irrelevant for those structures.

---

### ⚙️ Mechanism - How Replication Works

**LOG-BASED REPLICATION FLOW (Single Leader):**

```
┌────────────────────────────────────────────────────────┐
│  LEADER NODE                                           │
│  1. Client writes: UPDATE users SET name='Alice'      │
│     WHERE id=1                                         │
│  2. Leader applies write to its storage               │
│  3. Leader appends entry to replication log:          │
│     {lsn: 1042, op: UPDATE, table: users,             │
│      id: 1, name: 'Alice'}                            │
│  4. If sync replica: wait for ACK from replica        │
│  5. Acknowledge write to client                        │
│                      │                                │
│                      ▼ (replication stream)           │
│  REPLICA NODE                                          │
│  6. Reads next entry from leader's log                │
│  7. Applies: UPDATE users SET name='Alice'            │
│     WHERE id=1                                         │
│  8. If sync: sends ACK to leader                      │
│  9. Updates its "applied up to LSN 1042" pointer      │
│                                                        │
│  REPLICATION LAG = leader LSN - replica applied LSN   │
└────────────────────────────────────────────────────────┘
```

**LEADERLESS QUORUM MECHANISM:**
```
System: 5 replicas. W=3 (write quorum). R=3 (read quorum)

WRITE: Client writes X=10 to 3 replicas
  Node A: X=10 (t=5)
  Node B: X=10 (t=5)
  Node C: X=10 (t=5)
  Node D: X=5  (old - was unreachable during write)
  Node E: X=5  (old - was unreachable during write)

READ: Client reads X from 3 replicas
  Reads from: A, B, D
  Returns: [X=10@t=5, X=10@t=5, X=5@t=3]
  Version comparison: X=10 has higher timestamp → return
    X=10

WHY IT WORKS:
  W + R = 3 + 3 = 6 > N = 5
  At least (W + R - N) = 1 replica must have seen
  both write and read → read always finds latest write
```

---

### 💻 Code Example

**Replication-Aware Database Access (Wrong vs Right)**

```python
# BAD: Ignore replication, always use same connection
db = create_engine("postgresql://primary:5432/app")

def get_user_balance(user_id: int) -> Decimal:
    # Critical: reads from replica that may be lagging
    # User just transferred money; balance may be stale
    return db.execute(
        "SELECT balance FROM accounts WHERE id=%s",
        [user_id]
    ).scalar()

# Problem: if connection is to a replica, user may see
# balance BEFORE their recent transaction was replicated
# This can cause overdraft: user sees $100, actually $0
```

```python
# GOOD: Use session tracking for read-your-writes consistency
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

primary = create_engine("postgresql://primary:5432/app")
replica = create_engine("postgresql://replica:5432/app")

class AccountService:
    def transfer(
        self,
        from_id: int,
        to_id: int,
        amount: Decimal
    ) -> str:
        # All writes to primary
        with Session(primary) as session:
            # ... perform transfer ...
            session.commit()
            # Tag: writes complete up to this point
            write_lsn = session.execute(
                "SELECT pg_current_wal_lsn()"
            ).scalar()
        return write_lsn  # return to caller to use in reads

    def get_balance(
        self,
        user_id: int,
        min_lsn: str = None
    ) -> Decimal:
        if min_lsn:
            # After a write: ensure read is from primary
            # or a replica that has replayed past this LSN
            engine = self._engine_with_min_lsn(min_lsn)
        else:
            # No recent write: replica is fine
            engine = replica
        with Session(engine) as session:
            return session.execute(
                "SELECT balance FROM accounts WHERE id=%s",
                [user_id]
            ).scalar()
```

**Monitoring Replication Lag (Production)**

```sql
-- PostgreSQL: Check replication lag
SELECT
    application_name,
    state,
    write_lag,
    flush_lag,
    replay_lag,
    pg_size_pretty(
        pg_wal_lsn_diff(
            pg_current_wal_lsn(),
            replay_lsn
        )
    ) AS lag_size
FROM
    pg_stat_replication
ORDER BY
    replay_lag DESC;

-- Alert if replay_lag > 5 seconds
-- Investigate: check network bandwidth, replica disk I/O,
-- check if replica is processing large transactions
```

---

### ⚖️ Comparison Table

| Strategy | Conflict Risk | Write Throughput | Consistency | Best For |
|---|---|---|---|---|
| **Single-Leader** | None (only one writer) | Single-node ceiling | Strong (sync) or eventual | Most databases, transactional workloads |
| Multi-Leader | High (concurrent writes) | Multiple-node ceiling | Eventual | Multi-region writes, offline-capable apps |
| Leaderless | Medium (quorum managed) | Configurable | Tunable (W+R>N) | High availability, Amazon Dynamo-style |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Replicas always have the same data as the primary" | Only synchronous replicas are guaranteed to have the latest data. Asynchronous replicas lag behind and may return stale data. |
| "More replicas = better consistency" | More replicas improve fault tolerance and read throughput. They make consistency HARDER, not easier, because there are more copies to keep in sync. |
| "Replication handles write scaling" | Single-leader replication does NOT scale writes - all writes still go to one node. Write scaling requires sharding (partitioning data across multiple leaders). |
| "Replication prevents data loss" | Only synchronous replication prevents data loss on leader failure. Asynchronous replication may lose the last N writes if the leader fails before replicating. |

---

### 🚨 Failure Modes & Diagnosis

**Replication Lag Causing Stale Reads**

**Symptom:** User creates an account, is redirected to
their profile page, and sees "account not found." Refreshing
the page shows the profile correctly.

**Root Cause:** Write went to primary. Profile page read
went to a replica. The replica had not yet replicated the
INSERT for the new account. Classic read-after-write
inconsistency.

**Diagnosis:**
```sql
-- Check replica lag (PostgreSQL):
SELECT now() - pg_last_xact_replay_timestamp()
AS replication_delay;
-- If > 1 second: replica is lagging

-- Check which replica served the request:
-- Add replica identity to query results:
SELECT pg_is_in_recovery() as is_replica,
       inet_server_addr() as server;
```

**Fix:** Route reads for "recently written" data to the
primary. Implement session-based read-your-writes consistency:
after a write, tag the session with the LSN; route reads
to primary until the replica confirms it has replayed
past that LSN.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Node` - The unit being replicated
- `Message Passing` - How replication log entries are
  transmitted between nodes
- `Fault Tolerance` - The primary motivation for replication

**Builds On This (learn these next):**
- `Leader-Follower Replication` - Deep dive into single-leader
  replication mechanics, failover, and lag
- `Replication Lag` - The consistency problem caused by
  asynchronous replication
- `Read and Write Quorums` - How leaderless replication
  achieves consistency through quorum mathematics

**Alternatives / Comparisons:**
- `Sharding` - Complementary to replication. Sharding
  splits data across nodes for write scaling. Replication
  copies data across nodes for fault tolerance and read
  scaling. Production systems often use both: sharded
  clusters where each shard is replicated.

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Multiple copies of data on multiple nodes│
├──────────────┼──────────────────────────────────────────┤
│ THREE GOALS  │ Fault tolerance, read scaling, low latenc│
├──────────────┼──────────────────────────────────────────┤
│ KEY CHALLENGE│ Keeping all copies consistent            │
│              │ under concurrent writes                  │
├──────────────┼──────────────────────────────────────────┤
│ STRATEGIES   │ Single-leader, Multi-leader, Leaderless  │
├──────────────┼──────────────────────────────────────────┤
│ TIMING       │ Sync (no data loss, higher latency)      │
│              │ Async (low latency, possible data loss)  │
├──────────────┼──────────────────────────────────────────┤
│ ANTI-PATTERN │ Reading from replica after write without │
│              │ session consistency (stale read risk)    │
├──────────────┼──────────────────────────────────────────┤
│ TRADE-OFF    │ Consistency vs availability vs latency   │
│              │ (all three cannot be maximized together) │
├──────────────┼──────────────────────────────────────────┤
│ ONE-LINER    │ "Copies are easy; keeping them in sync   │
│              │  is the entire problem."                 │
├──────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE │ Leader-Follower Replication → Replication│
│              │ Lag → Read and Write Quorums             │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Replication teaches a fundamental lesson about distributed
state: the moment you have two copies of anything, you have
a consistency problem. This applies in all areas: cache and
database must be consistent; API response and event stream
must be consistent; replicas of a config file must be
consistent. Every time you duplicate state, ask: "What is
the consistency guarantee, and what is the behavior when
the copies diverge?"

**Where else this pattern appears:**
- **CDN** - Content delivery networks replicate static
  assets to edge locations globally. Cache invalidation
  (propagating updates to all edge nodes) is the same
  problem as replication lag.
- **DNS** - DNS records are replicated across authoritative
  servers. TTL controls how stale cached records are.
  This is essentially async replication with time-based
  consistency.

---

### 💡 The Surprising Truth

Amazon DynamoDB internally uses single-leader replication
(one node is the leader for each key range), but its public
consistency model is "eventual consistency" by default.
The reason: reads are served from any replica by default,
and replicas may lag. Only when you request "strongly
consistent reads" does DynamoDB route your request to
the leader. The performance and cost difference is 2x:
strongly consistent reads cost twice as many capacity
units and have higher latency. This is the concrete,
measurable cost of consistency - documented in DynamoDB's
pricing - making the abstract trade-off between consistency
and performance tangible and real.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. [EXPLAIN] Given a specific scenario (user updates
   profile, immediately views profile), explain exactly
   which consistency model is needed, which database
   configuration implements it, and what the trade-off is.
2. [DEBUG] A user reports seeing stale data after a write.
   Use replication lag metrics to diagnose which replica
   served the stale read and how far behind it was.
3. [DESIGN] Choose between single-leader, multi-leader,
   and leaderless replication for: a transactional banking
   database; a global social media feed; a collaborative
   document editor.
4. [CALCULATE] Given W=2, R=2, N=3 quorum configuration,
   determine the maximum number of node failures the system
   can tolerate while still accepting writes and reads.
5. [BUILD] Implement read-your-writes consistency for a web
   application using session-level LSN tracking.

---

### 🧠 Think About This Before We Continue

**Q1.** In a single-leader replication setup with asynchronous
replication, the leader fails before replicating its last
5 writes. A follower is promoted to leader. When the original
leader comes back online, it has 5 writes that the new leader
does not. What should happen to those 5 writes, and why does
this create a hard problem for the application?
*Hint: Consider what happens if those 5 writes were
acknowledged to clients. What invariants were broken?*

**Q2.** In a leaderless system with N=5, W=3, R=3, two
concurrent clients write to the same key at the same
time: Client 1 writes X=10 to nodes {A, B, C}, Client 2
writes X=20 to nodes {C, D, E}. Node C receives both writes.
A third client then reads from nodes {A, D, E}. What does
it see, and is this the correct value?
*Hint: What timestamp does each write carry? What does
"last write wins" mean when writes happen simultaneously?*

**Q3.** Cassandra uses a technique called "hinted handoff"
to handle temporary node failures during writes. When a
replica node is down, the coordinator stores the write
in a "hint" and replays it when the node comes back.
What problem does this solve, and what consistency guarantee
does it provide (or fail to provide)?
*Hint: Consider what happens if the coordinator fails
before replaying the hint.*
