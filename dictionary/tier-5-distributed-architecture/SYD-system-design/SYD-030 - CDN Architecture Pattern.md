---
id: SYD-030
title: CDN Architecture Pattern
category: System Design
tier: tier-5-distributed-architecture
folder: SYD-system-design
difficulty: ★★☆
depends_on: SYD-005, SYD-006
used_by:
related: SYD-031
tags:
  - architecture
  - performance
  - intermediate
  - networking
status: complete
version: 4
layout: default
parent: "System Design"
grand_parent: "Technical Dictionary"
nav_order: 30
permalink: /system-design/cdn-architecture-pattern/
---

# SYD-030 - CDN Architecture Pattern

⚡ TL;DR - A CDN replicates your content to edge
servers worldwide so users download from a nearby
node instead of traversing the globe to your origin.

| #030            | Category: System Design              | Difficulty: ★★☆ |
| :-------------- | :----------------------------------- | :-------------- |
| **Depends on:** | What is Scalability, What is a Cache |                 |
| **Used by:**    | -                                    |                 |
| **Related:**    | Connection Pooling (System Design)   |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A user in Tokyo loads your product page. Your servers
are in Virginia. The HTTP request travels ~14,000 km
each way. At the speed of light, the theoretical
minimum round-trip time is ~93ms. With network hops,
TLS handshake, TCP slow start, and server processing,
realistic latency is 300-600ms per page load. A 2MB
JavaScript bundle takes 4-8 seconds. Studies show
that a 100ms increase in load time drops e-commerce
conversion rate by ~1%. Your Virginia-hosted site is
losing 30-50% of its revenue from the Tokyo market
simply due to physics.

**THE BREAKING POINT:**
The breaking point is not just user experience.
During a product launch, millions of users worldwide
simultaneously hit your Virginia origin. It buckles
under the combined load. International users see
failures while US users experience degraded service.

**THE INVENTION MOMENT:**
"This is exactly why CDN architecture was created" -
move content as close to the user as possible, so
physics cannot be the bottleneck.

**EVOLUTION:**
Akamai (1998) pioneered commercial CDN after the
Slashdot effect repeatedly melted MIT's servers.
Early CDNs served only static files. CloudFront
(2008) integrated CDN with AWS. Cloudflare Workers
(2017) moved compute to the edge. Today's CDNs run
arbitrary code (Vercel Edge Functions, Fastly
Compute@Edge) and cache dynamic content with
granular invalidation.

---

### 📘 Textbook Definition

A **Content Delivery Network (CDN)** is a
geographically distributed network of proxy servers
(edge nodes) that cache and serve content on behalf
of an origin server. When a user requests a resource,
the CDN routes the request to the nearest edge node.
On a cache hit, the edge node serves the response
directly. On a miss, it fetches from the origin,
caches the response, and serves it. CDNs reduce
latency through physical proximity and reduce origin
load through caching.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
A CDN puts copies of your content in cities worldwide
so every user downloads from nearby.

**One analogy:**

> Amazon does not ship every product from one warehouse
> in Seattle. It maintains fulfillment centers in
> every major city. When you order in Dallas, the
> package ships from the Dallas warehouse, arriving in
> one day instead of a week. A CDN is a fulfillment
> center network for your web content.

**One insight:**
The speed of light is a hard physical constant.
No amount of software optimization can make a request
travel from Tokyo to Virginia faster than physics
allows. CDNs are one of the few latency improvements
that works by changing the laws of physics - or
rather, by shortening the distance to which they apply.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**

1. Network latency scales with physical distance.
2. Popular content is read far more than it is written.
3. HTTP responses are idempotent for the same URL.

**DERIVED DESIGN:**
Given that popular content is read many times without
changing (a product image, a JavaScript bundle), and
given that latency scales with distance, placing a
cached copy of that content near each group of users
is a direct application of the caching principle at
the network topology level.

The CDN must decide:

- **What to cache:** `Cache-Control` header drives this
- **How long to cache:** `max-age` or `s-maxage`
- **How to invalidate:** URL versioning or API purge
- **Where to route:** DNS-based or anycast routing
  to the nearest PoP (Point of Presence)

**THE TRADE-OFFS:**
**Gain:** Dramatically lower latency for global users.
Origin server load reduced by 90%+ for static assets.
DDoS mitigation by absorbing traffic at the edge.

**Cost:** Cache invalidation complexity. Stale content
risk. CDN misconfiguration can serve outdated data to
millions of users. Additional cost proportional to
traffic volume.

**ESSENTIAL vs ACCIDENTAL COMPLEXITY:**
**Essential:** Cache invalidation across hundreds of
edge nodes is inherently complex because there is no
instant global consistency.

**Accidental:** CDN vendor-specific configuration APIs
and cache key normalization rules are accidental
complexity - they vary by provider.

---

### 🧪 Thought Experiment

**SETUP:**
A JavaScript bundle (`app.js`, 1.5MB) is loaded on
every page view of a high-traffic news site.
The site has 10M daily users in 5 continents.
The bundle changes once per week.

**WHAT HAPPENS WITHOUT CDN:**
10M page views x 1.5MB = 15TB/day outbound from
the origin. Users in Asia experience 500ms+ load
time. During a major news event, origin bandwidth
is exhausted. The bundle serves slowly or times out.
Infrastructure bill explodes with cross-continent
bandwidth.

**WHAT HAPPENS WITH CDN:**
First user per day in each PoP triggers a cache miss
to the origin. The bundle is cached at 200+ edge
nodes globally. Subsequent users in each city serve
from the edge: 10-30ms latency, no origin hit.
Origin sees < 200 requests/day for the bundle.
15TB of traffic is absorbed by the CDN, not the
origin. Weekly deploy: one API call to purge.

**THE INSIGHT:**
For static content with a high read-to-write ratio,
a CDN converts a global origin-load problem into
a local edge-cache problem. The origin becomes
nearly irrelevant to the static asset delivery path.

---

### 🧠 Mental Model / Analogy

> Think of a viral YouTube video. The original video
> file lives on YouTube's primary servers. But when
> 50 million people simultaneously try to watch it,
> YouTube does not stream 50 million connections from
> one server room. It has pre-cached the video at
> edge servers in every major city. Your request goes
> to the nearest edge node, not to YouTube's origin.

Mapping:

- "YouTube's primary servers" → CDN origin server
- "Edge server in your city" → CDN PoP (edge node)
- "Pre-cached video at your local node" → cached asset
- "50 million simultaneous viewers" → high read load
- "Your request goes to nearest city" → anycast routing

**Where this analogy breaks down:** YouTube videos are
immutable after upload. Many CDN-cached resources
change (pricing, inventory). For mutable content,
cache invalidation becomes the hard problem that
this analogy does not address.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
A CDN is a service that stores copies of your website
files in cities around the world so people can
download them quickly from a nearby server.

**Level 2 - How to use it (junior developer):**
Set `Cache-Control: public, max-age=31536000` on
static assets with content-hash filenames
(`app.abc123.js`). Point your domain to the CDN.
The CDN serves assets from the nearest edge.
For cache invalidation, change the filename hash.

**Level 3 - How it works (mid-level engineer):**
CDNs use DNS-based routing: your domain CNAME points
to the CDN's DNS. The CDN's DNS resolver returns the
IP of the nearest PoP based on the user's DNS resolver
location. The PoP checks its cache. On a miss, it
fetches from origin, stores the response with the
`max-age` as TTL, and serves it. Subsequent requests
to the same PoP within the TTL window are cache hits.

**Level 4 - Why it was designed this way (senior/staff):**
CDN cache keys are (by default) the full URL including
query string. This means `example.com/api?user=1`
and `example.com/api?user=2` are cached separately -
which is correct for personalized content but wastes
cache space if query parameters do not affect the
response. Cache key normalization (stripping unused
query params, normalizing headers) is essential for
high hit ratios. Vary header (`Vary: Accept-Encoding`)
creates separate cache entries per encoding -
misuse creates cache fragmentation and drops hit ratio
to near zero.

**Level 5 - Mastery (distinguished engineer):**
Edge compute (Cloudflare Workers, Lambda@Edge) changes
the CDN from a passive cache to an active compute
platform. Authentication, A/B testing, request
routing, and personalization can run at the edge with
sub-5ms latency globally. The architectural implication
is that the origin becomes a data API; presentation
logic moves to the edge. The hard problem is state:
edge functions are stateless per-request, so any
state (user sessions, feature flags) must be read
from a distributed store with sub-millisecond access
(Cloudflare KV, Durable Objects). This creates a
new class of distributed system design challenges
at the edge.

---

### ⚙️ How It Works (Mechanism)

```
┌─────────────────────────────────────────┐
│         CDN REQUEST FLOW                │
│                                         │
│  User (Tokyo)                           │
│      │                                  │
│      │ DNS query: cdn.example.com       │
│      ▼                                  │
│  CDN DNS → returns Tokyo PoP IP         │
│      │                                  │
│      ▼                                  │
│  Tokyo Edge Node                        │
│      │                                  │
│  Cache HIT? ──YES──▶ Return (10ms)     │
│      │                                  │
│     NO                                  │
│      │                                  │
│      ▼                                  │
│  Fetch from Origin (Virginia) (300ms)   │
│      │                                  │
│  Cache response (TTL from headers)      │
│      │                                  │
│  Return to user + future users (~10ms)  │
└─────────────────────────────────────────┘
```

**Step 1 - DNS Resolution:**
User's browser queries DNS for your domain. The
CDN's Anycast or GeoDNS returns the IP address of
the nearest PoP (Point of Presence).

**Step 2 - Edge Cache Lookup:**
The PoP checks its local cache using the request URL
(and configured cache key). If found and within TTL:
cache hit - served immediately.

**Step 3 - Origin Fetch (Cache Miss):**
The PoP establishes a connection to your origin server.
Fetches the full response. Examines `Cache-Control`
response headers. If cacheable, stores in local cache.

**Step 4 - Cache Population:**
The response is stored at the edge PoP with TTL
derived from `Cache-Control: max-age` or `s-maxage`.
All subsequent requests to this PoP within TTL hit
the cache without touching the origin.

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**

```
User (Sydney) → DNS → Nearest CDN PoP
  → CDN cache lookup
      ← YOU ARE HERE (edge caching)
  → HIT: return asset (15ms)
  → MISS: fetch from US origin (250ms)
           → cache at Sydney PoP
           → return asset
```

**FAILURE PATH:**

```
CDN PoP network failure
  → CDN failover to next-nearest PoP
  → Higher latency for affected region
  → If all PoPs fail: origin fallback (if configured)
  → DDoS at origin if CDN shield is bypassed
```

**WHAT CHANGES AT SCALE:**
At 10x traffic, CDN absorbs proportionally more
origin traffic - the origin barely notices. At 100x,
CDN tier costs scale linearly. At 1000x, the CDN
bill becomes a significant infrastructure cost;
optimize by maximizing cache hit ratio and minimizing
cache-busting query parameters.

**CONCURRENCY & DISTRIBUTED IMPLICATIONS:**
CDN cache invalidation is eventually consistent.
After an API purge call, edge nodes may serve stale
content for up to 60 seconds while the purge
propagates. Design invalidation strategies that
tolerate this window (URL versioning eliminates it).

---

### 💻 Code Example

**Example 1 - Wrong vs Right: Cache headers**

```nginx
# BAD - tells CDN never to cache
# All traffic hits origin
server {
    location / {
        add_header Cache-Control "no-store";
    }
}
```

```nginx
# GOOD - immutable assets: cache 1 year
# Dynamic pages: short TTL or no cache
server {
    # Immutable: content-hashed filenames
    location ~* \.(js|css|png|woff2)$ {
        add_header Cache-Control
            "public, max-age=31536000, immutable";
    }
    # Dynamic pages: CDN can cache for 60s
    # but revalidate on every request after
    location / {
        add_header Cache-Control
            "public, max-age=60, s-maxage=60";
    }
    # Never cache API responses with user data
    location /api/user/ {
        add_header Cache-Control
            "private, no-store";
    }
}
```

**Example 2 - Cache invalidation via URL versioning**

```html
<!-- BAD - static filename, must purge CDN on deploy -->
<script src="/static/app.js"></script>

<!-- GOOD - content-hashed filename
     old and new versions can coexist in CDN
     Deploying new version just changes the hash -->
<script src="/static/app.abc123ef.js"></script>
```

```python
# Django WhiteNoise / webpack: generate hashed names
# Build step produces:
#   app.abc123ef.js -> set Cache-Control max-age=1year
# No CDN purge needed on deploy
# Old URL still valid (for users on old page)
# New URL immediately served from edge on first access
```

**Example 3 - Production: CloudFront CDN configuration**

```json
{
  "CacheBehaviors": [
    {
      "PathPattern": "/static/*",
      "CachePolicyId": "immutable-assets-1year",
      "Compress": true,
      "ViewerProtocolPolicy": "redirect-to-https"
    },
    {
      "PathPattern": "/api/*",
      "CachePolicyId": "no-cache-private",
      "AllowedMethods": [
        "GET",
        "HEAD",
        "OPTIONS",
        "PUT",
        "POST",
        "PATCH",
        "DELETE"
      ]
    }
  ]
}
```

---

### ⚖️ Comparison Table

| Feature            | Cloudflare   | CloudFront      | Fastly          | Akamai      |
| ------------------ | ------------ | --------------- | --------------- | ----------- |
| **Edge Compute**   | Workers (V8) | Lambda@Edge     | Compute@Edge    | EdgeWorkers |
| DDoS Protection    | Built-in     | Extra cost      | Add-on          | Built-in    |
| Cache Invalidation | Instant      | ~60s            | Instant         | Minutes     |
| Price Model        | Flat/usage   | Pay-per-request | Pay-per-request | Enterprise  |
| Best For           | General web  | AWS integration | Real-time logic | Enterprise  |

**How to choose:** Cloudflare for general web apps
and DDoS protection. CloudFront when your origin is
on AWS and you want tight integration. Fastly for
applications requiring instant purge and Varnish-like
control.

**Decision Tree:**

- Origin on AWS? → CloudFront first
- Need instant cache purge? → Fastly or Cloudflare
- Need edge compute globally? → Cloudflare Workers
- Enterprise SLA required? → Akamai

---

### ⚠️ Common Misconceptions

| Misconception                        | Reality                                                                                                                                                                                    |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| CDN only works for static files      | Modern CDNs cache dynamic content and run compute at the edge. API responses with appropriate Cache-Control are cached.                                                                    |
| CDN purge is instant                 | Purge propagation takes 30-120 seconds depending on the CDN. Use URL versioning for zero-stale-risk deploys.                                                                               |
| CDN eliminates origin entirely       | Origin still handles cache misses, dynamic content, and authenticated requests. It is reduced to 5-10% of total traffic for static assets.                                                 |
| Vary: Accept-Encoding is safe to set | Vary header creates multiple cache variants per URL. With Accept-Encoding, browsers send many variants, fragmenting the cache and destroying hit ratio. Use CDN-level compression instead. |
| HTTPS is slower with CDN             | Modern CDNs maintain persistent TLS connections to origin. TLS handshake overhead is absorbed by the edge; users pay it only once.                                                         |

---

### 🚨 Failure Modes & Diagnosis

**Cache Stampede on CDN Cold Start**

**Symptom:**
After a CDN purge or new deployment, origin CPU
spikes massively for 2-5 minutes. Cache miss rate
is 100%. Origin overwhelmed.

**Root Cause:**
All edge nodes have empty caches. The first requests
from every PoP simultaneously go to origin. With
200+ PoPs, origin receives 200x the normal miss
traffic at once.

**Diagnostic Command / Tool:**

```bash
# CloudFront: check cache miss rate after deploy
aws cloudwatch get-metric-statistics \
  --namespace AWS/CloudFront \
  --metric-name CacheMissRate \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T01:00:00Z \
  --period 60 \
  --statistics Average
```

**Fix:**
CDN "shield" or "origin shield" - designate one
regional PoP as the only node that contacts origin.
All other PoPs request from the shield PoP. This
collapses 200 simultaneous origin requests to 1.

**Prevention:**
Enable origin shield on CloudFront. Use Fastly's
shielding feature. Or use URL versioning to avoid
full purges.

---

**Serving Stale Private Content**

**Symptom:**
User A logs out. User B logs in on the same device.
User B sees User A's profile page, which was cached
by the CDN.

**Root Cause:**
Personalized or authenticated content was cached by
the CDN because the `Cache-Control` header was
missing or set to `public` in error.

**Diagnostic Command / Tool:**

```bash
# Check CDN response headers for a private page
curl -I https://example.com/profile/123 \
  | grep -i "cache-control\|age\|x-cache"
# "Age: 3600" means CDN served it from cache!
```

**Fix:**
Set `Cache-Control: private, no-store` on all
authenticated/personalized responses. Never let
them reach a shared CDN cache.

**Prevention:**
Default all authenticated routes to `private`.
Explicitly opt-in static resources to `public`.

---

**High Miss Rate Due to Cache Key Fragmentation**

**Symptom:**
CDN hit ratio is below 50% despite serving the
same content. CDN bill is unexpectedly high. Origin
load is high.

**Root Cause:**
Cache key includes query parameters that vary but
do not change the response (analytics tokens, UTM
parameters, session IDs).

**Diagnostic Command / Tool:**

```bash
# Log CDN cache key to identify fragmentation
# CloudFront: add x-forwarded-for to cache key?
# Check access logs for unique URLs vs total requests
aws s3 cp s3://cloudfront-logs/access.log . \
  | awk '{print $8}' | sort | uniq -c | sort -rn \
  | head -20
```

**Fix:**
Configure CDN to strip non-functional query params
from the cache key: UTM parameters, `fbclid`, etc.

**Prevention:**
Define explicit cache key rules in CDN configuration.
Whitelist query params that affect content; strip all
others from the cache key.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `What is a Cache` - CDN is caching applied at the
  network topology level; cache hit/miss mechanics
  are identical
- `What is Scalability` - CDN is one of the most
  cost-effective global read scaling tools available

**Builds On This (learn these next):**

- `Cache Invalidation Strategies` - how to safely
  update CDN-cached content without serving stale
  data to users
- `Edge Computing` - running application logic at
  CDN edge nodes, beyond simple caching

**Alternatives / Comparisons:**

- `Reverse Proxy (Nginx/Varnish)` - single-region
  caching without geographic distribution
- `Database Read Replicas` - read scaling for data
  rather than static assets and page content

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Geographically distributed cache network  │
│              │ that serves content from nearest edge node│
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Physics: light speed creates unavoidable  │
│ SOLVES       │ latency for global users hitting one origin│
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ For static assets with a long TTL, the    │
│              │ origin becomes nearly irrelevant to reads  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Serving global users; high read-to-write  │
│              │ ratio; static assets; DDoS protection      │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Content is always unique per user;        │
│              │ responses must never be shared between users│
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Caching authenticated responses in shared  │
│              │ CDN cache (user data leakage)              │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Low global latency vs cache invalidation   │
│              │ complexity and stale content risk          │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Serve from the nearest city, not the     │
│              │  nearest continent."                       │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Cache Invalidation → Edge Compute → DNS   │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**

1. CDN moves content physically closer to users;
   physics is the problem being solved.
2. Never cache authenticated/private content in a
   shared CDN - it is a security vulnerability.
3. URL versioning (content-hashed filenames) is the
   cleanest cache invalidation strategy for CDNs.

**Interview one-liner:**
"A CDN distributes content to edge nodes globally,
so users get files from a nearby server rather than
your origin. It reduces latency and origin load for
static assets. The key trade-off is cache invalidation:
for static files I use URL versioning with long TTLs;
for dynamic content I use short TTLs or no caching,
and I never cache responses with user-specific data."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
"Move data to the consumer, not the consumer to
the data." CDNs, database read replicas, and L1/L2
CPU caches all apply this principle at different
layers. Geographic distribution is the CDN's unique
contribution.

**Where else this pattern appears:**

- DNS caching - IP addresses are cached near the
  resolver so DNS does not travel to root servers
  for every lookup
- Browser cache - assets are stored locally so
  subsequent visits do not download them at all
- Replica databases in geographic regions - data
  close to read users rather than all on one server

**Industry applications:**

- Streaming platforms (Netflix Open Connect) -
  Netflix ISP-embedded servers store popular content
  inside ISPs so video streams never leave the ISP
  network
- Gaming (Xbox, PlayStation CDN) - game patches
  distributed to regional CDN nodes so 50 million
  users can download simultaneously

---

### 💡 The Surprising Truth

A CDN's most important job is often not content
delivery - it is DDoS absorption. Cloudflare regularly
absorbs attacks measured in terabits per second on
behalf of customers. The reason CDN infrastructure
can handle this is exactly the same property that
makes it good at delivery: distributed edge nodes
each absorb a fraction of the attack traffic and
the origin never sees it. The world's largest DDoS
defense infrastructure is commercially available
for $20/month because it was built to solve content
delivery and DDoS mitigation are two sides of the
same architectural coin.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**

1. [EXPLAIN] Explain why a CDN reduces latency for
   Tokyo users accessing a US-hosted site using
   only physics and the concept of data locality.
2. [DEBUG] Given a CDN hit ratio of 30% for a news
   site, identify the top 3 likely causes of low
   hit ratio and the diagnostic approach for each.
3. [DECIDE] Given authenticated user profile pages
   that are the same for all staff but unique per
   customer, decide which path is CDN-safe and
   which must be `Cache-Control: private`.
4. [BUILD] Configure Nginx Cache-Control headers
   for a web app with three asset types: static
   JS/CSS, dynamic HTML pages, and authenticated
   API responses.
5. [EXTEND] Design a CDN cache invalidation strategy
   for a news site where breaking news articles
   update every 5 minutes and must reflect updates
   within 10 seconds globally.

---

### 🧠 Think About This Before We Continue

**Q1.** A news site uses a CDN with a 1-hour TTL for
article HTML. A breaking news story is published.
How do users in different PoPs see the update at
different times? What is the maximum delay, and how
do you reduce it to under 5 seconds without disabling
caching entirely?
_Hint: Consider purge APIs, short TTL strategies,
and surrogate keys (tags) for invalidation._

**Q2.** Your CDN hit ratio drops from 85% to 40%
after a marketing campaign starts appending UTM
parameters to all URLs (`?utm_source=google`).
The content is identical regardless of UTM params.
How do you restore the hit ratio without removing
analytics tracking?
_Hint: Think about cache key normalization and
query parameter stripping._

**Q3.** [HANDS-ON] Configure a Cloudflare Worker
that adds a `X-Request-Country` header to every
response based on the edge's geographic location,
without touching the origin server. What are the
latency and cost implications of this approach
vs. adding the same header in your origin?
_Hint: Compare cold start latency, edge-to-origin
round trips, and per-request pricing._

---

### 🎯 Interview Deep-Dive

**Q1: Where would you place a CDN in a system
design and what types of content should it cache?**
_Why they ask:_ Tests understanding of CDN role
in the overall architecture.
_Strong answer includes:_

- CDN sits between DNS and origin: DNS CNAME points
  to CDN, which routes to origin on miss.
- Cache: static assets (JS, CSS, images) with
  content-hash URLs and 1-year TTL.
- Optionally: dynamic HTML with short TTL (60s)
  for public pages.
- Never cache: authenticated API responses, user
  session data, payment pages.

**Q2: How would you handle cache invalidation for
a CDN serving a large e-commerce product catalog
where prices change several times per day?**
_Why they ask:_ Tests understanding of CDN trade-offs
for mutable content.
_Strong answer includes:_

- Option 1: Short TTL (5-30 minutes). Simple but
  still serves stale prices for up to TTL window.
- Option 2: API purge on price change. Instant but
  requires CDN API calls from pricing service.
- Option 3: Surrogate keys - tag all product pages
  with their product ID. Purge by tag on price change.
- Option 4: Client-side price fetching - cache the
  page, fetch price via uncached API call from JS.

**Q3: What is the security risk of misconfiguring
CDN caching for authenticated content?**
_Why they ask:_ Tests security awareness in
infrastructure decisions.
_Strong answer includes:_

- If an authenticated page (user profile, order
  history) is cached by a CDN without `Cache-Control:
private`, the first user's response is cached and
  served to the next user who requests the same URL.
- Real incident: Bank of America cached account
  balance pages briefly (hypothetical illustration).
- Fix: default all authenticated routes to `private`.
  CDN should only cache public, non-personalized
  content. Verify with automated header checks
  in CI/CD pipeline.
