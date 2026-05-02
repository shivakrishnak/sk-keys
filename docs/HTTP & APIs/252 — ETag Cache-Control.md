---
layout: default
title: "ETag / Cache-Control"
parent: "HTTP & APIs"
nav_order: 252
permalink: /http-apis/etag-cache-control/
number: "0252"
category: HTTP & APIs
difficulty: ★★☆
depends_on: HTTP, REST, API Caching
used_by: REST APIs, CDN, Browser Caching
related: API Caching, HTTP Headers, Content Negotiation
tags:
  - etag
  - cache-control
  - http-caching
  - conditional-requests
  - intermediate
---

# 252 — ETag / Cache-Control

⚡ TL;DR — `ETag` is a response header containing a hash/fingerprint of the resource content (enabling conditional requests that return `304 Not Modified` with no body when content is unchanged), while `Cache-Control` is the master directive that tells browsers, CDNs, and proxies how long to cache a response and under what conditions — together they form the two-layer HTTP caching mechanism: TTL-based freshness and validation-based reuse.

| #252 | Category: HTTP & APIs | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | HTTP, REST, API Caching | |
| **Used by:** | REST APIs, CDN, Browser Caching | |
| **Related:** | API Caching, HTTP Headers, Content Negotiation | |

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A JavaScript app polls `GET /api/dashboard` every 30 seconds. The dashboard data
changes maybe once every 5 minutes. Without any caching: every 30-second poll hits
the server full force, fetches 50KB of JSON, returns it in full — even when the
data is completely identical to the last response. The user's browser is downloading
the same 50KB repeatedly. The server is querying the database every 30 seconds per
user for unchanged data. At 10,000 concurrent users: 10,000 DB queries every 30 seconds,
each returning identical data.

**THE INVENTION MOMENT:**
HTTP `If-Modified-Since` appeared in HTTP/1.0. ETags and `Cache-Control` were formalized
in HTTP/1.1 (RFC 2068, 1997) to address the limitations of pure time-based freshness:
file timestamps can be unreliable (copied files, clock drift), and `Expires` absolute-time
header relies on synchronized clocks between server and client. ETags solve this with
content fingerprinting: if the content hash hasn't changed, return 304 (nothing to download).
The result: zero bandwidth for unchanged resources.

---

### 📘 Textbook Definition

**ETag** (Entity Tag) is an HTTP response header containing a server-generated opaque
string (typically a content hash or version identifier) that uniquely identifies the
current version of a resource. Clients store the ETag and include it in subsequent
requests via `If-None-Match` (for GETs) or `If-Match` (for conditional writes).
If the resource's ETag matches, the server returns `304 Not Modified` with no response
body, saving bandwidth. **Cache-Control** is the HTTP/1.1 response (and request) header
that specifies caching directives: `max-age=N` (freshness TTL in seconds), `public`/
`private` (cache scope), `no-cache` (always revalidate), `no-store` (never cache),
`s-maxage=N` (shared/CDN-specific TTL), `immutable` (never revalidate before expiry),
`stale-while-revalidate=N` (serve stale while fetching fresh asynchronously).

---

### ⏱️ Understand It in 30 Seconds

**One line:**
`Cache-Control` says "don't ask me again for 5 minutes"; `ETag` says "if you ask again,
here's a fingerprint — I'll only send new data if it changed."

**One analogy:**

> ETag is like a document revision number.
> When you download a legal document and return next week for updates:
> "I have revision 47. Do you have anything newer?"
> "No — still revision 47. Nothing to download." (304 Not Modified)
> "Yes — it's revision 48 now. Here's the new version." (200 OK + full body)
> Cache-Control tells you how long to wait before even checking (max-age).

**One insight:**
ETag and Cache-Control serve different purposes that COMPLEMENT each other:
`Cache-Control: max-age=3600` means "don't ask for 1 hour."
After 1 hour, the cache is stale. Now ETag kicks in: "I'll ask but with `If-None-Match`,
so if content is unchanged you don't have to resend the body." Together: reduced requests (max-age) + reduced bandwidth on revalidation (ETag).

---

### 🔩 First Principles Explanation

**THE TWO LAYERS OF HTTP CACHING:**

```
LAYER 1 — FRESHNESS (Cache-Control: max-age):
  Server: "This response is valid for max-age seconds. Don't ask again until then."
  Client: stores response + records when it expires
  During TTL: serves from cache without any network request
  After TTL: proceeds to Layer 2 revalidation

LAYER 2 — REVALIDATION (ETag + If-None-Match):
  Client: "I have this resource with fingerprint X. If still X, skip the body."
  Server: computes current fingerprint
  If unchanged: 304 Not Modified (no body — zero bandwidth)
  If changed: 200 OK + new body + new ETag

Combined lifecycle:
  Time 0:    GET /api/data
             ← 200 OK, Cache-Control: max-age=300, ETag: "abc123", Body: {...}
  0-300s:    All requests → served from cache, no network
  300s:      Cache expired
             GET /api/data, If-None-Match: "abc123"
  If same:   ← 304 Not Modified (no body)  → update cache expiry, reuse body
  If changed:← 200 OK, ETag: "def456", new Body: {...}
```

**ETAG TYPES:**

```
STRONG ETag:  ETag: "abc123"
  Semantics: byte-for-byte identical response
  Matches: ONLY if exactly the same content (byte-level)
  Use for: most REST API resources

WEAK ETag:   ETag: W/"abc123"
  Semantics: semantically equivalent (same content, potentially different encoding)
  Matches: if semantically equivalent (e.g., same JSON with gzip vs no gzip)
  Use for: when Content-Encoding varies, or JSON field ordering may differ

CONDITIONAL WRITE (optimistic locking):
  GET /api/users/1 → ETag: "v5"

  PUT /api/users/1
  If-Match: "v5"        ← only update if still on version 5
  Body: { updated data }

  If resource still at version 5: 200 OK (update applied)
  If resource changed to v6 by someone else: 412 Precondition Failed
  → Prevents lost-update problem (optimistic locking via HTTP)
```

**CACHE-CONTROL DIRECTIVE MATRIX:**

```
Scenario                      → Directive
────────────────────────────────────────────────────────────────
Public API (product catalog)  → public, max-age=600, s-maxage=86400
User-specific (shopping cart) → private, max-age=60
Auth tokens / secrets         → no-store
Real-time data (stock price)  → no-cache (always revalidate)
  or                          → max-age=0, must-revalidate
Immutable versioned asset     → public, max-age=31536000, immutable
  (app.a1b2c3d4.js)
Paginated list (changes)      → public, max-age=60, stale-while-revalidate=30
```

---

### 🧪 Thought Experiment

**SCENARIO:** GitHub API response — list of pull requests.

```
REQUEST:
  GET /repos/user/repo/pulls HTTP/1.1
  Authorization: Bearer ghp_token123
  If-None-Match: "844ca96c0e4e3feea987"   ← ETag from previous response

NO NEW PRS (unchanged):
  HTTP/1.1 304 Not Modified
  ETag: "844ca96c0e4e3feea987"
  Cache-Control: private, max-age=60, must-revalidate
  X-RateLimit-Remaining: 4999
  X-Poll-Interval: 60
  → Zero body transfer. Browser uses cached response body.
  → Rate limit consumed (1 request used), but bandwidth = 0

NEW PR OPENED (changed):
  HTTP/1.1 200 OK
  ETag: "a2c4e6f8b0d2e4f6a8c0"   ← NEW ETag
  Cache-Control: private, max-age=60
  Content-Length: 4523
  → Full 4523-byte body returned with the new PR included

INSIGHT: GitHub's API uses ETag extensively.
  Callers polling the API MUST include If-None-Match from previous response
  to avoid unnecessary bandwidth + rate limit impact.
  New PR data fetched only when something actually changed.
```

---

### 🧠 Mental Model / Analogy

> ETag is like a book's ISBN — a unique fingerprint for the exact edition.
> Cache-Control's max-age is your bookshelf's "use-by date."
> If you shelved "revision 1.0.2" and today's max-age expired:
> you don't throw the book away and buy a new one (wasteful).
> You check: "Still ISBN 1.0.2?" → "Yes" → 304: keep reading your copy.
> "No, it's now ISBN 1.0.3" → 200: here's the new edition.
> The max-age prevents even going to the bookstore unnecessarily.
> The ISBN check prevents downloading an identical copy unnecessarily.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
`Cache-Control` tells your browser "don't bother checking for 5 minutes." After that,
`ETag` says "here's a fingerprint of what you have — the server only sends new data
if it actually changed." Together they minimize both requests and data transfer.

**Level 2 — How to use it (junior developer):**
In Spring MVC: use `ResponseEntity.ok().cacheControl(CacheControl.maxAge(...))` to set
`Cache-Control`. Use `webRequest.checkNotModified(etag)` to handle ETag-based conditional
requests — Spring automatically returns `304 Not Modified` when ETag matches. Compute
ETag as a hash of the response body or as a database version/timestamp.

**Level 3 — How it works (mid-level engineer):**
ETag computation tradeoffs: option A — hash the serialized response body (accurate but
requires serialization even on 304); option B — use a DB `version` column or `updated_at`
timestamp (faster, doesn't require full serialization). Strong vs weak ETags: use weak
ETags when responses may differ in encoding (gzip) but are semantically identical — prevents
CDNs from caching different compressed versions as different resources. The `Vary: Accept-Encoding`
header combined with this: tells caches to maintain separate cache entries per encoding.
For conditional writes: `If-Match` enables optimistic locking — atomic "compare and update"
via HTTP, replacing application-level version conflict detection.

**Level 4 — Why it was designed this way (senior/staff):**
The ETags + Cache-Control design represents HTTP's progressive disclosure model: simple
cases (just Cache-Control max-age) work without ETags; advanced optimization (304 responses)
adds ETags. The decision to use opaque strings rather than timestamps was deliberate —
timestamps are fragile (clock skew, same-second changes). Content hashes are correct but
expensive on server. The `W/` weak ETag prefix was added to address the real-world problem
of CDNs serving gzip vs identity, where byte-identical content produces different encoding
variants. The `immutable` directive (RFC 8246) represents the correct answer for cache-
busted static assets: when the URL encodes the content hash (app.a1b2c3.js), the content
will never change for that URL — `immutable` tells browsers to never even attempt
revalidation during the max-age window, eliminating conditional requests entirely for
assets that can't change.

---

### ⚙️ How It Works (Mechanism)

```
SPRING MVC ETAG HANDLING — FULL EXAMPLE:

@GetMapping("/api/v1/products/{id}")
public ResponseEntity<ProductDto> getProduct(@PathVariable String id,
                                              WebRequest webRequest) {
  ProductDto product = productService.findById(id);

  // Step 1: Compute ETag (use DB version for efficiency)
  String etag = "\"v" + product.getVersion() + "\"";

  // Step 2: Check conditional request (If-None-Match)
  if (webRequest.checkNotModified(etag)) {
      // Spring sets 304 Not Modified, returns null body
      return null;
  }

  // Step 3: Return full response with caching headers
  return ResponseEntity.ok()
      .eTag(etag)
      .cacheControl(CacheControl.maxAge(5, TimeUnit.MINUTES)
          .cachePublic())    ← public: CDN can cache
      .body(product);
}

BROWSER REQUEST FLOW:
  1st: GET /api/v1/products/123
       ← 200 OK, ETag: "v15", Cache-Control: public, max-age=300
       (cached for 300 seconds)

  2nd (within 300s): served from browser cache, no request sent

  3rd (after 300s): GET /api/v1/products/123, If-None-Match: "v15"
  Product unchanged: ← 304 Not Modified, ETag: "v15"
  Product updated:   ← 200 OK, ETag: "v16", new body
```

---

### 🔄 The Complete Picture — End-to-End Flow

```
ETAG + CACHE-CONTROL IN PRODUCTION:

  [Browser]           [CDN (Cloudflare)]      [Origin API]     [Database]
      │                       │                     │                │
  GET /products/42            │                     │                │
      ├──────────────────────→│                     │                │
      │                  CDN MISS                   │                │
      │                       ├───────────────────→│                │
      │                       │                 DB query 20ms        │
      │                       │                     ├───────────────→│
      │                       │                     │←──── Product v7│
      │                       │  200 OK             │                │
      │                       │  ETag: "v7"         │                │
      │                       │  Cache-Control:     │                │
      │                       │  public, max-age=300│                │
      │                       │  s-maxage=3600      │                │
      │                  Store in CDN               │                │
      │  200 OK               │                     │                │
  Store in browser cache      │                     │                │
      │                       │                     │                │

  Next request (within 300s): browser serves from LOCAL cache, no network

  After 300s (browser stale, CDN still fresh within 3600s):
      GET /products/42, If-None-Match: "v7"
      CDN: still valid for 3600s → returns cached 200 response from CDN

  After 3600s (CDN stale):
      CDN: GET /products/42, If-None-Match: "v7" → origin
      Origin: product still v7 → 304 Not Modified
      CDN: resets TTL, returns cached body to browser
```

---

### 💻 Code Example

```java
// ETag-based optimistic locking for writes
@RestController
public class OrderController {

    // GET: return ETag for conditional update
    @GetMapping("/api/v1/orders/{id}")
    public ResponseEntity<OrderDto> getOrder(@PathVariable Long id, WebRequest req) {
        Order order = orderService.findById(id);
        String etag = "\"" + order.getVersion() + "\"";

        if (req.checkNotModified(etag)) {
            return null;  // 304 Not Modified
        }

        return ResponseEntity.ok()
            .eTag(etag)
            .cacheControl(CacheControl.maxAge(1, TimeUnit.MINUTES).cachePrivate())
            .body(toDto(order));
    }

    // PUT: conditional write — 412 if someone else updated in background
    @PutMapping("/api/v1/orders/{id}")
    public ResponseEntity<OrderDto> updateOrder(
            @PathVariable Long id,
            @RequestHeader(value = "If-Match", required = false) String ifMatch,
            @RequestBody UpdateOrderRequest request) {

        if (ifMatch == null) {
            return ResponseEntity.status(HttpStatus.PRECONDITION_REQUIRED)
                .body(null);  // Require If-Match for updates
        }

        // Strip quotes from ETag
        long clientVersion = Long.parseLong(ifMatch.replaceAll("\"", ""));

        try {
            Order updated = orderService.updateWithVersion(id, request, clientVersion);
            String newEtag = "\"" + updated.getVersion() + "\"";
            return ResponseEntity.ok()
                .eTag(newEtag)
                .body(toDto(updated));
        } catch (OptimisticLockingFailureException e) {
            return ResponseEntity.status(HttpStatus.PRECONDITION_FAILED).build(); // 412
        }
    }
}
```

---

### ⚖️ Comparison Table

| Header                     | Purpose                   | Direction | Impact                                  |
| -------------------------- | ------------------------- | --------- | --------------------------------------- |
| **Cache-Control: max-age** | Set freshness TTL         | Response  | No requests during TTL                  |
| **ETag**                   | Resource fingerprint      | Response  | Enables 304 conditional requests        |
| **If-None-Match**          | Conditional GET           | Request   | 304 if ETag unchanged                   |
| **If-Match**               | Conditional write         | Request   | 412 if ETag changed (optimistic lock)   |
| **Last-Modified**          | Timestamp-based freshness | Response  | Alternative to ETag (less reliable)     |
| **If-Modified-Since**      | Conditional GET (time)    | Request   | 304 if not modified since time          |
| **Vary**                   | Cache key dimensions      | Response  | Separate cache entries per header value |

---

### ⚠️ Common Misconceptions

| Misconception                         | Reality                                                                                                                              |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `no-cache` = no caching               | `no-cache` = cache but always revalidate before use. Use `no-store` to actually prevent caching                                      |
| ETag must be a content hash           | Any opaque string that changes when the resource changes. DB version number, timestamp, or hash all work. Version number is cheapest |
| 304 Not Modified means no server work | Server still processes the request (validates ETag), just skips body serialization and transfer. Reduces bandwidth, not CPU entirely |
| `max-age=0` = no-store                | `max-age=0` = immediately stale (always revalidate via ETag). `no-store` = never even store it                                       |

---

### 🚨 Failure Modes & Diagnosis

**304 Responses Not Working**

Symptom:
Client sends `If-None-Match` header, server returns `200 OK` with full body every time
even though content didn't change.

Root Cause:
ETag computation includes non-deterministic elements (timestamp of serialization, random
UUID field, Java HashMap insertion order affecting JSON field sequence) — each request
generates a different ETag even for identical data.

Diagnostic:

```java
// Test: call GET twice, compare ETags:
String etag1 = httpClient.getHeader("/api/products/1", "ETag");
String etag2 = httpClient.getHeader("/api/products/1", "ETag");
assert etag1.equals(etag2) : "ETag is non-deterministic! Fix computation.";

// Common non-deterministic ETag sources:
// 1. UUID.randomUUID() in response
// 2. System.currentTimeMillis() in ETag computation
// 3. HashMap-backed JSON with unstable field ordering
//    Fix: TreeMap or @JsonPropertyOrder for deterministic ordering

// Correct stable ETag sources:
// - Database version column (integer incremented on updates)
// - MD5/SHA-256 of sorted, normalized response fields
// - Last-modified timestamp (milliseconds precision)
```

---

### 🔗 Related Keywords

- `API Caching` — the broader caching strategy; ETag/Cache-Control are the HTTP mechanisms
- `Content Negotiation` — `Vary` header interacts with both caching and content negotiation
- `Conditional Requests` — If-None-Match and If-Match request headers that use ETags
- `Optimistic Locking` — If-Match for conditional writes prevents lost updates

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ CACHE-CONTROL│ max-age: TTL seconds for freshness        │
│ DIRECTIVES   │ public: CDN can cache                     │
│              │ private: browser only                     │
│              │ no-cache: always revalidate               │
│              │ no-store: never store                     │
│              │ immutable: never revalidate (static)      │
├──────────────┼───────────────────────────────────────────┤
│ ETAG FLOW    │ Response: ETag: "v7"                      │
│              │ Request: If-None-Match: "v7"              │
│              │ Unchanged: 304 No Body                    │
│              │ Changed: 200 New Body + New ETag          │
├──────────────┼───────────────────────────────────────────┤
│ CONDL WRITE  │ PUT + If-Match: "v7"                      │
│              │ Conflict: 412 Precondition Failed         │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Cache-Control: when to ask; ETag: why"  │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ API Caching → CDN → Content Negotiation  │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q.** A high-traffic API returns a list of 500 products. The team uses `ETag: "v" + maxUpdatedAt`
(the timestamp of the most recently updated product). Under normal load, 90% of requests
return 304. During a flash sale, every product's `updatedAt` changes in under 2 seconds
(price updates). For the duration of the flash sale, all clients' ETags are instantly stale.
Analyze: why does this scenario make ETags effectively useless during the flash sale?
What alternative ETag strategy (hint: consider incremental batch versioning) or caching
approach would handle both the normal and flash-sale cases?
