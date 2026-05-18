---
id: DST-029
title: Linearizability
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-014, DST-016, DST-027, DST-028
used_by: DST-031, DST-033
related: DST-014, DST-016, DST-027, DST-028
tags:
  - distributed
  - consistency
  - correctness
  - formal
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 29
permalink: /technical-mastery/distributed-systems/linearizability/
---

⚡ TL;DR - Linearizability is the strongest consistency
guarantee a distributed system can provide: every
operation appears to execute instantaneously at some
point between its invocation and completion, and all
operations appear to occur in a single globally consistent
order; it is expensive (requires coordination) and is
the guarantee that makes distributed systems "feel"
like a single-node system.

---

### 📋 Entry Metadata

| #029 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Consistency, CAP Theorem, Quorums, Eventual Consistency | |
| **Used by:** | Vector Clocks, Two-Phase Commit | |
| **Related:** | Consistency, CAP Theorem, Quorums, Eventual Consistency | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A distributed lock service is used to prevent two
processes from running a job simultaneously. Process A
acquires the lock (writes "locked" to the database),
checks the value (reads "locked"), and starts the job.
Process B simultaneously acquires the lock on a replica
that hasn't seen Process A's write yet. The replica
shows "unlocked". Process B also "acquires" the lock.
Both processes run the job. The lock failed.

The failure: the database provided sequential consistency
or eventual consistency - the read from Process B could
return a value that predates Process A's write. A
linearizable database would guarantee that Process B's
read sees Process A's write (since A's write completed
before B's read began). The lock would have worked.

**THE CORE INSIGHT:**
Some distributed primitives - locks, leader election,
compare-and-swap, unique ID generation - require
stronger guarantees than "all replicas eventually agree."
They require that any read observes all writes that
completed before the read began. This is linearizability.

---

### 📘 Textbook Definition

**Linearizability** (also called atomic consistency or
strong consistency) is a consistency model where every
operation appears to take effect atomically at some
instant between the operation's invocation and its
response, and this instant is consistent with the
real-time ordering of operations.

More formally: there exists a serial execution order
of all operations that:
1. Is consistent with each operation's return value
2. Respects the real-time order: if operation A
   completes before operation B begins, A must
   appear before B in the serial order

Linearizability implies that the system behaves as if
there is a single, globally consistent copy of the data,
even though it is distributed across multiple nodes.

---

### ⏱️ Understand It in 30 Seconds

**The test:**
```
Linearizability = "External Consistency"

If client A writes X=1 and gets a success response,
then client B reads X, B must see X=1 (or a value
written after A's write).

A's write "completed" (success ACK received).
B's read "began" after A's write completed.
→ B must see A's write.
```

**The key property:**
```
Non-linearizable (sequential consistency):
  Operations may appear in a different global order
  than real-time, but all clients see the same order.
  Client B may see X=0 even after A's write completes.

Linearizable:
  Operations appear in real-time order.
  Client B MUST see X=1 if A's write completed first.
```

**The cost:**
```
Linearizability requires coordination:
  Every read must verify it is seeing the latest value
  (or the write must reach all nodes before ACK).
  This requires network round trips during reads/writes.
  Not achievable with pure async replication.
```

---

### 🔩 First Principles Explanation

**THE FORMAL MODEL:**

A history H of operation invocations and responses is
linearizable if there exists a legal sequential history
S such that:

1. S is consistent with H (each operation in H appears
   in S with the same arguments and return values)
2. If operation A completes before B begins in H,
   then A appears before B in S

```
Example: register with initial value 0

History H:
  t=0: Client A: write(1)
  t=2: Client A: write returns OK
  t=3: Client B: read starts
  t=5: Client B: read returns ???

Linearizable requirement:
  Client A's write completed at t=2.
  Client B's read started at t=3.
  ∴ B's read must return 1 (or a value written after t=2).
  Returning 0 violates linearizability.

Sequential consistency (weaker):
  B could see 0 if the system chose a serial order
  where B's read is "placed" before A's write.
  Even though A's write completed first in real time.
```

**WHY CAP THEOREM MEANS LINEARIZABILITY IS NOT FREE:**

From CAP: during a network partition, you cannot have
both linearizability (C) and availability (A). The proof:
- Partition separates node X and node Y
- Client writes to X
- X cannot replicate to Y (partition)
- Client reads from Y

If Y returns "latest" (linearizable), it must wait for
partition to heal. During that wait, Y is not available.
If Y returns its local value (available), it may not
reflect the write - not linearizable.

Linearizability = CP behavior. It requires that minority
partition nodes stop serving reads (or reject them) until
they can confirm they have the latest value.

---

### 🧠 Mental Model / Analogy

> Linearizability is the "sticky note" property. Imagine
> a whiteboard where the current value of X is written.
> One person can change the note at a time. The moment
> the change is complete (they put down the marker),
> anyone who looks at the whiteboard sees the new value.
> There is no "I haven't looked at the board in a few
> seconds" - the board is always current for any viewer
> who looks after the change completes.
>
> A non-linearizable system is like a whiteboard with
> 50 photographs distributed globally. The change is
> made on the original, but photos in Tokyo and London
> may still show the old value for a few seconds.
> Eventually all photos are updated. But during that
> window, a person in Tokyo looking at their photo
> sees old data even though the change is "done."

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is:**
Linearizability means: once a write succeeds, any future
read (from any node) sees that write. The system behaves
like there is only one copy of the data, even though it
is replicated. The strongest consistency guarantee.
Very safe, but slow.

**Level 2 - What it enables:**
Linearizability is required for distributed locks,
leader election, counter-based unique ID generation,
compare-and-swap operations, and any coordination
primitive where correctness depends on "no other process
has written this in the meantime."

**Level 3 - How it is implemented:**
Common implementations: Raft and Paxos consensus protocols.
In Raft, a read is linearizable only if it is served
by the current leader AFTER the leader confirms its
term via a round-trip to a majority quorum (read index
protocol). ZooKeeper provides linearizable writes via
Zab protocol and linearizable reads only via `sync()`
before read. etcd provides linearizable reads by default
(with the performance cost). Many SQL databases provide
linearizability within a single node; distributed SQL
databases (Spanner, CockroachDB) use consensus protocols
for cross-node linearizability.

**Level 4 - Linearizability vs Serializability:**
These are commonly confused:
- **Linearizability**: single-object, real-time ordering.
  A read-after-write guarantee for individual keys.
- **Serializability**: multi-object, transaction-level.
  Transactions appear to execute serially, but not
  necessarily in real-time order.
- **Strict Serializability** (Serializable + Linearizable):
  transactions execute serially AND in real-time order.
  The gold standard. Spanner provides this.

A system can be serializable without being linearizable
(two transactions can appear in an order that violates
real-time, as long as the order is consistent).

**Level 5 - The cost in numbers:**
Google Spanner's external consistency (linearizability
for transactions) requires synchronized clocks accurate
to ~7ms via GPS and atomic clocks, and each write waits
for the "commit wait" period (7ms) before completing
to ensure the assigned timestamp is in the past by
the time any reader sees it. This is the TrueTime
mechanism. A 7ms minimum write latency is the price
of global linearizability. For most applications, this
is acceptable and invisible. For high-frequency trading,
it is not - those systems sacrifice consistency for
sub-millisecond latency.

---

### ⚙️ Why It Holds True

**THE PROOF THAT LINEARIZABILITY REQUIRES COORDINATION:**

```
Claim: asynchronous reads without coordination
       cannot be linearizable in a distributed system.

Setup:
  - 2 nodes: node-A and node-B
  - Each serves local reads without contacting others
  - A client writes to node-A and gets ACK

Counterexample:
  1. Client writes X=1 to node-A (success ACK)
  2. Replication from A to B is in-flight (async)
  3. Different client reads X from node-B
  4. B has not received the replication yet
  5. B returns X=0

This violates linearizability: a write that completed
(step 1) is not visible to a subsequent read (step 3-5).

∴ For reads to be linearizable, either:
  (a) All writes must be synchronously applied on all
      nodes before ACK (high write latency), OR
  (b) Reads must contact the leader or majority to
      verify they have the latest value (read cost).
```

**RAFT LINEARIZABLE READS (Read Index Protocol):**

```
Without Read Index:
  Leader receives read request
  Returns leader's local state
  PROBLEM: leader may have been replaced; it's stale.

With Read Index:
  Leader receives read request
  Leader sends heartbeat to majority: "am I still leader?"
  Majority confirms: "yes, still leader"
  Leader returns read response
  COST: one extra network round trip per linearizable read
```

---

### 💻 Code Example

**Non-Linearizable vs Linearizable Lock**

```java
// BAD: using Redis SETNX without expiry / atomic check
// Non-linearizable under failover

public boolean acquireLock(String lockKey, String value) {
    // BAD: two operations, not atomic
    Boolean absent = redisTemplate.opsForValue()
        .setIfAbsent(lockKey, value);
    if (absent) {
        // RACE CONDITION: node fails between SETNX
        // and EXPIRE - lock never released
        redisTemplate.expire(lockKey, 30, TimeUnit.SECONDS);
    }
    return absent != null && absent;
}
// ALSO BAD: Redis replication is async. If primary fails
// after SETNX but before replication, new primary has
// no lock. Two clients acquire the "same" lock.
// Not linearizable under failover.
```

```java
// GOOD: use a CP system (etcd/ZooKeeper) for locks
// Linearizable by design via Raft/Zab consensus

import io.etcd.jetcd.Client;
import io.etcd.jetcd.Lock;

public class DistributedLock {
    private final Lock lockClient;
    private final long leaseTtlSeconds = 30;

    /**
     * Acquire lock via etcd (linearizable).
     * Raft consensus ensures no two clients
     * simultaneously acquire the same lock,
     * even during leader failover.
     */
    public byte[] acquire(String lockName) throws Exception {
        // etcd lock is atomic via Raft:
        // lock is only granted after majority quorum
        // confirms the write. Linearizable by definition.
        LockResponse response = lockClient.lock(
            ByteSequence.from(lockName, UTF_8),
            leaseId  // auto-released on TTL expiry
        ).get();
        return response.getKey().getBytes();
    }

    public void release(byte[] lockKey) throws Exception {
        lockClient.unlock(
            ByteSequence.from(lockKey)
        ).get();
    }
}
// Linearizable: etcd's Raft protocol ensures that
// once a lock is acquired, any other attempt to
// acquire the same lock sees the acquisition,
// regardless of which etcd node handles the request.
```

**Testing Linearizability Violations**

```python
# Test pattern: linearizability checker
# After a write ACK, any read must see the write.

def test_read_after_write_linearizable(db):
    # Write and receive acknowledgment:
    db.write("key", "value-1")  # blocks until ACK

    # Any subsequent read from any node must see value-1:
    results = []
    with concurrent.futures.ThreadPoolExecutor(10) as ex:
        futures = [
            ex.submit(db.read_from_node, "key", node)
            for node in db.all_nodes()
        ]
        results = [f.result() for f in futures]

    # Linearizability check: all results must be
    # "value-1" (or newer, if concurrent writes exist)
    for node, value in results:
        assert value == "value-1", (
            f"Node {node} returned '{value}' "
            f"after write of 'value-1' was ACKed. "
            f"LINEARIZABILITY VIOLATION."
        )
```

---

### ⚖️ Comparison Table

| Model | Ordering | Real-Time? | Cost | Use Case |
|---|---|---|---|---|
| **Linearizability** | Global, real-time | Yes | High (consensus) | Locks, leader election, CAS |
| **Sequential Consistency** | Global, not real-time | No | Medium | Some distributed DBs |
| **Causal Consistency** | Causal order only | No | Low-Medium | Social feeds, collaboration |
| **Eventual Consistency** | None during window | No | Lowest | Likes, views, preferences |
| **Read-your-writes** | Per-client only | No | Low | Profile updates, cart |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Serializable = linearizable" | Serializability is a transaction-level property (multi-object). Linearizability is a single-object, real-time property. A system can be serializable without being linearizable. |
| "All strongly consistent databases provide linearizability" | "Strong consistency" is sometimes used loosely. MySQL's InnoDB is serializable within a single node. Cross-node linearizability requires consensus. Verify the specific guarantee. |
| "Linearizability means no replication lag" | Linearizability means reads always see the latest written value. It does not mean writes are synchronous to all replicas - it means reads block until they can return a current value. |
| "etcd / ZooKeeper reads are linearizable by default" | ZooKeeper reads from followers are NOT linearizable by default. Use `sync()` before a read to ensure linearizability. etcd reads ARE linearizable by default (serializability=true). |

---

### 🚨 Failure Modes & Diagnosis

**Stale Leader Serving Non-Linearizable Reads**

**Symptom:** A distributed lock service implemented on
top of a consensus system returns "unlocked" even though
a lock was recently acquired. Process B sees the lock
as free and acquires it. Two holders simultaneously.

**Root Cause:** A Raft leader that has been deposed
(new leader elected) continues serving reads from its
local state without verifying its leadership status.
The deposed leader's local state does not have the
lock acquisition write that the new leader has.

**Detection:**
```bash
# etcd: verify leader status:
etcdctl endpoint status --cluster
# Look for: isLeader=true on the node serving reads
# If two nodes show isLeader=true: split-brain

# ZooKeeper: verify sync:
echo stat | nc zookeeper-host 2181 | grep leader
```

**Fix:**
- Use leader lease validation (confirm leadership
  via quorum heartbeat before serving reads)
- Use fencing tokens (DST-046) alongside locks:
  even if two holders believe they hold the lock,
  the one with the older fencing token is rejected
  by the protected resource

---

### 🔗 Related Keywords

**Prerequisites:**
- `Consistency` (DST-014), `CAP Theorem` (DST-016)
- `Read/Write Quorums` (DST-027)

**Builds On This:**
- `Vector Clocks` (DST-031)
- `Two-Phase Commit / 2PC` (DST-033)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ DEFINITION │ Ops appear instantaneous + in real-time    │
│            │ order; reads see all completed writes      │
├────────────┼────────────────────────────────────────────┤
│ REQUIRES   │ Consensus (Raft/Paxos) or sync writes      │
│            │ to majority before ACK                     │
├────────────┼────────────────────────────────────────────┤
│ COST       │ Network round trip per linearizable read;  │
│            │ unavailable during minority partition      │
├────────────┼────────────────────────────────────────────┤
│ USE FOR    │ Distributed locks, leader election, CAS,  │
│            │ unique ID generation                       │
├────────────┼────────────────────────────────────────────┤
│ SYSTEMS    │ etcd (default), ZooKeeper (with sync()),   │
│            │ Spanner, CockroachDB, Postgres (single-node│
├────────────┼────────────────────────────────────────────┤
│ ONE-LINER  │ "Once written, always readable - the       │
│            │  strongest contract a database can offer." │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

Linearizability is the foundational correctness property
that enables coordination in distributed systems. Any
time you need a distributed system to make a decision
that requires "no other process has changed this in the
meantime" - a lock, a counter increment, a leader election
vote - you need linearizability. Recognizing when a
problem requires linearizable semantics vs when eventual
consistency is sufficient is one of the key architectural
skills in distributed systems. Most data does not require
linearizability. Most coordination does.

---

### 💡 The Surprising Truth

Martin Kleppmann demonstrated in 2015 that even etcd's
linearizable reads have a subtle edge case during certain
network partition patterns. If a leader loses quorum
contact but its lease has not expired, it may continue
serving reads from its local state for the duration of
the lease (typically 150ms in etcd). This means
linearizability can be violated for up to 150ms. In
practice, this is acceptable for most use cases -
but it is why distributed lock services at Google
(Chubby) and critical coordination primitives use
additional mechanisms beyond consensus read linearity.
Perfect linearizability in the presence of Byzantine
faults (malicious nodes) is provably impossible (FLP
impossibility theorem). Every "linearizable" system
operates within assumptions about the failure model.

---

### ✅ Mastery Checklist

1. [DISTINGUISH] Given a system described as "strongly
   consistent," determine whether it is linearizable
   or merely sequentially consistent, and what test
   would reveal the difference.
2. [DESIGN] Specify whether a distributed lock, a
   unique order ID generator, and a user preference
   store each require linearizability or whether
   weaker consistency suffices.
3. [IMPLEMENT] Use etcd's linearizable read (serializably=true)
   and ZooKeeper's `sync()` + read pattern to implement
   the same lock acquisition and explain the difference.
4. [DEBUG] Given a symptom of two processes simultaneously
   holding the same distributed lock, diagnose whether
   the cause is stale leader reads, async replication
   on failover, or clock skew.
5. [EXPLAIN] The difference between linearizability and
   serializability, and why a system can be serializable
   without being linearizable, with a concrete example.
