---
id: DST-049
title: Distributed Locking
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-018, DST-046, DST-047
used_by: []
related: DST-018, DST-027, DST-041, DST-046, DST-047, DST-048
tags:
  - distributed
  - locking
  - mutex
  - etcd
  - redis
  - coordination
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 49
permalink: /technical-mastery/distributed-systems/distributed-locking/
---

⚡ TL;DR - A distributed lock (distributed mutex)
ensures that only one process across multiple nodes
can access a shared resource at a time; it is
implemented via atomic compare-and-swap in a
coordination service (etcd, ZooKeeper) or Redis;
it requires a TTL to prevent deadlock on process
crash, and a fencing token to prevent stale lock
holders from corrupting data after lease expiry.

---

### 📋 Entry Metadata

| #049 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Idempotency, Leader Election, Fencing Token | |
| **Used by:** | N/A (fundamental coordination primitive) | |
| **Related:** | Idempotency, Quorums, Raft, Leader Election, Fencing Token, Split-Brain | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
An inventory service runs on 10 pods. A customer
places an order for the last item in stock. All 10
pods process concurrent requests. All 10 check
inventory: `SELECT quantity WHERE product_id=42`
→ all see quantity=1. All 10 conclude: quantity > 0,
proceed to decrement. All 10 execute `UPDATE ...
SET quantity = quantity - 1`. One pod decrements
first: quantity=0. Nine more pods decrement: quantity
becomes -9. The product is oversold 9 times. Single-
node mutex (Java `synchronized`) doesn't work across
10 separate processes. A distributed lock is needed.

---

### 📘 Textbook Definition

A **distributed lock** (distributed mutex) is a
synchronization primitive that provides mutual
exclusion across processes on different machines.
At most one process holds the lock at any time.
Other processes requesting the lock wait until the
current holder releases it.

**Required properties:**
1. **Mutual exclusion:** Only one holder at a time
2. **Deadlock freedom:** The lock is eventually
   released even if the holder crashes (via TTL)
3. **Fault tolerance:** Lock service must be highly
   available
4. **Safety under delay:** A paused holder cannot
   corrupt data after lock expiry (fencing)

---

### ⏱️ Understand It in 30 Seconds

```
WITHOUT LOCK (race condition):
  Pod A: SELECT qty=1 → proceed
  Pod B: SELECT qty=1 → proceed (concurrent)
  Pod A: UPDATE SET qty=0 (ok)
  Pod B: UPDATE SET qty=-1 (WRONG: oversold)

WITH DISTRIBUTED LOCK:
  Pod A: acquire lock("inventory:42")
         → success (token=7)
  Pod B: acquire lock("inventory:42")
         → waiting (locked by A)
  Pod A: SELECT qty=1 → proceed
  Pod A: UPDATE SET qty=0 WHERE token<7 → ok
  Pod A: release lock
  Pod B: acquires lock (token=8)
  Pod B: SELECT qty=0 → out of stock
  Pod B: release lock, return "out of stock"
  CORRECT: no oversell
```

---

### 🔩 First Principles Explanation

**IMPLEMENTATION APPROACHES:**

**Redis (SETNX-based, simpler, less safe):**

```
ACQUIRE:
  SET lock:resource_id <unique_value> NX EX <ttl_seconds>
  NX = Set if Not eXists (atomic compare-and-set)
  Returns OK if acquired, nil if lock held.
  unique_value = UUID identifying the lock holder
  (prevents a holder from releasing another's lock)

RELEASE:
  Lua script (atomic):
    if GET(lock:resource_id) == unique_value then
      DEL(lock:resource_id)
    end
  (Must be Lua script for atomicity: check+delete)

WHY UNIQUE VALUE:
  Holder A acquires lock, TTL expires, B acquires.
  A tries to release: without unique_value check,
  A would release B's lock. With check: A's DEL
  is rejected (stored value = B's UUID, not A's).

LIMITATION:
  Redis failover (Sentinel): if primary fails and
  replica promoted before replication, the key
  might not exist on replica → two holders.
  For stronger guarantees: use Redlock (5 Redis nodes)
  or prefer etcd.
```

**etcd (CAS-based, stronger guarantees):**

```
ACQUIRE:
  PUT /locks/resource_id <holder_id>
  IF NOT EXISTS (version = 0)
  With lease (TTL)

  etcd guarantees: only one PUT succeeds due to
  consensus (Raft). Multiple concurrent PUT-if-
  not-exists: exactly one wins.

RELEASE:
  DELETE /locks/resource_id
  (instant release regardless of TTL)

LEASE RENEWAL:
  Holder must renew lease before TTL expires.
  Renew at TTL/3 for safety margin.

WATCH (for waiters):
  Waiting holders watch the lock key.
  On delete event: attempt acquisition.
  To prevent herd: use sequential keys
  (like ZooKeeper ephemeral sequential nodes).
```

**ZooKeeper (ephemeral sequential, most robust):**

```
ACQUIRE:
  Create ephemeral sequential node:
  /locks/resource_id/lock-NNNNNN
  (ZK auto-assigns NNNNNN incrementing)

  Get all children, find your position.
  If you have the lowest sequence: you hold the lock.
  Otherwise: watch the node just before you.

LOCK HOLDER:
  Node with lowest sequence number holds the lock.
  ZK automatically deletes ephemeral node on disconnect.
  → automatic TTL without explicit configuration.

RELEASE:
  Delete your ephemeral node.
  ZK notifies the next-lowest watcher.

ADVANTAGE:
  ZK ephemeral deletion = natural TTL.
  Sequential nodes = fair (FIFO) lock acquisition.
  No herd effect (each waiter watches only its
    predecessor).
```

**CHOOSING THE RIGHT LOCK SERVICE:**

```
Use case          Tool         Why
-----------------------------------------------------------
Simple mutual     Redis SETNX  Fast, simple; acceptable for
exclusion                       non-critical sections
(non-critical)

Leader election,  etcd or ZK   Raft/ZAB consensus; strong
distributed jobs,               safety; survives primary
  failure
high-availability               without lock loss

Database-backed   PostgreSQL   Advisory locks:
  pg_try_advisory_lock()
locks             advisory     Transactional: released on
  rollback
                  locks        Same DB as data (no extra
                    infra)

Low-latency       Redis with   Redlock: 5 independent
  Redis nodes
at scale          Redlock      Tolerates 2 failures; more
  overhead
```

---

### 🧠 Mental Model / Analogy

> A distributed lock is like a key to a storage room
> used by employees across multiple offices. There is
> only one key. When you need access, you check out
> the key from the front desk (lock service). If
> someone else has it, you wait. When you're done,
> you return the key. The key has an expiry: if you
> don't return it within 30 minutes (TTL), the front
> desk issues a replacement key (new lock acquired
> by someone else). The catch: if you're still in the
> storage room when the key expires, and someone else
> gets the replacement key, you might both be in the
> room simultaneously. The fencing token is the room
> number stamped on the key: the room door rejects
> anyone with an older stamp.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is:**
A way for processes on different machines to take
turns accessing a shared resource. Only one process
holds the "lock" at a time. Others wait. When the
holder is done (or crashes and the TTL expires), the
next process gets the lock.

**Level 2 - Why TTL matters:**
Without TTL: if the lock holder crashes, the lock
is never released. All other processes wait forever
(deadlock). With TTL: the lock automatically expires
after a set duration, even if the holder crashes.
Cost: the TTL creates a window where the holder might
be paused (GC) and another process acquires the lock
while the original is still "working."

**Level 3 - Why fencing is required:**
See DST-047. TTL alone does not prevent stale writes.
A holder paused for longer than the TTL will resume
and attempt a write after a new holder has been
granted the lock. Without fencing: two holders can
corrupt shared state. With fencing: the storage
rejects the stale write.

**Level 4 - Redis SETNX vs etcd:**
Redis SETNX is simpler but weaker: under Redis
failover, the lock key might not be replicated to
the new primary before the failover, allowing two
processes to acquire the lock simultaneously. etcd
uses Raft: the lock key is in the consensus log;
failover preserves it. For safety-critical locks
(inventory, payment), prefer etcd or ZooKeeper.

**Level 5 - Database advisory locks:**
PostgreSQL advisory locks are an underappreciated
option. `pg_try_advisory_lock(key)` acquires a
session-level lock. Locks are released when the
session ends. No separate infrastructure needed.
Transaction-level advisory locks are released on
COMMIT/ROLLBACK. Ideal when: the locked operation
is a database transaction, and simplicity is preferred
over distributed lock service overhead.

```sql
-- PostgreSQL advisory lock:
-- Try to acquire (non-blocking):
SELECT pg_try_advisory_lock(42);  -- 42 = resource key
-- Returns true if acquired, false if locked

-- Release:
SELECT pg_advisory_unlock(42);

-- Session-level: auto-released when connection closes
-- Transaction-level:
SELECT pg_try_advisory_xact_lock(42);
-- Auto-released on COMMIT or ROLLBACK
```

---

### 💻 Code Example

**Redis Distributed Lock: Wrong vs Right**

```python
# BAD: Race condition in lock acquisition,
# no fencing, holder can release another's lock

import redis
import time

r = redis.Redis()

def bad_lock(key: str, ttl: int) -> bool:
    # BUG 1: not atomic - check and set are separate
    if r.exists(key):
        return False
    r.set(key, "locked", ex=ttl)  # Race here
    return True

def bad_unlock(key: str) -> None:
    # BUG 2: no ownership check - can release
    # another holder's lock
    r.delete(key)

# Usage:
# if bad_lock("inventory:42", 30):
#     # ... do work (but no fencing token!)
#     bad_unlock("inventory:42")
```

```python
# GOOD: Atomic SETNX with unique token,
# safe release via Lua script, fencing token support

import redis
import uuid
import time
from contextlib import contextmanager
from typing import Optional

class RedisDistributedLock:
    # Lua script: atomic check-and-delete
    _RELEASE_SCRIPT = """
    if redis.call('get', KEYS[1]) == ARGV[1] then
        return redis.call('del', KEYS[1])
    else
        return 0
    end
    """

    def __init__(self, redis_client: redis.Redis):
        self.r = redis_client

    def acquire(
        self,
        key: str,
        ttl_seconds: int,
        retry_times: int = 3,
        retry_delay: float = 0.1
    ) -> Optional[str]:
        """
        Returns a unique token (holder ID) if acquired,
        None if lock unavailable after retries.
        Include the token in all writes (fencing).
        """
        holder_id = str(uuid.uuid4())

        for _ in range(retry_times):
            # Atomic: SET if Not eXists with TTL
            result = self.r.set(
                key,
                holder_id,
                nx=True,        # Only if not exists
                ex=ttl_seconds  # Expire after TTL
            )
            if result:
                return holder_id  # Token = lock holder ID
            time.sleep(retry_delay)

        return None  # Could not acquire

    def release(self, key: str, holder_id: str) -> bool:
        """
        Release only if we still hold the lock.
        Uses Lua script for atomic check-and-delete.
        """
        result = self.r.eval(
            self._RELEASE_SCRIPT,
            1,
            key,
            holder_id
        )
        return bool(result)

    def extend(
        self,
        key: str,
        holder_id: str,
        additional_seconds: int
    ) -> bool:
        """Extend TTL (renew lease) if still holder."""
        # Only extend if we still hold it
        current = self.r.get(key)
        if current and current.decode() == holder_id:
            return bool(
                self.r.expire(key, additional_seconds)
            )
        return False

@contextmanager
def distributed_lock(
    redis_client: redis.Redis,
    resource_key: str,
    ttl_seconds: int = 30
):
    """Context manager for distributed lock."""
    lock = RedisDistributedLock(redis_client)
    token = lock.acquire(
        f"lock:{resource_key}",
        ttl_seconds
    )
    if token is None:
        raise LockAcquisitionError(
            f"Could not acquire lock for {resource_key}"
        )
    try:
        yield token  # Caller uses token for fencing
    finally:
        lock.release(f"lock:{resource_key}", token)

# Usage:
# r = redis.Redis()
# try:
#     with distributed_lock(r, "inventory:42", ttl=30) as token:
#         qty = db.get_quantity(42)
#         if qty > 0:
#             # Include token in write for fencing (if DB supports):
#             db.decrement_quantity(42, fencing_token=token)
#         else:
#             raise OutOfStockError()
# except LockAcquisitionError:
#     return "Resource busy, please retry"
```

---

### ⚖️ Comparison Table

| Implementation | Consistency | Availability | Complexity | Best For |
|---|---|---|---|---|
| **Redis SETNX** | Eventual (failover risk) | High | Low | Non-critical mutual exclusion |
| **Redis Redlock** | Stronger (5 nodes) | High | Medium | Higher-confidence Redis locking |
| **etcd CAS** | Strong (Raft) | High | Medium | Leader election, distributed jobs |
| **ZooKeeper ephemeral** | Strong (ZAB) | High | Medium | Complex coordination, fair ordering |
| **PostgreSQL advisory** | Strong (ACID) | DB-dependent | Low | DB-scoped operations, simple setups |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "A distributed lock provides ACID transactions" | A distributed lock provides mutual exclusion. ACID transactions provide atomicity, consistency, isolation, and durability. They solve different problems. A lock coordinates access; a transaction coordinates state changes. Use both for critical sections. |
| "Redis is not safe for distributed locks" | Redis SETNX is safe for many use cases. Unsafe scenarios require: (1) Redis failover during lock hold AND (2) the operation cannot tolerate a brief double-lock window. For payment or inventory: use etcd. For scheduled jobs or cache refreshes: Redis is typically fine. |
| "Locks should be held as long as needed" | Locks should be held for the MINIMUM time necessary. Long-held locks reduce throughput and increase collision probability. Design to acquire lock, do minimal work, release. Move I/O and network calls OUTSIDE the locked section when possible. |
| "TTL prevents all problems" | TTL prevents deadlock. It does NOT prevent stale writes (requires fencing). It does NOT prevent duplicate execution (requires idempotency). A complete distributed locking solution requires TTL + fencing + idempotent operations. |

---

### 🚨 Failure Modes & Diagnosis

**Lock Contention (Many Waiters, Low Throughput)**

**Symptom:** Service throughput drops significantly
under load. Response times increase 10x. Redis shows
high lock acquisition rate but low success rate.
Thread pools or goroutines backed up waiting for locks.

**Root Cause:** Too much work done while holding
the lock. All concurrent requests serialize through
the locked section. Example: lock held while making
an external HTTP call (500ms). 100 concurrent requests:
each waits for the one before it = 50-second wait
for the last request.

**Diagnosis:**
```bash
# Check average lock hold duration:
# Application metric: lock_hold_duration_ms
# If P99 > 100ms: lock is held too long

# Redis: check lock key TTL to understand hold time:
redis-cli PTTL lock:inventory:42
# If consistently high: locks held long

# Check queue depth (concurrent waiters):
# Application metric: lock_wait_duration_ms
# High wait with low hold time: high contention
# (many threads competing for few slots)
```

**Fix:**
1. Move non-critical work (HTTP calls, read-only
   queries) outside the locked section.
2. Use optimistic locking instead: `UPDATE ... WHERE
   qty = :expected_qty` (no lock needed, detect conflict
   via 0 rows updated).
3. Shard the lock: instead of one lock per resource,
   use hash-based sharding (10 locks per resource,
   requests hash to one shard → 10x throughput).

---

### 🔗 Related Keywords

**Prerequisites:** `Idempotency` (DST-018),
`Leader Election` (DST-046), `Fencing Token` (DST-047)

**Closely related:** `Split-Brain` (DST-048)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ REDIS      │ SET key value NX EX ttl                    │
│            │ Release: Lua if get==value then del        │
│ ETCD       │ CAS PUT if version==0 with lease          │
│ ZK         │ Ephemeral sequential node, watch previous  │
│ PG         │ pg_try_advisory_lock(key)                  │
├────────────┼────────────────────────────────────────────┤
│ MUST HAVE  │ TTL (deadlock prevention on crash)         │
│            │ Unique token (prevent foreign release)     │
│            │ Fencing (prevent stale write after expiry) │
├────────────┼────────────────────────────────────────────┤
│ MINIMIZE   │ Lock hold time: do minimal work inside     │
│            │ Use optimistic locking when possible      │
├────────────┼────────────────────────────────────────────┤
│ ONE-LINER  │ "Lock=mutual exclusion; TTL=deadlock-free; │
│            │  fencing=stale-write-free. Need all three."│
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

Distributed locking is often the wrong solution.
Before reaching for a distributed lock, ask: can
this be solved with optimistic locking (database
UPDATE...WHERE condition) or idempotency (duplicate
writes are safe)? Optimistic locking trades lock
contention for retry cost; it is better when conflicts
are rare (< 5% of requests). Idempotency eliminates
the need for mutual exclusion entirely in some cases.
Distributed locks are appropriate when: the operation
has external side effects (cannot be retried safely),
OR the check-and-act must be atomic, OR the operation
spans multiple systems that cannot participate in
a single transaction. The distributed lock is a
powerful tool, but its complexity cost (TTL, fencing,
renewal, contention) is significant. Reserve it for
cases where simpler mechanisms genuinely don't work.

---

### 💡 The Surprising Truth

The Redlock controversy (Kleppmann vs Sanfilippo,
2016) revealed a fundamental philosophical split in
distributed systems thinking. Kleppmann argued that
Redlock was unsafe because it relied on timing
assumptions (no GC pauses longer than TTL, bounded
clock skew). Sanfilippo argued it was safe enough
for practical use because such timing violations
are extremely rare. Both were right in different
contexts. The deeper insight from the controversy:
the correct question is not "is this lock safe?"
but "what happens when the lock fails?" If the
worst case is "a job runs twice and we have idempotent
operations" → Redis SETNX is fine. If the worst
case is "a financial transaction executes twice
charging a customer" → use etcd or database
transactions. Match the lock's safety level to the
consequence of failure, not to an abstract correctness
ideal.

---

### ✅ Mastery Checklist

1. [IMPLEMENT] Write a Redis distributed lock with
   SETNX, unique holder ID, Lua script release,
   and TTL. Test that releasing a lock you don't hold
   (expired and re-acquired by another) does nothing.
2. [EXPLAIN] Why is Lua script required for the release
   operation? Show the race condition that exists
   without it.
3. [CHOOSE] For each: inventory decrement, daily report
   generation, user session management, payment
   processing - choose the appropriate locking mechanism
   and justify.
4. [DESIGN] A distributed lock is held while calling
   an external payment API that takes 2-5 seconds.
   The TTL is 10 seconds. What can go wrong and how
   do you fix the design?
5. [COMPARE] When is optimistic locking a better
   choice than a distributed lock? Give a concrete
   example of each.
