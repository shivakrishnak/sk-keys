---
layout: default
title: "Distributed Locks"
parent: "System Design"
nav_order: 714
permalink: /system-design/distributed-locks/
number: "714"
category: System Design
difficulty: ★★★
depends_on: "Idempotency Key, Consistent Hashing"
used_by: "Idempotency Key, Leader-Follower Pattern"
tags: #advanced, #distributed, #concurrency, #reliability, #consistency
---

# 714 — Distributed Locks

`#advanced` `#distributed` `#concurrency` `#reliability` `#consistency`

⚡ TL;DR — **Distributed Locks** provide mutual exclusion across multiple processes or machines, ensuring only one node executes a critical section at a time — essential when in-process JVM locks can't coordinate across a distributed system.

| #714            | Category: System Design                  | Difficulty: ★★★ |
| :-------------- | :--------------------------------------- | :-------------- |
| **Depends on:** | Idempotency Key, Consistent Hashing      |                 |
| **Used by:**    | Idempotency Key, Leader-Follower Pattern |                 |

---

### 📘 Textbook Definition

A **Distributed Lock** (also called a distributed mutex) is a synchronisation mechanism that provides mutual exclusion across multiple processes running on different machines. Unlike an in-process `synchronized` block or `java.util.concurrent.Lock` (which only coordinates threads within a single JVM), a distributed lock is coordinated via an external, shared service (typically Redis, ZooKeeper, etcd, or a database) that all participating nodes can reach. Key properties: **safety** (at most one process holds the lock at any time), **liveness** (the lock is eventually acquirable — no deadlock), **fault tolerance** (lock is released if the holder crashes, via TTL or session expiry). The **Redlock algorithm** (Martin Kleppmann and Redis Labs debate) addresses multi-node Redis environments. Common use cases: cron job deduplication, inventory reservation, idempotency key processing, distributed rate limiting, leader election.

---

### 🟢 Simple Definition (Easy)

Distributed Lock: a "do not disturb" sign shared across all servers. When Server A is doing something critical (processing a payment), it hangs the sign. Servers B and C see the sign and wait. When Server A is done, it takes down the sign. All servers see the same sign because it's stored in Redis (not just in Server A's memory).

---

### 🔵 Simple Definition (Elaborated)

A flash sale: 100 users simultaneously try to buy the last 1 item in stock. Without a lock: Server A checks "is count > 0?" → yes. Server B checks "is count > 0?" → yes. Both decrement → count becomes -1 → oversold. With a distributed lock: Server A acquires lock "item_99_lock", decrements count, releases lock. Server B waits for lock, acquires it, checks count = 0, returns "sold out." Only one transaction succeeds. The lock is in Redis — shared across all servers in the fleet.

---

### 🔩 First Principles Explanation

**Distributed lock mechanisms and failure modes:**

```
REDIS-BASED DISTRIBUTED LOCK (most common):

  Acquire lock:
    SET lock:{resource} {client_id} NX EX {ttl_seconds}
    NX = Set if Not eXists (atomic check-and-set)
    EX = expire in N seconds (auto-release on holder crash)

    Returns:
      "OK" → lock acquired
      nil  → lock already held by another client

  Release lock:
    MUST verify owner before deleting (prevent accidental release of another's lock):

    Lua script (atomic check-and-delete):
    if redis.call("GET", KEYS[1]) == ARGV[1] then
      return redis.call("DEL", KEYS[1])
    else
      return 0  -- not our lock, don't delete
    end

    Why Lua for release? Race condition without atomicity:
      Client A: GET lock → "client_A" (it's mine) ← lock expires here
      Client B: acquires lock
      Client A: DEL lock ← deletes Client B's lock! (wrong!)
      Lua script: atomic check + delete → no race condition

DISTRIBUTED LOCK FAILURE MODES:

  1. LOCK HOLDER CRASHES:
     Lock stays in Redis until TTL expires.
     Recovery: automatic (TTL ensures eventual release).
     Risk: TTL too long → other clients wait unnecessarily.
     Risk: TTL too short → lock expires while legitimate holder still working.

     Rule: TTL = expected_operation_duration × 5 (generous safety margin)

  2. CLOCK SKEW (Redlock problem):
     Redis nodes on different machines have slightly different clocks.
     Redlock algorithm: acquire lock on N/2+1 nodes simultaneously.
     If clocks drift: lock expiry may be inconsistent across nodes.

     Martin Kleppmann's critique: even Redlock can fail under process pauses.
     Solution: use fencing tokens (monotonically increasing ID with lock).

  3. PROCESS PAUSE (GC pause, VM pause):
     Client A: acquires lock, starts critical section
     Client A: JVM garbage collection pause → 30 seconds
     Lock TTL: expires after 10 seconds
     Client B: acquires lock (TTL expired)
     Client A: resumes from GC pause → still thinks it holds lock → DATA CORRUPTION

     Fix: FENCING TOKENS
     When lock is acquired: server returns a monotonically increasing token N.
     Client A gets token 10. Client B gets token 11 (Client A's expired).
     Resource server: rejects writes with token < current max token.
     Client A resumes with token 10: rejected (11 > 10 → newer lock exists).

IMPLEMENTING LOCK WITH FENCING TOKEN:

  Lock Acquisition:

  // Server-side: ZooKeeper ephemeral sequential node (naturally provides fencing):
  // Create: /locks/resource_name/lock-0000000010 (sequential → always increasing)
  // Lowest node = lock holder.
  // Node deleted on session close (client crash) → automatic release.

  // Redis with counter:
  // MULTI
  //   SETNX lock:{resource} {client_id}
  //   INCR lock_token:{resource}  ← fencing token
  // EXEC
  // → returns fencing token with lock

  Resource Server (e.g., database write endpoint):
    def write_with_fencing(data, fencing_token):
      if fencing_token <= last_seen_token[resource]:
        raise StaleTokenError("Lock superseded — write rejected")
      last_seen_token[resource] = fencing_token
      # proceed with write

PRACTICAL JAVA IMPLEMENTATION (Redisson):

  // Redisson: production-grade Redis distributed lock library for Java

  @Service
  public class InventoryService {

      @Autowired
      private RedissonClient redissonClient;

      public boolean reserveItem(String itemId, String orderId) {
          // Get distributed lock for this item:
          RLock lock = redissonClient.getLock("inventory:lock:" + itemId);

          try {
              // Try to acquire lock: wait up to 5s, hold for max 30s:
              boolean acquired = lock.tryLock(5, 30, TimeUnit.SECONDS);
              if (!acquired) {
                  throw new LockAcquisitionException("Could not reserve item: " + itemId);
              }

              // Critical section (only one thread across all servers executes this):
              int currentStock = inventoryRepository.getStock(itemId);
              if (currentStock <= 0) {
                  return false;  // out of stock
              }

              // Decrement and record reservation:
              inventoryRepository.decrementStock(itemId);
              reservationRepository.save(new Reservation(itemId, orderId));
              return true;

          } finally {
              // Always release lock (even if exception thrown):
              if (lock.isHeldByCurrentThread()) {
                  lock.unlock();
              }
          }
      }
  }

WHEN NOT TO USE DISTRIBUTED LOCKS:

  AVOID distributed locks when:
  1. High-throughput path: lock acquisition is a bottleneck (Redis roundtrip = 1ms → 1,000 ops/sec per lock)
  2. Long critical sections: TTL must be very long → poor availability
  3. Cross-datacenter: lock coordination latency = RTT between datacenters (150ms+)

  ALTERNATIVES:
  - Idempotency keys: check-and-insert (upsert) pattern for duplicate prevention
  - Optimistic locking: retry on version mismatch (no lock held during operation)
  - CAS operations: Compare-and-Swap in Redis or database (atomic without explicit lock)

  // Optimistic locking (JPA): no distributed lock needed
  @Version
  private Long version;  // incremented by DB on every update

  // Thread A and B both read item (version=5)
  // Thread A updates first → version=6 → succeeds
  // Thread B tries update → WHERE version=5 → version is now 6 → no rows updated → retry
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Distributed Locks:

- Multiple servers check same resource simultaneously → race conditions
- Overselling, double-booking, double-processing
- JVM `synchronized` only works within one JVM — useless across a fleet

WITH Distributed Locks:
→ Mutual exclusion across fleet: only one server executes critical section
→ Crash safety: TTL ensures lock is released even if holder crashes
→ Distributed coordination without single-point-of-failure (Redlock, etcd, ZooKeeper)

---

### 🧠 Mental Model / Analogy

> A physical office has one conference room booking system. To book the room, you grab the physical key from a hook (acquire lock). While you have the key, no one else can use the room (mutual exclusion). If you forget to return it, the janitor reclaims it after hours (TTL-based auto-release). The key is a physical object everyone shares — not a note in your personal notebook (which no one else can see).

"Physical conference room key" = distributed lock stored in Redis (shared across servers)
"Grabbing the key" = SET lock NX EX (atomic acquire)
"No one else can use room while you hold key" = mutual exclusion (NX = only one holder)
"Janitor reclaims forgotten key" = TTL auto-expiry (lock released if holder crashes)
"Personal notebook entry" = in-process JVM lock (invisible to other servers)

---

### ⚙️ How It Works (Mechanism)

**Redis distributed lock with retry and timeout:**

```python
import redis
import uuid
import time

class DistributedLock:
    def __init__(self, redis_client: redis.Redis, resource: str,
                 ttl_seconds: int = 30):
        self.redis = redis_client
        self.key = f"lock:{resource}"
        self.ttl = ttl_seconds
        self.client_id = str(uuid.uuid4())  # unique ID for this lock holder

    def acquire(self, timeout_seconds: float = 5.0) -> bool:
        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            result = self.redis.set(
                self.key,
                self.client_id,
                nx=True,           # SET if Not eXists
                ex=self.ttl        # auto-expire
            )
            if result:
                return True        # lock acquired
            time.sleep(0.05)       # wait 50ms before retry
        return False               # timeout

    def release(self) -> bool:
        # Atomic check-and-delete via Lua:
        script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        result = self.redis.eval(script, 1, self.key, self.client_id)
        return result == 1

    def __enter__(self):
        if not self.acquire():
            raise RuntimeError(f"Could not acquire lock: {self.key}")
        return self

    def __exit__(self, *args):
        self.release()

# Usage:
r = redis.Redis()
with DistributedLock(r, "inventory:item:SKU001", ttl_seconds=10) as lock:
    stock = get_stock("SKU001")
    if stock > 0:
        decrement_stock("SKU001")
        create_reservation("order_789", "SKU001")
# Lock auto-released when `with` block exits (even on exception)
```

---

### 🔄 How It Connects (Mini-Map)

```
Race condition (multiple servers, shared resource)
        │
        ▼
Distributed Locks ◄──── (you are here)
(mutual exclusion across fleet)
        │
        ├── Idempotency Key (uses Redis lock to prevent concurrent processing)
        ├── Leader-Follower Pattern (leader election via distributed lock)
        └── ZooKeeper / etcd (dedicated distributed coordination services)
```

---

### 💻 Code Example

**Spring Boot: cron job deduplication with distributed lock:**

```java
@Component
public class DailyReportJob {

    @Autowired private RedissonClient redissonClient;
    @Autowired private ReportService reportService;

    @Scheduled(cron = "0 0 6 * * *")  // 6 AM every day
    public void generateDailyReport() {
        // All 10 server instances will trigger this cron at 6 AM.
        // Only one should actually generate the report.

        String lockKey = "cron:daily-report:" + LocalDate.now();
        RLock lock = redissonClient.getLock(lockKey);

        // Don't wait — if can't acquire immediately, another server is running it:
        boolean acquired = lock.tryLock();
        if (!acquired) {
            log.info("Daily report already running on another instance — skipping");
            return;
        }

        try {
            log.info("Generating daily report (this instance won election)");
            reportService.generateDailyReport();
        } finally {
            if (lock.isHeldByCurrentThread()) {
                lock.unlock();
            }
        }
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                                                                                                                                                                                                                                       |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A distributed lock guarantees exactly-once processing     | Distributed locks provide mutual exclusion at a point in time, but don't guarantee exactly-once processing end-to-end. If the lock holder crashes after completing work but before committing the result, the next holder may redo the work. Use idempotency keys alongside locks for exactly-once guarantees |
| Long TTL makes distributed locks safer                    | Long TTL means: if the lock holder crashes, the lock blocks other processes for the full TTL duration. A 10-minute TTL on a crashed holder = 10 minutes of unavailability. Short TTL with watchdog heartbeat (Redisson does this automatically: refreshes TTL while lock is held) is safer                    |
| Redis SETNX alone is sufficient for a distributed lock    | SETNX without EX (expiry) risks a deadlock if the holder crashes before DEL. Always use `SET key value NX EX ttl` in a single atomic command. Never do SETNX then EXPIRE as two separate commands (crash between them = permanent lock)                                                                       |
| Distributed locks solve all concurrency problems at scale | At high throughput (>1,000 ops/sec on a single resource), lock contention becomes the bottleneck — threads queue for the lock. For high-throughput scenarios, redesign to avoid shared state: use partitioning (separate lock per item/user), optimistic locking (CAS with retry), or append-only structures  |

---

### 🔥 Pitfalls in Production

**Lock TTL expires before operation completes:**

```
PROBLEM: Long database operation exceeds lock TTL

  Operation: export 100,000 rows to CSV (takes 45 seconds)
  Lock TTL: 30 seconds (seemed generous at design time)

  T=0:   Client A acquires lock, starts export
  T=30:  Lock TTL expires (Client A still working on row 50,000)
  T=30:  Client B acquires lock (TTL expired)
  T=30:  Client B starts another export
  T=45:  Client A completes — exports 100K rows (CSV file 1)
  T=75:  Client B completes — exports 100K rows (CSV file 2)

  Result: Two simultaneous exports. Storage doubled. If export writes to DB:
    duplicate rows, contention, incorrect final state.

FIX 1: WATCHDOG / LOCK REFRESH
  While holding lock: background thread refreshes TTL every TTL/3 seconds.

  // Redisson automatic lock watchdog:
  RLock lock = redissonClient.getLock("export-lock");
  lock.lock();  // TTL: default 30s, Redisson watchdog refreshes every 10s
  // As long as holder is alive: TTL keeps refreshing
  // If holder crashes: JVM dies → watchdog stops → TTL expires → auto-release

FIX 2: GENEROUS TTL
  If operation can't be interrupted: TTL = max_expected_duration × 3
  Export max: 120 seconds. TTL = 360 seconds.
  Risk: crash → 6-minute wait. Accept this for rare batch jobs.

FIX 3: REDESIGN TO NOT NEED LONG LOCK
  Export 100K rows: don't lock the full duration.
  Lock only to: (1) create export job record, (2) mark as "in progress".
  Export runs without lock (idempotent: job ID ensures only one export per day).
  Lock acquisition is instantaneous; long operation runs without lock held.
```

---

### 🔗 Related Keywords

- `Idempotency Key` — complementary: lock prevents concurrent processing; idempotency key handles serialised retries
- `Leader-Follower Pattern` — leader election implemented via distributed lock
- `ZooKeeper` — dedicated distributed coordination service providing locks, leader election, watches
- `Optimistic Locking` — alternative to distributed locks for lower-contention scenarios (CAS/version field)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ SET NX EX in Redis: atomic acquire with   │
│              │ auto-expire; Lua for atomic release        │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Inventory reservation; cron deduplication;│
│              │ leader election; idempotency key races     │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ High-throughput (>1K ops/sec per lock);   │
│              │ long critical sections without watchdog   │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Conference room key — physical object     │
│              │  everyone shares; janitor reclaims it."   │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Leader-Follower Pattern → ZooKeeper        │
│              │ → Fencing Tokens                          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You're implementing a ticket booking system. When a user selects a seat, you want to "hold" it for 10 minutes to allow them to complete checkout. Multiple server instances may receive concurrent "hold" requests for the same seat. Design the distributed lock implementation: what is the lock key? What TTL? What happens if the user's checkout takes 11 minutes? What happens if the server holding the lock crashes at T=5 minutes? How does the system recover?

**Q2.** A distributed lock has been identified as a throughput bottleneck: 5,000 requests/second all need to acquire the same "user-balance-update" lock, but Redis can only handle ~2,000 lock operations/second efficiently. Propose at least two architectural alternatives that eliminate the need for this specific distributed lock while maintaining correctness. For each alternative, describe what trade-off or consistency model you're accepting.
