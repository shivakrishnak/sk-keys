---
layout: default
title: "Distributed Locking"
parent: "Distributed Systems"
nav_order: 597
permalink: /distributed-systems/distributed-locking/
number: "597"
category: Distributed Systems
difficulty: ★★★
depends_on: "Fencing and Epoch, Leader Election"
used_by: "ZooKeeper, etcd, Redis Redlock, Database SELECT FOR UPDATE"
tags: #advanced, #distributed, #coordination, #concurrency, #safety
---

# 597 — Distributed Locking

`#advanced` `#distributed` `#coordination` `#concurrency` `#safety`

⚡ TL;DR — **Distributed Locking** is the mechanism to ensure at most one node holds exclusive access to a shared resource at a time — requiring TTL-based expiry, fencing tokens, and correct storage-level enforcement to be safe in the presence of GC pauses and network partitions.

| #597 | Category: Distributed Systems | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Fencing and Epoch, Leader Election | |
| **Used by:** | ZooKeeper, etcd, Redis Redlock, Database SELECT FOR UPDATE | |

---

### 📘 Textbook Definition

**Distributed Locking** provides mutual exclusion across distributed processes: at most one process holds the lock at any time, enabling safe access to shared resources (database records, files, external APIs with rate limits) without race conditions. Unlike in-process locks (Java synchronized, Python threading.Lock), distributed locks must handle: **GC pauses** (lock holder appears dead, lock expires, other process acquires — original holder resumes unaware); **network partitions** (lock holder unreachable, considered dead); **clock skew** (lock TTL expiry inconsistent across nodes). Safe distributed lock implementations require: (1) **TTL-based expiry** (lock auto-releases if not renewed — prevents indefinite locking on holder crash); (2) **Fencing tokens** (monotonically increasing integer returned with lock — storage systems validate token, rejecting writes from expired lock holders); (3) **Quorum-based acquisition** (for correctness under node failures — Redlock uses 5 Redis nodes). Production systems: ZooKeeper ephemeral znodes + sequential (Curator LeaderLatch, InterProcessMutex); etcd transactions with leases; Redis Redlock (controversial — see Martin Kleppmann's analysis); database advisory locks (PostgreSQL SELECT FOR UPDATE, advisory_lock). For long-running operations: fencing tokens at the resource level are essential; TTL alone is insufficient.

---

### 🟢 Simple Definition (Easy)

Distributed lock: in a distributed system, make sure only ONE server is doing a specific operation at a time. Example: "only one cron job instance should run monthly billing." Server A acquires lock ("I'm billing now"). Server B tries to acquire lock ("Someone is already billing"). Server B waits. Server A finishes, releases lock. Server B acquires lock. Problem: Server A crashes mid-billing. Lock must expire automatically (TTL) so Server B can eventually proceed. Secondary problem: Server A had GC pause, lock expired, Server B acquired lock. Server A's GC ends. Two servers billing simultaneously. Solution: fencing token (Server B has newer token; storage rejects Server A's writes).

---

### 🔵 Simple Definition (Elaborated)

Three safety properties of a correct distributed lock: (1) Mutual exclusion: at most one holder at any time. (2) Deadlock-free: if lock holder crashes, lock eventually releases (TTL). (3) Fault-tolerant: lock service should be HA (quorum-based). ZooKeeper: uses ephemeral sequential znodes. Lock acquired = created lowest-numbered znode. Lock released = znode deleted (or session expires). Fault-tolerant: ZooKeeper 3-node quorum. Fencing: zxid (transaction ID) acts as fencing token. etcd: lease-based keys + transactions. Redis: fast but controversial for correctness (no built-in fencing token).

---

### 🔩 First Principles Explanation

**Lock algorithms and failure modes:**

```
NAIVE DISTRIBUTED LOCK (WRONG — no fencing):

  Server A: acquire lock by writing "locked" to Redis with SETNX.
  Server A: does critical work.
  Server A: releases lock by deleting "locked" from Redis.
  
  FAILURE: Server A GC pause during critical work.
    T=0: Server A acquires lock (TTL=30s).
    T=25: Server A: GC pause starts.
    T=30: Lock TTL expires. Redis: key deleted.
    T=31: Server B: acquires lock (same key, new TTL=30s). Starts critical work.
    T=55: Server A: GC pause ends. Thinks it still has lock. Resumes critical work.
    T=55-61: BOTH Server A and Server B in critical section. Race condition. Corruption.

CORRECT DISTRIBUTED LOCK WITH FENCING TOKEN:

  Step 1: Acquire lock → get monotonically increasing token.
    Server A: acquires lock. Gets token=47.
    Lock TTL: 30 seconds.
    
  Step 2: Use token in every write to the protected resource.
    Server A: writes to DB with token=47.
    DB: records "last accepted token = 47."
    
  Step 3: If lock expires and Server B acquires lock → gets token=48.
    Server B: writes to DB with token=48.
    DB: records "last accepted token = 48."
    
  Step 4: GC pause ends. Server A resumes with token=47.
    Server A: writes to DB with token=47.
    DB: "Current token=48 > 47. REJECT." Server A fenced.
    
  Implementation: etcd revision as fencing token.
    Acquire: etcd lease → put key → response.Header.Revision = fencing token.
    Write to resource: include Revision in request.
    Resource: only accept if token > last_seen_token. Atomic CAS.

ZOOKEEPER DISTRIBUTED LOCK (RECIPE):

  Protocol:
    1. Client: creates ephemeral sequential znode: /lock/node-XXXX (sequential number).
       Example: creates /lock/node-0000000001.
    2. Client: gets all znodes under /lock. Sorts by sequence number.
    3. If client's znode = smallest: LOCK ACQUIRED.
    4. If not smallest: client watches the znode with the next-smaller sequence number.
       Wait for that znode to be deleted.
    5. On watch trigger: go to step 2 (re-check).
    
  Example with 3 clients:
    C1 creates /lock/node-0001. Gets all: [0001]. C1 is smallest. LOCK ACQUIRED.
    C2 creates /lock/node-0002. Gets all: [0001, 0002]. C2 watches 0001.
    C3 creates /lock/node-0003. Gets all: [0001, 0002, 0003]. C3 watches 0002.
    
  C1 releases (deletes 0001):
    C2: receives watch notification (0001 deleted). Gets all: [0002, 0003].
    C2 is now smallest (0002). LOCK ACQUIRED. Proceeds.
    C3: still watching 0002. Not disturbed.
    
  CRASH-SAFETY: C1 crashes without releasing:
    ZooKeeper: C1's session expires (heartbeat timeout).
    C1's ephemeral znode 0001: automatically deleted on session expiry.
    C2: receives watch notification. Acquires lock.
    TTL equivalent: session timeout (default: 40s in ZooKeeper).
    
  WHY SEQUENTIAL? WATCH PREDECESSOR (not all):
    Without sequential: all clients watch a single "/lock" node.
    When lock releases: ALL clients get notified. All try to acquire. "Herd effect."
    With sequential + watch predecessor: only the next-in-line client is notified.
    O(1) notifications per lock release (not O(N)).
    
  FENCING TOKEN: use C1's znode's zxid (transaction ID) as fencing token.
    zxid = monotonically increasing per ZooKeeper write.
    New lock holder always gets higher zxid than previous. Safe fencing.

REDIS DISTRIBUTED LOCK (REDLOCK):

  Correct single-node Redis lock:
    SET resource_name my_random_value NX PX 30000
    NX: only set if not exists (atomic acquire).
    PX 30000: 30-second TTL.
    my_random_value: unique per lock acquisition (random UUID). Used to verify ownership on release.
    
  Release: check + delete atomically via Lua:
    if redis.call("GET", KEYS[1]) == ARGV[1] then  -- Check: is this still our lock?
        return redis.call("DEL", KEYS[1])           -- If yes: delete.
    else
        return 0
    end
    
  Redlock (multi-node Redis):
    5 Redis instances (independent, no replication).
    Acquire: attempt to acquire lock on ALL 5 within TTL/2 time.
    Acquired if: majority (3+) ACK within time window.
    Validity time: TTL - elapsed_time - clock_drift_margin.
    Release: send DEL to all 5 (even ones that didn't ACK).
    
  CONTROVERSY (Martin Kleppmann, 2016):
    Problem 1: No fencing token. Client A acquires Redlock.
               A: GC pause for 35s. Lock expires (TTL=30s). 
               B: acquires Redlock. Both A and B in critical section.
               Redlock doesn't give a fencing token → storage can't reject A's writes.
               
    Problem 2: Clock skew. Redis node R3's clock jumps forward 10s.
               R3 expires lock 10s early. B acquires lock on R3 + 2 others (3 of 5).
               A still has lock on R1, R2. Clock-based disagreement.
               
    Antirez (Redis author) response: Redlock is designed for "efficiency" (prevent double-work),
               not "correctness" (prevent concurrent writes to storage).
               For correctness: use ZooKeeper/etcd with fencing tokens.
               
  GUIDELINE:
    Use Redlock for: "only one instance does expensive operation" where occasional duplication
                     is acceptable (idempotent operations).
    Use ZooKeeper/etcd with fencing: for "correctness" (mutual exclusion with storage-level safety).

DATABASE-LEVEL DISTRIBUTED LOCKS:

  PostgreSQL advisory locks:
    pg_try_advisory_lock(lockid): try to acquire. Returns true/false. Non-blocking.
    pg_advisory_lock(lockid): acquire. Blocks until available.
    pg_advisory_unlock(lockid): release.
    
    Session-level: released on connection close (crash-safe).
    Transaction-level: released on COMMIT/ROLLBACK.
    
    SELECT pg_try_advisory_lock(hashtext('billing-job-lock'));
    -- Returns: t (acquired) or f (already held by another session).
    -- If t: proceed with billing. If f: skip (another instance is running).
    
    Advantage: same ACID transaction that uses the lock → no external lock service needed.
    Limitation: only for operations within PostgreSQL. Not cross-service.
    
  MySQL GET_LOCK():
    SELECT GET_LOCK('billing-job-lock', 10);  -- Wait up to 10s for lock. 1=acquired, 0=timeout.
    SELECT RELEASE_LOCK('billing-job-lock'); -- Release.
    -- Connection-scoped: released on connection close. Crash-safe.
    
  Database row-level SELECT FOR UPDATE:
    BEGIN;
    SELECT * FROM jobs WHERE name='billing' FOR UPDATE;
    -- If another session has this row locked: BLOCKS until they release.
    UPDATE jobs SET status='running', started_at=NOW() WHERE name='billing';
    COMMIT;
    -- Lock released on COMMIT. Transactional. Deadlock detection built-in.
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT distributed locking:
- Multiple instances execute critical sections simultaneously: double-billing, duplicate emails, inventory miscounts
- No coordination: any instance can start the "exclusive" operation without checking
- Data corruption: concurrent writes to the same record from multiple nodes

WITH distributed locking:
→ Mutual exclusion: guaranteed single executor of critical section
→ Automatic release: TTL prevents indefinite blocking on crash
→ Storage-level safety: fencing tokens prevent zombie lock holders from corrupting data

---

### 🧠 Mental Model / Analogy

> A single key for a single bathroom. You take the key, use the bathroom, return the key. Others wait for the key. If you have a seizure inside (crash): the bathroom manager has a passkey (TTL expiry) — they enter after a timeout, reset the bathroom, re-hang the key. If you had a brief blackout (GC pause), wake up thinking you still have the key — but the manager already gave the key to someone else with a new "lock ID" (fencing token). Your old key no longer opens the door. You are safely locked out.

"Taking the key" = acquiring the distributed lock (with fencing token)
"Bathroom manager passkey" = TTL-based automatic expiry
"New key with different ID" = fencing token (storage rejects old key holder's writes)
"Your old key no longer opens the door" = storage-level fencing enforcement

---

### ⚙️ How It Works (Mechanism)

**etcd-based distributed lock with fencing:**

```go
package main

import (
    "context"
    "fmt"
    clientv3 "go.etcd.io/etcd/client/v3"
    "go.etcd.io/etcd/client/v3/concurrency"
)

func main() {
    cli, _ := clientv3.New(clientv3.Config{
        Endpoints: []string{"etcd1:2379", "etcd2:2379", "etcd3:2379"},
    })
    defer cli.Close()
    
    // Session: lease with TTL=15s (auto-renewed while session is active).
    // If this process crashes: lease expires in 15s → lock auto-released.
    session, _ := concurrency.NewSession(cli, concurrency.WithTTL(15))
    defer session.Close()
    
    mutex := concurrency.NewMutex(session, "/locks/billing-job")
    
    ctx := context.Background()
    
    // Acquire lock (blocks until acquired):
    if err := mutex.Lock(ctx); err != nil {
        panic(err)
    }
    
    // Fencing token = etcd revision when lock was acquired.
    // This revision is globally monotonic — every new lock holder gets higher revision.
    fencingToken := mutex.Header().Revision
    fmt.Printf("Lock acquired. Fencing token: %d\n", fencingToken)
    
    // Critical section: use fencing token in all storage operations.
    // Storage must check: "is this token > last_seen_token?"
    processMonthlyBilling(cli, fencingToken)
    
    // Release lock:
    if err := mutex.Unlock(ctx); err != nil {
        panic(err)
    }
}

func processMonthlyBilling(cli *clientv3.Client, fencingToken int64) {
    // Example: mark billing job as running with fencing token.
    // Only succeeds if no one with a newer token has written to this key.
    ctx := context.Background()
    txn := cli.Txn(ctx)
    
    resp, err := txn.
        // Fencing: only proceed if nobody has written to this key with a newer token.
        If(clientv3.Compare(clientv3.ModRevision("/billing/status"), "<", fencingToken+1)).
        Then(clientv3.OpPut("/billing/status", fmt.Sprintf("running:%d", fencingToken))).
        Commit()
    
    if err != nil || !resp.Succeeded {
        fmt.Println("Fencing: another lock holder has taken over. Stopping.")
        return
    }
    
    fmt.Println("Billing processing started...")
    // ... billing work ...
}
```

---

### 🔄 How It Connects (Mini-Map)

```
Leader Election (elect one leader — similar to acquiring lock for leadership role)
        │
        ▼
Distributed Locking ◄──── (you are here)
(mutual exclusion across distributed processes; TTL + fencing tokens)
        │
        ├── Fencing and Epoch (fencing tokens: storage rejects expired lock holders)
        ├── ZooKeeper (provides lock primitives via ephemeral sequential znodes)
        └── Two-Phase Commit (2PC uses distributed locks during Phase 1)
```

---

### 💻 Code Example

**Spring Boot + ShedLock for distributed scheduled tasks:**

```java
// ShedLock: distributed lock for Spring @Scheduled tasks.
// Prevents multiple instances running the same scheduled job simultaneously.
// Uses DB table or ZooKeeper/etcd for lock storage.

@SpringBootApplication
@EnableSchedulerLock(defaultLockAtMostFor = "PT30M") // Max lock duration: 30 minutes
public class BillingApplication { ... }

@Component
public class MonthlyBillingJob {
    
    @Scheduled(cron = "0 0 1 1 * *") // 1st of every month at 1 AM
    @SchedulerLock(
        name = "monthly-billing",
        lockAtLeastFor = "PT5M",   // Hold lock minimum 5 minutes (prevent spurious re-runs)
        lockAtMostFor = "PT25M"    // Release lock after 25 minutes (crash safety TTL)
    )
    public void runMonthlyBilling() {
        // ShedLock ensures: only ONE instance of this method runs at any time.
        // If instance A crashes mid-billing: lock expires in 25 minutes → B can proceed.
        // If A finishes in 5 minutes: lock held minimum 5 minutes (prevents duplicate runs
        //   if multiple scheduler instances fire simultaneously at 1:00:00 AM).
        
        log.info("Starting monthly billing on instance: {}", instanceId);
        billingService.processAll(); // Idempotent: safe to retry after failure.
        log.info("Monthly billing complete.");
    }
}

// ShedLock table (PostgreSQL):
// CREATE TABLE shedlock (
//     name VARCHAR(64),
//     lock_until TIMESTAMP(3),      -- Lock expires at this time (fencing TTL).
//     locked_at TIMESTAMP(3),
//     locked_by VARCHAR(255),       -- Which instance holds the lock.
//     PRIMARY KEY (name)
// );
// INSERT or UPDATE with lock_until in the future = acquire.
// SELECT ... FOR UPDATE: prevents concurrent acquisition (database-level mutual exclusion).
// On expiry (lock_until < NOW()): any instance can acquire (replace the row).
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Redlock is safe for all distributed locking use cases | Redlock provides "efficiency locks" (avoiding expensive duplicate work) but NOT "correctness locks" (guaranteeing no two processes write to storage simultaneously). Without fencing tokens, a GC-paused process can resume after its Redlock expires and write to storage concurrently with the new lock holder. For correctness: use ZooKeeper or etcd with fencing tokens, where the storage system validates the token |
| TTL-based expiry is sufficient for lock safety | TTL prevents indefinite blocking but doesn't prevent concurrent access. If TTL = 30s and GC pause = 35s: lock expired, new holder acquired, original holder resumed = 5 seconds of concurrent access. TTL only prevents DEADLOCKS; fencing tokens prevent RACE CONDITIONS. Both are needed for a fully safe distributed lock |
| Distributed locks are equivalent to in-process locks | In-process locks (synchronized, mutex) are instantaneous — the JVM guarantees atomicity of lock acquire and release. Distributed locks involve network round trips (10-100ms), TTL clocks, and failure modes unknown to in-process locks. A distributed lock's "hold" can be violated by GC pauses, network partitions, and clock skew — none of which affect in-process locks. The semantics are fundamentally different |
| ZooKeeper locks are faster than etcd locks | ZooKeeper has watch-based notifications (ephemeral znode deletion triggers immediate watch event → lock handoff). etcd has similar watch semantics. Performance is similar for locks. The real difference is operational: ZooKeeper has a Java-based server with JVM GC issues; etcd is written in Go (fewer GC pauses). For high-throughput locking: etcd is generally preferred in modern architectures |

---

### 🔥 Pitfalls in Production

**Redis lock without fencing token causes double execution:**

```
REAL INCIDENT: E-commerce flash sale.
  "Send congratulations email to first 100 purchasers" job.
  Each email server acquires Redis lock before sending batch.
  Lock TTL: 30 seconds.
  Job time: ~45 seconds (under normal load).
  
  Flash sale: email server overloaded. Job took 60 seconds.
  At T=30s: Redis lock expired. Server B acquired lock. Started sending emails.
  Server A: still running at T=30-60s. Both A and B sending simultaneously.
  Result: ~50% of first-100 customers received duplicate congratulations emails.
  Customer support overwhelmed. Reputation damage.

BAD: Redis lock without fencing token and without idempotency:
  String lockToken = UUID.randomUUID().toString();
  Boolean acquired = redis.set("flash-sale-email-lock", lockToken, "NX", "PX", 30000);
  
  if (Boolean.TRUE.equals(acquired)) {
      // No fencing check during the 60-second operation:
      for (Customer customer : first100Customers) {
          emailService.send(customer, "Congratulations!"); // No idempotency check.
          // If lock expires mid-loop: another server also runs this loop.
      }
      redis.eval(RELEASE_LOCK_SCRIPT, lockToken);
  }

FIX 1: Idempotency at the resource level:
  // Track which customers received which email (in DB):
  for (Customer customer : first100Customers) {
      // Atomic: only send if not already sent.
      int updated = db.update(
          "INSERT INTO email_sent (customer_id, email_type, lock_generation) " +
          "VALUES (?, 'flash-sale-congrats', ?) " +
          "ON CONFLICT (customer_id, email_type) DO NOTHING",
          customer.getId(), lockToken  // lockToken as idempotency key
      );
      if (updated > 0) { // Only send if we successfully inserted (not duplicate).
          emailService.send(customer, "Congratulations!");
      }
  }

FIX 2: Lock TTL > max job duration + buffer:
  // If job takes up to 60s: set TTL = 120s (2× safety margin).
  // Renew lock during long jobs (keep-alive):
  Boolean acquired = redis.set("flash-sale-email-lock", lockToken, "NX", "PX", 120000);
  // Background thread: renew TTL every 30s while job is running.
  ScheduledFuture<?> renewal = scheduler.scheduleAtFixedRate(() -> {
      if (redis.get("flash-sale-email-lock").equals(lockToken)) {
          redis.pexpire("flash-sale-email-lock", 120000);
      }
  }, 30, 30, TimeUnit.SECONDS);

FIX 3 (correct): Use etcd/ZooKeeper with fencing tokens for correct mutual exclusion.
```

---

### 🔗 Related Keywords

- `Fencing and Epoch` — the fencing token mechanism that makes distributed locks correct (not just fast)
- `Leader Election` — a special case of distributed locking: acquire "leader" lock for indefinite period
- `ZooKeeper` — provides correct distributed locking via ephemeral sequential znodes + zxid fencing
- `Idempotency` — makes lock-free operations safe when locks aren't perfect (retry without duplication)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ TTL: deadlock prevention. Fencing token: │
│              │ zombie holder prevention. Both required  │
│              │ for correct distributed mutual exclusion.│
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Single-instance scheduled jobs; resource │
│              │ coordination; preventing duplicate work  │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ High-throughput critical paths (lock is  │
│              │ a bottleneck); use optimistic locking or │
│              │ CRDT-based coordination instead         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "TTL is the bathroom key's timeout;      │
│              │  fencing token is the new lock ID."      │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Fencing and Epoch → ZooKeeper → etcd →  │
│              │ Leader Election → Idempotency            │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You need a distributed lock for a cron job that processes a large batch (potentially 10 minutes long). You use Redis with TTL=15 minutes. During a deployment, the old instance is slow to stop and runs for 12 minutes after the new instance also starts. The new instance acquires the Redis lock. What happens? Does Redis Redlock help here? What is the correct solution that prevents both duplicate execution AND ensures progress if the original instance crashes?

**Q2.** ZooKeeper's distributed lock uses ephemeral sequential znodes. The "lock" is held as long as the ZooKeeper session is active (heartbeat maintained). Compare ZooKeeper's session-based lock with etcd's lease-based lock: what happens if the network between the lock holder and ZooKeeper is partitioned (but the lock holder is still alive)? After what point does the lock expire? How is this different from etcd's lease behavior?
