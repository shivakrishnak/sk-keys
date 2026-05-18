---
id: SYD-043
title: URL Shortener Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★☆
depends_on: SYD-001, SYD-008
used_by: ""
related: SYD-008, SYD-014, SYD-031, SYD-028
tags:
  - architecture
  - design
  - hashing
  - redirection
  - intermediate
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 43
permalink: /technical-mastery/syd/url-shortener-design/
---

⚡ TL;DR - A URL shortener maps a short code (7-8
alphanumeric characters) to a long URL. The core
design: generate a unique ID, encode it in base62,
store the mapping in a key-value store, redirect via
HTTP 301/302. The hard problems are: ID generation at
scale (no collision, globally unique), redirect latency
(sub-10ms via cache), abuse prevention (spam, malware
URLs), and analytics (counting clicks without
adding redirect latency).

| #043            | Category: System Design               | Difficulty: ★★☆ |
| :-------------- | :------------------------------------ | :-------------- |
| **Depends on:** | Scalability Fundamentals, Caching     |                 |
| **Related:**    | Caching, CDN, Sharding, Rate Limiting |                 |

---

### 🔥 The Problem This Solves

A 280-character tweet with a 200-character URL wastes
nearly all the character budget. Sharing a URL in print
media, QR codes, or SMS requires something human-
manageable. Platform analytics require click tracking.
Marketing campaigns need per-campaign attribution.

**The simple approach fails at scale:**

- Random short codes: collision probability rises quickly
  at millions of URLs (birthday paradox)
- Centralized counter: single-point bottleneck
- No cache: every redirect hits the database (300ms+)
- No abuse check: becomes a free phishing redirect service

---

### 📘 Textbook Definition

**URL shortener:** A service that accepts a long URL and
returns a short URL (short code + domain). When a user
visits the short URL, the service looks up the short code,
retrieves the original URL, and returns an HTTP redirect.

**Core components:**

1. **Short code generator:** Produces unique, collision-
   free short codes from a space of N characters.
2. **Mapping store:** Key-value store: short_code → long_url.
3. **Redirect handler:** Receives short code, returns HTTP
   301 (permanent) or 302 (temporary) with Location header.
4. **Analytics pipeline:** Records click events without
   blocking the redirect path.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Accept a long URL → generate a unique short code → store
the mapping → redirect on lookup.

**One analogy:**

> A coat check: give your coat (long URL), get a ticket
> number (short code). When you return with the ticket,
> you get your coat back. The ticket number is small and
> easy to carry.

**One insight:**
The classic interview question is: "Generate a unique
short code." There are two approaches:

1. **Hash the long URL:** MD5/SHA → take first 7 chars.
   Risk: collisions (two different URLs produce the
   same first 7 chars). Requires collision detection
   and retry with appended salt.
2. **Unique ID counter:** Generate a unique 64-bit ID,
   encode in base62. No collisions. Requires a
   distributed ID generator (Snowflake IDs, or a
   counter service).
   Counter-based is preferred in production because it
   guarantees uniqueness without collision handling.

---

### 🔩 First Principles Explanation

**BASE62 ENCODING:**

```python
# Base62 encoding: map integer ID to short string
# Characters: 0-9 (10) + a-z (26) + A-Z (26) = 62

BASE62_CHARS = (
    "0123456789"
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
)

def encode_base62(num: int) -> str:
    """Encode integer to base62 string."""
    if num == 0:
        return BASE62_CHARS[0]
    result = []
    while num > 0:
        result.append(BASE62_CHARS[num % 62])
        num //= 62
    return "".join(reversed(result))

def decode_base62(s: str) -> int:
    """Decode base62 string to integer."""
    result = 0
    for char in s:
        result = result * 62 + BASE62_CHARS.index(char)
    return result

# 7-character base62: 62^7 = 3.5 trillion URLs
# At 100M new URLs/day: 96 years of capacity
print(encode_base62(123456789))  # "8M0kX"
print(encode_base62(1000000000)) # "15ftgG"
```

**UNIQUE ID GENERATION OPTIONS:**

```
Option 1: Database auto-increment
  - Simple: each insert returns a unique ID
  - Problem: single DB = write bottleneck at scale
  - Problem: exposes total URL count (security)
  - Suitable for: < 1M URLs/day

Option 2: Distributed counter (Redis INCR)
  redis.incr("url:counter") → atomic, returns unique int
  - Fast (sub-millisecond), no collision
  - Problem: single Redis = SPOF; use Redis Cluster
  - Suitable for: 1-10M URLs/day

Option 3: Snowflake ID (Twitter pattern)
  64-bit: [timestamp 41 bits][datacenter 5][worker 5][seq
    12]
  - Globally unique, sortable, no coordination needed
  - Up to 4096 IDs/millisecond per worker
  - Suitable for: > 10M URLs/day

Option 4: Hash-based (MD5/SHA + first 7 chars)
  - No ID generator needed
  - Problem: collisions require detection+retry
  - Problem: same URL → same code (may be desired)
  - Suitable for: deduplication of identical URLs
```

**REDIRECT - 301 vs 302:**

```
HTTP 301 Permanent Redirect:
  - Browser caches the redirect
  - Second visit: browser goes directly to long URL
    (does NOT hit short URL service)
  - No analytics on repeat visits (cached in browser)
  - Lower server load for popular URLs
  - BAD for click analytics, GOOD for SEO and load

HTTP 302 Temporary Redirect:
  - Browser does NOT cache the redirect
  - Every visit hits the short URL service
  - Accurate click analytics (every click counted)
  - Higher server load
  - BAD for performance, GOOD for analytics
  - Default choice for analytics-enabled shorteners

Solution: Use 302 for analytics, but serve it from
  the edge cache (Nginx/CDN). The edge caches the
  (short_code → long_url) lookup so the database
  is not hit. Analytics still recorded at the edge.
```

---

### 🧪 Thought Experiment

**SIZING: Design a URL shortener for 100M daily URLs**

Daily writes: 100M URLs/day = 1,157 writes/second
Peak (10x): 11,570 writes/second
Daily reads (redirects): 10B reads/day (100x read:write)
= 115,741 reads/second
Peak reads: ~1M reads/second

**Storage:**
Each mapping: 7 bytes (short code) + 2,048 bytes (max URL)

- metadata ~200 bytes = ~2,255 bytes ≈ 3KB per URL
  100M URLs/day × 3KB = 300GB/day = 109TB/year
  Use sharded key-value store (Cassandra, DynamoDB, Redis
  Cluster) for horizontal scale.

**Read path:** 1M reads/second cannot be served by
even a sharded database directly. 80% of reads are to
popular URLs (Pareto). Cache the top URLs in Redis
(in-memory). Cache hit ratio target: 95%+. With 95%
cache hit: only 50K reads/second to the database.

**Write throughput:** 11,570 writes/second is achievable
with Cassandra or DynamoDB (wide-column stores handle
millions of writes/second). Key = short_code.

**ID generation:** Snowflake ID service (or DynamoDB
auto-increment counter). One Snowflake worker handles
4,096 IDs/ms = 4M IDs/second. More than enough.

---

### 🧠 Mental Model / Analogy

> URL shortening is like abbreviating a book citation:
> "The Great Gatsby, F. Scott Fitzgerald, 1925, Chapter 5,
> paragraph 3, sentence 2" → "TGG:5.3.2"
>
> The abbreviation is meaningless without the reference
> table (the library catalog). The short code is the
> abbreviation; the key-value store is the catalog.
>
> The design problem is: how do you ensure two different
> citations never produce the same abbreviation? And how
> do you look up the full citation in < 10ms?

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A URL shortener gives you a small, shareable link that
redirects to the real (long) link. When you click the
short link, the service looks up the full URL and sends
you there automatically.

**Level 2 - How to use it (junior developer):**
POST a long URL to the API → receive a short code.
When a user visits the short code URL, the service
does an HTTP redirect. Use a database (key=short_code,
value=long_url). For the short code: hash the URL or
use an auto-increment ID encoded in base62.

**Level 3 - How it works (mid-level engineer):**
ID generator (Snowflake or Redis INCR) → base62 encode
the ID (7 chars) → store mapping in Redis + a backing
store (Cassandra or DynamoDB). Redirect: check Redis
cache first (microseconds), then database on cache miss.
Use 302 redirect for click counting; cache the redirect
mapping at the CDN edge to avoid database load.

**Level 4 - Why it was designed this way (senior/staff):**
The redirect path is read-heavy and latency-sensitive.
The entire mapping fits in memory for popular URLs.
The hard design choices: (1) ID generation without
single-point bottleneck (Snowflake pattern), (2) redirect
analytics without adding latency to the critical path
(async write to analytics queue from the redirect handler,
not synchronously before responding), (3) abuse prevention
(safe browsing API check on write, blocklist of known
malicious domains, rate limiting per IP on write).

**Level 5 - Mastery (distinguished engineer):**
The meta-challenge of URL shorteners in production:
custom aliases, expiration (TTLs), A/B testing via
multiple targets, per-campaign analytics with segment
grouping, link preview cards (OGP metadata scraping),
and enterprise SSO (links visible only to authenticated
users). Each feature is a separate subsystem. The
foundational redirect and short code generation are
simple; the feature surface is what grows. The
architectural risk: at 10B+ mappings, the key-value
store needs consistent hashing and careful TTL-based
eviction. Hotspot URLs (viral links) cause cache
stampedes - use cache-aside with distributed locking
(or probabilistic early expiration) to prevent
thundering herd on cache miss.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ URL SHORTENER DATA FLOW                             │
│                                                      │
│ WRITE (shorten URL):                                │
│  Client ──POST /shorten?url=long-url──► API Server  │
│  API Server ──► ID Generator (Snowflake/Redis)      │
│  ──► encode_base62(id) = "aB3xZ9k"                  │
│  ──► store("aB3xZ9k" → "long-url") in Redis + DB    │
│  ──► return "https://short.ly/aB3xZ9k"              │
│                                                      │
│ READ (redirect):                                    │
│  Client ──GET /aB3xZ9k──► CDN/Edge Cache           │
│  Cache HIT: return 302 + Location: long-url         │
│  Cache MISS: ──► API Server ──► Redis cache         │
│  Redis HIT: return 302 + populate CDN cache         │
│  Redis MISS: ──► Database lookup                    │
│  DB HIT: populate Redis + CDN + return 302          │
│  DB MISS: return 404                                │
│                                                      │
│ ANALYTICS (async):                                  │
│  Redirect handler ──publish click event──►          │
│       Analytics Queue (Kafka/SQS)                   │
│  Consumer aggregates and stores to data warehouse   │
│  NO analytics work on the critical redirect path   │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Core URL shortener service (Python/FastAPI)**

```python
import redis
import hashlib
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import boto3  # DynamoDB for persistence

app = FastAPI()
r = redis.Redis(host="localhost", port=6379)
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("url_mappings")

BASE62 = (
    "0123456789"
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
)

def encode_base62(n: int) -> str:
    if n == 0:
        return BASE62[0]
    chars = []
    while n:
        chars.append(BASE62[n % 62])
        n //= 62
    return "".join(reversed(chars))

# Counter in Redis (use Snowflake in prod)
def next_id() -> int:
    return r.incr("url:global:counter")

@app.post("/shorten")
def shorten(long_url: str) -> dict:
    # Validate URL (only http/https schemes accepted)
    if not long_url.startswith(("http://", "https://")):
        raise HTTPException(
            status_code=400,
            detail="Only http/https URLs allowed"
        )
    uid = next_id()
    short_code = encode_base62(uid)

    # Persist to DynamoDB (durable)
    table.put_item(Item={
        "short_code": short_code,
        "long_url": long_url,
    })
    # Cache in Redis (fast reads)
    r.setex(f"url:{short_code}", 86400, long_url)

    return {"short_url": f"https://short.ly/{short_code}"}

@app.get("/{short_code}")
def redirect(short_code: str):
    # Cache-aside: Redis first
    cached = r.get(f"url:{short_code}")
    if cached:
        long_url = cached.decode()
    else:
        # Cache miss: read from DynamoDB
        resp = table.get_item(
            Key={"short_code": short_code})
        item = resp.get("Item")
        if not item:
            raise HTTPException(status_code=404)
        long_url = item["long_url"]
        r.setex(f"url:{short_code}", 86400, long_url)

    # 302: every click hits service (analytics)
    return RedirectResponse(
        url=long_url, status_code=302)
```

**Example 2 - Hash-based vs counter-based (collision risk)**

```python
# BAD: Hash-based with no collision handling
import hashlib

def shorten_hash_bad(long_url: str) -> str:
    h = hashlib.md5(long_url.encode()).hexdigest()
    return h[:7]  # First 7 hex chars
    # PROBLEM 1: Two different URLs can produce
    #   the same first 7 hex chars (collision)
    # PROBLEM 2: Same URL always gets same code
    #   (prevents short codes per-user per-campaign)
    # PROBLEM 3: hex (16 chars) wastes half the
    #   address space vs base62 (62 chars)

# GOOD: Counter-based with base62 encoding
def shorten_counter_good(uid: int) -> str:
    return encode_base62(uid)
    # No collision: each UID is unique by construction
    # Large address space: 62^7 = 3.5 trillion
    # Independent of URL content: aliases possible
    # Deduplication: check DB if URL already shortened
    #   (optional; depends on whether same URL can
    #   have multiple short codes)
```

---

### ⚖️ Comparison Table

| Component             | Simple Approach            | Production Approach                  |
| --------------------- | -------------------------- | ------------------------------------ |
| Short code generation | MD5 of URL, first 7 chars  | Snowflake ID + base62 encode         |
| Storage               | Single RDBMS table         | Redis cache + Cassandra/DynamoDB     |
| Redirect              | DB lookup on every request | CDN edge cache → Redis → DB          |
| Analytics             | Synchronous DB write       | Async Kafka event, aggregated        |
| Abuse prevention      | None                       | Rate limit writes, safe browsing API |

---

### ⚠️ Common Misconceptions

| Misconception                                    | Reality                                                                                                                                                                                                                                       |
| ------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 301 is better than 302 for all shorteners        | 301 caches in the browser - you lose all click analytics after the first visit. Use 302 if you need click counting. Use 301 only for permanent redirects where analytics are not needed.                                                      |
| MD5 hash of the URL guarantees uniqueness        | MD5 truncated to 7 characters has a high collision probability at millions of URLs (birthday paradox). Two different URLs can produce the same 7-character prefix. Always use a counter-based approach or detect collisions with retry logic. |
| URL shortener is a trivial system design problem | The basics are simple; the hard problems are scale (1B redirects/day), abuse prevention (phishing), TTL/expiry management, analytics latency, custom aliases, and link previews. These are each separate design challenges.                   |

---

### 🚨 Failure Modes & Diagnosis

**Cache Stampede on Viral Link**

**Symptom:**
A viral link (shared by a celebrity) receives 500K
requests in 60 seconds. The Redis cache entry expires.
500K concurrent requests all miss the cache
simultaneously and all query the database at once.
Database CPU spikes to 100%, request latency climbs
to 5+ seconds, timeouts cascade.

**Root Cause:** Thundering herd on cache expiry.
All 500K requests see a cold cache and all attempt
to warm it by reading from the database.

**Fix:**

```python
import threading
_cache_lock = {}  # Per-key locks in memory
# (Use Redis distributed lock in multi-process)

def get_with_lock(short_code: str) -> str:
    """Cache-aside with locking to prevent stampede."""
    cache_key = f"url:{short_code}"
    lock_key = f"lock:{short_code}"

    cached = r.get(cache_key)
    if cached:
        return cached.decode()

    # Acquire distributed lock (only 1 process warms)
    lock_acquired = r.set(
        lock_key, "1", nx=True, ex=5)  # 5s TTL
    if lock_acquired:
        try:
            # This process warms the cache
            resp = table.get_item(
                Key={"short_code": short_code})
            long_url = resp["Item"]["long_url"]
            r.setex(cache_key, 86400, long_url)
            return long_url
        finally:
            r.delete(lock_key)
    else:
        # Another process is warming; brief retry
        import time; time.sleep(0.05)
        cached = r.get(cache_key)
        return cached.decode() if cached else None
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `Scalability Fundamentals` - redirect path must
  handle millions of requests/second
- `Caching` - Redis cache-aside is the core of
  low-latency redirect service

**Builds On This (learn these next):**

- `CDN Architecture Pattern` - serve redirects
  from CDN edge nodes for global latency
- `Rate Limiting (System)` - prevent abuse of the
  shorten endpoint

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ WRITE FLOW  │ POST url → Snowflake ID → base62 →        │
│             │ store in Redis + DB → return short URL    │
├─────────────┼───────────────────────────────────────────┤
│ READ FLOW   │ GET /code → CDN cache → Redis → DB       │
│             │ → 302 redirect + async analytics event   │
├─────────────┼───────────────────────────────────────────┤
│ SHORT CODE  │ base62, 7 chars = 62^7 = 3.5T unique     │
│             │ Counter-based (not hash): no collisions  │
├─────────────┼───────────────────────────────────────────┤
│ 301 vs 302  │ 302: analytics. 301: browser caches,     │
│             │ no analytics after first visit.          │
├─────────────┼───────────────────────────────────────────┤
│ SCALE       │ 1M reads/sec → CDN + Redis (95% hit)    │
│             │ DB sees only 5% (cache misses)           │
├─────────────┼───────────────────────────────────────────┤
│ FAILURE     │ Viral link → cache stampede → use        │
│             │ distributed lock on cache warm           │
├─────────────┼───────────────────────────────────────────┤
│ ONE-LINER   │ "Counter-based ID + base62 + Redis       │
│             │  cache + 302 redirect = URL shortener"  │
├─────────────┼───────────────────────────────────────────┤
│ NEXT        │ Rate Limiter Design → News Feed Design   │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. Use a counter-based ID (Snowflake or Redis INCR) +
   base62 encoding for short codes. Never rely solely on
   truncated hashing - collisions occur at scale.
2. The redirect path is read-heavy. Cache short_code →
   long_url in Redis. Use 302 (not 301) to keep analytics
   working - but serve the 302 from edge cache to avoid
   DB load on every redirect.
3. The hardest operational problem is thundering herd:
   when a viral link's cache entry expires, lock the
   cache warming (one process warms; others wait) to
   prevent 500K concurrent DB queries.

**Interview one-liner:**
"URL shortener: POST long URL → Snowflake ID → base62 encode
(7 chars = 3.5T capacity) → store in Redis + DynamoDB → return
short URL. On redirect: CDN cache → Redis → DB, return HTTP 302
(not 301 - 302 enables analytics, 301 is browser-cached). Analytics
are async: emit click events to Kafka, don't block the redirect.
Failure mode: viral link causes cache stampede on expiry - fix with
distributed lock on cache warming (one process warms, others wait)."
