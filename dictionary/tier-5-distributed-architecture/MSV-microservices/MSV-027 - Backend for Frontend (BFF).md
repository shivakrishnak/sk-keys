---
layout: default
title: "Backend for Frontend (BFF)"
parent: "Microservices"
grand_parent: "Technical Dictionary"
nav_order: 27
permalink: /microservices/backend-for-frontend/
id: MSV-027
category: Microservices
difficulty: ★★★
depends_on: API Gateway, Service Decomposition, Inter-Service Communication
used_by: API Gateway, Rate Limiting, GraphQL APIs
related: API Gateway, GraphQL, Service Mesh
tags:
  - microservices
  - api
  - architecture
  - deep-dive
  - pattern
status: complete
version: 2
---

# MSV-027 - Backend for Frontend (BFF)

⚡ TL;DR - BFF is a pattern that creates a dedicated backend service per client type (mobile, web, third-party), each optimised for its client's specific data and interaction needs.

| #642 | Category: Microservices | Difficulty: ★★★ |
|:---|:---|:---|
| **Depends on:** | API Gateway, Service Decomposition, Inter-Service Communication | |
| **Used by:** | API Gateway, Rate Limiting, GraphQL APIs | |
| **Related:** | API Gateway, GraphQL, Service Mesh | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A food-delivery platform has a single API serving mobile apps, web browsers, and restaurant partner integrations. The mobile app needs compact responses (low bandwidth). The web app needs richer data (full menus, images, reviews). Restaurant partners need batch-optimised bulk APIs. The single API team must make every endpoint satisfy all three consumers simultaneously. Mobile requests return 50 fields the app never uses. Web requests need data from 5 extra services but the single gateway can't justify the aggregation logic. Partners are blocked waiting for changes that don't affect them.

**THE BREAKING POINT:**
One API for all clients is a compromise API for all clients. The general-purpose API is always over-fetching for some clients and under-fetching for others. The team maintaining the gateway becomes a bottleneck that all client teams depend on.

**THE INVENTION MOMENT:**
This is exactly why the Backend for Frontend (BFF) pattern was created - to give each client type an optimised, client-owned backend that serves exactly the data shape each client needs, at the performance characteristics each client requires.


**EVOLUTION:**
The Backend for Frontend pattern was coined by Sam Newman in 2015 to address a single API being forced to serve multiple client types with conflicting needs. The pattern emerged from Netflix's experience with TV, mobile, and web clients all hitting the same API and receiving more data than any individual client needed. The BFF provides a client-specific API layer, owned by the frontend team, that aggregates and transforms backend service calls to match each client's specific needs. The discipline evolved from 'one API for all' to 'one API per client type' - with the BFF as the translation layer.
---

### 📘 Textbook Definition

**Backend for Frontend (BFF)** is an architectural pattern where a dedicated backend service is created for each type of frontend client (e.g., mobile BFF, web BFF, partner API BFF). Each BFF is responsible for aggregating data from underlying microservices, translating and transforming it into the format optimised for its specific client, and implementing the data-fetching and interaction patterns appropriate for that client type. BFFs are typically owned by the frontend team for that client type. The pattern was coined by Sam Newman in 2015.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
Instead of one API for all clients, give each type of client its own dedicated API tailored to its exact needs.

**One analogy:**
> A personal chef vs a cafeteria. A cafeteria (general API) serves the same menu to everyone - it is efficient for the provider but produces unnecessary food waste and unpopular dishes. A personal chef (BFF) knows exactly what each person wants: Alice gets a gluten-free meal, Bob gets a low-sodium diet, Charlie gets a child-sized portion. Each client gets precisely what they need.

**One insight:**
The BFF pattern moves the "what data do we expose?" question from a platform-team concern to a client-team concern. The client team owns their BFF - they can change their API contract whenever their UI needs change, without coordinating with other client teams.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. Different clients have fundamentally different data shape requirements - what serves one client well harms another.
2. A general-purpose API is a compromised API - optimised for neither client fully.
3. Client-team ownership of the BFF aligns ownership with knowledge: the team that knows what the UI needs owns the API that provides it.

**DERIVED DESIGN:**
Each BFF is an application server (Node.js, Spring Boot, Go) that:
- Accepts requests from its specific client
- Calls the appropriate downstream microservices
- Aggregates, transforms, and filters data for its client
- Handles its client's authentication and session model
- Manages its client's specific error handling and retry needs

BFFs call the internal microservices directly (no shared API gateway between services). The microservices are the system of record; BFFs are presentation-optimised facades.

**BFF placement in the system:**

```
Mobile App     Web App      Partners
    │              │              │
    ▼              ▼              ▼
Mobile BFF    Web BFF      Partner BFF
    │              │              │
    └──────┬────────┘──────┬──────┘
           ▼               ▼
   Catalog Service    Order Service
   Inventory Svc      Payment Svc
   ...                ...
```

**THE TRADE-OFFS:**
**Gain:** Each client gets optimised API, client-team autonomy, smaller blast radius per change, can optimise per-client performance.
**Cost:** Code duplication across BFFs, more services to deploy and operate, shared concerns (auth, logging) must be extracted into libraries or the pattern re-introduces code duplication at BFF level.

---

### 🧪 Thought Experiment

**SETUP:**
Mobile app needs: `{productId, name, thumbnailUrl, price}` (4 fields). Web app needs: `{productId, name, description, imageUrls[], dimensions, weight, categoryPath[], reviews{count, avgRating}}` (20+ fields).

**WITHOUT BFF (single API):**
API returns all 20+ fields for every request. Mobile gets 20 fields, uses 4, discards 80% of data. Mobile bandwidth wasted. Alternatively: API returns 4 fields - web app must make 3 more API calls to get remaining data. Web is chatty. Every change to the mobile field set requires coordination with the web team.

**WITH BFF:**
Mobile BFF: `GET /m/products/{id}` → returns `{productId, name, thumbnailUrl, price}` - exactly 4 fields. Web BFF: `GET /w/products/{id}` → aggregates from Catalog + Reviews + Inventory, returns 20+ fields. Each team changes their BFF independently. Neither affects the other. Downstream services (Catalog, Reviews) are unchanged.

**THE INSIGHT:**
BFF moves the data shaping work from the general API layer (shared, hard to change) to the client layer (team-owned, easy to change). The downstream services stay stable; the presentation contract is per-client.

---

### 🧠 Mental Model / Analogy

> BFF is like tailoring vs off-the-rack clothing. A single general API is off-the-rack - it fits most people poorly. A BFF is a tailor-made suit for each customer: the tailor (client team) knows the client's measurements (data needs), constructs exactly what's needed, and can alter it whenever requirements change without disturbing other customers.

- "Off-the-rack" → single general-purpose API gateway
- "Tailor-made for Alice" → mobile BFF tailored for mobile app needs
- "Tailor-made for Bob" → web BFF tailored for web app needs
- "Tailoring as needed" → BFF owned by client team - changes when UI changes

Where this analogy breaks down: tailor-made suits are expensive to create. BFFs have upfront cost (initial implementation) and ongoing cost (maintaining multiple services). In small teams this overhead may not be worth it.

---

### 📶 Gradual Depth - Four Levels

**Level 1 - What it is (anyone can understand):**
Instead of one API that tries to serve everyone, you build a separate API for each type of user interface: one for mobile, one for the website, one for third-party apps. Each API knows exactly what its client needs.

**Level 2 - How to use it (junior developer):**
Create a Node.js or Spring Boot service per client type. This service calls the internal microservices and shapes the response. The mobile team owns the mobile BFF; they add/remove/reshape fields whenever the mobile UI changes. Deploy each BFF independently. Use a shared authentication library so all BFFs validate tokens consistently.

**Level 3 - How it works (mid-level engineer):**
BFFs typically live inside the same trust boundary as internal services - they authenticate with internal service-to-service credentials (not public JWTs). The BFF translates the client's session/JWT into internal service calls. Data aggregation in a BFF is usually reactive/parallel: fetch product, reviews, and inventory simultaneously with `Promise.all` / `Mono.zip` rather than sequentially. GraphQL can act as a BFF query language - clients define their own query shape, reducing over/under-fetching.

**Level 4 - Why it was designed this way (senior/staff):**
Sam Newman coined BFF based on SoundCloud's 2015 architecture, where different device teams found a general API too rigid. The key insight is Conway's Law: the team structure should mirror the system structure, and vice versa. A mobile team owning a mobile BFF means API contract changes that serve mobile needs can be made autonomously without broad coordination. The risk of BFF is logic duplication - if three BFFs all implement the same "get order status" logic with slightly different data shapes, business logic starts living in BFFs (an anti-pattern). The mitigation: BFFs are translation/aggregation layers only. Core business logic stays in domain services.

---

### ⚙️ How It Works (Mechanism)

**BFF architecture for multi-client platform:**

```
┌──────────────────────────────────────────────┐
│           BFF Architecture                   │
├──────────────────────────────────────────────┤
│                                              │
│  [iOS App]  [Android]  [Web SPA]  [Partners] │
│      │           │         │           │     │
│      ▼           ▼         ▼           ▼     │
│  [Mobile BFF] [Mobile BFF][Web BFF][Partner] │
│                                  BFF         │
│      └─────────────┬─────────────┘           │
│                    │                         │
│          ┌─────────┼─────────┐               │
│          ▼         ▼         ▼               │
│    [Catalog]  [Orders]  [Reviews]             │
│    Service    Service    Service              │
│                                              │
│  Mobile BFF: same BFF for iOS and Android    │
│  (same data shape, different auth formats)   │
└──────────────────────────────────────────────┘
```

**Mobile BFF endpoint - compact response:**

```javascript
// Node.js Mobile BFF
app.get('/m/products/:id', async (req, res) => {
    const userId = req.headers['x-user-id'];
    // Parallel calls to internal services
    const [product, stock] = await Promise.all([
        catalogService.getProduct(req.params.id),
        inventoryService.getStock(req.params.id)
    ]);
    // Shape response for mobile - minimal fields
    res.json({
        id: product.id,
        name: product.name,
        thumbnail: product.images[0]?.thumbUrl,  // first image only
        price: product.currentPrice,
        inStock: stock.availableQty > 0
        // No description, no full images array - mobile doesn't need them
    });
});
```

**Web BFF endpoint - rich response:**

```javascript
// Node.js Web BFF
app.get('/w/products/:id', async (req, res) => {
    // Web needs more data - parallel calls to more services
    const [product, stock, reviews] = await Promise.all([
        catalogService.getProduct(req.params.id),
        inventoryService.getStock(req.params.id),
        reviewService.getSummary(req.params.id)
    ]);
    // Shape response for web - full data set
    res.json({
        id: product.id,
        name: product.name,
        description: product.fullDescription,
        images: product.images,        // all images
        dimensions: product.dimensions,
        price: product.currentPrice,
        availableQuantity: stock.availableQty,
        reviews: {
            count: reviews.count,
            avgRating: reviews.avgRating,
            topReview: reviews.featured
        }
    });
});
```

---

### 🔄 The Complete Picture - End-to-End Flow

**NORMAL FLOW:**
Client Request → BFF for its client type ← YOU ARE HERE → BFF authenticates request → BFF fans out calls to microservices in parallel → BFF aggregates and shapes response → Optimised response returned to client

**FAILURE PATH:**
One downstream service returns 503 → BFF catches exception → Returns partial response with unavailable fields as null/empty (graceful degradation) → Client UI handles null fields → Partial data better than total failure

**WHAT CHANGES AT SCALE:**
At 10x traffic, each BFF scales independently - mobile BFF sees 10x while partner BFF sees 1x if partner volume doesn't increase proportionally. BFFs' aggregation logic becomes a memory pressure point at very high fan-out (assembling responses from 10+ services × 50,000 RPS). Caching per BFF layer (Redis, in-memory) reduces downstream pressure.

---

### 💻 Code Example

**Example 1 - Spring Boot Web BFF with parallel calls:**

```java
@RestController
@RequestMapping("/w")
public class WebProductController {
    private final CatalogClient catalog;
    private final InventoryClient inventory;
    private final ReviewClient reviews;

    @GetMapping("/products/{id}")
    public Mono<WebProductResponse> getProduct(
            @PathVariable String id) {
        return Mono.zip(
            catalog.getProduct(id),
            inventory.getStockStatus(id),
            reviews.getSummary(id)
        ).map(tuple ->
            WebProductResponse.assemble(
                tuple.getT1(),
                tuple.getT2(),
                tuple.getT3()
            )
        );
    }
}

public record WebProductResponse(
    String id, String name,
    String description, List<String> imageUrls,
    BigDecimal price, int availableQty,
    ReviewSummary reviews
) {
    static WebProductResponse assemble(
            CatalogProduct p, StockStatus s, ReviewSummary r) {
        return new WebProductResponse(
            p.id(), p.name(), p.description(), p.imageUrls(),
            p.price(), s.quantity(), r
        );
    }
}
```

**Example 2 - Graceful degradation when one service fails:**

```java
@GetMapping("/m/products/{id}")
public Mono<MobileProductResponse> getMobileProduct(
        @PathVariable String id) {
    Mono<CatalogProduct> product = catalog.getProduct(id)
        .onErrorReturn(CatalogProduct.fallback(id));
    Mono<StockStatus> stock = inventory.getStockStatus(id)
        .onErrorReturn(StockStatus.UNKNOWN);  // fail gracefully

    return Mono.zip(product, stock)
        .map(t -> MobileProductResponse.of(t.getT1(), t.getT2()));
    // Returns partial data rather than failing entirely
}
```

---

### ⚖️ Comparison Table

| Approach | Client Optimisation | Team Autonomy | Complexity | Best For |
|---|---|---|---|---|
| **BFF** | High (per-client) | Highest | High | 3+ different client types |
| Single API Gateway | Low (general) | Low | Low | Simple apps, few clients |
| GraphQL Gateway | High (client queries) | High | Medium | Flexible query needs |
| Direct Service Calls | Client handles | Independent | High | Internal SPA + simple API |

How to choose: use BFF when client types have genuinely different data needs and separate client teams exist. Use a single API Gateway for low-complexity scenarios or when clients have similar data requirements.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| Each mobile platform (iOS, Android) needs its own BFF | iOS and Android typically share a mobile BFF - they access the same data, just presented differently in the UI |
| BFF is just another name for API Gateway | API Gateway is infrastructure (routing, auth, rate limiting); BFF is a domain-aware aggregation service owned by a specific client team |
| BFFs should contain business logic | BFFs are presentation and aggregation layers only. Business logic must stay in domain services - logic in BFFs creates duplication and a distributed monolith risk |
| BFF is only for mobile apps | BFF applies to any distinct client type: mobile, web SPA, third-party partners, internal tooling |

---

### 🚨 Failure Modes & Diagnosis

**1. Business Logic Duplication Across BFFs**

**Symptom:** A price calculation rule is implemented in both Mobile BFF and Web BFF. A bug is fixed in Web BFF but not Mobile BFF - mobile shows wrong prices for two weeks.

**Root Cause:** Pricing logic mistakenly placed in BFFs instead of the Pricing service.

**Diagnostic:**
```bash
# Find pricing logic outside the pricing service
grep -rn "discount\|price.*calc\|applyVat" \
  mobile-bff/src/ web-bff/src/ --include="*.java" --include="*.js"
# Any hits = misplaced business logic
```

**Fix:** Extract the pricing logic to the Pricing service. BFFs call the service and display the result.

**Prevention:** Enforce a rule: if two BFFs would have the same logic, that logic belongs in a service.

**2. BFF Becomes a Bottleneck Due to Missing Parallelism**

**Symptom:** BFF P99 latency is 800ms. Each individual service call takes ~50ms. Response time is sum of all calls.

**Root Cause:** Service calls made sequentially rather than in parallel.

**Diagnostic:**
```bash
# Check for sequential vs parallel call patterns in BFF logs
grep "calling.*service" bff.log | \
  awk '{print $1, $2, $NF}' | head -20
# Sequential timestamps = sequential calls
```

**Fix:** Change sequential calls to parallel (Promise.all, Mono.zip, CompletableFuture.allOf).

**Prevention:** All BFF aggregation should use parallel call patterns by default. Make sequential calls only when result B depends on result A.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `API Gateway (Microservices)` - BFF is a specialisation of the API Gateway pattern; understanding the general pattern contextualises the BFF variant
- `Service Decomposition` - BFFs aggregate from correctly decomposed services; poor decomposition makes BFF aggregation painful

**Builds On This (learn these next):**
- `GraphQL` - an alternative query language approach that achieves similar goals to BFF - clients specify their query shape, reducing over/under-fetching
- `Rate Limiting (Microservices)` - BFFs are typically the right place to enforce per-client rate limits

**Alternatives / Comparisons:**
- `API Gateway (Microservices)` - single shared gateway vs per-client dedicated BFF; choose BFF when clients have significantly different data needs

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ A dedicated backend per client type       │
│              │ (mobile, web, partner), each optimised    │
│              │ for its client's specific needs           │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ One-size-fits-all API over/under-fetches  │
│ SOLVES       │ for every client type simultaneously      │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ BFF moves API contract ownership to the   │
│              │ client team - they change their API when  │
│              │ their UI changes, without coordination    │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ 3+ distinct client types with different   │
│              │ data needs, especially with separate      │
│              │ frontend teams                            │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Clients share similar data needs or small │
│              │ team size makes multiple BFFs costly      │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Per-client optimisation + autonomy vs     │
│              │ more services to build and maintain       │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "Don't make your clients adapt to your    │
│              │  API - make your API adapt to each client."│
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ GraphQL → API Gateway →                   │
│              │ Rate Limiting                             │
└──────────────────────────────────────────────────────────┘
```


---

### 💎 Transferable Wisdom

**Reusable Engineering Principle:**
Build client-specific APIs, not one-size-fits-all APIs. An API optimised for mobile (minimal data, offline sync) is different from an API optimised for web (rich data, server-side state), which is different from a third-party API (stable versioned contract, rate limited). Serving all clients from one API creates an API suboptimal for all of them. The BFF extends the 'right tool for the job' principle to API layer design.

**Where else this pattern appears:**
- **Database query optimisation:** A reporting query (full historical data) and an OLTP query (current state, single record) require different indexes and query strategies - the BFF pattern applied to data access layer design.
- **UI component libraries:** A mobile component library (touch-optimised, minimal) and a desktop library (keyboard-optimised, feature-rich) serve different client types with different trade-offs - the BFF pattern applied to frontend component design.
- **SDK design:** An embedded device SDK (minimal footprint) vs a web application SDK (feature-rich) serves different client types with different constraints - the BFF pattern applied to client library design.

---

### 💡 The Surprising Truth

The Backend for Frontend pattern has a hidden failure mode teams discover 12-18 months after adoption: BFF teams start duplicating backend business logic in their BFFs. The Mobile BFF calculates discounts. The Web BFF calculates discounts with slightly different rules. Six months later, the two BFFs diverge in their discount calculations and customers see different prices on mobile vs web. The BFF pattern requires strict discipline: BFFs should only aggregate and transform - never implement business logic. Business logic must live in backend services, consumed by all BFFs via API.
---

### 🧠 Think About This Before We Continue

**Q1.** A fintech platform has a Mobile BFF and a Web BFF. The mobile team discovers that their BFF is making 8 sequential service calls to assemble a transaction history page, taking 1.2 seconds. They want to add a Redis cache in the Mobile BFF to store transaction summaries. The web BFF already has similar caching. Describe the exact cache coherence problem this introduces, what event-driven invalidation strategy would address it, and whether caching in the BFF is the right approach or whether caching should be pushed further down to the transaction service level.

*Hint:* Think about what cache coherence means when two BFFs have separate caches of the same underlying data: when the transaction service updates a record, both Mobile BFF cache and Web BFF cache must be invalidated simultaneously. Explore whether a domain event `TransactionUpdated` published by the transaction service and consumed by both BFFs for cache invalidation solves the coherence problem, and whether pushing caching to the transaction service (shared cache, single invalidation path) eliminates the two-BFF coherence complexity entirely.

**Q2.** Your company decides to allow third-party developers to access the same backend services through a Partner BFF. Unlike Mobile and Web BFFs (which are internal), the Partner BFF is semi-public. Describe the specific security, versioning, and rate limiting requirements that differ between internal BFFs and a Partner BFF, and design the breaking-change management strategy for the Partner BFF that protects partners from unexpected API changes while still allowing the platform to evolve.

*Hint:* Think about what differs between internal and Partner BFF: internal (coordinate changes via Slack, can break and fix same day; no SLA on change notice), Partner (external developers' code breaks when API changes; require 90-day deprecation notice, versioned endpoints maintained in parallel, per-API-key rate limiting). Explore what minimum set of controls the Partner BFF needs that internal BFFs don't require: semantic versioning, breaking-change policy, developer portal, and API key management.

**Q3 (Design Trade-off):** You have 3 BFFs (Mobile, Web, TV/Streaming). All 3 call the same 5 backend services. The operations team reports that a single backend service outage now simultaneously affects all 3 BFFs and all their users. Design a resilience strategy for BFFs that limits the blast radius of a single backend service outage.

*Hint:* Think about what resilience options exist at the BFF layer: circuit breakers (stop calling the failing service, use cached or default data), partial response (return the page without the failing service's data rather than returning a full error), and priority degradation (serve critical data paths first during contention). Explore whether each BFF should implement its own resilience strategy independently based on what its client type can tolerate (mobile might accept cached data; web might show a visible error state for the failing section).
