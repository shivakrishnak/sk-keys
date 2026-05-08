---
layout: default
title: "Write-Through"
parent: "Caching"
grand_parent: "Technical Dictionary"
nav_order: 8
permalink: /caching/write-through/
id: CCH-008
category: Caching
difficulty: ★★☆
depends_on: Cache-Aside, Read-Through, Caching
used_by: System Design, Caching
related: Cache-Aside, Write-Behind, Write-Around
tags:
  - caching
  - write-through
  - consistency
  - redis
---

# CCH-008 — Write-Through

⚡ TL;DR — Write-Through keeps the cache **always in sync with the database** by writing to **both the cache and the database on every write** — the write is considered complete only after both succeed; this guarantees that the cache never returns stale data (on reads after writes), at the cost of write latency and write amplification.

| #478            | Category: Caching                       | Difficulty: ★★☆ |
| :-------------- | :-------------------------------------- | :-------------- |
| **Depends on:** | Cache-Aside, Read-Through, Caching      |                 |
| **Used by:**    | System Design, Caching                  |                 |
| **Related:**    | Cache-Aside, Write-Behind, Write-Around |                 |

---

### 🔥 The Problem This Solves

**STALE CACHE AFTER WRITES:**
In Cache-Aside, a write invalidates the cache, and the next read re-populates it from the database. In the window between invalidation and re-population (50-100ms for a busy endpoint), multiple readers may see a miss and hit the database simultaneously (mini-stampede). Write-Through eliminates this window: the cache is updated atomically with the database write, so the next read always finds the fresh value in cache — zero stale window, zero miss on the read after write.

**WRITE-THROUGH GUARANTEES READ-AFTER-WRITE CONSISTENCY:**
After a write completes (cache + DB both updated), any subsequent read from cache returns the just-written value. This is critical for workflows like: "update user profile" → immediately "display updated profile" — the cache must have the fresh value.

---

### 📘 Textbook Definition

**Write-Through** is a caching pattern where every write operation is applied to **both the cache and the underlying database synchronously**. The write is considered complete (ACK returned to caller) only after both the cache write and the database write have succeeded. This ensures the cache is always consistent with the database: any data in the cache represents the latest committed state. Write-Through is typically combined with **Read-Through** to form a complete cache layer: reads are served from cache (with auto-load on miss), writes update both cache and DB. Trade-offs: (1) write latency = max(cache write, DB write) since both must succeed; (2) write amplification — every DB write also triggers a cache write, even for data that may never be read; (3) strong cache-DB consistency for all data in cache.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Every write goes to cache AND database simultaneously — complete only when both succeed; cache is always fresh.

**One analogy:**

> A ledger system with a working copy and an official copy. Every transaction is written to both simultaneously: the bookkeeper writes the entry in the working copy (cache) AND the official ledger (database) before confirming the transaction. Anyone who reads the working copy always sees the latest entries. Slower to write (two books), but readers always see current data.

- "Working copy" → Redis/Caffeine cache
- "Official ledger" → database (source of truth)
- "Write to both before confirming" → Write-Through synchronous dual write
- "Readers always see latest" → no stale cache after writes
- "Slower to write (two books)" → write latency penalty

**One insight:**
Write-Through eliminates stale reads after writes but does NOT eliminate cold-cache reads. When a new key is written: it's stored in cache immediately (future reads are fast). But if Redis crashes after Write-Through setup: the cache is empty, and first reads must load from DB. Write-Through ensures "writes are in cache" but NOT "all reads hit the cache" — the cache must be pre-warmed or accept first-time misses.

---

### 🔩 First Principles Explanation

**WRITE-THROUGH IMPLEMENTATION:**

```java
// Write-Through: write to cache AND database on every save
@Service
public class UserService {

    @Autowired private UserRepository userRepository;
    @Autowired private RedisTemplate<String, User> redisTemplate;

    private static final Duration TTL = Duration.ofMinutes(30);

    // WRITE: update DB + cache simultaneously
    @Transactional
    public User updateUser(Long userId, UserUpdateRequest req) {
        // Step 1: Update database (source of truth)
        User user = userRepository.findById(userId)
            .orElseThrow(() -> new UserNotFoundException(userId));
        user.setEmail(req.getEmail());
        user.setDisplayName(req.getDisplayName());
        user = userRepository.save(user);  // DB COMMIT

        // Step 2: Update cache (Write-Through: keep cache in sync)
        String cacheKey = "user:" + userId;
        redisTemplate.opsForValue().set(cacheKey, user, TTL);
        // Cache now has the same value as DB

        return user;
    }

    // CREATE: also cache immediately on insert
    @Transactional
    public User createUser(UserCreateRequest req) {
        User user = new User(req.getEmail(), req.getDisplayName());
        user = userRepository.save(user);

        // Cache the new user immediately (future reads will hit cache)
        redisTemplate.opsForValue().set("user:" + user.getId(), user, TTL);

        return user;
    }

    // DELETE: remove from both
    @Transactional
    public void deleteUser(Long userId) {
        userRepository.deleteById(userId);
        redisTemplate.delete("user:" + userId);
    }

    // READ: pure cache-aside (or read-through with @Cacheable)
    @Cacheable(value = "users", key = "#userId")
    public User getUser(Long userId) {
        return userRepository.findById(userId).orElseThrow();
    }
}

// Spring @CachePut = Write-Through semantics:
@CachePut(value = "users", key = "#result.id")
public User updateUser(Long userId, UserUpdateRequest req) {
    // @CachePut: ALWAYS runs method body AND updates cache with return value
    // Unlike @Cacheable (skip method body on cache hit), @CachePut always executes
    User user = userRepository.findById(userId).orElseThrow();
    user.setEmail(req.getEmail());
    return userRepository.save(user);
    // After return: Spring writes result to cache (Write-Through)
}
```

**CONSISTENCY MODEL COMPARISON:**

```
Write-Through consistency guarantee:
  WRITE: cache.set("user:42", newUser) + db.UPDATE(newUser) — both succeed
  NEXT READ: cache.get("user:42") → newUser (always fresh, no stale window)

  FAILURE SCENARIO: DB write fails (constraint violation)
    → cache.set may have already occurred
    → cache shows new value, DB still has old value
    → DATA INCONSISTENCY!

  FIX: Write DB FIRST, then cache:
    db.UPDATE(newUser) — if this fails, throw exception, never reach cache.set
    cache.set("user:42", newUser) — only executed after DB success

  Pattern: always write DB before cache in Write-Through
  (Cache is the "second write" — safe to fail silently, DB is authoritative)

  If cache.set fails (Redis down) after DB success:
    → DB is correct, cache is stale (or has old value)
    → Next read may return stale cache value
    → TTL will eventually expire, next read re-fetches from DB
    → Or: delete cache key on cache-write failure (forced cache miss = DB re-fetch)

  Best practice on cache-write failure:
    try { redisTemplate.opsForValue().set(key, value, ttl); }
    catch (RedisException e) {
      log.warn("Cache write failed, deleting key for safety: {}", key);
      redisTemplate.delete(key);  // Force cache miss → next read = fresh DB fetch
    }
```

**WRITE-THROUGH WITH PIPELINE (ATOMICITY ATTEMPT):**

```java
// Redis pipeline: send both DB write and cache write atomically
// NOTE: Redis pipeline is NOT a transaction — it batches commands but doesn't rollback
// For true atomicity across DB + Redis: use Redis MULTI/EXEC + DB transaction
// (Complex and rarely needed — best practice is DB-first write described above)

// Atomic DB + Cache (Spring @Transactional + Redis):
// PROBLEM: Spring @Transactional commits DB but doesn't integrate with Redis atomically
// If Redis write fails after @Transactional commit: inconsistency (acceptable with TTL)

// SOLUTION: Spring's TransactionSynchronizationAdapter
// Write to Redis AFTER DB transaction commits (not during):
@Transactional
public User updateUser(Long userId, UserUpdateRequest req) {
    User user = userRepository.findById(userId).orElseThrow();
    user.setEmail(req.getEmail());
    user = userRepository.save(user);

    final User savedUser = user;
    // Register post-commit hook: only update cache AFTER DB transaction commits
    TransactionSynchronizationManager.registerSynchronization(
        new TransactionSynchronization() {
            @Override
            public void afterCommit() {
                // Executed only after DB transaction successfully commits
                redisTemplate.opsForValue().set("user:" + savedUser.getId(), savedUser, TTL);
            }
        }
    );

    return user;
}
// Benefit: Redis write only happens if DB commit succeeded → no cache/DB inconsistency
// If Redis write fails: cache miss → next read fetches from DB (safe degradation)
```

---

### 🧪 Thought Experiment

**WRITE-THROUGH ON A HIGH-WRITE WORKLOAD:**

An IoT system receives 100,000 sensor readings per second, each stored in TimescaleDB. Using Write-Through: every write → store in Redis + store in TimescaleDB.

**Problems:**

1. Write amplification: 100,000/s DB writes → also 100,000/s Redis writes. Redis handles 100K/s easily, but the added latency of two round trips per write matters.
2. Useless caching: most sensor readings are written once and never read (time-series append-only data). Cache fills up with data that's never accessed from cache.
3. Memory waste: Redis fills with IoT data that occupies memory but is never cache-hit.

**Conclusion:** Write-Through is wrong for append-only, rarely-re-read data. Cache-Aside (only cache data that's actually read frequently) or Write-Around (skip the cache on writes) is appropriate for IoT/time-series. Write-Through excels for: user profile data, configuration data, frequently-read-after-write entities where read-after-write consistency matters.

---

### 🧠 Mental Model / Analogy

> Write-Through is like a doctor who writes every patient note in both the visiting room chart (cache) AND the central medical records system (database) before seeing the next patient. Slower (writes to both systems), but any nurse who needs the chart (next read) always finds the latest information in the visiting room — no need to go to the central system. Compare to Write-Behind: doctor writes in visiting room chart only, and a clerk batches the updates to the central system later — faster visits, but the central system may be briefly out of date.

- "Visiting room chart" → Redis cache
- "Central medical records" → database
- "Writes to both before next patient" → synchronous Write-Through (write latency)
- "Nurse always finds latest" → no stale reads after writes
- "Clerk batches later" → Write-Behind (async DB write after cache write)

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Write-Through: every write goes to cache AND database. Reads are always fresh — no stale data after writes. Cost: every write is slower (two destinations). Good for data that is frequently read immediately after being written.

**Level 2:** Always write DB first, then cache. If DB write fails: don't write cache (throw exception). If cache write fails after DB success: log warning, delete cache key (force miss on next read). Use `@CachePut` for write-through with Spring Cache. Use `TransactionSynchronizationManager` post-commit hook to ensure cache write happens only after DB commit.

**Level 3:** Write-Through + Read-Through combination: reads auto-load from DB on miss (Read-Through), writes update both DB + cache (Write-Through). Together, this forms a complete transparent cache layer — the application never directly interacts with the DB. This is the architecture of AWS DAX for DynamoDB: all reads go to DAX (read-through), all writes go through DAX (write-through), application only sees the DAX API. Performance: reads fast (cache hit), writes slightly slower (two destinations), but stale data is eliminated.

**Level 4:** Write-Through is the foundation of many distributed caching strategies but faces a fundamental challenge in distributed systems: updating both the cache and the database atomically is impossible without a distributed transaction (2PC). The standard mitigation is "DB first then cache, accept brief inconsistency on cache failure." This is safe because: (1) the DB is always the source of truth; (2) cache inconsistency is bounded by TTL; (3) deleting the cache key on failure forces a fresh DB read. At large scale (multiple data centers), Write-Through must handle replication lag: writing to cache in region A and database in region A (replicated to region B), but region B's cache still has the old value until either it processes the DB replication event or TTL expires. CRDTs and vector clocks are the theoretical tools for multi-region cache consistency, but in practice, eventual consistency with short TTLs is the industry standard.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ WRITE-THROUGH vs CACHE-ASIDE WRITE                   │
├──────────────────────────────────────────────────────┤
│                                                      │
│ CACHE-ASIDE WRITE:                                   │
│   App → DB UPDATE (commit)                           │
│   App → Redis DEL key (invalidate)                   │
│   Next read: cache miss → DB fetch → cache populate  │
│   Stale window: from DEL until next read populates   │
│                                                      │
│ WRITE-THROUGH:                                       │
│   App → DB UPDATE (commit)                           │
│   App → Redis SET key value (update, not delete)     │
│   Next read: cache HIT → returns fresh value         │
│   Stale window: ZERO (cache updated on write)        │
│                                                      │
│ [WRITE-THROUGH ← YOU ARE HERE: SET after commit]     │
│                                                      │
│ Cost: +1 Redis write per DB write (write amplification)
│ Benefit: zero stale cache after any write            │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**USER PROFILE SERVICE WITH WRITE-THROUGH:**

```
1. User updates email: PUT /users/42 {email: "new@example.com"}
→ UserService.updateUser(42, {email: "new@example.com"})
→ [WRITE-THROUGH ← YOU ARE HERE]

2. @Transactional:
   UPDATE users SET email='new@example.com' WHERE id=42
   COMMIT
   → afterCommit hook fires:
   Redis: SET user:42 '{"id":42,"email":"new@example.com",...}' EX 1800

3. Response: 200 OK {updated user}

4. Immediate read: GET /users/42
   → Redis GET user:42 → HIT → {"email":"new@example.com"} ✓
   (Without Write-Through: cache miss → DB re-fetch needed)

5. 1000 subsequent reads within 30 min:
   → Redis HIT → fresh data → 2ms each (not 20ms DB)

Cache Write Failure scenario:
   DB: COMMIT (success)
   Redis: SET user:42 → ConnectionException (Redis down)
   → catch: log warning + Redis DEL user:42 (safe: forces miss)
   → Next read: cache miss → DB fetch → fresh value ✓
   DB is authoritative — cache failure doesn't corrupt data
```

---

### ⚖️ Comparison Table

| Write Pattern            | Write Latency         | Stale Risk              | Write Amplification | Best For                             |
| ------------------------ | --------------------- | ----------------------- | ------------------- | ------------------------------------ |
| Cache-Aside (invalidate) | DB only               | Brief (miss window)     | 1×                  | Read-heavy, tolerate brief stale     |
| Write-Through            | DB + Cache            | None (always fresh)     | 2×                  | Read-after-write consistency needed  |
| Write-Behind             | Cache only (async DB) | Potential data loss     | 1× (async)          | Write-heavy, eventual consistency OK |
| Write-Around             | DB only (skip cache)  | Always stale until read | 1×                  | Write-once, rarely re-read           |

---

### ⚠️ Common Misconceptions

| Misconception                                              | Reality                                                                                                                                                                                                                                |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Write-Through guarantees ACID across DB + cache"          | Write-Through does NOT use a distributed transaction. If cache write fails after DB commit, the DB has the new value but cache has the old one. This is why "DB first, then cache" + "delete on cache failure" is essential            |
| "Write-Through is slower because it writes twice"          | Write latency in Write-Through ≈ max(DB write time, Redis write time) because DB is always the slower operation. Redis writes (< 1ms) are negligible compared to DB writes (5-20ms). Total overhead is minimal                         |
| "Write-Through and @CachePut are the same as Write-Behind" | Write-Through writes DB synchronously (before returning to caller). Write-Behind writes DB asynchronously (after returning to caller). Spring `@CachePut` is Write-Through — the method body (DB write) runs before caching the result |

---

### 🚨 Failure Modes & Diagnosis

**1. Cache/DB Inconsistency After Redis Failure**

**Symptom:** Users report seeing old email addresses after updating their profile. Profile update API returns 200. Redis is intermittently unavailable (Redis cluster failover in progress).

**Root Cause:** Write-Through: DB updated (success), Redis SET fails (Redis unavailable). Old value persists in Redis after Redis recovers from failover. TTL hasn't expired yet. Reads return stale data from Redis.

**Fix:**

```java
// On cache-write failure: DELETE (force miss) instead of leaving stale value
try {
    redisTemplate.opsForValue().set("user:" + userId, updatedUser, Duration.ofMinutes(30));
} catch (RedisException e) {
    log.warn("Write-Through cache update failed for user:{}. Invalidating to prevent stale reads.", userId);
    try {
        redisTemplate.delete("user:" + userId);  // Force cache miss = fresh DB read
    } catch (RedisException e2) {
        log.error("Cache invalidation also failed for user:{}. Stale data risk until TTL expires.", userId);
        // Last resort: short TTL on stale entries means eventual self-healing
    }
}
```

---

### 🔗 Related Keywords

**Prerequisites:** Cache-Aside, Read-Through, Caching
**Builds On This:** System Design
**Related:** Cache-Aside, Write-Behind, Write-Around

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PATTERN     │ Write → DB + Cache (both must succeed)     │
│ BENEFIT     │ Zero stale after write; read-after-write ✓ │
│ COST        │ +1 Redis write per DB write                │
│ ORDER       │ ALWAYS: DB first → then cache              │
│ ON FAIL     │ Cache write fails → DELETE key (force miss) │
│ SPRING      │ @CachePut = Write-Through semantics        │
│ AVOID FOR   │ Append-only data, write-heavy time-series  │
│ ONE-LINER   │ "Write to DB then cache; next read is always│
│             │  guaranteed fresh from cache"               │
│ NEXT EXPLORE│ Write-Behind → Cache Invalidation          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE F — Comparison) A social media app has two features: (a) user profile (read 1000× per write), (b) activity feed (read once, then cached for 5 minutes, write-heavy — 10,000 writes/second). Choose the appropriate write strategy for each feature and justify with latency, consistency, and resource implications.

**Q2.** (TYPE D — Failure Scenario) A Write-Through implementation writes to Redis BEFORE writing to the database. A database constraint violation occurs (unique email). The cache has been updated with the new email; the DB rejects it. Describe: (a) the inconsistency state, (b) impact on subsequent reads, (c) how long the inconsistency persists, (d) the correct fix.
