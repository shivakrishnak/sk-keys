---
id: DST-053
title: Distributed Deadlock
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-014, DST-039, DST-049
used_by: []
related: DST-033, DST-039, DST-049
tags:
  - distributed
  - deadlock
  - locking
  - wait-for-graph
  - cycle-detection
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 53
permalink: /technical-mastery/distributed-systems/distributed-deadlock/
---

⚡ TL;DR - A distributed deadlock occurs when two or
more processes across different nodes wait for each
other's resources indefinitely; it is harder to detect
than single-node deadlock because no single node has
the full wait-for graph; prevention strategies include
lock ordering, wait-die/wound-wait preemption, and
timeouts, while detection requires a distributed
edge-chasing algorithm.

---

### 📋 Entry Metadata

| #053 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Consistency, Timeout Design, Distributed Locking | |
| **Used by:** | N/A (fundamental failure mode) | |
| **Related:** | Two-Phase Commit, Timeout Design, Distributed Locking | |

---

### 🔥 The Problem This Solves

**WORLD WITH IT:**
```
Node 1: Transaction T1 holds lock on record A.
         T1 requests lock on record B (waiting).
         
Node 2: Transaction T2 holds lock on record B.
         T2 requests lock on record A (waiting).

T1 waits for T2 (on Node 2).
T2 waits for T1 (on Node 1).

Node 1 cannot detect deadlock: it only sees T1 waiting.
Node 2 cannot detect deadlock: it only sees T2 waiting.
Neither node has the full wait-for graph.

Result: T1 and T2 wait indefinitely.
Database connections exhausted.
All queries time out.
```

Single-node deadlocks are detectable by cycle detection
in the local wait-for graph. Distributed deadlocks
are not - the cycle spans multiple nodes and no single
node can see it.

---

### 📘 Textbook Definition

A **deadlock** occurs when a set of processes are
each waiting for a resource held by another process
in the set, creating a circular dependency from which
none can proceed.

**Distributed deadlock** is a deadlock where the
waiting processes are on different nodes, making the
circular dependency invisible to any single participant.

**Four Coffman conditions (all required):**
1. **Mutual exclusion:** resources held exclusively
2. **Hold and wait:** a process holds resources while
   waiting for others
3. **No preemption:** resources cannot be forcibly
   taken
4. **Circular wait:** circular chain of processes
   each waiting for the next

---

### ⏱️ Understand It in 30 Seconds

```
SINGLE-NODE DEADLOCK (visible locally):
  T1 → waiting for lock B → held by T2
  T2 → waiting for lock A → held by T1
  Cycle: T1→T2→T1 (deadlock)
  PostgreSQL detects this in pg_stat_activity
  and kills one transaction.

DISTRIBUTED DEADLOCK (not visible locally):
  Node 1: T1 waits for T3 (which runs on Node 2)
  Node 2: T3 waits for T5 (which runs on Node 3)
  Node 3: T5 waits for T1 (which runs on Node 1)
  Cycle: T1→T3→T5→T1 (deadlock)
  No single node sees the full cycle.
  All three nodes show "transaction is waiting" -
  no local deadlock, but globally deadlocked.
```

---

### 🔩 First Principles Explanation

**WAIT-FOR GRAPH:**

```
In a single node:
  Wait-for graph: directed graph
  Node = transaction
  Edge A → B = "A is waiting for a lock held by B"
  Cycle in graph = deadlock

In distributed system:
  Wait-for graph spans multiple nodes.
  Each node has a partial view.
  To detect: must merge all partial graphs and
  check for cycles globally.

EXAMPLE:
  Node 1 sees:  T1 → T3 (T3 is on Node 2)
  Node 2 sees:  T3 → T5 (T5 is on Node 3)
  Node 3 sees:  T5 → T1 (T1 is on Node 1)

  Global graph: T1 → T3 → T5 → T1 (cycle = deadlock)
  No local cycle exists. Deadlock only visible globally.
```

**DETECTION ALGORITHM (Edge Chasing):**

```
1. Each node maintains local wait-for edges.
2. When a transaction T on Node A waits for
   transaction T' on Node B:
   Node A sends a PROBE message to Node B:
   PROBE(deadlock_id, T_initiator, T_current)

3. On receiving PROBE(id, initiator, current):
   a. If current == initiator: CYCLE DETECTED
      (probe has returned to the initiator)
   b. Else: forward probe to all transactions
      that current is waiting for.

4. If cycle detected: abort one transaction
   (typically the youngest = lowest cost).
```

**PREVENTION STRATEGIES:**

```
STRATEGY 1: LOCK ORDERING
  All transactions acquire locks in the same order.
  (e.g., always lock record with lower ID first)
  Prevents circular wait (Coffman condition 4).

  PROBLEM: requires all transactions to know
  all locks upfront (not always possible).

STRATEGY 2: WAIT-DIE (non-preemptive)
  When T_old and T_new want the same lock:
  If T_old wants lock held by T_new:
    T_old waits (older transactions wait for younger)
  If T_new wants lock held by T_old:
    T_new is aborted (dies) and restarts

STRATEGY 3: WOUND-WAIT (preemptive)
  When T_old and T_new want the same lock:
  If T_old wants lock held by T_new:
    T_new is wounded (preempted/aborted)
    T_old gets the lock
  If T_new wants lock held by T_old:
    T_new waits

STRATEGY 4: TIMEOUT
  Every transaction has a max wait time.
  If waiting longer than timeout: abort and retry.
  Simple and widely used. False positives
  (aborts non-deadlocked long transactions).
  Minimum: one transaction in deadlock cycle
  eventually times out and aborts, breaking cycle.
```

---

### 🧠 Mental Model / Analogy

> Distributed deadlock is like two drivers on a
> single-lane bridge from opposite ends. Driver A
> entered from the east, Driver B from the west.
> Neither can back up (no preemption). Each waits
> for the other to move. Locally, each sees only their
> own lane and a car blocking them - they don't see
> the full situation. Deadlock detection is like a
> traffic control system that monitors both ends of
> the bridge simultaneously. Prevention is like a
> rule: "always yield to eastbound traffic first"
> (lock ordering) - so only one direction ever enters
> first.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is:**
When two or more processes each hold a resource
that another needs and all are waiting for the others
to release - nobody can proceed. In distributed
systems, the wait cycle spans multiple nodes.

**Level 2 - Why it's harder in distributed systems:**
Each node only sees its own transactions. The deadlock
cycle is invisible locally because it spans node
boundaries. You need to combine wait information from
all nodes to see the cycle.

**Level 3 - Prevention vs detection:**
Prevention (lock ordering, wait-die, wound-wait)
eliminates deadlocks by making circular waits
impossible. Detection (edge chasing, centralized
wait-for graph) finds deadlocks after they form and
resolves by aborting a transaction. Most production
databases use timeout-based detection (simplest) with
optional cycle detection for known high-contention
operations.

**Level 4 - PostgreSQL's approach:**
PostgreSQL runs a deadlock detector every 1 second
(configurable via `deadlock_timeout`). It builds the
local wait-for graph and detects cycles. For distributed
deadlocks across nodes: PostgreSQL does not natively
detect them. Distributed PostgreSQL solutions (Citus,
Aurora) have their own coordination layer. The most
common mitigation in practice: set statement_timeout
to break deadlocks via timeout.

**Level 5 - Two-phase locking and deadlock:**
2PL (Two-Phase Locking) is the standard concurrency
protocol in relational databases. It prevents anomalies
(dirty reads, etc.) but inherently allows deadlocks.
The reason: 2PL requires acquiring all needed locks
before releasing any (the "growing" and "shrinking"
phases), and doesn't require declaring all locks upfront
(unlike strict 2PL with intent locks). The combination
of 2PL + runtime lock acquisition = deadlock possible.
Alternative: Optimistic Concurrency Control (OCC),
which acquires no locks and validates at commit time,
eliminating deadlocks entirely at the cost of higher
abort rate under contention.

---

### 💻 Code Example

**Deadlock Prevention: Wrong vs Right**

```python
# BAD: Inconsistent lock order (deadlock possible)

def transfer_bad(from_account: int, to_account: int,
                 amount: float) -> None:
    lock_a = get_lock(from_account)
    lock_b = get_lock(to_account)

    with lock_a:
        # Thread A holds from_account=1, waits for to_account=2
        with lock_b:
            # Thread B holds to_account=2, waits for from_account=1
            # DEADLOCK: Thread A waits for B's lock_b
            #           Thread B waits for A's lock_a
            do_transfer(from_account, to_account, amount)
```

```python
# GOOD: Consistent lock order prevents deadlock

import threading
from contextlib import contextmanager

_account_locks: dict[int, threading.Lock] = {}
_global_lock = threading.Lock()

def get_account_lock(account_id: int) -> threading.Lock:
    with _global_lock:
        if account_id not in _account_locks:
            _account_locks[account_id] = threading.Lock()
        return _account_locks[account_id]

@contextmanager
def ordered_locks(*account_ids: int):
    """Acquire locks in deterministic order (ascending ID)."""
    sorted_ids = sorted(set(account_ids))
    locks = [get_account_lock(aid) for aid in sorted_ids]
    acquired = []
    try:
        for lock in locks:
            # Acquire with timeout (fallback: don't block forever)
            acquired_ok = lock.acquire(timeout=5.0)
            if not acquired_ok:
                raise DeadlockTimeoutError(
                    "Could not acquire lock within 5s "
                    "(possible deadlock)"
                )
            acquired.append(lock)
        yield
    finally:
        for lock in reversed(acquired):
            lock.release()

def transfer_safe(
    from_account: int,
    to_account: int,
    amount: float
) -> None:
    # Always acquires in ascending ID order:
    # transfer(1→2) and transfer(2→1) both acquire 1 then 2.
    # No circular wait possible.
    with ordered_locks(from_account, to_account):
        do_transfer(from_account, to_account, amount)
```

**Detecting with SQL (PostgreSQL)**

```sql
-- Detect blocking lock chains (local deadlock candidates):
SELECT
    blocked_locks.pid AS blocked_pid,
    blocked_activity.query AS blocked_query,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.query AS blocking_query,
    now() - blocked_activity.query_start AS blocked_duration
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity
    ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.relation = blocked_locks.relation
    AND NOT blocking_locks.granted
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity
    ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted
ORDER BY blocked_duration DESC;

-- Check for deadlocks in pg_log:
-- grep "deadlock detected" postgresql-*.log | tail -20
-- Shows: which transactions were in the deadlock,
--        which was chosen as the victim.
```

---

### ⚖️ Comparison Table

| Strategy | Prevents Deadlock? | Cost | Best For |
|---|---|---|---|
| **Lock ordering** | Yes | Design constraint (all locks known upfront) | Fixed set of resources (accounts, rows) |
| **Wait-Die** | Yes | Higher abort rate for young transactions | Read-heavy workloads |
| **Wound-Wait** | Yes | Higher abort rate for old transactions | Write-heavy workloads |
| **Timeout** | No (detects) | False positives (slow but alive) | Simple, universal fallback |
| **Optimistic CC** | Yes (no locks) | Higher abort rate under contention | Low-contention workloads |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Timeouts detect deadlocks" | Timeouts RESOLVE deadlocks by aborting after waiting too long. They do not detect whether the cause was a deadlock or just a slow operation. Cycle detection is true deadlock detection. |
| "Distributed deadlocks are rare" | Distributed deadlocks are common in any system with distributed transactions (Sagas, 2PC, distributed SQL). Cross-service lock dependency chains are easy to create accidentally. |
| "Aborting the youngest transaction is always best" | Aborting the youngest minimizes wasted work (younger = less work done). But if the same young transaction keeps being aborted by an older dominant transaction, starvation occurs. Production systems use more nuanced victim selection. |
| "NoSQL databases don't have deadlocks" | NoSQL databases that offer transactions (MongoDB multi-document, DynamoDB transactions) can have deadlocks. NoSQL databases without transactions (Cassandra, basic Redis) cannot deadlock because they don't hold locks across operations. |

---

### 🚨 Failure Modes & Diagnosis

**Deadlock Storm Under Load**

**Symptom:** Database CPU normal, but most queries
are failing with "deadlock detected" or timing out
with "statement timeout." High error rate in application.
pg_stat_activity shows many transactions waiting.

**Root Cause:** Multiple concurrent transactions
accessing the same rows in inconsistent order. High
concurrency amplifies the probability of deadlock.

**Diagnosis:**
```bash
# PostgreSQL: count deadlocks:
SELECT deadlocks FROM pg_stat_database
WHERE datname = 'mydb';
# Watch with: watch -n 1 psql -c "SELECT deadlocks..."

# Find which queries are deadlocking:
grep "deadlock detected" postgresql-*.log | \
  grep -A 5 "Process" | \
  awk '{print $NF}' | sort | uniq -c | sort -rn | head -20
# Shows most frequent deadlocked query patterns

# Check lock wait times:
SELECT
    pid,
    wait_event_type,
    wait_event,
    query,
    now() - query_start AS wait_duration
FROM pg_stat_activity
WHERE wait_event_type = 'Lock'
ORDER BY wait_duration DESC;
```

**Fix:**
1. Add consistent row ordering to queries that
   access multiple rows: `WHERE id IN (...) ORDER BY id`.
2. Use `SELECT ... FOR UPDATE` with explicit ordering.
3. Reduce transaction scope (hold locks shorter).
4. Use `SKIP LOCKED` for job queue patterns to avoid
   deadlocks between concurrent workers.

---

### 🔗 Related Keywords

**Prerequisites:** `Consistency` (DST-014),
`Timeout Design` (DST-039),
`Distributed Locking` (DST-049)

**Related:** `Two-Phase Commit` (DST-033)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ DEFINITION │ Circular wait: A waits for B, B waits for A│
│ DETECT     │ Wait-for graph cycle; probe algorithm      │
│ PREVENT    │ Lock ordering, wait-die, wound-wait        │
│ RESOLVE    │ Abort one victim; timeout as fallback      │
├────────────┼────────────────────────────────────────────┤
│ HARD PART  │ Distributed: no single node sees the cycle │
│ SOLUTION   │ Merge partial graphs or use timeouts       │
├────────────┼────────────────────────────────────────────┤
│ POSTGRES   │ deadlock_timeout=1s; auto detects local    │
│            │ SELECT FOR UPDATE ORDER BY id prevents    │
├────────────┼────────────────────────────────────────────┤
│ ONE-LINER  │ "Deadlock = circular wait; prevent with    │
│            │  consistent lock order, detect with timeout│
│            │  or cycle scan."                          │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

The deadlock prevention principle - "always acquire
resources in a consistent global order" - is one of
the most broadly applicable concurrency lessons.
It applies to: database row locking (always lock by
primary key ascending), API call chains (never let
Service A call Service B AND Service B call Service A
synchronously), message processing (never consume
from Queue A while producing to Queue B if B also
produces to A), thread synchronization (always acquire
mutex_1 before mutex_2). The pattern: identify all
the resources that can be locked, assign them a total
order, and enforce that all processes acquire them in
that order. Circular dependencies become impossible
by construction. The same principle appears in
operating systems (Banker's Algorithm), database
theory (Strict 2PL), and concurrent programming.

---

### 💡 The Surprising Truth

Deadlock detection was "solved" for single-node
databases in the 1970s, but distributed deadlock
detection remains an active research problem because
of a fundamental tension: to detect distributed
deadlocks accurately requires communication between
all participating nodes, but that communication
itself can be delayed by the same network conditions
that make distributed systems hard. The result:
most production distributed databases (including
Google Spanner) choose NOT to implement distributed
deadlock detection, relying instead on transaction
timeouts. The reasoning: at scale, the cost of
running a distributed edge-chasing algorithm
continuously (all nodes must communicate) exceeds
the cost of occasional false-positive timeouts.
The "correct" algorithm is too expensive for
practical use in high-throughput systems.

---

### ✅ Mastery Checklist

1. [EXPLAIN] Construct a 3-transaction distributed
   deadlock scenario with specific wait-for edges
   across 3 nodes. Show why no single node can detect it.
2. [IMPLEMENT] Write a transfer() function that
   acquires account locks in a consistent order to
   prevent deadlock.
3. [COMPARE] For a payment processing service with
   high concurrency, choose between lock ordering,
   wait-die, and timeout approaches. Justify.
4. [DIAGNOSE] PostgreSQL shows high deadlock count
   in pg_stat_database. Write the SQL to find which
   transactions are involved.
5. [APPLY] A Saga with 3 steps acquires a database
   lock in step 1 and another in step 3. Two concurrent
   Sagas run simultaneously. Describe the deadlock
   scenario and the fix.
