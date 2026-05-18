---
id: SYD-067
title: CDN Architecture Pattern
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★☆
depends_on: SYD-064
used_by: ""
related: SYD-064, SYD-001, SYD-031, SYD-049
tags:
  - architecture
  - cdn
  - caching
  - design
  - intermediate
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Mastery"
nav_order: 67
permalink: /technical-mastery/syd/cdn-architecture-pattern/
---

⚡ TL;DR - A CDN (Content Delivery Network) caches content
at edge servers geographically distributed worldwide. A
user in Tokyo gets your images and videos from a Tokyo
edge server, not your origin server in Virginia - reducing
latency from 200ms to 5ms. Beyond static assets (images,
JS, CSS), modern CDNs cache API responses, handle TLS
termination at the edge, and run code at edge nodes
(Cloudflare Workers, Lambda@Edge). Key design question:
what should be cached at the edge vs. served from origin?
Rules: anything public, cacheable, and not user-specific
belongs at the edge.

| #067 | Category: System Design | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | What is a Cache (Conceptual) | |
| **Related:** | What is a Cache, Load Balancing, Caching, Video Streaming Design | |

---

### 🔥 The Problem This Solves

A Netflix video file is 4GB. If all viewers stream from
one data center in Virginia, international users experience
250ms+ latency for each chunk. At 10 million concurrent
viewers: 40TB/second of bandwidth from one location
is physically impossible. CDN solution: distribute copies
of the video to 200+ edge locations. Japanese viewers
get from Tokyo. German viewers from Frankfurt. Bandwidth
distributed globally. Latency: sub-10ms for the
nearest edge.

---

### 📘 Textbook Definition

**CDN (Content Delivery Network):** A geographically
distributed network of proxy servers and data centers
(edge locations/PoPs - Points of Presence) that deliver
content to users from the location nearest to them.

**Edge server / PoP:** A CDN server at a specific
geographic location. Caches content from the origin
server. Serves cached content to nearby users.

**Origin server:** The authoritative source of content
(your web server, application server, or storage bucket).
The CDN fetches from origin on a cache miss, then caches
the result.

**Cache-Control header:** HTTP header that instructs
CDNs and browsers how long to cache a response.
`Cache-Control: public, max-age=86400` = cache for 24 hours.
`Cache-Control: private, no-store` = never cache (user-specific).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Copies of your content, cached near your users.
Less distance = less latency = better experience.

**One analogy:**
> Amazon's warehouses vs. one central fulfillment center:
> Without CDN: one warehouse in Ohio ships to all US
> customers. 3-day delivery to LA. 1-day to Cleveland.
> With CDN: warehouses in Seattle, LA, Dallas, Miami.
> Same-day delivery to most customers because the item
> is already near them.
>
> CDN: "pre-shipping" popular content to locations
> near your users before they ask for it (or caching
> it after the first request from that region).

**One insight:**
The most important architectural decision with a CDN
is determining what to put at the edge. Static assets
(images, JS bundles) are obvious candidates. But the
real value comes from caching API responses for public,
non-user-specific data (product catalog, pricing,
trending content lists). These can have CDN cache TTLs
of 1-60 minutes, dramatically reducing origin traffic.
User-specific data (cart, order history, account page)
must never be cached at the CDN (served privately).

---

### 🔩 First Principles Explanation

**CDN REQUEST FLOW:**
```
USER (Tokyo) requests: example.com/image.jpg

WITHOUT CDN:
  Tokyo → DNS → example.com → Virginia origin → 200ms
  
WITH CDN (Cloudflare, Fastly, CloudFront):
  Tokyo → DNS → nearest CDN PoP (Tokyo edge)
  
  CDN checks cache:
    HIT: return image immediately (< 5ms)
    
    MISS:
      CDN Tokyo → origin Virginia (200ms, one-time)
      CDN caches image at Tokyo edge (TTL: 1 year)
      Return image to user
  
  All subsequent Tokyo users: CDN HIT (< 5ms).
  Origin is only called once per TTL per PoP.

CDN CACHE KEY:
  URL: example.com/image.jpg
  Optionally: query params, headers, cookies
  
  Wrong: caching with user-specific cookies in key.
  → Each user gets a separate cache entry. No sharing.
  → Effectively defeats the CDN for that resource.
  
  Right: strip user-specific headers before caching.
  Accept-Language can be part of the key (content varies).
```

**WHAT TO CACHE AT THE EDGE:**
```
ALWAYS CACHE (public, static):
  - Images, videos, audio (TTL: 1 year + versioning)
  - JavaScript bundles (versioned via content hash)
  - CSS stylesheets (versioned)
  - Fonts
  - Public API responses (product catalog, pricing)
    TTL: 1-60 minutes depending on freshness need

NEVER CACHE:
  - User-specific pages (account, cart, orders)
    Cache-Control: private, no-store
  - Authenticated API responses (user data)
  - Payment pages
  - Health check endpoints (/health)
    (CDN caching health responses defeats monitoring)

SOMETIMES CACHE (with care):
  - Search results (short TTL: 1-5 minutes)
  - Homepage (short TTL if personalized = never cache)
  - API responses: OK if same for all users
    (trending lists, featured products)
```

**CACHE INVALIDATION AT CDN:**
```
Problem: you deploy a new JS bundle.
Old version cached at 200+ edge nodes globally.
Users get old code for up to 1 year (cache TTL).

Solution: content-based versioning.
  Instead of: /app.js?v=1.2 (version in query param)
  Use: /app.a1b2c3d4.js (hash in filename)
  
  When code changes: hash changes.
  New URL: cache miss at all edges. Fresh content.
  Old URL: still cached but nobody requests it anymore.
  TTL: 1 year (or "immutable" Cache-Control header).
  
  This is the standard modern frontend build approach
  (Webpack, Vite generate hashed filenames).

For non-versioned content (API responses):
  CDN purge API: invalidate specific URLs on deploy.
  Cloudflare: POST /zones/{zone}/purge_cache
  CloudFront: create invalidation batch
  Takes 30 seconds to 1 minute to propagate globally.
```

**EDGE COMPUTING:**
```
Modern CDNs run code at edge nodes.

Use cases:
  - Authentication at edge (before origin sees request)
  - A/B testing (serve different content per user bucket)
  - Geo-blocking (check IP country, deny if restricted)
  - Request transformation (add/remove headers)
  - Bot detection (challenge suspicious requests)
  
Benefits:
  - Code runs in same PoP as the user. ~0ms overhead.
  - Scales with CDN (200+ PoPs automatically).
  - Reduces origin load (many requests handled at edge).
  
Tools: Cloudflare Workers, Fastly Compute@Edge,
       AWS Lambda@Edge, Vercel Edge Functions.
```

---

### 🧪 Thought Experiment

**CDN vs. No CDN: Video Streaming**

A video streaming service: 1M concurrent viewers.
Average bitrate: 5 Mbps. Total bandwidth: 5 Tbps.

Without CDN:
  All 5 Tbps from one data center.
  A single 100 Gbps uplink costs ~$10,000/month.
  Need 50 × 100 Gbps uplinks = $500,000/month.
  Network latency for Japan/Europe: 150-200ms.
  Buffering, quality degradation for distant users.

With CDN (e.g., CloudFront):
  Content cached at 400+ PoPs globally.
  Each PoP handles its geographic region.
  Data center: serves CDN origin requests only (5-10%
  of traffic = most CDN hits are served from cache).
  Bandwidth to CDN: 500 Gbps. Cost: ~$50,000/month.
  Bandwidth from CDN to users: CDN's cost, priced
  per TB transferred. ~$0.01-0.05/GB at scale.

  10x cost reduction + better global latency.

---

### 🧠 Mental Model / Analogy

> A CDN is like a franchise system:
>
> The original restaurant (origin) creates the recipe.
> Franchises (edge nodes) in every city cook the same
> meal for local customers.
> Customers go to their local franchise (low latency),
> not to the original restaurant on the other side
> of the country.
>
> When the recipe changes (cache invalidation):
> the franchise is notified and updates its version.
> Until then: the local version may be slightly old
> (replication lag / CDN TTL).

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A CDN stores copies of your website's files (images,
videos, code) on servers near your users around the
world. When a user in Japan visits your site, they
download files from a nearby server in Japan, not from
a server in the US. Much faster.

**Level 2 - How to use it (junior developer):**
Upload static assets to a CDN or configure CloudFront
in front of your S3 bucket. Set appropriate Cache-Control
headers: long TTL (1 year) for versioned assets, short TTL
for dynamic content. Use content-hash filenames for assets
that change (JS/CSS). Set Cache-Control: private for user-
specific responses.

**Level 3 - How it works (mid-level engineer):**
CDN reads Cache-Control headers to determine TTL. On miss:
fetches from origin, caches at the PoP. On hit: serves
from cache. CDN cache key: URL + selected headers. Strip
user-specific cookies from CDN requests for public content.
Cache invalidation: content-hash versioning (recommended)
or CDN purge API (slower). Edge computing (Lambda@Edge,
Workers) for auth, geo-blocking, A/B testing.

**Level 4 - Why it was designed this way (senior/staff):**
CDNs use anycast routing: the CDN domain resolves to
different IP addresses based on the user's geographic
location (or network proximity). The same hostname
(cdn.example.com) points to Tokyo for Japanese users
and Frankfurt for European users. This is transparent
to the application. The CDN is also a security layer:
it absorbs DDoS attacks (volumetric attacks are
distributed across 200+ PoPs, each with massive
bandwidth). Many CDNs provide WAF (Web Application
Firewall) to filter malicious requests before they
reach the origin. An attack that overwhelms a 10 Gbps
origin server is a small fraction of a CDN's total
capacity (tens of Tbps globally).

**Level 5 - Mastery (distinguished engineer):**
Netflix's Open Connect appliances are a proprietary CDN
embedded directly into ISP networks. When you watch
Netflix, the video comes from an Open Connect appliance
installed inside your ISP's data center - one hop away.
This is the ultimate CDN architecture: zero external
network traversal for the video stream. Netflix pre-
populates the most popular content on each appliance
nightly (proactive caching, not reactive on cache miss).
This requires predicting what users in each region will
watch tomorrow (ML-driven content prediction). For most
companies, commercial CDNs (CloudFront, Cloudflare, Fastly)
provide sufficient performance at much lower operational
complexity.

---

### ⚙️ How It Works (Mechanism)

```
┌──────────────────────────────────────────────────────┐
│ CDN REQUEST FLOW                                    │
│                                                      │
│ User (Paris) → DNS lookup: example.com             │
│ CDN anycast → resolves to Paris PoP IP            │
│                                                      │
│ Request → Paris CDN Edge                          │
│   Check cache key: /images/logo.png               │
│   HIT → return cached image (< 5ms)              │
│   MISS:                                            │
│     Forward to origin: us-east-1.example.com     │
│     Response: Cache-Control: public, max-age=31536000│
│     Cache at Paris PoP. Return to user.           │
│                                                      │
│ [HTTP Headers for CDN Control]                     │
│   # Cache for 1 year, immutable:                  │
│   Cache-Control: public, max-age=31536000,        │
│                  immutable                        │
│                                                      │
│   # Never cache (user-specific):                  │
│   Cache-Control: private, no-store                │
│                                                      │
│   # Serve stale while revalidating (background):  │
│   Cache-Control: stale-while-revalidate=3600      │
└──────────────────────────────────────────────────────┘
```

---

### 💻 Code Example

**Example 1 - Cache-Control headers (FastAPI)**
```python
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Static assets: long TTL + content-hash in filename
# Frontend build creates: /static/app.a1b2c3d4.js
# Cache-Control: public, max-age=31536000, immutable
app.mount("/static", StaticFiles(directory="static"),
          name="static")

# Public API: short TTL for CDN caching
@app.get("/api/products")
async def get_products(response: Response):
    products = fetch_product_catalog()
    response.headers["Cache-Control"] = (
        "public, max-age=300, "  # 5 minutes at CDN
        "stale-while-revalidate=60"  # Serve stale 60s
    )                             # while fetching fresh
    return products

# Private data: never cache at CDN
@app.get("/api/orders/{user_id}")
async def get_orders(user_id: str, response: Response):
    response.headers["Cache-Control"] = (
        "private, no-store")  # Browser can cache; CDN: NO
    return fetch_user_orders(user_id)

# Streaming API: never cache
@app.get("/api/notifications/stream")
async def stream_notifications(response: Response):
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    # ... SSE streaming

# WRONG: no Cache-Control headers = CDN caches by
# its own defaults (may cache user-specific data!)
@app.get("/api/cart_bad")
async def get_cart_bad(user_id: str):
    # No Cache-Control: CDN may cache this!
    # User A's cart gets served to User B. Privacy breach.
    return fetch_cart(user_id)
```

**Example 2 - CDN invalidation on deploy**
```python
import boto3
import os

def invalidate_cloudfront_cache(distribution_id: str,
                                  paths: list = None):
    """
    Invalidate CloudFront cache on deploy.
    Use sparingly: invalidations cost money and
    degrade CDN performance (cache misses).
    Prefer content-hash versioning.
    """
    if paths is None:
        # Only invalidate API responses, not static assets
        # Static assets are versioned by hash (no invalidation needed)
        paths = ["/api/products*", "/api/trending*"]
    
    client = boto3.client("cloudfront")
    client.create_invalidation(
        DistributionId=distribution_id,
        InvalidationBatch={
            "Paths": {
                "Quantity": len(paths),
                "Items": paths
            },
            "CallerReference": str(os.urandom(8).hex())
        }
    )
    print(f"Invalidation submitted for: {paths}")

# Called during deployment pipeline:
# After deploying new API: invalidate cached API responses
# Static assets: no invalidation needed (new hash = new URL)
```

---

### ⚖️ Comparison Table

| Content Type | Cache at CDN? | TTL | Versioning |
|---|---|---|---|
| **Images, videos** | Yes | 1 year | Content hash in filename |
| **JS/CSS bundles** | Yes | 1 year | Content hash in filename |
| **Public API responses** | Yes | 1-60 min | CDN purge on deploy |
| **User-specific API** | NO | - | - |
| **HTML pages (public)** | Carefully | 1-5 min | CDN purge on deploy |
| **HTML (personalized)** | NO | - | - |
| **Payment pages** | NO | - | - |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| CDN only speeds up static assets | Modern CDNs are programmable. They can cache API responses, authenticate users at the edge, run A/B tests, block malicious traffic, redirect URLs, and serve entire server-rendered pages. Treating the CDN as "just a file server" leaves significant performance and cost savings on the table. Well-designed APIs with proper Cache-Control headers can have 90%+ of reads served from CDN. |
| A CDN is a security feature | CDNs provide some security (DDoS mitigation, WAF) but are not a substitute for proper security. Your origin server must still validate authentication, authorization, and inputs for every request that reaches it. A CDN can be misconfigured to forward authenticated requests without proper validation. Always assume some requests will reach your origin bypassing the CDN. |
| CDN purge is instant | CDN cache invalidation is NOT instant. It typically takes 30 seconds to 2 minutes to propagate globally across all PoPs. Users who hit a PoP before the invalidation arrives will still get stale content. For content where this delay is unacceptable (breaking news, stock prices), use very short TTLs (30-60 seconds) or serve directly from origin without CDN caching. |

---

### 🚨 Failure Modes & Diagnosis

**Caching Authenticated User Data at CDN**

**Symptom:**
User A logs into the application. User B logs in
on the same browser or from the same IP. User B sees
User A's profile page, cart, or private data.
Privacy breach. Potentially regulatory violation.

**Root Cause:**
An API endpoint or page that returns user-specific
data is missing the `Cache-Control: private` header.
The CDN cached the first user's response and served it
to subsequent users requesting the same URL.

**Fix - Audit Cache-Control on all endpoints:**
```python
import functools
from fastapi import Response

def no_cdn_cache(route_handler):
    """
    Decorator: force no-CDN-cache on user-specific endpoints.
    Apply to ALL endpoints that return user-specific data.
    """
    @functools.wraps(route_handler)
    async def wrapper(*args, **kwargs):
        response = Response()
        result = await route_handler(*args, **kwargs,
                                      response=response)
        response.headers["Cache-Control"] = (
            "private, no-store, no-cache, max-age=0")
        response.headers["Pragma"] = "no-cache"
        return result
    return wrapper

@app.get("/api/users/me")
@no_cdn_cache
async def get_current_user(
        current_user: dict = Depends(get_current_user)):
    return current_user

# Automated check: in CI/CD pipeline, verify that all
# authenticated endpoints have Cache-Control: private.
# Missing headers = build failure.
```

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `What is a Cache (Conceptual)` - CDN is a type of
  cache; understanding cache fundamentals (TTL,
  eviction, hit rate) is essential

**Builds On This (learn these next):**
- `Load Balancing` - CDN distributes at the geographic
  level; load balancing distributes at the service level
- `Caching (System Design)` - in-depth caching patterns
  beyond CDN (application-level, distributed caches)
- `Video Streaming Design` - CDN is the core delivery
  mechanism for streaming platforms

---

### 📌 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│ CORE IDEA   │ Copy content near users. Less distance =  │
│             │ less latency. Origin load reduced 90%+.  │
├─────────────┼──────────────────────────────────────────┤
  │
│ WHAT TO CACHE│ Public, static, non-user-specific.       │
│              │ Images, JS/CSS, public API responses.   │
├─────────────┼──────────────────────────────────────────┤
  │
│ NEVER CACHE │ User-specific data.                       │
│             │ Cache-Control: private, no-store          │
├─────────────┼──────────────────────────────────────────┤
  │
│ VERSIONING  │ Hash in filename: /app.abc123.js         │
│             │ New hash = new URL = cache miss = fresh. │
├─────────────┼──────────────────────────────────────────┤
  │
│ INVALIDATION│ Purge API (30-120s lag) or versioning.  │
│             │ Not instant. Short TTL for dynamic data. │
├─────────────┼──────────────────────────────────────────┤
  │
│ SECURITY    │ Private header = most important safety.  │
│             │ Missing = privacy breach.                │
├─────────────┼──────────────────────────────────────────┤
  │
│ ONE-LINER   │ "Cache at edge. Public=yes. Private=no. │
│             │  Version assets. Purge on deploy."      │
├─────────────┼──────────────────────────────────────────┤
  │
│ NEXT        │ Connection Pooling (System Design)        │
└─────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. CDN = caches near users. Public, non-user-specific
   content (images, JS, public APIs): cache at CDN.
   User-specific content (cart, orders, account): never
   cache at CDN (always send `Cache-Control: private`).
2. Version static assets by content hash (Webpack/Vite
   do this automatically). Hashed filename = new URL on
   change = cache miss = always fresh, without needing
   explicit cache invalidation.
3. CDN invalidation is not instant (30-120 seconds to
   propagate globally). For rapidly-changing content:
   use short TTLs (1-5 minutes) or avoid CDN caching.
   For static assets: never need to invalidate (use
   content-hash versioning).

**Interview one-liner:**
"CDN: edge servers globally cache content near users. Static assets (images,
JS/CSS): Cache-Control: public, max-age=31536000, immutable (versioned by content
hash - new hash = new URL = fresh from origin without invalidation). Public API
responses: short TTL (1-60 min) with CDN purge on deploy. User-specific data:
Cache-Control: private, no-store (never cached at CDN - privacy breach risk).
CDN also handles TLS termination at edge, DDoS mitigation, and WAF. Edge computing
(Workers, Lambda@Edge) runs auth/A/B testing at edge PoP."
