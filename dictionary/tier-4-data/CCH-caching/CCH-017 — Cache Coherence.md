---
layout: default
title: "Cache Coherence"
parent: "Caching"
grand_parent: "Technical Dictionary"
nav_order: 17
permalink: /caching/cache-coherence/
id: CCH-017
category: Caching
difficulty: ★★★
depends_on: Distributed Cache, Cache Invalidation, Multi-Level Cache
used_by: System Design, Distributed Systems, Caching
related: Distributed Cache, Multi-Level Cache, Cache Invalidation
tags:
  - caching
  - cache-coherence
  - mesi
  - invalidation
  - deep-dive
---

# CCH-017 — Cache Coherence

⚡ TL;DR — Cache coherence is the guarantee that **all caches in a system observe the same value for a shared memory location at any point in time**; in software, it means all instances of a distributed application see the same cached data; violations cause "split-brain cache" bugs where different users get different answers from the same API depending on which instance handles their request.

| #487            | Category: Caching                                        | Difficulty: ★★★ |
| :-------------- | :------------------------------------------------------- | :-------------- |
| **Depends on:** | Distributed Cache, Cache Invalidation, Multi-Level Cache |                 |
| **Used by:**    | System Design, Distributed Systems, Caching              |                 |
| **Related:**    | Distributed Cache, Multi-Level Cache, Cache Invalidation |                 |

---

### 🔥 The Problem This Solves

**PER-INSTANCE LOCAL CACHE DIVERGENCE:**
20 instances of a service each have a local Caffeine cache (L1). Instance A handles a "update product price" request, evicts the local cache. Instances B through T still have the old price. Users load-balanced to Instances B-T see stale prices. This is a **cache coherence violation** — multiple cache instances (one per application instance) disagree on the current value.

**CPU-LEVEL AND DISTRIBUTED CACHE COHERENCE ARE PARALLEL PROBLEMS:**
CPUs with L1/L2 caches per core have the same problem: Core 1 modifies a variable → its L1 cache has new value → Core 2's L1 cache still has old value. The CPU **cache coherence protocol** (MESI) handles this automatically. In distributed software systems, engineers must implement the equivalent manually: broadcast invalidations via pub/sub, use a shared L2 Redis cache, or use Redis keyspace notifications.

---

### 📘 Textbook Definition

**Cache Coherence** is the property of a system with multiple caches where any read of a shared data item returns the **most recently written value** of that item. Formally: if Process P1 writes value X to location A, then Process P2 reads location A after P1's write completes, P2 should observe X (not a stale value). In computer architecture: **MESI Protocol** (Modified, Exclusive, Shared, Invalid) is the canonical hardware cache coherence protocol: each CPU cache line is tagged with its state (M: only this core has it, modified; E: only this core has it, clean; S: shared across cores, consistent; I: invalid, must be fetched from memory or other cache). A write to a Shared cache line: all other cores' copies transition to Invalid (write-invalidate). In distributed software: equivalents of MESI are pub/sub broadcast invalidation (write-invalidate), versioned cache entries (write-update), and Redis keyspace notifications (event-driven invalidation). **Local + Distributed Cache (L1+L2)**: the hardest coherence problem: Instance A updates L2 (Redis), but doesn't know which instances have the key in their L1 (local Caffeine) — it must broadcast an invalidation to all instances for them to evict their local copy.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Cache coherence = guarantee that all caches return the same value; violated when per-instance local caches diverge after a write.

**One analogy:**

> A household with a whiteboard in every room (local cache). Everyone can write on their room's whiteboard. When the grocery list changes: if only the kitchen whiteboard is updated, the family member checking the bedroom whiteboard sees the old list. Cache coherence = a rule that when the kitchen whiteboard changes, a broadcast goes to all rooms: "erase your whiteboard" (invalidate) or "update your whiteboard" (write-update). Without the rule: different family members act on different information = inconsistency.

- "Whiteboard in each room" → Caffeine cache in each application instance
- "Kitchen updates grocery list" → one instance receives write request
- "Other rooms see old list" → other instances serve stale cache
- "Broadcast: erase your whiteboard" → pub/sub invalidation to all instances
- "Consistent whiteboards across all rooms" → cache coherence

**One insight:**
For L1 (Caffeine) + L2 (Redis) multi-level caches, full cache coherence requires **two-layer invalidation**: (1) DEL the Redis key (L2 invalidation), AND (2) publish an invalidation message (Redis pub/sub) so all instances evict their local Caffeine copy. If you only do step 1: all instances still serve stale data from L1 until their TTL expires. The local TTL becomes the "coherence window" — the duration during which different instances may return different values.

---

### 🔩 First Principles Explanation

**MESI PROTOCOL (CPU CACHE COHERENCE):**

```
CPU Core 1 (L1 Cache) ←→ Core 2 (L1 Cache) ←→ Core 3 (L1 Cache)
         ↕                      ↕                      ↕
                     Shared L2/L3 Cache / RAM

MESI States for each cache line:
  M (Modified):  This core has the ONLY copy, and it's modified (dirty)
                 Other cores: state = I (Invalid)
  E (Exclusive): This core has the ONLY copy, and it's clean
                 Other cores: state = I (Invalid)
  S (Shared):    Multiple cores have a clean copy
                 All caches: state = S
  I (Invalid):   This cache line is stale/empty — must fetch before use

Write to a SHARED cache line (Core 1 writes):
  1. Core 1 broadcasts "I'm writing to address 0x1234" (bus invalidation)
  2. Core 2 and Core 3: receive invalidation → set their cache line to I
  3. Core 1: cache line state: M (Modified, dirty, only copy)
  4. Core 2 reads 0x1234: state is I → fetches from memory (or Core 1's cache)
  → All cores agree on the latest value after the read

Software equivalent:
  MESI state = Redis SET + local Caffeine state
  Write-invalidate = Redis DEL + pub/sub broadcast to Caffeine caches
  M state = only one instance has value (not applicable in distributed)
  I state = cache miss (key deleted) → fetch from DB
  S state = multiple instances have same value (all cached consistently)
```

**L1+L2 COHERENCE WITH PUB/SUB:**

```java
// Multi-level cache with coherence: L1 Caffeine + L2 Redis
// When a write happens: invalidate BOTH levels across ALL instances

@Component
public class CoherentCacheService {

    private final Cache<String, Object> localCache;  // L1: Caffeine, per-instance
    private final RedisTemplate<String, Object> redis;  // L2: shared Redis
    private final RedisMessageListenerContainer listenerContainer;

    private static final String INVALIDATION_CHANNEL = "cache:invalidations";

    @PostConstruct
    public void startListening() {
        // Subscribe to invalidation messages from other instances
        listenerContainer.addMessageListener(
            (message, pattern) -> {
                String key = new String(message.getBody());
                localCache.invalidate(key);  // Evict from L1 on this instance
                log.debug("L1 invalidated by remote notification: {}", key);
            },
            new ChannelTopic(INVALIDATION_CHANNEL)
        );
    }

    public Object get(String key) {
        // 1. Check L1 (local, fast)
        Object l1Value = localCache.getIfPresent(key);
        if (l1Value != null) {
            return l1Value;  // L1 hit: ~0.01ms
        }

        // 2. Check L2 (shared Redis)
        Object l2Value = redis.opsForValue().get(key);
        if (l2Value != null) {
            localCache.put(key, l2Value);  // Promote to L1
            return l2Value;  // L2 hit: ~1ms
        }

        return null;  // Miss: caller queries DB
    }

    public void put(String key, Object value, Duration ttl) {
        // Write to L2 first (shared, all instances see it)
        redis.opsForValue().set(key, value, ttl);

        // Update L1 on this instance
        localCache.put(key, value);

        // Broadcast invalidation so OTHER instances evict their L1
        // (This instance's L1 was just set to the new value above)
        redis.convertAndSend(INVALIDATION_CHANNEL, key);
        // Other instances: receive message → localCache.invalidate(key)
        // Their next read: L1 miss → L2 hit (new value from Redis) → promote to L1
    }

    public void invalidate(String key) {
        // Step 1: Delete from L2 (shared Redis)
        redis.delete(key);

        // Step 2: Evict from L1 on THIS instance
        localCache.invalidate(key);

        // Step 3: Broadcast to all OTHER instances to evict their L1
        redis.convertAndSend(INVALIDATION_CHANNEL, key);

        // [COHERENCE ← YOU ARE HERE: all instances' L1 now evicted]
        // All instances: next read → L1 miss → L2 miss → DB query
        // All instances see fresh data after DB fetch ✓
    }
}
```

**REDIS KEYSPACE NOTIFICATIONS (PASSIVE COHERENCE):**

```java
// Alternative: instead of app-level pub/sub, use Redis keyspace notifications
// Redis automatically publishes events when keys are modified/deleted

// redis.conf:
// notify-keyspace-events "KEA"
//   K = keyspace events, E = keyevent events, A = all commands

@Component
public class KeyspaceNotificationListener {

    private final Cache<String, Object> localCache;

    @PostConstruct
    public void subscribeToKeyspaceEvents() {
        // Subscribe to: __keyevent@0__:del (all DEL commands on DB 0)
        // and: __keyevent@0__:expired (all key expirations)
        listenerContainer.addMessageListener(
            (message, pattern) -> {
                String key = new String(message.getBody());
                localCache.invalidate(key);  // Key was deleted/expired in Redis → evict local
            },
            new PatternTopic("__keyevent@0__:del")
        );
        listenerContainer.addMessageListener(
            (message, pattern) -> {
                String key = new String(message.getBody());
                localCache.invalidate(key);
            },
            new PatternTopic("__keyevent@0__:expired")
        );
    }
}
// Benefit: no need to add invalidation calls in service code
// Drawback: adds overhead to Redis (publishing events for every key operation)
// and: notifications are "at most once" (not guaranteed delivery)
// → If a notification is missed: L1 cache is stale (incoherent) until TTL
// → Use short L1 TTL as safety net (30-60 seconds max)
```

---

### 🧪 Thought Experiment

**COHERENCE WINDOW: How Long Can Caches Disagree?**

Setup: 10 instances, L1 Caffeine TTL = 5 minutes, L2 Redis TTL = 30 minutes. No pub/sub invalidation.

Write event at T=0: Instance 1 evicts L1 and L2 after DB write. Instances 2-10 still have old value in L1 (Caffeine).

**Coherence window = 5 minutes** (the L1 TTL). For 5 minutes, Instances 2-10 serve stale data. After 5 minutes: their L1 entries expire. They hit L2 Redis: but L2 was evicted too! They hit the DB (fresh data) and repopulate L1 and L2 with the new value. From T=5min: all instances are coherent again.

**With pub/sub invalidation:** Coherence window = pub/sub latency (~1-5ms). All instances evict L1 almost instantly after the write.

**Practical decision:** Is 5 minutes of inconsistency acceptable? For product prices: no. For article view counts: yes. The coherence window is a business decision, not a technical one.

---

### 🧠 Mental Model / Analogy

> Cache coherence in a multi-core CPU is solved by hardware (MESI protocol — automatic write-invalidate). In distributed software systems, there's no automatic protocol — **you are the MESI protocol**. When you write data and update the cache, you must broadcast "invalidate" to all other caches (pub/sub). When you read data with a stale cache, you must "fetch from memory" (DB query). The MESI protocol is deterministic and instantaneous (bus transactions). Pub/sub is asynchronous and best-effort. This is why the **coherence window in distributed systems is non-zero** — a brief period exists where some caches have stale data.

---

### 📶 Gradual Depth — Four Levels

**Level 1:** Cache coherence = all caches return the same value. Violated by per-instance local caches (L1 Caffeine) in multi-instance deployments. Solution: shared distributed cache (Redis) or pub/sub L1 invalidation.

**Level 2:** For L1+L2 cache: on write → DEL from Redis (L2) + publish invalidation on Redis pub/sub channel → all instances receive message → invalidate local Caffeine cache (L1). Short L1 TTL (30-60s) as safety net in case pub/sub message is lost.

**Level 3:** Write-invalidate (broadcast DEL) vs. write-update (broadcast new value): write-invalidate is simpler and safer (next read fetches fresh from DB). Write-update is faster (no subsequent DB miss) but risks broadcast failures leaving some caches with wrong update. Redis keyspace notifications as passive alternative: subscribe to `__keyevent@0__:del` and `__keyevent@0__:expired` — no manual invalidation calls needed in service code, but "at most once" delivery means occasional incoherence.

**Level 4:** The fundamental tradeoff: coherence ↔ latency. A fully coherent system requires synchronous communication (all caches updated before write returns) — distributed consensus is O(network RTT per node). A system with a coherence window allows asynchronous invalidation (pub/sub, TTL expiry) — eventual coherence with bounded staleness. For most web applications, the coherence window can be 1-30 seconds (bounded staleness) without user-visible impact. For financial data (balances, prices): coherence window must be < 1 second; use Redis as the single source of truth for caching (no local L1 caches for these keys, or L1 TTL of 1 second max). The MESI protocol in CPUs achieves coherence in < 100ns because it's hardwired. Software pub/sub achieves coherence in 1-5ms under normal conditions, 100-500ms under high load. Plan your L1 TTL based on the worst-case pub/sub latency under your load profile.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────────┐
│ L1+L2 CACHE COHERENCE VIA PUB/SUB                       │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  App Instance 1        App Instance 2    App Instance 3  │
│  L1: product:42=9.99   L1: product:42=9.99  L1: same    │
│         ↓ WRITE                                          │
│  DB: UPDATE price=29.99                                  │
│  Redis DEL product:42  (L2 invalidated)                  │
│  Redis PUBLISH cache:invalidations "product:42"          │
│         ↓                                                │
│  L1: invalidate        [COHERENCE ← YOU ARE HERE]        │
│  product:42            L1: invalidate    L1: invalidate  │
│                        product:42        product:42       │
│                                                          │
│  Next GET product:42 on any instance:                    │
│  L1 miss → L2 miss → DB: 29.99 → repopulate L1+L2       │
│  All instances: product:42 = 29.99 ✓ (coherent)         │
└──────────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
PRICE UPDATE: PUT /products/42 {price: 29.99}
→ Hits Instance 5 (of 20)
→ DB UPDATE (ACID commit) ✓
→ afterCommit:
   Redis DEL product:42                (L2 invalidated)
   Redis PUBLISH "cache:invalidations" "product:42"

All 20 instances listening on "cache:invalidations":
   Receive: "product:42"
   Caffeine.invalidate("product:42")   (L1 evicted on all instances)

Window: ~1-5ms pub/sub latency
[COHERENCE ← YOU ARE HERE: within 5ms all L1 caches evicted]

User requests GET /products/42 → any instance:
   L1: MISS (evicted) → L2: MISS (deleted) → DB: 29.99 → cache both → return 29.99

Within 100ms: all instances serving 29.99 from refreshed L1+L2 caches ✓
```

---

### ⚖️ Comparison Table

| Approach                        | Coherence Window            | Complexity    | Failure Modes                   |
| ------------------------------- | --------------------------- | ------------- | ------------------------------- |
| Only shared Redis (no L1)       | ~0ms (all reads hit shared) | Low           | Redis outage affects all        |
| L1 (short TTL, no invalidation) | = L1 TTL (30-300s)          | Low           | Stale during TTL window         |
| L1 + pub/sub invalidation       | ~1-5ms (pub/sub latency)    | Medium        | Lost pub/sub message = stale L1 |
| L1 + keyspace notifications     | ~1-5ms                      | Low (passive) | At-most-once delivery           |
| Write-update broadcast          | ~1-5ms                      | High          | Stale update if broadcast fails |

---

### ⚠️ Common Misconceptions

| Misconception                                 | Reality                                                                                                                                                                                                                |
| --------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Using Redis means no coherence problems"     | Redis is a distributed cache but is still a single shared storage — coherence issues arise from LOCAL caches (L1 Caffeine per-instance) sitting in front of Redis. Redis itself is coherent if only L2 (Redis) is used |
| "Short TTL is sufficient for cache coherence" | Short TTL bounds the coherence window but doesn't eliminate it. A 5-second TTL means up to 5 seconds of incoherence — acceptable for some use cases, not for others                                                    |
| "Redis pub/sub guarantees delivery"           | Redis pub/sub is fire-and-forget: if a subscriber misses a message (network glitch, restarting), it does NOT receive replayed messages. Always pair pub/sub invalidation with a safety-net short TTL                   |

---

### 🚨 Failure Modes & Diagnosis

**1. L1 Cache Serving Stale Price After Price Update**

**Symptom:** PUT /products/42 returns 200 (price updated to $29.99). GET /products/42 on some instances returns $9.99 (old price). Inconsistency observed within seconds of the update.

**Root Cause:** L1 (Caffeine) per-instance cache has `expireAfterWrite = 5 minutes`. Price update evicts Redis (L2) and local L1 on Instance 5 (the writer). Instances 1-4, 6-20 still have old price in L1.

**Diagnosis:**

```bash
# Check Redis: should be deleted/updated
redis-cli GET product:42
# If returns null: L2 was correctly invalidated; issue is L1 Caffeine

# Check if pub/sub is configured:
redis-cli SUBSCRIBE cache:invalidations
# Try updating a product — should see message here
# If no message: invalidation broadcast not implemented

# Spring Boot: check cache stats
# GET /actuator/caches (Spring Boot Actuator)
# Look for hit rate on products cache — if very high, L1 hits are dominating
```

**Fix:** Implement pub/sub invalidation as shown above OR reduce L1 TTL to 30 seconds for price-sensitive data.

---

### 🔗 Related Keywords

**Prerequisites:** Distributed Cache, Cache Invalidation, Multi-Level Cache
**Builds On This:** System Design, Distributed Systems
**Related:** Distributed Cache, Multi-Level Cache, Cache Invalidation

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT         │ All caches return same value for same key │
│ VIOLATED BY  │ Per-instance L1 caches in multi-instance  │
│ MESI         │ CPU coherence: M/E/S/I states per line    │
│ SW SOLUTION  │ Shared Redis (no L1) OR pub/sub L1 evict  │
│ COHERENCE    │ Window = pub/sub latency (~1-5ms)          │
│ WINDOW       │ Without pub/sub: = L1 TTL (can be minutes)│
│ SAFETY NET   │ Short L1 TTL (30-60s) for missed messages  │
│ PUB/SUB      │ "at most once" — not guaranteed delivery   │
│ ONE-LINER    │ "Multi-level caches diverge after writes  │
│              │  → broadcast invalidations via pub/sub"    │
│ NEXT EXPLORE │ Multi-Level Cache → Cache Warming          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** (TYPE C — Design Question) Design a cache coherence strategy for a financial application where account balances must NEVER be stale beyond 1 second across 50 instances. You have L1 (Caffeine) and L2 (Redis). Redis pub/sub delivers in ~2ms under normal load, ~200ms under peak load. How do you guarantee the 1-second coherence SLA? What is your degradation strategy when Redis pub/sub is overwhelmed?

**Q2.** (TYPE A — MESI Deep Dive) Explain what happens at the CPU level when two threads on different cores simultaneously try to write to the same variable (causing a cache coherence race). Trace through the MESI protocol states for both cores' cache lines. What is the hardware guarantee that prevents both writes from succeeding simultaneously? How does this compare to the lack of such guarantees in distributed software caches?
