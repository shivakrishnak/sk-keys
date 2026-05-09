---
id: SYD-039
title: Distributed Locks
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★★
depends_on: SYD-038, SYD-040
used_by: SYD-044, SYD-048
related: SYD-038, SYD-040, SYD-041
tags:
  - distributed
  - concurrency
  - reliability
  - pattern
  - deep-dive
status: complete
version: 1
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 39
permalink: /syd/distributed-locks/
---

# SYD-039 - Distributed Locks

⚡ TL;DR - A distributed lock ensures that only one process across many servers can execute a critical section at a time - preventing race conditions in systems where a single-process mutex cannot work.

| SYD-039         | Category: System Design        | Difficulty: ★★★ |
| :-------------- | :----------------------------- | :-------------- |
| **Depends on:** | SYD-038, SYD-040               |                 |
| **Used by:**    | SYD-044, SYD-048               |                 |
| **Related:**    | SYD-038, SYD-040, SYD-041     |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In a single-process system, a mutex or synchronized block protects a critical section. In a distributed system with 10 server instances, a mutex on instance A means nothing to instance B. Both can execute the same critical section simultaneously, causing double payments, inventory overselling, or duplicate job execution.

**THE BREAKING POINT:**
Horizontal scaling breaks in-process synchronization. When you add a second server to handle load, you inadvertently removed the safety guarantee that existed with one server. The same code that was correct at 1 instance becomes a race condition at 2.

**THE INVENTION MOMENT:**
Move the lock out of the process and into a shared, external store that all instances can see. The lock becomes a coordination point - an external flag that says "I am in the critical section, wait your turn."

**EVOLUTION:**
Early distributed locks used database row-level locks (`SELECT FOR UPDATE`). Redis became popular with `SETNX` (set if not exists). The Redlock algorithm generalized this to multiple Redis nodes for higher availability. ZooKeeper and etcd provide consensus-based locks. Modern systems use cloud-native options like DynamoDB conditional writes or Google Chubby's distributed lock service.

---

### 📘 Textbook Definition

A **distributed lock** is a mechanism that provides mutual exclusion across processes running on different machines. It guarantees that at most one holder can execute a guarded critical section at any point in time, even in the presence of failures, using a shared external coordination service (Redis, ZooKeeper, etcd, or database). Unlike in-process locks, distributed locks must handle network partitions, clock skew, and process crashes.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A flag in a shared store that says "someone is working here - others must wait."

**One analogy:**

> A distributed lock is like a physical key hanging outside a single bathroom in an office with multiple floors. Anyone on any floor must come get the key before entering. The shared key is the lock; the bathroom is the critical section.

**One insight:**
The hardest part of distributed locks is not acquiring them - it is handling what happens when the lock holder crashes while holding the lock. Without a timeout (TTL), the lock is held forever and the system deadlocks.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Mutual exclusion: at most one holder at a time.
2. Deadlock freedom: a crashed holder must eventually release the lock (via TTL).
3. Fault tolerance: the lock service itself must not be a single point of failure.
4. Safety: a lock holder must not accidentally hold beyond its TTL if clock skew causes TTL miscalculation.

**DERIVED DESIGN:**
Store the lock as a key in Redis with TTL. Use `SET key value NX PX ttl` (atomic: set if not exists with expiry). Value = unique owner token. Release by checking token matches before deleting (prevents releasing another holder's lock). Use Lua script for atomic check-and-delete.

**THE TRADE-OFFS:**
**Gain:** Serialization of critical sections across any number of instances; prevents double execution.
**Cost:** Requires external dependency (Redis/ZooKeeper); adds latency for lock acquire/release; introduces split-brain risk if lock service has network partition.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** You need shared state visible to all participants to coordinate access.
**Accidental:** Clock skew handling, TTL tuning, Redlock quorum math, fencing tokens.

---

### 🧪 Thought Experiment

**SETUP:** An e-commerce site has 5 app servers. A flash sale limits a product to 100 units. Inventory is stored in a DB.

**WHAT HAPPENS WITHOUT DISTRIBUTED LOCK:**
1000 users hit "Buy" simultaneously. All 5 servers read `inventory = 100`. Each server deducts 1 and writes `inventory = 99`. Result: 5 servers each sold 1 unit but all wrote 99, so the DB shows 99 remaining despite selling 5. With 1000 concurrent buyers, all seeing `inventory = 100` before any write completes, you can oversell by hundreds.

**WHAT HAPPENS WITH DISTRIBUTED LOCK:**
Before reading/writing inventory, each server must acquire `lock:product_123`. Only one server gets it. It reads 100, deducts 1, writes 99, releases lock. Next server acquires lock, reads 99, deducts 1, writes 98, releases. Perfectly serialized. Zero overselling.

**THE INSIGHT:**
A lock is not just about preventing wrong writes - it is about preventing the read-modify-write cycle from being interleaved across processes. The race condition lives in the gap between read and write, not just in the write itself.

---

### 🧠 Mental Model / Analogy

> A distributed lock is like a talking stick in a meeting. Only the person holding the stick may speak (execute the critical section). To get the stick, you must wait for the current holder to pass it. If the holder falls asleep (crashes), a timer kicks them out and the stick is available again.

- **Talking stick** = lock key in Redis/ZooKeeper
- **Holding the stick** = `SET NX` succeeds
- **Speaking** = executing the critical section
- **Passing the stick** = `DEL key` (release)
- **Timer** = lock TTL (prevents permanent hold by crashed process)
- **Unique token** = prevents one process from releasing another's lock

Where this analogy breaks down: in a real meeting, a sleeping person is obviously sleeping; in distributed systems, a slow process may still believe it holds the lock even after TTL expiry - leading to split-brain.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
When multiple workers do the same job simultaneously, they can interfere with each other. A distributed lock is a sign that says "one at a time" - each worker must check in and check out, and only one is allowed in at a time.

**Level 2 - How to use it (junior developer):**
Use Redis `SET key token NX PX 30000` to acquire (NX=only if not exists, PX=TTL in ms). On success, execute critical section, then delete key. Always set a TTL so a crashed process does not hold the lock forever. Use a unique token per acquisition to avoid releasing someone else's lock.

**Level 3 - How it works (mid-level engineer):**
Atomic `SET NX PX` prevents TOCTOU race. Owner stores a UUID as the value. Release: Lua script atomically checks value == owned UUID, then deletes. Without Lua: two commands (GET + DEL) allow another process to acquire between them. TTL must be longer than the longest expected critical section execution.

**Level 4 - Why it was designed this way (senior/staff):**
Redis Redlock uses 2N+1 Redis nodes and requires majority quorum. This prevents a single Redis failure from making the lock unavailable or granting it to two processes. However, Redlock is controversial: Martin Kleppmann showed that clock jumps or GC pauses can cause a holder to believe it still holds the lock after TTL expiry. Fencing tokens (monotonically incrementing sequence numbers returned on lock grant) solve this - the protected resource rejects requests with stale tokens.

**Expert Thinking Cues:**
- Ask: "What is the worst case execution time of the critical section? Is it shorter than the TTL?"
- Ask: "What happens if a GC pause suspends the lock holder for longer than the TTL?"
- Red flag: using distributed locks where idempotency + retries would suffice
- Red flag: TTL set to the average case, not the p99.9 worst case

---

### ⚙️ How It Works (Mechanism)

**Acquire (Redis):**
```
SET lock:resource_id <uuid> NX PX 30000
  -> OK: lock acquired
  -> nil: lock held by another - retry/fail
```

**Release (Lua script - atomic):**
```lua
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
```

**Lock flow:**
```
Process A: SET lock:X uuid_A NX PX 30000 -> OK
Process B: SET lock:X uuid_B NX PX 30000 -> nil (wait)
Process A: [executes critical section]
Process A: EVAL "check-and-del" lock:X uuid_A -> 1
Process B: SET lock:X uuid_B NX PX 30000 -> OK
Process B: [executes critical section]
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
[Process needs critical section]
         |
         v
[SET lock:key uuid NX PX ttl]  <- YOU ARE HERE
         |
         v
[Execute critical section]
         |
         v
[EVAL check-and-delete]
         |
         v
[Lock released - next waiter]
```

**FAILURE PATH:**
```
[Process acquires lock]
         |
[Process crashes mid-execution]
         |
[Lock TTL expires automatically]
         |
[Next process acquires lock]
         |
[Possible duplicate work -> use idempotency]
```

**WHAT CHANGES AT SCALE:**
At high contention (thousands of processes competing), a naive retry loop creates a thundering herd. Use exponential backoff with jitter on retry. Consider the lock granularity: `lock:product` vs `lock:product:123` - finer granularity = less contention but more lock management.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
A process that holds the lock may be paused by GC or OS scheduler after acquiring but before the critical section completes. The TTL may expire during the pause. The process resumes believing it holds the lock, but another process has already acquired it. Fencing tokens (monotonic counter returned on grant) let the resource reject stale operations.

---

### 💻 Code Example

**BAD - no TTL, no token validation:**
```python
# BAD: no expiry = deadlock on crash
# BAD: no token = can release another's lock
import redis
r = redis.Redis()

def acquire_lock(key):
    return r.setnx(key, "locked")   # no TTL!

def release_lock(key):
    r.delete(key)                   # no ownership check!
```

**GOOD - atomic acquire with TTL and token:**
```python
import redis, uuid, time

r = redis.Redis()
LOCK_TTL_MS = 30_000  # 30 seconds

def acquire_lock(key, timeout=10):
    token = str(uuid.uuid4())
    deadline = time.time() + timeout
    while time.time() < deadline:
        # Atomic: SET if not exists, with TTL
        acquired = r.set(
            key, token,
            nx=True,          # only if not exists
            px=LOCK_TTL_MS    # auto-expire
        )
        if acquired:
            return token
        time.sleep(0.1 + (time.time() % 0.05))  # jitter
    return None  # could not acquire

# Atomic release via Lua (check owner then delete)
RELEASE_SCRIPT = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
"""

def release_lock(key, token):
    script = r.register_script(RELEASE_SCRIPT)
    return script(keys=[key], args=[token])

# Usage
def process_inventory(product_id, quantity):
    lock_key = f"lock:inventory:{product_id}"
    token = acquire_lock(lock_key)
    if not token:
        raise Exception("Could not acquire lock")
    try:
        deduct_inventory(product_id, quantity)
    finally:
        release_lock(lock_key, token)
```

**How to test / verify correctness:**
- Launch 100 concurrent threads all trying to decrement a counter from 100 to 0 - assert final value is exactly 0, not negative.
- Simulate crash: acquire lock, kill process mid-section, assert lock expires after TTL and next holder can acquire.
- Test stale release: acquire with token A, expire TTL, acquire with token B, attempt release with token A - assert no-op.

---

### ⚖️ Comparison Table

| Mechanism          | Consistency | Availability | Complexity | Best for                |
| ------------------ | ----------- | ------------ | ---------- | ----------------------- |
| Redis SETNX        | Weak (single node) | High  | Low        | Best-effort locking     |
| Redlock (Redis)    | Stronger    | Medium       | Medium     | Cross-datacenter locks  |
| ZooKeeper          | Strong (CP) | Medium       | High       | Leader election         |
| etcd               | Strong (CP) | Medium       | Medium     | K8s coordination        |
| DB `SELECT FOR UPDATE` | Strong | Low (DB bound) | Low      | Simple serialization    |
| DynamoDB cond write | Strong     | High         | Medium     | Serverless locking      |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
| ------------- | ------- |
| "Redis distributed lock is always safe" | A single-node Redis lock can be lost if Redis restarts before AOF flush. Redlock over N nodes provides better guarantees but still has edge cases with clock skew. |
| "TTL should match average execution time" | TTL must exceed p99.9 execution time including GC pauses. An average-case TTL expires on slow executions and allows double execution. |
| "Releasing the lock is always safe" | Without token validation, a slow process can release the lock acquired by another process after its own TTL expired. Always validate ownership before releasing. |
| "Distributed locks are the right tool for all contention" | Optimistic concurrency (compare-and-swap, version columns) is often preferable to pessimistic locking - it scales better under low contention. |
| "A distributed lock guarantees correctness" | A lock prevents concurrent execution but not duplicate execution after TTL expiry. Combine locks with idempotency for full safety. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Deadlock due to missing TTL**

**Symptom:** System progressively hangs as all lock slots are held forever after a service instance crashes.

**Root Cause:** Lock acquired with `SETNX` but no expiry set. Crashed process never released.

**Diagnostic:**
```bash
redis-cli keys "lock:*"
redis-cli ttl lock:product_123   # returns -1 = no expiry
```

**Fix:** Always use `SET key value NX PX ttl` - never `SETNX` + `EXPIRE` (two commands, not atomic).

**Prevention:** Code review and integration test: kill process mid-lock, verify lock expires.

---

**Failure Mode 2: Lock released by wrong owner**

**Symptom:** Two processes simultaneously execute the critical section.

**Root Cause:** Process A's lock expired (slow execution), Process B acquired it. Process A completed and called `DEL key` without checking ownership, releasing B's lock. Process C then acquired and Process B was still running.

**Diagnostic:**
```bash
# Check lock value != expected owner token
redis-cli get lock:resource_123
# Compare with token held by process
```

**Fix:** Use Lua atomic check-and-delete instead of bare `DEL`.

**Prevention:** Always store unique token as lock value; always verify before release.

---

**Failure Mode 3: Lock contention thundering herd**

**Symptom:** Lock acquisition latency spikes when many processes compete. CPU spikes on Redis.

**Root Cause:** All waiters retry on fixed tight interval, creating synchronized retry storms.

**Diagnostic:**
```bash
redis-cli monitor | grep "lock:"
# Count commands per second on lock keys
```

**Fix:**
```python
# BAD: fixed retry
time.sleep(0.1)

# GOOD: exponential backoff with jitter
import random
time.sleep(0.1 * (2 ** attempt) + random.uniform(0, 0.05))
```

**Prevention:** Exponential backoff with jitter on all lock retry loops.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-038 - Idempotency Key]] - complement to locks for duplicate-safe execution
- [[SYD-040 - Leader-Follower Pattern]] - locks used in leader election

**Builds On This (learn these next):**
- [[SYD-041 - Write-Ahead Logging (System)]] - WAL + locking for durable coordination
- [[SYD-044 - Rate Limiter Design]] - rate limiters use atomic Redis operations similar to distributed locks

**Alternatives / Comparisons:**
- [[SYD-038 - Idempotency Key]] - often preferable to locking for mutation dedup
- [[SYD-040 - Leader-Follower Pattern]] - leader election is a long-lived distributed lock

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│ WHAT IT IS   │ Shared external flag ensuring    │
│              │ one-at-a-time across all servers │
├──────────────┼──────────────────────────────────┤
│ PROBLEM      │ Horizontal scaling breaks        │
│ IT SOLVES    │ in-process mutex                 │
├──────────────┼──────────────────────────────────┤
│ KEY INSIGHT  │ TTL prevents deadlock; unique    │
│              │ token prevents stale release     │
├──────────────┼──────────────────────────────────┤
│ USE WHEN     │ Critical section must run        │
│              │ exactly once across N servers    │
├──────────────┼──────────────────────────────────┤
│ AVOID WHEN   │ Low contention - use optimistic  │
│              │ concurrency instead              │
├──────────────┼──────────────────────────────────┤
│ TRADE-OFF    │ Safety vs availability vs        │
│              │ throughput (locks serialize)     │
├──────────────┼──────────────────────────────────┤
│ ONE-LINER    │ "SET NX PX ttl + Lua release =  │
│              │ safe distributed mutex."         │
├──────────────┼──────────────────────────────────┤
│ NEXT EXPLORE │ SYD-040 Leader-Follower Pattern  │
└─────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Always set a TTL - no TTL means a crashed process holds the lock forever.
2. Store a unique token as the lock value; verify ownership before release.
3. Consider whether idempotency + optimistic concurrency can replace pessimistic locking.

**Interview one-liner:** "A distributed lock uses atomic SET-if-not-exists in a shared store with a TTL - the TTL handles crash recovery and a unique token prevents stale releases."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** When shared mutable state must be accessed by N independent agents, you need a coordination primitive external to all agents. Any coordination that lives inside one agent is invisible to the others.

**Where else this pattern appears:**
- **Leader election:** Kubernetes leader election uses distributed locks in etcd - one pod holds the leader lock and renews it periodically.
- **Cron job deduplication:** Distributed cron systems (Quartz, Celery beat) use locks to ensure only one node executes a scheduled job.
- **Cache stampede prevention:** A single "fill lock" prevents all cache-miss threads from simultaneously querying the DB.

---

### 💡 The Surprising Truth

Martin Kleppmann's 2016 analysis showed that even a correctly implemented Redlock can allow two processes to simultaneously believe they hold the lock - because a GC pause longer than the lock TTL can occur between a successful `SET NX` and the start of the critical section. The holder resumes post-GC, believes the lock is valid, and proceeds - while another process has already acquired the lock. The only safe solution is fencing tokens: the resource accepts operations only from the current lock generation, rejecting stale writes.

---

### 🧠 Think About This Before We Continue

**Q1 (Root Cause):** A payment service runs on 3 instances with a 10-second lock TTL. A JVM GC pause on instance A lasts 12 seconds. Walk through the exact sequence of events and what happens to payments processed during A's pause.

*Hint:* Trace what happens to A's lock during the GC pause (TTL expires), what instance B does (acquires the lock), and what happens when A resumes (believes it holds the lock). Then explore fencing tokens as the solution.

**Q2 (Scale):** Your inventory service processes 50K transactions/second with a distributed lock per SKU. Each lock hold averages 5ms. How many concurrent lock holders can you have, and what is the maximum throughput for a single hot SKU?

*Hint:* Apply Little's Law. For a single SKU: throughput = 1 / lock_hold_time = 200 ops/sec maximum, regardless of how many servers you add. This is why lock granularity matters - explore how partitioning the lock (e.g., lock per warehouse bin) multiplies throughput.

**Q3 (Design Trade-off):** A flash sale must prevent overselling 100 units among 1M concurrent buyers. Compare distributed locking vs database optimistic concurrency (`UPDATE inventory SET qty = qty - 1 WHERE qty > 0 AND id = X`) for this scenario. Which handles the 1M concurrent burst better?

*Hint:* Analyze the lock contention model (all 1M requests queue for the same lock) vs the optimistic model (DB handles concurrent writes with row-level locking at the storage engine level, returning affected rows count). Look at how modern DBs like PostgreSQL handle this at the MVCC layer.
