---
id: SYD-043
title: URL Shortener Design
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★☆
depends_on: SYD-042, SYD-027
used_by: SYD-044
related: SYD-044, SYD-028, SYD-011
tags:
  - architecture
  - design
  - intermediate
  - caching
  - algorithm
status: complete
version: 3
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 43
permalink: /syd/url-shortener-design/
---

# SYD-043 - URL Shortener Design

⚡ TL;DR - A URL shortener maps long URLs to compact codes and redirects fast at scale; the hard parts are code generation, collision avoidance, hot-key caching, and abuse prevention.

| SYD-043         | Category: System Design        | Difficulty: ★★☆ |
| :-------------- | :----------------------------- | :-------------- |
| **Depends on:** | SYD-042, SYD-027               |                 |
| **Used by:**    | SYD-044                        |                 |
| **Related:**    | SYD-044, SYD-028, SYD-011     |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
Long URLs are 200+ character strings. They break in emails, exceed character limits in SMS, and are impossible to memorize. Tracking click analytics on a raw long URL requires middleware interception with no standard mechanism.

**THE BREAKING POINT:**
Social media enforces character limits. QR codes break with URLs longer than ~100 characters. Marketing campaigns need click analytics. Affiliate systems need per-link tracking. None of these work with raw long URLs.

**THE INVENTION MOMENT:**
Store a mapping `short_code -> long_url` in a database. Serve `GET /abc123` returning `302 Location: <long_url>`. The short code is 6-8 characters. The redirect is a single DB lookup. Analytics are captured on every redirect.

**EVOLUTION:**
TinyURL (2002) was first. Bit.ly added analytics and APIs. Twitter's t.co added security scanning and brand safety. Modern URL shorteners add: custom domains, link expiry, password protection, QR code generation, campaign tracking (UTM parameters), and real-time click dashboards. The scale challenge shifted from "handle the lookups" to "serve analytics on billions of clicks in real time."

---

### 📘 Textbook Definition

A **URL shortener** is a web service that accepts a long URL and returns a short alias URL. When a client requests the alias, the service performs a redirect (HTTP 301 or 302) to the original URL. Core components: a code generator, a persistent mapping store, a redirect service (hot path), and an analytics pipeline (cold path). The system is read-heavy (1000:1 redirect:create ratio is typical).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Store `abc123 -> https://very.long.url/` and redirect fast.

**One analogy:**

> A URL shortener is like a coat check. You hand in your coat (long URL) and receive a ticket number (short code). You return the ticket (short URL click) and get your coat back. The attendant (redirect server) just looks up the ticket in a small ledger.

**One insight:**
Reads dominate writes heavily (10K:1 or more). The entire redirect hot path should be serviced from cache. The DB is a backup for cache misses, not the primary read path.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Each short code maps to exactly one long URL.
2. The same long URL may optionally map to multiple short codes (or be deduplicated).
3. Short code generation must be collision-free and globally unique.
4. The redirect path must be faster than the user noticing the redirect (< 50ms p99).

**DERIVED DESIGN:**
Write path: validate long URL, generate unique code (counter+Base62 or random+collision check), store mapping, return short URL.
Read path: extract code from request, check Redis cache, if miss query DB, return redirect, increment click counter async.

**THE TRADE-OFFS:**
**Gain:** Clean short URLs, analytics, abuse control from a centralized layer.
**Cost:** Single point of failure if the shortener is down; trust issues (users clicking unknown short URLs); link decay (shortener goes offline = all links die).

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Unique code assignment without collisions; fast redirect lookup.
**Accidental:** Analytics pipeline, custom domains, link preview metadata scraping.

---

### 🧪 Thought Experiment

**SETUP:** A viral tweet contains a short link. The tweet gets 5M impressions in 10 minutes. All 5M users click within minutes.

**WHAT HAPPENS WITHOUT CACHING:**
5M requests hit the redirect service. Each performs a DB lookup. DB serves 50K QPS at best. Queue forms. Redirects take 10+ seconds. The tweet becomes unfollowable. The DB crashes.

**WHAT HAPPENS WITH CACHING:**
Redis holds the `code -> long_url` mapping with TTL=24h. First click misses cache, populates it. Subsequent 4,999,999 clicks hit Redis directly (sub-millisecond). DB is queried once. System serves 5M requests without DB involvement.

**THE INSIGHT:**
URL shorteners are a perfect cache use case: reads outnumber writes, data is immutable (code -> URL never changes), and the working set of "hot links" is small. Cache hit rates above 99% are achievable.

---

### 🧠 Mental Model / Analogy

> A URL shortener is a key-value lookup service with a redirect layer. The short code is the key. The long URL is the value. Redis is the front-of-store. PostgreSQL/MySQL is the warehouse. Analytics falls off the side asynchronously.

- **Short code** = key (6-8 Base62 characters)
- **Long URL** = value
- **Redis** = cache layer (99% of reads)
- **Database** = durable store (1% of reads on miss)
- **Click counter** = async side channel
- **302 redirect** = response type (don't cache in browser)

Where this analogy breaks down: most key-value stores don't generate keys on write - the URL shortener must generate unique short codes, which adds a code-generation complexity layer.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
You give a long address; the service gives you a short one. Anyone who uses the short address is automatically sent to the long one.

**Level 2 - How to use it (junior developer):**
POST `/shorten {url: "..."}` -> returns `{short_url: "https://svc.io/abc123"}`. The service returns a 302 redirect on GET `/abc123`. Use 301 for permanent redirects (browser caches), 302 for trackable redirects (every click hits your server).

**Level 3 - How it works (mid-level engineer):**
Code generation options: (a) counter-based: encode a DB auto-increment ID in Base62 (predictable, sequential); (b) random token: UUID prefix, collision check on insert; (c) hash-based: MD5/SHA of long URL, take first 7 chars, check collision. Redirect: Redis GET `code` -> on hit return 302; on miss DB SELECT, populate Redis, return 302. Analytics: Kafka event per click, Flink/Spark aggregation.

**Level 4 - Why it was designed this way (senior/staff):**
Counter-based Base62 is simplest but reveals creation order (security concern) and requires a centralized counter (single point of contention at high write rate). Random token is stateless but collision probability grows with dataset. Hash-based deduplication (same URL = same code) saves storage but breaks analytics attribution per share. A distributed ID scheme (Snowflake ID + Base62) gives sortability, uniqueness, and no central counter. Click analytics must be async - the redirect p99 cannot be held hostage to a Kafka write or a DB increment.

**Expert Thinking Cues:**
- Ask: "Should the same long URL get the same short code, or a new one each time?"
- Ask: "What happens to existing short links if the service migrates DB?"
- Red flag: synchronous click analytics on redirect hot path
- Red flag: no abuse prevention - shorteners can launder malicious URLs

---

### ⚙️ How It Works (Mechanism)

**Create flow:**
```
POST /shorten {url: long_url}
  1. Validate URL (format, domain blacklist)
  2. Check duplicate: existing mapping for long_url?
  3. Generate code: encode(counter++) -> Base62
  4. INSERT INTO mappings (code, long_url, created_at)
     ON CONFLICT (code) -> regenerate
  5. Return {short_url: "https://svc.io/{code}"}
```

**Redirect flow:**
```
GET /{code}
  1. Redis GET {code}
     -> HIT: return 302 Location: long_url
     -> MISS:
       a. SELECT long_url FROM mappings WHERE code=?
       b. Redis SET {code} long_url EX 86400
       c. return 302 Location: long_url
  2. Async: publish click event to Kafka
     {code, user_agent, ip, timestamp, referer}
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
```
[User clicks short link in browser]
         |
         v
[DNS resolves to CDN/LB]  <- YOU ARE HERE
         |
         v
[Redirect service extracts code]
         |
         v
[Redis lookup: code -> long_url]
    HIT (99%)  |  MISS (1%)
         |              |
         |         [DB lookup + cache fill]
         v
[302 Location: long_url]
         |
         v
[Async: click event to Kafka]
         |
         v
[Analytics pipeline: aggregate]
```

**FAILURE PATH:**
```
[Redis unavailable]
         |
[Fallback: direct DB lookup]
         |
[Higher latency but functional]
         |
[Alert: Redis down, DB under elevated load]
```

**WHAT CHANGES AT SCALE:**
At 1B redirects/day (11K QPS): Redis cluster required (single-node memory insufficient for all codes). Partition Redis by code prefix. Use CDN to cache redirect responses for static URLs. Separate read replicas for DB.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
Counter-based code generation needs a distributed counter or centralized sequence generator. Snowflake IDs (timestamp + machine_id + sequence) solve this without central coordination. Cache stampede on cache expiry of a viral link: use probabilistic early expiration (Redis jitter on TTL).

---

### 💻 Code Example

**BAD - sequential counter reveals order, no collision check:**
```python
# BAD: auto-increment exposes enumeration
# BAD: no abuse check, no cache
@app.post("/shorten")
def shorten(url: str):
    cur.execute(
        "INSERT INTO links (url) VALUES (?)", url
    )
    id = cur.lastrowid  # predictable, enumerable!
    return {"short": f"https://svc.io/{id}"}
```

**GOOD - Base62 encoding with caching and validation:**
```python
import hashlib, base64, re

ALPHABET = (
    "0123456789"
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
)

def base62(n: int, length=7) -> str:
    code = []
    while n:
        n, r = divmod(n, 62)
        code.append(ALPHABET[r])
    return "".join(reversed(code)).zfill(length)

def is_safe_url(url: str) -> bool:
    # Basic validation: scheme + no SSRF targets
    if not re.match(r"^https?://", url):
        return False
    if any(b in url for b in ["localhost", "127.0"]):
        return False
    return True

def shorten(long_url: str, db, cache) -> str:
    if not is_safe_url(long_url):
        raise ValueError("Unsafe URL")

    # Check cache/db for duplicate
    key = hashlib.md5(long_url.encode()).hexdigest()
    existing = cache.get(f"dup:{key}")
    if existing:
        return existing

    # Generate unique code via DB sequence
    row = db.execute(
        "INSERT INTO links (url) VALUES (?) RETURNING id",
        long_url
    ).fetchone()
    code = base62(row["id"])
    short = f"https://svc.io/{code}"

    # Cache for dedup and redirect
    cache.set(f"dup:{key}", short, ex=86400)
    cache.set(code, long_url, ex=86400)
    return short

def redirect(code: str, db, cache) -> str:
    # Hot path: cache first
    url = cache.get(code)
    if url:
        return url
    row = db.execute(
        "SELECT url FROM links WHERE code = ?", code
    ).fetchone()
    if not row:
        raise KeyError("Not found")
    cache.set(code, row["url"], ex=86400)
    return row["url"]
```

**How to test / verify correctness:**
- Generate 1M links, assert no duplicate short codes.
- Request a non-existent code, assert 404.
- Populate Redis, verify redirect returns without DB query (mock DB to raise on call).
- Submit a malicious URL (SSRF target), assert rejection.

---

### ⚖️ Comparison Table

| Code strategy     | Sequential | Guessable | Deduplicates | Collision risk |
| ----------------- | ---------- | --------- | ------------ | -------------- |
| Counter + Base62  | Yes        | Yes       | No           | None           |
| Random token      | No         | No        | No           | Grows with N   |
| Hash-based        | No         | No        | Yes          | Managed        |
| Snowflake + Base62 | Sortable  | No        | No           | None           |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
| ------------- | ------- |
| "301 redirect is better for performance" | 301 tells browsers to cache the redirect permanently, bypassing your server. This prevents click tracking and makes the redirect irreversible in the browser's cache. Use 302 for trackable links. |
| "Hash-based codes never collide" | Hash truncation (taking first 7 chars of MD5) does collide at scale. At 1 billion URLs, collision probability is non-negligible. Always check for collision on insert. |
| "The DB is the bottleneck" | The DB is rarely the bottleneck with a warm Redis cache. The bottleneck is usually Redis throughput or network bandwidth on high-traffic viral links. |
| "URL shorteners are simple CRUD apps" | At scale they require: distributed ID generation, cache stampede prevention, real-time analytics pipelines, abuse detection, custom domain routing, and CDN integration. |
| "All short URLs should be permanent" | Links should have configurable expiry. Expired links free up code space and prevent link hijacking (expired code reassigned to malicious URL). |

---

### 🚨 Failure Modes & Diagnosis

**Failure Mode 1: Cache stampede on viral link expiry**

**Symptom:** 10K simultaneous cache misses for the same code; DB queries spike; latency spikes.

**Root Cause:** A viral link's Redis TTL expired; all in-flight requests simultaneously query the DB.

**Diagnostic:**
```bash
redis-cli monitor | grep "GET viral_code"
# Hundreds of simultaneous GETs without SET following
```

**Fix:** Use probabilistic (jittered) cache expiry - each cached item's TTL = base_ttl + random(0, jitter). Or use cache mutex: first miss acquires lock, others wait for cache population.

**Prevention:** Set TTL based on link age and click rate; hot links get longer TTLs.

---

**Failure Mode 2: Code collision on hash-based generation**

**Symptom:** Two different long URLs map to the same short code; one URL becomes unreachable.

**Root Cause:** Hash truncation collision on insert without proper collision detection.

**Diagnostic:**
```sql
SELECT code, COUNT(*) FROM links
GROUP BY code HAVING COUNT(*) > 1;
```

**Fix:** Add UNIQUE constraint on `code` column. On conflict, regenerate with a different salt.

**Prevention:** Always insert with `ON CONFLICT DO NOTHING` + verify affected rows = 1.

---

**Failure Mode 3 (Security): Short URL phishing vector**

**Symptom:** Users report being redirected to malicious sites after clicking "trusted" short links.

**Root Cause:** No URL validation at create time; attacker created links to phishing pages.

**Diagnostic:** Check redirect destination against malware URL feeds (Google Safe Browsing API).

**Fix:**
```python
# BAD: no validation
def shorten(url): return store(url)

# GOOD: validate against Safe Browsing
import requests
def is_safe(url):
    resp = requests.post(SAFE_BROWSING_API, json={
        "client": {"clientId": "app", "clientVersion": "1"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    })
    return not resp.json().get("matches")
```

**Prevention:** Check all new URLs against Safe Browsing API at creation time; rescan existing links periodically.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- [[SYD-027 - Capacity Planning]] - estimate read/write QPS before designing
- [[SYD-042 - Data Partitioning Strategies]] - shard mappings table when it grows large

**Builds On This (learn these next):**
- [[SYD-044 - Rate Limiter Design]] - protect the create endpoint from abuse
- [[SYD-028 - Rate Limiting (System)]] - complementary protection layer

**Alternatives / Comparisons:**
- [[SYD-011 - Consistent Hashing (Load Balancing)]] - distribute redirect service across nodes

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│ WHAT IT IS   │ Key-value mapping service with   │
│              │ HTTP redirect layer              │
├──────────────┼──────────────────────────────────┤
│ PROBLEM      │ Long URLs unusable in limited-   │
│ IT SOLVES    │ character contexts + analytics   │
├──────────────┼──────────────────────────────────┤
│ KEY INSIGHT  │ Read:write is 10000:1; cache     │
│              │ the hot path completely          │
├──────────────┼──────────────────────────────────┤
│ USE WHEN     │ Marketing, SMS, social sharing,  │
│              │ QR codes, link analytics         │
├──────────────┼──────────────────────────────────┤
│ AVOID WHEN   │ Links must be permanent and      │
│              │ independent of third-party SLA   │
├──────────────┼──────────────────────────────────┤
│ TRADE-OFF    │ Convenience vs link dependency   │
│              │ on shortener availability        │
├──────────────┼──────────────────────────────────┤
│ ONE-LINER    │ "Generate unique code, cache     │
│              │ redirect, track async."          │
├──────────────┼──────────────────────────────────┤
│ NEXT EXPLORE │ SYD-044 Rate Limiter Design      │
└─────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. Use 302 redirects (not 301) so every click goes through your server for tracking.
2. Cache the code->URL mapping in Redis; the DB is a fallback, not the read path.
3. Validate all URLs at creation time against malware/phishing lists.

**Interview one-liner:** "A URL shortener is a read-heavy key-value store with a redirect layer - the interesting parts are collision-free code generation, cache-first redirect serving, and async click analytics."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:** For read-heavy key-value lookups, the primary store is rarely the bottleneck - the cache layer is the critical path. Design the cache strategy first (eviction, TTL, stampede prevention), then treat the DB as a durable fallback.

**Where else this pattern appears:**
- **Feature flags:** A feature flag key maps to a configuration value - read heavily from cache, rarely written.
- **DNS resolution:** A domain name maps to an IP address - cached aggressively at every layer.
- **Session lookup:** A session token maps to user data - same read-heavy, write-rare pattern.

---

### 💡 The Surprising Truth

HTTP 301 redirects can trap users in stale redirects for months. A browser that cached a 301 redirect to a new destination will continue using that destination even if the mapping is changed or deleted from the shortener database - until the user clears their browser cache. Bit.ly uses 301 for SEO value but accepts this trade-off. For mutable links or A/B testing, 302 is the only safe choice.

---

### 🧠 Think About This Before We Continue

**Q1 (Scale):** Your URL shortener serves 100K redirects/second on Black Friday. Your Redis cluster has 3 nodes. A single viral campaign link receives 50K redirects/second - half your total traffic. How does this hot key affect your Redis cluster, and what architectural change handles it?

*Hint:* A single Redis key is served by one primary node regardless of cluster size. 50K QPS on one node is feasible, but 500K is not. Explore key replication patterns (client-side read from multiple replicas) or a tiered local cache (in-process LRU in the redirect service) for ultra-hot keys.

**Q2 (Design Trade-off):** Should your URL shortener deduplicate (same long URL = same short code) or allow multiple short codes per long URL? Evaluate both for marketing campaign tracking, click analytics accuracy, and storage efficiency.

*Hint:* Deduplication requires a reverse index (long_url -> code) that must be consistent with the forward index. Multiple codes per URL allows per-campaign tracking. Explore how Bit.ly handles this by creating new codes per-user even for the same destination URL.

**Q3 (First Principles):** A URL shortener that goes offline makes millions of existing links non-functional. Design a "link durability" feature where organizations can self-host their redirect rules so links survive the shortener going out of business.

*Hint:* Look at link durability through the lens of DNS - the shortener is a kind of DNS. Explore how PURL (Persistent URL) works and why W3ID (w3id.org) uses GitHub as the redirect config store to ensure permanence independent of any single service.
