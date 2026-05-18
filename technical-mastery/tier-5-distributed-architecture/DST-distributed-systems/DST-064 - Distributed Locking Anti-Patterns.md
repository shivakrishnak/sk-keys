---
id: DST-064
title: Distributed Locking Anti-Patterns
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-047, DST-049, DST-063
used_by: []
related: DST-046, DST-047, DST-049, DST-063
tags:
  - distributed
  - locking
  - anti-patterns
  - redlock
  - fencing
  - race-conditions
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 64
permalink: /technical-mastery/distributed-systems/distributed-locking-anti-patterns/
---

⚡ TL;DR - The most dangerous distributed locking
anti-patterns are: assuming a lock held in memory
is still valid after a GC pause (the Redlock
critique), using distributed locks for safety where
idempotency is the correct solution, and failing
to use fencing tokens to protect the storage layer;
correct distributed locking requires: acquiring lock,
getting a fencing token, including the token in every
write, and having storage reject stale tokens.

---

### 📋 Entry Metadata

| #064 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Fencing Token, Distributed Locking, Lease-Based Coordination | |
| **Used by:** | N/A (safety patterns) | |
| **Related:** | Leader Election, Fencing Tokens, Distributed Locking, Leases | |

---

### 🔥 The Problem This Solves

**WORLD WITH THESE ANTI-PATTERNS:**
An engineer reads about Redis SETNX as a distributed
lock. Implements it. Works fine in testing. In
production: a 3-second GC pause causes the lock TTL
to expire while the process is still "running."
Another process acquires the lock. Both processes
now believe they hold the lock simultaneously.
Both write to the same record. Last write wins.
Data corruption. Audit trail shows two conflicting
writes with the same timestamp.

The dangerous property of distributed locks: they
appear to work correctly under normal conditions
but fail silently under the exact conditions where
they matter most (pauses, network delays, clock skew).

---

### 📘 Textbook Definition

**Distributed locking anti-patterns** are common
implementation approaches that appear correct under
normal conditions but produce unsafe behavior under
specific distributed system failure modes (GC pauses,
network delays, clock skew, process crashes).

**Key papers:**
- Martin Kleppmann, "How to do distributed locking"
  (2016): critique of Redlock, fencing token proposal
- Redis documentation: Redlock algorithm description
  and acknowledgment of limitations

---

### ⏱️ Understand It in 30 Seconds

```
ANTI-PATTERN 1: NO FENCING TOKEN
  Process A acquires lock.
  Process A: GC pause (3 seconds).
  Lock TTL expires. Process B acquires lock.
  Process A: GC ends. Still thinks it has lock.
  Process A writes to storage.
  Process B writes to storage.
  TWO SIMULTANEOUS WRITERS → data corruption.

CORRECT:
  Process A acquires lock → gets token=42.
  Process A writes: {token: 42, data: ...}
  Storage: last_seen_token=42.
  
  GC pause → lock expires → Process B gets token=43.
  Process B writes: {token: 43, data: ...}
  Storage: last_seen_token=43.
  
  Process A resumes (stale): writes {token: 42, ...}
  Storage REJECTS: 42 < last_seen_token=43.
  Process A knows it has a stale lock.

ANTI-PATTERN 2: USING LOCK FOR SAFETY-CRITICAL OPS
  Wrong: distributed lock → critical section → done.
  Right: idempotent operation + idempotency key.
  Lock reduces concurrency; idempotency ensures
  correctness even without a lock.
```

---

### 🔩 First Principles Explanation

**ANTI-PATTERN 1: REDLOCK - THE MARTIN KLEPPMANN CRITIQUE:**

```
REDLOCK PROTOCOL (Redis):
  1. Acquire lock on N Redis masters with SETNX + TTL.
  2. If majority acquired: lock is held.
  3. Perform critical section.
  4. Release lock on all masters.

STATED GOAL: Strong distributed lock.

THE PROBLEM (Kleppmann, 2016):
  Assume lock acquired at T=0, TTL=10s.
  At T=5s: GC pause starts on lock holder.
  At T=10s: lock expires. Another process acquires.
  At T=15s: GC ends. Original holder resumes.
  T=15s > T=10s: lock is EXPIRED on Redis masters.
  But original holder has no idea - it continues.
  TWO LOCK HOLDERS simultaneously.

WHY REDLOCK DOES NOT FIX THIS:
  Redlock uses wall-clock time for TTL.
  GC pauses, VM suspension, or network delays can
  cause the process to continue AFTER its lock expired.
  No wall-clock TTL can prevent this without
  external enforcement (fencing).

REDIS'S RESPONSE:
  Redlock is designed for efficiency, not safety.
  For safety-critical locks: use fencing tokens.
  For distributed coordination: use Raft-based
  systems (etcd, ZooKeeper) which provide stronger
  guarantees.
```

**ANTI-PATTERN 2: USING LOCK WHERE IDEMPOTENCY SUFFICES:**

```python
# BAD: Distributed lock to prevent duplicate payment

import redis

def process_payment_bad(order_id: str, amount: float):
    lock_key = f"payment_lock:{order_id}"
    r = redis.Redis()
    
    # Acquire lock:
    acquired = r.set(lock_key, "1", nx=True, ex=30)
    if not acquired:
        return  # Someone else processing
    
    try:
        # Critical section:
        charge_credit_card(order_id, amount)
        mark_order_paid(order_id)
    finally:
        r.delete(lock_key)
    
    # PROBLEMS:
    # 1. If GC pause after charge_credit_card but before
    #    mark_order_paid: lock expires, another process
    #    charges AGAIN. Idempotency not guaranteed.
    # 2. If charge_credit_card returns error: what does
    #    the caller retry? The lock was already released.
    # 3. If the process crashes after charging but before
    #    releasing lock: 30-second delay until retry.
```

```python
# GOOD: Idempotency key (no distributed lock needed)

def process_payment_good(order_id: str, amount: float):
    # First: check if already paid (read-your-writes):
    order = db.get_order(order_id)
    if order.status == "PAID":
        return  # Already paid; nothing to do.

    # Idempotency key = unique identifier for this attempt:
    idempotency_key = f"payment:{order_id}"

    try:
        # Stripe, Braintree, and most payment APIs support
        # idempotency keys natively:
        result = payment_gateway.charge(
            amount=amount,
            idempotency_key=idempotency_key
            # If same key is used again: returns same result,
            # does NOT charge twice.
        )
    except PaymentGatewayError as e:
        # Log and re-raise: caller can retry safely
        # (idempotency key prevents double charge)
        raise

    # Atomic update: only transition from PENDING to PAID
    db.conditional_update(
        table="orders",
        key=order_id,
        condition={"status": "PENDING"},
        update={"status": "PAID", "payment_id": result.id}
    )
    # If concurrent update happened: condition fails.
    # Caller retries: idempotency key returns same payment.
    # No duplicate charge. No race condition.
    # No distributed lock needed.
```

**ANTI-PATTERN 3: LOCK WITHOUT FENCING TOKEN:**

```python
# BAD: Lock without fencing token
# (process can continue after lock expires)

def update_user_bad(user_id: str, data: dict):
    lock = redis_lock.acquire(f"user:{user_id}", ttl=10)
    if not lock:
        raise LockAcquisitionError("Could not acquire lock")

    # === GC PAUSE HERE (10+ seconds) ===
    # Lock TTL expires. Another process acquires it.
    # Another process writes to user record.

    # THIS WRITE IS NOW STALE:
    db.update_user(user_id, data)
    # TWO PROCESSES WROTE SIMULTANEOUSLY.

    redis_lock.release(f"user:{user_id}")
```

```python
# GOOD: Lock with fencing token
# (storage layer rejects stale writes)

def update_user_good(user_id: str, data: dict):
    # Acquire lock → get fencing token:
    token = etcd_client.lock_and_get_token(
        f"/locks/user/{user_id}",
        ttl=10
    )
    # token is a monotonically increasing integer
    # (etcd's revision number or a dedicated counter)

    try:
        # Include fencing token in every write:
        success = db.update_user_with_fence(
            user_id=user_id,
            data=data,
            fencing_token=token
            # DB executes:
            # UPDATE users SET ...
            # WHERE id = :user_id
            #   AND last_write_token < :token
            # If token is stale: UPDATE affects 0 rows.
        )
        if not success:
            raise StaleTokenError(
                "Write rejected: fencing token outdated. "
                "Lock expired during operation."
            )
    finally:
        etcd_client.release_lock(f"/locks/user/{user_id}")

# DB SCHEMA CHANGE REQUIRED:
# ALTER TABLE users ADD COLUMN last_write_token BIGINT DEFAULT 0;
# CREATE INDEX ON users (id, last_write_token);
```

**ANTI-PATTERN 4: USING LOCK FOR THROUGHPUT OPTIMIZATION:**

```
MISTAKE: Using distributed lock to throttle access.
  "We use a distributed lock to limit concurrent
   database writes to 1 at a time."
  
PROBLEMS:
  - Single global lock = single point of contention
  - All writes queue on one Redis key
  - Lock acquisition time adds to every write latency
  - If Redis unavailable: all writes fail
  
BETTER: Use a per-entity lock (user, order) or
  a queue with N workers, or a semaphore with
  a configurable concurrency limit.
  
CORRECT TOOL: For throughput limiting, use:
  Rate limiter (token bucket per resource)
  Semaphore with count N (allow N concurrent)
  Not a mutual exclusion lock (count=1)
```

---

### 🧠 Mental Model / Analogy

> Using a distributed lock without a fencing token
> is like a hotel room key card with a 10-minute
> expiry. You check in, get the key card, enter the
> room. You fall asleep for 20 minutes (GC pause).
> The key card expired. The hotel re-assigned the room.
> A new guest got their key card and entered. Now two
> guests are in the same room. Your key card still
> physically opens the door (the lock says "valid
> for this room"), but the room was already given
> to someone else. A fencing token is like a room
> number that increments with each assignment.
> The room door checks: "is your room number >= the
> last room number?" and rejects stale key cards.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - The core problem:**
A distributed lock can expire while the holder thinks
it still has it (GC pause, network delay, VM suspend).
Without additional protection, two processes both
believe they hold the lock.

**Level 2 - Why Redlock doesn't fully solve it:**
Redlock acquires on N Redis masters for quorum.
But if the holder pauses AFTER acquiring, the lock
expires on Redis. Redis has no way to tell the holder
"your time is up." The holder continues, oblivious.
No amount of quorum math changes this.

**Level 3 - The fencing token solution:**
The only correct solution for safety under GC pauses:
fencing tokens. The storage layer (database) checks
that the fencing token is greater than the last seen
token. A paused process wakes up with a stale token;
the storage rejects its write. This requires storage
support, which is why it requires schema changes.

**Level 4 - Idempotency vs locking:**
Many use cases that engineers solve with distributed
locks are better solved with idempotency keys. A
lock prevents concurrent execution. An idempotency
key makes concurrent execution safe (both executions
produce the same result). Idempotency is a stronger
guarantee (works even after a lock failure) and has
lower latency (no lock acquisition overhead).

**Level 5 - When distributed locks ARE correct:**
Distributed locks are appropriate when: (1) the
operation is not idempotent and cannot be made
idempotent without significant redesign, (2) the
storage layer supports fencing tokens, (3) the lock
is needed for efficiency (not safety), and the
correctness is independently guaranteed. Example:
a distributed lock preventing two workers from
processing the same job, where processing is
idempotent and the lock only improves efficiency.

---

### 💻 Code Example

**Full Correct Lock Implementation with Fencing**

```python
# Complete correct distributed lock pattern

import etcd3
from contextlib import contextmanager
from typing import Generator

class FencedLock:
    """
    Distributed lock with fencing token support.
    Uses etcd for leader election (stronger than Redis).
    """

    def __init__(self, etcd_host: str = "localhost"):
        self.etcd = etcd3.client(host=etcd_host)

    @contextmanager
    def acquire(
        self, key: str, ttl: int = 30
    ) -> Generator[int, None, None]:
        """
        Acquire lock and yield fencing token.
        Fencing token = etcd revision (monotonically increases
        with every write to the cluster).
        """
        # Create a lease for TTL-based expiry:
        lease = self.etcd.lease(ttl)

        # Attempt atomic lock acquisition:
        # (compare-and-swap: only create if key doesn't exist)
        success, response = self.etcd.transaction(
            compare=[self.etcd.transactions.version(key) == 0],
            success=[
                self.etcd.transactions.put(
                    key, "locked", lease=lease
                )
            ],
            failure=[]
        )

        if not success:
            raise LockAcquisitionError(
                f"Lock {key} already held by another process"
            )

        # Fencing token = etcd cluster revision after lock put:
        # (Every successful write increments the revision)
        fencing_token = response.header.revision

        try:
            yield fencing_token
            # Caller uses fencing_token in all storage writes
        finally:
            # Release lock:
            self.etcd.delete(key)
            lease.revoke()


# Storage layer: DB write with fencing token check
def write_with_fencing(
    db_conn,
    table: str,
    record_id: str,
    data: dict,
    fencing_token: int
) -> bool:
    """
    Write data only if fencing_token > last_write_token.
    Returns False if write was rejected (stale lock).
    """
    # Requires schema: ALTER TABLE ... ADD last_write_token BIGINT
    result = db_conn.execute(
        f"""
        UPDATE {table}
        SET data = :data,
            last_write_token = :token
        WHERE id = :id
          AND last_write_token < :token
        """,
        {"data": data, "token": fencing_token, "id": record_id}
    )
    return result.rowcount > 0


# Usage:
lock = FencedLock()
try:
    with lock.acquire("/locks/document/doc-123") as token:
        # Got the lock. token is monotonically increasing.
        success = write_with_fencing(
            db_conn, "documents",
            "doc-123", {"content": "..."}, token
        )
        if not success:
            # Lock expired during operation (GC pause etc)
            raise StaleOperationError(
                "Write rejected: lock was stale"
            )
except LockAcquisitionError:
    # Lock already held; implement retry or return busy
    pass
```

---

### ⚖️ Comparison Table

| Approach | Safe Against GC Pause? | Safe Against Network Delay? | Requires Schema Change? |
|---|---|---|---|
| **Redis SETNX only** | No | No | No |
| **Redlock** | No | Partially | No |
| **etcd lock (ephemeral)** | No | Yes (quorum) | No |
| **etcd lock + fencing token** | Yes | Yes | Yes (last_write_token column) |
| **Idempotency key** | Yes | Yes | No |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "Redlock is safe for mutual exclusion" | Redlock provides quorum-based lock acquisition, reducing the chance of two processes holding the lock simultaneously. But under GC pauses or VM suspend, the lock can expire while the holder continues. Redlock does not prevent this. It is safe for efficiency (reducing duplicate work), not for safety-critical mutual exclusion. |
| "etcd locks are perfectly safe" | etcd locks (ephemeral keys) provide stronger guarantees than Redis SETNX. But GC pauses can still cause a holder to continue after its lock expired. Without fencing tokens, the storage layer cannot reject stale writes from the paused holder. |
| "Fencing tokens require a new DB table" | You need ONE additional column per table that needs fencing protection. This is a targeted schema change, not a new table. Alternatively, use a compare-and-swap that includes the fencing token in the WHERE clause. |
| "Distributed locks are always wrong" | They are not wrong; they are misused. Correct uses: reducing duplicate work in queue processing (efficiency, not safety), coordinating cluster-level operations where idempotency is guaranteed, and feature flag rollouts where the lock protects configuration reads. |

---

### 🚨 Failure Modes & Diagnosis

**Double-Write Despite Lock**

**Symptom:** Audit log shows two writes to the same
record within milliseconds of each other, from two
different processes. Both believed they held the lock.
The first write was overwritten by the second without
a conflict.

**Root Cause:** Process A held a Redis lock. Process
A experienced a JVM GC pause (8 seconds). Redis lock
TTL (5 seconds) expired. Process B acquired the lock.
Process A's GC ended; Process A continued writing.
No fencing token → storage accepted both writes.

**Diagnosis:**
```bash
# Check GC pause duration from JVM logs:
grep "GC pause" /var/log/app/gc.log | \
  awk '{print $NF}' | sort -n | tail -10
# Long pauses (>lock_ttl) = GC-caused lock expiry

# Check Redis lock acquisition/release logs:
redis-cli MONITOR | grep "lock:"
# Look for: two SETNX commands for same key
# without a DELETE between them

# Check if fencing token was used:
grep "last_write_token" db_audit_log.sql
# If no last_write_token in WHERE clause: fencing missing
```

**Fix:**
1. Add fencing tokens (last_write_token column to DB).
2. Use G1GC or ZGC for Java (lower pause times).
3. Set lock TTL >> max expected GC pause (not a fix,
   but reduces frequency).
4. Or: redesign using idempotency keys instead of
   distributed locks for this use case.

---

### 🔗 Related Keywords

**Prerequisites:** `Fencing Token` (DST-047),
`Distributed Locking` (DST-049),
`Lease-Based Coordination` (DST-063)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ ROOT CAUSE │ GC pause/VM suspend → lock expires while  │
│ OF BUGS    │ holder continues                          │
├────────────┼────────────────────────────────────────────┤
│ REDLOCK    │ Efficiency tool; NOT a safety tool        │
│ TRUTH      │ Under GC pause: still fails              │
├────────────┼────────────────────────────────────────────┤
│ FENCING    │ Token in every write;                     │
│ PATTERN    │ DB: WHERE last_write_token < :token       │
│            │ DB rejects stale writes automatically     │
├────────────┼────────────────────────────────────────────┤
│ PREFER     │ Idempotency keys when operation is        │
│ INSTEAD    │ retryable: no lock needed for safety      │
├────────────┼────────────────────────────────────────────┤
│ ONE-LINER  │ "Distributed lock = reduce duplicate work;│
│            │  fencing token = enforce correctness."   │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

The Redlock critique illustrates a general principle:
a mechanism designed for efficiency should not be
repurposed for safety. Redlock was designed to reduce
the probability of two processes holding a lock
simultaneously (efficiency: usually only one process
does the work). When used as a safety mechanism
("only one process EVER writes"), it fails under GC
pauses. The safety guarantee requires independent
enforcement (fencing tokens at the storage layer),
not just probability reduction at the lock layer.
This principle transfers to: API rate limiting (reduces
load; doesn't prevent all overload - need load shedding
for safety), optimistic locking (reduces conflicts;
doesn't prevent all conflicts - need retry handling),
and circuit breakers (reduces load on failing service;
doesn't prevent all calls - need health checks).
Every efficiency mechanism needs a corresponding
safety mechanism for failure cases.

---

### 💡 The Surprising Truth

The Redis documentation for Redlock explicitly states
that it is not suitable for safety-critical applications.
This was clarified after Martin Kleppmann published
his critique in 2016 and Salvatore Sanfilippo (Redis
creator) responded. The conclusion: use fencing
tokens for safety. Despite this, many engineering
teams still implement Redlock-style locks for safety-
critical operations (payment processing, inventory
deduction, job deduplication) without fencing tokens.
The reason: fencing tokens require storage-side support
(schema change, WHERE clause), which many teams
avoid as "over-engineering." The cost of this decision
is usually discovered during a post-mortem after
a production double-charge or data corruption incident.
The fencing token pattern is not over-engineering;
it is the correct solution for the problem.

---

### ✅ Mastery Checklist

1. [EXPLAIN] Construct the scenario where Redlock
   fails under GC pause. Walk through the timeline:
   lock acquisition, pause start, TTL expiry,
   second acquisition, pause end, concurrent writes.
2. [IMPLEMENT] Add a fencing token to a distributed
   lock: the lock grants a token, the DB write
   includes `WHERE last_write_token < :token`.
   Write a test that proves a GC-paused writer
   is correctly rejected.
3. [COMPARE] For a job queue where duplicate processing
   must be prevented: should you use a distributed
   lock or an idempotency key? Design the idempotency
   key approach.
4. [IDENTIFY] Review this code: `lock = redis.set(key, ttl=30); do_critical_work(); redis.delete(key)`. List all the ways this can fail in production.
5. [DECIDE] Three scenarios: (a) prevent duplicate
   email send, (b) prevent double database write,
   (c) prevent two workers processing same job.
   For each: distributed lock, idempotency key, or both?
