---
layout: default
title: "Thundering Herd (System)"
parent: "System Design"
nav_order: 700
permalink: /system-design/thundering-herd/
number: "700"
category: System Design
difficulty: ★★★
depends_on: "Caching, Load Balancing, Auto Scaling"
used_by: "Rate Limiting (System), Capacity Planning"
tags: #advanced, #distributed, #performance, #reliability, #architecture
---

# 700 — Thundering Herd (System)

`#advanced` `#distributed` `#performance` `#reliability` `#architecture`

⚡ TL;DR — **Thundering Herd** occurs when a large number of processes simultaneously wake up and compete for the same resource (cache expiry, server restart, broadcast wakeup), overwhelming the system and causing cascade failure.

| #700 | Category: System Design | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | Caching, Load Balancing, Auto Scaling | |
| **Used by:** | Rate Limiting (System), Capacity Planning | |

---

### 📘 Textbook Definition

**Thundering Herd** (also called Cache Stampede or Dog-Pile Effect) is a system failure pattern where a sudden surge of concurrent requests simultaneously attempt the same expensive operation after a period of dormancy or a shared invalidation event. Classic triggers: (1) a popular cache key expires — all concurrent readers get a cache miss and simultaneously query the database; (2) a server restarts after being down — all queued clients reconnect simultaneously; (3) a scheduled job broadcasts to millions of sleeping worker processes — all wake up at the same instant. The thundering herd effect causes resource exhaustion (database overload, connection pool saturation, CPU spikes) precisely when the system is most vulnerable (just after a failure or cold start). Prevention strategies: **probabilistic early expiration**, **mutex/lock-based cache recomputation**, **request coalescing**, **jitter on reconnect timers**, and **lazy loading with staggered expiry**.

---

### 🟢 Simple Definition (Easy)

Thundering Herd: everyone rushes through the same door at the same time. A cache key expires at midnight — 10,000 users simultaneously hit the database (all see a cache miss at the same instant). The database can't handle 10,000 simultaneous queries → crashes. The herd thunders through a single bottleneck at once. The fix: stagger the rush, coalesce duplicate requests, or let only one "scout" fetch the data while the rest wait.

---

### 🔵 Simple Definition (Elaborated)

Home page of a popular site cached for 60 seconds. At T=60 exactly, the cache entry expires. 5,000 concurrent users are hitting the home page. All 5,000 simultaneously get a cache miss → all 5,000 fire a database query → database overwhelmed → all 5,000 requests timeout → users see error pages. One user's request would have been fine. Five thousand simultaneous identical requests is the herd. Common variants: cache stampede (expired key), connection stampede (server restart + client reconnects), worker stampede (scheduled cron job waking all workers simultaneously).

---

### 🔩 First Principles Explanation

**Thundering herd variants and fixes:**

```
VARIANT 1: CACHE STAMPEDE (most common)

  Timeline:
  T=0:     Cache key "homepage" set, TTL=60 seconds
  T=60:    Cache key expires
  T=60.001: 5,000 concurrent readers: ALL get "cache miss"
            ALL fire: db.query("SELECT * FROM featured_products LIMIT 20")
  T=60.050: Database: 5,000 simultaneous identical queries
            Connection pool: exhausted (pool size = 100)
            Queue: 4,900 queries waiting
            Queries: each takes 200ms normally → now 30 seconds (resource contention)
  T=90:    Database crashes (OOM, connection limit exceeded)
  
  SOLUTIONS:
  
  A. MUTEX LOCK (Cache Stampede Lock / Cache Miss Coalescing):
  
    When a cache miss occurs, only ONE request fetches from DB.
    Others: wait for the first request to finish and populate cache.
    
    // Java: cache-aside with lock using Redis SETNX (SET if Not eXists):
    public String getHomepage() {
      String cached = redis.get("homepage");
      if (cached != null) return cached;  // cache hit
      
      // Cache miss: try to acquire lock
      boolean acquired = redis.setnx("homepage:lock", "1");
      if (acquired) {
        redis.expire("homepage:lock", 30);  // lock TTL: 30s (safety net)
        try {
          String data = db.query("SELECT ...");
          redis.setex("homepage", 60, data);
          return data;
        } finally {
          redis.del("homepage:lock");  // release lock
        }
      } else {
        // Another process is fetching — wait and retry
        Thread.sleep(50);  // poll interval
        return getHomepage();  // recursive retry (with backoff in prod)
      }
    }
    
    PROBLEM: threads block while waiting.
    BETTER: return stale data while refresh happens ("stale while revalidate").
  
  B. PROBABILISTIC EARLY EXPIRATION (PER):
  
    Before the TTL expires, stochastically recompute the cache.
    Items with high recomputation cost and many readers: expire earlier on average.
    
    // PER algorithm (XFetch by Vattani et al., 2015):
    double expiryTime = cacheSetTime + ttl;
    double currentTime = System.currentTimeMillis() / 1000.0;
    double recomputationTime = 0.1; // 100ms estimated recomputation
    double beta = 1.0; // tuning parameter
    
    boolean shouldRecompute = 
      currentTime - beta * recomputationTime * Math.log(Math.random()) > expiryTime;
    
    // Result: cache is refreshed BEFORE it expires, by a random early amount
    // Earlier refresh probability increases as TTL approaches
    // Only ONE request at a time is in the "early refresh" window → no stampede
  
  C. JITTER (TTL randomisation):
  
    Instead of fixed TTL=60, use: TTL = 60 + random(0, 10)
    Effect: cache keys don't all expire at the same instant
    
    // Different users' requests: 
    //   homepage key (user A's request cached): TTL=63
    //   homepage key (user B's request cached): TTL=67  
    //   All staggered by ±10 seconds
    
    Cache.setex("homepage", 60 + random.nextInt(10), data)
    
    Result: expiration spread over 10 seconds → max 10% of herd per second
    Simplest fix. Doesn't eliminate stampede entirely, just reduces peak.

VARIANT 2: CONNECTION STAMPEDE (server restart)

  Scenario: Service A goes down briefly (deploy/crash).
  Client B: 1,000 connections retry. All use exponential backoff... 
  But they all started failing at the same time → same backoff intervals → 
  all retry at T+1s → server overwhelmed → goes down again → retry cycle
  
  FIX: JITTER in exponential backoff
  
  BAD (synchronised retries — thundering herd):
    retry_delay = min(2^attempt, 60)  // same for all clients
    
  GOOD (desynchronised via jitter):
    // Full jitter:
    retry_delay = random(0, min(2^attempt, 60))
    // Decorrelated jitter (AWS recommended):
    retry_delay = min(max_delay, random(base, prev_delay * 3))
    
  Result: 1,000 clients spread their retries across 0-60 seconds
  Server: 1,000 connections / 60 seconds = ~17 connections/second (manageable)
  vs. 1,000 connections in 1 second (overwhelming)

VARIANT 3: WORKER STAMPEDE (scheduled jobs + message queues)

  Scenario: 1,000 worker processes subscribe to a queue.
  A message "process batch" is broadcast at midnight.
  All 1,000 workers: wake up simultaneously → all try to acquire database connection.
  
  FIX: MESSAGE VISIBILITY / COMPETING CONSUMERS (SQS design):
    SQS: each message visible to ONE consumer at a time.
    Consumer processes: compete for messages → natural rate limiting.
    1,000 workers: each picks up one message → 1,000 messages processed in parallel
    (Not simultaneously on the same resource — each gets a different message)
    
  FIX: DISTRIBUTED RATE LIMITING (see Rate Limiting keyword)
    Token bucket: workers draw tokens before processing
    Rate: 100 db operations/second maximum
    Workers: limited to 100 concurrent ops regardless of how many wake up
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT Thundering Herd protection:
- Cache expiry → database overload → cascade failure at predictable intervals
- Server restarts → connection storm → immediate second outage
- Scheduled jobs → synchronised resource contention → job delays / failures

WITH Thundering Herd protection:
→ Cache miss: only one request hits database; others wait or get stale data
→ Server restart: clients reconnect gradually (jittered backoff)
→ Scheduled workloads: distributed queue processing prevents simultaneous spikes

---

### 🧠 Mental Model / Analogy

> A popular bakery (cache) runs out of fresh bread (cache expiry). 500 customers simultaneously ask the baker to bake more bread (database queries). The bakery has one oven (one DB connection). Instead of 500 people shouting "bake me bread!" simultaneously, the fix is: one person asks (mutex), the baker bakes one batch, and the bread is shared among all 500 when ready (cache repopulation). The other 499 wait patiently (or eat the slightly old bread from yesterday — stale-while-revalidate).

"Bakery running out of fresh bread" = cache expiry (cache miss event)
"500 customers simultaneously asking" = thundering herd (all readers query DB at once)
"One person asks, shares result" = mutex lock (one request recomputes, others use result)
"Eating yesterday's bread" = stale-while-revalidate (serve stale while cache refreshes)

---

### ⚙️ How It Works (Mechanism)

**Redis: cache stampede prevention with SET NX + stale-while-revalidate:**

```python
import redis
import time
import threading

r = redis.Redis(host='redis', port=6379)

CACHE_TTL = 60          # 60 seconds cache TTL
LOCK_TTL = 30           # 30 seconds max lock hold time
STALE_EXTENSION = 30    # extend stale data by 30 seconds while refreshing

def get_homepage():
    # Check cache:
    cached = r.get("homepage:data")
    if cached:
        return cached  # cache hit: fast path
    
    # Cache miss: try to acquire lock for refresh
    lock_acquired = r.set("homepage:lock", "1", nx=True, ex=LOCK_TTL)
    
    if lock_acquired:
        # This request recomputes the cache
        try:
            # Optionally: extend stale data TTL so other requests
            # can serve stale while this one recomputes:
            # (stale-while-revalidate pattern)
            data = expensive_db_query()
            r.setex("homepage:data", CACHE_TTL, data)
            return data
        finally:
            r.delete("homepage:lock")
    else:
        # Another request holds the lock: wait and retry
        # OR: serve stale data if available with extended TTL
        stale = r.get("homepage:data:stale")
        if stale:
            return stale  # serve stale immediately (no wait)
        
        # No stale data: wait with brief backoff
        time.sleep(0.1)
        return get_homepage()  # retry (add max retry limit in prod)

def expensive_db_query():
    # Save a stale copy before overwriting:
    existing = r.get("homepage:data")
    if existing:
        r.setex("homepage:data:stale", STALE_EXTENSION, existing)
    
    # Simulate expensive query:
    time.sleep(0.2)
    return f"<html>Homepage content at {time.time()}</html>"
```

---

### 🔄 How It Connects (Mini-Map)

```
Cache (expired key)    Server Restart    Scheduled Jobs
(cache miss trigger)   (reconnect storm) (broadcast wakeup)
        │                    │                  │
        └────────────────────┴──────────────────┘
                             ▼
                    Thundering Herd ◄──── (you are here)
                    (simultaneous resource contention)
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
            Rate Limiting        Capacity Planning
            (throttle herd)      (size for herd peaks)
```

---

### 💻 Code Example

**Spring Boot + Caffeine cache: probabilistic early expiration:**

```java
@Configuration
public class CacheConfig {
    @Bean
    public CacheManager cacheManager() {
        CaffeineCacheManager manager = new CaffeineCacheManager();
        manager.setCaffeine(Caffeine.newBuilder()
            // Refresh after write (not expire after write):
            // Key difference: refreshAfterWrite does NOT remove the key on expiry.
            // Old value: served to ALL readers until new value is ready.
            // Only ONE background thread: recomputes the value.
            // Zero thundering herd: readers never block!
            .refreshAfterWrite(55, TimeUnit.SECONDS)  // start refresh at 55s (before 60s TTL)
            .expireAfterWrite(60, TimeUnit.SECONDS)    // absolute max TTL
            .maximumSize(1000)
        );
        return manager;
    }
}

@Service
public class HomepageService {
    @Cacheable(value = "homepage", key = "'featured'")
    public List<Product> getFeaturedProducts() {
        // Caffeine with refreshAfterWrite:
        // - First call: compute and cache
        // - Subsequent calls while cache valid: return cached
        // - After 55s: NEXT READ triggers async background refresh
        //   (old value returned immediately, background thread refreshes)
        // - After 60s: stale value still returned until refresh completes
        // - No stampede: only ONE background refresh thread ever runs
        return productRepository.findFeatured();
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Thundering herd only affects caches | It affects any shared resource with synchronized wake-up: connection pools (reconnection storms), database connection limits (multiple services restart simultaneously), message queues (broadcast wakeup of consumers), DNS TTL expiry (all clients refresh simultaneously). Any pattern of synchronised dormancy → simultaneous activation is a thundering herd |
| Adding more cache servers eliminates thundering herd | More cache nodes reduce single-node load but don't eliminate the herd. If 10,000 clients simultaneously miss the same key, distributing those 10,000 simultaneous DB queries across 10 nodes still overwhelms the database (1,000 queries per node simultaneously). The fix is coalescing or jitter, not scaling |
| Thundering herd is rare and not worth planning for | Cache expiry is routine. Scheduled jobs are routine. Server restarts (deployments) are routine. Any system with multiple cache entries and concurrent users will experience mini-herds on every cache miss. The scale of impact determines whether it's noticeable. Planning for it prevents production incidents |
| Increasing cache TTL eliminates thundering herd | Longer TTL: stampede happens less frequently but at higher magnitude (more stale reads accumulated → larger surge when expiry hits). The fundamental problem (synchronised expiry) is unchanged; only the frequency shifts |

---

### 🔥 Pitfalls in Production

**Deployment causes thundering herd via application restart:**

```
PROBLEM: Rolling restart causes cache stampede

  Scenario: 
    20 app servers serving 50,000 requests/minute.
    Each server: warm in-memory Caffeine cache (1,000 cached items).
    Rolling deploy: restart servers one by one (5 minutes each).
    
  At T=0: server 1 restarted → cold cache.
    All requests to server 1: cache miss → DB query
    DB load: +5% (server 1 is 1/20 = 5% of fleet)
    Acceptable.
    
  At T=5: server 2 restarted → cold cache.
    +5% DB load. Still OK.
    
  At T=15: 4 servers cold → 20% more DB queries.
    DB: starting to strain.
    
  At T=60: all 20 servers restarted (but they take 5 min each to warm up):
    At peak: 10 servers are cold (50% of fleet).
    DB load: +50% from cold cache misses.
    DB: throughput limit hit → queries slow down → request timeouts.
    
  Cold cache + rolling deploy = self-inflicted thundering herd.

FIX 1: Cache warm-up before serving traffic
  Deployment script:
    1. Start new server instance
    2. Execute warm-up script: pre-populate 100 most common cache keys from DB
    3. ONLY THEN: add to load balancer pool
    
    # warm-up script example:
    # curl http://localhost:8080/internal/cache-warmup
    # → endpoint: loads top-100 products, top-10 categories, home page data into cache
    
FIX 2: External shared cache (Redis)
  If cache is in Redis (not in-process Caffeine):
  Server restart: connects to Redis → all cache entries still there.
  No cold cache on restart → no thundering herd.
  
  Trade-off: in-process cache is faster (0.01ms vs 1ms Redis roundtrip)
  For stampede prevention: Redis cache is far superior.

FIX 3: Stagger deployments with longer bake time per instance
  Deploy 1 server, wait 10 minutes (warm-up time), then next server.
  Slower deployment (100 servers × 10 min = 16 hours!) but no stampede.
  Better: combine with cache warm-up (Fix 1) to reduce bake time to 1 minute.
```

---

### 🔗 Related Keywords

- `Caching` — cache expiry is the most common thundering herd trigger
- `Rate Limiting (System)` — token bucket / leaky bucket can throttle the herd
- `Capacity Planning` — size infrastructure for thundering herd peaks, not averages
- `Auto Scaling` — scaling events themselves can trigger thundering herds (cold start)
- `Exponential Backoff with Jitter` — prevents connection stampede after server restart

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Simultaneous resource contention from     │
│              │ synchronized wake-up or cache expiry      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Designing cache expiry strategy; retry    │
│              │ logic; scheduled job architectures        │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ N/A — always design to PREVENT thundering │
│              │ herd, not tolerate it                     │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Bakery runs out of bread — 500 customers │
│              │  all shout at the baker at once."         │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Cache Stampede → Jitter/Backoff           │
│              │ → Rate Limiting                           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** You have a news website with 1 million daily active users. The homepage is cached for 5 minutes (TTL=300s). At 9 AM every weekday (peak time), there is a sudden surge of 50,000 concurrent users. Calculate: at any given 9 AM peak, what is the approximate number of simultaneous cache misses when the homepage cache expires? How many database queries per second does this generate (assume miss takes 200ms)? Design a complete anti-stampede strategy using at least 2 complementary techniques.

**Q2.** A microservices system has Service A calling Service B via HTTP. Service B goes down for 30 seconds (deploy). Service A has 500 instances, each with an HTTP client using exponential backoff: `delay = 2^attempt seconds`. Service B recovers at T=30s. Describe exactly what happens to Service B's load at T=30s, T=31s, T=32s, etc. with pure exponential backoff vs. exponential backoff with full jitter (each instance independently randomises). Calculate the approximate connection rate per second for both approaches during the first 10 seconds after B recovers.
