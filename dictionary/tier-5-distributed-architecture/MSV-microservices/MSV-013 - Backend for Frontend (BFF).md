---
id: MSV-013
title: Backend for Frontend (BFF)
category: Microservices
tier: tier-5-distributed-architecture
folder: MSV-microservices
difficulty: ★★☆
depends_on: MSV-012, MSV-010
used_by: MSV-019
related: MSV-012, MSV-019, MSV-010, MSV-029
tags:
  - microservices
  - api
  - intermediate
  - patterns
status: complete
version: 4
layout: default
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 13
permalink: /microservices/backend-for-frontend-bff/
---

# MSV-013 - Backend for Frontend (BFF)

⚡ TL;DR - Backend for Frontend (BFF) is the pattern of
creating a dedicated backend service for each client type
(mobile, web, partner API). Each BFF aggregates and shapes
data specifically for its client, eliminating over-fetching,
under-fetching, and cross-client API coupling.

| #013 | Category: Microservices | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | API Gateway, Inter-Service Communication | |
| **Used by:** | API Composition Pattern | |
| **Related:** | API Gateway, API Composition Pattern, Inter-Service Communication, Contract-First API Design | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
You have one API used by both a mobile app and a web app.
The mobile app needs a compact payload (5 fields) to fit
small screen real estate and limited bandwidth. The web app
needs a rich payload (25 fields) for its detailed views.
You compromise: the shared API returns 25 fields.
Mobile gets 20 unnecessary fields in every response.
Bandwidth wasted, battery drained, mobile users complain
about slow load times.

A partner integration needs the API formatted differently
(different field names, different date formats). You add
query parameters to the shared API: `?format=partner&fields=...`.
The shared API now has 15 query parameters to support all
client types. Every release, three teams coordinate on
what the shared API should look like. Releases slow down
because a mobile change breaks the partner integration.

**THE BREAKING POINT:**
A single API serving multiple clients creates a contradiction:
different clients have different needs for data shape, payload
size, protocol (REST vs GraphQL vs binary), auth requirements,
and caching behaviour. Compromising to serve all results
in a suboptimal API for every client.

**THE INVENTION MOMENT:**
The BFF pattern, coined by Sam Newman (2015), solves this
by creating one small, thin backend per client type. Each
BFF owns the API contract for its client and orchestrates
calls to downstream microservices to assemble the required
data in the right shape.

---

### 📘 Textbook Definition

**Backend for Frontend (BFF)** is an architectural pattern
in which a dedicated API layer (the BFF) is created for
each distinct client type (mobile app, web app, partner API,
IoT device, etc.). The BFF acts as a mediator between the
client and the underlying microservices: it aggregates data
from multiple downstream services, shapes the response to
match the client's exact data needs, and handles client-
specific concerns (offline support, batching, auth flows).
Each BFF is owned by the team that builds the frontend it
serves, ensuring tight alignment between API contract and
client requirements.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
BFF = one dedicated backend per client type, shaped exactly
for that client's needs, rather than one shared API that
tries to serve everyone.

**One analogy:**
> A hotel has a concierge for leisure guests and a separate
> business centre for corporate guests. Each provides the
> same underlying hotel services (room service, transport)
> but packages them differently: concierge books restaurant
> tables and tours; business centre books meeting rooms and
> prints boarding passes. One underlying hotel, two
> specialised entry points.

**One insight:**
BFF moves the "adapt data for this client" logic from the
client (where it creates code duplication across platforms)
or from a shared API (where it creates bloat) into a thin
dedicated service. The responsibility for the client API
contract lives with the team that understands the client.

---

### 🔩 First Principles Explanation

**THE CORE PROBLEM BFF SOLVES:**

```
WITHOUT BFF (shared API):
─────────────────────────
Mobile App  ──→┐
Web App     ──→┼──→  General API  ──→  Microservices
Partner     ──→┘
IoT Device  ──→

Problem: API is a compromise for all, optimal for none.
         Release velocity: all clients constrained by
         the most conservative client team.

WITH BFF (dedicated per client):
─────────────────────────────────
Mobile App  ──→  Mobile BFF  ──→┐
Web App     ──→  Web BFF     ──→┼──→  Microservices
Partner     ──→  Partner BFF ──→┘

Benefit: Each BFF optimised for its client.
         Each BFF releases independently.
         Mobile team owns Mobile BFF.
```

**THE ORCHESTRATION ROLE:**
The BFF is an orchestration layer. A single mobile BFF
request for "dashboard" might internally:
1. Call User Service for profile
2. Call Order Service for recent orders
3. Call Notification Service for unread count
4. Assemble into one compact JSON response
5. Apply mobile-specific transformations (date formatting,
   image URL resizing parameters)

**THE OWNERSHIP MODEL:**
The full-stack team (frontend + BFF + downstream service
changes needed) owns the client experience end-to-end.
Changes to the mobile UI require only changes to the
Mobile BFF and the mobile app - no coordination with
web team or partner team.

---

### 🧪 Thought Experiment

**SETUP:**
An e-commerce platform has: mobile app, web app, and
a B2B partner API. All use the same product and order data.

**Without BFF:**
Shared GET /products/{id} returns:
- 30 fields (all metadata for completeness)
- 1.2KB per response
- Partner needs different date formats
- Mobile needs image thumbnails
- Web needs full image gallery

**With BFF:**
Mobile BFF GET /products/{id}:
- Returns 8 fields (name, price, image-thumb, stock)
- 120 bytes per response (90% size reduction)
- Pre-calculates thumbnail URL in BFF
- 10x less data over mobile network

Web BFF GET /products/{id}:
- Returns 30 fields + gallery images
- Full rich response

Partner BFF GET /v1/products/{id}:
- Returns fields in partner's schema (custom names)
- ISO 8601 dates (partner requirement)
- HMAC auth (not JWT, partner's auth model)

**THE INSIGHT:**
Three clients, three optimal APIs, one consistent set of
underlying microservices. The BFF translates between client
world and service world without either side needing to
understand the other.

---

### 🧠 Mental Model / Analogy

> BFF is like a personal chef vs a buffet restaurant.
> A buffet (shared API) serves everyone from the same
> dishes - some guests want just salad, some want a full
> meal. The menu is a compromise. A personal chef (BFF)
> prepares exactly what each diner needs: compact and
> fast for the diet-conscious, elaborate for the food
> enthusiast. Same underlying ingredients (downstream
> microservices), entirely different presentation.

Where this analogy breaks down: a personal chef is more
expensive than a buffet. Similarly, BFFs increase the
number of services to maintain. BFF is justified when
client differences are significant and teams are large
enough to own separate APIs.

---

### 📶 Gradual Depth - Five Levels

**Level 1 - What it is (anyone can understand):**
BFF means "one backend per type of frontend". The mobile
app gets an API built specifically for mobile needs, the
web app gets its own, the partner gets their own. Each is
small, fast, and exactly right for its client.

**Level 2 - How to use it (junior developer):**
Create separate Spring Boot applications: `mobile-bff`,
`web-bff`, `partner-bff`. Each calls the same downstream
microservices but returns different response shapes.
Use Feign Clients or WebClient to call downstream services.
Each BFF has its own routes, auth, and payload contracts.

**Level 3 - How it works (mid-level engineer):**
The BFF is a thin orchestration layer: receive request from
client, dispatch parallel calls to downstream services (using
CompletableFuture or reactive), aggregate results, transform
to client-specific shape, return response. Client auth (JWT
for mobile, API key for partner, session for web) is handled
in the BFF. Downstream services receive user context via
trusted headers.

**Level 4 - Why it was designed this way (senior/staff):**
The BFF pattern emerged from Netflix's experience (2013+)
with multiple client types (mobile, web, TV) accessing the
same API. The shared API created a version compatibility
nightmare: mobile v1 users still using app v1 needed old
API shape; web needed new shape; TV had different
constraints entirely. BFF let each client team evolve their
API independently. The key insight: "team topologies
drive architecture" - Conway's Law means a separate team
for each client type naturally leads to separate BFFs.

**Level 5 - Mastery (distinguished engineer):**
The BFF vs GraphQL debate is nuanced. GraphQL is a query
language that solves the same problem. GraphQL Federation
allows a single graph with distributed schema resolution.
Staff engineers choose: BFF when clients have fundamentally
different API protocols or auth flows (REST for mobile,
SOAP for legacy partner); GraphQL when clients differ
only in data selection from the same graph; BFF+GraphQL
when the BFF serves as the GraphQL server and downstream
microservices are REST/gRPC.

---

### ⚙️ How It Works (Mechanism)

**MOBILE BFF REQUEST PROCESSING:**

```
Mobile App: GET /dashboard (with JWT)
  │
  ▼
Mobile BFF:
  1. Validate JWT (extract userId)
  2. Parallel fan-out:
     a. GET user-service/users/{userId}      → profile
     b. GET order-service/orders?userId={id} → orders
     c. GET notification-service/count/{id}  → badges
  3. Wait for all 3 responses (join)
  4. Assemble mobile-specific response:
     {
       "profile": {name, avatarThumb},
       "recentOrders": [{id, status, total}],
       "unreadCount": 3
     }
  5. Gzip compress (mobile bandwidth saving)
  6. Return to mobile app
```

**PARALLEL CALL PATTERN:**

```java
@GetMapping("/dashboard")
public Mono<DashboardResponse> dashboard(
    @RequestHeader("X-User-Id") String userId) {

    // Parallel reactive calls (non-blocking)
    Mono<UserProfile> profile =
        userClient.getProfile(userId)
            .map(this::toMobileProfile);

    Mono<List<OrderSummary>> orders =
        orderClient.getRecentOrders(userId, 5)
            .map(this::toMobileSummaries);

    Mono<Integer> unread =
        notificationClient.getUnreadCount(userId);

    // Combine when all complete
    return Mono.zip(profile, orders, unread)
        .map(tuple -> new DashboardResponse(
            tuple.getT1(),
            tuple.getT2(),
            tuple.getT3()
        ));
}
// Total time = max(profile, orders, unread) latency
// NOT sum - parallel execution
```

---

### 🔄 The Complete Picture - End-to-End Flow

**MULTI-CLIENT ARCHITECTURE:**

```
Mobile App ──→ Mobile BFF (port 8081)
                  │ GET /dashboard
                  ├─ user-service    (parallel)
                  ├─ order-service   (parallel)
                  └─ notif-service   (parallel)
                  → compact JSON (120 bytes)

Web App    ──→ Web BFF (port 8082)
                  │ GET /dashboard
                  ├─ user-service    (full profile)
                  ├─ order-service   (full history)
                  ├─ recommendation  (personalised)
                  └─ analytics       (A/B test bucket)
                  → rich JSON (4KB)

Partner    ──→ Partner BFF (port 8083)
                  │ GET /v1/orders
                  ├─ order-service   (bulk query)
                  └─ transform to partner schema
                  → ISO 8601 dates, partner field names
```

**TEAM OWNERSHIP:**
```
Mobile team  → owns: Mobile App + Mobile BFF
Web team     → owns: Web App + Web BFF
Partner team → owns: Partner integration + Partner BFF
Platform team → owns: downstream microservices

Each team releases independently.
```

---

### 💻 Code Example

**Example 1 - Wrong vs Right: over-fetching in shared API**

```java
// BAD: shared API returns all fields for all clients
// Mobile gets 30 fields but only uses 5
@GetMapping("/products/{id}")
public ProductDTO getProduct(@PathVariable String id) {
    Product product = productService.findById(id);
    return ProductDTO.fromFull(product); // all 30 fields
}
// Mobile: receives 1.2KB, renders 120 bytes
// Partner: field names wrong for their schema
```

```java
// GOOD: Mobile BFF returns mobile-specific shape
// In mobile-bff service:
@GetMapping("/products/{id}")
public MobileProductDTO getProduct(
    @PathVariable String id) {

    // Call downstream product-service (all fields)
    ProductFull product = productClient.getById(id);

    // Transform to mobile-specific shape (5 fields)
    return MobileProductDTO.builder()
        .name(product.getName())
        .price(product.getPrice())
        .thumbUrl(imageService
            .toThumbnailUrl(product.getImageUrl()))
        .inStock(product.getStockCount() > 0)
        .rating(product.getAverageRating())
        .build();
    // 90% smaller payload - faster load, less battery
}
```

---

### ⚖️ Comparison Table

| Approach | Client-Specific Shape | Team Independence | Complexity | Best For |
|---|---|---|---|---|
| **Shared REST API** | No | No | Low | Few clients, similar needs |
| **BFF per client** | Yes | Yes | Medium (N BFFs) | Multiple client types |
| **GraphQL** | Yes (query selection) | Partial | Medium | Clients with same domain |
| **GraphQL Federation** | Yes | Yes | High | Large graph, many teams |

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| BFF is just a proxy that forwards requests | BFF is an orchestration layer. It aggregates multiple services, transforms data shapes, and handles client-specific concerns. A pure proxy is just a gateway. |
| One BFF per client app means dozens of BFFs | BFF per client TYPE (mobile, web, partner), not per app. Typically 2-4 BFFs for most systems. |
| BFF duplicates business logic | BFF contains only API orchestration and data shaping, not business logic. Business rules stay in domain services. |

---

### 🚨 Failure Modes & Diagnosis

**BFF becomes a bottleneck (sequential calls)**

**Symptom:**
Mobile dashboard endpoint takes 600ms. Three downstream
services each take 200ms.

**Root Cause:**
```java
// BAD: sequential calls
UserProfile profile = userClient.get(userId); // 200ms
List<Order> orders = orderClient.get(userId); // 200ms
int unread = notifClient.count(userId);       // 200ms
// Total: 600ms (sum of all latencies)
```

**Diagnostic Command:**
```bash
# Check distributed trace spans in Jaeger
# Sequential: each span starts after previous ends
# Parallel: all spans start at same time
curl http://jaeger:16686/api/traces?service=mobile-bff
```

**Fix:**
Convert to parallel calls using Mono.zip or
CompletableFuture.allOf(). Total time = max(all downstream
times), not sum.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `API Gateway` - gateway handles cross-cutting concerns;
  BFF handles client-specific orchestration

**Builds On This (learn these next):**
- `API Composition Pattern` - the core technique used inside
  BFF to aggregate multiple service responses

**Alternatives / Comparisons:**
- `GraphQL` - solves over/under-fetching via query language
  instead of multiple BFF instances

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Dedicated backend per client type         │
│              │ Shapes data exactly for that client       │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM      │ One shared API can't serve mobile, web,   │
│ IT SOLVES    │ and partner optimally - always compromises │
├──────────────┼───────────────────────────────────────────┤
│ KEY BENEFIT  │ Mobile team owns Mobile BFF - releases    │
│              │ independently without web/partner coord   │
├──────────────┼───────────────────────────────────────────┤
│ CRITICAL     │ Parallel fan-out to downstream services:  │
│ PATTERN      │ Mono.zip() or CompletableFuture.allOf()  │
├──────────────┼───────────────────────────────────────────┤
│ ANTI-PATTERN │ Sequential calls = sum of latencies       │
│              │ instead of max latency (parallel)        │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Purpose-built API per client type:       │
│              │  exactly what mobile needs, nothing more" │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ API Composition Pattern → GraphQL         │
└──────────────────────────────────────────────────────────┘
```

**If you remember only 3 things:**
1. BFF per client TYPE, not per client app. Typically 2-4
   BFFs for mobile, web, and partner.
2. Always use parallel calls (Mono.zip / CompletableFuture)
   for downstream fan-out - sequential = sum of latencies.
3. BFF contains orchestration and shaping, not business
   logic. Business rules stay in domain services.

**Interview one-liner:**
"The Backend for Frontend pattern creates a dedicated API
layer for each distinct client type. Each BFF aggregates
and shapes data from multiple downstream services specifically
for its client - mobile gets compact payloads, web gets
rich data, partners get their schema. It enables each client
team to own their API contract and release independently.
The critical implementation pattern is parallel fan-out."

---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
BFF applies Interface Segregation at the service level:
clients should not depend on APIs they don't use. A shared
API that serves 20 fields when a client needs 5 violates
ISP at the network layer. BFF restores single responsibility
by giving each client exactly the interface it needs.

**Where else this pattern appears:**
- Mobile apps with offline support: BFF handles sync logic
- IoT devices: BFF translates between MQTT and internal APIs
- Legacy integration: BFF adapts SOAP/XML to modern JSON

---

### 💡 The Surprising Truth

BFF teams sometimes fall into the trap of adding business
logic to the BFF because it's convenient. Within 6-12 months,
the BFF contains critical rules that should be in domain
services. When a new client type is added, the logic must
be duplicated. The discipline: BFF calls services and
transforms data. The test: "Would a second BFF for a new
client need the same logic?" If yes, it belongs in a service.

---

### ✅ Mastery Checklist

**You've mastered this when you can:**
1. **DESIGN** Design a BFF architecture for a fintech app
   with mobile app, web dashboard, and bank partner API.
2. **IMPLEMENT** Write a BFF endpoint using Mono.zip for
   3 parallel downstream calls.
3. **DECIDE** Determine when BFF is better than GraphQL
   for a given client diversity scenario.
4. **DEBUG** Given 800ms BFF latency with 200ms downstream
   services, identify and fix the sequential call pattern.
5. **EXTEND** Design a BFF that supports offline sync for
   a mobile app: caching strategy, staleness detection,
   conflict resolution.

---

### 🧠 Think About This Before We Continue

**Q1.** Your Mobile BFF fans out to 5 services. Three
respond in 50ms; one takes 200ms, one takes 500ms. Mono.zip
total = 500ms. UX requirement: 300ms max. What are your
options? (Hint: partial responses, progressive loading,
caching, relaxing consistency for non-critical data.)

**Q2.** Mobile BFF and Web BFF both call User Service
for subscription tier. The User Service team renames
`subscriptionLevel` to `tier`. How does this propagate?
What breaks? What prevents silent breakage?
(Hint: consumer-driven contract testing - Pact.)

**Q3.** Compare BFF with GraphQL Federation for 200
microservices and 5 client types. At what scale does
GraphQL Federation become more maintainable? What are
the operational trade-offs of each approach?