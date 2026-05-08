---
layout: default
title: "Eviction Policies (LRU, LFU, FIFO)"
parent: "Caching"
grand_parent: "Technical Dictionary"
nav_order: 12
permalink: /caching/eviction-policies/
id: CCH-012
category: Caching
difficulty: ★★☆
depends_on: TTL, Caching, Redis Data Structures
used_by: Caching, System Design, Redis
related: TTL, Cache Invalidation, Redis Data Structures
tags:
  - caching
  - eviction
  - lru
  - lfu
  - redis
---

# CCH-012 - Eviction Policies (LRU, LFU, FIFO)

⚡ TL;DR - When a cache's memory is full, the eviction policy decides which entries to remove to make room for new ones; **LRU** (Least Recently Used) removes the entry not accessed for the longest time; **LFU** (Least Frequently Used) removes the entry accessed the least times; **FIFO** removes the oldest-inserted entry; Redis supports all three plus variants - choosing the right policy determines whether your cache holds hot data or cold data under memory pressure.

| #482            | Category: Caching                              | Difficulty: ★★☆ |
| :-------------- | :--------------------------------------------- | :-------------- |
| **Depends on:** | TTL, Caching, Redis Data Structures            |                 |
| **Used by:**    | Caching, System Design, Redis                  |                 |
| **Related:**    | TTL, Cache Invalidation, Redis Data Structures |                 |

---

### 🔥 The Problem This Solves

**CACHE MEMORY IS FINITE:**
A Redis cache with `maxmemory 4gb` can hold roughly 4GB of data. A busy application with millions of unique cache keys will exceed this limit. Without an eviction policy, Redis refuses new writes when memory is full - causing application errors. With an eviction policy, Redis automatically removes entries to make room for new data, choosing which entries to evict based on the policy.

**WRONG EVICTION = CACHE SERVES COLD DATA:**
If the policy evicts hot (frequently accessed) data to make room for cold (rarely accessed) data, every request for hot data misses the cache and hits the database. A good eviction policy keeps frequently accessed data in memory and evicts the data least likely to be needed again.

---

### 📘 Textbook Definition

**Cache eviction** is the process of removing entries from a cache when the cache reaches its capacity limit (`maxmemory` in Redis). **Eviction policies** determine which entries to remove: **LRU (Least Recently Used)**: evicts the entry that has not been accessed for the longest time. Assumes temporal locality - recently accessed data is likely to be accessed again. **LFU (Least Frequently Used)**: evicts the entry accessed the fewest total times. Better than LRU for workloads with long-lived hot keys (LRU might evict a hot key just because it wasn't accessed in the last few minutes). **FIFO (First In, First Out)**: evicts the oldest-inserted entry regardless of access frequency or recency - simple but ignores access patterns. **Random**: evicts a random entry - simple, low overhead, surprisingly competitive with LRU for uniform access distributions. Redis `maxmemory-policy` options: `noeviction` (refuse writes when full), `allkeys-lru`, `volatile-lru` (only evict keys with TTL), `allkeys-lfu`, `volatile-lfu`, `allkeys-random`, `volatile-random`, `volatile-ttl` (evict keys with shortest TTL first). Caffeine (Java) uses **Window TinyLFU** - a variant of LFU with a small protected "admission window" for recently seen keys - superior to pure LRU and LFU for most real workloads.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
When cache is full, eviction policy picks which entry to remove - LRU removes oldest-access, LFU removes least-accessed, FIFO removes oldest-insert.

**One analogy:**

> A limited bookshelf (cache). When full and you add a new book: LRU - remove the book you haven't picked up for the longest time (been sitting untouched). LFU - remove the book you've read the fewest times overall. FIFO - remove the book you bought first. A person who reads some books daily (hot) and some once a year (cold): LFU correctly keeps daily books; LRU might accidentally evict a daily book during a slow weekend; FIFO evicts arbitrarily.

**One insight:**
LRU is not always optimal. A database scanning use case (sequential full-table scans) will "pollute" an LRU cache: every scanned page is inserted (becoming "most recently used") and evicts actually-hot pages that were being served to real user queries. This is "cache pollution." LFU handles this better: scanned pages (accessed once) have low frequency and are evicted before high-frequency pages. Caffeine's Window TinyLFU is specifically designed to resist scan pollution.

---

### 🔩 First Principles Explanation

**REDIS EVICTION POLICY CONFIGURATION:**

```bash
# redis.conf
maxmemory 4gb
maxmemory-policy allkeys-lfu  # evict least-frequently-used from all keys

# Policy options and when to use each:
# noeviction      → refuse writes when full; use when data loss is unacceptable
# allkeys-lru     → general caching (temporal locality assumption)
# volatile-lru    → evict only TTL-having keys by LRU (preserve TTL-free critical data)
# allkeys-lfu     → better for workloads with stable hot keys (e.g., product catalog)
# volatile-lfu    → LFU but only TTL-having keys
# allkeys-random  → when all data equally likely to be accessed
# volatile-random → when TTL-having data is disposable
# volatile-ttl    → evict keys closest to TTL expiry first (most about to expire anyway)

# Check current eviction stats:
redis-cli INFO stats | grep evicted
# evicted_keys: number of keys evicted since server start

# Real-time eviction rate:
redis-cli --stat  # shows evicted keys per second in continuous output
```

**LRU IMPLEMENTATION (CONCEPTUAL):**

```
LRU Cache (pseudocode using doubly-linked list + hashmap):

Data structure:
  HashMap: key → (value, node) for O(1) lookup
  Doubly-linked list: MRU end ←→ ... ←→ LRU end

GET(key):
  node = hashmap[key]
  if not found: return MISS
  Move node to MRU end of list (just accessed → most recent)
  return node.value

SET(key, value):
  if key in hashmap:
    Update value, move to MRU end
  else:
    Create node at MRU end
    hashmap[key] = node
    if len(hashmap) > capacity:
      evict_node = list.tail (LRU end)
      list.remove(evict_node)
      del hashmap[evict_node.key]

Redis LRU approximation:
  Redis does NOT maintain a full doubly-linked list (too expensive for millions of keys)
  Instead: Redis samples `maxmemory-samples` (default 5) random keys when eviction needed
  Evicts the sampled key with the oldest access time
  This is an APPROXIMATION of LRU (not exact) but much cheaper: O(samples) not O(N)
  Increasing maxmemory-samples=10 improves accuracy at cost of slightly higher CPU
```

**LFU IN REDIS (APPROXIMATION):**

```
Redis LFU implementation:
  Each key stores an access counter (8-bit Morris counter - logarithmic approximation)
  Maximum raw count: 255 (represents ~1 million accesses)
  Counter decays over time: lfu-decay-time=1 (halve count every 1 minute)

  This means LFU is "recent frequency" not pure frequency:
  - A key with 1000 accesses 30 minutes ago has lower effective freq than
  - A key with 10 accesses in the last 1 minute
  - Avoids LFU stale-frequency problem (old popular keys never evicted)

  Tune LFU:
  lfu-log-factor=10    # how fast counter grows (10 = logarithmic, 100 = very slow)
  lfu-decay-time=1     # minutes between counter halving (1 = decay rapidly)

  Check key frequency score:
  redis-cli OBJECT FREQ product:42  # returns current LFU approximation counter
```

**CAFFEINE WINDOW TINYLFU (BEST OVERALL EVICTION):**

```
Window TinyLFU algorithm:
  Admission window (1% of cache): LRU, new entries go here
  Protected segment (80% of cache): entries promoted here after passing admission
  Probation segment (20% of cache): recently evicted from protected, given another chance

  Admission filter: Bloom-filter-based frequency sketch
  New entry competes with a random victim: admitted only if higher frequency

  Benefits:
  - Resistant to scan pollution (scan entries have low frequency → not admitted)
  - Handles Zipfian distributions better than pure LRU/LFU
  - Self-tuning based on hit rate

  In practice: Caffeine achieves 10-40% better hit rate than Redis LRU for typical workloads
  When to use Caffeine: in-process JVM cache; single application instance
  When to use Redis: multi-instance applications, distributed cache required
```

---

### 🧪 Thought Experiment

**LRU vs LFU FOR A NEWS SITE:**

A news site caches article content. Top 100 "evergreen" articles (published months ago) are read 100,000 times/day each. A trending article (published today) is read 500,000 times in the first hour, then drops to 100 reads/day.

**LRU behavior:** Trending article is "most recently used" during its viral hour. After the viral hour, the trending article hasn't been read for an hour → moves toward the LRU end. If memory pressure occurs, LRU might evict the trending (now cold) article AND one of the evergreen articles. After the trending article goes cold, LRU works well again.

**LFU behavior:** After the viral hour, the trending article has accumulated 500,000 accesses (high frequency). LFU will NOT evict it even though it's cold - it thinks it's "popular" because of the viral period. The evergreen articles (100K/day × 30 days = 3M accesses) are also protected. LFU with decay time: the trending article's frequency counter decays over minutes/hours → eventually LFU will correctly identify it as cold and evict it.

**Winner:** Redis LFU with `lfu-decay-time=1` (fast decay) handles this well. Caffeine Window TinyLFU handles it even better because of the admission filter.

---

### 🧠 Mental Model / Analogy

> LRU = last to leave the party gets to stay. LFU = most popular guest gets to stay (by total interactions). FIFO = first to arrive is first to leave (a queue). For a nightclub (cache) that wants to maximize revenue: keep frequent guests (high-spenders = hot data). LFU wins for stable popularity. LRU wins when trends shift quickly. FIFO wins when you don't know or care about popularity.

---

### 📶 Gradual Depth - Four Levels

**Level 1:** Cache full → eviction removes an entry. LRU: not used recently → remove. LFU: not used frequently → remove. FIFO: oldest insert → remove. Redis default: no eviction (`noeviction`) - you must configure `maxmemory-policy`.

**Level 2:** For general caching: use `allkeys-lru` (good default). For stable product catalogs: use `allkeys-lfu` (keeps frequently accessed products). For session caches where session data should expire but critical config data shouldn't: use `volatile-lru` (only evicts keys WITH TTL). Set `maxmemory-samples=10` for more accurate LRU approximation.

**Level 3:** Monitor eviction rate with `INFO stats → evicted_keys`. High eviction rate = cache is too small for the working set → add memory or reduce object sizes. Use `redis-cli --hotkeys` (with LFU policy) to identify the most frequently accessed keys - helps verify that hot data is staying in cache. In Java: use Caffeine over Redis for in-process caches - Window TinyLFU has provably better hit rates, and in-process cache has zero network RTT.

**Level 4:** Eviction policy selection is a workload-specific optimization problem. The Belady OPT algorithm (evict the key that will not be used for the longest time in the future) is provably optimal but requires future knowledge. LRU approximates OPT for workloads with strong temporal locality (recently accessed = likely accessed again). LFU approximates OPT for workloads with stable Zipfian access distributions (a small set of keys accounts for most accesses, and this set is stable over time). For workloads with shifting access patterns (trending content, seasonal products), neither pure LRU nor pure LFU is optimal - Window TinyLFU's admission window handles this by giving new entries a chance to prove themselves before committing them to the protected region.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ REDIS EVICTION ON maxmemory EXCEEDED                 │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Client: SET new_key value                            │
│   Redis: check used_memory > maxmemory               │
│     YES → need to evict                              │
│       Sample maxmemory-samples (default 5) keys      │
│       Select worst candidate per policy:             │
│         allkeys-lru: oldest last-access time         │
│         allkeys-lfu: lowest access frequency         │
│         volatile-ttl: shortest TTL remaining         │
│       Evict selected key                             │
│       [EVICTION ← YOU ARE HERE: key removed]         │
│       Retry: check memory again, repeat if needed    │
│     NO → proceed with SET                            │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture - End-to-End Flow

```
Redis maxmemory=100MB, policy=allkeys-lru
Cache has 95MB of product entries.
New request: cache product:98765 (5MB entry needed)

→ Redis: 95MB + 5MB = 100MB → at limit → eviction needed
→ Redis samples 5 random keys:
    product:10  (last accessed: 10 minutes ago)
    product:20  (last accessed: 2 minutes ago)
    product:30  (last accessed: 45 minutes ago)  ← LRU candidate
    product:40  (last accessed: 8 minutes ago)
    product:50  (last accessed: 3 minutes ago)
→ LRU: evict product:30 (oldest last-access: 45 min ago)
→ Redis frees product:30's memory
→ Redis stores product:98765

Consequence: next request for product:30 → cache MISS → DB fetch
(product:30 was evicted not because of TTL but because it was least recently used)

Monitoring:
  redis-cli INFO stats | grep evicted_keys
  OBJECT IDLETIME product:30  # seconds since last access
```

---

### ⚖️ Comparison Table

| Policy       | What's Evicted            | Best For                                      | Weakness                            |
| ------------ | ------------------------- | --------------------------------------------- | ----------------------------------- |
| LRU          | Least recently accessed   | General caching, temporal locality            | Scan pollution; evicts old hot keys |
| LFU          | Least frequently accessed | Stable hot sets (product catalog)             | Slow to adapt to new trending items |
| FIFO         | Oldest inserted           | Simple queues; uniform distribution           | Ignores access patterns entirely    |
| Random       | Random entry              | Uniform workloads                             | Unpredictable, may evict hot data   |
| volatile-ttl | Shortest TTL              | When you want to evict "about to expire" keys | Ignores access patterns             |
| noeviction   | Nothing (error)           | Critical data that must not be evicted        | OOM risk if memory grows            |

---

### ⚠️ Common Misconceptions

| Misconception                        | Reality                                                                                                                                                                              |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| "LRU evicts the oldest keys overall" | LRU evicts by last ACCESS time, not creation time. A key created 1 year ago but accessed 1 minute ago will NOT be evicted before a key created 5 minutes ago but not accessed since  |
| "Redis LRU is exact"                 | Redis uses sampling-based approximate LRU (not exact). The `maxmemory-samples` setting controls accuracy - higher = more accurate but more CPU                                       |
| "noeviction is the safest policy"    | `noeviction` causes Redis to return errors when memory is full, which breaks applications. It's only "safe" for data that must not be lost - you must also ensure memory never fills |

---

### 🔗 Related Keywords

**Prerequisites:** TTL, Caching, Redis Data Structures
**Builds On This:** Caching, System Design
**Related:** TTL, Cache Invalidation, Redis Data Structures

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ LRU         │ Evict least recently ACCESSED              │
│ LFU         │ Evict least frequently ACCESSED            │
│ FIFO        │ Evict oldest INSERTED                      │
│ REDIS CFG   │ maxmemory + maxmemory-policy in redis.conf │
│ DEFAULT     │ Redis default = noeviction (error on full) │
│ RECOMMEND   │ allkeys-lru (general) / allkeys-lfu (stable)│
│ MONITOR     │ INFO stats → evicted_keys rate             │
│ JAVA        │ Caffeine Window TinyLFU (best hit rate)    │
│ ONE-LINER   │ "When cache is full, eviction picks who    │
│             │  leaves - LRU=idle, LFU=unpopular"         │
│ NEXT EXPLORE│ Cache Stampede → Thundering Herd           │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This

**Q1.** (TYPE B) Your Redis cache has `allkeys-lru` configured. After a batch job at midnight scans and loads 500,000 product IDs into the cache for a nightly report, your hit rate drops from 95% to 40% and stays low for the next 2 hours. Explain: what happened (LRU cache pollution), and what are two ways to prevent it?
