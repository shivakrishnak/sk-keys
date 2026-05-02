---
layout: default
title: "REST"
parent: "HTTP & APIs"
nav_order: 213
permalink: /http-apis/rest/
number: "213"
category: HTTP & APIs
difficulty: ★☆☆
depends_on: HTTP/1.1, HTTP Methods (GET, POST, PUT, PATCH, DELETE), HTTP Status Codes
used_by: RESTful Constraints, HATEOAS, API Design Best Practices, API Versioning, OpenAPI / Swagger
tags:
  - networking
  - protocol
  - http
  - rest
  - architecture
  - foundational
---

# 213 — REST

`#networking` `#protocol` `#http` `#rest` `#architecture` `#foundational`

⚡ TL;DR — An architectural style for distributed systems that uses HTTP semantics (methods, URLs, status codes) and stateless communication to expose resources uniformly.

| #213 | Category: HTTP & APIs | Difficulty: ★☆☆ |
|:---|:---|:---|
| **Depends on:** | HTTP/1.1, HTTP Methods (GET, POST, PUT, PATCH, DELETE), HTTP Status Codes | |
| **Used by:** | RESTful Constraints, HATEOAS, API Design Best Practices, API Versioning, OpenAPI / Swagger | |

---

### 📘 Textbook Definition

**REST (Representational State Transfer)** is an architectural style for distributed hypermedia systems, defined by Roy Fielding in his 2000 dissertation. REST is characterised by six constraints: client-server separation, statelessness, cacheability, uniform interface, layered system, and (optional) code-on-demand. In the context of web APIs, REST means using HTTP methods (GET, POST, PUT, DELETE) to act on resources identified by URLs, with state represented as transferable representations (JSON, XML) and operations communicated via standard HTTP semantics. "RESTful" describes APIs that conform to REST constraints, though in practice many APIs are informally REST-like without full adherence.

### 🟢 Simple Definition (Easy)

REST is a way to design web APIs where resources (users, orders, products) have URLs and you interact with them using standard HTTP methods (GET, POST, PUT, DELETE).

### 🔵 Simple Definition (Elaborated)

Before REST became dominant, APIs used SOAP or RPC — complex, tightly coupled protocols where the API defined custom operations (getUser, createOrder, deleteProduct) rather than leveraging HTTP's built-in semantics. REST flips this: each thing in the system (a user, an order) has an address (URL) and you interact with it using HTTP verbs as actions. This leverages HTTP's existing infrastructure — caching, authentication, content negotiation, intermediaries — without reinventing them. The result is simpler, more scalable, and more cache-friendly APIs that any HTTP-compliant tool can interact with.

### 🔩 First Principles Explanation

**Fielding's insight:** HTTP was already a distributed hypermedia protocol. Good APIs should work WITH HTTP's properties, not around them.

**The 6 REST constraints:**

1. **Client-Server:** UI separated from data storage. Clients don't persist data; servers don't render UI. Enables independent evolution.

2. **Stateless:** Each request contains all information needed to process it. No server-held session state between requests. Enables horizontal scaling — any server can handle any request.

3. **Cacheable:** Responses must declare themselves cacheable or not. Enables CDN and browser caching to reduce server load.

4. **Uniform Interface (the central constraint):**
   - *Resource identification:* Resources identified via URLs (`/users/42`).
   - *Manipulation via representations:* Clients manipulate resources through JSON/XML representations.
   - *Self-descriptive messages:* Each message includes enough information to describe how to process it (Content-Type, methods).
   - *HATEOAS:* Responses include links to related actions (rarely implemented in practice).

5. **Layered System:** Client doesn't know if it's talking to origin server or intermediary (CDN, load balancer). Enables transparent infrastructure.

6. **Code-on-Demand (optional):** Server can send executable code (JavaScript). Almost never used in APIs.

**Resources vs. Actions:**

```
NOT REST (action-based, RPC-style):
POST /getUserById?id=42
POST /deleteOrder?orderId=10
POST /createUserAccount

REST (resource-based):
GET    /users/42
DELETE /orders/10
POST   /users    (with body)
```

**Resource naming conventions:**

```
/users              → collection: list/create users
/users/42           → single resource: CRUD on user 42
/users/42/orders    → nested: orders belonging to user 42
/users/42/orders/7  → specific nested: order 7 of user 42
```

### ❓ Why Does This Exist (Why Before What)

WITHOUT REST (SOAP/custom RPC):

- Each API requires custom client libraries and WSDL/IDL knowledge.
- Caching impossible — all operations go through POST with opaque bodies.
- No standard meaning for operations — every API invents its own verbs.

What breaks without it:
1. CDNs can't cache POST-only APIs — everything hits origin servers.
2. Generic HTTP debugging tools (curl, Postman) require custom configuration per API.

WITH REST:
→ Any HTTP client can interact with any REST API without custom libraries.
→ GET responses cacheable by CDNs automatically.
→ Self-documenting through URL structure and HTTP semantics.

### 🧠 Mental Model / Analogy

> REST is like a post office system. Every person and thing has a unique address (URL). You send standard-format letters using standard action types: "DELIVER" (POST), "RETRIEVE" (GET), "REPLACE" (PUT), "REMOVE" (DELETE). The post office (HTTP infrastructure) knows how to handle each type: delivery slips are shared (stateless), some letters are marked "may be copied" (cacheable), and intermediary sorting offices (CDNs, proxies) understand the standard markings.

"Address" = URL, "letter type" = HTTP method, "post office rules" = HTTP standards, "sorting offices" = CDNs/proxies.

The key: using standard infrastructure (post office) means you don't need to build your own delivery system.

### ⚙️ How It Works (Mechanism)

**REST API example — user resource:**

```
GET    /users        200 + [{id:1,...},{id:2,...}]
POST   /users        201 + {id:3,...} + Location: /users/3
GET    /users/3      200 + {id:3, name:"Carol", email:...}
PUT    /users/3      200 + {id:3, name:"Carol Updated",...}
PATCH  /users/3      200 + {id:3, email:"new@ex.com",...}
DELETE /users/3      204 (no content)
GET    /users/3      404 (not found after deletion)
```

**URL design principles:**

```
Nouns, not verbs:
  /users not /getUsers
  /orders/42/cancel → debated: POST /orders/42/cancellations
                              or PUT /orders/42/status {status:cancelled}

Plural collection names:
  /users not /user
  /products not /product-list

Hierarchy for relationships:
  /users/42/orders      → user 42's orders
  /orders?userId=42     → alternative: filter via query params

Query parameters for filtering/sorting:
  /users?role=admin&sort=name&limit=20&page=2
```

**Richardson Maturity Model (REST levels):**

```
Level 0: HTTP as transport (SOAP over HTTP, RPC over HTTP)
Level 1: Resources (/users, /orders — nouns not verbs)
Level 2: HTTP Verbs + Status Codes (GET/POST/PUT/DELETE + 200/201/404)
Level 3: HATEOAS (hypermedia links in responses)

Most "REST" APIs are actually Level 2.
True REST per Fielding requires Level 3.
```

### 🔄 How It Connects (Mini-Map)

```
HTTP/1.1 (protocol foundation)
      ↓ leveraged by
REST ← you are here
  (architectural style: resources + verbs + stateless)
      ↓ constrained by
RESTful Constraints | HATEOAS
      ↓ implemented as
JSON:API | OpenAPI / Swagger | API Design Best Practices
      ↓ alternatives
GraphQL (query-based) | gRPC (RPC-based) | SOAP (legacy)
```

### 💻 Code Example

Example 1 — RESTful API design in Spring Boot:

```java
@RestController
@RequestMapping("/api/v1")
public class UserController {

    // Collection resource
    @GetMapping("/users")
    public Page<UserDto> list(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(required = false) String role) {
        return userService.findAll(role, PageRequest.of(page, size));
    }

    // Nested resource: user's orders
    @GetMapping("/users/{userId}/orders")
    public List<OrderDto> userOrders(
            @PathVariable Long userId) {
        return orderService.findByUser(userId);
    }

    // State transition via sub-resource
    @PostMapping("/orders/{orderId}/cancellations")
    public ResponseEntity<OrderDto> cancel(
            @PathVariable Long orderId,
            @RequestBody CancellationRequest req) {
        OrderDto cancelled = orderService.cancel(orderId, req);
        return ResponseEntity.ok(cancelled);
    }
}
```

Example 2 — REST vs RPC style comparison:

```bash
# RPC style (NOT REST):
POST /api?action=getUserById&id=42
POST /api?action=updateUserEmail&id=42&email=new@ex.com

# REST style:
GET  /users/42
PATCH /users/42 -d '{"email":"new@ex.com"}'

# The REST style:
# - Uses HTTP verbs for action semantics
# - Uses URLs for resource identity
# - Uses status codes for outcome signalling
# - GET result is cacheable (CDN can serve it)
```

Example 3 — HATEOAS (Level 3 REST) response:

```json
{
  "id": 42,
  "name": "Alice",
  "email": "alice@example.com",
  "_links": {
    "self": {"href": "/users/42"},
    "orders": {"href": "/users/42/orders"},
    "update": {"href": "/users/42", "method": "PUT"},
    "delete": {"href": "/users/42", "method": "DELETE"}
  }
}
```

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Any HTTP API is REST | Many "REST APIs" are actually RPC-over-HTTP (POST /getUser). True REST requires all 6 constraints including statelessness and uniform interface. |
| REST requires JSON | REST is format-agnostic. A REST API can serve XML, CSV, or any representation. JSON became dominant due to JavaScript ecosystem preferences, not REST requirements. |
| REST is always better than GraphQL/gRPC | REST excels for public APIs and resource-oriented operations. GraphQL excels for flexible querying from rich clients. gRPC excels for internal services needing high performance. |
| /users/42/delete is a valid REST URL | REST uses HTTP methods for actions; URLs represent resources. The correct REST approach is DELETE /users/42. |
| REST is stateless means no sessions | Server-side sessions are prohibited, but the client can carry state (JWT token, session cookie containing state). "Stateless" means the server has no session state — each request is self-contained. |

### 🔥 Pitfalls in Production

**1. Using POST for Everything (Accidental RPC)**

```bash
# BAD: RPC-style over HTTP — no caching, wrong semantics
POST /api/getUserById?id=42
POST /api/searchProducts?q=laptop
POST /api/getOrderStatus?orderId=10

# GOOD: Resource-oriented with correct methods
GET /users/42
GET /products?q=laptop
GET /orders/10/status
```

**2. Embedding Actions in URLs (Verb-Based URLs)**

```bash
# BAD: Action-based URLs
POST /users/42/activate
POST /users/42/deactivate  
GET /users/42/getOrders

# GOOD: Resource state transitions
PUT /users/42/status -d '{"status":"active"}'
GET /users/42/orders   (noun-based sub-resource)
```

**3. Returning Inconsistent Error Structures**

```java
// BAD: Different error shapes break client parsing
@GetMapping("/users/{id}")
public User getUser(@PathVariable Long id) {
    if (!exists(id)) {
        return null; // returns 200 with null body...
    }
}

// GOOD: Consistent error bodies using RFC 7807 Problem Details
{
  "type": "https://api.example.com/errors/user-not-found",
  "title": "User Not Found",
  "status": 404,
  "detail": "User with id 42 does not exist"
}
```

### 🔗 Related Keywords

- `RESTful Constraints` — the formal 6 constraints that define REST.
- `HATEOAS` — the most neglected REST constraint; hypermedia-driven navigation.
- `HTTP Methods` — the verbs that give REST operations their semantics.
- `HTTP Status Codes` — the standard outcome signalling mechanism REST uses.
- `OpenAPI / Swagger` — the spec format for documenting REST APIs.
- `GraphQL` — the query-based alternative to REST for flexible client queries.
- `gRPC` — the RPC alternative for internal high-performance service communication.

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ KEY IDEA     │ Resources + URLs + HTTP verbs + stateless:│
│              │ leverage HTTP's infrastructure for APIs.  │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Public APIs, resource-oriented services,  │
│              │ browser/mobile clients, cacheable data.   │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Complex queries needing custom shapes →   │
│              │ GraphQL; high-perf internal → gRPC.       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "REST: treat HTTP as the API, not just    │
│              │ as the transport."                        │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ RESTful Constraints → HATEOAS → OpenAPI   │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A REST API's statelessness constraint requires each request to contain all information needed to process it. A service uses JWT tokens for authentication — the token contains user ID and roles. Another team argues that storing user roles in a database cache per session is more efficient (avoids decoding JWT on every request). Evaluate this argument: does a server-side role cache violate REST's statelessness constraint, and what operational consequences emerge when the role cache and JWT diverge?

**Q2.** REST HATEOAS (Level 3) embeds hypermedia links in every response, theoretically allowing clients to navigate an API without hardcoded URLs. Despite being a core REST constraint in Fielding's original thesis, almost no production JSON REST API implements HATEOAS. Analyse the practical reasons why HATEOAS is rarely implemented, what problems it was designed to solve that are solved by other means today, and in what specific type of API would HATEOAS provide genuine value that alternatives cannot match.

