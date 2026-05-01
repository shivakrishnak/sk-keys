---
layout: default
title: "API Gateway (Microservices)"
parent: "Microservices"
nav_order: 641
permalink: /microservices/api-gateway-microservices/
number: "641"
category: Microservices
difficulty: ★★☆
depends_on: "Service Discovery, Inter-Service Communication"
used_by: "Backend for Frontend (BFF), Service Mesh (Microservices)"
tags: #intermediate, #microservices, #networking, #architecture, #pattern
---

# 641 — API Gateway (Microservices)

`#intermediate` `#microservices` `#networking` `#architecture` `#pattern`

⚡ TL;DR — An **API Gateway** is a single entry point for all external client requests into a microservices system. It handles cross-cutting concerns: **routing** (to correct service), **authentication/authorisation**, **rate limiting**, **SSL termination**, **protocol translation**, and **request aggregation**. Examples: Spring Cloud Gateway, Kong, AWS API Gateway, Nginx.

| #641            | Category: Microservices                                  | Difficulty: ★★☆ |
| :-------------- | :------------------------------------------------------- | :-------------- |
| **Depends on:** | Service Discovery, Inter-Service Communication           |                 |
| **Used by:**    | Backend for Frontend (BFF), Service Mesh (Microservices) |                 |

---

### 📘 Textbook Definition

An **API Gateway** is a server that acts as the single entry point into a microservices system from external clients (web browsers, mobile apps, third-party consumers). It decouples clients from the internal service topology: clients call one endpoint; the gateway routes calls to the appropriate microservices, applies cross-cutting concerns, and returns aggregated responses. Core functions include: **routing** — forward requests to the correct upstream service based on URL path, headers, or method; **authentication/authorisation** — validate JWT tokens or API keys before forwarding; **rate limiting** — protect services from abuse; **SSL/TLS termination** — handle HTTPS at the gateway, use HTTP internally; **request/response transformation** — translate between external API shapes and internal service APIs; **aggregation** — call multiple services in parallel and merge responses for a single client request. Gateways also enable client-type-specific APIs via the Backend for Frontend (BFF) pattern. Common implementations: Spring Cloud Gateway (reactive, JVM), Kong (Nginx-based, plugin ecosystem), AWS API Gateway, Apigee, Nginx, Traefik.

---

### 🟢 Simple Definition (Easy)

An API Gateway is the front door to your microservices system. Instead of clients knowing where each service lives, they talk to one address. The gateway figures out which service should handle each request and forwards it. It also handles security, rate limiting, and other shared concerns in one place — so individual services don't have to.

---

### 🔵 Simple Definition (Elaborated)

Without an API Gateway, a mobile app needs to call `OrderService` at port 8081, `ProductService` at port 8082, and `UserService` at port 8083 — and implement authentication in each call. With a gateway, the app calls one endpoint (`api.myapp.com`). The gateway validates the JWT token, routes `/api/orders` to `OrderService`, `/api/products` to `ProductService`, and `/api/users` to `UserService` — and handles HTTPS, rate limiting, and logging. Services move, scale, or change ports without the mobile app knowing.

---

### 🔩 First Principles Explanation

**What the gateway handles so services don't have to:**

```
WITHOUT GATEWAY:                 WITH GATEWAY:

Client must know:                Client knows:
  OrderService: 10.0.1.1:8081     API: api.example.com/api
  ProductService: 10.0.1.2:8082
  UserService: 10.0.1.3:8083

Client handles:                  Gateway handles:
  JWT validation in each call      JWT validation once, pass identity header downstream
  Rate limiting detection          Rate limiting by IP/user/API key
  SSL in each connection           SSL termination (HTTPS externally, HTTP internally)
  CORS headers on each service     CORS headers at gateway

Services handle:                 Services handle:
  Business logic + auth            Business logic only

GATEWAY ROUTING RULES:
  Route 1: path=/api/orders/**  → OrderService (round-robin load balanced)
  Route 2: path=/api/products/**→ ProductService
  Route 3: path=/api/users/**   → UserService

  Filters applied on all routes:
    Pre-filters:  JWT validation, rate limit check, request logging
    Post-filters: response header injection, error format normalisation
```

**Authentication at the gateway — JWT passthrough:**

```
CLIENT CALL:
  GET api.example.com/api/orders/12345
  Authorization: Bearer eyJhbGciOiJSUzI1NiJ9...

GATEWAY PRE-FILTER:
  1. Extract JWT from Authorization header
  2. Validate signature (using public key / JWKS endpoint)
  3. Check expiry (exp claim)
  4. Check issuer (iss claim)
  5. If invalid → 401 Unauthorized (request NOT forwarded to service)

  If valid: extract claims:
    sub: "user-123"
    roles: ["CUSTOMER", "PREMIUM"]

  Forward to OrderService with custom headers:
    X-User-Id: user-123
    X-User-Roles: CUSTOMER,PREMIUM
    (Remove Authorization header from internal call for efficiency)

ORDER SERVICE:
  @RequestMapping("/api/orders/{id}")
  public Order getOrder(
      @PathVariable Long id,
      @RequestHeader("X-User-Id") String userId) {
    // No JWT parsing needed — gateway already validated
    // Just use the pre-extracted user identity
    return orderService.findByIdForUser(id, userId);
  }
```

**Spring Cloud Gateway route definition:**

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: orders
          uri: lb://order-service # lb:// = Spring Cloud LoadBalancer
          predicates:
            - Path=/api/orders/**
          filters:
            - name: RequestRateLimiter
              args:
                redis-rate-limiter.replenishRate: 100 # 100 req/s per key
                redis-rate-limiter.burstCapacity: 200 # burst up to 200
                key-resolver: "#{@ipKeyResolver}"
            - name: CircuitBreaker
              args:
                name: order-circuit-breaker
                fallbackUri: forward:/fallback/orders
            - RemoveRequestHeader=Authorization # strip JWT before forwarding
            - AddRequestHeader=X-Forwarded-Service, api-gateway

        - id: products
          uri: lb://product-service
          predicates:
            - Path=/api/products/**
```

---

### ❓ Why Does This Exist (Why Before What)

WITHOUT API Gateway:

1. Clients must know all service addresses → coupling: every service relocation requires client updates.
2. Each service implements JWT validation → duplicated logic, inconsistent implementation.
3. Clients make multiple calls for one page → multiple round trips → high latency.
4. No central rate limiting → services exposed directly to internet traffic spikes.
5. Services need to handle HTTPS → SSL certificates on every service.

WITH API Gateway:
→ Single stable client-facing URL, internal topology hidden.
→ Cross-cutting concerns (auth, rate limiting, SSL) in one place.
→ Request aggregation: one client call → gateway calls multiple services in parallel.
→ Service changes (scaling, IP changes) transparent to clients.

---

### 🧠 Mental Model / Analogy

> An API Gateway is like the front desk of a large hospital. Patients (clients) don't go directly to the cardiology wing, the lab, or the pharmacy — they check in at the front desk. The receptionist (gateway) verifies their identity (authentication), ensures they're not overwhelming the system (rate limiting), and directs them to the right department (routing). The front desk also knows when the cardiology wing is temporarily closed and redirects patients to another ward (fallback routing). Departments focus on care, not visitor management.

"Front desk receptionist" = API Gateway
"Verify identity" = JWT validation / authentication
"Directing to department" = routing to correct microservice
"Knowing which ward is closed" = circuit breaker fallback routing

---

### ⚙️ How It Works (Mechanism)

**Spring Cloud Gateway — custom global filter (request logging + JWT extraction):**

```java
@Component
@Order(1)  // runs before route-specific filters
class JwtExtractionGlobalFilter implements GlobalFilter {

    @Autowired JwtValidator jwtValidator;

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String authHeader = exchange.getRequest().getHeaders()
            .getFirst(HttpHeaders.AUTHORIZATION);

        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }

        String token = authHeader.substring(7);
        try {
            Claims claims = jwtValidator.validateAndExtract(token);

            // Add extracted identity as headers for downstream services:
            ServerHttpRequest modifiedRequest = exchange.getRequest().mutate()
                .header("X-User-Id", claims.getSubject())
                .header("X-User-Roles", String.join(",", claims.get("roles", List.class)))
                .header(HttpHeaders.AUTHORIZATION, "")  // strip JWT
                .build();

            return chain.filter(exchange.mutate().request(modifiedRequest).build());

        } catch (JwtException e) {
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }
    }
}
```

---

### 🔄 How It Connects (Mini-Map)

```
External Clients
(browser, mobile, 3rd party)
        │
        ▼
API Gateway (Microservices)  ◄──── (you are here)
(routing, auth, rate limiting, SSL)
        │
        ├── Service Discovery → gateway finds service instances via registry
        ├── Backend for Frontend (BFF) → specialised gateways per client type
        ├── Service Mesh → handles east-west (service-to-service) traffic
        └── Rate Limiting (Microservices) → implemented at gateway layer
```

---

### 💻 Code Example

**Response aggregation — fan-out to multiple services:**

```java
@RestController
class DashboardAggregatorController {

    @Autowired WebClient.Builder webClientBuilder;

    // Single endpoint that aggregates data from 3 services:
    @GetMapping("/api/dashboard/{userId}")
    public Mono<DashboardResponse> getDashboard(@PathVariable String userId) {
        WebClient client = webClientBuilder.build();

        Mono<OrderSummary> orders = client.get()
            .uri("lb://order-service/api/orders/user/{userId}", userId)
            .retrieve().bodyToMono(OrderSummary.class);

        Mono<LoyaltyPoints> loyalty = client.get()
            .uri("lb://loyalty-service/api/loyalty/{userId}", userId)
            .retrieve().bodyToMono(LoyaltyPoints.class);

        Mono<List<Recommendation>> recs = client.get()
            .uri("lb://recommendation-service/api/recommendations/{userId}", userId)
            .retrieve().bodyToFlux(Recommendation.class).collectList();

        // Parallel calls, combine responses:
        return Mono.zip(orders, loyalty, recs)
            .map(tuple -> DashboardResponse.builder()
                .orders(tuple.getT1())
                .loyaltyPoints(tuple.getT2())
                .recommendations(tuple.getT3())
                .build());
    }
}
```

---

### ⚠️ Common Misconceptions

| Misconception                                        | Reality                                                                                                                                                                                                             |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The API Gateway replaces the Service Mesh            | They solve different problems: API Gateway handles north-south traffic (client → services); Service Mesh handles east-west traffic (service → service). You need both in a mature microservices system              |
| The API Gateway should contain business logic        | The API Gateway should only handle cross-cutting concerns (routing, auth, rate limiting, SSL). Business logic belongs in services. Thick gateways become bottlenecks and monoliths                                  |
| A single API Gateway serves all client types equally | Mobile apps, browsers, and third-party consumers have different needs (data shape, auth methods, rate limits). The BFF pattern creates client-specific gateways rather than a single overly complex one             |
| API Gateway is only needed for external traffic      | Some architectures use internal gateways for service-to-service calls. However, this is usually better handled by a Service Mesh which provides per-service observability and security without centralizing routing |

---

### 🔥 Pitfalls in Production

**API Gateway as a single point of failure:**

```
PROBLEM: All external traffic flows through the gateway.
  If the gateway crashes → all services unreachable → complete outage.
  If the gateway is slow → all services appear slow.
  If the gateway has a bug (e.g., wrong rate limit config) → all services affected.

MITIGATIONS:
  1. High Availability: run multiple gateway instances behind a load balancer
     (e.g., 3 Spring Cloud Gateway pods with K8s HPA for scaling)

  2. Circuit breakers on ALL gateway routes:
     If order-service is DOWN → gateway returns 503 for /api/orders
     But /api/products still works → partial degradation, not full outage

  3. Timeouts on ALL upstream calls:
     gateway timeout < upstream service timeout (gateway should fail fast)

  4. Rate limiting with Redis:
     Store rate limit counters in Redis (not gateway memory)
     → Gateway instances can scale horizontally + share limits

  5. Gateway config as code (GitOps):
     Route changes reviewed → tested in staging → deployed
     Never make live route changes in production console (risky)

  6. Circuit breaker fallback routes:
     fallback: return cached response, static page, or graceful error
     Not just a generic 503 — maintain UX during partial outages
```

---

### 🔗 Related Keywords

- `Service Discovery` — gateway uses service discovery to find upstream service instances
- `Backend for Frontend (BFF)` — specialised gateway pattern per client type
- `Service Mesh (Microservices)` — handles service-to-service (east-west) communication
- `Rate Limiting (Microservices)` — primary location for rate limiting implementation

---

### 📌 Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│ ROLE         │ Single entry point for external clients   │
│ HANDLES      │ Routing, Auth, Rate Limiting, SSL,        │
│              │ Request aggregation                       │
├──────────────┼───────────────────────────────────────────┤
│ TOOLS        │ Spring Cloud Gateway (reactive JVM)       │
│              │ Kong, AWS API Gateway, Nginx, Traefik      │
├──────────────┼───────────────────────────────────────────┤
│ DON'T        │ Put business logic in the gateway        │
│              │ Use a single gateway for all client types │
├──────────────┼───────────────────────────────────────────┤
│ NORTH-SOUTH  │ API Gateway (external → services)         │
│ EAST-WEST    │ Service Mesh (service → service)          │
└──────────────────────────────────────────────────────────┘
```

---

### 🧠 Think About This Before We Continue

**Q1.** A large API Gateway for an e-commerce platform handles authentication for 10 microservices. Currently, it validates JWT tokens synchronously (calls an auth service for each request). At peak traffic (50,000 requests/second), the auth service becomes the bottleneck. Describe three strategies to reduce the auth service load: (a) local JWT validation using a public key (no network call); (b) caching validated tokens in Redis with a short TTL; (c) token introspection with a circuit breaker fallback. What are the security trade-offs of each strategy, particularly around token revocation latency?

**Q2.** The API Gateway is a potential single point of failure. Describe a multi-region API Gateway architecture (e.g., AWS + Spring Cloud Gateway): how are requests routed to the nearest region (DNS-based routing, Anycast)? If one region's gateway cluster goes down, how do clients fail over to another region? What is the role of CDNs (CloudFront, Cloudflare) in front of API Gateways for both performance and DDoS protection?
