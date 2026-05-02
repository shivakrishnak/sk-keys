---
layout: default
title: "REST"
parent: "HTTP & APIs"
nav_order: 213
permalink: /http-apis/rest/
number: "0213"
category: HTTP & APIs
difficulty: ★☆☆
depends_on: HTTP/1.1, HTTP Methods, HTTP Status Codes, URLs
used_by: RESTful Constraints, API Gateway, API Design Best Practices, BFF
related: GraphQL, gRPC, SOAP, RESTful Constraints, HATEOAS
tags:
  - api
  - rest
  - http
  - architecture
  - foundational
---

# 213 — REST

⚡ TL;DR — REST is an architectural style for distributed systems that treats every piece of data or functionality as a named resource, accessed via uniform HTTP operations, giving the entire web and most modern APIs a consistent, cacheable, scalable interface.

| #213            | Category: HTTP & APIs                                            | Difficulty: ★☆☆ |
| :-------------- | :--------------------------------------------------------------- | :-------------- |
| **Depends on:** | HTTP/1.1, HTTP Methods, HTTP Status Codes, URLs                  |                 |
| **Used by:**    | RESTful Constraints, API Gateway, API Design Best Practices, BFF |                 |
| **Related:**    | GraphQL, gRPC, SOAP, RESTful Constraints, HATEOAS                |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
In the late 1990s, every distributed system invented its own protocol for remote
interaction. CORBA used binary IIOP. DCOM used Windows-specific COM infrastructure.
Java RMI coupled both sides to the same JVM. SOAP used XML envelopes with bespoke
WSDLs. All of these shared a problem: tight coupling. To call a CORBA service
you needed CORBA. To call a RMI service you needed Java. To call a SOAP service
you needed a generated client stub. Every service was a unique snowflake requiring
custom integration work from every consumer.

**THE BREAKING POINT:**
The internet proved that hyperlinked text could scale to billions of users because
browsers were universal clients connected to uniquely-named resources (URLs) via
a uniform interface (HTTP GET). But APIs rejected this model and required custom
clients, IDLs, and proprietary transports — making integration exponentially harder.

**THE INVENTION MOMENT:**
This is exactly why REST was described. Roy Fielding's 2000 PhD dissertation
formalised what the web already was, and named the architectural constraints
that made it scalable. Apply those same constraints to APIs, and you get APIs
that work with any HTTP client — a universal interface backed by 30 years of
HTTP infrastructure.

---

### 📘 Textbook Definition

**REST** (Representational State Transfer) is an architectural style for distributed
hypermedia systems, described by Roy Fielding in his 2000 doctoral dissertation.
REST is defined by six architectural constraints: **client-server** separation,
**statelessness** (each request carries all necessary context), **cacheability**
(responses explicitly label whether they can be cached), **uniform interface**
(resources identified by URIs, manipulated through representations), **layered
system** (intermediaries like proxies are transparent to clients and servers),
and optionally **code on demand** (servers can deliver executable code to clients).
An API that follows these constraints is called **RESTful**. REST leverages existing
web infrastructure (HTTP, TLS, CDNs, proxies, load balancers) because RESTful APIs
speak standard HTTP — the infrastructure already knows how to handle them.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
REST is the design philosophy that makes web APIs work like websites — nouns
(resources) you can read, create, update, and delete using standard verbs.

**One analogy:**

> REST is like a well-organised library. Every book (resource) has a unique
> call number (URL). You interact with books using the same four actions:
> "borrow" (GET), "donate a book" (POST), "replace a book" (PUT), "return
> and remove" (DELETE). The librarian (server) never needs to remember your
> last visit (stateless) — you bring the library card every time (request
> carries context). Any new librarian can immediately help you using the same
> system.

**One insight:**
REST's most powerful idea is not its conventions — it's that by using HTTP
exactly as it was designed, your API inherits three decades of existing
infrastructure: CDNs cache GET responses, browsers prefetch resources,
proxies route by URL, monitoring tools parse status codes, and every
programming language already has an HTTP client. You get this for free.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS (THE SIX CONSTRAINTS):**

1. **Client-Server:** The UI and data storage are separated. Client manages
   presentation; server manages data. They evolve independently.

2. **Stateless:** Every request from client to server must contain all information
   needed to understand the request. Sessions are not stored server-side. If
   authentication is needed, the token travels with every request.

3. **Cacheable:** Responses must label themselves as cacheable or non-cacheable.
   This enables CDNs, browser caches, and proxy caches — the foundation of web
   scale without central servers handling every request.

4. **Uniform Interface:** This is REST's defining constraint. Four sub-constraints:
   - Resources are identified by URIs: `/users/123`, `/orders/456`
   - Resources are manipulated through representations: the client sends/receives
     JSON/XML, not database rows — the representation can differ from storage
   - Self-descriptive messages: each message carries enough info to be processed
     (Content-Type, status code)
   - HATEOAS (optional in practice): responses include links to next actions

5. **Layered System:** Client cannot tell if it's talking to origin server,
   proxy, cache, or load balancer. Each layer only knows about the adjacent layer.

6. **Code on Demand (optional):** Server can extend client functionality by
   sending executable code (JavaScript). Rarely used in APIs.

**RESOURCES AND REPRESENTATIONS:**

```
┌──────────────────────────────────────────────────────┐
│           REST: Resources vs Representations         │
├──────────────────────────────────────────────────────┤
│ Resource (abstract concept):                         │
│   "The user with ID 123"                             │
│   URI: /users/123 (the identity, permanent)          │
│                                                      │
│ Representation (concrete transfer):                  │
│   JSON: {"id":123, "name":"Alice"}                   │
│   XML:  <user><id>123</id><name>Alice</name></user>  │
│                                                      │
│ Same resource, multiple representations:             │
│   GET /users/123 Accept: application/json → JSON     │
│   GET /users/123 Accept: application/xml  → XML      │
└──────────────────────────────────────────────────────┘
```

**THE TRADE-OFFS:**

- Gain: universal client support, leverages HTTP infrastructure (caching,
  CDN, proxies); decoupled evolution of client and server
- Cost: chatty by nature (multiple requests for related data); statelessness
  means re-sending auth credentials every request (token overhead); not ideal
  for operations that don't map to CRUD on a resource

---

### 🧪 Thought Experiment

**SETUP:**
A social media app needs to show a user's profile page: their details, their 10
latest posts, and the number of their followers. Compare RPC (one custom call)
vs REST (separate resources).

**WHAT HAPPENS WITH RPC (non-REST):**

1. Client calls `getUserProfilePage(userId=123)` — one request
2. Server fetches and combines user + posts + follower count into one response
3. Fast, but tightly coupled: client can't cache user data and posts separately
4. If the user changes their email, client must reload the whole profile
5. Mobile app and web app need the same combined call, even if mobile wants
   fewer posts

**WHAT HAPPENS WITH REST:**

1. GET `/users/123` → user details (cache for 1 hour)
2. GET `/users/123/posts?limit=10` → posts (cache for 30 seconds)
3. GET `/users/123/followers/count` → count (cache for 5 minutes)
4. 3 separate requests, but each independently cacheable
5. CDN serves cached user details for 99% of requests — 0 origin hits
6. Mobile app requests `/posts?limit=5` — same API, different params
7. Email change → only `/users/123` cache invalidations; posts cache untouched

**THE INSIGHT:**
REST's resource model costs upfront (multiple round trips) but pays off at scale
via independent cacheability. A social media API where user profiles are cached
at CDN serves millions of users with a handful of origin requests per minute.
This is impossible with opaque RPC calls that combine multiple concerns.

---

### 🧠 Mental Model / Analogy

> REST is the web's universal remote control. Every resource is a button on the
> remote control identified by its position (URL). Every press is one of four
> standard actions: look at the screen (GET), add a channel (POST), replace a
> channel (PUT), delete a channel (DELETE). Any remote control that knows these
> four buttons works with any TV. Any HTTP client that knows GET, POST, PUT,
> DELETE works with any REST API.

**Mapping:**

- "remote control" → HTTP client (browser, curl, JavaScript fetch, OkHttp)
- "TV" → REST API server
- "channel position" → resource URL
- "look at the screen" → GET
- "add a channel" → POST
- "replace a channel" → PUT
- "delete a channel" → DELETE
- "any remote works with any TV" → uniform interface

**Where this analogy breaks down:**
A real TV remote has no concept of "the remote doesn't remember previous
channel changes" (statelessness). And real remotes can't receive data back
from the TV (the request-response nature of HTTP). The analogy captures the
uniform interface but misses statelessness and the bidirectional exchange.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
REST is the most common way for software on the internet to talk to each other.
Instead of inventing new "languages" for each app, REST says: every piece of
data is a "resource" with a web address (URL), and you interact with it using
the same four words — GET (read), POST (create), PUT (replace), DELETE (remove).
Since every app on the web already understands these words, any app can talk to
any REST API.

**Level 2 — How to use it (junior developer):**
Design URLs as nouns (resources), not verbs (actions). Use plural nouns:
`/users`, `/orders`, `/products`. Use HTTP methods for the verbs: GET `/users`
(list all), POST `/users` (create one), GET `/users/123` (get one), PUT
`/users/123` (replace one), DELETE `/users/123` (remove one). Never use URLs
like `/getUser` or `/deleteOrder` — put the verb in the HTTP method, not the
URL. Return correct status codes: 200, 201, 204, 400, 401, 403, 404, 500.

**Level 3 — How it works (mid-level engineer):**
REST's value comes from its constraints working together. Statelessness + HTTP
methods + proper status codes = retry-safe, cacheable, infrastructure-transparent
APIs. The `Vary: Accept` header + content negotiation = one URL, multiple formats.
The uniform interface means an API gateway, CDN, load balancer, or rate limiter
can act on any REST API without knowing its business domain — they only need to
understand HTTP. When REST breaks down (complex queries, real-time updates,
bulk operations), this is typically a sign of pushing REST beyond its natural
domain — consider GraphQL for complex queries or gRPC for bidirectional streaming.

**Level 4 — Why it was designed this way (senior/staff):**
Fielding's insight was that the web's extraordinary scalability came specifically
from these six constraints working in combination — not from any individual
constraint. He wrote the dissertation to explain WHY the web worked, and then
showed that any distributed system applying those same constraints would inherit
the same scalability properties. The "REST is just HTTP + JSON" oversimplification
in popular usage ignores most of Fielding's constraints (especially statelessness,
cacheability, and HATEOAS) — which is why most real-world "REST" APIs are
technically just "HTTP APIs." This distinction matters when debugging scalability
problems that REST's cacheability should prevent.

---

### ⚙️ How It Works (Mechanism)

**Resource-URL Hierarchy Design:**

```
┌──────────────────────────────────────────────────────┐
│               REST Resource URL Hierarchy            │
├──────────────────────────────────────────────────────┤
│ Collection:      GET  /users                         │
│                  POST /users                         │
│                                                      │
│ Single resource: GET    /users/{id}                  │
│                  PUT    /users/{id}                  │
│                  PATCH  /users/{id}                  │
│                  DELETE /users/{id}                  │
│                                                      │
│ Sub-resource:    GET  /users/{id}/orders             │
│                  POST /users/{id}/orders             │
│                                                      │
│ Action (non-CRUD): POST /users/{id}/reset-password   │
│ (use POST for actions that don't map to CRUD)        │
└──────────────────────────────────────────────────────┘
```

**Request-Response Example (full cycle):**

```
# Create a user:
POST /users HTTP/1.1
Content-Type: application/json

{"name": "Alice", "email": "alice@example.com"}

→ HTTP/1.1 201 Created
→ Location: /users/456
→ Content-Type: application/json

→ {"id": 456, "name": "Alice", "email": "alice@example.com",
→  "createdAt": "2024-01-15T10:30:00Z"}

# Retrieve the user:
GET /users/456 HTTP/1.1
Accept: application/json

→ HTTP/1.1 200 OK
→ Cache-Control: max-age=300
→ ETag: "abc123"
→ {"id": 456, "name": "Alice", ...}
```

**Statelessness — what it means concretely:**

```
┌──────────────────────────────────────────────────────┐
│           Stateless vs Stateful Sessions             │
├──────────────────────────────────────────────────────┤
│ Stateful (NOT REST):                                 │
│  POST /login → server stores session                │
│  GET /profile → server looks up session             │
│  (Server MUST remember previous request)            │
│                                                      │
│ Stateless (REST):                                   │
│  GET /profile HTTP/1.1                              │
│  Authorization: Bearer eyJhbGc...                   │
│  (Every request is complete — no server session)    │
│                                                      │
│ Implication: any server in a load-balanced pool     │
│  can handle any request — stateless = horizontally  │
│  scalable by definition                             │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**

```
┌──────────────────────────────────────────────────────┐
│         REST API Request — Full System View          │
├──────────────────────────────────────────────────────┤
│ Client builds request: method + URL + headers + body │
│         ↓                                            │
│ TLS/HTTPS established                                │
│         ↓                                            │
│ CDN: is this GET? Is it cached? → Return cache       │
│         ↓ (cache miss or non-cacheable)              │
│ Load balancer: routes by URL or round-robin          │
│         ↓                                            │
│ [REST API ← YOU ARE HERE]                            │
│ Server: router matches {Method, URL} → handler       │
│         ↓                                            │
│ Auth filter → validation → business logic → DB       │
│         ↓                                            │
│ Response: status + headers + JSON body               │
│         ↓                                            │
│ CDN: stores GET 200 response if Cache-Control allows │
│         ↓                                            │
│ Client parses: status code first, then body          │
└──────────────────────────────────────────────────────┘
```

**FAILURE PATH:**
Auth token missing → server returns `401 Unauthorized` with `WWW-Authenticate:
Bearer realm="api.example.com"` → client must re-authenticate before retrying.

**WHAT CHANGES AT SCALE:**
At high scale, proper REST cacheability transforms scale. A product detail API
(GET `/products/{id}`) with `Cache-Control: public, max-age=300` allows CDN to
serve ~98% of requests from cache. The 2% cache misses hit origin. Without correct
Cache-Control headers, 100% of requests hit origin — a 50× scale difference
from a two-line header change.

---

### 💻 Code Example

**Example 1 — Well-designed REST controller (Spring Boot):**

```java
@RestController
@RequestMapping("/api/v1/orders")
public class OrderController {

    // Collection resource: list with pagination
    @GetMapping
    public ResponseEntity<Page<OrderDto>> listOrders(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        Page<OrderDto> orders = orderService.findAll(
            PageRequest.of(page, size));
        return ResponseEntity.ok()
            .cacheControl(CacheControl.maxAge(60, TimeUnit.SECONDS))
            .body(orders);
    }

    // Single resource: create
    @PostMapping
    public ResponseEntity<OrderDto> createOrder(
            @RequestBody @Valid CreateOrderRequest req) {
        OrderDto order = orderService.create(req);
        URI location = URI.create("/api/v1/orders/" + order.getId());
        return ResponseEntity.created(location).body(order); // 201
    }

    // Single resource: read
    @GetMapping("/{id}")
    public ResponseEntity<OrderDto> getOrder(
            @PathVariable Long id) {
        OrderDto order = orderService.findById(id)
            .orElseThrow(() -> new NotFoundException(id));
        return ResponseEntity.ok()
            .eTag(order.getVersion().toString())
            .cacheControl(CacheControl.maxAge(30, TimeUnit.SECONDS))
            .body(order);
    }

    // Single resource: partial update
    @PatchMapping("/{id}")
    public ResponseEntity<OrderDto> updateOrder(
            @PathVariable Long id,
            @RequestBody Map<String, Object> updates) {
        return ResponseEntity.ok(orderService.patch(id, updates));
    }
}
```

**Example 2 — Common REST anti-patterns:**

```java
// BAD: Verb in URL — method IS the verb, not the path
@GetMapping("/getUser/{id}")    // GET /getUser/123
@PostMapping("/deleteOrder/{id}") // should be DELETE /orders/{id}
@PostMapping("/updateStatus")   // should be PATCH /orders/{id}

// BAD: Returns 200 for errors
@GetMapping("/{id}")
public ResponseEntity<Object> getUser(@PathVariable Long id) {
    Optional<User> user = userRepo.findById(id);
    if (user.isEmpty()) {
        return ResponseEntity.ok(Map.of("error", "not found"));
        // WRONG: returns 200 with error body
    }
    return ResponseEntity.ok(user.get());
}

// GOOD: Correct status codes, resource-oriented URLs
@GetMapping("/users/{id}")
public ResponseEntity<User> getUser(@PathVariable Long id) {
    return userRepo.findById(id)
        .map(ResponseEntity::ok)            // 200 when found
        .orElseThrow(() ->
            new ResponseStatusException(HttpStatus.NOT_FOUND));   // 404
}
```

---

### ⚖️ Comparison Table

| Style     | Interface         | Caching   | Type Safety     | Streaming         | Best For               |
| --------- | ----------------- | --------- | --------------- | ----------------- | ---------------------- |
| **REST**  | HTTP + JSON       | Excellent | Manual          | Limited           | Public APIs, CRUD      |
| GraphQL   | POST /graphql     | Complex   | Schema          | Subscriptions     | Complex queries        |
| gRPC      | HTTP/2 + Protobuf | No        | Generated stubs | Bidirectional     | Internal microservices |
| SOAP      | HTTP + XML        | No        | WSDL            | No                | Legacy enterprise      |
| WebSocket | TCP (upgrade)     | N/A       | Manual          | Yes (full-duplex) | Real-time              |

**How to choose:** Use REST for public-facing APIs and CRUD-heavy services where
caching and client universality matter. Use GraphQL when clients need flexible
field selection. Use gRPC for internal microservices needing high performance and
strong typing. Use WebSocket for real-time bidirectional communication.

---

### ⚠️ Common Misconceptions

| Misconception                           | Reality                                                                                                                                                                              |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| REST means using JSON over HTTP         | REST is a set of architectural constraints. Using JSON + HTTP is common but not sufficient. True REST requires statelessness, cacheability, uniform interface, and other constraints |
| All HTTP APIs are RESTful               | An API using POST for everything with session-based auth on a server-side session is HTTP but not REST (violates statelessness and uniform interface)                                |
| REST is always better than gRPC/GraphQL | REST's caching strengths apply to read-heavy public APIs. Internal microservices with complex operations often benefit from gRPC's type safety and bidirectional streaming           |
| /users/{id}/delete is RESTful           | Never put verbs in URLs. Use DELETE /users/{id} — the method IS the verb                                                                                                             |
| REST requires HATEOAS in practice       | Fielding considers HATEOAS (hypermedia) mandatory. In practice, almost no real-world API implementations include HATEOAS — making them technically "HTTP APIs", not REST             |

---

### 🚨 Failure Modes & Diagnosis

**Chatty API (N+1 REST Pattern)**

Symptom: Loading a list page requires 1 + N API calls (1 for the list, N for
each item's details); mobile client sees 500ms page load even though server
processes each call in 10ms.

Root Cause: REST's resource granularity matches individual entities well but
requires aggregation at client or API layer for composed views.

Diagnostic Command / Tool:

```bash
# Chrome DevTools Network tab: count requests per page load
# Look for patterns: GET /users, GET /users/1, GET /users/2, ...etc.

# Server side: count per-session API calls:
grep "GET /api/users/" access.log | awk '{print $1}' \
  | sort | uniq -c | sort -rn | head -5
```

Fix: Add composite endpoints: `GET /users?include=orders,profile` or implement
GraphQL for flexible field selection. Design "view" resources that aggregate
related data: `GET /user-dashboard/123` returns everything needed for the
dashboard in one call.

Prevention: Design API around consumer use cases, not just data entities.
Apply BFF (Backend for Frontend) pattern for mobile vs web clients.

---

**Broken Caching (GET with Side Effects)**

Symptom: CDN serves stale data even after the data changes; state changes
triggered by hitting "refresh" in browser; inconsistent results from refreshing.

Root Cause: API uses GET requests for operations with side effects
(incrementing view counters, recording "last seen", triggering actions).
CDN caches GET responses and serves stale data, but also misses side effects
on cache hits.

Diagnostic Command / Tool:

```bash
# Check if GET responses trigger side effects by examining logs:
grep "GET /api/posts" access.log | wc -l  # total GETs
# vs database updates triggered:
SELECT COUNT(*) FROM view_events WHERE date = today;
# If CDN hit rate is 80%, GETs >> db updates — side effects missed
```

Fix: Never use GET for operations with side effects. Use POST for actions.
Move "last seen" tracking to async background processes triggered separately.

Prevention: Code review: any GET handler that writes to a database is a bug.
Enforce this with architecture tests (ArchUnit).

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `HTTP/1.1` — REST is built entirely on HTTP; understanding HTTP methods, status
  codes, and headers is required to implement REST correctly
- `HTTP Methods` — the HTTP verbs (GET, POST, PUT, PATCH, DELETE) are REST's
  uniform interface; their idempotency properties are REST's safety guarantees
- `HTTP Status Codes` — REST uses status codes as the machine-readable outcome
  of every operation

**Builds On This (learn these next):**

- `RESTful Constraints` — the six formal constraints that define REST vs HTTP-API;
  important for understanding what "truly RESTful" means
- `API Design Best Practices` — practical conventions for URL structure, versioning,
  pagination, and error responses in REST APIs
- `API Gateway` — the infrastructure layer that proxies, secures, and manages
  REST APIs at scale

**Alternatives / Comparisons:**

- `GraphQL` — query language that avoids REST's N+1 problem by fetching exactly
  the fields needed in one request; trades cacheability for query flexibility
- `gRPC` — binary RPC protocol over HTTP/2; trades REST's universality and
  cacheability for performance and bidirectional streaming
- `SOAP` — XML-based predecessor; more rigid, more verbose, but offers WS-\*
  standards for enterprise security and transactions

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Architectural style: named resources +   │
│              │ uniform HTTP operations + statelessness  │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Proprietary RPC required custom clients; │
│ SOLVES       │ REST reuses universal HTTP infrastructure │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Statelessness × cacheability × uniform   │
│              │ interface = free horizontal scalability  │
│              │ + CDN offload                            │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Public APIs, CRUD, resource-centric data │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Complex queries needing many resources;  │
│              │ high-throughput internal microservices   │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Universal client support + caching vs    │
│              │ chatty (N+1) for complex aggregations    │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "The web scaled to billions of users     │
│              │  using these six constraints — so can   │
│              │  your API."                              │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ RESTful Constraints → API Design →       │
│              │ GraphQL → API Gateway                   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A REST API at `GET /users/{id}` returns a user object with `Cache-Control:
max-age=300`. The user updates their password. The CDN has 50 edge nodes worldwide,
each with their own cached copy. Describe the complete sequence of events — from
the moment the password update is committed to the database — that must occur to
guarantee the cached version is never served after the update. What REST mechanism
is designed to handle this, and what is its fundamental limitation?

**Q2.** REST's statelessness constraint requires clients to re-send authentication
credentials with every request. At 10,000 requests/second, a JWT verification (with
asymmetric RS256 signature validation) costs 0.3ms of CPU per request. Calculate
total CPU time dedicated to auth per second, and compare this to a hypothetical
stateful session approach where sessions are stored in Redis and verified in 0.01ms
(Redis lookup). What architectural trade-off does REST's statelessness impose, and
at what scale does it become the dominant CPU cost?
