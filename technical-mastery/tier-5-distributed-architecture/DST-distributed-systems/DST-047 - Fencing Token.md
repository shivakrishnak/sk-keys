---
id: DST-047
title: Fencing Token
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★☆
depends_on: DST-046, DST-048, DST-049
used_by: []
related: DST-041, DST-046, DST-048, DST-049
tags:
  - distributed
  - fencing
  - leader-election
  - distributed-locking
  - safety
status: complete
version: 4
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Mastery"
nav_order: 47
permalink: /technical-mastery/distributed-systems/fencing-token/
---

⚡ TL;DR - A fencing token is a monotonically increasing
number issued to each new lock/lease holder; it is
included in every write to shared storage, and the
storage rejects any write with a token number lower
than the highest seen; this prevents a stale lock
holder (paused leader, delayed request) from corrupting
shared state after its lock has been revoked.

---

### 📋 Entry Metadata

| #047 | Category: Distributed Systems | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Leader Election, Split-Brain, Distributed Locking | |
| **Used by:** | N/A (terminal safety mechanism) | |
| **Related:** | Raft (term = fencing token), Leader Election, Split-Brain, Distributed Locking | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**

```
Timeline:
  t=0:  Client A acquires distributed lock (lease=30s)
  t=10: Client A's JVM GC pause starts
  t=35: Lease expires (A still paused - JVM unresponsive)
  t=36: Client B acquires lock
  t=38: Client B writes X=100 to shared storage
  t=40: Client A resumes from GC pause
  t=41: A believes it still holds the lock (didn't notice
    expiry)
  t=42: A writes X=200 to shared storage
        (OVERWRITES B's value - A's lock was expired!)
  t=43: B reads X=100... but gets X=200 (corrupted by A)

RESULT: A violated the mutual exclusion guarantee
even though the locking mechanism worked correctly.
The lock expired, A just didn't know it.
```

This is the fundamental problem: a lock cannot
prevent a process that has already passed the lock
check from writing after the lock expires. The write
happens after the lock check - there is always a
window where the lock can expire between check and
write. The fencing token closes this window.

---

### 📘 Textbook Definition

A **fencing token** (also called an epoch number,
leader term, or lock token) is a monotonically
increasing integer associated with a lock or lease.
Each time a new lock is granted, the token increments.
The lock holder includes its token in every write
to the shared resource. The shared resource tracks
the highest token it has seen and rejects any write
with a lower token.

**First described:** Martin Kleppmann, in "Designing
Data-Intensive Applications" (2017), formalized this
pattern to address the fundamental limitation of
distributed locks.

---

### ⏱️ Understand It in 30 Seconds

```
WITHOUT FENCING:
  A acquires lock (token=33)
  A pauses (GC)
  Lock expires
  B acquires lock (token=34)
  B writes (no token check) → X=100
  A resumes, writes (no token check) → X=200 (WRONG)

WITH FENCING TOKEN:
  A acquires lock → receives token=33
  A pauses
  Lock expires
  B acquires lock → receives token=34
  B sends Write(X=100, token=34)
  Storage: highest_token=0 → 34≥0 → accept; store 34 as
    highest
  Storage: X=100, highest_token=34

  A resumes, sends Write(X=200, token=33)
  Storage: current highest_token=34 → 33<34 → REJECT
  A's stale write is rejected. X remains 100. Correct.
```

---

### 🔩 First Principles Explanation

**TOKEN ISSUANCE:**

```
Token source must be monotonically increasing and
durable. Options:

1. ZooKeeper zxid (transaction ID):
   Every ZooKeeper write increments a global counter.
   Lock node creation at zxid=42 → client uses 42.
   Next lock: zxid=57 (any operations in between
   also incremented the counter).
   Always increasing. Never reuses.

2. Raft term number:
   Raft increments term on every leader election.
   Each term's leader uses its term as the token.
   Old leader (term=3) vs new leader (term=4):
   new leader's term > old → old leader's writes rejected.
   etcd exposes this as the revision (modify_revision).

3. etcd revision:
   Every etcd write increments a global revision.
   Leader acquires key at revision=100 → uses 100.
   Any subsequent write to etcd increments revision.
   Next acquirer gets revision=105+ → always higher.

4. Database sequence:
   SELECT nextval('lock_epoch_seq') on each lock grant.
   Stored and returned to the lock holder.
```

**STORAGE-SIDE ENFORCEMENT:**

```sql
-- Schema: resource table with fencing
CREATE TABLE shared_resource (
    resource_id  VARCHAR(255) PRIMARY KEY,
    value        TEXT,
    last_token   BIGINT NOT NULL DEFAULT 0
);

-- Write with fencing check:
UPDATE shared_resource
SET
    value = :new_value,
    last_token = :token
WHERE
    resource_id = :resource_id
    AND last_token < :token;
-- If 0 rows updated: token is stale (rejected)
-- Caller must check rows_affected == 1

-- Alternatively: conflict error pattern
UPDATE shared_resource
SET value = :new_value, last_token = :token
WHERE resource_id = :id AND last_token < :token
RETURNING last_token;
-- If no row returned: stale token
```

**THE CRITICAL DESIGN REQUIREMENT:**

The fencing check must happen in the same atomic
operation as the write. If they are separate:

```
BAD (separate check and write):
  1. Client sends: GET last_token WHERE id=X
  2. Storage returns: 34
  3. Client checks: my_token (34) >= 34 → ok
  4. [Another client writes token=35 HERE]
  5. Client sends: UPDATE SET value=Y, last_token=34
     (now 34 < 35 → should be rejected, but check
      already passed in step 3)
  RESULT: Stale write accepted despite higher token

GOOD (atomic compare-and-swap):
  UPDATE SET value=Y, last_token=34
  WHERE last_token < 34
  -- Atomic: if another write raised token to 35,
  -- this UPDATE matches last_token < 34 condition,
  -- which is false (35 is NOT < 34) → 0 rows affected
  -- → client knows its write was rejected
```

---

### 🧠 Mental Model / Analogy

> A fencing token is like a check written from a
> numbered checkbook. Every new lock holder gets the
> next check number. When depositing a check at the
> bank (writing to shared storage), the bank records
> the highest check number it has accepted. If you
> try to deposit check #33 but the bank has already
> processed check #34, it refuses your check. Your
> check is stale - it was issued before the more
> recent holder, who already deposited their check.
> The bank doesn't know whether your check was delayed
> or fraudulent - it just knows it's older than what
> it has already seen, and old checks are not accepted.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is:**
A number that goes up every time a lock changes hands.
You include this number in your writes. The storage
only accepts writes with the CURRENT (or newer) number.
Stale writes (from old lock holders) are rejected.

**Level 2 - Why it's necessary:**
A distributed lock can expire while the holder is
paused (GC, network). The holder doesn't know this.
It wakes up and writes. Without fencing, the storage
accepts the stale write. With fencing: the new lock
holder has a higher token; the stale holder's token
is lower; the write is rejected.

**Level 3 - Where the token comes from:**
The token must come from the same system that manages
the lock (or a trusted monotonic source). ZooKeeper
uses its transaction ID (zxid). Raft uses its term.
etcd uses its global revision. The storage must
enforce the monotonic check atomically.

**Level 4 - What storage must do:**
The storage (database, file system, message broker)
must participate in fencing by checking the token
on every write. This means the storage must have
been designed with fencing support, or you must add
conditional write logic. This is not always possible
with third-party storage systems. When not possible:
use timeouts (lock TTL << acceptable write latency),
accept the brief window of double-write, or design
operations to be idempotent.

**Level 5 - Fencing in practice:**
etcd's `prev_kv` and `mod_revision` provide built-in
fencing for writes conditional on a specific revision.
Kubernetes uses resource versions as fencing tokens:
every Kubernetes resource has a `resourceVersion`
field, and all updates must include the current
version. If another update has incremented it, the
conditional update fails (HTTP 409 Conflict), forcing
the client to re-fetch and re-apply.

---

### 💻 Code Example

**Fencing Token: Wrong vs Right**

```python
# BAD: Distributed lock without fencing
# Stale lock holder can overwrite newer writes

import redis

class UnsafeLock:
    def __init__(self, r: redis.Redis, key: str, ttl: int):
        self.r = r
        self.key = key
        self.ttl = ttl

    def acquire(self) -> bool:
        # SETNX: set if not exists
        return bool(
            self.r.set(self.key, "locked", nx=True, ex=self.ttl)
        )

    def release(self) -> None:
        self.r.delete(self.key)

# Usage:
# lock = UnsafeLock(r, "order:42:lock", 30)
# if lock.acquire():
#     db.write("order", 42, new_value)  # BUG: no fencing
#     lock.release()
# If lock expires during db.write(), stale write succeeds.
```

```python
# GOOD: Fencing token issued with lock acquisition,
# enforced on storage write (PostgreSQL example)

import redis
import uuid
import time
import psycopg2
from typing import Optional

class FencedLock:
    def __init__(
        self,
        redis_client: redis.Redis,
        db_conn,
        lock_key: str,
        ttl_seconds: int = 30
    ):
        self.r = redis_client
        self.db = db_conn
        self.lock_key = lock_key
        self.ttl = ttl_seconds
        self._token: Optional[int] = None
        self._holder_id = str(uuid.uuid4())

    def acquire(self) -> Optional[int]:
        """
        Acquire lock and return fencing token.
        Returns None if lock is not available.
        Token is a monotonically increasing integer.
        """
        # Atomic: increment lock epoch and set holder
        # Using Redis Lua script for atomicity:
        script = """
        local current = redis.call('GET', KEYS[1])
        if current == false then
            -- No lock held: acquire
            local new_token = redis.call(
                'INCR', KEYS[1] .. ':epoch'
            )
            redis.call('SET', KEYS[1],
                ARGV[1], 'EX', ARGV[2])
            redis.call('SET', KEYS[1] .. ':token',
                new_token, 'EX', ARGV[2])
            return new_token
        end
        return nil
        """
        result = self.r.eval(
            script,
            1,
            self.lock_key,
            self._holder_id,
            self.ttl
        )
        if result is not None:
            self._token = int(result)
        return self._token

    def write_with_fencing(
        self,
        resource_id: str,
        new_value: str
    ) -> bool:
        """Write to storage only if fencing token is valid."""
        if self._token is None:
            raise RuntimeError("Must acquire lock before writing")

        cursor = self.db.cursor()
        cursor.execute(
            """
            UPDATE shared_resources
            SET value = %s, last_token = %s
            WHERE resource_id = %s
              AND last_token < %s
            """,
            (new_value, self._token, resource_id, self._token)
        )
        self.db.commit()
        rows_affected = cursor.rowcount

        if rows_affected == 0:
            # Token was rejected: stale write
            return False
        return True

    def release(self) -> None:
        """Release lock (voluntary)."""
        if self._token is not None:
            script = """
            if redis.call('GET', KEYS[1]) == ARGV[1] then
                redis.call('DEL', KEYS[1])
                redis.call('DEL', KEYS[1] .. ':token')
                return 1
            end
            return 0
            """
            self.r.eval(
                script, 1, self.lock_key, self._holder_id
            )
            self._token = None
```

---

### ⚖️ Comparison Table

| Mechanism | Prevents stale write | Requires storage support | Source |
|---|---|---|---|
| **Fencing token** | Yes | Yes (conditional write) | Lock service |
| **TTL only** | Partially (reduces window) | No | N/A |
| **Idempotency** | No (but safe to retry) | No | Application |
| **Raft term** | Yes (built-in) | Yes (Raft leader check) | Raft election |
| **Kubernetes resourceVersion** | Yes | Yes (K8s API server) | etcd revision |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| "A short TTL eliminates the need for fencing" | A short TTL reduces the window but doesn't eliminate it. A 100ms TTL with a 200ms GC pause still allows a stale write. Fencing is the only true solution. |
| "The lock holder can detect its own lock expiry" | Not reliably. A GC pause means the JVM is completely stopped - it cannot detect anything during the pause. By the time it resumes, arbitrary time may have passed. |
| "Fencing requires a special distributed lock service" | Any monotonically increasing source works. Database sequences, Raft terms, etcd revisions. The requirement is: the token must increase on every new lock grant, and the storage must enforce conditional writes. |
| "Redis SETNX is safe for leader election" | Redis SETNX with TTL provides mutual exclusion under normal conditions but is NOT safe under network partitions or clock skew (documented in the Redlock algorithm controversy). For safety-critical leader election: use etcd or ZooKeeper. |

---

### 🚨 Failure Modes & Diagnosis

**Stale Write Bypasses Fencing (Missing Token Check)**

**Symptom:** Shared resource occasionally contains
stale data after a leader failover. Data written by
the new leader is overwritten by the old leader.

**Root Cause:** The write path does not include the
fencing token check. The storage accepts all writes
regardless of token.

**Diagnosis:**
```sql
-- Check if shared_resources table has last_token column:
\d shared_resources
-- If no last_token column: fencing not implemented

-- Check if writes actually include the token:
-- Enable query logging (PostgreSQL):
ALTER SYSTEM SET log_min_duration_statement = '0';
SELECT pg_reload_conf();
-- grep "UPDATE shared_resources" pg_log/*
-- Verify UPDATE includes WHERE last_token < :token
```

**Fix:** Add conditional update to every write that
requires fencing protection. Wrap in a helper function
that always enforces the check. Write an integration
test that simulates a stale token write and verifies
it is rejected.

---

### 🔗 Related Keywords

**Prerequisites:** `Leader Election` (DST-046),
`Split-Brain` (DST-048), `Distributed Locking` (DST-049)

**Built-in in:** Raft (term as fencing token),
Kubernetes (resourceVersion), etcd (mod_revision)

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WHAT       │ Monotonic integer per lock acquisition     │
│ HOW        │ Include token in every write               │
│            │ Storage rejects writes with lower token   │
├────────────┼────────────────────────────────────────────┤
│ WHY NEEDED │ Lock expiry ≠ holder immediately stops     │
│            │ GC pause or network delay → stale write   │
├────────────┼────────────────────────────────────────────┤
│ TOKEN SRC  │ ZK zxid, Raft term, etcd revision, DB seq │
│ ENFORCE    │ Atomic WHERE last_token < :token on write  │
├────────────┼────────────────────────────────────────────┤
│ CRITICAL   │ Check must be atomic with the write        │
│            │ Separate check + write has TOCTOU race    │
├────────────┼────────────────────────────────────────────┤
│ ONE-LINER  │ "Locks expire; fencing tokens are forever. │
│            │  Token ensures the latest wins."          │
└─────────────────────────────────────────────────────────┘
```

---

### 💎 Transferable Wisdom

Fencing tokens solve the most subtle correctness bug
in distributed systems: the gap between "lock check"
and "write execution." This is a distributed systems
instance of the Time-Of-Check-To-Time-Of-Use (TOCTOU)
race condition - a problem that also exists in file
system security and concurrent programming. The
solution is always the same: make the check and the
action atomic. In distributed systems: atomic
conditional write (check token + write data in one
operation). In file systems: open() with O_EXCL flag
(create + exclusive check atomic). In concurrent
code: compare-and-swap (check + swap atomic). The
pattern: "if nothing has changed since I checked,
proceed; otherwise, abort" is the universal
concurrency safety invariant.

---

### 💡 The Surprising Truth

Martin Kleppmann's formalization of fencing tokens
came directly from a public controversy about the
Redlock algorithm - Redis's author Salvatore
Sanfilippo's proposal for distributed locking across
multiple Redis instances. Kleppmann wrote a blog
post in 2016 ("How to do distributed locking") arguing
that Redlock was unsafe because it relied on timing
assumptions (millisecond-level accuracy across nodes)
that cannot be guaranteed in practice (GC pauses,
network delays, NTP jumps). He proposed fencing tokens
as the correct solution. Sanfilippo responded, arguing
that Redlock was safe enough for its intended use
cases. The debate revealed a deep truth: there is no
"safe enough" in distributed systems - either a
mechanism is provably safe under clearly stated
assumptions, or it is not. Fencing tokens make the
safety guarantee explicit and implementable.

---

### ✅ Mastery Checklist

1. [EXPLAIN] The exact sequence of events (GC pause,
   lock expiry, new holder, stale write) that fencing
   tokens prevent. Use a specific timeline with
   concrete timestamps.
2. [IMPLEMENT] A storage write function that includes
   a fencing token check using a single atomic
   UPDATE...WHERE last_token < :token.
3. [IDENTIFY] Given a distributed lock implementation
   that uses Redis SETNX but does NOT include fencing,
   describe a specific failure scenario.
4. [COMPARE] List three distributed systems that have
   fencing-like mechanisms built-in (and name the
   token in each).
5. [DESIGN] A distributed job scheduler must ensure
   only one instance runs a given job. Design the
   fencing mechanism including token issuance, token
   inclusion in job execution, and rejection logic.
