---
id: SYD-039
title: Distributed Locks
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-019
used_by: SYD-040
related: SYD-019, SYD-038, SYD-040, SYD-062
tags:
  - architecture
  - concurrency
  - distributed-systems
  - coordination
  - advanced
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 39
permalink: /syd/distributed-locks/
---

# SYD-039 - Distributed Locks

⚡ TL;DR - A distributed lock (distributed mutex)
ensures only one process across multiple machines
can execute a critical section at a time. Unlike a
single-machine mutex (in-memory), a distributed lock
uses an external coordination service (Redis, ZooKeeper,
etcd) as the shared state. Correct distributed locks
require: atomicity of acquire+expire, fencing tokens
to handle lock holder crashes, and careful TTL tuning
to balance safety against availability. They are one
of the most subtle and failure-prone primitives in
distributed systems.

| #039 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Redundancy and Failover | |
| **Used by:** | Leader-Follower Pattern | |
| **Related:** | Redundancy and Failover, Idempotency Key, Leader-Follower Pattern, Saga Pattern | |

---

### 🔥 The Problem This Solves

**THE DISTRIBUTED RACE CONDITION:**
An e-commerce site has 10 application servers. A
flash sale has 1 item in stock. Two users buy at
exactly the same time. Each server independently
checks: "is stock > 0?" Both see stock=1. Both
decrement. Stock becomes -1. Two orders placed for
one item. The system oversold by 100%.

A single-machine mutex would prevent this: only one
thread checks-and-decrements at a time. With 10
servers sharing a database: the in-process mutex
does not protect across servers. A distributed lock
that only one server can hold at a time restores
the mutual exclusion guarantee.

---

### 📘 Textbook Definition

**Distributed lock (distributed mutex):** A synchronization
primitive that provides mutual exclusion for a shared
resource across multiple processes on multiple machines.
Only the process holding the lock may execute the
critical section. All other processes must wait or fail-fast.

**Key components:**
- **Lock acquisition:** Atomic check-and-set on shared
  state (Redis SETNX, ZooKeeper ephemeral node, etcd
  compare-and-swap)
- **Lock expiry (TTL):** Automatic release if the lock
  holder crashes without releasing
- **Fencing token:** Monotonically increasing number
  issued with the lock; used to reject requests from
  processes that held an expired lock
- **Lock release:** Only the original holder may release;
  use a unique value to prevent accidental release by
  another process

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Across 10 servers, only one can hold the lock at a
time. The lock lives in Redis (or ZooKeeper, etcd).
TTL prevents permanent deadlock if the holder crashes.

**One analogy:**
> A single key to a shared bathroom in an office:
> - Any of 10 people can take the key
> - While one person has the key (holds the lock),
>   others must wait
> - Key is on a self-return timer (TTL): if someone
>   doesn't return it in 5 minutes, it resets
>
> The key is stored in Redis (not on anyone's desk).
> If the key holder's computer crashes, the timer
> returns the key automatically.
>
> Problem: if the timer fires while someone is still
> in the bathroom, the next person takes the key and
> enters. Two people in the bathroom (the fencing
> token problem). Distributed locks have this subtlety.

**One insight:**
Distributed locks are harder than they appear. A process
can hold a lock, be paused (GC pause, network partition,
VM snapshot), have its TTL expire, and then wake up
and continue operating AS IF it still holds the lock.
The fencing token pattern is the only reliable protection
against this "expired but still running" hazard.

---

### 🔩 First Principles Explanation

**REDIS DISTRIBUTED LOCK (Redlock naive vs correct):**

**NAIVE IMPLEMENTATION (incorrect):**
```
# BAD: separate commands = not atomic
EXISTS lock_key → 0 (not locked)
# [another process runs here → race condition!]
SET lock_key 1 EX 30
# Both processes think they hold the lock
```

**CORRECT IMPLEMENTATION (SET NX EX):**
```
# GOOD: atomic SET with NX (not-exists) and EX (TTL)
SET lock_key {unique_value} NX EX 30

NX = only set if not exists (atomically)
EX = expire in 30 seconds (prevents deadlock on crash)
value = unique per lock holder (for safe release)

Returns OK → lock acquired
Returns nil → lock already held; retry or fail
```

**SAFE LOCK RELEASE:**
```
# WRONG: check then delete (not atomic)
GET lock_key → compare with our value
DEL lock_key → might delete ANOTHER process's lock!

# CORRECT: Lua script (atomic check-and-delete)
if redis.call("GET", KEYS[1]) == ARGV[1] then
  return redis.call("DEL", KEYS[1])
else
  return 0
end

Why: if TTL expired, another process may have
acquired the lock. Without checking our value,
we'd delete their lock. Lua script ensures we
only delete if we still own it.
```

**THE FENCING TOKEN PROBLEM:**

```
Timeline:
  t=0: Process A acquires lock (TTL=30s), token=1
  t=10: Process A is paused (GC pause, 60 seconds!)
  t=30: Lock TTL expires
  t=31: Process B acquires lock, token=2
  t=35: Process B writes to database with token=2
  t=70: Process A resumes (was paused for 60s)
  t=70: Process A writes to database with token=1
         → OVERWRITES Process B's write!
  
Fencing token fix:
  Lock service issues monotonically increasing token
  Database validates: reject writes with token ≤
  last seen token.
  
  At t=70, database sees token=1 < 2 → reject.
  Process A's write is rejected. Data safe.
```

**WHEN DISTRIBUTED LOCKS ARE (AND ARE NOT) APPROPRIATE:**

```
Use distributed locks when:
  1. Exactly one operation must run at a time
     (inventory decrement, scheduled job)
  2. Short critical section (< lock TTL / 2)
  3. Failure to acquire = fail-fast is acceptable
  
Avoid distributed locks when:
  1. Long operations (risk of TTL expiry mid-execution)
  2. High contention (100 processes competing for 1 lock)
     → Use optimistic locking or idempotency keys instead
  3. Strong consistency guarantees needed
     → Use a real consensus system (etcd, ZooKeeper)
     (Redis Redlock has documented weaknesses with
     clock skew and network partitions)
```

---

### 🧪 Thought Experiment

**SCENARIO: Distributed cron job - "run exactly once"**

A system has 5 application servers. A cron job should
run every minute to process outstanding payments.
If it runs on all 5 servers simultaneously: 5x
duplicate processing. Idempotency handles duplicates,
but the overhead is wasteful and can cause rate limit
issues on the payment processor.

**Solution: Distributed lock for leader election**
At the start of each minute:
1. All 5 servers attempt: `SET cron:payment_processor
   {server_id} NX EX 55`
2. Exactly one server acquires the lock (the "leader")
3. Only the lock holder runs the cron job
4. After job completion: release the lock
5. If job runs more than 55s: next minute, job may
   run on a different server (TTL ensures no permanent
   monopoly by crashed server)

**The TTL math:**
Job takes ~30 seconds. TTL = 55 seconds. Safety margin:
25 seconds. If a server crashes mid-job at t=30, the
lock expires at t=55. The next server picks up the
work at t=55. Maximum delay for recovery: 25 seconds.
If job takes > 55 seconds: lock may expire and two
servers run simultaneously. Prevent this: job should
complete in < TTL/2 (< 27 seconds). If job takes
longer: use a heartbeat to extend the TTL.

---

### 🧠 Mental Model / Analogy

> Distributed lock is like a talking stick in a meeting:
> - One stick, shared by all participants (stored
>   centrally in Redis)
> - Only the person holding the stick may speak
>   (execute the critical section)
> - If someone holds the stick and leaves the room
>   (crashes), a timer automatically returns the stick
>   to the center (TTL)
>
> Fencing token problem:
> - If someone takes the stick, falls asleep, the stick
>   is returned by timer, someone else gets it and
>   speaks, then the original person wakes up and
>   tries to talk over them
> - The facilitator (database) checks: "whose stick
>   turn number is this?" and tells the woken-up
>   person "your turn has passed; silent please"

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
Across multiple servers, only one can "hold the lock"
at a time. Others must wait. The lock is stored in
a shared system (Redis) so all servers can see it.

**Level 2 - How to use it (junior developer):**
Use a battle-tested library: `redlock-py` (Python),
`redlock` (Node.js), `Redisson` (Java). Do not implement
from scratch. The library handles atomic acquire,
TTL, and safe release. Set TTL to at least 3x your
expected critical section duration.

**Level 3 - How it works (mid-level engineer):**
`SET key value NX EX ttl` is the atomic Redis command.
NX = set only if key not exists. EX = auto-expire.
Release via Lua script (check value == mine, then DEL).
Heartbeat extension: if operation may exceed TTL, use
a background thread to extend TTL before it expires.

**Level 4 - Why it was designed this way (senior/staff):**
Redis Redlock (multi-node distributed lock) is
documented by Martin Fowler and contested by Redis's
author Salvatore Sanfilippo: Redlock uses N independent
Redis instances and requires quorum (majority) for
acquisition. This provides stronger guarantees than
a single Redis instance but still has known weaknesses
with clock skew. For financial systems requiring
strong consistency: use etcd (Raft-based) or ZooKeeper
(ZAB-based) instead. They provide stronger consistency
but have higher latency.

**Level 5 - Mastery (distinguished engineer):**
Martin Kleppmann's analysis ("How to do distributed
locking" 2016) demonstrates that distributed locks
over asynchronous networks cannot provide perfect
safety guarantees. A process can hold a lock, be
paused (GC, VM snapshot, network partition), TTL
expires, another process acquires the lock, then
the first process resumes - now two processes
simultaneously believe they hold the lock. The fencing
token is the only known mitigation. This is why
distributed locks should be used for efficiency
(reduce duplicate work) not safety (prevent incorrect
state mutations that require fencing at the storage
layer). For true safety: use optimistic locking at
the database (version column + compare-and-swap) or
consensus protocols (Raft, Paxos).

---

### ⚙️ How It Works (Mechanism)

**Redis distributed lock acquire/release:**

```
┌──────────────────────────────────────────────────────┐
│ ACQUIRE                                             │
│                                                      │
│  Process A: SET lock:{resource} {uuid_A} NX EX 30  │
│  → OK: lock acquired (uuid_A stored, TTL=30s)       │
│                                                      │
│  Process B: SET lock:{resource} {uuid_B} NX EX 30  │
│  → nil: lock held by A; retry or fail-fast          │
│                                                      │
│ CRITICAL SECTION                                    │
│  Process A executes protected code (< 30s)          │
│                                                      │
│ RELEASE (Lua script, atomic)                        │
│  GET lock:{resource} == uuid_A?                     │
│    YES: DEL lock:{resource}                         │
│         (lock released for next process)            │
│    NO:  do nothing                                  │
│         (TTL expired, another process holds it)     │
│                                                      │
│ If A crashes before RELEASE:                        │
│  TTL expires at 30s → lock auto-released            │
│  Process B can now acquire                          │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Redis distributed lock (Python)**
```python
import redis
import uuid
import time
from contextlib import contextmanager

r = redis.Redis(host="redis", port=6379)

# Lua script for atomic release
RELEASE_SCRIPT = """
if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("DEL", KEYS[1])
else
    return 0
end
"""
_release_script = r.register_script(RELEASE_SCRIPT)

@contextmanager
def distributed_lock(
        resource: str,
        ttl_seconds: int = 30,
        retry_interval: float = 0.1,
        max_retries: int = 30):
    """
    Context manager for distributed lock.
    Raises RuntimeError if lock cannot be acquired.
    """
    lock_key = f"lock:{resource}"
    lock_value = str(uuid.uuid4())  # unique per holder
    acquired = False

    try:
        for attempt in range(max_retries):
            # Atomic: SET lock_key lock_value NX EX ttl
            result = r.set(
                lock_key, lock_value,
                nx=True, ex=ttl_seconds
            )
            if result:
                acquired = True
                break
            time.sleep(retry_interval)

        if not acquired:
            raise RuntimeError(
                f"Could not acquire lock: {resource}")

        yield lock_value  # provide token to caller

    finally:
        if acquired:
            # Atomic release: only delete if we own it
            _release_script(
                keys=[lock_key],
                args=[lock_value]
            )

# Usage:
def process_inventory_order(product_id: str,
                              quantity: int):
    """Protected by distributed lock per product."""
    resource = f"inventory:{product_id}"

    with distributed_lock(resource, ttl_seconds=10):
        # Only ONE server executes this block at a time
        stock = get_stock(product_id)
        if stock < quantity:
            raise InsufficientStockError()
        deduct_stock(product_id, quantity)
        create_order(product_id, quantity)
    # Lock auto-released when block exits
```

**Example 2 - BAD: Not using atomic SET NX EX**
```python
# BAD: Non-atomic check-then-set creates race condition
def acquire_lock_BAD(resource: str) -> bool:
    lock_key = f"lock:{resource}"

    # Step 1: Check if lock exists
    if r.exists(lock_key):
        return False  # Lock is held

    # [GAP: Another process acquires lock HERE]

    # Step 2: Set the lock
    r.set(lock_key, "locked")
    r.expire(lock_key, 30)
    # Both processes might reach step 2 simultaneously!
    # Both acquire the lock. Race condition.
    return True

# GOOD: Single atomic command (as in Example 1)
def acquire_lock_GOOD(resource: str,
                       lock_value: str,
                       ttl: int = 30) -> bool:
    """Atomic acquire: SET NX EX is one operation."""
    result = r.set(
        f"lock:{resource}",
        lock_value,
        nx=True,  # only set if not exists
        ex=ttl    # auto-expire
    )
    return result is not None

# Atomic: no gap between check and set.
# Only one caller gets True.
```

**Example 3 - Distributed lock with fencing token (Java)**
```java
// Fencing token pattern for database writes
// Protects against expired-but-running lock holders

@Service
public class InventoryService {

    @Autowired
    private DistributedLockService lockService;

    public void processOrder(String productId, int qty) {
        // Acquire lock with fencing token
        LockResult lock = lockService.acquire(
            "inventory:" + productId,
            Duration.ofSeconds(30)
        );
        if (!lock.acquired()) {
            throw new LockAcquisitionException();
        }

        long fencingToken = lock.token();
        // fencingToken is monotonically increasing
        // (incremented each time this lock is acquired)

        try {
            // Pass fencing token to ALL downstream writes
            int stock = inventoryRepo.getStock(productId);
            if (stock < qty) {
                throw new InsufficientStockException();
            }
            // DB write includes fencing token for validation
            inventoryRepo.deductStock(
                productId, qty, fencingToken);
            // DB rejects write if fencingToken < last seen
        } finally {
            lockService.release(lock);
        }
    }
}

// In InventoryRepository:
// UPDATE inventory SET stock = stock - ?
// WHERE product_id = ?
//   AND last_fence_token < ?  -- reject stale lock holders
// If 0 rows updated: write rejected (stale token)
```

---

### ⚖️ Comparison Table

| Approach | Atomicity | Consistency | Fencing | Use Case |
|---|---|---|---|---|
| **Redis SETNX** | Yes | Weak (single node; clock skew) | No | Low-stakes coordination, rate limiting |
| **Redis Redlock** | Yes | Medium (quorum of N nodes) | No | Distributed leader election, job coordination |
| **ZooKeeper ephemeral** | Yes | Strong (ZAB consensus) | Yes (sequential node ID) | Production critical locks |
| **etcd (compare-and-swap)** | Yes | Strong (Raft) | Yes (lease ID) | Production critical locks |
| **DB optimistic lock** | N/A | Strong | Implicit (version) | Low-contention resource protection |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Redis distributed locks are safe for all use cases | Redis single-node locks can fail on network partitions and clock skew. For safety-critical operations (financial transactions), use a Raft-based consensus system (etcd, ZooKeeper) or database optimistic locking with fencing. |
| Lock TTL can be set to a large value "to be safe" | A very long TTL means a crashed process holds the lock for a very long time, blocking all other processes. TTL = minimum time to detect failure. Set it to the minimum that prevents permanent deadlock (3-5x expected operation time). |
| Distributed locks guarantee exactly-once execution | Distributed locks reduce duplicate execution likelihood but cannot guarantee it due to the GC pause / network partition problem (the fencing token problem). For exactly-once guarantees: use idempotency keys at the resource layer, not only at the lock layer. |

---

### 🚨 Failure Modes & Diagnosis

**Lock Not Released (Process Crash Mid-Critical-Section)**

**Symptom:**
At 2am, the payment processing server crashes during
a lock hold (power failure). The cron job stops running.
All subsequent cron attempts see the lock as held.
No payments are processed for 30 seconds (until TTL).
Operations team is paged for a "payments outage."

**Diagnosis:**
```python
# Check if lock is stuck (TTL not set correctly)
ttl = r.ttl("lock:payment_processor")
if ttl == -1:
    print("STUCK: lock has no TTL - permanent deadlock")
    # This happens if TTL was set separately (not NX EX)
    # and the SET-EXPIRE sequence was interrupted

if ttl == -2:
    print("Lock does not exist (expired or released)")

# If lock appears stuck for > expected duration:
# Check if the holder is alive
lock_holder = r.get("lock:payment_processor")
# lock_holder is the UUID or server_id of the holder
# Check if that server is responding
```

**Prevention:**
```python
# Always use SET NX EX (never SET then EXPIRE)
# SET NX EX is one atomic command: TTL is set in same
# operation as lock acquisition. Impossible to set
# without TTL, even if process crashes between SET and EXPIRE.

# NEVER: r.setnx(key, value) followed by r.expire(key, ttl)
# If crash between setnx and expire: no TTL → deadlock
# ALWAYS: r.set(key, value, nx=True, ex=ttl)  # atomic
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Redundancy and Failover` - distributed locks are
  needed because multiple nodes handle the same workload

**Builds On This (learn these next):**
- `Leader-Follower Pattern` - uses distributed locks
  for leader election
- `Idempotency Key` - complementary pattern; use both
  for truly safe distributed operations

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ ACQUIRE       │ SET key uuid NX EX ttl (atomic)          │
│               │ Returns OK=acquired, nil=already held    │
├───────────────┼──────────────────────────────────────────┤
│ RELEASE       │ Lua script: if GET key == uuid: DEL key  │
│               │ Never DEL without checking ownership     │
├───────────────┼──────────────────────────────────────────┤
│ TTL           │ Auto-expire on crash. Set = 3x operation │
│               │ duration. Never SET without TTL.         │
├───────────────┼──────────────────────────────────────────┤
│ FENCING       │ Monotonic token from lock service.       │
│               │ Storage layer rejects stale tokens.      │
├───────────────┼──────────────────────────────────────────┤
│ REDIS         │ Single node = weak. Use Redlock (N nodes)│
│               │ for medium guarantees, etcd for strong.  │
├───────────────┼──────────────────────────────────────────┤
│ DON'T USE FOR │ Long operations (> TTL risk)             │
│               │ High contention (use optimistic locks)   │
│               │ True exactly-once (use fencing + idem.)  │
├───────────────┼──────────────────────────────────────────┤
│ ONE-LINER     │ "Atomic SETNX + TTL + Lua release.      │
│               │  Fencing token for expired-but-running."│
├───────────────┼──────────────────────────────────────────┤
│ NEXT EXPLORE  │ Leader-Follower Pattern                  │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Acquire: `SET key uuid NX EX ttl` - one atomic command.
   Release: Lua script checks value matches before DEL.
   Never use separate SETNX + EXPIRE (not atomic).
2. TTL = safety net for crashed processes. Set to 3x
   expected critical section duration. If job may
   exceed TTL: use a background heartbeat to extend TTL.
3. Distributed locks are for efficiency (reduce duplicate
   work), not hard safety. For true safety: add fencing
   tokens at the storage layer to reject writes from
   expired lock holders.

**Interview one-liner:**
"Distributed locks provide mutual exclusion across multiple servers
using external coordination (Redis, etcd). The correct Redis
implementation uses a single atomic command: `SET key uuid NX EX ttl`
(NX = only if not exists, EX = auto-expire TTL). Release uses a
Lua script that checks value ownership before DEL (prevents releasing
another process's lock). Critical subtlety: a process can hold a
lock, be paused (GC pause), have its TTL expire, another process
acquires the lock, and then the original process resumes - both
believe they hold the lock. The fencing token pattern mitigates
this: a monotonically increasing token is issued with each lock
acquisition; the storage layer rejects writes with stale tokens.
For strong guarantees: use etcd (Raft) or ZooKeeper (ZAB) instead
of Redis."
