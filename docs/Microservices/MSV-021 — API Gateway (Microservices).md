---
layout: default
title: "API Gateway (Microservices)"
parent: "Microservices"
nav_order: 21
permalink: /microservices/api-gateway/
number: "MSV-021"
category: Microservices
difficulty: ★★☆
depends_on: Inter-Service Communication, Service Discovery, HTTP & APIs
used_by: Backend for Frontend, Service Mesh, Rate Limiting
related: Backend for Frontend, Service Mesh, Load Balancing
tags:
  - microservices
  - api
  - networking
  - intermediate
  - pattern
---

# MSV-021 — API Gateway (Microservices)

⚡ TL;DR — An API Gateway is a single entry point that routes external requests to the correct microservice, centralising cross-cutting concerns like authentication, rate limiting, SSL termination, and request aggregation.

| #641 | Category: Microservices | Difficulty: ★★☆ |
|:---|:---|:---|
| **Depends on:** | Inter-Service Communication, Service Discovery, HTTP & APIs | |
| **Used by:** | Backend for Frontend, Service Mesh, Rate Limiting | |
| **Related:** | Backend for Frontend, Service Mesh, Load Balancing | |

---

### 🔥 The Problem This Solves

**WORLD WITHOUT IT:**
A mobile app must assemble a product page. It needs to call: Catalog Service for product details, Inventory Service for stock, Pricing Service for current price, and Reviews Service for ratings. The mobile app makes 4 round-trip API calls. Each adds 50ms of mobile latency. Total: 200ms+ just in network. Plus: each service must independently validate the JWT token, apply rate limiting, and handle CORS. The same authentication code lives in 20 different services with 20 slightly different implementations.

**THE BREAKING POINT:**
Clients making multiple calls for a single UI render creates chatty client-server communication. Cross-cutting concerns (auth, rate limiting, logging) duplicated across services creates inconsistency and maintenance burden. Clients are directly coupled to internal service topology — changing a service's address requires updating every mobile app.

**THE INVENTION MOMENT:**
This is exactly why the API Gateway pattern was created — to provide a single, stable facade over the internal service topology, handling cross-cutting concerns once and aggregating responses for clients.

---

### 📘 Textbook Definition

An **API Gateway** is a server-side load balancer and reverse proxy that sits between external clients and backend microservices. It serves as the single entry point for all external API traffic, performing request routing, composition, and cross-cutting concern enforcement. Core functions include: request routing (to the correct service), authentication and authorisation (validate tokens before forwarding), rate limiting, SSL/TLS termination, request/response transformation, and API composition (aggregating multiple service responses into one). Commercial and open-source implementations include Kong, AWS API Gateway, NGINX, and Spring Cloud Gateway.

---

### ⏱️ Understand It in 30 Seconds

**One line:**
The front door to all your microservices — one place handles security, routing, and assembly for all external callers.

**One analogy:**
> An API Gateway is like a hotel concierge. Guests (clients) don't wander through the kitchen or housekeeping. They ask the concierge for everything. The concierge verifies you're a registered guest (authentication), calls the right departments (routing), assembles what you need (aggregation), and enforces hotel policies (rate limiting). The hotel's internal operations remain invisible to guests.

**One insight:**
The API Gateway isn't just routing — it is the place where "external contract" meets "internal chaos." External clients see a clean, stable API. Behind the gateway, services can be refactored, split, merged, or redeployed without any client impact.

---

### 🔩 First Principles Explanation

**CORE INVARIANTS:**
1. External clients should not know the internal service topology.
2. Cross-cutting concerns (auth, rate limiting, CORS) should be implemented once, not duplicated across services.
3. The gateway must be at least as available as the services it protects — it is on the critical path for all external traffic.

**DERIVED DESIGN:**
Given Invariant 1, the gateway owns the public API contract. It maps external routes (`/api/v1/products`) to internal service calls (`http://catalog-service:8080/products`). When the internal topology changes (catalog service splits into catalog-search and catalog-detail), only the gateway routing config changes — external clients are unaffected.

Given Invariant 2, the gateway's filter chain runs before any request reaches a service:
1. SSL termination
2. JWT validation
3. Rate limit check
4. Log request ID
5. Forward to service

Each filter is implemented once in the gateway. Services receive pre-validated requests.

**THE TRADE-OFFS:**
**Gain:** Client simplicity, centralised security, topology decoupling, aggregation capability.
**Cost:** Gateway is a single point of failure (mitigated by HA deployment), potential bottleneck under high traffic, gateway becomes complex as logic accumulates.

---

### 🧪 Thought Experiment

**SETUP:**
A product page needs data from 4 services. Without a gateway, the mobile client calls all 4 directly over 4G.

**WITHOUT API GATEWAY:**
- 4 × 50ms mobile RTT = 200ms network overhead
- Each service validates JWT token independently
- Service addresses must be known to the mobile app
- Changing a service's URL requires an app update

**WITH API GATEWAY:**
- Client calls `/api/v1/product-page/{id}` — ONE call
- Gateway validates JWT once
- Gateway calls all 4 services in parallel (co-located, LAN speeds: 4×1ms)
- Gateway assembles response
- Total: 1 × 50ms client RTT + ~5ms server assembly = 55ms
- Service URLs invisible to client

**THE INSIGHT:**
The gateway converts client-facing latency from O(N × network round trips) to O(1 × network round trip + N × internal calls). Internal calls are orders of magnitude faster than mobile network round trips.

---

### 🧠 Mental Model / Analogy

> An API Gateway is like an airport terminal. All flights (services) leave from one terminal (gateway). You check in (authenticate), go through security (rate limiting, auth), and board the right plane (routing). You don't enter the airfield directly. The terminal handles all the common procedures for all passengers, regardless of which plane they're boarding.

- "Airport terminal" → API gateway
- "Security check" → authentication + rate limiting
- "Departure gate" → routing rule to specific service
- "Different airlines under one roof" → different microservices behind one API
- "Runway invisible to passengers" → internal service topology hidden

Where this analogy breaks down: an airport terminal doesn't combine multiple planes' cargo into your luggage (response aggregation). The gateway does exactly this — combining responses from multiple services into one response.

---

### 📶 Gradual Depth — Four Levels

**Level 1 — What it is (anyone can understand):**
An API Gateway is the single front door to all your services. Instead of clients knowing about 20 different services, they only know about the gateway. The gateway handles routing, security, and combining results.

**Level 2 — How to use it (junior developer):**
Configure routes in your gateway to map external URLs to internal services. Set up JWT validation as a gateway filter so all requests are authenticated before reaching any service. Configure rate limiting per client or API key. The services behind the gateway can trust that requests have already been validated.

**Level 3 — How it works (mid-level engineer):**
The gateway uses a route predicate (path match, host match, header match) to determine which service handles each request. Filter chains run in order: pre-filters (auth, rate limit, log) → forward to service → post-filters (transform response, add headers). Request aggregation requires the gateway to fan out calls to multiple services in parallel and merge responses — implemented as a dedicated route with aggregation logic.

**Level 4 — Why it was designed this way (senior/staff):**
The API Gateway evolved from the traditional reverse proxy (Nginx, HAProxy) by adding programmability. NGINX routes traffic; API Gateways run filter chains written in code (Spring Cloud Gateway uses Reactive WebFlux; Kong uses Lua plugins). The critical insight: place only truly cross-cutting, stable concerns in the gateway. Domain logic must never reach the gateway — it causes the "smart gateway, dumb services" anti-pattern that defeats the purpose of microservices. The modern evolution is the BFF (Backend for Frontend) pattern: instead of one smart gateway, each client type (mobile, web, third-party) gets its own gateway tailored to its specific response shape needs.

---

### ⚙️ How It Works (Mechanism)

**Gateway request lifecycle:**

```
┌─────────────────────────────────────────────────┐
│         API Gateway Request Flow                │
├─────────────────────────────────────────────────┤
│ 1. TLS termination (decrypt HTTPS)             │
│ 2. Route matching (which service handles this) │
│    GET /api/v1/products/* → catalog-service    │
│    POST /api/v1/orders/* → order-service       │
│ 3. Pre-filter chain:                           │
│    a. Validate JWT → extract user claims        │
│    b. Rate limit check → 429 if exceeded        │
│    c. Add correlation-id header                 │
│    d. Log request metadata                      │
│ 4. Forward to upstream service (HTTP/gRPC)     │
│ 5. Post-filter chain:                           │
│    a. Transform response (remove internal fields│
│    b. Add security headers (HSTS, X-Frame)      │
│    c. Log response metadata                     │
│ 6. Return response to client                   │
└─────────────────────────────────────────────────┘
```

**Spring Cloud Gateway configuration:**

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: catalog-route
          uri: lb://catalog-service  # lb:// = load-balanced
          predicates:
            - Path=/api/v1/products/**
          filters:
            - StripPrefix=2        # removes /api/v1/ prefix
            - name: RequestRateLimiter
              args:
                redis-rate-limiter.replenishRate: 100
                redis-rate-limiter.burstCapacity: 200
        - id: orders-route
          uri: lb://order-service
          predicates:
            - Path=/api/v1/orders/**
            - Method=POST,GET
          filters:
            - AddRequestHeader=X-Gateway-Source, api-gateway
```

**JWT validation filter:**

```java
@Component
public class JwtAuthFilter implements GlobalFilter, Ordered {

    @Override
    public Mono<Void> filter(
            ServerWebExchange exchange, GatewayFilterChain chain) {
        String token = exchange.getRequest()
            .getHeaders().getFirst("Authorization");

        if (token == null || !token.startsWith("Bearer ")) {
            exchange.getResponse().setStatusCode(
                HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }

        try {
            Claims claims = jwtService.parse(token.substring(7));
            // Inject user ID for downstream services
            ServerHttpRequest mutatedRequest = exchange.getRequest()
                .mutate()
                .header("X-User-Id", claims.getSubject())
                .build();
            return chain.filter(
                exchange.mutate().request(mutatedRequest).build()
            );
        } catch (JwtException e) {
            exchange.getResponse()
                .setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }
    }

    @Override
    public int getOrder() { return -100; } // run first
}
```

---

### 🔄 The Complete Picture — End-to-End Flow

**NORMAL FLOW:**
Mobile Client → HTTPS → API Gateway ← YOU ARE HERE → JWT validated → Route matched → Request forwarded to service → Response returned through gateway → Client receives response

**AGGREGATION FLOW:**
Client GET /product-page/123 → Gateway fans out in parallel → Catalog, Inventory, Pricing, Reviews Services → Gateway merges responses → Single JSON response → Client (one round trip)

**FAILURE PATH:**
Downstream service returns 500 → Gateway logs error + correlationId → Returns 503 to client (or fallback response if configured) → Rate limiter continues counting — gateway stays available even as backend services fail

**WHAT CHANGES AT SCALE:**
At 100,000 req/s, the gateway is on the hot path for all traffic. It must scale horizontally. Use stateless gateway instances (no session state) so any instance handles any request. Rate limiting requires shared state (Redis) when multiple gateway instances run — Redis adds ~1ms latency per rate-limit check. At 1M req/s, consider splitting gateways per domain (separate gateway for public API vs partner API vs internal).

---

### 💻 Code Example

**Example 1 — BAD: Services doing their own auth (duplicated logic):**

```java
// BAD: every service re-implements JWT validation
@RestController
public class ProductController {
    @GetMapping("/products/{id}")
    public Product getProduct(
            @PathVariable Long id,
            @RequestHeader("Authorization") String token) {
        // Same JWT validation code in 20 services
        if (!jwtService.validate(token)) {
            throw new UnauthorizedException();
        }
        return productService.findById(id);
    }
}
```

**Example 2 — GOOD: Auth delegated to gateway (services trust gateway):**

```java
// GOOD: gateway validates JWT, passes user ID as header
// Services trust the header (internal network only)
@RestController
public class ProductController {
    @GetMapping("/products/{id}")
    public Product getProduct(
            @PathVariable Long id,
            @RequestHeader("X-User-Id") String userId) {
        // No token validation needed — gateway already did it
        return productService.findById(id, userId);
    }
}
// Configure network policy: only gateway can reach services
```

**Example 3 — Response aggregation for product page:**

```java
// Gateway aggregates 4 service calls into one response
@GetMapping("/product-page/{id}")
public Mono<ProductPageResponse> getProductPage(
        @PathVariable String id,
        @RequestHeader("X-User-Id") String userId) {

    Mono<CatalogProduct> catalog =
        catalogClient.getProduct(id);
    Mono<StockStatus> stock =
        inventoryClient.getStockStatus(id);
    Mono<Price> price =
        pricingClient.getPrice(id, userId);

    return Mono.zip(catalog, stock, price)
        .map(tuple -> ProductPageResponse.of(
            tuple.getT1(), tuple.getT2(), tuple.getT3()
        ));
    // All 3 calls made in parallel — total latency = max(3)
}
```

---

### ⚖️ Comparison Table

| Solution | Routing | Auth | Aggregation | Best For |
|---|---|---|---|---|
| **API Gateway** | Yes | Centralised | Yes | External traffic, cross-cutting concerns |
| Load Balancer (L4) | IP/Port only | No | No | Pure traffic distribution |
| Service Mesh | Yes | mTLS | No | Internal service-to-service |
| BFF | Yes | Yes | Yes (tailored) | Client-specific optimisation |
| Nginx / HAProxy | Yes (static) | Limited | No | Simple proxy without filter chains |

How to choose: use API Gateway for external-facing traffic; consider BFF when different clients (mobile vs web) need significantly different response shapes; use Service Mesh for internal service-to-service policies.

---

### ⚠️ Common Misconceptions

| Misconception | Reality |
|---|---|
| The API Gateway should contain business logic | Never. The gateway handles cross-cutting infrastructure concerns only. Business logic in the gateway defeats microservices independence and creates a bottleneck |
| API Gateway eliminates the need for service-level authentication | Service-level auth is still needed for internal service-to-service calls. Gateway auth only protects external-to-internal calls |
| One API Gateway is sufficient for all clients | Different clients (mobile, web, third-party) have different response shape needs. BFF pattern addresses this with per-client gateways |
| The API Gateway must be maintained by a central team | Gateway configuration (routes, rate limits) can be decentralised per service team using GitOps patterns |
| API Gateway replaces the service mesh | They serve different purposes: gateway handles north-south traffic (external to internal); service mesh handles east-west traffic (service to service) |

---

### 🚨 Failure Modes & Diagnosis

**1. Gateway Becomes a Bottleneck**

**Symptom:** P99 latency increases occur even when downstream services are fast. CPU usage on gateway nodes is consistently above 80%.

**Root Cause:** Gateway CPU is occupied by SSL termination, JWT validation, and response aggregation for very high traffic volume. Single gateway cluster is undersized.

**Diagnostic:**
```bash
# Check gateway pod CPU/memory
kubectl top pods -n gateway
# Check rate limiter performance
redis-cli -h redis-gateway info stats | grep -E "ops|hit_rate"
# Trace gateway processing time
curl -w "@curl-format.txt" https://api.example.com/v1/products/1
```

**Fix:** Scale gateway horizontally. Distribute SSL termination to edge nodes (CDN). Cache JWT public keys locally to avoid repeated fetches. Consider splitting into domain-specific gateways.

**Prevention:** Load test the gateway separately from the services. The gateway must handle the sum of all service traffic volumes.

**2. Gateway as Anti-Pattern — Business Logic Accumulation**

**Symptom:** Gateway configuration file is 10,000 lines. Routes contain conditional logic based on user type, A/B test flags, and product category rules.

**Root Cause:** Teams added business logic to the gateway for "convenience" — it was the easiest place to put client-specific transformations.

**Diagnostic:**
```bash
# Check gateway config size and complexity
wc -l gateway/routes.yml
grep -c "if\|condition\|predicates" gateway/routes.yml
# High count = logic creep
```

**Fix:** Move business logic to service layer or BFF. The gateway should only contain infrastructure concerns: routing, auth, rate limiting, header manipulation. Extract complex client-specific aggregation to a dedicated BFF service.

**Prevention:** Establish a "gateway suitability test": if a rule depends on business data (user tier, product category), it belongs in a service, not the gateway.

**3. Gateway Single Point of Failure**

**Symptom:** Gateway pod crashing takes the entire API offline — all external traffic fails simultaneously.

**Root Cause:** Gateway deployed as a single replica with no redundancy.

**Diagnostic:**
```bash
kubectl get pods -n gateway
# If replicas = 1: single point of failure
kubectl get deploy -n gateway -o yaml | grep replicas
```

**Fix:**
```yaml
# Gateway deployment with minimum replicas
spec:
  replicas: 3  # at least 3 for HA
  strategy:
    rollingUpdate:
      maxUnavailable: 1  # always keep 2 running during updates
---
# Add PodDisruptionBudget
apiVersion: policy/v1
kind: PodDisruptionBudget
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: api-gateway
```

**Prevention:** Always deploy the gateway with minimum 3 replicas across multiple availability zones.

---

### 🔗 Related Keywords

**Prerequisites (understand these first):**
- `Inter-Service Communication` — the gateway orchestrates and routes inter-service communication patterns
- `Service Discovery` — the gateway uses service discovery to resolve backend service addresses dynamically
- `HTTP & APIs` — the gateway's core protocol is HTTP; REST and API contract knowledge is foundational

**Builds On This (learn these next):**
- `Backend for Frontend (BFF)` — extends the API Gateway pattern with client-specific gateways optimised for each consumer's needs
- `Rate Limiting (Microservices)` — typically implemented at the gateway layer as a cross-cutting concern
- `Service Mesh (Microservices)` — the complementary pattern for east-west (internal) traffic management

**Alternatives / Comparisons:**
- `Service Mesh (Microservices)` — handles internal service-to-service traffic management; API Gateway handles external-to-internal
- `Backend for Frontend (BFF)` — a specialisation of API Gateway with per-client optimisation rather than a single shared gateway

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ WHAT IT IS   │ Single entry point for all external       │
│              │ traffic, handling routing, auth, rate     │
│              │ limiting, and response aggregation        │
├──────────────┼───────────────────────────────────────────┤
│ PROBLEM IT   │ Clients coupled to internal topology;     │
│ SOLVES       │ cross-cutting concerns duplicated across  │
│              │ services; chatty client-server calls      │
├──────────────┼───────────────────────────────────────────┤
│ KEY INSIGHT  │ The gateway owns the external contract.   │
│              │ Internal topology can change freely as    │
│              │ long as the gateway routes correctly      │
├──────────────┼───────────────────────────────────────────┤
│ USE WHEN     │ Multiple microservices need a stable,     │
│              │ unified external API with shared concerns │
├──────────────┼───────────────────────────────────────────┤
│ AVOID WHEN   │ Placing business logic in the gateway —   │
│              │ keep it infrastructure-only               │
├──────────────┼───────────────────────────────────────────┤
│ TRADE-OFF    │ Centralised control vs single point of    │
│              │ failure if not deployed with HA           │
├──────────────┼───────────────────────────────────────────┤
│ ONE-LINER    │ "One front door, many back rooms —        │
│              │  clients see the lobby, not the kitchen." │
├──────────────┼───────────────────────────────────────────┤
│ NEXT EXPLORE │ Backend for Frontend → Service Mesh →     │
│              │ Rate Limiting                             │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** Your API Gateway handles authentication for 100 services. The JWT validation currently fetches the JWKS (public key set) from the auth service on every token validation — adding 30ms to every request. Propose a key caching strategy that reduces this to sub-millisecond, and describe the exact security trade-off introduced by caching: what attack scenarios does caching enable that per-request fetching prevents?

**Q2.** Your platform grows to have 3 client types: mobile app (needs minimal data, bandwidth-sensitive), web app (needs rich data), and third-party API consumers (need standard REST contracts). You currently have one API Gateway serving all three. A colleague proposes splitting into 3 separate gateways (BFF pattern). Walk through the operational, security, and developer experience trade-offs of this split, and define the specific criteria that make the split worth the added complexity.

