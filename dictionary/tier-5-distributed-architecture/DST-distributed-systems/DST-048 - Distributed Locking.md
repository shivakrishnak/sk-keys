---
id: DST-019
title: "Distributed Locking"
category: Distributed Systems
tier: tier-5-distributed-architecture
folder: DST-distributed-systems
difficulty: ★★★
depends_on: DST-012, DST-013, DST-046
used_by:
related: DST-013, DST-012, DST-046, DST-044
tags:
  - distributed
  - reliability
  - pattern
  - advanced
  - deep-dive
status: complete
version: 2
layout: default
parent: "Distributed Systems"
grand_parent: "Technical Dictionary"
nav_order: 48
permalink: /distributed-systems/distributed-locking/
---

# DST-052 - Distributed Locking

⚡ TL;DR - A distributed lock coordinates exclusive access to a shared resource across multiple processes or machines, but unlike local mutexes it can silently fail — the lock holder can be presumed dead while still running, causing two processes to believe they hold the lock simultaneously; fencing tokens are the only correct mitigation.

| Metadata        |                                    |     |
| :-------------- | :--------------------------------- | :-- |
| **Depends on:** | DST-012, DST-013, DST-046          |     |
| **Used by:**    |                                    |     |
| **Related:**    | DST-013, DST-012, DST-046, DST-044 |     |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A distributed job scheduler runs multiple worker instances for availability. A cron job "send daily report" should run exactly once. Without coordination: all three workers start the job simultaneously, sending three identical emails. A file processing pipeline must process each file exactly once — without locking: multiple workers process the same file in parallel, corrupting the output.

**THE BREAKING POINT:**
Local mutex locks (synchronized, ReentrantLock) only work within a single process. Across multiple JVMs or microservice instances: there is no shared memory, no OS-level synchronization primitive. Distributed systems need a coordination mechanism that spans machine boundaries.

**THE INVENTION MOMENT:**
Early distributed systems used database rows as locks (SELECT FOR UPDATE). As systems scaled beyond single databases: external lock services emerged. Chubby (Google, 2006) — a distributed lock service backed by Paxos — became the reference implementation. ZooKeeper (Apache, 2008) open-sourced a similar model. Redis became popular for simpler (and less correct) lock implementations. The lesson Chubby and ZooKeeper taught: distributed locks are fundamentally hard because of the FAILURE MODES that local locks don't have.

**EVOLUTION:**
1960s: Peterson's algorithm (shared memory mutex). 1990s: database-based distributed locks. 2006: Chubby (Paxos-backed). 2008: ZooKeeper. 2012: Redis SETNX-based locking. 2016: Antirez proposes Redlock (multi-node Redis). Martin Kleppmann critiques Redlock (timing assumptions). 2018: Kleppmann/Antirez debate highlights that only fencing tokens make distributed locks safe. Today: etcd-based locks (Kubernetes), ZooKeeper (Kafka), Redis (caching-tier locks with fencing).

---

### 📘 Textbook Definition

**Distributed locking** is a coordination mechanism that ensures at most one process (or thread) in a distributed system can hold exclusive access to a shared resource at any given time. A distributed lock has: (1) **Lock acquisition:** a process writes a unique lock token to a shared lock store (database, ZooKeeper node, Redis key). (2) **Lock lease/TTL:** the lock expires after a TTL to prevent indefinite holding if the owner crashes. (3) **Lock release:** the owner deletes the lock token on completion. **The fundamental challenge:** a process holding a lock can be declared dead (TTL expiry) while it is still alive (GC pause, network partition). After TTL expiry: another process acquires the lock. Now TWO processes believe they hold the lock simultaneously. This is **split-brain locking** — and it breaks the mutual exclusion guarantee. **Fencing tokens** (DST-013) are the correct mitigation: each lock acquisition gets a monotonically increasing token; the protected resource rejects any write from a token older than the last seen token.

---

### ⏱️ Understand It in 30 Seconds

**One line:** Distributed locks provide mutual exclusion across machines, but TTL-based expiry means two processes can hold the lock simultaneously — fencing tokens are required to make writes to the protected resource safe.

> A distributed lock is like renting a locker at a gym — you get the key for 1 hour (TTL). If you fall asleep in the sauna (GC pause) and someone else rents the same locker after your hour expires: both of you have keys. Fencing tokens are like writing your rental number on everything you put in the locker — the locker attendant only accepts items with the LATEST rental number. Old items are rejected, even if the old key-holder is still around.

**One insight:** A distributed lock with TTL but no fencing token is NOT correct — it merely makes lock collisions unlikely, not impossible. Correctness requires the protected resource to enforce fencing token ordering.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. **At-most-one holder:** at any logical moment, at most one process considers itself the lock holder and the protected resource accepts writes from it. This is mutual exclusion.
2. **TTL guarantees liveness:** if the lock holder crashes: the lock expires after TTL, allowing other processes to acquire it. Without TTL: a crashed lock holder blocks all others indefinitely.
3. **TTL breaks safety:** the holder is declared dead at TTL, but may still be alive (paused). Safety and liveness are in tension — TTL is the trade-off.
4. **Fencing tokens restore safety:** each lock acquisition gets an incrementing token. The resource rejects writes from expired token holders, even if they're alive and believe they hold the lock.

**DERIVED DESIGN:**
Correct distributed locking requires both: (a) a lock store with TTL (for liveness), AND (b) a fencing token protocol at the protected resource (for safety). A lock store alone (Redis, ZooKeeper) provides the token generation and TTL. Fencing enforcement must be implemented in the application layer (protected resource checks token before applying write).

**THE TRADE-OFFS:**
**Gain:** Mutual exclusion across distributed processes. Prevents duplicate work, race conditions, data corruption in shared resource access.
**Cost:** Lock acquisition latency (network round-trip to lock store). Lock store availability = system availability (SPOF unless replicated). Fencing token implementation complexity at every protected resource.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Distributed mutual exclusion requires consensus — at least one coordination round-trip. This is the minimal cost.
**Accidental:** Redlock's complexity (5-node Redis quorum, timing-based lock validity) is accidental — it tries to implement consensus-like guarantees without a consensus protocol. Using ZooKeeper or etcd (actual consensus) is simpler and more correct.

---

### 🧪 Thought Experiment

**SETUP:** Three payment processing workers (W1, W2, W3). Redis lock key: `payment:12345`. TTL: 30 seconds.

**HAPPY PATH:**

- W1: `SET payment:12345 worker1 NX PX 30000` → OK (lock acquired)
- W1 processes payment (takes 5 seconds) → commits → `DEL payment:12345`
- W2: `SET payment:12345 worker2 NX PX 30000` → OK (acquired)
- Payment processed exactly once. Correct.

**DANGEROUS PATH (GC pause causes double processing):**

- W1: `SET payment:12345 worker1 NX PX 30000` → OK (lock acquired)
- W1: starts processing payment
- W1: JVM Full GC pause starts at T=25s (pauses for 40 seconds)
- T=30s: TTL expires → `payment:12345` deleted from Redis
- W2: `SET payment:12345 worker2 NX PX 30000` → OK (acquires lock)
- W2: starts processing payment (same payment!)
- T=65s: W1 GC pause ends → W1 continues processing
- W1: commits payment (W1's lock token is `worker1`)
- W2: commits payment (W2's lock token is `worker2`)
- Result: DOUBLE CHARGE — payment processed twice

**WITH FENCING TOKEN:**

- W1: acquires lock, receives fencing token `42`
- W2: acquires lock after TTL, receives fencing token `43`
- W1 (woken from GC): sends commit with token `42`
- Database: "last seen token = 43, reject token 42"
- W1's commit: REJECTED. Double charge prevented.
- W2's commit: ACCEPTED (token 43 = current).

**THE INSIGHT:** The fencing token is enforced by the RESOURCE (database), not the lock store (Redis). Redis cannot prevent the old token holder from writing — only the database can. This is why "Redis lock = safe" is a misconception.

---

### 🧠 Mental Model / Analogy

> A distributed lock is like a museum's "one person in the restoration room" policy. The policy officer (lock store) gives each visitor a numbered badge (fencing token) when they enter. If a visitor passes out and is taken away (GC pause / crash), the museum issues a higher-numbered badge to the next visitor. If the passed-out visitor wakes up and tries to re-enter: the room itself checks their badge number — "badge 42, but current badge is 43 — you can't enter." The room (protected resource) enforces the policy, not just the officer at the door.

**Mapping:**

- **Museum door policy officer** → lock store (Redis, ZooKeeper, etcd)
- **Numbered badge** → fencing token
- **Visitor passing out** → GC pause / network isolation
- **Higher-numbered badge issued to next visitor** → new lock acquisition with incremented token
- **Room checking badge number** → protected resource validating fencing token
- **Badge 42 rejected (43 current)** → old lock holder's write rejected

Where this analogy breaks down: in a museum, you know a visitor has left when they physically exit. In distributed systems: you can never be sure a process is dead (the fundamental uncertainty). The museum's analogy assumes clear physical presence/absence — distributed systems have only timeouts and fencing to work with.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
A distributed lock says "only one worker can do this at a time." It's like a "In Use" sign on a bathroom door — but the sign disappears after 30 seconds (TTL) in case someone got stuck inside. The problem: if someone was just slow in the bathroom (not stuck), two people might enter. Fix: stamp each person's entry receipt with a number — the bathroom rejects anyone whose number is older than the last person's.

**Level 2 - How to use it (junior developer):**
Redis-based lock (Redisson): `RLock lock = redissonClient.getLock("payment:12345"); lock.lock(30, TimeUnit.SECONDS); try { processPayment(); } finally { lock.unlock(); }`. Redisson handles fencing internally for supported operations. For ZooKeeper: use Curator's InterProcessMutex. CRITICAL: implement fencing token at the protected resource for any payment, billing, or idempotency-critical operation.

**Level 3 - How it works (mid-level engineer):**
Redis `SET key value NX PX ttl`: atomically creates key ONLY IF NOT EXISTS (NX = no-overwrite), with PX millisecond expiry. Lock acquired if response is "OK". Lock value = unique owner ID (UUID). Release: Lua script `if redis.call("get", key) == owner then return redis.call("del", key) end` — atomic check-and-delete to prevent releasing another owner's lock. ZooKeeper lock: create ephemeral sequential znode `/locks/payment-0000000042`. Lowest sequence number = lock holder. On failure: ephemeral znode auto-deleted. Watcher notifies next-in-queue. ZooKeeper naturally provides incrementing sequence numbers as fencing tokens.

**Level 4 - Why it was designed this way (senior/staff):**
Chubby (Google's distributed lock service) was designed for coarse-grained locking (minutes, not milliseconds) — configuration, leader election, partition ownership. It uses Paxos internally: lock acquisition is a Paxos write. Fencing tokens are "sequencers" — a Chubby-generated monotone token that clients present to lock-protected services. The service rejects stale sequencers. This design (consensus-backed lock + sequencer-enforced resource access) is correct under all failure scenarios — but with Paxos latency (~100ms). Redis-based locks trade correctness for latency (<1ms). For non-critical mutual exclusion (caching, rate limiting): Redis trade-off is acceptable. For critical operations (billing, idempotency, partition ownership): only consensus-backed locks (ZooKeeper, etcd, Chubby) with fencing tokens are correct.

**Expert Thinking Cues:**

- "Redis Redlock is safe — uses 5 nodes" → Redlock's safety depends on timing assumptions (clocks don't drift, GC pauses < lock validity). Kleppmann showed these assumptions are violated in practice. For correctness-critical locks: use etcd or ZooKeeper (actual consensus).
- "Our distributed job scheduler uses Redis locks — is it safe?" → Safe enough for "don't run duplicate jobs" with idempotent jobs. NOT safe for "process payment exactly once" without fencing token enforcement at the payment DB.
- "ZooKeeper session expired — is our lock lost?" → Yes. ZooKeeper's ephemeral znode is deleted on session expiry. If your session expires while holding the lock: the lock is released. Rebuild the session and re-acquire. This is correct behavior — it prevents indefinite lock holding by crashed holders.
- "Our lock TTL is 60 seconds — is that long enough?" → TTL must be > worst-case lock-holder execution time + GC pause time + network delay. If any of those is unknown: TTL doesn't help (you'll always have false expiry cases). Use fencing tokens in addition to TTL.

---

### ⚙️ How It Works (Mechanism)

**Redis lock protocol:**

```
Acquire:
  SET lock_key owner_id NX PX ttl_ms
  → "OK" = acquired
  → nil  = already held

Release (MUST be atomic):
  EVAL "if redis.call('get',KEYS[1])==ARGV[1]
        then return redis.call('del',KEYS[1])
        else return 0 end"
        1 lock_key owner_id
  → 1 = released
  → 0 = not owner (lock expired and taken by another)

ZooKeeper lock protocol (with fencing tokens):
  1. Create ephemeral sequential znode:
     /locks/payment-0000000042 (sequence = fencing token)
  2. List children, find lowest sequence
  3. If mine is lowest: I hold the lock
  4. Else: watch the next-lower node for deletion
  5. On deletion notification: re-check (step 2)
  Release: delete my znode
  Fencing token: the sequence number (0000000042)
```

**Split-brain locking timeline:**

```
Time:  0s     25s    30s   65s
W1:    [acquire lock]---GC---[wakeup, writes stale data]
                    ↑TTL expires↑
W2:              [acquire lock]---[writes correct data]

With fencing tokens:
  W1 token: 42, W2 token: 43
  DB sees W2 write (token 43): accepted
  DB sees W1 write (token 42): REJECTED (42 < 43)
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW (ZooKeeper lock with fencing token):**

```
Worker  ZooKeeper  Protected DB
  │         │            │
  │─create /locks/job-0042──▶│
  │◀─seq=42──│            │
  │─getChildren─▶│         │
  │◀─[42=lowest]─│         │
  │ LOCK HELD (fencing token=42)
  │─PROCESS + UPDATE(token=42)────▶│
  │         │            │ ← YOU ARE HERE
  │         │            │ (DB validates 42 >= last_seen)
  │─delete /locks/job-0042─▶│
  │ lock released          │
```

**FAILURE PATH (GC pause / crash):**
Worker's ZooKeeper session expires (ephemeral znode auto-deleted). ZooKeeper notifies next waiter. Next worker creates new znode with seq=43. Old worker wakes up, presents token=42. Protected DB: "42 < 43, rejected." Safe.

**WHAT CHANGES AT SCALE:**
At scale: lock contention becomes the bottleneck. 1000 workers competing for the same lock → ZooKeeper "herd effect" (all 1000 watch the same znode). Solution: watch only the immediately preceding znode (each worker watches one predecessor). This reduces ZooKeeper load from O(n) to O(1) per lock release.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Distributed locks introduce lock ordering deadlock across services: Service A holds Lock X, waits for Lock Y. Service B holds Lock Y, waits for Lock X. Solution: always acquire locks in a consistent global order (lexicographic order by lock name). Alternatively: use lock timeouts + exponential backoff. Distributed deadlock detection (asking all lock holders) is expensive and rarely implemented.

---

### 💻 Code Example

**BAD - Redis lock without fencing (unsafe for critical operations):**

```java
// UNSAFE: no fencing token. GC pause → double processing.
public void processPayment(String paymentId) {
    String lockKey = "payment:" + paymentId;
    String ownerId = UUID.randomUUID().toString();
    // Try to acquire for 30 seconds
    Boolean acquired = redis.opsForValue()
        .setIfAbsent(lockKey, ownerId, 30, TimeUnit.SECONDS);
    if (Boolean.TRUE.equals(acquired)) {
        try {
            // If GC pause > 30s here: lock expires.
            // Another worker acquires, processes payment.
            // THIS worker wakes up and also processes.
            // Double charge if no fencing at DB.
            chargeCustomer(paymentId); // DANGER
        } finally {
            // ALSO UNSAFE: non-atomic check-and-delete:
            // if (redis.get(lockKey).equals(ownerId)):
            //   redis.del(lockKey)  ← race condition!
            redis.delete(lockKey);
        }
    }
}
```

**GOOD - ZooKeeper lock with fencing token:**

```java
import org.apache.curator.framework.recipes.locks
    .InterProcessMutex;

public void processPayment(String paymentId)
    throws Exception {
    // ZooKeeper ephemeral sequential znode
    // Sequence number = fencing token
    InterProcessMutex lock = new InterProcessMutex(
        zkClient,
        "/locks/payment/" + paymentId
    );

    // Curator handles: create ephemeral sequential znode,
    // watch predecessor, acquire on predecessor deletion
    if (lock.acquire(30, TimeUnit.SECONDS)) {
        try {
            // Get the fencing token (ZK sequence number):
            long fencingToken = getFencingToken(zkClient,
                "/locks/payment/" + paymentId);
            // Pass fencing token to protected resource:
            // DB validates token > last_seen_token for key
            chargeCustomerWithFencing(paymentId, fencingToken);
            // DB layer: if token < last_seen: reject write
            // This prevents stale GC-paused process writes
        } finally {
            lock.release();
            // ZK: deletes ephemeral znode
            // Next waiter is notified and acquires
        }
    } else {
        throw new LockAcquisitionException(
            "Could not acquire lock for: " + paymentId);
    }
}

// At the protected resource (DB layer):
// This check makes the lock CORRECT under GC pauses
public void chargeCustomerWithFencing(
        String paymentId, long token) {
    // Atomic compare-and-update in database:
    int updated = jdbcTemplate.update(
        "UPDATE payment_locks " +
        "SET last_token=?, status='processed' " +
        "WHERE payment_id=? AND last_token < ?",
        token, paymentId, token
    );
    if (updated == 0) {
        throw new StaleTokenException(
            "Fencing token rejected: " + token);
        // Stale token from GC-paused worker correctly rejected
    }
}
```

**How to test / verify correctness:**

```bash
# Test fencing token rejection:
# 1. Acquire lock (token=42), simulate GC pause (sleep > TTL)
# 2. Acquire lock again with different process (token=43)
# 3. Wake first process, attempt write with token=42
# 4. Verify: DB rejected token=42 write

# ZooKeeper: check for herd effect:
echo stat | nc zookeeper-host 2181 | grep "connections"
# If connections spike on lock release: herd effect
# Fix: ensure each waiter watches only predecessor znode

# Redis: check for orphaned locks:
redis-cli keys "payment:*" | wc -l
# Count should be ≤ number of active processing workers
# High count: TTL too long or locks not released on failure
```

---

### ⚖️ Comparison Table

| Lock Store             | Correctness                    | Latency  | HA model                  | Best for                             |
| :--------------------- | :----------------------------- | :------- | :------------------------ | :----------------------------------- |
| Redis SETNX            | Unsafe without fencing         | < 1ms    | Active-passive / Sentinel | Rate limiting, caching, non-critical |
| Redlock (Redis)        | Weakly safe (timing-dependent) | 1-5ms    | 5 nodes quorum            | Medium criticality (disputed)        |
| ZooKeeper              | Correct with fencing           | 5-20ms   | Paxos (ZAB)               | Critical: leader election, Kafka     |
| etcd                   | Correct with fencing           | 2-10ms   | Raft                      | Kubernetes, modern systems           |
| Postgres advisory lock | Correct (session-scoped)       | < 1ms    | None (single DB)          | Same-DB coordination                 |
| Chubby                 | Correct with sequencer         | 50-200ms | Paxos                     | Google internal systems              |

---

### ⚠️ Common Misconceptions

| Misconception                                                            | Reality                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| :----------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Redis SETNX is a safe distributed lock"                                 | Redis SETNX provides best-effort mutual exclusion. A GC pause longer than the TTL causes two processes to hold the lock simultaneously. Without fencing tokens at the protected resource: data corruption is possible. Safe only for non-critical coordination (rate limiting, caching invalidation).                                                                                                                                        |
| "Redlock solves the Redis safety problem"                                | Redlock requires timing assumptions: lock validity = TTL - drift - network delay. If clocks drift or GC pauses exceed validity: Redlock can also fail (two holders simultaneously). Martin Kleppmann demonstrated concrete failure scenarios. Redlock is better than single-node Redis but still not correct in the presence of arbitrary process pauses.                                                                                    |
| "ZooKeeper locks are safe without fencing tokens"                        | ZooKeeper ephemeral znodes + sequential IDs provide the fencing token. But the RESOURCE must check the token — ZooKeeper cannot enforce this for you. If your payment database doesn't validate the ZooKeeper sequence number: a paused process can still write stale data after its session expired and another process took the lock.                                                                                                      |
| "Distributed lock TTL should be very short to minimize collision window" | Short TTL reduces the window for two holders but increases false expiry rate (normal slow operations appear dead). The right TTL = max(expected execution time) + max(GC pause) + max(network delay). If any of these are unbounded: no TTL is correct — use fencing tokens instead of relying on TTL for safety.                                                                                                                            |
| "We can use a single database row as a distributed lock safely"          | `SELECT FOR UPDATE` or advisory locks work correctly within a single database. Problems: the database itself is a SPOF for the lock. Long lock-holding transactions block other DB operations. If the connection drops without explicit commit/rollback: connection cleanup time determines how long the lock is held after crash. Use advisory locks for same-DB coordination; use a dedicated lock service for cross-service coordination. |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: GC Pause Causes Double Processing Without Fencing**

**Symptom:** A customer received two charges for the same order. Application logs show two successful `chargeCustomer()` calls for the same `orderId`. Both calls are from different workers and 35 seconds apart — matching the Redis lock TTL.
**Root Cause:** Worker 1 acquired the Redis lock, then experienced a GC pause > TTL (35+ seconds). Lock expired. Worker 2 acquired the lock, processed the payment. Worker 1's GC pause ended — it continued processing from where it left off, unaware that its lock had expired. No fencing token at the payment service → both charges succeeded.
**Diagnostic:**

```bash
# Check GC log for pauses > lock TTL:
grep "GC pause\|Full GC" /var/log/app/gc.log | \
  awk '$NF ~ /[0-9]+ms/{gsub(/ms/,"",$NF); if ($NF > 30000) print}'
# Any GC pause > 30000ms = risk of TTL expiry during pause

# Check Redis lock activity for the orderId:
redis-cli monitor | grep "order:12345"
# Look for SET (acquire), DEL (release), EXPIRE events
# If two SET events with different owners within TTL window:
# = double processing occurred

# Check application duplicate processing:
grep "chargeCustomer.*orderId=12345" /var/log/app/app.log
# Two log lines = double processing confirmed
```

**Fix:**
BAD: Redis lock without fencing. Trusting TTL as the safety mechanism.
GOOD: Add fencing token enforcement at the payment service: `UPDATE payments SET status='charged', fencing_token=? WHERE order_id=? AND fencing_token < ?`. Old token's update is rejected. Implement payment idempotency key at the payment gateway (separate from locking).
**Prevention:** JVM: use G1GC or ZGC to minimize GC pause duration. Set lock TTL > expected worst-case GC pause. Implement fencing tokens for all correctness-critical locks, regardless of lock TTL.

**Failure Mode 2: ZooKeeper Herd Effect on Lock Release**

**Symptom:** ZooKeeper CPU spikes every time a high-contention lock is released. Application latency spikes simultaneously. ZooKeeper logs show thousands of watch notifications firing simultaneously. Lock acquisition time increases from 5ms to 500ms under load.
**Root Cause:** All lock waiters watching the SAME lock znode (the currently-held lock). On release: all waiters receive the watch notification simultaneously — "thundering herd." All N waiters rush to check if they can acquire the lock. ZooKeeper processes N simultaneous requests, causing CPU spike.
**Diagnostic:**

```bash
# ZooKeeper: check watch count on lock znode:
echo "stat /locks/mylock" | zkCli.sh 2>/dev/null
# Field: "dataWatches: 847" = 847 concurrent waiters
# All watching same znode = herd effect

# Correct implementation: each waiter watches ONLY predecessor:
# /locks/mylock-0000000042 watches /locks/mylock-0000000041
# On 41's deletion: 42 fires, checks if it's the lowest
# Only ONE watch fires per lock release
```

**Fix:**
BAD: `getChildren("/locks")` → watch the lowest → all N watch same node.
GOOD: Create sequential znode, watch ONLY the immediately preceding znode. Curator's InterProcessMutex implements this correctly.
**Prevention:** Always use Curator's InterProcessMutex for ZooKeeper locking — never implement ZooKeeper locks from scratch. Curator's implementation handles herd effect, session expiry, and re-entrance correctly.

**Failure Mode 3: Security - Lock Poisoning via Unauthorized Lock Acquisition**

**Symptom:** An attacker gains access to the Redis instance (via misconfigured firewall or network sniffing of `requirepass` credential). The attacker executes `SET payment:12345 attacker NX PX 999999999` — acquiring the payment lock with a 11-day TTL. All legitimate payment workers are locked out of processing payment 12345 for 11 days. Alternatively: attacker executes `DEL payment:*` — releasing all locks, allowing multiple workers to process simultaneously.
**Root Cause:** Redis instance accessible without authentication from attacker's network. Lock keys have predictable names (`payment:{orderId}`). An unauthorized `SET NX` creates a lock owned by the attacker; unauthorized `DEL` releases valid locks.
**Diagnostic:**

```bash
# Check Redis access control:
redis-cli -h redis-host AUTH wrong_password
# If error: "WRONGPASS" = auth enabled (good)
# If OK or no auth prompt: unprotected (bad)

# Check Redis network exposure:
nmap -p 6379 redis-host
# Should not be reachable from internet

# Monitor Redis for unexpected lock operations:
redis-cli monitor | grep "SET\|DEL" | \
  grep -v "<expected-service-IPs>"
# Any SET/DEL from unexpected IPs = unauthorized access
```

**Fix:**
BAD: Redis exposed without authentication on shared network.
GOOD: (1) `requirepass` in Redis config with strong password. (2) Redis ACL: `ACL SETUSER service on >password ~payment:* +SET +DEL +GET` — restrict to only the commands and key patterns needed. (3) Network segmentation: Redis accessible ONLY from application servers (firewall). (4) TLS for Redis connections (`--tls-port`, `--tls-cert-file`).
**Prevention:** Redis containing distributed locks is as sensitive as a database. Apply the same network isolation, authentication, and access control as your primary database.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- DST-012 - Split Brain (distributed locking is fundamentally a split-brain prevention mechanism)
- DST-013 - Fencing Token (fencing tokens are the correct mitigation for distributed lock safety failures)
- DST-046 - Leader Election (leader election is implemented using distributed locks)

**Builds On This (learn these next):**

- Nothing directly in DST category

**Alternatives / Comparisons:**

- DST-013 - Fencing Token (the safety mechanism that makes distributed locks correct)
- DST-012 - Split Brain (the failure mode distributed locking tries to prevent)
- DST-044 - Quorum (ZooKeeper/etcd locks use quorum internally for consistency)

---

### 📌 Quick Reference Card

```
+------------------+--------------------------------+
| WHAT IT IS       | Mutual exclusion across        |
|                  | distributed processes via      |
|                  | shared lock store + TTL        |
+------------------+--------------------------------+
| PROBLEM SOLVED   | Coordinating exclusive access  |
|                  | to shared resource across      |
|                  | multiple service instances     |
+------------------+--------------------------------+
| KEY INSIGHT      | TTL expiry can cause two       |
|                  | processes to hold the lock;    |
|                  | fencing tokens are required    |
+------------------+--------------------------------+
| USE WHEN         | Job deduplication, leader      |
|                  | election, partition ownership  |
+------------------+--------------------------------+
| AVOID WHEN       | High-frequency locking         |
|                  | (use partitioning instead)     |
+------------------+--------------------------------+
| TRADE-OFF        | Safety (fencing) vs.           |
|                  | implementation simplicity      |
+------------------+--------------------------------+
| ONE-LINER        | Distributed lock = TTL +       |
|                  | fencing token at the resource  |
+------------------+--------------------------------+
| NEXT EXPLORE     | DST-013 Fencing Token,         |
|                  | DST-012 Split Brain            |
+------------------+--------------------------------+
```

**If you remember only 3 things:**

1. Distributed locks with TTL but NO fencing tokens are NOT correct for critical operations. Two processes can hold the lock simultaneously after GC pause.
2. Fencing tokens are enforced at the PROTECTED RESOURCE (database), not at the lock store (Redis). The resource rejects writes from stale token holders.
3. For correctness-critical locks: use ZooKeeper (Curator) or etcd — not Redis. For non-critical coordination (rate limiting, caching): Redis is acceptable.

**Interview one-liner:**
"A distributed lock provides mutual exclusion across processes using a shared lock store (Redis, ZooKeeper, etcd) with a TTL. The critical failure mode: if the lock holder pauses (GC, network) longer than the TTL, another process acquires the lock. Now both processes believe they hold the lock. Fix: fencing tokens — each lock acquisition gets an incrementing token, and the protected resource rejects writes from any token less than the last seen. The resource (database), not the lock store, enforces fencing. For correctness-critical locks, use ZooKeeper or etcd (consensus-backed); Redis lacks the timing guarantees required for correctness."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Time-bounded guarantees (TTLs) provide liveness but not safety. Any system where "timeout = failure assumption" can produce false positives: the timed-out entity may still be alive and active. Safety requires the RESOURCE to check a monotone token (version, sequence number, fencing token) that proves authority at the time of write — not just at the time of lock acquisition. This pattern ("epoch/version at write time, not just at acquire time") appears in optimistic locking, MVCC, CAS operations, and distributed lock fencing. The lesson: never trust TTL alone for safety; always enforce authority at the moment of resource access.

**Where else this pattern appears:**

- **Kubernetes leader election (controller manager):** Kubernetes controllers (deployment, replication set) use a distributed lease (stored in etcd) for leader election. The elected leader holds the lease; on TTL expiry: another candidate acquires it. The lease's resource version (Kubernetes etcd version) serves as the fencing token. Controllers include the resource version in all API write calls; the API server rejects writes from stale resource versions. Same pattern: TTL for liveness + resource version for safety.
- **Database optimistic locking (row versioning):** `UPDATE table SET ... WHERE id=? AND version=?`. The version is a fencing token: if another process updated (and incremented version), the current process's update is rejected (0 rows updated). This is distributed locking without an external lock store — the database row itself is the lock, and the version column is the fencing token. Same pattern: TTL → "lock" via SELECT FOR UPDATE → UPDATE WHERE version matches.
- **S3 conditional writes (ETags):** AWS S3 supports `If-Match` header in PUT requests: `PUT /bucket/file If-Match: "etag-of-last-read"`. If another process has written the file since your read (changing the ETag): your PUT is rejected (412 Precondition Failed). The ETag is the fencing token. S3 is the protected resource enforcing fencing. Same pattern: ETags as monotone tokens, resource enforces ordering.

---

### 💡 The Surprising Truth

Martin Kleppmann's 2016 critique of Redlock ("How to do distributed locking") sparked a public debate with Redis creator Salvatore Sanfilippo (antirez) that became one of the most important public distributed systems discussions of the decade. Kleppmann showed that Redlock's safety depends on an assumption that Redis's authors acknowledged: "all Redis nodes, upon receiving time from the OS, must not show delays in handling requests." Kleppmann demonstrated that a simple `kill -STOP` process pause (or GC pause, or OS scheduling delay) violates this assumption and causes Redlock to fail. Antirez responded that Redlock is designed for "non-critical systems where correctness matters more than performance." The surprising truth: the debate revealed that MOST Redis lock users were using Redlock or simple SETNX for CRITICAL operations (job scheduling, payment processing) while believing they had strong correctness guarantees. The debate moved the industry to understand that distributed lock correctness requires fencing tokens — a concept that Chubby had implemented since 2006 but that had not been widely understood in the Redis community until Kleppmann's post. A technical blog post changed how an entire generation of engineers thought about distributed locks.

---

### 🧠 Think About This Before We Continue

**Q1 (D - Root Cause):** Your microservice uses a Redis lock with 30-second TTL to prevent duplicate Stripe payment processing. Production incident: a customer was charged twice. Your GC logs show no pause > 30 seconds. Your Redis monitoring shows no lock expiry anomalies. The two charges are 8 seconds apart. What are the possible explanations? What would you check first to determine the root cause?
_Hint:_ Two charges 8 seconds apart with no GC pause suggests: (1) The lock was released before payment confirmation (bug in try/finally — unlock before payment confirmed). (2) Two requests for the same paymentId with different request IDs (client retried with a new request — not a lock collision but a duplicate request). (3) Redis single-node failover: if Redis sentinel promoted a new primary, in-flight SET NX calls might replay. (4) Lock key collision: `payment:` + orderId maps to same key for two different orders (hash collision? bug in key construction?). Check: Stripe idempotency key (separate from application-level lock), application lock release sequence, Redis sentinel failover events, lock key generation logic.

**Q2 (C - Design Trade-off):** A distributed scheduler must run 10,000 unique jobs per hour, each job locking a unique resource for processing (no contention between different jobs). Option A: Redis SETNX with 60s TTL, no fencing. Option B: ZooKeeper sequential znodes with fencing tokens. Option C: PostgreSQL advisory locks (single DB). Compare the three options for this specific use case (high volume, unique resources, no contention). Does fencing matter here if jobs are truly unique (no two jobs lock the same resource)?
_Hint:_ No contention between different jobs: fencing token between jobs is irrelevant (different resources = no conflict). Fencing matters for the SAME job running twice. Unique jobs = still possible for the same job to run twice if: worker crashes mid-job and another worker picks it up (TTL expiry). So fencing does matter even with unique resources. Redis: 10,000 acquisitions/hour = ~2.8/second — easily handled. ZooKeeper: 2.8 sequential znode creates/second — also fine, but 5-10x higher latency per acquisition. PostgreSQL: 10,000 advisory locks on a single DB — depends on DB connection count and lock table size. For unique-resource, high-volume, non-critical jobs: Redis trade-off may be acceptable. For idempotent job execution guarantee: what is the cost of a double-execution? That determines which option is appropriate.

**Q3 (A - System Interaction):** etcd's distributed lock (lease-based, used by Kubernetes) uses the following mechanism: (1) worker acquires lease (PUT key with TTL → lease ID returned). (2) Worker keeps lease alive by calling `keepAlive()` periodically (before TTL expiry). (3) On worker crash: keepAlive stops → lease expires → key deleted → next waiter acquires. Describe what happens if: (a) the worker's network partition isolates it from etcd but the worker is still running, (b) the worker's process is GC-paused longer than the keepAlive interval. In each scenario: does etcd correctly expire the lease, and does the protected resource receive inconsistent writes?
_Hint:_ Network partition from etcd: worker cannot call keepAlive → lease expires at TTL → etcd deletes key → another worker acquires lock. Worker (still running, just isolated from etcd) continues processing and tries to write to protected resource. Protected resource: if fencing token is enforced (etcd lease revision as fencing token) → isolated worker's write rejected (revision < current). Correct. GC pause > keepAlive interval: same effect as network partition from etcd's perspective — lease expires, another worker acquires. The paused worker resumes, tries to continue processing. Without fencing: double processing. With fencing: rejected. In BOTH cases: etcd correctly expires the lease. Safety depends entirely on whether the RESOURCE enforces fencing tokens.

