---
id: DST-027
title: Read and Write Quorums
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-012, DST-014, DST-016
used_by: DST-028, DST-033
related: DST-012, DST-014, DST-026, DST-028
tags:
  - distributed
  - consistency
  - replication
  - quorum
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 27
permalink: /technical-mastery/distributed-systems/read-write-quorums/
---

⚡ TL;DR - A quorum is the minimum number of nodes that
must acknowledge a write (W) or respond to a read (R)
for the operation to succeed; when W + R > N (number
of replicas), a read is guaranteed to see the latest
write because the write set and read set must overlap
by at least one node.

---

### 📋 Entry Metadata

| #027 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Replication, Consistency, CAP Theorem | |
| **Used by:** | Eventual Consistency, Two-Phase Commit | |
| **Related:** | Replication, Consistency, Replication Lag, Eventual Consistency | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT QUORUMS:**
A distributed database has 3 replicas. A write goes
to only 1 replica (W=1). A read comes from 1 replica
(R=1). If the write went to replica-A, and the read
goes to replica-B, the read returns stale data. There
is no guarantee the read sees the write.

To guarantee the read sees the write, you could always
read from the primary (W=1 to primary, R=1 from primary).
But this makes the primary a bottleneck - it must handle
all reads and writes. At scale, this does not work.

**THE CORE INSIGHT:**
Quorums provide a mathematical guarantee of consistency
without requiring all operations to go through a single
node. By requiring W replicas to acknowledge a write
and R replicas to respond to a read, you can choose
W and R such that any read is guaranteed to hit at least
one node that has the latest write.

---

### 📘 Textbook Definition

In a distributed system with N replicas:
- **W (write quorum):** the minimum number of replicas
  that must acknowledge a write before it is considered
  successful
- **R (read quorum):** the minimum number of replicas
  that must respond to a read; the response with the
  highest timestamp/version is returned

**Consistency guarantee:** if W + R > N, at least one
node in every read set has seen the write, guaranteeing
the read returns the most recent value.

**Common configurations:**
- W=1, R=N: Fast writes, slow reads, read consistent
- W=N, R=1: Slow writes, fast reads, read consistent
- W=N/2+1, R=N/2+1: Balanced, consistent (Cassandra QUORUM)
- W=1, R=1: Fast everything, inconsistent (Cassandra ONE)

---

### ⏱️ Understand It in 30 Seconds

**The math:**
```
N = 3 replicas
W = 2 (write to 2 nodes before success)
R = 2 (read from 2 nodes, return highest version)

W + R = 4 > N = 3 ✓ → consistent reads

Every read of 2 nodes must overlap with every write
of 2 nodes (since 2+2 > 3, pigeonhole principle).
```

**The guarantee:**
```
Write goes to: [node-1, node-2]   (W=2 ✓)
Read from:     [node-2, node-3]   (R=2 ✓)
Overlap:        node-2

node-2 has the latest value → read returns correct data.
```

**No guarantee (W + R ≤ N):**
```
W=1, R=1 (1+1 ≤ 3):
Write to:  [node-1]
Read from: [node-2]
Overlap:   none → read may return stale data
```

---

### 🔩 First Principles Explanation

**THE PIGEONHOLE PRINCIPLE:**

If you write to W replicas and read from R replicas,
the overlap between the two sets is at least W + R - N.
For W + R > N, the overlap is guaranteed to be ≥ 1.
Any read must include at least one node that received
the write.

```
N=5, W=3, R=3: overlap ≥ 3+3-5 = 1 ✓
N=5, W=2, R=2: overlap ≥ 2+2-5 = -1 → no guarantee
N=5, W=3, R=2: overlap ≥ 3+2-5 = 0 → no guarantee
N=5, W=3, R=3: at least 1 overlapping node ✓
```

**WHAT HAPPENS AT EACH NODE DURING A QUORUM READ:**

```
Client: READ key=user:1
Coordinator: sends read to R=2 nodes
  node-1: {"value": "Alice", "version": 5}
  node-2: {"value": "Bob",   "version": 7}  ← newest
  → return version 7: "Bob"

Optionally: coordinator sends version 7 to node-1
to repair the stale value (read repair pattern)
```

**VERSION TRACKING:**

Each write must carry a version that replicas can
compare. In Cassandra: write timestamp. In DynamoDB:
version number. In custom implementations: monotonically
increasing logical clock. Without a version, the
coordinator cannot determine which replica has the
latest value.

---

### 🧠 Mental Model / Analogy

> A law requires a jury to be "unanimous" (N=12, W=12,
> R=12) for conviction - slow but maximally consistent.
> A "majority vote" (N=12, W=7, R=7) gives the same
> guarantee with less consensus required. A "plurality
> rule" (N=12, W=4, R=4) may produce inconsistent
> results because two different sets of 4 might disagree.
>
> The quorum principle: any read and write that share
> at least one juror (node) will share the same
> information. Quorums are the minimum size to guarantee
> this sharing.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is:**
A quorum is the minimum number of nodes that must agree
before an operation counts. In a 3-node cluster with
W=2 and R=2: a write only succeeds when 2 nodes confirm,
and a read gets answers from 2 nodes and returns the
newest. This guarantees you always read the latest write.

**Level 2 - When to use it:**
Use quorums when you need stronger consistency than
single-replica writes provide, but cannot afford to write
to ALL replicas. The W=majority, R=majority (QUORUM
in Cassandra) setting is the practical default for
consistency. Use W=1, R=1 (ANY/ONE in Cassandra) when
you need maximum throughput and can accept stale reads.

**Level 3 - How to tune it:**
The N, W, R parameters are tunable per operation in
most distributed databases:

```
# Cassandra CQL: per-query consistency:
SELECT * FROM users WHERE id=1
  USING CONSISTENCY QUORUM;  # R=majority
INSERT INTO users(id, name) VALUES (1, 'Alice')
  USING CONSISTENCY ONE;     # W=1 (fast, inconsistent)
```

Choose based on the operation's consistency requirement:
financial data → QUORUM or ALL. Activity feed → ONE.

**Level 4 - The limitations:**
W + R > N guarantees that a read sees the latest
COMMITTED write. It does not protect against:
- Concurrent writes (two simultaneous writes to the
  same key with same version - last-write-wins by default)
- Coordinator failure mid-write (W nodes may have
  different versions)
- Clock skew in timestamp-based version comparison

These edge cases require additional mechanisms: sloppy
quorums, vector clocks, or conditional writes.

**Level 5 - Sloppy quorums:**
In a 5-node cluster, if 2 nodes are unreachable, a
strict quorum of W=3 fails. Cassandra uses "sloppy
quorums" in some configurations: write to 3 available
nodes, even if some are not the "home" replicas for
the key (hinted handoff). This improves availability
at the cost of consistency - the written value may
be on non-canonical replicas. When home replicas
recover, hinted values are replayed. This is not a
strict W + R > N guarantee.

---

### ⚙️ Mechanism - Quorum in Cassandra

```
WRITE (W=QUORUM, N=3 replicas, QUORUM=2):

Client
  │
  ▼
Coordinator
  │──────────► node-1: write key=A, val=X, ts=100
  │──────────► node-2: write key=A, val=X, ts=100
  │──────────► node-3: write key=A, val=X, ts=100
  │                     (async, fire-and-forget)
  │
Wait for W=2 ACKs:
  ◄── node-1: ACK
  ◄── node-2: ACK
  ▲
  │ node-3 may be slow/down; doesn't matter (W=2 met)
  │
Client: WRITE SUCCESS

READ (R=QUORUM, QUORUM=2):

Client
  │
  ▼
Coordinator
  │──────────► node-1: read key=A → {val=X, ts=100}
  │──────────► node-2: read key=A → {val=X, ts=100}
  │──────────► node-3: read key=A (optional, latency)
  │
Compare versions: ts=100 is highest
Return: val=X

Read repair: if any node had older version,
coordinator sends latest value to repair it
```

---

### 💻 Code Example

**Quorum Writes vs Single-Replica Writes**

```python
# BAD: Write to single replica, read from single replica
# W=1, R=1: no consistency guarantee
from cassandra.cluster import Cluster
from cassandra.policies import ConsistencyLevel

cluster = Cluster(['node-1', 'node-2', 'node-3'])
session = cluster.connect('myapp')

# Inconsistent: write goes to one node
session.execute(
    "INSERT INTO accounts(id, balance) VALUES (%s, %s)",
    (account_id, new_balance),
    # Default: ConsistencyLevel.ONE
)

# Read may go to different node that hasn't seen write
result = session.execute(
    "SELECT balance FROM accounts WHERE id=%s",
    (account_id,)
    # Default: ConsistencyLevel.ONE
)
# RISK: balance may be stale - critical bug for finances
```

```python
# GOOD: Quorum for financial data (strong consistency)
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from cassandra import ConsistencyLevel

cluster = Cluster(['node-1', 'node-2', 'node-3'])
session = cluster.connect('myapp')

# W=QUORUM: write to majority of replicas
write_stmt = SimpleStatement(
    "INSERT INTO accounts(id, balance) VALUES (%s, %s)",
    consistency_level=ConsistencyLevel.QUORUM  # W=2/3
)
session.execute(write_stmt, (account_id, new_balance))

# R=QUORUM: read from majority, return highest version
read_stmt = SimpleStatement(
    "SELECT balance FROM accounts WHERE id=%s",
    consistency_level=ConsistencyLevel.QUORUM  # R=2/3
)
result = session.execute(read_stmt, (account_id,))
# Guaranteed to see the write above: W(2) + R(2) > N(3)
```

**Custom Quorum Implementation**

```python
# Simplified quorum logic for illustration:

import concurrent.futures

def quorum_write(
    replicas: list,
    key: str,
    value: str,
    version: int,
    W: int
) -> bool:
    """Write to all replicas, require W ACKs."""
    acks = 0
    with concurrent.futures.ThreadPoolExecutor() as ex:
        futures = {
            ex.submit(r.write, key, value, version): r
            for r in replicas
        }
        for future in concurrent.futures.as_completed(
            futures
        ):
            try:
                if future.result():
                    acks += 1
                    if acks >= W:
                        return True  # Quorum reached
            except Exception:
                pass  # Node unreachable, try others
    return acks >= W

def quorum_read(
    replicas: list,
    key: str,
    R: int
) -> tuple[str, int]:
    """Read from R replicas, return highest version."""
    responses = []
    with concurrent.futures.ThreadPoolExecutor() as ex:
        futures = [
            ex.submit(r.read, key) for r in replicas
        ]
        for future in concurrent.futures.as_completed(
            futures, timeout=2.0
        ):
            try:
                value, version = future.result()
                responses.append((value, version))
                if len(responses) >= R:
                    break
            except Exception:
                pass
    if len(responses) < R:
        raise QuorumError(
            f"Only {len(responses)}/{R} replicas responded"
        )
    # Return value with highest version:
    return max(responses, key=lambda r: r[1])
```

---

### ⚖️ Comparison Table

| Configuration | Write Cost | Read Cost | Consistent? | Use Case |
|---|---|---|---|---|
| **W=N, R=1** | Slow (all nodes) | Fast | Yes | Read-heavy, rarely write |
| **W=1, R=N** | Fast | Slow (all nodes) | Yes | Write-heavy, read for audit |
| **W=N/2+1, R=N/2+1** | Moderate | Moderate | Yes | General purpose (Cassandra QUORUM) |
| **W=1, R=1** | Fast | Fast | No | Non-critical, eventual OK |
| **W=N, R=N** | Very Slow | Very Slow | Yes (strong) | Max durability |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "W + R > N guarantees linearizability" | It guarantees the read returns the most recent committed write, but concurrent writes or coordinator failures can still cause anomalies. Linearizability requires additional protocols (e.g., Raft). |
| "Quorums eliminate the need for a leader" | Leaderless quorums (Cassandra) still have edge cases. True leaderless consistency at scale requires conflict resolution (CRDTs, last-write-wins). |
| "QUORUM consistency level is always safe" | QUORUM fails if more than N/2 nodes are down. In a 3-node cluster, losing 2 nodes makes QUORUM unavailable. Design for what happens when quorum cannot be reached. |
| "Sloppy quorum is equivalent to strict quorum" | Sloppy quorum improves availability but weakens consistency. Written values may be on non-canonical nodes until hinted handoff completes. |

---

### 🚨 Failure Modes & Diagnosis

**Quorum Unavailable Exception**

**Symptom:**
```
cassandra.Unavailable: Error from server: code=1000
[Unavailable exception]
message="Cannot achieve consistency level QUORUM"
required=2, alive=1
```

**Cause:** More than 1 node in a 3-replica cluster is
unreachable. QUORUM requires 2 of 3 nodes. With only
1 alive, quorum cannot be formed.

**Resolution:**
```python
# Strategy 1: Temporary fallback to ONE consistency
# (accept stale reads during degraded mode)
from cassandra import ConsistencyLevel

def read_with_fallback(session, query, params):
    try:
        stmt = SimpleStatement(
            query,
            consistency_level=ConsistencyLevel.QUORUM
        )
        return session.execute(stmt, params)
    except cassandra.Unavailable:
        # Log and alert: cluster degraded
        log.warning("Quorum unavailable, falling back to ONE")
        stmt = SimpleStatement(
            query,
            consistency_level=ConsistencyLevel.ONE
        )
        return session.execute(stmt, params)

# Strategy 2: Circuit breaker - fail fast, don't degrade
# Preferred for financial data where stale = wrong
```

---

### 🔗 Related Keywords

**Prerequisites:**
- `Replication` (DST-012), `Consistency` (DST-014), `CAP Theorem` (DST-016)

**Builds On This:**
- `Eventual Consistency / BASE Properties` (DST-028)
- `Two-Phase Commit / 2PC` (DST-033)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ FORMULA    │ W + R > N → consistent reads               │
│ N=3        │ W=2, R=2: QUORUM (most common)             │
│            │ W=1, R=1: ONE (fast, inconsistent)         │
├────────────┼────────────────────────────────────────────┤
│ GUARANTEE  │ Read overlaps at least one write node      │
├────────────┼────────────────────────────────────────────┤
│ CASSANDRA  │ QUORUM = majority of replicas              │
│            │ ALL = every replica                        │
│            │ ONE = single replica (fast, inconsistent)  │
├────────────┼────────────────────────────────────────────┤
│ LIMITS     │ Only guarantees vs concurrent writes       │
│            │ Sloppy quorum weakens guarantee            │
├────────────┼────────────────────────────────────────────┤
│ ONE-LINER  │ "If write set + read set share a node,     │
│            │  the read must see the write."             │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

Quorums are the fundamental primitive for achieving
consistency without centralization. The same principle
applies far beyond databases: Raft and Paxos require
majority quorums for log entry commitment. Blockchain
mining requires majority hash power. DNS change
propagation requires seeing the change on majority
of resolvers to consider it propagated. Any distributed
decision-making system uses the quorum principle: a
subset that must overlap with any future subset.
Whenever you see "majority vote" or "consensus" in a
distributed system, you are seeing quorums.

---

### 💡 The Surprising Truth

Amazon DynamoDB's original quorum configuration was W=2,
R=2, N=3. In 2012, the DynamoDB team discovered that
even with W+R>N, a specific concurrent write pattern
could cause "lost updates": two coordinators writing
the same key simultaneously could each get W=2 ACKs,
but the two writes could be on different sets of 2
nodes, leaving the cluster in a split state. Neither
write was "lost" in the sense of being discarded - both
existed on different replica sets, with no single node
having both. This is the "concurrent write conflict"
that quorums alone cannot prevent. The fix: conditional
writes (`put_item` with `ConditionExpression`), which
ensure writes are idempotent with respect to a specific
version. Quorums guarantee freshness; conditional writes
guarantee atomicity under concurrency.

---

### ✅ Mastery Checklist

1. [CALCULATE] Given N=5, determine the minimum W and R
   for strong consistency. Verify W + R > N. Calculate
   the maximum number of node failures the system can
   tolerate while still forming a quorum.
2. [IMPLEMENT] Set Cassandra consistency level to QUORUM
   for a write-critical operation and ONE for a
   non-critical read. Verify behavior under node failure.
3. [DECIDE] Choose between QUORUM and LOCAL_QUORUM for
   a multi-datacenter Cassandra deployment where cross-DC
   latency is 80ms.
4. [DEBUG] A service reports intermittent stale reads
   despite using QUORUM. Investigate whether sloppy
   quorum (hinted handoff) or concurrent writes are
   the cause.
5. [EXPLAIN] Why W + R > N does not prevent all
   consistency anomalies and what additional mechanism
   (conditional writes or CAS) is needed for correctness
   under concurrent writes.
