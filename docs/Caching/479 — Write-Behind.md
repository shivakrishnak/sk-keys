---
layout: default
title: "Write-Behind"
parent: "Caching"
nav_order: 479
permalink: /caching/write-behind/
number: "0479"
category: Caching
difficulty: ★★★
depends_on: Write-Through, Cache-Aside, Caching
used_by: System Design, Distributed Systems
related: Write-Through, Cache Invalidation, Saga Pattern (DB)
tags:
  - caching
  - write-behind
  - async-write
  - durability
  - deep-dive
---

# 479 — Write-Behind

⚡ TL;DR — Write-Behind (write-back) writes to the **cache first and returns immediately to the caller**, then asynchronously flushes the cached writes to the database later; this achieves very low write latency and high write throughput at the cost of **durability risk** — data in cache but not yet in the database can be lost if the cache crashes.

| #479            | Category: Caching                                    | Difficulty: ★★★ |
| :-------------- | :--------------------------------------------------- | :-------------- |
| **Depends on:** | Write-Through, Cache-Aside, Caching                  |                 |
| **Used by:**    | System Design, Distributed Systems                   |                 |
| **Related:**    | Write-Through, Cache Invalidation, Saga Pattern (DB) |                 |

---

### 🔥 The Problem This Solves

**DATABASE WRITES ARE THE BOTTLENECK:**
For write-heavy workloads (gaming leaderboards, live counters, real-time bidding, IoT sensor writes), the database is the bottleneck. Each write must wait for: network round trip to DB (1-5ms), disk fsync (PostgreSQL `synchronous_commit = on`: 5-20ms per commit), WAL write, index update. At 50ms per write, a single PostgreSQL instance handles ~20 writes/second per connection.

**WRITE-BEHIND REMOVES THE DB FROM THE WRITE HOT PATH:**
Write to Redis (< 1ms, in-memory, no disk sync). Return success immediately. A background process batches and flushes Redis writes to the DB asynchronously. The caller doesn't wait for DB — they get sub-millisecond write latency. Throughput: Redis handles 100,000+ writes/second. Database sees batched writes at manageable rates.

---

### 📘 Textbook Definition

**Write-Behind** (also **Write-Back**) is a caching strategy where write operations are applied to the **cache immediately** and the **caller is returned success before the database is updated**. The database update is deferred and performed asynchronously by a background process (flush daemon, scheduler, or message queue). This strategy prioritizes write latency and throughput: the caller's write path is as fast as the cache (sub-millisecond), and database writes are batched for efficiency. Risk: data in the cache that hasn't been flushed to the database is **vulnerable to loss** if the cache crashes or is evicted before flushing — the "dirty" data is gone. Implementations: **Redis with custom flush daemon**, **Ehcache write-behind threads**, **database buffer pool** (MySQL InnoDB buffer pool: data is written to in-memory buffer first, flushed to disk by background cleaner threads — this is Write-Behind at the storage engine level), **CPU write-back caches** (L1/L2 cache: writes go to cache first, flushed to RAM on eviction — the original Write-Behind in computer architecture).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Write to cache, return success immediately, flush to database later in background — ultra-low write latency, but "dirty" data in cache can be lost before flushing.

**One analogy:**

> A barista takes your order (write to cache — instant acknowledgment) and puts a ticket on the spike. You're confirmed: "Got it!" Your order hasn't gone to the kitchen yet (database). The cook periodically grabs all tickets from the spike and processes them in batch (background flush). Faster for you (immediate confirmation), but if the spike catches fire before the cook sees your ticket (cache crash before flush): your order is lost.

- "Barista takes order → immediate confirmation" → Write-Behind: write to cache, return ACK
- "Ticket on the spike" → dirty write in Redis
- "Cook grabs batch" → background flush thread: batch-write to DB
- "Spike catches fire" → Redis crash before flush → data loss
- "Your order is lost" → dirty data lost = durability gap

**One insight:**
Write-Behind is fundamentally a durability-latency tradeoff. Durability means: every committed write survives system failure. Write-Through achieves this (DB commit = durable). Write-Behind sacrifices durability: data is "confirmed" to the caller but stored only in cache (volatile). The database — the durable store — lags behind. The gap between cache write and DB write is the **durability window** — the maximum data loss window on crash. Minimize this by: short flush intervals (1-5 seconds), Redis persistence (AOF with fsync=always), or using a durable message queue (Kafka) as the "dirty write buffer" instead of in-memory cache.

---

### 🔩 First Principles Explanation

**WRITE-BEHIND WITH REDIS + SCHEDULED FLUSH:**

```java
// Write-Behind pattern: write to Redis first, flush to DB asynchronously

@Service
public class ScoreService {

    private static final String LEADERBOARD_KEY = "leaderboard:global";
    private static final String DIRTY_SCORES_KEY = "dirty:scores"; // Set of dirty user IDs

    // WRITE: sub-millisecond (Redis only)
    public void updateScore(String userId, int delta) {
        // Step 1: Update cache immediately (Write-Behind)
        redisTemplate.opsForZSet().incrementScore(LEADERBOARD_KEY, userId, delta);

        // Step 2: Mark as dirty (needs DB flush)
        redisTemplate.opsForSet().add(DIRTY_SCORES_KEY, userId);

        // Step 3: Return SUCCESS immediately
        // DB has NOT been updated yet — caller doesn't wait for DB
        // Latency: < 1ms (Redis write)
    }

    // READ: fast (from Redis — always has latest, even before DB flush)
    public Long getRank(String userId) {
        return redisTemplate.opsForZSet().reverseRank(LEADERBOARD_KEY, userId);
    }

    // BACKGROUND FLUSH: periodically sync dirty entries to DB
    @Scheduled(fixedDelay = 5000)  // flush every 5 seconds
    @Transactional
    public void flushDirtyScoresToDatabase() {
        // Get all dirty user IDs
        Set<String> dirtyUserIds = redisTemplate.opsForSet().members(DIRTY_SCORES_KEY);
        if (dirtyUserIds == null || dirtyUserIds.isEmpty()) return;

        // Fetch current scores from Redis
        for (String userId : dirtyUserIds) {
            Double score = redisTemplate.opsForZSet().score(LEADERBOARD_KEY, userId);
            if (score != null) {
                // Upsert to database (batch would be more efficient)
                scoreRepository.upsertScore(userId, score.longValue());
            }
        }

        // Clear dirty set after successful DB write
        redisTemplate.delete(DIRTY_SCORES_KEY);

        log.info("Flushed {} dirty scores to database", dirtyUserIds.size());
    }
}

// DURABILITY RISK: if Redis crashes between updateScore() and flushDirtyScoresToDatabase():
// → dirty scores are LOST (not in DB, not in Redis anymore)
// → last flush point = consistent state; everything since last flush = gone
// For leaderboard (gaming): acceptable (lose < 5 seconds of score updates)
// For financial data: NOT acceptable — use Write-Through instead
```

**WRITE-BEHIND WITH DURABLE QUEUE (SAFER):**

```java
// Safer Write-Behind: use Kafka as durable "dirty write buffer"
// Even if Redis crashes, Kafka retains the write events

@Service
public class SafeWriteBehindService {

    public void updateUserBalance(String userId, BigDecimal delta) {
        // Step 1: Update Redis (fast, for reads)
        redisTemplate.opsForHash().increment("user:balance", userId, delta.longValue());

        // Step 2: Publish to Kafka (durable write record)
        // Kafka: replication factor=3, acks=all → durable even on broker failure
        kafkaTemplate.send("balance-updates",
            userId,  // key (ensures same user goes to same partition → ordered)
            new BalanceUpdateEvent(userId, delta, Instant.now())
        );
        // Return SUCCESS: caller gets ACK after Redis + Kafka write
        // DB not yet updated — but Kafka has the event durably
    }

    // Kafka consumer (separate service / same service): flush events to DB
    @KafkaListener(topics = "balance-updates", groupId = "balance-db-writer")
    @Transactional
    public void persistBalanceUpdate(BalanceUpdateEvent event) {
        // Idempotent: use event ID to prevent double-apply
        if (!processedEventRepository.exists(event.getEventId())) {
            userBalanceRepository.addDelta(event.getUserId(), event.getDelta());
            processedEventRepository.save(event.getEventId());
        }
    }
}
// Durability: Kafka survives Redis crash — no data loss
// Latency: Redis (< 1ms) + Kafka publish (~2ms) = 3ms total (vs 20ms Write-Through)
// Complexity: higher (Kafka + consumer + idempotency tracking)
```

**DIRTY PAGE EVICTION RISK:**

```
Redis dirty data lifecycle:
  1. Write hits Redis: key marked as dirty
  2. Redis memory fills: LRU eviction kicks in
  3. Redis evicts a dirty key BEFORE background flush
  4. That write is permanently lost — never reached DB

Prevention:
  Option A: Redis maxmemory-policy = noeviction
    → Redis refuses new writes when memory full
    → Application gets an error → can handle gracefully (fall back to DB write)
    → No data loss, but requires memory capacity planning

  Option B: Track dirty keys in a separate set
    → Before evicting, check if key is in dirty set
    → If dirty: flush to DB before evicting
    → Custom logic (not built into Redis out-of-the-box)

  Option C: Use Kafka as buffer (previous example)
    → Dirty data is in Kafka (durable), not just Redis
    → Redis eviction is safe (Kafka still has the event)

Production recommendation for Write-Behind:
  If data loss > 0 events is not acceptable → do NOT use Write-Behind
  If "lose up to N seconds of writes" is acceptable → Write-Behind is appropriate
  Always document the durability SLA clearly: "up to 5 second data loss window"
```

---

### 🧪 Thought Experiment

**WRITE-BEHIND FOR FINANCIAL TRANSACTIONS?**

Banking: user transfers $100. Write-Behind: debit Redis counter (-$100), return success, flush to DB in 5 seconds.

**Scenario 1:** Between return-success and DB flush, Redis crashes. DB still shows +$100 balance. But the user received a "success" confirmation and may have already spent the funds elsewhere. $100 has "appeared" to vanish.

**Scenario 2:** Redis is slow to flush. User's bank account shows $100 deducted (from Redis read). They check on another device (different cache): $100 still there (DB hasn't been updated yet). Money appears in two places simultaneously.

**Conclusion:** Write-Behind is fundamentally incompatible with financial-grade durability requirements. Write-Through + ACID PostgreSQL is mandatory for money movement. Write-Behind is appropriate for: gaming scores, view counts, non-critical counters, analytics events, session data — where brief data loss is acceptable and stated clearly in the SLA.

---

### 🧠 Mental Model / Analogy

> Write-Behind is like a whiteboard at a restaurant kitchen. Waiters scribble orders on the whiteboard (cache write — instant), tell the customer "order received!" (return ACK), and a dedicated "transcription person" periodically copies all whiteboard orders to the official order book (DB flush). Ultra-fast order taking. Risk: if the whiteboard is erased (cache crash) before transcription, those orders are permanently lost. The customer was told "order received" but the kitchen never got it.

- "Write on whiteboard" → Redis write (Write-Behind)
- "Tell customer confirmed" → return ACK to caller
- "Transcription person" → background flush thread/scheduler
- "Official order book" → database
- "Whiteboard erased before transcription" → Redis crash before flush → data loss

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Write-Behind: write to cache first, return success, flush to DB asynchronously. Ultra-low write latency. Risk: data in cache not yet in DB can be lost on crash. Use for: high-frequency, non-critical writes (counters, leaderboards). Never use for: financial data, critical business records.

**Level 2:** Implement flush with `@Scheduled` (simple) or Kafka (durable). Track dirty keys in a Redis Set to know what needs flushing. Set Redis `maxmemory-policy = noeviction` to prevent dirty data eviction. Define and document the durability window (e.g., "up to 5s data loss on Redis crash"). Monitor flush lag: alert if dirty set size exceeds threshold (indicates flush is falling behind write rate).

**Level 3:** Batch efficiency: instead of flushing one record at a time, collect dirty IDs and issue a single `UPSERT ... ON CONFLICT` batch write: `INSERT INTO scores (user_id, score) VALUES (...) ON CONFLICT (user_id) DO UPDATE SET score = EXCLUDED.score`. This reduces DB write amplification significantly: 1,000 individual Redis writes → 1 DB batch insert (1ms vs. 1,000 × 5ms = 5,000ms). Write-Behind at the DB engine level: MySQL InnoDB buffer pool is Write-Behind architecture — modified pages ("dirty pages") stay in buffer pool and are flushed by background cleaner threads. PostgreSQL shared_buffers + bgwriter is the same pattern. Both use WAL as the durability guarantee (WAL is synchronous; dirty pages flush is asynchronous).

**Level 4:** Write-Behind is a special case of the **command pattern + event sourcing**: the "write to cache" step records the intent (like an event log), and the background flush applies the intent to the durable store. The key insight: if the intent log (Kafka) is durable but the application state (Redis) is volatile, you get durable Write-Behind — the event is not lost even if the in-memory state is. This is why Kafka-backed Write-Behind is categorically safer than pure Redis Write-Behind: Kafka's durability guarantees (replication, fsync) mean the "dirty write" survives any single-node failure. The application's state can always be rebuilt from Kafka. This transforms Write-Behind into an eventually-consistent, durable, high-throughput write architecture — used by systems like Twitter's timeline service, LinkedIn's activity streams, and high-frequency gaming leaderboards at scale.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ WRITE-BEHIND LIFECYCLE                               │
├──────────────────────────────────────────────────────┤
│                                                      │
│ WRITE PATH (caller):                                 │
│   App → Redis ZADD score:user42 1000 (< 1ms)         │
│   App → Redis SADD dirty:users user42                │
│   App ← SUCCESS returned immediately                 │
│   DB: NOT YET UPDATED ← this is the durability gap   │
│                                                      │
│ BACKGROUND FLUSH (every 5s):                         │
│   Scheduler: SMEMBERS dirty:users → [user42, user99] │
│   DB: INSERT INTO scores (user_id, score)            │
│       VALUES (42, 1000), (99, 500)                   │
│       ON CONFLICT DO UPDATE SET score=EXCLUDED.score  │
│   Redis: DEL dirty:users                             │
│   DB is now up-to-date ✓                             │
│                                                      │
│ CRASH BETWEEN WRITE AND FLUSH:                       │
│   Redis crashes after ZADD but before DB flush       │
│   → dirty:users set lost (Redis volatile)            │
│   → user42's new score is GONE                       │
│   → DB shows last flushed value (stale)              │
│   [WRITE-BEHIND ← YOU ARE HERE: durability gap]      │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**GAMING LEADERBOARD WITH WRITE-BEHIND:**

```
Player Alice: scores 500 points
→ ScoreService.updateScore("alice", 500)
→ [WRITE-BEHIND ← YOU ARE HERE: Redis first, DB later]

→ Redis ZADD leaderboard:global alice 500 (atomic increment)
→ Redis SADD dirty:players alice
→ Return: "Score updated!" — 0.8ms total

Background flush (runs every 5 seconds):
→ Redis SMEMBERS dirty:players → [alice, bob, carol, ...]
→ PostgreSQL: INSERT INTO player_scores (player_id, score) VALUES
     ('alice', 500), ('bob', 1200), ('carol', 300)
   ON CONFLICT (player_id) DO UPDATE SET score = EXCLUDED.score,
     updated_at = NOW()
→ Redis: DEL dirty:players

1,000 score updates per second:
→ Redis: handles 100K ops/s → no bottleneck
→ DB: sees 1 batch write every 5 seconds (not 5,000 individual writes)
→ DB load reduction: 5,000 writes → 1 batch = 5,000× fewer DB operations

Read leaderboard: GET /leaderboard/top100
→ Redis ZREVRANGE leaderboard:global 0 99 WITHSCORES
→ Returns top 100 scores (fresh: includes unflushed writes)
→ DB not queried ← reads are always fresh from Redis ✓
```

---

### ⚖️ Comparison Table

| Aspect           | Write-Through                   | Write-Behind                             | Cache-Aside (invalidate)     |
| ---------------- | ------------------------------- | ---------------------------------------- | ---------------------------- |
| Write latency    | DB latency (slow path)          | Cache latency (< 1ms)                    | DB latency                   |
| Write throughput | Limited by DB                   | Limited by cache (100K+/s)               | Limited by DB                |
| Durability       | Strong (DB committed = durable) | Weak (data loss window = flush interval) | Strong                       |
| Complexity       | Medium                          | High (flush daemon, dirty tracking)      | Low                          |
| Best for         | Profile data, critical records  | Counters, leaderboards, non-critical     | General read-heavy workloads |

---

### ⚠️ Common Misconceptions

| Misconception                                             | Reality                                                                                                                                                                                                      |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "Write-Behind is the same as Write-Through with async DB" | Write-Behind: caller gets ACK before DB write. Write-Through: caller waits until BOTH cache and DB succeed. The timing of the ACK is the critical difference — durability semantics are completely different |
| "Redis persistence (AOF) makes Write-Behind safe"         | Redis AOF (fsync=everysec) only protects against Redis process crash, not Redis host failure (hardware, OOM). Even with AOF, Write-Behind has durability risk — the DB is the only truly durable store       |
| "Write-Behind always loses data on crash"                 | With Kafka as the write buffer (instead of volatile Redis), Write-Behind is durable — Kafka's replicated log survives node failures. The Redis in-memory state is rebuilt from Kafka on recovery             |

---

### 🚨 Failure Modes & Diagnosis

**1. Write-Behind Flush Falling Behind Write Rate**

**Symptom:** Redis `dirty:players` set is growing: 100 → 10,000 → 1,000,000 members over 1 hour. DB and Redis show increasingly divergent data. Background flush scheduler is logging slowly but not catching up.

**Root Cause:** Write rate (50,000 writes/second) exceeds flush throughput (5,000 rows/flush × every 5 seconds = 1,000 rows/second). Flush is 50× too slow.

**Fix:**

```java
// Increase parallelism: multiple flush threads
@Scheduled(fixedDelay = 1000)  // flush every 1 second (not 5)
@Async("flushExecutor")         // async thread pool
public void flushDirtyScores() { ... }

// Or: batch larger, flush less often but more efficiently
// Use COPY command (PostgreSQL) for bulk insert: 10× faster than individual INSERTs

// Or: use Kafka partition parallelism
// Kafka consumers: multiple partitions → multiple parallel DB writers
// Scale consumers until flush throughput > write throughput

// Alert: dirty set size > 100,000 → flush is falling behind → PagerDuty
```

---

### 🔗 Related Keywords

**Prerequisites:** Write-Through, Cache-Aside, Caching
**Builds On This:** System Design, Distributed Systems
**Related:** Write-Through, Cache Invalidation, Saga Pattern (DB)

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ PATTERN     │ Write cache → ACK caller → flush DB async  │
│ LATENCY     │ < 1ms (cache write only)                   │
│ DURABILITY  │ WEAK: data loss window = flush interval    │
│ DIRTY TRACK │ Redis Set of pending-flush keys            │
│ SAFE BUFFER │ Kafka (durable) > Redis (volatile)         │
│ USE FOR     │ Leaderboards, counters, gaming, analytics  │
│ NEVER FOR   │ Financial transactions, critical records    │
│ MONITOR     │ dirty-set size; flush lag; DB vs cache diff│
│ ONE-LINER   │ "Cache first, DB later — fast writes, weak │
│             │  durability — document the data loss SLA"  │
│ NEXT EXPLORE│ Cache Invalidation → TTL                   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C — Design Question) Design a Write-Behind system for a real-time multiplayer game where 1 million players update their scores simultaneously during a 30-minute event. Requirements: write latency < 5ms, read latency < 10ms (from leaderboard), data loss acceptable up to 30 seconds, must survive a single Redis node failure. Design the cache structure, dirty tracking, flush mechanism, and failure handling. Include Redis persistence settings and a Kafka-based fallback.

**Q2.** (TYPE D — Failure Scenario) A Write-Behind system has been running for 6 months. One morning, the Redis cluster is restarted for a maintenance upgrade. The Redis data is cleared during the upgrade (no persistence configured). After restart, 4 minutes of score updates from 50,000 players are gone. The DB still has data from the last successful flush. Walk through: (a) what users experience, (b) how you diagnose the extent of the data loss, (c) how you prevent this in the future, (d) is there any way to recover the lost 4 minutes of data?
