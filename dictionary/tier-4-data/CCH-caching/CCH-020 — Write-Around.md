---
layout: default
title: "Write-Around"
parent: "Caching"
nav_order: 20
permalink: /caching/write-around/
id: CCH-020
category: Caching
difficulty: ★★★
depends_on: Cache-Aside, Write-Through, Write-Behind
used_by: System Design, Caching
related: Write-Through, Write-Behind, Cache-Aside
tags:
  - caching
  - write-around
  - cache-strategies
  - write-patterns
  - deep-dive
---

# CCH-020 — Write-Around

⚡ TL;DR — Write-Around means **bypass the cache on writes** — write directly to the database, and only cache data when it is subsequently read; it is the inverse of Write-Through (which always populates the cache on write) and is ideal for write-once/read-rarely workloads like IoT telemetry, audit logs, and archived records that would otherwise pollute the cache with data unlikely to be re-read.

| #490            | Category: Caching                        | Difficulty: ★★★ |
| :-------------- | :--------------------------------------- | :-------------- |
| **Depends on:** | Cache-Aside, Write-Through, Write-Behind |                 |
| **Used by:**    | System Design, Caching                   |                 |
| **Related:**    | Write-Through, Write-Behind, Cache-Aside |                 |

---

### 🔥 The Problem This Solves

**CACHE POLLUTION FROM WRITE-HEAVY WORKLOADS:**
Write-Through strategy: every write → update DB + update cache. For an IoT sensor system writing 100,000 temperature readings/minute: every reading is written to both DB and cache. Cache capacity: 100K entries. After 1 minute: cache is full of temperature readings. But 99% of these readings are NEVER read again (monitoring queries aggregate data, not fetch individual readings). The cache is full of useless entries, evicting hot data (user profiles, product catalog) to make room. **Cache pollution** — writing data to cache that will never be read from cache.

**AUDIT LOG WRITES:**
Every user action creates an audit log entry. 500K users × 10 actions/day = 5M audit entries/day. Write-Through: all 5M entries in cache. Individual audit entries are almost never read (only compliance queries aggregate them). Cache is polluted with audit entries, displacing actual hot data.

---

### 📘 Textbook Definition

**Write-Around** (also **write-direct** or **write-bypass**) is a cache write strategy where **writes go directly to the storage layer (database) without updating the cache**. The cache is only populated on a subsequent read (cache miss → DB → populate cache), as in the Cache-Aside pattern's read path. Write-Around is the default behavior of Cache-Aside when writes explicitly invalidate (DEL) rather than update the cache. **Key property**: on a write, the cache entry for the written key is invalidated (deleted) if it exists, but no new cache entry is created. On the next read: cache miss → DB → populate cache. **When to use**: write-heavy workloads where the written data is rarely re-read; batch writes (bulk inserts); append-only data (logs, events, telemetry); data that is processed asynchronously before being read. **When NOT to use**: write-then-immediately-read patterns (e.g., create user → redirect to user profile page → profile page reads from cache → MISS because Write-Around didn't populate).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Write-Around = write directly to the database, skip the cache; cache is only populated on the next read — prevents writing-once/never-read data from polluting the cache.

**One analogy:**

> A library acquires thousands of books per month. Write-Through: every new book acquisition immediately placed on the "most popular" shelf (cache). Problem: 90% of new acquisitions are obscure reference books that patrons rarely check out — they displace the popular novels. Write-Around: new books go directly to the archive shelves (database). A book only gets placed on the "most popular" shelf when a patron actually checks it out (first read populates cache). The popular shelf stays occupied by actually popular books.

- "New book acquisition" → write operation
- "Archive shelves" → database
- "Most popular shelf" → cache
- "Book placed on popular shelf when first checked out" → cache populated on first read
- "Obscure reference books displacing popular novels" → cache pollution

**One insight:**
The "write-around" vs. "write-through" decision is fundamentally a **read-frequency prediction** at write time. Write-through is optimal when every write will be followed by one or more reads (read probability ≈ 1). Write-around is optimal when most writes will NEVER be read individually (read probability ≈ 0). For most real systems, a hybrid applies: write-around for high-volume append-only data (events, logs, telemetry), write-through or cache-invalidation for entity data (users, products, orders) that IS read frequently.

---

### 🔩 First Principles Explanation

**WRITE-AROUND IN CACHE-ASIDE:**

```java
// Cache-Aside is naturally Write-Around when writes only invalidate (DEL) the cache
// rather than updating (SET) it.

@Service
public class UserService {

    // Write-Around: write to DB, then DEL cache (not SET new value in cache)
    @Transactional
    public User updateUser(String userId, UserUpdateRequest req) {
        // 1. Write to DB (source of truth)
        User updated = userRepository.save(new User(userId, req));

        // 2. BYPASS CACHE: don't SET the new value in cache
        // Instead, just invalidate the old cached value (if any)
        redisTemplate.delete("user:" + userId);

        // 3. Return the DB result
        return updated;

        // Next read for this user:
        // Redis GET user:userId → nil (MISS — key was deleted)
        // DB SELECT → fresh value → Redis SET → populate cache
        // The cache is populated LAZILY on next read
    }

    // Read: Cache-Aside read path (unchanged)
    public User getUser(String userId) {
        User cached = redisTemplate.opsForValue()
            .get("user:" + userId, User.class);
        if (cached != null) return cached;

        User dbUser = userRepository.findById(userId).orElseThrow();
        redisTemplate.opsForValue().set("user:" + userId, dbUser, Duration.ofMinutes(15));
        return dbUser;
    }
}
```

**WRITE-AROUND FOR PURE APPEND-ONLY DATA (IoT):**

```java
// IoT temperature sensor data: write millions of readings per hour
// Individual readings are almost never read — only aggregates are queried
// Perfect Write-Around use case: never pollute cache with sensor readings

@Service
public class SensorDataService {

    // Write-Around: writes go ONLY to DB (no cache involvement)
    public void recordReading(SensorReading reading) {
        // Write directly to DB (time-series database or PostgreSQL)
        sensorRepository.save(reading);

        // NO cache operation — not even invalidation
        // Cache is never aware this write happened
        // Individual readings are write-once, never individually read
    }

    // Aggregate queries: only these are worth caching
    @Cacheable(value = "sensor-aggregates", key = "#sensorId + ':' + #hour")
    public SensorAggregate getHourlyAggregate(String sensorId, String hour) {
        // This is cached because aggregates ARE read repeatedly
        // Individual readings are NOT cached (Write-Around for writes)
        return sensorRepository.calculateHourlyAvg(sensorId, hour);
    }

    // Access pattern:
    // 100K writes/min: sensor readings → DB only (Write-Around)
    // 1K reads/min: aggregates → cache hit (cached on first read)
    // Cache contents: only aggregates (small, frequently read)
    // Cache NOT polluted with 100K sensor readings (large, never individually read)
}
```

**COMPARISON: WRITE-THROUGH vs. WRITE-AROUND:**

```java
// Write-Through: always update cache on write
@Transactional
public Product updateProductPrice(String id, BigDecimal price) {
    Product product = productRepository.updatePrice(id, price);

    // Write-Through: update cache IMMEDIATELY after DB write
    redisTemplate.opsForValue().set("product:" + id, product, Duration.ofMinutes(15));

    return product;
    // Benefit: next read → cache HIT (no DB query)
    // Risk: cache always has fresh data (no stale window at all)
}

// Write-Around: skip cache update, only invalidate
@Transactional
public Product updateProductPriceWriteAround(String id, BigDecimal price) {
    Product product = productRepository.updatePrice(id, price);

    // Write-Around: just DELETE from cache (don't populate with new value)
    redisTemplate.delete("product:" + id);

    return product;
    // Benefit: no cache pollution; next read fetches fresh from DB
    // Risk: next read → cache MISS (one extra DB query to repopulate)
}

// When to use which:
// Write-Through: product price changes are infrequent AND reads are very frequent
//   → cache always warm after write, high hit rate
// Write-Around: product catalog is huge (1M products), updates are rare
//   → only actually-read products enter cache; cache stays unclogged
```

**AUDIT LOG WRITE-AROUND:**

```java
@Service
public class AuditService {

    // Write-Around: audit entries written to DB only
    // Individual audit entries are NEVER individually read in normal operation
    // Compliance queries use aggregates and filtered queries (not by audit_id)
    public void audit(String userId, String action, Object details) {
        AuditEntry entry = new AuditEntry(userId, action, details, Instant.now());
        auditRepository.save(entry);
        // No cache. No TTL. No Redis operation.
        // Write-Around: DB is the only destination.
    }

    // The ONLY read path that might be cached:
    // "Recent actions by user X" — could be cached (if frequently viewed by users)
    @Cacheable(value = "user-audit-summary", key = "#userId")
    public List<AuditEntry> getRecentActions(String userId) {
        return auditRepository.findByUserId(userId, PageRequest.of(0, 10));
        // This summary IS cached; individual entries are not
    }
}
```

---

### 🧪 Thought Experiment

**CACHE POLLUTION: BEFORE AND AFTER WRITE-AROUND**

Cache configuration: Redis, max 50K entries, LRU eviction. System: 1M users, 10K products. Top 10K products: 90% of product reads.

**Before Write-Around (Write-Through for everything):**
Every IoT sensor reading (100K/min) is written to cache. Cache fills with sensor data within 30 seconds. LRU eviction: sensor readings (accessed once each) are "recent" — they evict the top 10K products (accessed thousands of times per minute). Product cache hit rate: drops from 90% to 20%. Every product page load → DB query. DB overload.

**After Write-Around for sensor data:**
Sensor readings: DB only (Write-Around). Cache: contains top 10K products (stable, frequently read). Product cache hit rate: 90% (no eviction pressure from sensor data). DB load: normal.

**Lesson:** Eviction policies (LRU, LFU) work best when the cache only contains data worth keeping. Write-Around prevents the cache from being populated with write-once/never-read data that would displace valuable hot keys.

---

### 🧠 Mental Model / Analogy

> Write-Around is the "lazy loading" of writes. Write-Through is "eager loading" — every write → cache. Write-Around is lazy — cache only gets data when it's actually NEEDED (on first read). For data that's rarely read: lazy is more efficient. For data that's always read immediately after write: eager is more efficient. The cache is finite; be selective about what enters it.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Write-Around = writes go to DB, not cache; cache is populated only on the next read (cache miss). Prevents cache pollution from write-heavy, rarely-read data (logs, IoT, audit trails).

**Level 2:** Implement with Cache-Aside read path + DELETE-on-write (not SET-on-write). Use Write-Through for entity data frequently read after writes (user profile, product price). Use Write-Around for append-only data, bulk inserts, and rarely-read records.

**Level 3:** Combined: Write-Around for IoT readings + Write-Through for aggregates. When a new aggregate is computed (scheduled), push it to cache (write-through the aggregate, not the raw readings). Result: raw data → DB only (Write-Around); aggregated/summarized data → cache (Write-Through). This is the common pattern in analytics + caching: cache the materialized views / aggregates, not the raw events.

**Level 4:** Write-Around is also the correct strategy when the **write path and read path are decoupled by time**: data is written in bulk (nightly batch job), and read queries hit the DB for analysis (not cache). The cache is only relevant for online queries (real-time user-facing reads), not for batch analytics. In this case: Write-Around for batch writes (direct to DB); Cache-Aside + Write-Through for online API writes; online reads use cache. Write-Around also pairs naturally with **CQRS** (Command Query Responsibility Segregation): the command side (writes) never touches the cache; the query side (reads) uses Cache-Aside to populate read models. Commands write directly to the write model (DB), and the read model cache is refreshed via event consumers (eventual consistency).

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ WRITE-AROUND vs. WRITE-THROUGH                       │
├──────────────────────────────────────────────────────┤
│                                                      │
│ WRITE-THROUGH (sensor reading):                      │
│   App → Redis SET reading:12345 {temp:22.5}          │
│   App → DB INSERT reading (temp:22.5)                │
│   Cache: now has reading:12345 (occupies 1 slot)     │
│   Next read of reading:12345: Cache HIT              │
│   Problem: reading:12345 is NEVER read again         │
│   → Cache slot wasted; hot data evicted              │
│                                                      │
│ WRITE-AROUND (sensor reading):                       │
│   App → DB INSERT reading (temp:22.5)                │
│   Redis: NOT touched                                 │
│   [WRITE-AROUND ← YOU ARE HERE: cache bypassed]      │
│   Cache: unchanged — hot data still there            │
│   Next read of reading:12345: Cache MISS → DB        │
│   (acceptable: individual readings are never read)   │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
IoT TELEMETRY PIPELINE (Write-Around):
Sensor → POST /readings {sensorId: "S42", temp: 22.5, ts: 1234567}
→ SensorDataService.recordReading(...)
→ [WRITE-AROUND ← YOU ARE HERE]
→ DB INSERT INTO readings (...) ← only destination, no cache
→ HTTP 201 Created

Dashboard query (aggregates only):
GET /sensors/S42/hourly-avg?hour=2025-01-15T14
→ Cache CHECK: "sensor-aggregates:S42:2025-01-15T14" → MISS (first request)
→ DB: SELECT AVG(temp) FROM readings WHERE sensor=S42 AND hour=14 → 21.8
→ Redis SET sensor-aggregates:S42:2025-01-15T14 {avg:21.8} EX 3600
→ Response: {avg: 21.8}

Same dashboard query (next 60 minutes):
→ Cache HIT: {avg: 21.8} in 1ms — no DB query ✓

Result:
  100K writes/min: all go to DB only (Write-Around) — zero cache operations
  1K reads/min: aggregates served from cache (populated lazily on first read)
  Cache: clean, contains only aggregates (never polluted by raw readings)
```

---

### ⚖️ Comparison Table

| Strategy      | Cache on Write?                      | Cache on Read?                      | Use Case                                            |
| ------------- | ------------------------------------ | ----------------------------------- | --------------------------------------------------- |
| Write-Through | Yes (SET new value)                  | Cache HIT (populated by write)      | Frequently read after write (user profile, price)   |
| Write-Around  | No (DEL old value only)              | Cache MISS on first read (then HIT) | Rarely-read writes (IoT, logs, audit, bulk inserts) |
| Write-Behind  | Yes (write cache first, flush async) | Cache HIT                           | High write volume + tolerate data loss risk         |
| Cache-Aside   | No (lazy read-populate)              | MISS → DB → populate                | General purpose                                     |

---

### ⚠️ Common Misconceptions

| Misconception                                              | Reality                                                                                                                                                                                                                                                                                 |
| ---------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Write-Around always causes a cache miss on the next read" | Yes, the FIRST read after a Write-Around write is a cache miss. This is acceptable if the data is rarely or never re-read. If the data IS read immediately after writing, Write-Through is more appropriate (avoids the read miss)                                                      |
| "Write-Around means never caching written data"            | Write-Around means not caching at write time. The cache is still populated lazily on the first subsequent read. Once cached, subsequent reads are cache hits — the data IS eventually in the cache                                                                                      |
| "Write-Around and Cache-Aside are the same"                | Cache-Aside describes the read pattern (lazy read-populate). Write-Around describes the write pattern (skip cache on write, just DEL). They overlap but Cache-Aside alone doesn't specify the write behavior — it could use Write-Through (SET on write) or Write-Around (DEL on write) |

---

### 🚨 Failure Modes & Diagnosis

**1. Stale Cache After Update (Write-Around Not Invalidating)**

**Symptom:** User updates their email address. Profile page still shows old email for the next 15 minutes (cache TTL).

**Root Cause:** Write-Around implementation forgot to invalidate the existing cache entry. Only wrote to DB, didn't delete the cached user profile. Correct Write-Around: write to DB + DEL cache entry (the old value must be evicted).

**Fix:**

```java
// Incorrect Write-Around (forgot to evict):
public User updateEmail(String userId, String newEmail) {
    return userRepository.updateEmail(userId, newEmail);
    // PROBLEM: old cached email still in cache for 15min → stale reads
}

// Correct Write-Around (write to DB + evict cache):
@Transactional
public User updateEmail(String userId, String newEmail) {
    User updated = userRepository.updateEmail(userId, newEmail);

    // Evict the old cached entry (don't populate with new value — that's Write-Through)
    redisTemplate.delete("user:" + userId);  // Write-Around eviction

    return updated;  // Next GET user will be a cache miss → DB → fresh data → populate cache
}
```

---

### 🔗 Related Keywords

**Prerequisites:** Cache-Aside, Write-Through, Write-Behind
**Builds On This:** System Design, Caching
**Related:** Write-Through, Write-Behind, Cache-Aside

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT         │ Write to DB, skip cache; populate on read  │
│ CACHE ON WRITE│ NO — only DEL existing cache entry        │
│ CACHE ON READ │ YES — lazily on first read after write    │
│ BEST FOR     │ IoT readings, audit logs, bulk inserts     │
│ AVOID FOR    │ Write-then-immediately-read patterns       │
│ KEY RULE     │ Always DELETE old cache entry on write     │
│ vs WRITE-THRU│ Write-Through: SET new value on write      │
│              │ Write-Around: DEL old value on write       │
│ vs CACHE-ASIDE│ Same read path; WA explicit about writes  │
│ ONE-LINER    │ "Bypass cache on writes — prevent          │
│              │  pollution from rarely-read write data"    │
│ NEXT EXPLORE │ Cache Aside vs RT Comparison → Consistent  │
│              │ Hashing in Cache                           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C — Design Question) Design the cache write strategy for a social media platform with: (a) user profile updates (rare writes, frequent reads — millions of reads per hour for popular users), (b) post creation (high write volume, read by followers within seconds to minutes), (c) analytics events (click, view, hover — 100M events/day, aggregated for dashboards, never individually queried). For each, recommend Write-Through, Write-Around, or Write-Behind and justify.

**Q2.** (TYPE B — Code Review) Review this cache service:

```java
public void saveOrder(Order order) {
    orderRepository.save(order);
    cacheManager.getCache("orders").put("order:" + order.getId(), order);
}
public Optional<Order> getOrder(String id) {
    Cache.ValueWrapper cached = cacheManager.getCache("orders").get("order:" + id);
    if (cached != null) return Optional.of((Order) cached.get());
    Optional<Order> order = orderRepository.findById(id);
    order.ifPresent(o -> cacheManager.getCache("orders").put("order:" + id, o));
    return order;
}
```

(a) What write strategy does this use? (b) What problems could it have? (c) Under what conditions would Write-Around be better here?
