---
layout: default
title: "Distributed Locking"
parent: "Distributed Systems"
nav_order: 597
permalink: /distributed-systems/distributed-locking/
number: "0597"
category: Distributed Systems
difficulty: ★★★
depends_on: Split Brain, Fencing, Leader Election, Quorum
used_by: Job Schedulers, Resource Coordination, Distributed Caches
related: Fencing, Split Brain, Leader Election, Redlock
tags:
  - distributed-locking
  - mutex
  - distributed-systems
  - advanced
---

# 597 — Distributed Locking

⚡ TL;DR — A distributed lock ensures mutual exclusion across multiple processes on different machines — at most one lock holder at any time. Unlike OS mutexes, distributed locks must handle: network partitions, process crashes, GC pauses, and clock skew. The key components: (1) a lease/TTL to handle dead lock-holders, (2) a fencing token to handle zombie processes that outlive their lease, (3) a linearizable store (etcd, ZooKeeper) for safe CAS-based acquisition. Redis-based locks (Redlock) are controversial — they lack fencing tokens and can fail under clock skew.

┌──────────────────────────────────────────────────────────────────────────┐
│ #597         │ Category: Distributed Systems      │ Difficulty: ★★★      │
├──────────────┼────────────────────────────────────┼──────────────────────┤
│ Depends on:  │ Split Brain, Fencing, Leader        │                      │
│ Used by:     │ Job Schedulers, Resource Coord.     │                      │
│ Related:     │ Fencing, Split Brain, Leader Elect. │                      │
└──────────────────────────────────────────────────────────────────────────┘

### 🔥 The Problem This Solves

Distributed cron job: 10 application instances, each tries to send daily report emails. Without distributed locking: all 10 instances send 10 copies of the daily email. With distributed locking: only the instance that holds the lock sends the email; others skip. Same pattern for: database migrations, cache warmup, payment processing exactly-once, inventory reservation.

---

### 📘 Textbook Definition

**Distributed lock** (also: distributed mutex) is a shared, cluster-wide mutual exclusion mechanism. Requirements:
1. **Safety (Mutual Exclusion):** Only one process holds the lock at any time
2. **Liveness (No Deadlock):** If the lock holder dies, the lock is eventually released
3. **Fault-tolerance:** Lock service itself must be replicated (not a single point of failure)

**Lease-based implementation:** Lock has a TTL. If holder dies/disconnects before releasing, lock expires after TTL → another holder can acquire. Risk: if holder is slow (GC pause) and TTL expires, another holder acquires — violating mutual exclusion. Solution: fencing token (holder must prove token validity to resource, resource rejects stale tokens).

**Safe implementations:**
- **etcd:** PUT with lease + compare-and-swap; linearizable (Raft-backed)
- **ZooKeeper:** ephemeral sequential znode; lowest zxid = lock holder

**Unsafe implementations (for critical resources):**
- **Redis SETNX + EXPIRE:** single node = single point of failure; no fencing tokens
- **Redlock (multi-Redis):** requires synchronized clocks; violates safety under clock skew or process pauses per Martin Kleppmann

---

### ⏱️ Understand It in 30 Seconds

**One line:** Distributed mutex with TTL to handle crashes + fencing token to handle slow/zombie holders.

**Analogy:** A valet parking token. The valet gives you token #42 for your car. Only token #42 can retrieve that car. The token expires in 2 hours (TTL). If you lose the token, the valet office can re-issue it to parking services after expiry. If someone claims to have the car but presents token #40 (older generation), the valet refuses — a newer token (#42) was issued, old tokens are void.

---

### 🔩 First Principles Explanation

```
CORRECT DISTRIBUTED LOCK DESIGN:

  ACQUISITION (etcd CAS):
  PUT /locks/job-sender = "node-A:token-42" IF key does not exist
  Attach lease (TTL=10s) to the PUT = auto-expires if node-A dies
  etcd's Raft consensus ensures: only ONE Put wins the "key doesn't exist" check
  
  TOKEN = lease ID (monotonically increasing) = fencing token
  
  USAGE:
  Node A writes to shared resource: includes fencing_token=42
  Resource checks: token=42 > max_seen_token=41 → accepted ✓
  
  CRASH SCENARIO:
  Node A acquires lock (token=42, TTL=10s)
  Node A crashes at T=5s
  At T=10s: etcd TTL expires → /locks/job-sender key deleted
  Node B acquires lock (token=43, TTL=10s)
  
  Node A restarts at T=12s, tries to write to shared resource with token=42:
  Resource: token=42 < max_seen_token=43 → REJECTED ✓
  
  GC PAUSE SCENARIO (classic distributed lock bug):
  T=0: Node A acquires lock (token=42, TTL=10s)
  T=8s: Node A starts GC → STW pause begins
  T=10s: Lock TTL expires
  T=10.1s: Node B acquires lock (token=43)
  T=13s: Node A GC finishes → node A thinks it still holds lock!
  
  WITHOUT FENCING: Node A and B both write → CORRUPTION
  WITH FENCING:    Node A writes token=42, resource rejects (max_seen=43) ✓
  
  ∴ Fencing tokens are REQUIRED for safe distributed locking.
```

---

### 🧠 Mental Model / Analogy

> Distributed lock = numbered safe deposit box key at a bank. The bank vault (shared resource) tracks the highest key generation it has accepted. When you approach with key generation 7: "current highest is 8 — your key is expired." The vault records are kept in a fault-tolerant ledger (etcd/ZooKeeper, backed by consensus). The bank doesn't accept Xeroxed copies of keys or keys from different (non-consensus) locksmith shops.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Distributed lock = TTL + CAS acquisition on a consensus store (etcd/ZooKeeper). Release: delete the key. Crash recovery: TTL expiry auto-releases. Fencing token: lease ID as monotonic counter.

**Level 2:** Redlock controversy: Antirez proposed 5 Redis nodes, write to majority (3/5), validity = min_TTL - elapsed - clock_drift. Kleppmann's critique: (a) if any Redis node crashes and restarts (persisting state), it may lose the SET → two clients think they hold the lock; (b) GC pause between SET and actual work → TTL may have expired → another client holds lock; (c) no fencing tokens → storage cannot reject zombie writes. Antirez's counter: these are edge cases, Redlock is sufficient for "efficiency" locks (not "correctness" locks). Practical guidance: use etcd/ZooKeeper for correctness-critical locks; Redlock acceptable for "at most once per 5 minutes run a job" use cases.

**Level 3:** Lock-ordering for deadlock prevention: if your job requires two distributed locks (lock A and lock B), always acquire them in the same global order (alphabetical by name, for example). Without global order: node 1 holds lock-A, tries for lock-B; node 2 holds lock-B, tries for lock-A → distributed deadlock. Timeout-based deadlock detection: all lock acquisitions have context TTL; if not acquired within TTL, abort and retry after random backoff.

**Level 4:** Database advisory locks as an alternative: PostgreSQL `pg_advisory_lock(key)` / `pg_try_advisory_lock(key)` — session-scoped advisory locks via the database. No TTL (session is the lease: disconnection = release). Safe for single-region, single-database deployments. Advantage: no separate lock service; disadvantage: locks tied to database availability, cross-region not possible, no fencing tokens for external resources.

---

### ⚙️ How It Works (Mechanism)

```
ETCD DISTRIBUTED LOCK — STEP BY STEP:

  1. Create lease: etcd.lease.grant(TTL=10s) → leaseId=0xABCDEF (fencing token!)
  
  2. CAS put: TXNIF (key "/lock/myjob" doesn't exist)
              THEN put "/lock/myjob" = "node-1", attach leaseId
              ELSE return error
     → Raft consensus: only ONE node's TXNIF succeeds across the cluster
  
  3. Heartbeat: keepAlive(leaseId) every 5s (< TTL) → renews lease; node alive
  
  4. Critical section: execute job, pass leaseId as fencing token to any resource writes
  
  5. Release: delete "/lock/myjob" OR just stop keepAlive (let TTL expire)
  
  CONTENDED LOCK (Waiters):
  a. Watch "/lock/myjob" for DELETE events
  b. When DELETE event fires: attempt CAS again
  c. Thundering herd problem: all waiters retry simultaneously
     Solution: ZooKeeper uses sequential ephemeral znodes; only the next node (min seq) is notified
     etcd solution: use lease-based election library (jetcd Election API)
```

---

### 💻 Code Example

```java
// Spring Boot + Jedis Redis distributed lock with fencing token simulation
// For production: use Redisson or switch to etcd-based lock (jetcd)

@Component
public class DistributedLock {

    private final RedisTemplate<String, String> redis;
    
    public DistributedLock(RedisTemplate<String, String> redis) {
        this.redis = redis;
    }

    // Acquire lock with fencing token returned on success
    // Returns empty if lock not acquired; caller should retry or skip
    public Optional<LockToken> tryAcquire(String lockName, Duration ttl) {
        String tokenValue = UUID.randomUUID().toString(); // Use monotonic counter in production
        
        // SET lockName tokenValue NX PX ttlMs — atomic acquisition
        Boolean success = redis.opsForValue()
            .setIfAbsent(lockName, tokenValue, ttl);
        
        if (Boolean.TRUE.equals(success)) {
            return Optional.of(new LockToken(lockName, tokenValue, 
                System.currentTimeMillis() + ttl.toMillis()));
        }
        return Optional.empty();
    }

    // Release lock only if we own it (fencing: don't release someone else's lock!)
    public void release(LockToken token) {
        // Lua script: atomic check + delete (prevents releasing wrong owner's lock)
        String script = "if redis.call('get', KEYS[1]) == ARGV[1] then " +
                        "  return redis.call('del', KEYS[1]) " +
                        "else return 0 end";
        redis.execute((RedisCallback<Long>) connection -> 
            connection.eval(script.getBytes(), ReturnType.INTEGER, 1,
                token.lockName().getBytes(), token.value().getBytes()));
    }
}

// Usage: daily report sender (efficiency lock — not safety-critical)
@Scheduled(cron = "0 0 9 * * ?")
public void sendDailyReport() {
    Optional<LockToken> lock = distributedLock.tryAcquire("daily-report-lock", Duration.ofMinutes(5));
    if (lock.isEmpty()) {
        log.info("Another instance is sending the report — skipping");
        return;
    }
    try {
        reportService.send();
    } finally {
        lock.ifPresent(distributedLock::release);
    }
}
```

---

### ⚖️ Comparison Table

| Implementation | Safety | Fencing | Fault Tolerant | Complexity |
|---|---|---|---|---|
| **etcd lease + CAS** | Strong (Raft) | Yes (leaseId) | Yes | Medium |
| **ZooKeeper ephemeral** | Strong (Zab) | Yes (zxid) | Yes | Medium |
| **Redis SETNX** | Weak (single node) | No | No | Low |
| **Redlock (5 Redis)** | Weak (clock-dependent) | No | Partial | Medium |
| **PostgreSQL advisory** | Strong (DB session) | N/A | DB-dependent | Low |

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────────┐
│ MUST HAVE     │ TTL/Lease (crash recovery)                  │
│               │ Fencing token (GC pause / zombie safety)    │
│               │ Linearizable store (etcd, ZooKeeper)        │
│ RELEASE       │ Only release YOUR token (check before del)  │
│ AVOID         │ Redis SETNX for correctness-critical locks  │
│ DEADLOCK      │ Always acquire multiple locks in same order │
└──────────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** A payment service uses a distributed lock (etcd-based, lease TTL=10s) to ensure at-most-once payment processing. A critical section processes a payment and writes to a Postgres database. (1) If the process GC-pauses for 15s (> TTL), another instance acquires the lock and also processes the payment. With fencing tokens from etcd, how would you prevent double payment — given that Postgres doesn't natively know about etcd fencing tokens? (2) Design a database-level mechanism that achieves the same effect as fencing tokens using only Postgres features. (3) Is a distributed lock even the right tool for at-most-once payment processing, or is idempotency the better solution?
