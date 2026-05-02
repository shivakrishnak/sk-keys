---
layout: default
title: "RESTful Constraints"
parent: "HTTP & APIs"
nav_order: 214
permalink: /http-apis/restful-constraints/
number: "214"
category: HTTP & APIs
difficulty: ★★☆
depends_on: REST, HTTP/1.1, HTTP Methods (GET, POST, PUT, PATCH, DELETE), Idempotency in HTTP
used_by: HATEOAS, API Design Best Practices, API Backward Compatibility
tags:
  - networking
  - protocol
  - http
  - rest
  - architecture
  - intermediate
---

# 214 — RESTful Constraints

`#networking` `#protocol` `#http` `#rest` `#architecture` `#intermediate`

⚡ TL;DR — The six formal architectural constraints Roy Fielding defined as necessary for an API to qualify as REST: client-server, stateless, cacheable, uniform interface, layered system, code-on-demand.

| #214 | Category: HTTP & APIs | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | REST, HTTP/1.1, HTTP Methods (GET, POST, PUT, PATCH, DELETE), Idempotency in HTTP | |
| **Used by:** | HATEOAS, API Design Best Practices, API Backward Compatibility | |

---

### 📘 Textbook Definition

**RESTful Constraints** are the six architectural constraints defined by Roy Fielding in his 2000 dissertation that collectively define the Representational State Transfer (REST) architectural style. Each constraint adds a specific property to the architecture: **Client-Server** (separation of concerns), **Stateless** (requests self-contained), **Cacheable** (explicit response cache declarations), **Uniform Interface** (standardised resource operations), **Layered System** (transparent intermediaries), and **Code-on-Demand** (optional: transferable logic). Together, these constraints yield desirable properties: scalability, simplicity, modifiability, visibility, portability, and reliability. Violating any mandatory constraint produces an architecture that is merely "HTTP-based" rather than truly RESTful.

### 🟢 Simple Definition (Easy)

The six rules that make an API truly "REST": keep clients and servers separate, make each request self-contained, let responses be cached, use a uniform way to access resources, allow invisible intermediaries, and optionally send executable code.

### 🔵 Simple Definition (Elaborated)

Fielding derived REST by observing the web's architecture and identifying which properties made it scale so well. He formalised these as six constraints. Breaking any of the mandatory five (excluding Code-on-Demand) degrades specific properties: breaking statelessness makes horizontal scaling hard; breaking the uniform interface makes the API opaque to generic tools; breaking cacheability forces every request to hit origin servers. In practice, most "REST" APIs imperfectly implement these constraints — particularly the Uniform Interface's HATEOAS requirement — but the principles guide API design trade-offs.

### 🔩 First Principles Explanation

**Constraint 1 — Client-Server:**

Separates UI concerns from data storage concerns. The client manages presentation and user state; the server manages data and business logic. Neither should mix. This enables independent evolution: you can replace the mobile app without touching the API.

**Constraint 2 — Stateless:**

Each request from client to server must contain all information required to understand and process the request. The server retains no session state between requests. Every request is self-contained — authentication token, context, all included.

*Consequence:* Horizontal scalability. Any request can be routed to any server. No need for "sticky sessions" or shared session stores.

*Nuance:* The CLIENT can hold state (session token, user preferences). "Stateless" means the SERVER doesn't maintain per-client state between requests.

**Constraint 3 — Cacheable:**

Responses must declare themselves cacheable or non-cacheable using HTTP cache control semantics (`Cache-Control`, `ETag`, `Expires`). When responses are cacheable, clients, proxies, and CDNs can reuse them, reducing server load and latency.

*Consequence:* Scalability and performance. A REST API serving read-heavy content can scale indefinitely via a CDN cache.

**Constraint 4 — Uniform Interface (most important):**

The core REST constraint. Sub-constraints:
- **Resource identification:** Resources identified by URIs. `/users/42` identifies a user.
- **Manipulation through representations:** Clients manipulate resources via representations (JSON/XML), not direct database calls.
- **Self-descriptive messages:** Each message includes metadata describing how to process it (Content-Type, HTTP method, status code).
- **HATEOAS:** Responses include hypermedia controls (links) for navigating related resources.

*Consequence:* Generic clients work with any REST API. HTTP tools (curl, browsers, CDNs) work without API-specific knowledge.

**Constraint 5 — Layered System:**

The client cannot tell whether it's connected directly to the origin server or an intermediary (load balancer, CDN, proxy, API gateway). Intermediaries are transparent.

*Consequence:* Infrastructure can be added, removed, or changed without modifying client or server. You can add a CDN between client and server without changing either.

**Constraint 6 — Code-on-Demand (optional):**

Servers can extend client functionality by sending executable code (JavaScript). Reduces client complexity by delegating business logic to server-sent code.

*Consequence:* Clients are simpler — they download behaviour rather than encoding it. Used in web browsers (JavaScript). Rarely used in REST APIs.

### ❓ Why Does These Exist (Why Before What)

WITHOUT RESTful Constraints:

- SOAP APIs: custom protocols that can't be intermediated by standard CDNs.
- Session-heavy APIs: stick to one server — can't scale horizontally.
- Verb-based (RPC) APIs: no cacheability, opaque to generic tools.

What breaks without each constraint:
1. No stateless → sticky sessions → no horizontal scaling.
2. No cacheable → all requests hit origin → can't CDN-scale.
3. No uniform interface → every API requires custom tooling.
4. No layered → can't add CDN/LB transparently.

WITH RESTful Constraints:
→ The web proves the model: billions of clients, thousands of CDNs, millions of servers — all using REST's constraints.

### 🧠 Mental Model / Analogy

> REST constraints are like the rules that make the postal system work at global scale. (1) Client-Server: you write letters; postal workers deliver — separate concerns. (2) Stateless: each letter is self-addressed — the post office doesn't remember who you've written to before. (3) Cacheable: some letters are marked "share freely" — copies can be made and distributed. (4) Uniform Interface: standard envelope format — any postal system worldwide can process it. (5) Layered: you don't know which sorting offices handle your letter — they're invisible. (6) Code-on-demand: some envelopes contain instructions (forms to fill in).

The postal system scales to billions of letters per day precisely because these constraints enable parallel processing by any postal office, anywhere.

### ⚙️ How It Works (Mechanism)

**Constraint violations and consequences:**

```
Violation                  Property Lost     Consequence
─────────────────────────────────────────────────────────────
Server stores per-client   Scalability      Sticky sessions required
session state              ───────────────  Single-server deployments

GET /deleteUser?id=42      Cacheability     CDN caches deletion!
(unsafe method via GET)    Safety           Bots trigger side effects

POST /api for all ops      Cacheability     No CDN caching possible
(RPC-over-HTTP)            Uniform Interface Custom client per API

Server exposes database    Layered System   DB change breaks clients
column names in API        Modifiability    Direct coupling

No HATEOAS links           Uniform Interface Client hardcodes all URLs
                           Discoverability  Breaking URL changes break all clients
```

**Stateless vs stateful comparison:**

```
Stateful (NOT REST):
Client sends: GET /next-order
Server has: "Alice is logged in, querying her next order"
→ Server must remember Alice's session state

Stateless (REST):
Client sends: GET /users/42/orders/next
             Authorization: Bearer eyJhbGciOiJSUzI1NiJ9...
→ Token contains Alice's identity; no server session needed
→ ANY backend server can handle this request
```

### 🔄 How It Connects (Mini-Map)

```
Fielding's REST dissertation (2000)
           ↓ defines
RESTful Constraints ← you are here
  (6 constraints → uniform, scalable API architecture)
           ↓ guidance applied to
HTTP Methods | HTTP Status Codes | HTTP Headers
           ↓ most contested constraint
HATEOAS (hypermedia)
           ↓ practical application
API Design Best Practices | OpenAPI | API Versioning
```

### 💻 Code Example

Example 1 — Demonstrating each constraint in an API:

```java
// CONSTRAINT 1: Client-Server — controller knows nothing about UI
@RestController
public class UserController {
    // Only returns data; no rendering, no session management

    // CONSTRAINT 2: Stateless — all context in request
    @GetMapping("/users/{id}/orders")
    public List<OrderDto> userOrders(
            @PathVariable Long id,
            // All authentication in the request itself:
            @RequestHeader("Authorization") String token) {
        // No server-side session lookup needed
        User user = tokenService.extractUser(token);
        return orderService.findByUser(id);
    }

    // CONSTRAINT 3: Cacheable — explicit cache headers
    @GetMapping("/products/{id}")
    public ResponseEntity<ProductDto> getProduct(
            @PathVariable Long id,
            @RequestHeader(value="If-None-Match", required=false)
            String etag) {
        Product p = productService.findById(id);
        String currentEtag = "\"" + p.getVersion() + "\"";
        if (currentEtag.equals(etag)) {
            return ResponseEntity.status(304).build();
        }
        return ResponseEntity.ok()
            .header("ETag", currentEtag)
            .header("Cache-Control", "max-age=3600")
            .body(toDto(p));
    }

    // CONSTRAINT 4: Uniform Interface — resource + HATEOAS
    @GetMapping("/users/{id}")
    public EntityModel<UserDto> getUser(@PathVariable Long id) {
        UserDto dto = toDto(userService.findById(id));
        return EntityModel.of(dto,
            linkTo(methodOn(UserController.class)
                .getUser(id)).withSelfRel(),
            linkTo(methodOn(UserController.class)
                .userOrders(id, null)).withRel("orders")
        );
    }
}
```

Example 2 — Testing statelessness:

```bash
# Load balancer routes request to different servers on retry
# Each request must succeed regardless of which server handles it

# Token contains all identity — no session lookup needed:
curl -H "Authorization: Bearer eyJhbGciOiJSUzI1NiJ9..." \
     https://api.example.com/users/42/orders

# If this returns 401 depending on which server handles it,
# statelessness is violated — server has undisclosed session state
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Any API using HTTP is RESTful | REST requires all 5 mandatory constraints. An API using HTTP via POST for everything violates statelessness-of-caching and uniform interface. |
| HATEOAS is optional for a REST API | According to Fielding, HATEOAS is part of the Uniform Interface constraint and required for true REST. Most practitioners treat it as optional. |
| Stateless means no authentication state | Clients can carry state (JWT tokens with user data). "Stateless" means the server doesn't remember per-client state between requests. |
| Using JWTs makes an API fully stateless | JWTs allow stateless authentication, but if the server validates JWTs against a database blacklist, it has reintroduced server state. |
| RESTful constraints determine performance | REST constraints determine architectural properties (scalability, modifiability). Performance is separately determined by implementation choices. |

### 🔥 Pitfalls in Production

**1. Violating Statelessness with Server-Side Sessions**

```java
// BAD: Server stores user context — breaks horizontal scalability
HttpSession session = request.getSession();
session.setAttribute("currentUser", user); // stored on THIS server

// GOOD: All context in the JWT token
@GetMapping("/orders")
public List<Order> getOrders(
        @AuthenticationPrincipal JwtUser user) {
    // User extracted from token on every request — no session
    return orderService.findByUserId(user.getId());
}
```

**2. Non-Cacheable Responses for Public Read Data**

```java
// BAD: Public product catalog with no cache headers
@GetMapping("/products")
public List<Product> getProducts() {
    return productService.findAll();
    // Every request hits the database!
}

// GOOD: Cache public read data aggressively
return ResponseEntity.ok()
    .cacheControl(CacheControl.maxAge(1, TimeUnit.HOURS))
    .eTag(String.valueOf(catalog.getVersion()))
    .body(products);
// CDN serves 99% of product catalog requests
```

**3. Coupling Client to Implementation Details (Violation of Uniform Interface)**

```json
// BAD: Exposing internal IDs and column names
{
  "usr_id": 42,            // database column name
  "usr_tbl_created": "...", // internal field naming
  "db_acct": "premium"    // implementation detail
}

// GOOD: Domain-meaningful representation
{
  "id": 42,
  "accountType": "premium",
  "joinedAt": "2024-01-15T00:00:00Z"
}
```

### 🔗 Related Keywords

- `REST` — the architectural style whose formal definition these constraints constitute.
- `HATEOAS` — the most ambitious and most ignored of the four Uniform Interface sub-constraints.
- `Idempotency in HTTP` — the safe/idempotent properties of methods align with the stateless constraint.
- `API Design Best Practices` — practical guidelines derived from RESTful constraints.
- `HTTP Status Codes` — part of the self-descriptive message requirement of the Uniform Interface.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ 1. Client-Server  │ Separate UI from data concerns      │
│ 2. Stateless      │ Each request fully self-contained   │
│ 3. Cacheable      │ Responses declare cacheability      │
│ 4. Uniform Iface  │ Resources, representations, HATEOAS │
│ 5. Layered System │ Transparent intermediaries OK       │
│ 6. Code-on-Demand │ Optional: server sends executable   │
├──────────────────────────────────────────────────────────┤
│ ONE-LINER │ "REST constraints = properties that made    │
│            the web scale to billions of users."         │
├──────────────────────────────────────────────────────────┤
│ NEXT EXPLORE │ HATEOAS → API Design Best Practices      │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A service implements stateless authentication via JWT. To support token revocation (revoking a token before expiry), it maintains a Redis blacklist of revoked token IDs. The API team argues this is "still stateless" because the blacklist is in Redis rather than local server memory. Evaluate this argument against Fielding's definition of the stateless constraint: does distributed external state violate the constraint, and what is the practical architectural consequence of your answer for horizontal scaling?

**Q2.** The Layered System constraint says a client cannot tell if it's communicating with the origin server or an intermediary. A CDN edge node serving cached REST responses fulfils this constraint. However, when the CDN serves a stale cached response after the origin server's data changes, clients see different data than the origin server holds. Does this violate any REST constraint, and if not, explain precisely why serving stale data in a layered system is architecturally correct behaviour rather than a bug in REST's design.

