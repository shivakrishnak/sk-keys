---
layout: default
title: "RESTful Constraints"
parent: "HTTP & APIs"
nav_order: 214
permalink: /http-apis/restful-constraints/
number: "0214"
category: HTTP & APIs
difficulty: ★★☆
depends_on: REST, HTTP/1.1, HTTP Methods, HTTP Status Codes, Statelessness
used_by: HATEOAS, API Design Best Practices, API Gateway, Hypermedia
related: REST, HATEOAS, GraphQL, gRPC, Uniform Interface
tags:
  - api
  - rest
  - architecture
  - http
  - intermediate
---

# 214 — RESTful Constraints

⚡ TL;DR — RESTful constraints are the six formal rules from Fielding's 2000 dissertation that define REST, and understanding them explains why compliant APIs are inherently scalable, client-agnostic, and cacheable by infrastructure they know nothing about.

| #214            | Category: HTTP & APIs                                          | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------------- | :-------------- |
| **Depends on:** | REST, HTTP/1.1, HTTP Methods, HTTP Status Codes, Statelessness |                 |
| **Used by:**    | HATEOAS, API Design Best Practices, API Gateway, Hypermedia    |                 |
| **Related:**    | REST, HATEOAS, GraphQL, gRPC, Uniform Interface                |                 |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
By 2000, the web had already proven it could scale to hundreds of millions of users
with commodity hardware and no shared state between servers. But software architects
couldn't articulate why the web scaled and their own distributed systems didn't.
They copied HTTP's surface (verbs, status codes, JSON) but missed the properties
that made HTTP work: caching, statelessness, layered intermediaries. The result:
"REST APIs" that used HTTP syntax but broke HTTP semantics — requiring sessions,
refusing cacheability, embedding verbs in URLs — and then wondering why they
couldn't scale.

**THE BREAKING POINT:**
Without a formal specification of what REST actually IS, API designers confused
"using HTTP" with "REST," missing the constraints that give REST its properties.

**THE INVENTION MOMENT:**
This is exactly why Fielding formulated the six constraints. They are not
preferences or best practices — they are the necessary and sufficient conditions
for a distributed system to exhibit the scalability properties of the web.
Violate any constraint: lose its corresponding property. Keep all six: inherit
the web's scalability model.

---

### 📘 Textbook Definition

**RESTful constraints** are the six architectural constraints defined by Roy Fielding
in his 2000 dissertation "Architectural Styles and the Design of Network-based
Software Architectures" that constitute the REST (Representational State Transfer)
architectural style. The constraints are: **1) Client-Server** (separation of UI
from data storage), **2) Stateless** (each request contains all context; no server-
side session state), **3) Cacheable** (responses must declare cacheability explicitly),
**4) Uniform Interface** (a single standardised interface between client and server,
comprising: resource identification by URI, resource manipulation through
representations, self-descriptive messages, and HATEOAS), **5) Layered System**
(clients and servers can interact through intermediaries transparently), and
**6) Code on Demand** (optional: servers may deliver executable code). A system
satisfying all constraints is RESTful; violating any constraint causes loss of the
corresponding scalability or decoupling property.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The six RESTful constraints are the exact rules that make REST APIs inherit the
web's scalability — each constraint enforces one specific architectural property.

**One analogy:**

> Think of RESTful constraints as building codes for architecture. A building
> without structural codes might look like a building, but it won't safely support
> load. An "API without RESTful constraints" might look REST-shaped (HTTP + JSON)
> but won't inherit REST's structural properties (cacheability, scalability,
> intermediary transparency). The constraints ARE the load-bearing structure.

**One insight:**
Each RESTful constraint maps directly to one scalability or decoupling property.
Removing a constraint doesn't make the API worse in some vague way — it removes
a specific guarantee: statelessness → horizontal scalability; cacheability →
CDN offload; uniform interface → client independence; layered system → proxy
and CDN transparency. This 1:1 mapping is why Fielding's work remains authoritative
25 years later.

---

### 🔩 First Principles Explanation

**THE SIX CONSTRAINTS AND THEIR PROPERTIES:**

**Constraint 1 — Client-Server Separation**

Rule: The user interface (client) is decoupled from data storage (server).
They communicate only through the interface; neither knows the other's implementation.

Property granted:

- Clients and servers evolve independently
- Multiple clients (web, mobile, CLI) can use the same server without server changes
- Server can change database technology without affecting any client

Violation: Clients that know about DB schema, or servers that know about client
rendering logic = tight coupling = evolve together, release together.

**Constraint 2 — Stateless**

Rule: Each request from client to server must contain ALL information needed
to understand and process the request. The server stores NO session state between
requests.

Property granted:

- Any server in a pool can handle any request → horizontal scaling by definition
- No sticky sessions required at load balancers
- Server failure is transparent — client's next request goes to any surviving server

Violation: Server-side session stores mean all requests from one user must go to
the same server (sticky sessions) or all servers must share a session store
(centralised bottleneck). Both limit horizontal scale.

```
┌──────────────────────────────────────────────────────┐
│ Stateful vs Stateless — Scaling Difference           │
├──────────────────────────────────────────────────────┤
│ STATEFUL:                                            │
│  User → Server A (session: userId=123)               │
│  Failover? → Server B (no session!) → ERROR          │
│  Scale out? → Must sync sessions across all servers  │
│                                                      │
│ STATELESS:                                           │
│  User → Server A (Authorization: Bearer token→JWT)   │
│  Failover? → Server B (reads JWT) → SUCCESS          │
│  Scale out? → Add servers, no coordination needed    │
└──────────────────────────────────────────────────────┘
```

**Constraint 3 — Cacheable**

Rule: Every response must explicitly label whether it can be cached, for how long,
and under what conditions (`Cache-Control`, `ETag`, `Expires`).

Property granted:

- GET requests with correct Cache-Control are served entirely by CDN/browser
  cache — zero origin server load for cache hits
- At scale: 99% of reads can be CDN hits → 100× server capacity

Violation: Non-cacheable responses (or missing headers, defaulting to no-cache)
force every request to hit origin, requiring linear server scaling with traffic.

**Constraint 4 — Uniform Interface** (the defining constraint)

Four sub-constraints:

1. **Resource identification by URI**: every resource has a stable, unique URI
2. **Manipulation through representations**: clients interact with representations
   (JSON/XML), not server objects directly; representations may differ from
   server storage
3. **Self-descriptive messages**: each message carries enough info to process it
   (`Content-Type`, status code, required headers)
4. **HATEOAS**: responses include links to available next actions

Property granted:

- Any HTTP client can interact with any REST API without custom contract
- Intermediaries (CDN, proxy, gateway) act on requests without domain knowledge
- API surface is explorable without documentation (with HATEOAS)

Violation: Using POST for everything; embedding actions in URLs; requiring
out-of-band knowledge of what parameters to send = loss of uniform interface
= custom client required for every operation.

**Constraint 5 — Layered System**

Rule: Each layer only knows about the adjacent layer. Clients cannot tell if
they're talking to the origin server or a cache, proxy, or load balancer.

Property granted:

- CDNs, gateways, load balancers, security proxies can be inserted transparently
- Client doesn't need updating when infrastructure changes
- Legacy systems can be wrapped behind a REST API gateway

Violation: Clients that detect or require specific server-side behaviour
(checking server identity, requiring specific backend headers) = infrastructure
transparency lost.

**Constraint 6 — Code on Demand (Optional)**

Rule: Servers may send executable code to clients (e.g., JavaScript in browsers).

Property granted:

- Client functionality extensible by server without client updates
- Thin clients possible

Rarely relevant for API design; primarily explains browser-based web apps.

**THE TRADE-OFFS:**

- Gain: each constraint independently enables a specific scalability property
- Cost: statelessness forces credential re-transmission (JWT overhead); cacheability
  requires careful cache-invalidation design; uniform interface limits expressive
  power for complex operations

---

### 🧪 Thought Experiment

**SETUP:**
Two APIs. API-A violates the stateless constraint (uses server-side sessions).
API-B follows all six constraints. Both are deployed on 2 servers with a load
balancer. You need to handle 10× the traffic.

**WHAT HAPPENS WITH API-A (violates stateless):**

1. Scale to 20 servers — but sessions are on only 2 existing servers
2. New servers have no sessions — load balancer must be configured for sticky sessions
3. If Server 1 dies, all its sessions are lost — users logged out globally
4. To share sessions: add Redis cluster ($$$) → Redis becomes the new bottleneck
5. Sticky sessions mean load balancers can't distribute load evenly
6. Scaling is complex, expensive, and introduces new failure points

**WHAT HAPPENS WITH API-B (all six constraints):**

1. Scale to 20 servers — add them to load balancer, done
2. Every request carries a JWT — any server processes any request
3. Server 1 dies — its in-flight requests fail, but new requests hit servers 2–20
4. GET responses cached at CDN — 20 origin servers handle only 5% of traffic
5. Scaling is: add a server, route traffic to it. Linear cost, no coordination.

**THE INSIGHT:**
The RESTful constraints are not API design preferences — they are explicit engineering
trade-offs that exchange flexibility (stateful sessions, opaque operations) for
specific, measurable scalability guarantees. Understanding which constraint grants
which property lets you diagnose exactly _why_ an API can't scale before you
spend money on infrastructure.

---

### 🧠 Mental Model / Analogy

> RESTful constraints are architectural invariants — the same way structural
> engineering rules are invariants. A bridge is designed with specific constraints
> (load limits, span length, material strength requirements). Remove any constraint
> and the bridge might still look like a bridge but will fail under certain loads.
> Remove the stateless constraint from REST and the API still looks REST-like —
> but it will fail under horizontal scaling. The constraints aren't arbitrary
> strictness; they are load-bearing structures.

**Mapping:**

- "bridge" → REST API
- "structural constraints" → the six REST constraints
- "load the bridge handles" → concurrent users / horizontal scale
- "removing a structural constraint" → violating a REST constraint
- "bridge failing under load" → API failing to scale

**Where this analogy breaks down:**
Bridge failures are often catastrophic and permanent. REST constraint violations
are progressive and observable — you can usually identify exactly which constraint
violation is causing which scaling problem and fix it incrementally.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
REST is defined by six rules. Each rule is like a contract that makes web APIs
work reliably and scalably. Breaking one is like removing a rung from a ladder —
the ladder still looks like a ladder, but it becomes dangerous at height. The rules
exist because websites already followed them accidentally, and Fielding noticed
that's exactly why the web could serve billions of users.

**Level 2 — How to use it (junior developer):**
The constraints most violatable in practice: (1) Stateless — don't store user
sessions on the server; use JWT tokens the client sends each time. (2) Cacheable —
always set `Cache-Control` headers on GET responses; never return sensitive data
with `Cache-Control: public`. (3) Uniform interface — put verbs in HTTP methods,
not URLs; use standard HTTP status codes, not custom response wrappers with
`{"success": false}`.

**Level 3 — How it works (mid-level engineer):**
The most commonly violated constraint in enterprise APIs is cacheability — not
because teams decide to violate it, but because they never set `Cache-Control`
headers, defaulting to `no-cache`. This means every GET request hits origin, and
adding a CDN in front provides no benefit. Fixing this requires understanding the
two-step process: the server setting `Cache-Control: max-age=300, public` on
appropriate GET responses, and the CDN being configured to honour `Vary: Accept`
to avoid serving wrong-format cached responses.

**Level 4 — Why it was designed this way (senior/staff):**
The constraint formulation is deliberately architectural (system properties) rather
than prescriptive (specific technology choices). This solved a problem Fielding
observed: HTTP was being abused for RPC in a way that preserved the protocol's
syntax but discarded its semantics. By formalising the constraints as separate
properties, each with a clearly derivable scalability benefit, Fielding gave
architects a diagnostic tool: "My API doesn't scale horizontally — which constraint
am I violating? → Stateless. Fix: move from session state to JWT." The constraint
language made the diagnostic conversation precise.

---

### ⚙️ How It Works (Mechanism)

**Constraint 2 — Stateless → Implementation:**

```
# VIOLATES STATELESS (server-side session):
POST /login
→ Server: session[abc123] = {userId: 1}
→ Set-Cookie: JSESSIONID=abc123

GET /profile
Cookie: JSESSIONID=abc123
→ Server: lookup session[abc123] → userId: 1
→ Requires same server or shared session store

# SATISFIES STATELESS (JWT):
POST /login
→ Returns: {"token": "eyJhbGciOiJSUzI1NiJ9..."}

GET /profile
Authorization: Bearer eyJhbGciOiJSUzI1NiJ9...
→ Server: verifies JWT signature → extracts userId: 1
→ Any server processes this transparently
```

**Constraint 3 — Cacheable → Headers:**

```
# NOT cacheable (default if missing Cache-Control):
HTTP/1.1 200 OK
Content-Type: application/json
↑ Many proxies default to "no-cache" for missing CC

# CORRECT — explicitly cacheable:
HTTP/1.1 200 OK
Cache-Control: public, max-age=300
ETag: "v1-abc123"
Vary: Accept-Encoding

# NOT CACHEABLE (secure/private):
HTTP/1.1 200 OK
Cache-Control: no-store
↑ User-specific data — never cache
```

**Constraint 4 — Uniform Interface — Resource vs Action mapping:**

```
┌──────────────────────────────────────────────────────┐
│      Uniform Interface: Mapping Operations            │
├──────────────────────────────────────────────────────┤
│ VIOLATES:  POST /cancelOrder/{id}   (verb in URL)    │
│ CORRECT:   POST /orders/{id}/cancel (sub-resource)   │
│         or: PATCH /orders/{id} body: {status:cancel} │
│                                                      │
│ VIOLATES:  GET /getAllActiveUsers (verb in URL)       │
│ CORRECT:   GET /users?status=active                  │
│                                                      │
│ VIOLATES:  POST /users/search (POST for reads)       │
│ CORRECT:   GET /users?name=alice&role=admin          │
│         or: POST /users/searches (creates a search   │
│             resource — then HATEOAS links next page) │
└──────────────────────────────────────────────────────┘
```

---

### 🔄 The Complete Picture — End-to-End Flow

**HOW CONSTRAINTS INTERACT:**

```
┌──────────────────────────────────────────────────────┐
│       RESTful Constraints and Infrastructure          │
├──────────────────────────────────────────────────────┤
│ Client (any HTTP client)                             │
│   │ Uniform Interface: method + URI + headers        │
│   ↓                                                  │
│ CDN Layer                                            │
│   │ Cacheable: serves GET if Cache-Control allows   │
│   │ Layered System: client unaware of CDN            │
│   ↓                                                  │
│ Load Balancer                                        │
│   │ Stateless: routes to any server (no affinity)   │
│   │ Layered System: client unaware of LB             │
│   ↓                                                  │
│ [RESTFUL CONSTRAINTS ← YOU ARE HERE]                 │
│ Any server in pool                                   │
│   │ Stateless: reads all context from request       │
│   │ Uniform Interface: method → handler routing     │
│   ↓                                                  │
│ Database (client-server: server manages storage)    │
└──────────────────────────────────────────────────────┘
```

**FAILURE PATH:**
Session state present on Server A → Server A fails → all active users with
sessions on A lose their session → 401 Unauthorized on next request →
user forced to re-login → data loss for in-flight operations.

**WHAT CHANGES AT SCALE:**
At 100× scale, cacheability becomes the dominant constraint. At 10,000 req/s to
`GET /products/{id}`, with `Cache-Control: public, max-age=300`, a CDN catches
~98% of requests. That's 9,800 req/s served from CDN, 200 req/s hitting origin.
Removing or misusing cacheability: 10,000 req/s hit origin — 49× more origin load
for the same traffic. No amount of horizontal scaling is as cost-effective as
correct caching.

---

### 💻 Code Example

**Example 1 — Enforcing statelessness in Spring Boot:**

```java
// BAD: Stateful session — violates stateless constraint
@PostMapping("/login")
public ResponseEntity<?> login(@RequestBody LoginDto dto,
                               HttpSession session) {
    User user = authService.authenticate(dto);
    session.setAttribute("userId", user.getId()); // Server-side state!
    return ResponseEntity.ok().build();
}

// GOOD: Stateless JWT — satisfies constraint 2
@PostMapping("/login")
public ResponseEntity<TokenDto> login(@RequestBody LoginDto dto) {
    User user = authService.authenticate(dto);
    String token = jwtService.generateToken(user);
    return ResponseEntity.ok(new TokenDto(token)); // Client carries state
}

// In Spring Security config — enforce stateless:
http.sessionManagement(session ->
    session.sessionCreationPolicy(
        SessionCreationPolicy.STATELESS)  // No server sessions
);
```

**Example 2 — Implementing cacheability correctly:**

```java
@GetMapping("/products/{id}")
public ResponseEntity<ProductDto> getProduct(
        @PathVariable Long id,
        @RequestHeader(value = "If-None-Match",
                       required = false) String ifNoneMatch) {

    ProductDto product = productService.findById(id);
    String etag = '"' + product.getVersion() + '"';

    // Check if client's cached version is still valid:
    if (etag.equals(ifNoneMatch)) {
        return ResponseEntity.status(HttpStatus.NOT_MODIFIED)
            .eTag(etag).build(); // 304 — no body, saves bandwidth
    }

    return ResponseEntity.ok()
        // Public: CDN can cache this
        .cacheControl(CacheControl.maxAge(5, TimeUnit.MINUTES).cachePublic())
        .eTag(etag)           // Enable conditional requests
        .body(product);
}
```

**Example 3 — Uniform interface: correct resource naming:**

```java
// BAD: Verb-based URL (violates uniform interface)
@PostMapping("/sendWelcomeEmail/{userId}") // verb in URL!
@GetMapping("/fetchUserDetails/{userId}")  // verb in URL!

// GOOD: Resource-based URLs with HTTP verbs
@PostMapping("/users/{id}/welcome-email") // POST = trigger action
@GetMapping("/users/{id}")               // GET = fetch resource

// BAD: Using same method for different operations
@PostMapping("/search")          // read via POST = breaks caching
// GOOD:
@GetMapping("/users")            // GET /users?name=alice&active=true
```

---

### ⚖️ Comparison Table

| Constraint        | Property Granted       | Violation Symptom                    | Fix                     |
| ----------------- | ---------------------- | ------------------------------------ | ----------------------- |
| Stateless         | Horizontal scalability | Sticky sessions, session replication | JWT tokens              |
| **Cacheable**     | CDN offload, scale     | Origin overload on GET traffic       | Cache-Control headers   |
| Uniform Interface | Client independence    | Custom clients per API               | Standard methods + URIs |
| Layered System    | Proxy transparency     | Breaking when CDN added              | Honour HTTP semantics   |
| Client-Server     | Independent evolution  | Coupling of UI and data logic        | Clear API boundary      |
| Code on Demand    | Thin clients           | N/A (optional)                       | Send JS to clients      |

**How to choose which to prioritise:** All six constraints must be satisfied for
a RESTful system. However, the most frequently violated in production with the
most impact are: Stateless (horizontal scale), Cacheable (10–100× origin offload),
and Uniform Interface (client compatibility). Fix these first.

---

### ⚠️ Common Misconceptions

| Misconception                             | Reality                                                                                                                                                       |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "RESTful" just means using HTTP with JSON | REST requires all six constraints. Most "REST APIs" violate at least one, technically making them "HTTP APIs"                                                 |
| Stateless means no user authentication    | Stateless means no server-side session state. JWT tokens are stateless authentication — the credential travels in every request to any server                 |
| Code on Demand is required for REST       | Code on Demand is the only OPTIONAL constraint — it is explicitly marked optional by Fielding                                                                 |
| HATEOAS is impractical and rarely needed  | Fielding considers HATEOAS mandatory for the uniform interface constraint. Its absence is why most APIs require out-of-band documentation for every operation |
| REST and HTTP are the same thing          | HTTP is a protocol. REST is an architectural style that uses HTTP as its preferred transport but describes constraints beyond the protocol                    |

---

### 🚨 Failure Modes & Diagnosis

**Stateless Violation — Session Coupling**

Symptom: Adding new server instances doesn't help; load balancer sticky sessions
required; server crashes cause immediate user logouts.

Root Cause: Server-side HTTP sessions violate the stateless constraint. New
servers have no session state and cannot serve users whose sessions are on
other servers.

Diagnostic Command / Tool:

```bash
# Check if sticky sessions are configured (Nginx):
grep -i "ip_hash\|sticky" /etc/nginx/nginx.conf
# ip_hash; ← STICKY SESSIONS = stateless violation

# Check Java app for session usage:
grep -r "HttpSession\|session.getAttribute" src/ | wc -l
```

Fix: Replace server-side sessions with JWT tokens. Configure Spring Security
`SessionCreationPolicy.STATELESS`.

Prevention: Enforce stateless sessions in CI: fail build if `HttpSession`
usage is added without architectural review (`ArchUnit` test).

---

**Cacheable Violation — Missing Cache-Control Headers**

Symptom: CDN hit rate 0%; all traffic passing through to origin even after CDN
deployment; read-heavy APIs not scaling without proportional server increases.

Root Cause: GET responses lack `Cache-Control` headers. CDN defaults to
pass-through (no caching) when headers are absent.

Diagnostic Command / Tool:

```bash
# Check if CDN is caching:
curl -I https://api.example.com/products/123 | grep -i "cache"
# Should see: Cache-Control: public, max-age=300
# And from CDN: X-Cache: HIT

# Check CDN hit ratio in CDN console or:
curl https://cdn-provider.example.com/analytics/hitrate
```

Fix: Add `Cache-Control: public, max-age=N` to all public GET responses.
Add `Cache-Control: private, no-store` to user-specific responses.

Prevention: Integration test asserting `Cache-Control` header presence on all
GET endpoints. Deny merge if public GET endpoints return no-cache by default.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**

- `REST` — the RESTful constraints define REST; you must understand what REST is
  before studying the constraints that constitute it
- `HTTP Methods` — the uniform interface constraint is implemented via HTTP methods;
  understanding method semantics is required
- `HTTP Status Codes` — self-descriptive messages (constraint 4) require correct
  status codes; knowing which code to use is prerequisite

**Builds On This (learn these next):**

- `HATEOAS` — the fourth sub-constraint of the uniform interface; the most
  controversial and least-implemented RESTful constraint
- `API Design Best Practices` — operationalising RESTful constraints into daily
  design decisions
- `API Caching` — constraint 3 (cacheability) in practice; Cache-Control,
  ETag, CDN configuration

**Alternatives / Comparisons:**

- `GraphQL` — explicitly non-RESTful: uses POST for queries (violates uniform
  interface); always returns 200 (violates self-descriptive messages); excellent
  for query flexibility at the cost of REST's cacheable constraint
- `gRPC` — uses HTTP/2 but defines its own interface contract via Protobuf IDL;
  does not follow REST's uniform interface constraint

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Six constraints that define REST and each │
│              │ grant a specific scalability property     │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ "HTTP APIs" that look RESTful but lack    │
│ SOLVES       │ REST's scalability and decoupling properties│
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ Each constraint maps 1:1 to a property:   │
│              │ stateless→h-scale, cacheable→CDN offload  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Designing any public HTTP API that must   │
│              │ scale or be consumed by diverse clients   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Internal microservices using gRPC gain    │
│              │ nothing from REST constraints             │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Inherit web-scale infrastructure + client │
│              │ universality vs less expressive than RPC  │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Every RESTful constraint removes a       │
│              │  bottleneck — and only a bottleneck."     │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ HATEOAS → API Caching →                  │
│              │ API Design Best Practices                 │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** The layered system constraint states that a client cannot tell if it is
talking to the origin server or a cache, proxy, or gateway. A company deploys
an API gateway that adds a custom `X-Gateway-Processed: true` header to every
proxied request and a CDN that returns `X-Cache: HIT` or `MISS` in responses.
Does the presence of these headers violate the layered system constraint? Justify
your answer by analysing whether clients can or should depend on these headers for
correct operation — and specify exactly what would constitute a constraint violation.

**Q2.** A newly joined engineer proposes replacing your stateless JWT architecture
with Redis-backed server-side sessions to reduce CPU load from RS256 signature
verification (0.3ms per request → 0.01ms Redis lookup per request). She argues
this satisfies the stateless constraint because "the state is in Redis, not in any
individual server." Evaluate this claim strictly against Fielding's definition of
the stateless constraint. Will this change preserve REST's horizontal scaling
guarantee, and under what failure scenario does the Redis-backed session approach
diverge from true statelessness?
